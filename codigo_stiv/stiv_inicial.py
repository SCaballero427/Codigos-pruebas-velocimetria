"""STIV inicial: el metodo tal como nacio en la prueba 3 (Sile Main Canal, julio de 2026).

Es el codigo de `evolucion_algoritmo_velocimetria/v3_smc_stiv` sacado del notebook a un modulo, sin
cambiar nada del metodo. Sirve como punto de partida para comparar con `stiv_completo.py`, que
reune todas las mejoras posteriores.

Lo que hace y lo que no
-----------------------
- Video **cenital** (mirando hacia abajo): no corrige la perspectiva ni la lente.
- Escala **conocida** (m por pixel), sacada de dos puntos de la imagen a una distancia conocida.
- Una **linea de 1 pixel** por vertical de la seccion, todas centradas en la misma columna.
- Control de calidad con **un solo criterio**: la coherencia (nitidez de las rayas, de 0 a 1).
- Relleno de las verticales rechazadas por **interpolacion lineal** entre las medidas; junto a los
  muros copia el valor medido mas cercano (canal de hormigon con muros verticales).
- Caudal por trapecios: alfa x velocidad x calado.

Uso
---
    python stiv_inicial.py            # ejemplo: Sile Main Canal, desde esta carpeta

    import stiv_inicial
    r = stiv_inicial.medir_canal(video, filas, ...)

Solo necesita numpy y OpenCV.
"""
from pathlib import Path

import cv2
import numpy as np


def mapa_lineas(filas, angulos_deg, ds, x0, x1):
    """Coordenadas de muestreo de cada linea: mapx, mapy de forma (n_lineas, n_muestras).

    Todas las lineas se centran en la columna (x0 + x1) / 2; solo cambia su fila.
    """
    filas = np.atleast_1d(np.asarray(filas, float))
    angs = np.radians(np.atleast_1d(np.asarray(angulos_deg, float)))
    n_mu = int((x1 - x0) / ds)
    # t recorre la linea centrada en su punto medio, en pixeles
    t = (np.arange(n_mu) - (n_mu - 1) / 2) * ds
    cx = 0.5 * (x0 + x1)
    mapx = np.zeros((len(filas), n_mu), np.float32)
    mapy = np.zeros((len(filas), n_mu), np.float32)
    for i, (f, a) in enumerate(zip(filas, angs)):
        mapx[i] = cx + t * np.cos(a)
        mapy[i] = f + t * np.sin(a)
    return mapx, mapy


def construir_sti(archivo, mapx, mapy, n_frames, sigma):
    """Apila n_frames filas muestreadas -> STI de forma (n_lineas, n_frames, n_muestras).

    El video se lee una sola vez y solo se guarda lo que hay bajo las lineas.
    """
    cap = cv2.VideoCapture(str(archivo))
    sti = np.zeros((mapx.shape[0], n_frames, mapx.shape[1]), np.float32)
    for k in range(n_frames):
        ok, fr = cap.read()
        if not ok:
            sti = sti[:, :k, :]
            break
        gris = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY).astype(np.float32)
        # Antialias ANTES de muestrear: sin esto el submuestreo inventa orientaciones.
        gris = cv2.GaussianBlur(gris, (0, 0), sigma)
        sti[:, k, :] = cv2.remap(gris, mapx, mapy, cv2.INTER_LINEAR)
    cap.release()
    return sti


def preparar_sti(sti):
    """Quita el fondo estatico y el parpadeo global, y normaliza."""
    a = sti - sti.mean(axis=0, keepdims=True)   # fondo fijo de cada muestra (rayas verticales)
    a = a - a.mean(axis=1, keepdims=True)       # parpadeo de cada fotograma (rayas horizontales)
    d = a.std()
    return a / d if d > 0 else a


def tensor_estructura(bloque, sigma=1.5):
    """Pendiente m (muestras/fotograma) y coherencia C de un trozo de STI."""
    g = cv2.GaussianBlur(bloque, (0, 0), sigma)
    # eje 0 = tiempo (filas), eje 1 = espacio (columnas)
    It = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    Ix = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
    # se recorta el borde: Sobel contamina 2 px por el efecto de borde
    It, Ix = It[2:-2, 2:-2], Ix[2:-2, 2:-2]
    Jxx = float((Ix * Ix).sum())
    Jtt = float((It * It).sum())
    Jxt = float((Ix * It).sum())
    if Jxx + Jtt <= 0:
        return np.nan, 0.0
    # autovector del autovalor MENOR = direccion a lo largo de las estelas
    _, vec = np.linalg.eigh(np.array([[Jxx, Jxt], [Jxt, Jtt]]))
    ex, et = vec[:, 0]
    if et < 0:            # el autovector esta definido salvo signo: se orienta hacia t creciente
        ex, et = -ex, -et
    m = ex / et if et != 0 else np.nan
    coherencia = np.sqrt((Jxx - Jtt) ** 2 + 4 * Jxt ** 2) / (Jxx + Jtt)
    return m, float(coherencia)


def medir_sti(sti_p, lado=64, coh_min=0.50, sigma=1.5):
    """Pendiente robusta de una STI, por bloques con solape: (m, coherencia mediana)."""
    nt, nx = sti_p.shape
    paso = lado // 2
    ms, cs = [], []
    for t0 in range(0, nt - lado + 1, paso):
        for x0 in range(0, nx - lado + 1, paso):
            m, c = tensor_estructura(sti_p[t0:t0 + lado, x0:x0 + lado], sigma)
            if np.isfinite(m):
                ms.append(m); cs.append(c)
    if not ms:
        return np.nan, 0.0
    ms, cs = np.array(ms), np.array(cs)
    coh_mediana = float(np.median(cs))
    usables = cs >= coh_min
    if usables.sum() == 0:
        return np.nan, coh_mediana
    # mediana ponderada por coherencia: los bloques nitidos pesan mas
    mm, cc = ms[usables], cs[usables]
    orden = np.argsort(mm)
    mm, cc = mm[orden], cc[orden]
    acumulado = np.cumsum(cc) / cc.sum()
    return float(mm[np.searchsorted(acumulado, 0.5)]), coh_mediana


def medir_canal(archivo, s_transecto, prof_transecto, fila_agua_sup, escala, columna_ini,
                columna_fin, angulo_flujo, v_esperada, alfa, n_frames=250, lado_bloque=64,
                coh_min_bloque=0.50, sigma_derivada=1.5, coh_min_estacion=0.70):
    """Todo el metodo de la prueba 3: de un video cenital a la velocidad y el caudal.

    s_transecto, prof_transecto: progresiva (m desde la orilla) y calado (m) de cada vertical;
    las de calado 0 son los bordes del agua. fila_agua_sup: fila de la imagen donde empieza el agua
    (progresiva 0). escala: m por pixel. Devuelve un diccionario con todo lo calculado.
    """
    cap = cv2.VideoCapture(str(archivo))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    dt = 1.0 / fps
    s_transecto = np.asarray(s_transecto, float)
    prof_transecto = np.asarray(prof_transecto, float)
    es_contorno = prof_transecto == 0.0

    # Una linea por vertical; paso de muestreo = lo que avanza el agua por fotograma (estelas a 45)
    filas = fila_agua_sup + s_transecto / escala
    ds = int(round(v_esperada * dt / escala))
    sigma_antialias = 0.5 * ds
    mapx, mapy = mapa_lineas(filas, np.full(len(filas), angulo_flujo), ds, columna_ini, columna_fin)

    sti_crudo = construir_sti(archivo, mapx, mapy, n_frames, sigma_antialias)
    v = np.full(len(filas), np.nan)
    coherencia = np.full(len(filas), np.nan)
    for i in range(len(filas)):
        if es_contorno[i]:
            v[i] = 0.0                # condicion de contorno: calado nulo y muro
            continue
        m, coherencia[i] = medir_sti(preparar_sti(sti_crudo[i]), lado_bloque, coh_min_bloque,
                                     sigma_derivada)
        v[i] = m * ds * escala / dt if np.isfinite(m) else np.nan

    # Control de calidad: solo la coherencia
    medida = (~es_contorno) & (coherencia >= coh_min_estacion) & np.isfinite(v)
    # Relleno: interpolacion entre medidas (en los extremos, el valor medido mas cercano)
    v_eff = v.copy()
    rellenadas = np.where(~(medida | es_contorno))[0]
    v_eff[rellenadas] = np.interp(s_transecto[rellenadas], s_transecto[medida], v[medida])
    q_especifico = alfa * v_eff * prof_transecto
    caudal = float(np.trapezoid(q_especifico, s_transecto))
    return dict(fps=fps, ds=ds, sti_crudo=sti_crudo, v=v, coherencia=coherencia, medida=medida,
                v_eff=v_eff, q_especifico=q_especifico, caudal=caudal)


if __name__ == "__main__":
    # Ejemplo: Sile Main Canal (prueba 3), con los mismos valores que el notebook de la v3.
    RAIZ = Path(__file__).resolve().parent.parent
    VIDEO = RAIZ / "casos/02_smc_pyorc/entradas/SMC_estabilizado.mkv"
    SECCION = np.loadtxt(RAIZ / "datos/USGS/Station_Stage_SileCanal.csv", delimiter=",",
                         skiprows=1, usecols=(0, 1))
    FILA_AGUA_SUP, FILA_AGUA_INF, ANCHO_CANAL = 438, 1463, 1.8288
    r = medir_canal(VIDEO, SECCION[:, 0], SECCION[:, 1], FILA_AGUA_SUP,
                    escala=ANCHO_CANAL / (FILA_AGUA_INF - FILA_AGUA_SUP), columna_ini=600,
                    columna_fin=3400, angulo_flujo=-1.0, v_esperada=0.95, alfa=0.92)
    print(f"Verticales medidas: {int(r['medida'].sum())} de {int((SECCION[:, 1] > 0).sum())}")
    print(f"Caudal: {r['caudal']:.4f} m3/s (aforo 1.4362 m3/s)")
