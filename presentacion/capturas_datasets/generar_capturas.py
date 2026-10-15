"""Capturas ligeras de los videos del dataset y de los resultados de las pruebas, para GitHub.

Los videos del dataset (`datasets vision velocimetria/`, 45 GB) y los videos de resultados no caben en
el repositorio de forma razonable; esta carpeta guarda en su lugar una imagen de cada uno, en JPEG
reducido. Cuatro partes, cada una se puede rehacer por separado:

    python generar_capturas.py videos       # un fotograma de cada video del dataset + hojas de contacto
    python generar_capturas.py resultados   # fotogramas de los mp4 de resultado + figuras de cada caso
    python generar_capturas.py validacion   # re-corre validacion/caso_*.py y dibuja una medida
    python generar_capturas.py noche        # el programa en directo sobre grabaciones de noche de Japon

Se ejecuta desde esta carpeta con el .venv del programa en directo (numpy + OpenCV, sin pyorc):

    ..\\..\\casos\\09_directo_tokio\\.venv\\Scripts\\python.exe generar_capturas.py videos
"""
import csv, io, os, runpy, shutil, sys, contextlib
import numpy as np
import cv2

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))   # raiz del proyecto
DATASET = os.path.join(RAIZ, "datos", "externos", "datasets vision velocimetria")
ANIDADA = os.path.join(RAIZ, "casos")
VALIDACION = os.path.join(RAIZ, "casos", "09_directo_tokio", "validacion")

EXTENSIONES = (".mp4", ".avi", ".mov", ".mkv", ".mts")
LADO_VIDEO = 640          # px del lado mayor de cada captura del dataset: se reconoce el rio, pesa ~40 KB
LADO_RESULTADO = 1280     # los resultados llevan texto y flechas que tienen que leerse
LADO_VALIDACION = 1600    # el dibujo del programa: video + vista rectificada + panel de STI
CALIDAD = 72
BRILLO_OSCURO = 20        # mediana por debajo de esto la captura sin estirar es negra. Mediana y no media:
                          # en el Bradano el agua esta a 0.12/255 pero la orilla de grava sube la media


def guardar_jpg(ruta, img, lado):
    h, w = img.shape[:2]
    k = lado / max(h, w)
    if k < 1:
        img = cv2.resize(img, (round(w * k), round(h * k)), interpolation=cv2.INTER_AREA)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, CALIDAD, cv2.IMWRITE_JPEG_OPTIMIZE, 1])
    buf.tofile(ruta)      # imwrite no acepta rutas con caracteres fuera de ASCII en Windows
    return img


def leer_imagen(ruta):
    return cv2.imdecode(np.fromfile(ruta, np.uint8), cv2.IMREAD_COLOR)


def estirar(img):
    """Estiramiento de contraste por percentiles. Solo para que la captura no sea un rectangulo negro:
    se anota en el indice, para que nadie lo tome por el aspecto real del video."""
    lo, hi = np.percentile(img, [1, 99.5])
    return np.clip((img.astype(np.float32) - lo) * 255 / max(hi - lo, 1), 0, 255).astype(np.uint8)


def fotograma(ruta, fraccion=0.5):
    """El fotograma en `fraccion` de la duracion; si el contenedor no deja saltar, el primero."""
    cap = cv2.VideoCapture(ruta)
    if not cap.isOpened():
        return None, {}
    info = {"ancho": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), "alto": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": cap.get(cv2.CAP_PROP_FPS), "fotogramas": int(cap.get(cv2.CAP_PROP_FRAME_COUNT))}
    n = max(0, int(info["fotogramas"] * fraccion))
    cap.set(cv2.CAP_PROP_POS_FRAMES, n)
    ok, f = cap.read()
    if not ok:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ok, f = cap.read()
        n = 0
    cap.release()
    info["capturado"] = n
    return (f if ok else None), info


def grupo_de(rel):
    """Hoja de contacto a la que va cada video: un dataset por hoja, Heiskanen partido por rio."""
    p = rel.replace("\\", "/").split("/")
    if p[0] == "data":
        return "HARMONIOUS"
    if p[0].startswith("Heiskanen"):
        return "Heiskanen_" + p[3]          # Surface_flow_velocities/Raw_data/<rio>
    if p[0] == "Boneyardcreek":
        return "Boneyard_Creek"
    return "Otros"


def rotulo_de(rel):
    """Nombre bajo cada miniatura. En HARMONIOUS hay videos que se llaman "1", "10" u "output2": si el
    nombre no dice de que rio es, se le antepone."""
    p = rel.replace("\\", "/").split("/")
    nombre = os.path.splitext(p[-1])[0]
    if p[0] == "data" and p[1].lower().replace("river", "")[:4] not in nombre.lower():
        return f"{p[1]}/{nombre}"
    return nombre


def hoja_contacto(entradas, ruta, ancho_mini=240, columnas=8):
    """Mosaico de miniaturas con el nombre de cada video debajo."""
    alto_txt = 16
    minis = []
    for img, nombre in entradas:
        h, w = img.shape[:2]
        m = cv2.resize(img, (ancho_mini, round(h * ancho_mini / w)), interpolation=cv2.INTER_AREA)
        if m.shape[0] > ancho_mini:                 # videos verticales: no estirar la fila
            m = cv2.resize(img, (round(w * ancho_mini / h), ancho_mini), interpolation=cv2.INTER_AREA)
        minis.append((m, nombre))
    alto_celda = max(m.shape[0] for m, _ in minis) + alto_txt + 6
    filas = -(-len(minis) // columnas)
    lienzo = np.full((filas * alto_celda, columnas * (ancho_mini + 6), 3), 255, np.uint8)
    for k, (m, nombre) in enumerate(minis):
        y0, x0 = (k // columnas) * alto_celda + 3, (k % columnas) * (ancho_mini + 6) + 3
        lienzo[y0:y0 + m.shape[0], x0:x0 + m.shape[1]] = m
        cv2.putText(lienzo, nombre[:40], (x0, y0 + alto_celda - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.32,
                    (0, 0, 0), 1, cv2.LINE_AA)
    guardar_jpg(ruta, lienzo, 99999)


# ───────────────────────────────────── 1. videos del dataset ─────────────────────────────────────
def capturas_videos():
    rutas = sorted(os.path.join(d, f) for d, _, fs in os.walk(DATASET) for f in fs
                   if f.lower().endswith(EXTENSIONES))
    # el unico dataset de HARMONIOUS sin video publica solo fotogramas: se toma el primero
    murg = os.path.join(DATASET, "data", "MurgRiver", "Frames")
    sueltas = sorted(os.path.join(murg, f) for f in os.listdir(murg)
                     if f.lower().endswith((".png", ".jpg", ".tif", ".gif")))[:1] if os.path.isdir(murg) else []
    filas, grupos = [], {}
    for k, ruta in enumerate(rutas + sueltas, 1):
        rel = os.path.relpath(ruta, DATASET)
        if ruta in sueltas:
            f = leer_imagen(ruta)
            if f is None:                                   # GIF: OpenCV lo lee como video
                f, _ = fotograma(ruta, 0)
            info = {"ancho": f.shape[1], "alto": f.shape[0], "fps": 0, "fotogramas": 1, "capturado": 0}
        else:
            f, info = fotograma(ruta)
        if f is None:
            print(f"  [{k}/{len(rutas)}] NO SE PUDO LEER {rel}")
            filas.append({"video": rel, "error": "no se pudo leer"})
            continue
        estirado = float(np.median(f)) < BRILLO_OSCURO
        if estirado:
            f = estirar(f)
        salida = os.path.join(AQUI, "videos", os.path.splitext(rel)[0] + ".jpg")
        mini = guardar_jpg(salida, f, LADO_VIDEO)
        grupos.setdefault(grupo_de(rel), []).append((mini, rotulo_de(rel)))
        dur = info["fotogramas"] / info["fps"] if info["fps"] else 0
        filas.append({"video": rel.replace("\\", "/"), "captura": os.path.relpath(salida, AQUI).replace("\\", "/"),
                      "ancho": info["ancho"], "alto": info["alto"], "fps": round(info["fps"], 3),
                      "fotogramas": info["fotogramas"], "duracion_s": round(dur, 1),
                      "tamano_MB": round(os.path.getsize(ruta) / 1e6, 1),
                      "fotograma_capturado": info["capturado"], "contraste_estirado": int(estirado), "error": ""})
        print(f"  [{k}/{len(rutas) + len(sueltas)}] {rel}  {info['ancho']}x{info['alto']}"
              + ("  (estirado)" if estirado else ""))
    campos = ["video", "captura", "ancho", "alto", "fps", "fotogramas", "duracion_s", "tamano_MB",
              "fotograma_capturado", "contraste_estirado", "error"]
    with open(os.path.join(AQUI, "indice_videos.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, campos, restval="")
        w.writeheader()
        w.writerows(filas)
    for g, entradas in grupos.items():
        hoja_contacto(entradas, os.path.join(AQUI, "hojas_contacto", f"{g}.jpg"))
        print(f"  hoja de contacto {g}: {len(entradas)} videos")


# ───────────────────────────────────── 2. resultados de los casos ─────────────────────────────────
# (carpeta del caso, videos de resultado a capturar); las figuras fig*.png de salidas/ van todas
CASOS = [
    ("04_boneyard_stiv", ["velocidad_tiempo_real", "velocidad_manual", "velocidad_sin_nivel",
                                "velocidad_nivel", "velocidad_nivel_chapa", "velocidad_nivel_curva"]),
    ("06_bradano_stiv", ["velocidad_tiempo_real"]),
    ("07_arrow_siembra", ["velocidad_tiempo_real"]),
    ("05_hommerich_stiv", ["velocidad_tiempo_real"]),
]


def capturas_resultados():
    for caso, videos in CASOS:
        sal = os.path.join(ANIDADA, caso, "salidas")
        destino = os.path.join(AQUI, "resultados", caso[3:].split("_")[0])   # 04_boneyard_stiv -> boneyard
        for v in videos:
            ruta = os.path.join(sal, v + ".mp4")
            for frac in (0.25, 0.75):        # dos instantes: se ve que la medida no es un fotograma fijo
                f, _ = fotograma(ruta, frac)
                if f is None:
                    print(f"  NO SE PUDO LEER {ruta}")
                    break
                guardar_jpg(os.path.join(destino, f"{v}_{int(frac * 100)}pct.jpg"), f, LADO_RESULTADO)
            print(f"  {caso}: {v}.mp4")
        for fig in sorted(x for x in os.listdir(sal) if x.startswith("fig") and x.endswith(".png")):
            guardar_jpg(os.path.join(destino, fig[:-4] + ".jpg"), leer_imagen(os.path.join(sal, fig)),
                        LADO_RESULTADO)
            print(f"  {caso}: {fig}")


# ───────────────────────────── 3. validacion del programa en directo ─────────────────────────────
def con_franja(img, video, modo_act, i, n, t, res, extra=None):
    """La cabecera de dibujar() esta pensada para la pantalla: en un 4K reducido no se lee, asi que se
    repite lo esencial en una franja propia, a tamano legible. `extra`: lineas que se anaden debajo."""
    k = LADO_VALIDACION / img.shape[1]
    img = cv2.resize(img, (LADO_VALIDACION, round(img.shape[0] * k)), interpolation=cv2.INTER_AREA)
    ac = [r["v"] for r in res if r["aceptada"]]
    textos = [f"{os.path.basename(video)}  |  stiv_directo.py, modo {modo_act}  |  medida {i + 1} de "
              f"{n} (la del medio), t = {t:.0f} s",
              f"estaciones aceptadas {len(ac)} de {len(res)}  |  mediana de la seccion "
              + (f"{np.median(ac):.3f} m/s" if ac else "--") + "  |  verde = aceptada, rojo = rechazada"]
    textos += extra or []
    franja = np.full((6 + 26 * len(textos), img.shape[1], 3), 20, np.uint8)
    for j, tx in enumerate(textos):
        cv2.putText(franja, tx, (10, 22 + 26 * j), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 1, cv2.LINE_AA)
    return np.vstack([img, franja])


def capturas_validacion():
    """Los caso_*.py de validacion/ solo dejan texto y JSON. Se re-corren tal cual (mismo codigo, misma
    referencia) interceptando sd.medir para quedarse con el fotograma de cada medida, y se dibuja la
    medida del MEDIO del video con dibujar() del propio programa: ni la mejor ni la peor, para no
    escoger. Los JSON que escriben van a una carpeta temporal, no pisan los de validacion/salidas."""
    sys.path.insert(0, VALIDACION)
    import correr as C
    sd = C.sd
    bucle_original, medir_original, procesar_original = C.bucle, sd.medir, sd.Geometria.procesar
    estado = {"frame": None, "medidas": []}

    def procesar(self, frame, modo="dia"):
        estado["frame"] = frame
        return procesar_original(self, frame, modo)

    def medir(*a, **k):
        res = medir_original(*a, **k)
        # copia superficial: bucle() quita el "sti" de cada resultado despues, y el panel lo necesita
        ok, jpg = cv2.imencode(".jpg", estado["frame"], [cv2.IMWRITE_JPEG_QUALITY, 95])
        estado["medidas"].append((jpg, a[1], [dict(r) for r in res], a[3] if len(a) > 3 else k.get("modo", "dia")))
        return res

    def bucle(video, cfg, orientacion_auto, modo, fin_s, verbose):
        estado["medidas"] = []
        geom, med = bucle_original(video, cfg, orientacion_auto, modo, fin_s, verbose)
        if estado["medidas"]:
            i = len(estado["medidas"]) // 2
            jpg, g, res, modo_act = estado["medidas"][i]
            t = med[i][0] if i < len(med) else 0.0
            frame = cv2.imdecode(jpg, cv2.IMREAD_COLOR)
            img = sd.dibujar(frame, g, res, {"titulo": f"Validacion: {os.path.basename(video)}", "t": t,
                                             "llenado": 1.0, "retraso": 0.0, "modo": modo_act,
                                             "px_muestra": g.px_por_muestra, "verificada": True}, False)
            nombre = estado["caso"] + ("_" + video.split("_")[-2] if estado["caso"] == "heiskanen" else "")
            img = con_franja(img, video, modo_act, i, len(estado["medidas"]), t, res)
            guardar_jpg(os.path.join(AQUI, "resultados", "validacion_directo", nombre + ".jpg"), img, LADO_VALIDACION)
            print(f"  -> captura {nombre}.jpg (medida {i + 1} de {len(estado['medidas'])}, t = {t:.0f} s)")
        return geom, med

    C.bucle, sd.medir, sd.Geometria.procesar = bucle, medir, procesar
    temporal = os.path.join(AQUI, "_temporal")
    os.makedirs(os.path.join(temporal, "salidas"), exist_ok=True)
    os.chdir(temporal)
    for caso in ("sile", "bradano", "heiskanen"):
        estado["caso"] = caso
        print(f"== caso_{caso}.py")
        sys.argv = [f"caso_{caso}.py"]
        texto = io.StringIO()
        with contextlib.redirect_stdout(texto):
            runpy.run_path(os.path.join(VALIDACION, f"caso_{caso}.py"), run_name="__main__")
        print(texto.getvalue())
        with open(os.path.join(AQUI, "resultados", "validacion_directo", f"{caso}.txt"), "w", encoding="utf-8") as fh:
            fh.write(texto.getvalue())
    os.chdir(AQUI)
    shutil.rmtree(temporal)       # los JSON re-escritos ya estan en validacion/salidas: no se guardan dos veces


# ───────────────────────────── 4. el programa en directo de noche (Japon) ─────────────────────────
DIRECTO = os.path.join(RAIZ, "casos", "09_directo_tokio")
GRAB_NIVEL = os.path.join(DIRECTO, "verificacion_nivel", "grabaciones")
AVISO_PROGRAMA = "Programa actual: en Myoshoji de noche se mide y se dibuja, pero no se acepta ninguna estacion (noche_no_valida)"
AVISO_FORZADO = ["FORZADO (medir_noche = True), solo para ver que mide: ~0.06 m/s son destellos de farola sobre ondulaciones",
                 "casi quietas. Refutado por el aforo oficial (0.4-0.6 m/s) y por el dia con el mismo nivel (0.48 m/s)"]
# (nombre de la captura, video, ajustes de la camara, segundos a medir, lineas extra de la franja). Las .ts
# de verificacion_nivel/grabaciones/ estan fuera de git (se rehacen con grabar_directo.py); el clip de
# raspberry/prueba/ si esta
NOCHE = [
    ("myoshoji_noche_clip90s", os.path.join(DIRECTO, "raspberry", "prueba", "myoshoji_noche_90s.mp4"),
     None, None, [AVISO_PROGRAMA]),
    ("myoshoji_20261014_1817JST", os.path.join(GRAB_NIVEL, "myoshoji_20261014_1817JST.ts"),
     None, 180, ["Grabacion del directo del 14-10-2026, 18:17-18:20 hora de Japon (noche, camara en color con farolas)",
                 AVISO_PROGRAMA]),
    ("myoshoji_20261014_1817JST_forzado", os.path.join(GRAB_NIVEL, "myoshoji_20261014_1817JST.ts"),
     {"medir_noche": True}, 180,
     ["Grabacion del directo del 14-10-2026, 18:17-18:20 hora de Japon (noche, camara en color con farolas)"]
     + AVISO_FORZADO),
]
# figuras del diagnostico dia/noche ya guardadas en verificacion_nivel/salidas/diagnostico/
FIGURAS_NOCHE = ["sti_largo_dia_1542", "sti_largo_noche_1800", "trazas_dia_1542", "trazas_noche_1800"]


def capturas_noche():
    """Myoshoji de noche con el codigo del programa (validacion/correr.py), dibujando la medida del
    MEDIO con dibujar() del propio programa, como en la parte 3. Solo hay noche de Myoshoji: las
    grabaciones de Kurome y Shimoda son de dia."""
    sys.path.insert(0, VALIDACION)
    import correr as C
    sd = C.sd
    medir_original, procesar_original = sd.medir, sd.Geometria.procesar
    estado = {"frame": None, "medidas": []}

    def procesar(self, frame, modo="dia"):
        estado["frame"] = frame
        return procesar_original(self, frame, modo)

    def medir(*a, **k):
        res = medir_original(*a, **k)
        ok, jpg = cv2.imencode(".jpg", estado["frame"], [cv2.IMWRITE_JPEG_QUALITY, 95])
        estado["medidas"].append((jpg, a[1], [dict(r) for r in res], a[3] if len(a) > 3 else k.get("modo", "dia")))
        return res

    sd.medir, sd.Geometria.procesar = medir, procesar
    destino = os.path.join(AQUI, "resultados", "directo_tokio_noche")
    try:
        for nombre, video, ajustes, fin_s, extra in NOCHE:
            if not os.path.exists(video):
                print(f"  FALTA {video} (fuera de git: grabar_directo.py)")
                continue
            print(f"== {nombre}")
            estado["medidas"] = []
            geom, med = C.correr_camara(video, "myoshoji", "auto", fin_s, ajustes=ajustes)
            if not estado["medidas"]:
                print("  sin medidas")
                continue
            i = len(estado["medidas"]) // 2
            jpg, g, res, modo_act = estado["medidas"][i]
            t = med[i][0] if i < len(med) else 0.0
            cfg = sd.cargar_config()
            img = sd.dibujar(cv2.imdecode(jpg, cv2.IMREAD_COLOR), g, res,
                             {"titulo": f"Myoshoji de noche: {os.path.basename(video)}", "t": t, "llenado": 1.0,
                              "retraso": 0.0, "modo": modo_act, "px_muestra": g.px_por_muestra,
                              "verificada": bool(cfg.get("escala_verificada"))}, False)
            img = con_franja(img, video, modo_act, i, len(estado["medidas"]), t, res, extra)
            guardar_jpg(os.path.join(destino, nombre + ".jpg"), img, LADO_VALIDACION)
            print(f"  -> {nombre}.jpg (medida {i + 1} de {len(estado['medidas'])}, t = {t:.0f} s)")
    finally:
        sd.medir, sd.Geometria.procesar = medir_original, procesar_original
    diag = os.path.join(DIRECTO, "verificacion_nivel", "salidas", "diagnostico")
    for fig in FIGURAS_NOCHE:
        guardar_jpg(os.path.join(destino, fig + ".jpg"), leer_imagen(os.path.join(diag, fig + ".png")), LADO_RESULTADO)
        print(f"  figura {fig}")


if __name__ == "__main__":
    partes = {"videos": capturas_videos, "resultados": capturas_resultados, "validacion": capturas_validacion,
              "noche": capturas_noche}
    for p in sys.argv[1:] or list(partes):
        partes[p]()
