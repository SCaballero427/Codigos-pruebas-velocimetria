"""Comprueba que los dos modulos reproducen los resultados de las pruebas.

- stiv_inicial.py  -> prueba 3 (Sile Main Canal), como el notebook de la v3.
- stiv_completo.py -> pruebas 3, 5, 6, 7 y 8, cada una con la configuracion de su notebook
  (v3, v5, v6, v7 y v8 de `evolucion_algoritmo_velocimetria/`).

Uso, desde esta carpeta y con el entorno de requirements_pyorc.txt:
    python validar.py                 # todas (unos 15 min: el video 4K del Sile es lo lento)
    python validar.py bradano arrow   # solo algunas: sile, hommerich, bradano, arrow, yaqui

Las pruebas 5 a 7 necesitan la carpeta de datasets externos (ver datos/externos/LEEME.md).
"""
import json
import os
import sys
import time
from pathlib import Path

import cv2
import numpy as np

import stiv_completo as st
import stiv_inicial

RAIZ = Path(__file__).resolve().parent.parent


def buscar_datasets():
    """Carpeta 'datasets vision velocimetria', donde este (igual que los notebooks v4 a v7)."""
    candidatos = [RAIZ / "datos/externos/datasets vision velocimetria"]
    if os.environ.get("DATASETS_VELOCIMETRIA"):
        candidatos.append(Path(os.environ["DATASETS_VELOCIMETRIA"]))
    candidatos.append(RAIZ.parent / "test_pyorc-20261009T172625Z-1-001/test_pyorc/datasets vision velocimetria")
    for c in candidatos:
        if c.is_dir():
            return c
    raise SystemExit("No se encuentran los datasets externos: ver datos/externos/LEEME.md")


def fps(archivo):
    cap = cv2.VideoCapture(str(archivo))
    f = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    return f


def informe(nombre, obtenido, esperado):
    print(f"  {nombre:<46} {obtenido:<26} notebook: {esperado}")


# =============================================================================== prueba 3
def sile():
    print("\n== Prueba 3, Sile Main Canal (v3) ==")
    video = RAIZ / "casos/02_smc_pyorc/entradas/SMC_estabilizado.mkv"
    sec = np.loadtxt(RAIZ / "datos/USGS/Station_Stage_SileCanal.csv", delimiter=",", skiprows=1)
    s, prof = sec[:, 0], sec[:, 1]
    fila_sup, fila_inf, ancho = 438, 1463, 1.8288
    escala = ancho / (fila_inf - fila_sup)

    t0 = time.time()
    r0 = stiv_inicial.medir_canal(video, s, prof, fila_sup, escala, 600, 3400, -1.0, 0.95, 0.92)
    informe("inicial: verticales medidas", f"{int(r0['medida'].sum())} de 11", "9 de 11")
    informe("inicial: caudal", f"{r0['caudal']:.4f} m3/s", "1.4484 m3/s")
    print(f"  ({time.time() - t0:.0f} s)")

    # La misma prueba con el modulo completo y las mejoras apagadas
    dt = 1.0 / fps(video)
    ds = int(round(0.95 * dt / escala))
    centros = np.column_stack([np.full(len(s), 2000.0), fila_sup + s / escala])
    mapx, mapy, nb = st.mapa_banda(centros, -1.0, ds, 3400 - 600, 0, 1)
    cfg = st.Configuracion(ds=ds, escala=escala, dt=dt, n_frames=250, derivadas="sobel")
    t0 = time.time()
    r = st.medir_video(video, mapx, mapy, nb, cfg)
    contorno = prof == 0
    medida, _ = st.control_calidad(r, cfg, es_contorno=contorno)
    q, _ = st.caudal(s, st.rellenar(s, r["v"], medida, contorno, "muro"), prof, 0.92)
    informe("completo, derivadas sobel: verticales medidas", f"{int(medida.sum())} de 11", "9 de 11")
    informe("completo, derivadas sobel: caudal", f"{q:.4f} m3/s", "1.4484 m3/s (aforo 1.4362)")
    print(f"  ({time.time() - t0:.0f} s)")

    # Las mismas STI con las derivadas por defecto de la version completa (diferencias centrales, v4)
    cfg.derivadas = "centrales"
    for i in range(len(s)):
        m, r["coherencia"][i] = st.medir_sti(r["sti_prep"][i], cfg.lado_bloque, cfg.coh_min_bloque,
                                             cfg.sigma_derivada)
        r["v"][i] = m * ds * escala / dt if np.isfinite(m) else np.nan
    medida, _ = st.control_calidad(r, cfg, es_contorno=contorno)
    q, _ = st.caudal(s, st.rellenar(s, r["v"], medida, contorno, "muro"), prof, 0.92)
    informe("completo, derivadas centrales: caudal", f"{q:.4f} m3/s", "(v4 en adelante)")


# =============================================================================== prueba 5
def hommerich():
    import pyproj
    print("\n== Prueba 5, rio Geul en Hommerich (v5) ==")
    d = buscar_datasets() / "Hommerich"
    video = d / "20241010_081717.mp4"
    datos = d / "hommerich_20241010_081717_pyorc_data.zip"
    cfg_cam = json.loads((datos / "cam_config_gcp1.json").read_text(encoding="utf-8"))
    pose = st.pose_camara(cfg_cam["gcps"]["src"], cfg_cam["gcps"]["dst"], cfg_cam["camera_matrix"],
                          cfg_cam["dist_coeffs"])
    informe("puntos de control: error mediano / maximo",
            f"{np.median(pose['error_px']):.2f} / {pose['error_px'].max():.2f} px", "0.56 / 2.50 px")
    z_agua = float(cfg_cam["gcps"]["z_0"]) + (93.345 - float(cfg_cam["gcps"]["h_ref"]))

    # La seccion en el sistema (u transversal, v aguas abajo), como en el notebook
    gj = json.loads((datos / "cs1_ordered.geojson").read_text(encoding="utf-8"))
    lon, lat, z = np.array([f["geometry"]["coordinates"] for f in gj["features"]], float).T
    x, y = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:28992", always_xy=True).transform(lon, lat)
    P = np.column_stack([x, y])
    mojado = z < z_agua
    centro = P[mojado].mean(axis=0)
    e_u = np.linalg.svd(P[mojado] - centro)[2][0]
    if np.dot(P[-1] - P[0], e_u) < 0:
        e_u = -e_u
    e_v = np.array([-e_u[1], e_u[0]])
    u = (P - centro) @ e_u
    idx = np.where(mojado)[0]
    bordes = []
    for a, b in ((idx[0] - 1, idx[0]), (idx[-1] + 1, idx[-1])):
        f = (z_agua - z[b]) / (z[a] - z[b])
        bordes.append(u[b] + f * (u[a] - u[b]))
    s = np.concatenate([[bordes[0]], u[idx], [bordes[1]]])
    prof = np.concatenate([[0.0], z_agua - z[idx], [0.0]])
    orden = np.argsort(s)
    s, prof = s[orden], prof[orden]
    centro = centro + 2.5 * e_v                       # seccion 2.5 m aguas abajo
    res, largo, margen = 0.01, 5.0, 0.6
    u0, u1, v1 = s[0] - margen, s[-1] + margen, largo / 2 + margen
    mapa = st.mapa_plano(pose, z_agua, centro, e_u, e_v, u0, u1, -v1, v1, res)

    dt = 1.0 / fps(video)
    ds = int(round(1.2 * dt / res))
    centros = np.column_stack([(s - u0) / res, np.full(len(s), mapa[0].shape[0] / 2)])
    mapx, mapy, nb = st.mapa_banda(centros, -90.0, ds, largo / res, 0, 1)
    cfg = st.Configuracion(ds=ds, escala=res, dt=dt, n_frames=250, lado_bloque=32, contraste_min=3.0)
    r = st.medir_video(video, mapx, mapy, nb, cfg, mapa_rect=mapa)
    contorno = prof == 0
    medida, _ = st.control_calidad(r, cfg, es_contorno=contorno)
    q, _ = st.caudal(s, st.rellenar(s, r["v"], medida, contorno, "rampa"), prof, 0.85)
    informe("verticales medidas", f"{int(medida.sum())} de {int((~contorno).sum())}", "12 de 16")
    informe("caudal", f"{q:.3f} m3/s", "12.922 m3/s")


# =============================================================================== prueba 6
def bradano():
    print("\n== Prueba 6, rio Bradano (v6) ==")
    video = buscar_datasets() / "data/RiverBradano/Stabilised/Video/RiverBradano_24_fps_Stabilised.avi"
    escala, dt = 0.009, 1.0 / fps(video)
    ds = int(round(0.9 * dt / escala))
    centros = np.column_stack([456 + 111 * np.arange(9), np.full(9, 706.0)])
    mapx, mapy, nb = st.mapa_banda(centros, -90.0, ds, 128 * 4, 24, 7)
    cfg = st.Configuracion(ds=ds, escala=escala, dt=dt, n_frames=600, brillo_max_agua=5.0)
    r = st.medir_video(video, mapx, mapy, nb, cfg)
    medida, motivos = st.control_calidad(r, cfg)
    informe("puntos medidos", f"{np.where(medida)[0].tolist()}", "[1, 2, 3, 4, 5]")
    informe("velocidad (valor central)", f"{np.nanmedian(r['v'][medida]):.4f} m/s", "0.7428 m/s")
    informe("rechazado por brillo", f"{[i for i, m in enumerate(motivos) if 'brillo de orilla' in m]}", "[8]")


# =============================================================================== prueba 7
def arrow():
    import pandas as pd
    print("\n== Prueba 7, rio Arrow (v7) ==")
    d = buscar_datasets() / "data/RiverArrow"
    videos = {
        "sin sembrar": d / "Stabilised/GoPro_Stable_trans_Unseeded/Video/Arrow_GoPro_Unseeded_Stabilised.avi",
        "sembrado": d / "Stabilised/GoPro_stable_trans_seeded/Video/Arrow_GoPro_Seeded_Stabilised.avi",
    }
    val = pd.read_excel(d / "Reference/Validation_Data_Arrow_GoPro.xlsx", header=None)
    filas, sec = [], None
    for _, fila in val.iloc[11:].iterrows():
        etq = str(fila[0])
        if etq.startswith("XS"):
            sec = etq
        elif sec is not None and etq.replace(".", "").isdigit():
            filas.append((sec, float(fila[0]), float(fila[1])))
    secciones = list(dict.fromkeys(f[0] for f in filas))
    angulos = {}
    for sc in secciones:
        p = np.array([(f[1], f[2]) for f in filas if f[0] == sc])
        dd = p[-1] - p[0]
        angulos[sc] = float(np.degrees(np.arctan2(-dd[0], dd[1])))       # normal a la seccion
    centros = np.array([(f[1], f[2]) for f in filas])
    angs = np.array([angulos[f[0]] for f in filas])

    escala, dt = 0.0174, 1.0 / fps(videos["sembrado"])
    ds = int(round(0.45 * dt / escala))
    mapx, mapy, nb = st.mapa_banda(centros, angs, ds, 48 * 5, 6, 3)
    valido, visible = st.cobertura(mapx, mapy, nb, (464, 505), margen=5)
    cfg = st.Configuracion(ds=ds, escala=escala, dt=dt, n_frames=600, lado_bloque=24, modulo=True,
                           cobertura_min=0.50)
    esperado = {"sin sembrar": "0 de 49", "sembrado": "38 de 49, 0.3978 m/s"}
    for etq, video in videos.items():
        r = st.medir_video(video, mapx, mapy, nb, cfg, valido=valido)
        medida, _ = st.control_calidad(r, cfg, fraccion_visible=visible)
        extra = f", {np.nanmedian(r['v'][medida]):.4f} m/s" if medida.any() else ""
        informe(f"{etq}: puntos medidos", f"{int(medida.sum())} de {len(medida)}{extra}", esperado[etq])

    saltos, parches = [1, 2, 4, 8], [(150, 150), (250, 200), (200, 250)]
    for etq, esp in (("sembrado", "0.725 0.559 0.337 0.154"), ("sin sembrar", "0.055 0.072 0.042 0.031")):
        curva = st.curva_decorrelacion(st.cargar_gris(videos[etq]), saltos, parches)
        informe(f"curva de decorrelacion, {etq}", " ".join(f"{c:.3f}" for c in curva), esp)


# =============================================================================== prueba 8
def yaqui():
    print("\n== Prueba 8, canal piloto Yaqui (v8) ==")
    video = RAIZ / "datos/canal_riego/WhatsApp Video 2026-08-16 at 8.07.12 PM.mp4"
    cap = cv2.VideoCapture(str(video))
    f_fps, n_total = cap.get(cv2.CAP_PROP_FPS), int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    _, fr0 = cap.read()
    cap.release()
    gris0 = cv2.cvtColor(fr0, cv2.COLOR_BGR2GRAY)
    alto, ancho = gris0.shape
    dt = 1.0 / f_fps

    # Geometria sin ninguna medida: orillas, punto de fuga y homografia con una lente supuesta
    focal, ymin, ymax, v_esp = 780.0, 1.40, 3.20, 0.056
    v1, (a_i, b_i), (a_d, b_d) = st.orillas_punto_fuga(gris0, 60, 560, 10)
    informe("punto de fuga", f"({v1[0]:.1f}, {v1[1]:.1f})", "(519.0, -53.1)")
    H1, _, _ = st.homografia_horizonte(v1, focal, ancho, alto, 0.0, ymax, 1.0)
    ys = np.linspace(120, 520, 9)

    def x_plano(a, b):
        q = cv2.perspectiveTransform(np.float32(np.column_stack([a * ys + b, ys])).reshape(-1, 1, 2), H1)
        return float(q.reshape(-1, 2)[:, 0].mean())
    x_izq, x_der = x_plano(a_i, b_i), x_plano(a_d, b_d)
    esc = 1.0 / (v_esp * dt)                          # 1 px del plano = lo que avanza el agua por fotograma
    xmin, xmax = x_izq - 0.2, x_der + 0.2
    H, _, _ = st.homografia_horizonte(v1, focal, ancho, alto, xmin, ymax, esc)
    tam = (int((xmax - xmin) * esc), int((ymax - ymin) * esc))
    mapa = st.mapa_homografia(H, tam)

    x_est = np.linspace(x_izq + 0.10, x_der - 0.10, 15)
    centros = np.column_stack([(x_est - xmin) * esc, np.full(15, tam[1] / 2)])
    ds = int(round(v_esp * dt * esc))
    mapx, mapy, nb = st.mapa_banda(centros, -90.0, ds, (ymax - ymin) * esc - 1, 0.10 * esc, 11)
    valido, visible = st.cobertura(mapx, mapy, nb, (ancho, alto), mapa_rect=mapa)

    # Ajustes de este video: filtro de restos y compensacion del movimiento de la mano
    mascara = np.zeros(gris0.shape, np.uint8)
    mascara[0:520, :] = 255
    agua = np.array([[b_i, 0], [b_d, 0], [a_d * alto + b_d, alto], [a_i * alto + b_i, alto]], np.int32)
    cv2.fillPoly(mascara, [agua], 0)
    estab = st.Estabilizador(gris0, mascara)
    cfg = st.Configuracion(ds=ds, escala=1.0 / esc, dt=dt, n_frames=n_total, cuantil_senal=0.85,
                           coh_min_estacion=0.60, cobertura_min=0.50, densidad_min=0.004,
                           densidad_max=0.05)
    r = st.medir_video(video, mapx, mapy, nb, cfg, mapa_rect=mapa, realce=st.realce_tophat(5, 0.8),
                       estabilizacion=estab, valido=valido)
    medida, _ = st.control_calidad(r, cfg, fraccion_visible=visible)
    informe("movimiento de la camara (mediana)", f"{np.median(estab.derivas):.2f} px", "6.70 px")
    informe("puntos medidos", f"{np.where(medida)[0].tolist()}", "[8, 9, 10, 11, 12, 13]")
    informe("velocidad (valor central)", f"{np.nanmedian(r['v'][medida]):.4f} alt. camara/s", "0.0571")


if __name__ == "__main__":
    PRUEBAS = dict(sile=sile, hommerich=hommerich, bradano=bradano, arrow=arrow, yaqui=yaqui)
    for nombre in (sys.argv[1:] or PRUEBAS):
        PRUEBAS[nombre]()
