"""STIV completo sobre las grabaciones de 24 h con el programa del directo (stiv_directo.py --archivo),
y un solo CSV por camara en reproduccion/<camara>.csv con la hora REAL de la grabacion (--hora-inicio +
PTS) en la columna hora_local y la noche decidida tambien por el sol a esa hora.

    python reproducir.py --rapido             # lo antes posible (~1.5-3 h las 4 camaras en este PC)
    python reproducir.py                      # como si fuera el directo, a velocidad real (~21.5 h)
    python reproducir.py --rapido --camaras shimoda --trozos 6 --procesos 6

--rapido: cada grabacion se parte en --trozos trozos (por bytes de segmento HLS: cada uno empieza por
un fotograma clave, asi que el trozo es un .ts que se decodifica solo, sin recomprimir; el mismo corte
que noche_24h/tramo.py) y los trozos se procesan en paralelo, sin esperar al reloj. Diferencias con el
directo: cada trozo pierde sus primeros 10-60 s (el STI se llena de nuevo; con 4 trozos por camara son
~4 min de 21.5 h), y sin --tiempo-real el programa mide cada vez que el hilo de medida queda libre, con
un minimo de 1 s de video entre medidas (en directo, cada 1 s exacto): salen menos medidas por minuto,
con el mismo metodo. Los trozos se borran al acabar.

Sin --rapido: --tiempo-real, cada fotograma a su hora y las cuatro camaras a la vez; lo que haria el
directo esa noche, en lo que dura el video.

Los huecos de la grabacion (PC suspendido de 09:24 a 11:33 JST) son saltos de PTS: el programa los
trata como un corte del directo (vacia el STI y sigue). Mientras corre, Windows no suspende el equipo.
"""
import argparse, csv, glob, os, subprocess, sys, threading, time
from multiprocessing.pool import ThreadPool
from datetime import datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
CASO = os.path.join(AQUI, "..")
GRAB = os.path.join(CASO, "verificacion_nivel", "grabaciones")
SALIDA = os.path.join(AQUI, "reproduccion")
TROZOS = os.path.join(AQUI, "trozos")
CAMARAS = ["myoshoji", "kurome", "shimoda", "akigawa"]


def grabaciones(camara):
    """[(video, filas de su _segmentos.csv)] de una camara, en orden."""
    res = []
    for seg in sorted(glob.glob(os.path.join(GRAB, f"{camara}_2026102*JST_segmentos.csv"))):
        with open(seg, encoding="utf-8") as f:
            filas = list(csv.DictReader(f))
        if filas:
            res.append((seg.replace("_segmentos.csv", ".ts"), filas))
    return res


def stiv(camara, video, hora, csv_salida, log, tiempo_real):
    log.write(f"=== {os.path.basename(video)} desde {hora}\n")
    log.flush()
    orden = [sys.executable, "-u", os.path.join(CASO, "stiv_directo.py"), "--camara", camara, "--archivo", video,
             "--sin-ventana", "--hora-inicio", hora, "--csv", csv_salida]
    if tiempo_real:
        orden.append("--tiempo-real")
    return subprocess.call(orden, cwd=CASO, stdout=log, stderr=subprocess.STDOUT,
                           env=dict(os.environ, PYTHONIOENCODING="utf-8"))


def tiempo_real(camara):
    with open(os.path.join(SALIDA, f"{camara}.log"), "a", encoding="utf-8") as log:
        for video, filas in grabaciones(camara):
            stiv(camara, video, filas[0]["hora_descarga_jst"], os.path.join(SALIDA, f"{camara}.csv"), log, True)
        log.write("=== fin\n")


def trozos(camara, n):
    """[(camara, video, byte inicial, bytes, hora JST, nombre)]: cada grabacion en n trozos de bytes
    parecidos, cortados en limites de segmento."""
    res = []
    for video, filas in grabaciones(camara):
        total = sum(int(f["bytes"]) for f in filas)
        k = n if total > 1e9 else 1          # la grabacion corta (12 min) va entera
        cortes, acum, i0 = [], 0, 0
        for i, f in enumerate(filas):
            if acum >= total * (len(cortes) + 1) / k and len(cortes) < k - 1:
                cortes.append((i0, i))
                i0 = i
            acum += int(f["bytes"])
        cortes.append((i0, len(filas)))
        for a, b in cortes:
            inicio = sum(int(f["bytes"]) for f in filas[:a])
            largo = sum(int(f["bytes"]) for f in filas[a:b])
            hora = filas[a]["hora_descarga_jst"]
            nombre = f"{camara}_{datetime.fromisoformat(hora):%Y%m%d_%H%M%S}"
            res.append((camara, video, inicio, largo, hora, nombre))
    return res


def procesar_trozo(t):
    camara, video, inicio, largo, hora, nombre = t
    os.makedirs(TROZOS, exist_ok=True)
    clip = os.path.join(TROZOS, nombre + ".ts")
    csv_trozo = os.path.join(SALIDA, "trozos", nombre + ".csv")
    if os.path.exists(csv_trozo + ".hecho"):
        return nombre, 0
    os.makedirs(os.path.dirname(csv_trozo), exist_ok=True)
    if os.path.exists(csv_trozo):
        os.remove(csv_trozo)                  # trozo a medias de una corrida anterior: se repite
    with open(video, "rb") as f, open(clip, "wb") as g:
        f.seek(inicio)
        quedan = largo
        while quedan:
            bloque = f.read(min(quedan, 64 << 20))
            g.write(bloque)
            quedan -= len(bloque)
    t0 = time.time()
    with open(os.path.join(SALIDA, "trozos", nombre + ".log"), "w", encoding="utf-8") as log:
        codigo = stiv(camara, clip, hora, csv_trozo, log, False)
    os.remove(clip)
    if codigo == 0:
        open(csv_trozo + ".hecho", "w").close()
    return nombre, time.time() - t0


def unir(camara):
    """reproduccion/<camara>.csv: los trozos de la camara, en orden de hora."""
    filas, cabecera = [], None
    for f in sorted(glob.glob(os.path.join(SALIDA, "trozos", f"{camara}_*.csv"))):
        with open(f, encoding="utf-8") as g:
            r = csv.reader(g)
            cabecera = next(r, None) or cabecera
            filas.extend(r)
    filas.sort(key=lambda x: (x[0], int(x[2])))
    with open(os.path.join(SALIDA, f"{camara}.csv"), "w", newline="", encoding="utf-8") as g:
        w = csv.writer(g)
        w.writerow(cabecera)
        w.writerows(filas)
    return len(filas)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--camaras", nargs="+", default=CAMARAS)
    ap.add_argument("--rapido", action="store_true")
    ap.add_argument("--trozos", type=int, default=4, help="--rapido: trozos por grabacion larga")
    ap.add_argument("--procesos", type=int, default=12, help="--rapido: trozos a la vez")
    a = ap.parse_args()
    if os.name == "nt":
        import ctypes
        # ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED: sin suspension mientras viva este
        # proceso. La pantalla tambien: en este portatil (espera moderna) apagar la pantalla por
        # inactividad lo suspendia aunque el sistema estuviera pedido (2026-10-25: 5.7 h dormido)
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x1 | 0x2)
    os.makedirs(SALIDA, exist_ok=True)
    t0 = time.time()
    if a.rapido:
        tareas = [t for c in a.camaras for t in trozos(c, a.trozos)]
        # los trozos mas grandes primero: el ultimo en acabar marca la duracion total
        tareas.sort(key=lambda t: -t[3])
        print(f"{len(tareas)} trozos, {a.procesos} a la vez", flush=True)
        with ThreadPool(a.procesos) as p:
            for i, (nombre, s) in enumerate(p.imap_unordered(procesar_trozo, tareas), 1):
                print(f"[{i}/{len(tareas)}] {nombre}: {s / 60:.0f} min (total {(time.time() - t0) / 60:.0f} min)",
                      flush=True)
        for c in a.camaras:
            print(f"{c}: {unir(c)} filas en reproduccion/{c}.csv", flush=True)
    else:
        hilos = [threading.Thread(target=tiempo_real, args=(c,)) for c in a.camaras]
        for h in hilos:
            h.start()
        for h in hilos:
            h.join()
    print(f"terminado en {(time.time() - t0) / 3600:.1f} h: {SALIDA}")


if __name__ == "__main__":
    main()
