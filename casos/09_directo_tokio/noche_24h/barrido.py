"""Barrido del analisis nocturno: pasa varios tramos de las grabaciones de 24 h por el programa, con el
metodo tal cual o con una VARIANTE (cambios del metodo que se prueban sin tocar stiv_directo.py), en
paralelo, y guarda un json por (variante, camara, tramo) en resultados/.

    python barrido.py base                         # todas las camaras, todos los tramos
    python barrido.py base --camaras shimoda --tramos 19:00 21:00
    python barrido.py resumen base                 # tabla noche/dia por estacion

Tramos de AJUSTE y de COMPROBACION separados: las variantes se eligen mirando solo los de ajuste, y los
de comprobacion se miran una vez, al final.

La referencia de dia tiene que ser del MISMO NIVEL que la noche: el 24 llovio de 8 a 14 h y el Myoshoji
(la unica estacion cuyo sensor ve el agua) paso de 1.21 m por la manana a 1.28-1.29 m de 14 h a 0 h, y
volvio a 1.21-1.23 m de madrugada. La primera mitad de la noche se compara con la tarde (15 y 16 h), la
madrugada con la manana (6:30 y 7:30), y las 1 h (1.26 m) con las dos. Las otras camaras no tienen nivel
util (sensor en 0.00); se asume la misma evolucion (la misma lluvia).
"""
import argparse, json, os, sys, time
from multiprocessing import Pool

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "resultados")
CAMARAS = ["myoshoji", "kurome", "shimoda", "akigawa"]
SEGUNDOS = 180            # 3 min: llena las tres escalas (10, 30 y 60 s) y deja 2 min de medidas
T_DESCARTE = 60.0         # las medidas de antes no tienen aun las escalas lentas llenas
MANANA = ["2026-10-24T06:30", "2026-10-24T07:30"]
TARDE = ["2026-10-24T15:00", "2026-10-24T16:00"]
DIA = MANANA + ["2026-10-24T13:00"] + TARDE
AJUSTE = ["2026-10-24T19:00", "2026-10-24T23:00", "2026-10-25T03:00"]
COMPROBACION = ["2026-10-24T21:00", "2026-10-25T01:00", "2026-10-25T04:30"]
TRAMOS = DIA + AJUSTE + COMPROBACION
# transiciones: en 30-40 min el caudal no cambia y la luz si; un metodo que no dependa de la luz da lo
# mismo a un lado y a otro (el amanecer del 24 esta en el primer tramo de la grabacion)
AMANECER = ["2026-10-24T05:26", "2026-10-24T05:40", "2026-10-24T05:55", "2026-10-24T06:10", "2026-10-24T06:30"]
ATARDECER = ["2026-10-24T16:30", "2026-10-24T16:50", "2026-10-24T17:10", "2026-10-24T17:30",
             "2026-10-24T17:50", "2026-10-24T18:10"]


def variante_base(sd):
    """El metodo tal cual."""


def sin_motas(sd):
    """Quita el reintento con el realce de motas que el modo dia hace en las estaciones que fallan: de
    noche las 'motas' son destellos de farola."""
    medir = sd.medir
    sd.medir = lambda *a, **k: medir(*a[:5], None, **{x: y for x, y in k.items() if x != "buffers_motas"})


def excluir_brillo(sd, umbral):
    """Proceso de dia, pero las posiciones cuyo brillo mediano supera `umbral` (los reflejos de las
    farolas) no cuentan: actividad 0, como el deslumbramiento del modo noche. Solo vale con el proceso
    de dia, en el que el buffer guarda el gris tal cual."""
    construir = sd.construir_stis

    def nuevo(buffer, lag, modo="dia"):
        sti, act = construir(buffer, lag, modo)
        if modo == "dia":
            med = np.median(buffer[::4], axis=0).reshape(sd.N_ESTACIONES, sd.LINEAS_BANDA, -1)
            for i in range(sd.N_ESTACIONES):
                act[i][:, (med[i] > umbral).any(axis=0)] = 0
        return sti, act
    sd.construir_stis = nuevo


def actividad(sd, valor):
    sd.ACTIVIDAD_MIN = valor


# nombre -> (cambios del metodo, argumentos de correr_tramo)
VARIANTES = {
    # "base" es el programa de ANTES de este analisis (noche solo por la imagen): sus tramos de dia y de
    # noche se calcularon antes de anadir el sol a stiv_directo.py. "nuevo" es el programa corregido.
    "base": (variante_base, {}),
    "nuevo": (variante_base, {}),
    "dia": (sin_motas, {"modo": "dia"}),
    "dia_motas": (variante_base, {"modo": "dia"}),
    "noche": (variante_base, {"modo": "noche"}),
    "dia_brillo60": (lambda sd: (sin_motas(sd), excluir_brillo(sd, 60)), {"modo": "dia"}),
    "dia_brillo40": (lambda sd: (sin_motas(sd), excluir_brillo(sd, 40)), {"modo": "dia"}),
    "noche_act02": (lambda sd: actividad(sd, 0.2), {"modo": "noche"}),
    "dia_act02": (lambda sd: (sin_motas(sd), actividad(sd, 0.2)), {"modo": "dia"}),
}


def trabajo(args):
    variante, camara, tramo = args
    ruta = os.path.join(RES, variante, f"{camara}_{tramo.replace(':', '')}.json")
    if os.path.exists(ruta):
        return ruta
    import tramo as tr
    sd = tr.sd
    cambios, kw = VARIANTES[variante]
    cambios(sd)
    t0 = time.time()
    geom, med, stis, h0 = tr.correr_tramo(camara, tramo, SEGUNDOS, verbose=False, **kw)
    med = [(t, res) for t, res in med if t >= T_DESCARTE]
    pe = tr.por_estacion(med, sd.N_ESTACIONES)
    acc = [r["v"] for _, res in med for r in res if r["aceptada"]]
    modos = sorted({r["modo"] for _, res in med for r in res})
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    json.dump({"variante": variante, "camara": camara, "tramo": tramo, "inicio_jst": h0.isoformat(),
               "modos": modos, "n_medidas": len(med), "aceptadas": len(acc),
               "mediana": float(np.median(acc)) if acc else None, "estaciones": pe,
               "segundos_proceso": round(time.time() - t0)},
              open(ruta, "w", encoding="utf-8"), indent=1, default=float)
    if stis:
        os.makedirs(os.path.join(RES, variante, "sti"), exist_ok=True)
        tr.guardar_stis(stis[-1], os.path.join(RES, variante, "sti", os.path.basename(ruta)[:-5] + ".png"))
    return ruta


def cargar(variante, camara, tramo):
    ruta = os.path.join(RES, variante, f"{camara}_{tramo.replace(':', '')}.json")
    return json.load(open(ruta, encoding="utf-8")) if os.path.exists(ruta) else None


def referencia(ref, cam, tramos):
    """Velocidad de dia por estacion: mediana de los tramos con >= 10 medidas aceptadas."""
    dia = [cargar(ref, cam, t) for t in tramos]
    vd = []
    for i in range(9):
        vs = [d["estaciones"][i]["v"] for d in dia if d and d["estaciones"][i]["aceptadas"] >= 10]
        vd.append(float(np.median(vs)) if vs else np.nan)
    return vd


def ref_de(tramo):
    """Tramos de dia con el mismo nivel que un tramo de noche (ver arriba)."""
    h = int(tramo[11:13])
    return TARDE if 17 <= h <= 23 else MANANA if 2 <= h <= 6 else TARDE + MANANA


def resumen(variante, camaras, ref="base"):
    """Por camara y estacion: referencia de dia del mismo nivel (con la variante `ref`) y cada tramo de
    noche con `variante`, como v (fraccion aceptada) cociente noche/dia."""
    for cam in camaras:
        print(f"\n== {cam}  (referencia de dia con '{ref}': manana {', '.join(t[11:] for t in MANANA)}; "
              f"tarde {', '.join(t[11:] for t in TARDE)})")
        print("            " + " ".join(f"  est{i}   " for i in range(9)))
        for nombre, tr in (("manana", MANANA), ("tarde", TARDE)):
            vd = referencia(ref, cam, tr)
            print(f"{nombre:12s}" + " ".join(f"{v:+.2f}     " if np.isfinite(v) else "  --      " for v in vd))
        for t in AJUSTE + COMPROBACION:
            d = cargar(variante, cam, t)
            if not d:
                continue
            vd = referencia(ref, cam, ref_de(t))
            celdas = []
            for i, p in enumerate(d["estaciones"]):
                frac = p["aceptadas"] / max(p["n"], 1)
                if p["aceptadas"] and np.isfinite(vd[i]) and vd[i]:
                    celdas.append(f"{p['v']:+.2f}({frac:.0%}){p['v'] / vd[i]:4.2f}"[:10].ljust(10))
                elif p["aceptadas"]:
                    celdas.append(f"{p['v']:+.2f}({frac:.0%})".ljust(10))
                else:
                    m = max(p["motivos"], key=p["motivos"].get) if p["motivos"] else "-"
                    celdas.append(m[:9].ljust(10))
            marca = "A" if t in AJUSTE else "C"
            print(f"{marca} {t[5:16]:10s}" + " ".join(celdas) + f" | {'/'.join(d['modos'])}")


def transicion(variante, camaras):
    """Cada tramo del amanecer y del atardecer, por estacion: v (fraccion aceptada) y el modo."""
    for cam in camaras:
        print(f"\n== {cam} '{variante}'")
        for t in AMANECER + ATARDECER:
            d = cargar(variante, cam, t)
            if not d:
                continue
            celdas = [f"{p['v']:+.2f}({p['aceptadas'] / max(p['n'], 1):.0%})".ljust(11) if p["aceptadas"]
                      else (max(p["motivos"], key=p["motivos"].get) if p["motivos"] else "-")[:10].ljust(11)
                      for p in d["estaciones"]]
            print(f"{t[11:16]} " + " ".join(celdas) + f" | {'/'.join(d['modos'])}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("variante")
    ap.add_argument("extra", nargs="?")
    ap.add_argument("--camaras", nargs="+", default=CAMARAS)
    ap.add_argument("--tramos", nargs="+", default=TRAMOS)
    ap.add_argument("--procesos", type=int, default=8)
    a = ap.parse_args()
    if a.variante == "resumen":
        resumen(a.extra, a.camaras)
        return
    if a.variante == "transicion":
        transicion(a.extra, a.camaras)
        return
    tramos = [t if "T" in t else f"2026-10-24T{t}" for t in a.tramos]
    tareas = [(a.variante, c, t) for c in a.camaras for t in tramos]
    t0 = time.time()
    with Pool(a.procesos) as p:
        for i, r in enumerate(p.imap_unordered(trabajo, tareas), 1):
            print(f"[{i}/{len(tareas)}] {os.path.basename(r)} ({time.time() - t0:.0f} s)", flush=True)


if __name__ == "__main__":
    main()
