"""Pasa un tramo de las grabaciones de 24 h (verificacion_nivel/grabaciones/<camara>_*JST.ts) por el
programa (validacion/correr.py, el mismo codigo que en directo), eligiendo el tramo por HORA DE JAPON.

    python tramo.py shimoda 05:26 120                   # 120 s desde las 05:26 JST del 24
    python tramo.py shimoda 2026-10-25T03:00 180        # otra fecha
    python tramo.py shimoda 05:26 120 --modo dia        # forzando el modo
    python tramo.py shimoda 05:26 120 --sti sti.png     # guarda los STI de la ultima medida
    python tramo.py kurome 20:00 600 --csv kurome.csv   # CSV con las columnas de medidas_directo.csv

En estas .ts NO se puede saltar con CAP_PROP_POS_MSEC: el PTS sigue al reloj real, asi que los huecos
de la grabacion (el PC suspendido) son saltos de PTS, y OpenCV cae en otro sitio al buscar (pedido
20000 s -> 25930 s). En vez de saltar, el tramo se COPIA byte a byte: cada segmento HLS empieza por un
fotograma clave y el _segmentos.csv da sus bytes, asi que los segmentos que cubren el tramo forman un
.ts pequeno que se decodifica solo, sin recomprimir (clips/). La hora JST de cada medida es la hora de
descarga del primer segmento mas el tiempo dentro del clip (unos segundos de retraso respecto al
directo, sin importancia aqui).
"""
import argparse, csv, glob, os, sys
from datetime import datetime, timedelta, timezone

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "validacion"))
from correr import correr_camara, por_estacion       # noqa: E402
import stiv_directo as sd                            # noqa: E402

JST = timezone(timedelta(hours=9))
GRAB = os.path.join(AQUI, "..", "verificacion_nivel", "grabaciones")
CLIPS = os.path.join(AQUI, "clips")
FECHA_POR_DEFECTO = "2026-10-24"


def a_hora(hora, fecha=FECHA_POR_DEFECTO):
    return datetime.fromisoformat(hora if "T" in hora else f"{fecha}T{hora}").replace(tzinfo=JST)


def recortar(camara, desde, segundos):
    """Copia a clips/ los segmentos que cubren [desde, desde + segundos]: (ruta, hora JST del inicio)."""
    for seg in sorted(glob.glob(os.path.join(GRAB, f"{camara}_*JST_segmentos.csv"))):
        filas = list(csv.DictReader(open(seg, encoding="utf-8")))
        if not filas:
            continue
        horas = [datetime.fromisoformat(f["hora_descarga_jst"]) for f in filas]
        if not horas[0] <= desde <= horas[-1]:
            continue
        i = max(k for k, h in enumerate(horas) if h <= desde)
        j = i
        while j + 1 < len(filas) and horas[j + 1] < desde + timedelta(seconds=segundos):
            j += 1
        inicio = sum(int(f["bytes"]) for f in filas[:i])
        largo = sum(int(f["bytes"]) for f in filas[i:j + 1])
        os.makedirs(CLIPS, exist_ok=True)
        ruta = os.path.join(CLIPS, f"{camara}_{horas[i]:%Y%m%d_%H%M%S}_{j - i + 1}seg.ts")
        if not os.path.exists(ruta) or os.path.getsize(ruta) != largo:
            with open(seg.replace("_segmentos.csv", ".ts"), "rb") as f:
                f.seek(inicio)
                datos = f.read(largo)
            with open(ruta, "wb") as g:
                g.write(datos)
        return ruta, horas[i]
    raise SystemExit(f"ninguna grabacion de {camara} contiene {desde:%Y-%m-%d %H:%M} JST")


def correr_tramo(camara, hora, segundos, modo="auto", fecha=FECHA_POR_DEFECTO, verbose=True, ajustes=None):
    """Devuelve (geom, medidas, stis, hora JST del inicio del clip); stis = [medida][estacion]."""
    clip, h0 = recortar(camara, a_hora(hora, fecha), segundos)
    if verbose:
        print(f"{camara} {h0:%Y-%m-%d %H:%M:%S} JST, {segundos:.0f} s -> {os.path.basename(clip)}")
    stis, medir_original = [], sd.medir

    def medir_y_guardar(*a, **k):
        # correr.bucle tira los STI; aqui se guardan antes, sin tocar el programa
        res = medir_original(*a, **k)
        stis.append([r.get("sti") for r in res])
        return res

    sd.medir = medir_y_guardar
    try:
        geom, med = correr_camara(clip, camara, modo, segundos, verbose, ajustes, hora_inicio=h0)
    finally:
        sd.medir = medir_original
    return geom, med, stis, h0


def resumen(med, titulo=""):
    pe = por_estacion(med, sd.N_ESTACIONES)
    acc = [r["v"] for _, res in med for r in res if r["aceptada"]]
    print(f"{titulo} " + " ".join(f"{p['v']:+.2f}/{p['aceptadas']}" if p["aceptadas"] else "--" for p in pe))
    print(f"   aceptadas {len(acc)} de {len(med) * sd.N_ESTACIONES}, mediana {np.median(acc) if acc else float('nan'):+.3f}")
    for p in pe:
        if p["motivos"]:
            print(f"   est {p['estacion']}: {p['motivos']}")
    return pe


def guardar_csv(med, h0, ruta):
    """Las mismas columnas que salidas/<camara>/medidas_directo.csv, con la hora JST de la grabacion en
    vez de la hora local del PC, y el segundo del clip en vez del del flujo."""
    verificada = int(bool(sd.cargar_config().get("escala_verificada")))
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["hora_jst", "t_clip_s", "estacion", "y_m", "v_m_s", "coherencia", "bloques_activos",
                    "aceptada", "motivos", "escala_verificada", "s_por_fila", "modo"])
        for t, res in med:
            hora = (h0 + timedelta(seconds=t)).isoformat(timespec="seconds")
            for r in res:
                w.writerow([hora, f"{t:.2f}", r["estacion"], f"{r['y_m']:.3f}", f"{r['v']:.4f}",
                            f"{r['coherencia']:.3f}", r["bloques_activos"], int(r["aceptada"]), r["motivos"],
                            verificada, f"{r['dt_fila']:.3f}", r["modo"] + ("+motas" if r.get("motas") else "")])


def guardar_stis(stis_medida, ruta):
    import cv2
    tiras = []
    for s in stis_medida:
        if s is None:
            continue
        s = np.asarray(s, dtype=np.float32)
        s = cv2.normalize(s, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        tiras.append(cv2.resize(s, (160, 300), interpolation=cv2.INTER_NEAREST))
        tiras.append(np.full((300, 4), 255, np.uint8))
    if tiras:
        cv2.imwrite(ruta, np.hstack(tiras))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("camara")
    ap.add_argument("hora", help="HH:MM[:SS] hora de Japon (del --fecha), o AAAA-MM-DDTHH:MM")
    ap.add_argument("segundos", type=float)
    ap.add_argument("--fecha", default=FECHA_POR_DEFECTO)
    ap.add_argument("--modo", default="auto", choices=("auto", "dia", "noche"))
    ap.add_argument("--sti", help="png con los STI de la ultima medida")
    ap.add_argument("--csv", help="CSV con todas las medidas, como medidas_directo.csv")
    a = ap.parse_args()
    geom, med, stis, h0 = correr_tramo(a.camara, a.hora, a.segundos, a.modo, a.fecha)
    resumen(med, f"{a.camara} {a.hora}")
    if a.csv:
        guardar_csv(med, h0, a.csv)
    if a.sti and stis:
        guardar_stis(stis[-1], a.sti)


if __name__ == "__main__":
    main()
