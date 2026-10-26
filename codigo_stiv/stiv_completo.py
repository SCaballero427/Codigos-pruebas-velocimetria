"""STIV completo: el metodo de la prueba 3 con todas las mejoras de julio y agosto de 2026.

Reune en un solo modulo lo que se fue anadiendo de la v4 a la v8 de
`evolucion_algoritmo_velocimetria/`. Cada mejora es OPCIONAL: con las opciones apagadas y
`derivadas="sobel"`, el programa hace lo mismo que la version inicial (`stiv_inicial.py`). Por
defecto las derivadas del tensor son diferencias centrales (v4), que en el Sile Main Canal cambian el
caudal un +1.3 % (1.4672 frente a 1.4484 m3/s, aforo 1.4362).

Mejoras generales (sirven para cualquier rio o canal)
-----------------------------------------------------
- [v4] Correccion de perspectiva de cada fotograma antes de leer las lineas, y lineas con centro y
  largo propios (ya no atadas a una columna de la imagen).
- [v4] Velocidad aproximada medida con correlacion de fase entre fotogramas, en vez de a ojo.
- [v4] Suavizado opcional antes de medir la inclinacion (espuma muy fina).
- [v4] Regla de cambio con el tiempo: descarta lo quieto (muros), que da rayas perfectas con v = 0.
- [v5] Posicion de la camara con puntos medidos en el terreno y la calibracion de la lente, y
  correccion de la perspectiva con un mapa pixel a pixel que incluye la deformacion de la lente.
- [v5] Relleno de las verticales sin medida en orillas en rampa (la velocidad baja a cero en el
  borde) ademas del de muros verticales, y caudal por trapecios.
- [v6] Banda de lineas paralelas por punto, igualadas y promediadas (poco material flotante).
- [v6] Cada regla de calidad se puede apagar (None).
- [v7] Un angulo por punto y lineas que se salen de la imagen (solo cuentan los trozos que caen
  dentro); todo el proceso en una funcion (`medir_video`) para medir varios videos igual.
- [v7] Curva de decorrelacion: comprueba si el agua tiene algo que seguir, sin usar STIV.
- [v8] Solo votan los trozos de la imagen espacio-tiempo que tienen algo flotando.

Ajustes que dependen del video (opcionales)
-------------------------------------------
- [v6] Brillo maximo del agua (agua oscura con orilla clara).
- [v8] Filtro de restos flotantes (top-hat) contra los cuadros de la compresion.
- [v8] Compensacion del movimiento de la camara (camara en la mano), aplicada al mapa.
- [v8] Cantidad de restos que pasan por cada punto (densidad) como regla de calidad.
- [v8] Orillas y punto de fuga para corregir la perspectiva sin ninguna medida del lugar.

Uso basico
----------
    import stiv_completo as st
    mapx, mapy, n_banda = st.mapa_banda(centros, angulos, ds, largo, ancho, n_lineas)
    cfg = st.Configuracion(ds=ds, escala=..., dt=1 / fps, n_frames=600, brillo_max_agua=5.0)
    r = st.medir_video(video, mapx, mapy, n_banda, cfg)
    medida, motivos = st.control_calidad(r, cfg)

`validar.py` reproduce con este modulo los resultados de las pruebas 3, 5, 6, 7 y 8.
Solo necesita numpy y OpenCV.
"""
from dataclasses import dataclass

import cv2
import numpy as np


# =============================================================================== geometria
def pose_camara(px_imagen, xyz_terreno, K, dist):
    """[v5] Posicion y orientacion de la camara a partir de puntos medidos en el terreno.

    px_imagen (N,2) en pixeles, xyz_terreno (N,3) en metros, K matriz de la camara y dist los
    coeficientes de deformacion de la lente. Se resuelve en coordenadas locales (restando el centro
    de los puntos) porque las coordenadas proyectadas absolutas (~1e5) condicionan mal el calculo.
    """
    src = np.asarray(px_imagen, float)
    dst = np.asarray(xyz_terreno, float)
    origen = dst.mean(axis=0)
    obj = np.ascontiguousarray(dst - origen)
    K = np.asarray(K, float)
    dist = np.asarray(dist, float).reshape(-1, 1)
    # SQPNP aguanta puntos casi en un plano; LM afina la solucion
    _, rvec, tvec = cv2.solvePnP(obj, src, K, dist, flags=cv2.SOLVEPNP_SQPNP)
    rvec, tvec = cv2.solvePnPRefineLM(obj, src, K, dist, rvec, tvec)
    error = np.linalg.norm(cv2.projectPoints(obj, rvec, tvec, K, dist)[0].reshape(-1, 2) - src, axis=1)
    return dict(rvec=rvec, tvec=tvec, K=K, dist=dist, origen=origen, error_px=error)


def mundo_a_pixel(pose, xy, z):
    """[v5] Puntos (N,2) del plano horizontal z (m) -> pixeles (N,2) de la imagen, con la lente."""
    xy = np.asarray(xy, float).reshape(-1, 2)
    pts = np.column_stack([xy, np.full(len(xy), z)]) - pose["origen"]
    return cv2.projectPoints(np.ascontiguousarray(pts), pose["rvec"], pose["tvec"], pose["K"],
                             pose["dist"])[0].reshape(-1, 2)


def mapa_plano(pose, z_agua, centro_xy, e_u, e_v, u0, u1, v0, v1, resolucion):
    """[v5] Mapa pixel a pixel de la vista desde arriba, en metros, incluida la lente.

    El plano rectificado tiene columnas a lo largo de e_u (de u0 a u1) y filas a lo largo de e_v
    (de v1 arriba a v0 abajo), a `resolucion` m por pixel. Devuelve (mapx, mapy) para cv2.remap: para
    cada pixel de la vista desde arriba, de que punto de la imagen original viene.
    """
    ancho = int(round((u1 - u0) / resolucion))
    alto = int(round((v1 - v0) / resolucion))
    jj, ii = np.meshgrid(np.arange(ancho), np.arange(alto))
    U = u0 + (jj + 0.5) * resolucion
    V = v1 - (ii + 0.5) * resolucion
    XY = np.asarray(centro_xy, float) + U[..., None] * np.asarray(e_u) + V[..., None] * np.asarray(e_v)
    px = mundo_a_pixel(pose, XY.reshape(-1, 2), z_agua).reshape(alto, ancho, 2)
    return (np.ascontiguousarray(px[..., 0], np.float32), np.ascontiguousarray(px[..., 1], np.float32))


def homografia_horizonte(punto_fuga, focal, ancho_img, alto_img, xmin, ymax, esc):
    """[v4] Imagen -> plano del agua (px) sin ninguna medida del lugar.

    Con balanceo nulo, la fila del punto de fuga del eje del cauce es el horizonte, y con una focal
    supuesta da la inclinacion de la camara. La unidad de longitud es la altura de la camara sobre
    el agua; `esc` son pixeles del plano por altura de camara. Devuelve (H, cabeceo, guinada).
    """
    cxi, cyi = ancho_img / 2, alto_img / 2
    theta = np.arctan((cyi - punto_fuga[1]) / focal)          # cabeceo, del horizonte
    K = np.array([[focal, 0, cxi], [0, focal, cyi], [0, 0, 1.0]])
    R = np.array([[1, 0, 0],
                  [0, -np.sin(theta), -np.cos(theta)],
                  [0, np.cos(theta), -np.sin(theta)]])
    g2i = K @ np.column_stack([R[:, 0], R[:, 1], [0, np.cos(theta), np.sin(theta)]])
    d = R.T @ np.linalg.inv(K) @ np.array([punto_fuga[0], punto_fuga[1], 1.0])
    psi = np.arctan2(d[0], d[1])                              # guinada: cauce vertical en la salida
    rot = np.array([[np.cos(psi), np.sin(psi), 0],
                    [-np.sin(psi), np.cos(psi), 0], [0, 0, 1.0]])
    S = np.array([[esc, 0, -xmin * esc], [0, -esc, ymax * esc], [0, 0, 1.0]])
    return S @ np.linalg.inv(g2i @ np.linalg.inv(rot)), np.degrees(theta), np.degrees(psi)


def mapa_homografia(H, tam):
    """[v8] La homografia imagen -> plano convertida en mapa (mapx, mapy) para cv2.remap.

    tam = (ancho, alto) del plano. Con el mapa, la estabilizacion se puede aplicar al mapa.
    """
    jj, ii = np.meshgrid(np.arange(tam[0], dtype=np.float32), np.arange(tam[1], dtype=np.float32))
    q = cv2.perspectiveTransform(np.stack([jj.ravel(), ii.ravel()], 1).reshape(-1, 1, 2),
                                 np.linalg.inv(H)).reshape(tam[1], tam[0], 2)
    return np.ascontiguousarray(q[..., 0]), np.ascontiguousarray(q[..., 1])


def recta_ransac(P, tol=6.0, iters=600):
    """[v8] Recta x = a*y + b robusta a puntos sueltos. Devuelve (a, b, puntos en la recta)."""
    rng = np.random.default_rng(0)
    mejor = (0, 0.0, 0.0)
    for _ in range(iters):
        (x1, y1), (x2, y2) = P[rng.choice(len(P), 2, replace=False)]
        if abs(y1 - y2) < 20:
            continue
        a = (x1 - x2) / (y1 - y2)
        n = (np.abs(P[:, 0] - (a * P[:, 1] + x1 - a * y1)) < tol).sum()
        if n > mejor[0]:
            mejor = (n, a, x1 - a * y1)
    m = np.abs(P[:, 0] - (mejor[1] * P[:, 1] + mejor[2])) < tol
    a, b = np.polyfit(P[m, 1], P[m, 0], 1)
    return float(a), float(b), int(m.sum())


def orillas_punto_fuga(gris, fila_ini, fila_fin, paso=10):
    """[v8] Las dos orillas de un canal recto y su punto de fuga, sin ninguna medida del lugar.

    En cada fila se busca el maximo gradiente horizontal en cada mitad de la imagen y se ajusta una
    recta a cada orilla. Las orillas son paralelas en el mundo y se cortan en el punto de fuga.
    Devuelve (punto_fuga, (a_izq, b_izq), (a_der, b_der)) con las rectas x = a*y + b.
    """
    ancho = gris.shape[1]
    izq, der = [], []
    for y in range(fila_ini, fila_fin, paso):
        fila = cv2.GaussianBlur(gris[y:y + 1, :].astype(np.float32), (9, 1), 0).ravel()
        d = np.abs(np.diff(fila))
        izq.append((int(np.argmax(d[:ancho // 2])), y))
        der.append((int(ancho // 2 + np.argmax(d[ancho // 2:])), y))
    a_i, b_i, _ = recta_ransac(np.array(izq, float))
    a_d, b_d, _ = recta_ransac(np.array(der, float))
    y_v = (b_d - b_i) / (a_i - a_d)
    return np.array([a_i * y_v + b_i, y_v]), (a_i, b_i), (a_d, b_d)


def _norm(a):
    a = a.astype(np.float32)
    return (a - a.mean()) / (a.std() + 1e-6)


def velocidad_esperada(archivo, mapa_rect, filas, columnas, n=40, inicio=100):
    """[v4] Desplazamiento tipico del agua por fotograma (px del plano), por correlacion de fase.

    Compara una franja de agua (filas, columnas: slices del plano rectificado) entre fotogramas
    seguidos y devuelve la mediana de (dx, dy). De ahi sale el paso de muestreo sin estimar nada a ojo.
    """
    cap = cv2.VideoCapture(str(archivo))
    cap.set(cv2.CAP_PROP_POS_FRAMES, inicio)
    prev, desp = None, []
    for _ in range(n):
        ok, fr = cap.read()
        if not ok:
            break
        r = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        if mapa_rect is not None:
            r = cv2.remap(r, mapa_rect[0], mapa_rect[1], cv2.INTER_LINEAR)
        banda = _norm(r[filas, columnas])
        if prev is not None:
            desp.append(cv2.phaseCorrelate(prev, banda)[0])
        prev = banda
    cap.release()
    return np.median(np.array(desp), axis=0)


# =============================================================================== lineas
def mapa_lineas(centros, angulos_deg, ds, largo):
    """[v4] Coordenadas de muestreo de cada linea: mapx, mapy de forma (n_lineas, n_muestras).

    Cada linea tiene su centro (x, y), su angulo y su largo en px; ds es el paso de muestreo.
    """
    centros = np.atleast_2d(np.asarray(centros, float))
    angs = np.radians(np.broadcast_to(np.asarray(angulos_deg, float), (len(centros),)))
    n_mu = int(largo / ds)
    # t recorre la linea centrada en su punto medio, en pixeles
    t = (np.arange(n_mu) - (n_mu - 1) / 2) * ds
    mapx = np.zeros((len(centros), n_mu), np.float32)
    mapy = np.zeros((len(centros), n_mu), np.float32)
    for i, ((cx, cy), a) in enumerate(zip(centros, angs)):
        mapx[i] = cx + t * np.cos(a)
        mapy[i] = cy + t * np.sin(a)
    return mapx, mapy


def mapa_banda(centros, angulos_deg, ds, largo, ancho, n_lineas):
    """[v6, v7] Una banda de n_lineas paralelas por punto, repartidas en `ancho` px a traves de la
    corriente, con un angulo por punto (o uno para todos). Devuelve (mapx, mapy, n_lineas), con las
    lineas de cada punto seguidas: (n_puntos * n_lineas, n_muestras). n_lineas = 1 es una sola linea.
    """
    c = np.atleast_2d(np.asarray(centros, float))
    a = np.radians(np.broadcast_to(np.asarray(angulos_deg, float), (len(c),)))
    perp = np.column_stack([-np.sin(a), np.cos(a)])   # a traves de la linea, por punto
    offsets = np.linspace(-ancho / 2, ancho / 2, n_lineas) if n_lineas > 1 else np.zeros(1)
    todos = (c[:, None, :] + offsets[None, :, None] * perp[:, None, :]).reshape(-1, 2)
    angs = np.repeat(np.degrees(a), len(offsets))
    return (*mapa_lineas(todos, angs, ds, largo), len(offsets))


def cobertura(mapx, mapy, n_banda, tam_imagen, margen=5, mapa_rect=None):
    """[v7, v8] Que muestras de cada linea ven la imagen.

    tam_imagen = (ancho, alto) de la imagen original. Sin mapa_rect, las lineas estan en la imagen;
    con el, estan en el plano rectificado y se mira de donde viene cada muestra. Devuelve
    (valido (n_puntos, n_muestras), fraccion de la linea que se ve por punto). Una muestra vale si se
    ve en todas las lineas de su banda.
    """
    ancho, alto = tam_imagen
    if mapa_rect is None:
        dentro = ((mapx >= margen) & (mapx < ancho - margen) & (mapy >= margen) & (mapy < alto - margen))
    else:
        dentro_rect = ((mapa_rect[0] >= 0) & (mapa_rect[0] < ancho - 1)
                       & (mapa_rect[1] >= 0) & (mapa_rect[1] < alto - 1)).astype(np.float32)
        dentro = cv2.remap(dentro_rect, mapx, mapy, cv2.INTER_NEAREST) > 0.5
    valido = dentro.reshape(-1, n_banda, mapx.shape[1]).all(axis=1)
    return valido, valido.mean(axis=1)


# =============================================================================== video -> STI
def realce_tophat(lado=5, sigma=0.8):
    """[v8] Filtro de restos flotantes: deja solo lo mas brillante que su entorno y mas pequeno que
    un disco de `lado` px (tras un desenfoque de `sigma` px contra el ruido de un pixel). Borra los
    cuadros planos que deja la compresion del video. Devuelve la funcion para `construir_sti`."""
    nucleo = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (lado, lado))

    def realzar(gris):
        return cv2.morphologyEx(cv2.GaussianBlur(gris, (0, 0), sigma), cv2.MORPH_TOPHAT, nucleo)
    return realzar


class Estabilizador:
    """[v8] Movimiento de la camara en cada fotograma, respecto al primero.

    Sigue `n_puntos` esquinas de la zona fija (mascara > 0: orillas, fuera del agua) siempre contra
    el fotograma 0, para que el error no se acumule, y ajusta una afinidad (desplazamiento, giro y
    escala). `construir_sti` la aplica al mapa de rectificacion, no a la imagen.
    """

    def __init__(self, gris0, mascara, n_puntos=600):
        self.gris0 = gris0
        self.P0 = cv2.goodFeaturesToTrack(gris0, n_puntos, 0.01, 7, mask=mascara)
        self.derivas = []

    def __call__(self, gris):
        p1, st, _ = cv2.calcOpticalFlowPyrLK(
            self.gris0, gris, self.P0, None, winSize=(21, 21), maxLevel=3,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
        ok = st.ravel() == 1
        A, _ = cv2.estimateAffinePartial2D(self.P0[ok], p1[ok], method=cv2.RANSAC,
                                           ransacReprojThreshold=2.0)
        A = np.array([[1.0, 0, 0], [0, 1.0, 0]]) if A is None else A
        self.derivas.append(float(np.median(np.linalg.norm((p1[ok] - self.P0[ok]).reshape(-1, 2), axis=1))))
        return A


def construir_sti(archivo, mapx, mapy, n_frames, sigma, mapa_rect=None, realce=None,
                  estabilizacion=None):
    """Apila n_frames filas muestreadas -> STI de forma (n_lineas, n_frames, n_muestras).

    [v4, v5] Si se da un mapa de rectificacion (mapx, mapy del plano a la imagen), cada fotograma se
    corrige con remap antes del antialias. [v8] `realce` se aplica al fotograma en gris antes de
    corregirlo; `estabilizacion` devuelve la afinidad del fotograma, que se aplica al mapa (necesita
    mapa_rect).
    """
    cap = cv2.VideoCapture(str(archivo))
    sti = np.zeros((mapx.shape[0], n_frames, mapx.shape[1]), np.float32)
    for k in range(n_frames):
        ok, fr = cap.read()
        if not ok:
            sti = sti[:, :k, :]
            break
        gris = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        mx, my = mapa_rect if mapa_rect is not None else (None, None)
        if estabilizacion is not None:
            A = estabilizacion(gris).astype(np.float32)
            mx, my = (A[0, 0] * mx + A[0, 1] * my + A[0, 2], A[1, 0] * mx + A[1, 1] * my + A[1, 2])
        if realce is not None:
            gris = realce(gris)
        gris = gris.astype(np.float32)
        if mapa_rect is not None:
            gris = cv2.remap(gris, mx, my, cv2.INTER_LINEAR)
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


def tensor_estructura(bloque, sigma=1.5, derivadas="centrales"):
    """Pendiente m (muestras/fotograma) y coherencia C de un trozo de STI.

    [v4] Suavizado opcional (sigma = 0 lo apaga, para espuma muy fina) y diferencias centrales.
    derivadas = "sobel" usa las de la version inicial (Sobel 3x3 recortando 2 px de borde).
    """
    g = cv2.GaussianBlur(bloque, (0, 0), sigma) if sigma > 0 else bloque
    # eje 0 = tiempo (filas), eje 1 = espacio (columnas)
    if derivadas == "sobel":
        It = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)[2:-2, 2:-2]
        Ix = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)[2:-2, 2:-2]
    else:
        It, Ix = np.gradient(g)
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


def medir_sti(sti_p, lado=64, coh_min=0.50, sigma=1.5, valido=None, energia=None, cuantil=None,
              derivadas="centrales"):
    """Pendiente robusta de una STI, por bloques con solape: (m, coherencia mediana).

    [v7] `valido` (una por muestra) marca las muestras que ven la imagen; los trozos que tocan alguna
    de fuera no cuentan. [v8] Con `energia` (una STI del mismo tamano) y `cuantil`, solo cuentan los
    trozos cuyo maximo de energia esta por encima de ese cuantil: los que contienen algo flotando.
    """
    nt, nx = sti_p.shape
    paso = lado // 2
    ms, cs, es = [], [], []
    for t0 in range(0, nt - lado + 1, paso):
        for x0 in range(0, nx - lado + 1, paso):
            if valido is not None and not valido[x0:x0 + lado].all():
                continue          # trozo con muestras fuera de la imagen
            m, c = tensor_estructura(sti_p[t0:t0 + lado, x0:x0 + lado], sigma, derivadas)
            if np.isfinite(m):
                ms.append(m); cs.append(c)
                es.append(energia[t0:t0 + lado, x0:x0 + lado].max() if energia is not None else 0.0)
    if not ms:
        return np.nan, 0.0
    ms, cs, es = np.array(ms), np.array(cs), np.array(es)
    if cuantil is not None:
        senal = es >= np.quantile(es, cuantil)
        ms, cs = ms[senal], cs[senal]
    coh_mediana = float(np.median(cs))
    usables = cs >= coh_min
    if usables.sum() == 0:
        return np.nan, coh_mediana
    # mediana ponderada por coherencia: los trozos nitidos pesan mas
    mm, cc = ms[usables], cs[usables]
    orden = np.argsort(mm)
    mm, cc = mm[orden], cc[orden]
    acumulado = np.cumsum(cc) / cc.sum()
    return float(mm[np.searchsorted(acumulado, 0.5)]), coh_mediana


# =============================================================================== medida completa
@dataclass
class Configuracion:
    """Parametros de la medida. Las reglas de calidad en None estan apagadas."""
    ds: float                          # paso de muestreo de las lineas (px): lo que avanza el agua por fotograma
    escala: float                      # unidades de longitud (m o alturas de camara) por px del plano
    dt: float                          # s entre fotogramas
    n_frames: int = 250
    sigma_antialias: float = None      # px; por defecto ds / 2
    lado_bloque: int = 64              # trozos de la STI; mas pequenos si el video es corto
    coh_min_bloque: float = 0.50
    sigma_derivada: float = 1.5        # 0 = sin suavizado (espuma muy fina, v4)
    derivadas: str = "centrales"       # "sobel" = las de la version inicial
    cuantil_senal: float = None        # [v8] p. ej. 0.85: solo vota el 15 % de trozos con mas senal
    umbral_particula: float = 4.0      # [v8] nivel del filtro de restos que cuenta como resto
    modulo: bool = False               # [v7] velocidad en modulo si el sentido de las lineas es arbitrario
    # reglas de calidad
    coh_min_estacion: float = 0.70
    contraste_min: float = None        # [v4] cambio minimo con el tiempo (descarta muros)
    brillo_max_agua: float = None      # [v6] ajuste: agua oscura con orilla clara
    cobertura_min: float = None        # [v7] parte minima de la linea que se ve
    densidad_min: float = None         # [v8] ajuste: restos minimos que pasan
    densidad_max: float = None         # [v8] ajuste: por encima es la orilla
    v_max: float = None                # limite fisico, p. ej. 3 x velocidad aproximada


def medir_video(archivo, mapx, mapy, n_banda, cfg, mapa_rect=None, realce=None, estabilizacion=None,
                valido=None):
    """[v7] Todo el proceso para un video: de las lineas a la velocidad de cada punto.

    Devuelve un diccionario con, por punto: v, coherencia, contraste (cambio con el tiempo), brillo
    y densidad (restos que pasan), ademas de las STI. Las reglas de calidad se aplican aparte con
    `control_calidad`, para poder ver todos los valores antes de decidir.
    """
    sigma = cfg.sigma_antialias if cfg.sigma_antialias is not None else 0.5 * cfg.ds
    sti_crudo = construir_sti(archivo, mapx, mapy, cfg.n_frames, sigma, mapa_rect, realce, estabilizacion)
    n_puntos = sti_crudo.shape[0] // n_banda
    # (punto, linea de la banda, tiempo, muestra)
    sti_crudo = sti_crudo.reshape(n_puntos, n_banda, *sti_crudo.shape[1:])
    contraste = np.median(sti_crudo.std(axis=2), axis=2).mean(axis=1)
    brillo = sti_crudo.mean(axis=(1, 2, 3))
    densidad = (sti_crudo.max(axis=1) > cfg.umbral_particula).mean(axis=(1, 2))
    v = np.full(n_puntos, np.nan)
    coherencia = np.full(n_puntos, np.nan)
    sti_prep = []
    for i in range(n_puntos):
        # [v6] cada linea de la banda se iguala por separado y luego se promedian
        prep = np.mean([preparar_sti(l) for l in sti_crudo[i]], axis=0)
        sti_prep.append(prep)
        m, coherencia[i] = medir_sti(
            prep, cfg.lado_bloque, cfg.coh_min_bloque, cfg.sigma_derivada,
            valido=None if valido is None else valido[i],
            energia=sti_crudo[i].mean(axis=0) if cfg.cuantil_senal is not None else None,
            cuantil=cfg.cuantil_senal, derivadas=cfg.derivadas)
        if np.isfinite(m):
            v[i] = (abs(m) if cfg.modulo else m) * cfg.ds * cfg.escala / cfg.dt
    return dict(v=v, coherencia=coherencia, contraste=contraste, brillo=brillo, densidad=densidad,
                sti_crudo=sti_crudo, sti_prep=np.stack(sti_prep), n_frames=sti_crudo.shape[2])


def control_calidad(r, cfg, fraccion_visible=None, es_contorno=None):
    """Que puntos se aceptan. Cada regla es independiente y se apaga con None en la configuracion.

    Devuelve (medida (bool por punto), motivos (lista de rechazos por punto)).
    """
    n = len(r["v"])
    reglas = {
        "coherencia": r["coherencia"] < cfg.coh_min_estacion,
        "no medido": ~np.isfinite(r["v"]),
    }
    if cfg.contraste_min is not None:
        reglas["quieto"] = r["contraste"] < cfg.contraste_min
    if cfg.brillo_max_agua is not None:
        reglas["brillo de orilla"] = r["brillo"] > cfg.brillo_max_agua
    if cfg.cobertura_min is not None and fraccion_visible is not None:
        reglas["fuera de la imagen"] = np.asarray(fraccion_visible) < cfg.cobertura_min
    if cfg.densidad_min is not None:
        reglas["sin restos"] = r["densidad"] < cfg.densidad_min
    if cfg.densidad_max is not None:
        reglas["orilla (restos)"] = r["densidad"] > cfg.densidad_max
    if cfg.v_max is not None:
        reglas["velocidad imposible"] = np.abs(np.nan_to_num(r["v"])) > cfg.v_max
    if es_contorno is not None:
        reglas["borde del agua"] = np.asarray(es_contorno)
    medida = np.ones(n, bool)
    motivos = [[] for _ in range(n)]
    for nombre, falla in reglas.items():
        medida &= ~falla
        for i in np.where(falla)[0]:
            motivos[i].append(nombre)
    return medida, motivos


# =============================================================================== caudal
def rellenar(s, v, medida, es_contorno, orillas="rampa"):
    """Velocidad en las verticales sin medida.

    orillas = "muro" (v3): recta entre las medidas y, junto al muro, el valor medido mas cercano,
    porque junto a un muro vertical el agua sigue corriendo rapido. orillas = "rampa" (v5): los
    bordes del agua (v = 0) tambien sirven de apoyo, porque en una orilla en rampa el agua se frena.
    """
    s = np.asarray(s, float)
    v_eff = np.where(es_contorno, 0.0, np.where(medida, v, np.nan))
    apoyo = medida | es_contorno if orillas == "rampa" else medida
    rellenar_aqui = ~(medida | es_contorno)
    v_eff[rellenar_aqui] = np.interp(s[rellenar_aqui], s[apoyo], v_eff[apoyo])
    return v_eff


def caudal(s, v_eff, prof, alfa):
    """Caudal (m3/s) por trapecios: alfa x velocidad de la superficie x calado, de orilla a orilla."""
    q = alfa * np.asarray(v_eff) * np.asarray(prof)
    return float(np.trapezoid(q, s)), q


# =============================================================================== diagnostico
def cargar_gris(archivo, n=None):
    """El video entero (o sus n primeros fotogramas) en gris: solo para videos cortos."""
    cap = cv2.VideoCapture(str(archivo))
    fs = []
    while n is None or len(fs) < n:
        ok, fr = cap.read()
        if not ok:
            break
        fs.append(cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY).astype(np.float32))
    cap.release()
    return np.stack(fs)


def curva_decorrelacion(pila, saltos, parches, radio=28):
    """[v7] Cuanto dura el dibujo de la superficie: parecido de un trozo de agua consigo mismo tras
    `saltos` fotogramas, buscandolo en toda la zona para que el desplazamiento no cuente.

    pila: fotogramas en gris (cargar_gris); parches: esquinas (x, y) de trozos de agua lejos de las
    orillas. Devuelve un valor por salto (1 = identico). Si el agua no lleva nada que seguir, la curva
    esta en el nivel del ruido desde el primer salto. No usa STIV ni ninguna referencia.
    """
    nrm = (pila - pila.mean(axis=0)) / (pila.std(axis=0) + 1e-6)
    curva = []
    for dt in saltos:
        busq = min(10 + 7 * dt, 60)
        picos = []
        for (x0, y0) in parches:
            acc = None
            for k in range(len(nrm) - dt):
                A = nrm[k, y0:y0 + 2 * radio, x0:x0 + 2 * radio]
                B = nrm[k + dt, max(y0 - busq, 0):y0 + 2 * radio + busq,
                        max(x0 - busq, 0):x0 + 2 * radio + busq]
                r = cv2.matchTemplate(B, A, cv2.TM_CCOEFF_NORMED)
                acc = r if acc is None else acc + r
            picos.append(float((acc / (len(nrm) - dt)).max()))
        curva.append(float(np.mean(picos)))
    return np.array(curva)
