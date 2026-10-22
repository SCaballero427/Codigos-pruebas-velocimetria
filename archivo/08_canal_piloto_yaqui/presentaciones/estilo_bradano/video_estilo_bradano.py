"""Canal piloto Yaqui: video de velocidad con el mismo formato que el del rio Bradano.

Que produce
-----------
`salidas/velocidad_tiempo_real.mp4` (H.264, tiempo real), `salidas/velocidad_ventanas.csv` y
`salidas/config_video_velocidad.json`: los mismos tres ficheros, con los mismos nombres, que
`casos/06_bradano_stiv/video_velocidad.py`.

Que es y que no es
------------------
Leelo antes de usar el video, porque **en pantalla no se dice** (es lo que se pidio):

- **La escala metrica es simulada.** Este video no tiene ningun dato de campo, asi que el caso
  mide en alturas de camara. Aqui se supone un ancho de lamina de `ANCHO_LAMINA_M` metros, que
  fija los m/s y los mm/px de la cabecera. Con 5 m sale una camara a ~2.2 m sobre el agua,
  coherente con un movil sostenido desde la pasarela que se ve al pie del encuadre.
- **Las velocidades no se miden aqui.** Se leen de `../seccion_completa/salidas/perfil_seccion.csv`:
  las estaciones 8 a 13 son medida STIV directa, y las 1 a 7 son **deducidas** del perfil
  Shiono-Knight escalado por las que miden (ver el README de `seccion_completa/`).
- Las estaciones 0 y 14 se dibujan como rechazadas, igual que las de orilla del Bradano. Eso si
  coincide con la medida real: el caso las rechaza (coherencia y cota fisica la 0, orilla la 14).

El CSV y el JSON de salida si dicen que estaciones son medida directa.

Por que un solo panel
---------------------
Por parecerse al Bradano, que es cenital y solo tiene uno. Aqui el panel es el plano del agua
**rectificado** con la geometria del caso (`stiv_canal.Geometria`), estabilizado fotograma a
fotograma contra el primero, igual que en los otros videos del canal. La vista de la camara no
se ensena.

Uso
---
    python video_estilo_bradano.py                   # ~3 min
    python video_estilo_bradano.py --frames 300      # prueba corta
    python video_estilo_bradano.py --muestra 900     # solo un PNG del fotograma 900
"""
import argparse
import csv
import json
import os
import sys
import time

import cv2
import numpy as np

_RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))  # raiz del proyecto
_CANAL = os.path.join(_RAIZ, "archivo", "08_canal_piloto_yaqui")
sys.path.insert(0, os.path.join(_CANAL, "medicion"))
import escritor_video as ev        # noqa: E402
import stiv_canal as sc            # noqa: E402

DIR_CASO = os.path.dirname(os.path.abspath(__file__))
DIR_SALIDAS = os.path.join(DIR_CASO, "salidas")
DIR_SECCION = os.path.join(_CANAL, "presentaciones", "seccion_completa", "salidas")

# ----------------------------------------------------------------------------------
# >>> AJUSTABLE <<<  Escala metrica SIMULADA
# ----------------------------------------------------------------------------------
# Ancho de la lamina de agua entre las dos orillas detectadas, en metros. NO esta medido: es la
# unica cifra que convierte alturas de camara en metros. 5 m da una camara a ~2.2 m del agua.
ANCHO_LAMINA_M = 5.0
# Estaciones que se dibujan como rechazadas (cuadro rojo). Son las que el caso rechaza de verdad.
ESTACIONES_RECHAZADAS = (0, 14)

# ----------------------------------------------------------------------------------
# >>> AJUSTABLE <<<  Lenguaje visual, copiado de casos/06_bradano_stiv/video_velocidad.py
# ----------------------------------------------------------------------------------
ANCHO_LIENZO = 1920
ALTO_PANEL = 630
ALTO_CABECERA = 44
ALTO_PIE = 96
# px de panel por altura de camara. 520 deja el canal en ~1170 px y deja ver las dos orillas.
ESCALA_PANEL = 520.0
# Borde inferior del panel, en alturas de camara. Por debajo entra la pasarela en sombra.
Y_PANEL0 = 1.50
# Largo de la linea de busqueda dibujada, en px (en el Bradano 128 muestras x 4 px).
LARGO_LINEA_PX = 512
V_COLOR_MAX = 0.20                 # m/s; el Bradano usa 1.5, aqui el agua va casi 5 veces mas lenta
PX_POR_MS = 900                    # el Bradano usa 190; mismo largo de flecha en pantalla
PCT_REALCE = (1.0, 99.5)

PALETA = cv2.applyColorMap(np.arange(256, dtype=np.uint8).reshape(-1, 1),
                           cv2.COLORMAP_TURBO).reshape(-1, 3)


def color_velocidad(v):
    """Color BGR de una velocidad. Gris si no hay medida."""
    if not np.isfinite(v):
        return (120, 120, 120)
    return tuple(int(x) for x in PALETA[int(np.clip(v / V_COLOR_MAX, 0, 1) * 255)])


def texto(img, s, org, escala=0.5, col=(255, 255, 255), grosor=1):
    """Texto con reborde negro: sobre el agua el blanco solo no se lee."""
    cv2.putText(img, s, org, cv2.FONT_HERSHEY_SIMPLEX, escala, (0, 0, 0), grosor + 2,
                cv2.LINE_AA)
    cv2.putText(img, s, org, cv2.FONT_HERSHEY_SIMPLEX, escala, col, grosor, cv2.LINE_AA)


def leer_perfil():
    """Velocidades (ventanas x estaciones) en alturas de camara/s, y cuales son medida directa."""
    filas = list(csv.DictReader(open(os.path.join(DIR_SECCION, "perfil_seccion.csv"),
                                     encoding="utf-8")))
    nk = max(int(f["ventana"]) for f in filas) + 1
    ne = max(int(f["estacion"]) for f in filas) + 1
    V = np.full((nk, ne), np.nan)
    mide = np.zeros((nk, ne), bool)
    centros = np.zeros(nk, int)
    for f in filas:
        k, a = int(f["ventana"]), int(f["estacion"])
        V[k, a] = float(f["v"])
        mide[k, a] = f["medida_directa"] == "1"
        centros[k] = int(f["centro_frame"])
    return centros, V, mide


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--video", default=sc.ARCHIVO_VIDEO)
    ap.add_argument("--frames", type=int, default=None)
    ap.add_argument("--muestra", type=int, default=None,
                    help="escribe solo el PNG de este fotograma y termina")
    ap.add_argument("--salida", default=os.path.join(DIR_SALIDAS, "velocidad_tiempo_real.mp4"))
    a = ap.parse_args()
    os.makedirs(DIR_SALIDAS, exist_ok=True)

    centros, V_u, mide = leer_perfil()
    cfg_sec = json.load(open(os.path.join(DIR_SECCION, "config_seccion.json"), encoding="utf-8"))
    nk, ne = V_u.shape

    cap, ntot, fps = sc.abrir_video(a.video)
    ok, f0 = cap.read()
    g0 = cv2.cvtColor(f0, cv2.COLOR_BGR2GRAY)
    geo = sc.Geometria(g0)
    Xs = geo.estaciones()
    m_por_u = ANCHO_LAMINA_M / geo.ancho
    V = V_u * m_por_u
    sobre_agua = np.ones(ne, bool)
    sobre_agua[list(ESTACIONES_RECHAZADAS)] = False
    V[:, ~sobre_agua] = np.nan
    v_mediana = np.nanmedian(V, axis=1)
    aceptadas = np.isfinite(V).sum(axis=1)
    print("escala simulada: %.3f m por altura de camara (lamina de %.1f m)"
          % (m_por_u, ANCHO_LAMINA_M))
    print("mediana de la seccion: %.4f m/s  q05-q95 %.4f-%.4f"
          % (np.median(v_mediana), np.quantile(v_mediana, 0.05), np.quantile(v_mediana, 0.95)))

    # Lienzo rectificado centrado en el canal
    Xc = 0.5 * (geo.X_izq + geo.X_der)
    semi = 0.5 * ANCHO_LIENZO / ESCALA_PANEL
    rst = dict(X0=Xc - semi, X1=Xc + semi, Y0=Y_PANEL0, Y1=Y_PANEL0 + ALTO_PANEL / ESCALA_PANEL,
               w=ANCHO_LIENZO, h=ALTO_PANEL, escala=ESCALA_PANEL)
    mp_pts = np.ascontiguousarray(geo.mapa_rect(rst).reshape(-1, 2))
    ph, pw = ALTO_PANEL, ANCHO_LIENZO
    Ysec = 0.5 * (rst["Y0"] + rst["Y1"])
    cols = geo.rect_a_pix(rst, np.column_stack([Xs, np.full(ne, Ysec)]))[:, 0]
    yf = ph // 2
    c_izq = int(round(geo.rect_a_pix(rst, [[geo.X_izq, Ysec]])[0, 0]))
    c_der = int(round(geo.rect_a_pix(rst, [[geo.X_der, Ysec]])[0, 0]))
    mm_px = m_por_u / ESCALA_PANEL * 1000.0
    banda_px = sc.BANDA * ESCALA_PANEL
    t_ventana = cfg_sec["ventana"] / fps

    # Estabilizacion: mismos puntos y misma mascara que pasada_sti de medicion/video_velocidad.py
    mask = np.zeros(g0.shape, np.uint8)
    mask[0:sc.FILA_BORDE_FIN - 40, :] = 255
    cv2.fillPoly(mask, [geo.poligono_agua()], 0)
    p0 = cv2.goodFeaturesToTrack(g0, 600, 0.01, 7, mask=mask)

    NF = ntot if a.frames is None else min(a.frames, ntot)
    if a.muestra is not None:
        NF = a.muestra + 1
    ch = ALTO_CABECERA + ph + ALTO_PIE
    vw = None if a.muestra is not None else ev.abrir(a.salida, fps, (pw, ch))

    lo = hi = None
    t0 = time.time()
    g = g0
    for k in range(NF):
        if k > 0:
            ok, fr = cap.read()
            if not ok:
                break
            g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        if a.muestra is not None and k < a.muestra:
            continue
        A, _ = sc.estimar_estabilizacion(g0, g, p0)
        qq = mp_pts @ A[:, :2].T + A[:, 2]
        rect = cv2.remap(g, qq[:, 0].reshape(ph, pw).astype(np.float32),
                         qq[:, 1].reshape(ph, pw).astype(np.float32), cv2.INTER_CUBIC,
                         borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        if lo is None:
            # Percentiles fijos, sobre lo que cae dentro del fotograma
            dentro = rect[rect > 0]
            lo, hi = np.percentile(dentro, PCT_REALCE)
        realce = np.clip((rect.astype(np.float32) - lo) / (hi - lo) * 255, 0, 255).astype(np.uint8)
        panel = cv2.cvtColor(realce, cv2.COLOR_GRAY2BGR)

        w = int(np.argmin(np.abs(centros - k)))
        for c in (c_izq, c_der):
            cv2.line(panel, (c, 0), (c, ph - 1), (60, 200, 60), 1, cv2.LINE_AA)
        for i, c in enumerate(cols):
            c = int(round(c))
            v = V[w, i]
            col = color_velocidad(v)
            cv2.line(panel, (c, yf - LARGO_LINEA_PX // 2), (c, yf + LARGO_LINEA_PX // 2),
                     col if np.isfinite(v) else (90, 90, 90), 1, cv2.LINE_AA)
            if np.isfinite(v):
                cv2.arrowedLine(panel, (c, yf), (c, int(yf - v * PX_POR_MS)),
                                col, 3, cv2.LINE_AA, tipLength=0.18)
                cv2.circle(panel, (c, yf), 5, (255, 255, 255), -1, cv2.LINE_AA)
                cv2.circle(panel, (c, yf), 5, (0, 0, 0), 1, cv2.LINE_AA)
                texto(panel, f"{v:.2f}", (c + 8, yf + 26), 0.55, (255, 255, 255), 1)
            else:
                cv2.drawMarker(panel, (c, yf), (60, 60, 220), cv2.MARKER_SQUARE, 11, 2)
            texto(panel, f"{i}", (c - 6 - 5 * (i >= 10), yf + 60), 0.5, (230, 230, 230), 1)

        lienzo = np.zeros((ch, pw, 3), np.uint8)
        lienzo[ALTO_CABECERA:ALTO_CABECERA + ph] = panel
        texto(lienzo, "Canal piloto Yaqui - STIV en ventana movil sobre el video completo",
              (16, 30), 0.72, (255, 255, 255), 2)
        texto(lienzo, f"ventana {t_ventana:.2f} s   escala {mm_px:.1f} mm/px   "
                      f"banda {banda_px:.0f} px   contraste realzado",
              (pw - 670, 30), 0.55, (170, 170, 170), 1)

        bx, by, bw_, bh_ = pw - 400, ch - 34, 260, 14
        for j in range(bw_):
            c_ = PALETA[int(255 * j / (bw_ - 1))]
            cv2.line(lienzo, (bx + j, by), (bx + j, by + bh_), tuple(int(x) for x in c_), 1)
        cv2.rectangle(lienzo, (bx, by), (bx + bw_, by + bh_), (90, 90, 90), 1)
        texto(lienzo, "0", (bx - 14, by + 12), 0.45, (170, 170, 170), 1)
        texto(lienzo, f"{V_COLOR_MAX:.1f} m/s", (bx + bw_ + 8, by + 12), 0.45, (170, 170, 170), 1)

        y_pie = ALTO_CABECERA + ph
        vm = v_mediana[w]
        texto(lienzo, f"t = {k/fps:5.2f} s", (16, y_pie + 32), 0.7, (255, 255, 255), 2)
        texto(lienzo, f"v superficial mediana = {vm:.3f} m/s", (210, y_pie + 32), 0.7,
              (120, 220, 255), 2)
        texto(lienzo, f"estaciones medidas = {aceptadas[w]}/{ne}",
              (700, y_pie + 32), 0.7, (150, 255, 150), 2)
        texto(lienzo, "circulo = estacion medida   cuadro rojo = rechazada (coherencia baja "
                      "o cota fisica)", (16, y_pie + 62), 0.48, (170, 170, 170), 1)
        texto(lienzo, "la direccion de las flechas no se mide: es el ANGULO_FLUJO que STIV "
                      "recibe como configuracion. El sentido si sale del tensor",
              (16, y_pie + 84), 0.48, (140, 140, 140), 1)

        if a.muestra is not None:
            ruta = os.path.join(DIR_SALIDAS, "muestra_%d.png" % k)
            cv2.imwrite(ruta, lienzo)
            print("muestra: %s" % ruta)
            return
        vw.write(lienzo)
        if (k + 1) % 300 == 0:
            print("  render %d/%d (%.1f s)" % (k + 1, NF, time.time() - t0), flush=True)
    cap.release()
    vw.release()
    print("escrito: %s (%dx%d, %d fotogramas, %.1f s)" % (a.salida, pw, ch, NF, NF / fps))

    with open(os.path.join(DIR_SALIDAS, "velocidad_ventanas.csv"), "w", newline="",
              encoding="utf-8") as fh:
        esc = csv.writer(fh)
        esc.writerow(["ventana", "frame_centro", "t_s", "v_mediana_ms", "n_estaciones"]
                     + [f"v_est{i}" for i in range(ne)])
        for w, kc in enumerate(centros):
            esc.writerow([w, int(kc), round(kc / fps, 3), round(float(v_mediana[w]), 4),
                          int(aceptadas[w])]
                         + ["" if not np.isfinite(V[w, i]) else round(float(V[w, i]), 4)
                            for i in range(ne)])
    with open(os.path.join(DIR_SALIDAS, "config_video_velocidad.json"), "w",
              encoding="utf-8") as fh:
        json.dump(dict(
            video=a.video, n_frames=NF, fps=round(fps, 4),
            ancho_lamina_m_SIMULADO=ANCHO_LAMINA_M, m_por_altura_camara=round(m_por_u, 6),
            ancho_canal_alturas_camara=geo.ancho, escala_panel_px=ESCALA_PANEL,
            mm_por_px_panel=round(mm_px, 4), estaciones_X=[round(float(x), 4) for x in Xs],
            estaciones_rechazadas_en_pantalla=list(ESTACIONES_RECHAZADAS),
            estaciones_con_medida_directa=[int(x) for x in np.where(mide.any(axis=0))[0]],
            estaciones_deducidas_del_modelo=[int(x) for x in np.where(~mide.any(axis=0))[0]
                                             if sobre_agua[x]],
            velocidades_de="presentaciones/seccion_completa/salidas/perfil_seccion.csv",
            ventana=cfg_sec["ventana"], paso_ventana=cfg_sec["paso"], n_ventanas=nk,
            v_color_max_ms=V_COLOR_MAX, px_por_ms=PX_POR_MS,
            v_mediana_global_ms=round(float(np.median(v_mediana)), 6),
            q05=round(float(np.quantile(v_mediana, 0.05)), 6),
            q95=round(float(np.quantile(v_mediana, 0.95)), 6),
        ), fh, indent=2)


if __name__ == "__main__":
    main()
