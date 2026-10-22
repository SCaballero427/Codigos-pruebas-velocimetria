#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
 SIMULADOR DE ENCUADRE PARA STIV CON CAMARA VISIBLE EN UN PUENTE SOBRE CANAL
===============================================================================

 STIV (Space-Time Image Velocimetry) mide la velocidad superficial del agua
 apilando en el tiempo los pixeles de unas lineas de busqueda paralelas al
 flujo: la textura que viaja con el agua deja en esa imagen espacio-tiempo
 (STI) unas franjas inclinadas cuyo angulo da la velocidad.

 El programa responde a las preguntas de dimensionamiento de la estacion:

   1. Con la altura, la posicion lateral y la orientacion de la camara en el
      puente, ¿se ve el canal entero (el ancho de agua y de borde a borde) en
      la seccion donde se quiere medir?
   2. ¿Cuantos centimetros de superficie de agua representa cada pixel, a lo
      largo del flujo y a lo ancho, y como empeora al alejarse del puente?
   3. Con los fps de la camara y el rango de velocidades esperado, ¿el
      patron de la STI queda con un angulo que el algoritmo mida bien?

 Muestra vistas sincronizadas: perfil longitudinal, planta con la huella del
 campo de vision, seccion transversal, la imagen simulada con las lineas de
 busqueda, una lupa a la resolucion real del sensor y el resumen STIV.

 Forma parte del caso 08 (canal piloto Yaqui): sirve para decidir donde y
 como montar una camara fija en el puente del canal antes de instalarla.
 Entradas en entradas/ (medidas del canal y ficha de la camara); las camaras
 que se guardan desde la interfaz van a salidas/camaras_visibles.json.

 Uso (desde esta carpeta):
        python simulador_stiv_puente.py
        python simulador_stiv_puente.py --test   (autocomprobacion, sin GUI)

 Requisitos: solo biblioteca estandar de Python 3 (tkinter, zlib, struct).

-------------------------------------------------------------------------------
 SISTEMA DE REFERENCIA
-------------------------------------------------------------------------------
   x   a lo largo del canal, desde la cara del puente (x = 0) hacia donde
       mira la camara (aguas arriba o aguas abajo)                     [m]
   y   transversal, desde el eje del canal, + a la derecha mirando como
       la camara                                                       [m]
   z   cota sobre el fondo del canal                                   [m]
   La camara esta en C = (0, y_c, z_c). El canal es prismatico y recto.

-------------------------------------------------------------------------------
 FORMULAS PRINCIPALES (verificadas numericamente; ver autocomprobacion())
-------------------------------------------------------------------------------

 (F1) Constante del modelo estenopeico e IFOV del pixel central
          k = (N/2) / tan(FOV/2)                              [pixeles]
          IFOV = 1/k                                          [rad]

 (F2) Ejes de la camara. delta = inclinacion hacia abajo (0 = horizontal,
      90 = cenital), psi = giro en planta (+ hacia la derecha):
          adelante f = ( cos(delta)cos(psi),  cos(delta)sin(psi), -sin(delta))
          derecha  r = (-sin(psi),            cos(psi),            0)
          arriba   a = ( sin(delta)cos(psi),  sin(delta)sin(psi),  cos(delta))

 (F3) Proyeccion de un punto P, con q = P - C:
          X = q.f,  X_r = q.r,  X_a = q.a       (X > 0: delante de la camara)
          u = W/2 + k_h * X_r / X,      v = H/2 - k_v * X_a / X

 (F4) Rayo de un pixel (inversa de F3):
          d = f + ((u - W/2)/k_h) r + ((H/2 - v)/k_v) a,   P = C + t d

 (F5) Superficie vista en la seccion transversal (trapecio de fondo b,
      talud m horizontal por 1 vertical, bordes a la altura H_c, tirante d):
          ancho de agua   T = b + 2 m d
          ancho de bordes B = b + 2 m H_c
      Es una poligonal en (y, z): terreno, talud, agua, talud, terreno. Como
      el canal es prismatico, el rayo se intersecta en el plano (y, z) con
      cada tramo y gana el primer corte con t > 0; asi se resuelven tambien
      las ocultaciones de un talud sobre el agua.

 (F6) RESOLUCION EN EL AGUA (GSD). Derivando F3 respecto a la coordenada e
      del mundo (e = x a lo largo del flujo, e = y a lo ancho):
          du/de =  k_h (r_e X - f_e X_r) / X^2
          dv/de = -k_v (a_e X - f_e X_a) / X^2
          GSD_e = 1 / sqrt((du/de)^2 + (dv/de)^2)               [m/pixel]

 (F7) Caso particular: punto en el plano vertical del eje optico (psi = 0,
      y = y_c), a la distancia horizontal x, con H_w = z_c - d la altura
      sobre el agua y theta = atan(H_w / x) la depresion del rayo:
          GSD_x = H_w cos^2(theta - delta) / (k_v sin^2(theta))
          GSD_y = sqrt(x^2 + H_w^2) cos(theta - delta) / k_h
      En cenital (delta = theta = 90): GSD = H_w / k. El 1/sin^2(theta)
      explica por que la resolucion a lo largo del flujo cae tan rapido al
      alejarse: el agua se ve cada vez mas de canto.

 (F8) Longitud de una linea de busqueda en la imagen y GSD medio:
          l_px = |uv(fin) - uv(inicio)|,      g = L / l_px
      (la proyeccion de una recta es una recta).

 (F9) Angulo del patron en la STI (Fujita et al.). La STI se construye
      sobre la imagen ortorrectificada con un paso espacial S_x [m/pixel]
      igual para todas las lineas, usando una de cada k imagenes:
          desplazamiento = U k / (fps S_x)        [pixeles por imagen usada]
          theta_STI      = atan(desplazamiento)   [grados desde el eje t]
      45 grados = 1 pixel por imagen. Cerca de 0 la textura apenas se mueve
      entre imagenes; cerca de 90 salta tantos pixeles que se pierde la
      correlacion (aliasing). S_x no debe ser mas fino que el GSD nativo
      del peor punto de las lineas (se inventaria detalle); hacerlo mas
      grueso reduce el angulo de las velocidades altas a costa de menos
      pixeles en cada linea: n = L / S_x.

 (F10) Error de velocidad por un error angular dtheta del algoritmo:
          dU / U = dtheta / (sin(theta) cos(theta))
       Es minimo a 45 grados y crece sin limite hacia 0 y 90.

 (F11) Paso de imagenes que deja la velocidad U a 45 grados, fps minimos y
       S_x minimo para que la velocidad maxima no pase de theta_max:
          k* = fps S_x / U
          fps_min = U_max k / (S_x tan(theta_max))
          S_x_min = U_max k / (fps tan(theta_max))

 (F12) COBERTURA. Un punto P0 + s e esta en la imagen si cumple
          X > 0,   W/2 X +- k_h X_r >= 0,   H/2 X -+ k_v X_a >= 0
       y como X, X_r, X_a son lineales en s, cada condicion es A s + B >= 0:
       el tramo visible de una recta es un intervalo exacto. El ancho de
       agua entero se ve en x si se ven las dos orillas (y = +-T/2, z = d).

 (F13) Apuntado automatico: el eje optico pasa por el centro del canal en
       la seccion de medida (x_s, 0, d):
          psi   = atan2(-y_c, x_s)
          delta = atan2(z_c - d, sqrt(x_s^2 + y_c^2))

 (F14) Tamano de un trazador de diametro D en la imagen:
          n_px = D / max(GSD_x, GSD_y)    en el peor punto de la linea
       Por debajo de 1 pixel el trazador solo baja el contraste de un pixel.

 AVISO: el modelo es estenopeico, sin distorsion de la lente, con el canal
 recto, el agua plana y el puente reducido a la posicion de la camara (no se
 dibujan pilas ni baranda). Los FOV de las camaras genericas son teoricos.
 Sirve para dimensionar, no para calibrar: la ortorrectificacion real
 necesita puntos de control medidos en campo.
===============================================================================
"""

import base64
import json
import math
import operator
import os
import struct
import sys
import tempfile
import zlib

# =============================================================================
# 1. CAMARA
# =============================================================================

def k_pix(n_pix, fov_grados):
    """(F1) Pixeles por radian equivalentes del modelo estenopeico."""
    return (n_pix / 2.0) / math.tan(math.radians(fov_grados) / 2.0)


def ifov_mrad(fov_grados, n_pix):
    """(F1) IFOV del pixel central, en mrad. Por la distancia en m da mm."""
    return 1000.0 / k_pix(n_pix, fov_grados)


def _punto(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def camara(p):
    """(F2) Posicion, ejes y constantes de la camara.

    p['incl'] es la inclinacion hacia abajo y p['giro'] el giro en planta,
    ambos en grados."""
    de = math.radians(p["incl"])
    ps = math.radians(p["giro"])
    cd, sd, cp, sp = math.cos(de), math.sin(de), math.cos(ps), math.sin(ps)
    return dict(C=(0.0, p["ycam"], p["zcam"]),
                f=(cd * cp, cd * sp, -sd),
                r=(-sp, cp, 0.0),
                up=(sd * cp, sd * sp, cd),
                k_h=k_pix(p["res_h"], p["fov_h"]),
                k_v=k_pix(p["res_v"], p["fov_v"]),
                W=p["res_h"], H=p["res_v"])


def proyectar(cam, P):
    """(F3) Punto del mundo -> (u, v) en pixeles, o None si queda detras."""
    C = cam["C"]
    q = (P[0] - C[0], P[1] - C[1], P[2] - C[2])
    X = _punto(q, cam["f"])
    if X <= 1e-9:
        return None
    return (cam["W"] / 2.0 + cam["k_h"] * _punto(q, cam["r"]) / X,
            cam["H"] / 2.0 - cam["k_v"] * _punto(q, cam["up"]) / X)


def rayo(cam, u, v):
    """(F4) Direccion (sin normalizar) del rayo que pasa por el pixel (u, v)."""
    a = (u - cam["W"] / 2.0) / cam["k_h"]
    b = (cam["H"] / 2.0 - v) / cam["k_v"]
    f, r, up = cam["f"], cam["r"], cam["up"]
    return tuple(f[i] + a * r[i] + b * up[i] for i in range(3))


def en_imagen(cam, uv, margen=0.0):
    """True si (u, v) cae en el sensor, a margen pixeles del borde o mas."""
    return (uv is not None and margen - 1e-9 <= uv[0] <= cam["W"] - margen
            + 1e-9 and margen - 1e-9 <= uv[1] <= cam["H"] - margen + 1e-9)


def interseccion_agua(cam, d, cota):
    """Punto donde el rayo d corta el plano z = cota, o None si no baja."""
    if d[2] >= -1e-12:
        return None
    C = cam["C"]
    t = (cota - C[2]) / d[2]
    return (C[0] + t * d[0], C[1] + t * d[1], cota)


# =============================================================================
# 2. CANAL
# =============================================================================

AGUA, TALUD, TERRENO = 1, 2, 3
LEJOS = 1.0e4            # extension de los tramos de terreno a cada lado [m]


def anchos(p):
    """(F5) Ancho de la superficie de agua T y de borde a borde B."""
    return (p["b"] + 2.0 * p["m"] * p["tirante"],
            p["b"] + 2.0 * p["m"] * p["hc"])


def segmentos(p):
    """(F5) Poligonal (y, z) de la superficie vista: terreno, talud, agua,
    talud, terreno. Cada tramo es ((y0, z0), (y1, z1), tipo)."""
    T, B = anchos(p)
    d, hc = p["tirante"], p["hc"]
    return [((-LEJOS, hc), (-B / 2.0, hc), TERRENO),
            ((-B / 2.0, hc), (-T / 2.0, d), TALUD),
            ((-T / 2.0, d), (T / 2.0, d), AGUA),
            ((T / 2.0, d), (B / 2.0, hc), TALUD),
            ((B / 2.0, hc), (LEJOS, hc), TERRENO)]


def cota_superficie(p, y):
    """Cota de la superficie vista (agua o terreno) a la abscisa y."""
    T, B = anchos(p)
    ay = abs(y)
    if ay <= T / 2.0:
        return p["tirante"]
    if ay >= B / 2.0:
        return p["hc"]
    return (ay - p["b"] / 2.0) / p["m"]


def primer_impacto(yc, zc, dy, dz, segs):
    """(F5) Primer corte con t > 0 de la recta (yc + t dy, zc + t dz) con la
    poligonal. Devuelve (t, tipo) o None."""
    mejor = None
    for (y0, z0), (y1, z1), tipo in segs:
        ey, ez = y1 - y0, z1 - z0
        det = ey * dz - dy * ez
        if abs(det) < 1e-14:
            continue
        oy, oz = y0 - yc, z0 - zc
        t = (ey * oz - ez * oy) / det
        if t <= 1e-9 or (mejor is not None and t >= mejor[0]):
            continue
        s = (dy * oz - dz * oy) / det
        if -1e-9 <= s <= 1.0 + 1e-9:
            mejor = (t, tipo)
    return mejor


def es_visible(cam, segs, P):
    """True si el rayo de la camara a P no corta antes la superficie."""
    C = cam["C"]
    imp = primer_impacto(C[1], C[2], P[1] - C[1], P[2] - C[2], segs)
    return imp is None or imp[0] >= 1.0 - 1e-6


# =============================================================================
# 3. RESOLUCION Y COBERTURA
# =============================================================================

def gsd(cam, P, eje):
    """(F6) Metros de superficie por pixel en P en la direccion del eje del
    mundo indicado (0 = x, a lo largo del flujo; 1 = y, a lo ancho)."""
    C = cam["C"]
    q = (P[0] - C[0], P[1] - C[1], P[2] - C[2])
    f, r, up = cam["f"], cam["r"], cam["up"]
    X = _punto(q, f)
    if X <= 1e-9:
        return float("inf")
    Xr, Xa = _punto(q, r), _punto(q, up)
    du = cam["k_h"] * (r[eje] * X - f[eje] * Xr) / (X * X)
    dv = -cam["k_v"] * (up[eje] * X - f[eje] * Xa) / (X * X)
    return 1.0 / max(math.hypot(du, dv), 1e-15)


def gsd_plano_eje(p, x):
    """(F7) GSD (a lo largo, a lo ancho) en el plano vertical del eje, con
    giro nulo. Solo se usa para comprobar F6."""
    Hw = p["zcam"] - p["tirante"]
    th = math.atan2(Hw, x)
    de = math.radians(p["incl"])
    k_h = k_pix(p["res_h"], p["fov_h"])
    k_v = k_pix(p["res_v"], p["fov_v"])
    gx = Hw * math.cos(th - de) ** 2 / (k_v * math.sin(th) ** 2)
    gy = math.hypot(x, Hw) * math.cos(th - de) / k_h
    return gx, gy


def intervalo(cam, P0, e, lo, hi):
    """(F12) Intervalo de s en [lo, hi] para el que P0 + s e cae en la
    imagen, o None si no hay ninguno."""
    C = cam["C"]
    q0 = (P0[0] - C[0], P0[1] - C[1], P0[2] - C[2])
    AX, BX = _punto(e, cam["f"]), _punto(q0, cam["f"])
    Ar, Br = _punto(e, cam["r"]), _punto(q0, cam["r"])
    Au, Bu = _punto(e, cam["up"]), _punto(q0, cam["up"])
    W2, H2, kh, kv = cam["W"] / 2.0, cam["H"] / 2.0, cam["k_h"], cam["k_v"]
    for A, B in ((AX, BX - 1e-9),
                 (W2 * AX + kh * Ar, W2 * BX + kh * Br),
                 (W2 * AX - kh * Ar, W2 * BX - kh * Br),
                 (H2 * AX - kv * Au, H2 * BX - kv * Bu),
                 (H2 * AX + kv * Au, H2 * BX + kv * Bu)):
        if abs(A) < 1e-15:
            if B < 0.0:
                return None
        elif A > 0.0:
            lo = max(lo, -B / A)
        else:
            hi = min(hi, -B / A)
    return (lo, hi) if lo <= hi else None


def _cortar(a, b):
    if a is None or b is None:
        return None
    lo, hi = max(a[0], b[0]), min(a[1], b[1])
    return (lo, hi) if lo <= hi else None


def cobertura(p, cam, segs):
    """Alcances del encuadre sobre el agua y tramos del canal vistos enteros.

    Devuelve un diccionario con:
      cerca, lejos  distancia x del agua en el borde inferior y superior de la
                    columna central (lejos = inf si esa columna ve el cielo);
      agua_entera   intervalo de x con las dos orillas del agua en la imagen;
      canal_entero  intervalo de x con los dos bordes del canal en la imagen;
      y_seccion     intervalo de y del agua visible en la seccion x_s;
      orillas_ok    las dos orillas de la seccion se ven y no estan tapadas.
    """
    T, B = anchos(p)
    d, xs = p["tirante"], p["xs"]
    W, H = cam["W"], cam["H"]
    abajo = interseccion_agua(cam, rayo(cam, W / 2.0, H), d)
    arriba = interseccion_agua(cam, rayo(cam, W / 2.0, 0.0), d)
    ex, ey = (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)
    agua = _cortar(intervalo(cam, (0.0, -T / 2.0, d), ex, 0.0, LEJOS),
                   intervalo(cam, (0.0, T / 2.0, d), ex, 0.0, LEJOS))
    canal = _cortar(intervalo(cam, (0.0, -B / 2.0, p["hc"]), ex, 0.0, LEJOS),
                    intervalo(cam, (0.0, B / 2.0, p["hc"]), ex, 0.0, LEJOS))
    ysec = intervalo(cam, (xs, 0.0, d), ey, -LEJOS, LEJOS)
    orillas = all(en_imagen(cam, proyectar(cam, P)) and es_visible(cam, segs, P)
                  for P in ((xs, -T / 2.0, d), (xs, T / 2.0, d)))
    return dict(cerca=abajo[0] if abajo else None,
                lejos=arriba[0] if arriba else float("inf"),
                agua_entera=agua, canal_entero=canal,
                y_seccion=ysec, orillas_ok=orillas)


def huella(cam, cota, alcance, n=24):
    """(F12) Contorno en planta del campo de vision sobre el plano z = cota,
    recortado a la distancia alcance (para los rayos que ven el cielo)."""
    W, H = cam["W"], cam["H"]
    borde = ([(W * i / n, 0.0) for i in range(n)] +
             [(W, H * i / n) for i in range(n)] +
             [(W * (n - i) / n, H) for i in range(n)] +
             [(0.0, H * (n - i) / n) for i in range(n)])
    C = cam["C"]
    puntos = []
    for u, v in borde:
        d = rayo(cam, u, v)
        P = interseccion_agua(cam, d, cota)
        lh = math.hypot(d[0], d[1])
        if P is None or math.hypot(P[0] - C[0], P[1] - C[1]) > alcance:
            if lh < 1e-12:
                continue
            P = (C[0] + alcance * d[0] / lh, C[1] + alcance * d[1] / lh)
        puntos.append((P[0], P[1]))
    return puntos


# =============================================================================
# 4. STIV
# =============================================================================

# >>> AJUSTABLE <<< Umbrales de calificacion: criterio propio, no norma.
# (F9) Rangos de angulo de la STI, en grados desde el eje de tiempo. A 20 y
# 70 grados el error de velocidad (F10) es 1.56 veces el minimo de 45; a 10
# y 80, 2.9 veces.
ANGULO_BUENO = (20.0, 70.0)
ANGULO_ACEPTABLE = (10.0, 80.0)
# (F14) Tamano del trazador en pixeles: bueno / aceptable.
TRAZADOR_PX = (2.0, 1.0)
# (F8) Longitud de la linea de busqueda en pixeles: buena / aceptable.
LINEA_PX = (60.0, 30.0)
# Margen respecto al borde de la imagen, en fraccion del lado, que se deja al
# colocar la seccion automaticamente.
MARGEN_IMAGEN = 0.02     # >>> AJUSTABLE <<<
MAX_SECCION = 500.0      # distancia maxima de busqueda de la seccion [m]

NIVELES = ("BUENO", "ACEPTABLE", "POBRE", "FUERA")


def peor(*califs):
    return max(califs, key=NIVELES.index)


def calificar_angulo(th):
    if ANGULO_BUENO[0] <= th <= ANGULO_BUENO[1]:
        return "BUENO"
    if ANGULO_ACEPTABLE[0] <= th <= ANGULO_ACEPTABLE[1]:
        return "ACEPTABLE"
    return "POBRE"


def calificar_px(n, umbrales):
    return "BUENO" if n >= umbrales[0] else (
        "ACEPTABLE" if n >= umbrales[1] else "POBRE")


def angulo_sti(v, g, fps, paso):
    """(F9) Desplazamiento [px/imagen usada] y angulo [grados] en la STI."""
    desp = v * paso / (fps * g)
    return desp, math.degrees(math.atan(desp))


def error_velocidad(th_grados, dtheta_grados):
    """(F10) Error relativo de velocidad [%] por un error angular."""
    th = math.radians(th_grados)
    den = math.sin(th) * math.cos(th)
    if den <= 1e-12:
        return float("inf")
    return 100.0 * math.radians(dtheta_grados) / den


def apuntar(p, xs):
    """(F13) Inclinacion y giro [grados] que llevan el eje optico al centro
    del canal en la seccion x_s."""
    dy = -p["ycam"]
    giro = math.degrees(math.atan2(dy, xs))
    incl = math.degrees(math.atan2(p["zcam"] - p["tirante"],
                                   math.hypot(xs, dy)))
    return incl, giro


def orientar(p, xs):
    """Copia de p con la seccion en xs y, si se pide, la camara apuntada."""
    q = dict(p, xs=xs)
    if p["auto_apuntar"]:
        q["incl"], q["giro"] = apuntar(p, xs)
    return q


def lineas_busqueda(p):
    """Lineas de busqueda paralelas al flujo, centradas en la seccion x_s y
    repartidas en el centro de n franjas iguales del ancho de agua."""
    T = anchos(p)[0]
    n, L, xs, d = p["n_lineas"], p["largo"], p["xs"], p["tirante"]
    lineas = []
    for i in range(n):
        y = -T / 2.0 + T * (i + 0.5) / n
        lineas.append(dict(n=i + 1, y=y, A=(xs - L / 2.0, y, d),
                           B=(xs + L / 2.0, y, d)))
    return lineas


def cabe_seccion(p):
    """¿Caben enteras en la imagen (con margen) y sin tapar todas las lineas
    de busqueda y las dos orillas de la seccion? Devuelve (ok, motivos)."""
    cam = camara(p)
    segs = segmentos(p)
    T = anchos(p)[0]
    margen = MARGEN_IMAGEN * min(cam["W"], cam["H"])
    motivos = []
    if p["xs"] - p["largo"] / 2.0 < p["x_puente"] - 1e-9:
        motivos.append("las lineas empiezan a menos de %.1f m del puente"
                       % p["x_puente"])
    fuera = []
    for ln in lineas_busqueda(p):
        for P in (ln["A"], ln["B"]):
            if not (en_imagen(cam, proyectar(cam, P), margen)
                    and es_visible(cam, segs, P)):
                fuera.append("L%d" % ln["n"])
                break
    if fuera:
        motivos.append("no se ven enteras: %s" % ", ".join(fuera))
    for lado, y in (("izquierda", -T / 2.0), ("derecha", T / 2.0)):
        P = (p["xs"], y, p["tirante"])
        if not (en_imagen(cam, proyectar(cam, P), margen)
                and es_visible(cam, segs, P)):
            motivos.append("no se ve la orilla %s" % lado)
    return not motivos, motivos


def seccion_auto(p):
    """Seccion de medida mas cercana al puente (mejor resolucion) en la que
    cabe todo (cabe_seccion). Barrido con paso creciente y biseccion final.
    Devuelve None si no hay ninguna hasta MAX_SECCION."""
    def cabe(xs):
        return cabe_seccion(orientar(p, xs))[0]

    x0 = p["x_puente"] + p["largo"] / 2.0
    if cabe(x0):
        return x0
    xs = x0
    while xs < MAX_SECCION:
        sig = xs + max(0.25, 0.02 * xs)
        if cabe(sig):
            lo, hi = xs, sig
            for _ in range(40):
                mid = (lo + hi) / 2.0
                if cabe(mid):
                    hi = mid
                else:
                    lo = mid
            return hi
        xs = sig
    return None


def resolver(p):
    """Fija la seccion y la orientacion. Devuelve (q, aviso)."""
    if p["auto_seccion"]:
        xs = seccion_auto(p)
        if xs is None:
            return orientar(p, p["xs"]), (
                "No hay ninguna seccion hasta %.0f m en la que quepa todo; "
                "se usa la distancia escrita." % MAX_SECCION)
        return orientar(p, xs), None
    return orientar(p, p["xs"]), None


def analizar(q):
    """Calculos completos para una configuracion ya resuelta."""
    cam = camara(q)
    segs = segmentos(q)
    D = q["trazador"] / 100.0
    lineas = []
    for ln in lineas_busqueda(q):
        uvA, uvB = proyectar(cam, ln["A"]), proyectar(cam, ln["B"])
        ln["uvA"], ln["uvB"] = uvA, uvB
        ln["dentro"] = all(en_imagen(cam, uv) for uv in (uvA, uvB)) and all(
            es_visible(cam, segs, P) for P in (ln["A"], ln["B"]))
        ln["califs"] = {}
        ln["vel"] = []
        if uvA is None or uvB is None:
            ln.update(px=0.0, g=float("inf"), gx_max=float("inf"),
                      gx_min=float("inf"), gy=float("inf"), traz_px=0.0,
                      calif="FUERA", nativa=False)
            lineas.append(ln)
            continue
        ln["nativa"] = True
        ln["px"] = math.hypot(uvB[0] - uvA[0], uvB[1] - uvA[1])
        ln["g"] = q["largo"] / max(ln["px"], 1e-9)
        gxs, gys = [], []
        for i in range(11):
            s = i / 10.0
            P = tuple(ln["A"][k] + s * (ln["B"][k] - ln["A"][k])
                      for k in range(3))
            gxs.append(gsd(cam, P, 0))
            gys.append(gsd(cam, P, 1))
        ln["gx_max"], ln["gx_min"] = max(gxs), min(gxs)
        ln["gy"] = gys[5]
        ln["gy_max"] = max(gys)
        ln["traz_px"] = D / max(ln["gx_max"], ln["gy_max"])
        lineas.append(ln)

    # (F9) Paso de la STI ortorrectificada, comun a todas las lineas.
    nativas = [ln for ln in lineas if ln["nativa"]]
    sx_nativo = max(ln["gx_max"] for ln in nativas) if nativas else None
    sx = sx_nativo if q["auto_sx"] or sx_nativo is None else q["sx"] / 100.0
    for ln in nativas:
        ln["sti_px"] = q["largo"] / sx
        for v in (q["vmin"], q["vmax"]):
            desp, th = angulo_sti(v, sx, q["fps"], q["paso"])
            ln["vel"].append(dict(v=v, desp=desp, th=th,
                                  err=error_velocidad(th, q["dtheta"]),
                                  calif=calificar_angulo(th)))
        ln["califs"] = dict(
            angulo=peor(*(r["calif"] for r in ln["vel"])),
            trazador=calificar_px(ln["traz_px"], TRAZADOR_PX),
            longitud=calificar_px(ln["sti_px"], LINEA_PX))
        ln["calif"] = (peor(*ln["califs"].values()) if ln["dentro"]
                       else "FUERA")

    ok, motivos = cabe_seccion(q)
    validas = [ln for ln in lineas if ln["vel"]]
    # Peor punto: el extremo de la linea con mas metros por pixel.
    peor_punto = None
    if validas:
        lp = max(validas, key=lambda ln: ln["gx_max"])
        gA, gB = gsd(cam, lp["A"], 0), gsd(cam, lp["B"], 0)
        peor_punto = (lp, lp["A"] if gA > gB else lp["B"])
    return dict(cam=cam, segs=segs, lineas=lineas, ok=ok, motivos=motivos,
                cob=cobertura(q, cam, segs), peor=peor_punto, sx=sx,
                sx_nativo=sx_nativo)


def fps_minimos(q, sx):
    """(F11) fps que mantienen la velocidad maxima por debajo de
    ANGULO_BUENO[1], con el paso k y el S_x actuales."""
    return q["vmax"] * q["paso"] / (sx *
                                    math.tan(math.radians(ANGULO_BUENO[1])))


def sx_minimo(q):
    """(F11) S_x [m/px] que deja la velocidad maxima en ANGULO_BUENO[1]."""
    return q["vmax"] * q["paso"] / (q["fps"] *
                                    math.tan(math.radians(ANGULO_BUENO[1])))


# =============================================================================
# 5. CODIFICACION PNG
# =============================================================================
#
# tkinter solo admite datos en base64 para GIF y PNG; se genera un PNG real
# sin dependencias: firma, bloques IHDR, IDAT e IEND, filas con filtro 0.

def _bloque_png(tipo, datos):
    """Un bloque PNG: longitud, tipo, datos y CRC-32 de (tipo + datos)."""
    return (struct.pack(">I", len(datos)) + tipo + datos +
            struct.pack(">I", zlib.crc32(tipo + datos) & 0xFFFFFFFF))


def png_bytes(ancho, alto, pixeles, canales):
    """Construye un PNG de 8 bits. canales = 1 (gris) o 3 (RGB)."""
    tipo_color = 0 if canales == 1 else 2
    ihdr = struct.pack(">IIBBBBB", ancho, alto, 8, tipo_color, 0, 0, 0)
    bytes_por_fila = ancho * canales
    crudo = bytearray()
    for j in range(alto):
        crudo.append(0)
        crudo += pixeles[j * bytes_por_fila:(j + 1) * bytes_por_fila]
    return (b"\x89PNG\r\n\x1a\n"
            + _bloque_png(b"IHDR", ihdr)
            + _bloque_png(b"IDAT", zlib.compress(bytes(crudo), 6))
            + _bloque_png(b"IEND", b""))


def reescalar_rgb(rgb, W, H, Wd, Hd):
    """Reescala una imagen RGB por vecino mas proximo (cada pixel del sensor
    sigue viendose como un bloque nitido)."""
    cols = [min(W - 1, int((i + 0.5) * W / Wd)) for i in range(Wd)]
    salida = bytearray()
    previa, fila = -1, b""
    for j in range(Hd):
        fj = min(H - 1, int((j + 0.5) * H / Hd))
        if fj != previa:
            base = fj * W * 3
            fila = b"".join(bytes(rgb[base + 3 * c:base + 3 * c + 3])
                            for c in cols)
            previa = fj
        salida += fila
    return bytes(salida)


def tam_vista(W, H, ancho_max, alto_max):
    """Tamano en pantalla de una imagen W x H encajada conservando la
    proporcion."""
    e = min(ancho_max / float(W), alto_max / float(H))
    return max(1, int(round(W * e))), max(1, int(round(H * e)))


# =============================================================================
# 6. SIMULACION DE LA IMAGEN VISIBLE
# =============================================================================

def _hash(i, j):
    h = (i * 374761393 + j * 668265263) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return h ^ (h >> 16)


def trazar(p, cam, segs, us, vs, escala=1.0, ss=1):
    """Color RGB de los pixeles de centros us x vs (coordenadas del sensor).

    escala es el ancho de cada pixel trazado en pixeles del sensor (mayor que
    1 si la imagen se traza reducida) y ss el supermuestreo por lado.

    Cada muestra es un rayo (F4) intersectado con la seccion (F5):
      - agua: color base con un oleaje suave y trazadores (espuma, hojas) de
        diametro p['trazador'] repartidos al azar. Si el pixel abarca mas
        que el trazador, este se reparte en el pixel con menos contraste, como
        en un sensor real: lejos del puente la textura se apaga;
      - taludes de hormigon, terreno con hierba y cielo;
      - lo que queda en x < 0 es el propio puente;
      - neblina con la distancia.
    """
    yc, zc = cam["C"][1], cam["C"][2]
    fx, fy, fz = cam["f"]
    rx, ry, _rz = cam["r"]
    ux, uy, uz = cam["up"]
    k_h, k_v, W, H = cam["k_h"], cam["k_v"], cam["W"], cam["H"]
    d = p["tirante"]
    T2 = anchos(p)[0] / 2.0
    rapido = abs(yc) <= T2       # sin talud entre la camara y el agua
    rt = p["trazador"] / 200.0
    celda = max(4.0 * 2.0 * rt, 0.03)
    pie0 = escala / ss / math.sqrt(k_h * k_v)
    sub = [((k + 0.5) / ss - 0.5) * escala for k in range(ss)]
    n2 = float(ss * ss)
    sin, sqrt, exp, floor = math.sin, math.sqrt, math.exp, math.floor

    def muestra(a, b):
        dx = fx + a * rx + b * ux
        dy = fy + a * ry + b * uy
        dz = fz + b * uz
        if dz >= -1e-9:
            e = min(1.0, dz / (math.hypot(dx, dy) + 1e-9) * 2.5)
            return (175 - 55 * e, 200 - 45 * e, 228 - 10 * e)
        imp = None
        if rapido:
            t = (d - zc) / dz
            y = yc + t * dy
            if -T2 <= y <= T2:
                imp = (t, AGUA)
        if imp is None:
            imp = primer_impacto(yc, zc, dy, dz, segs)
            if imp is None:
                return (175, 200, 228)
        t, tipo = imp
        x = t * dx
        y = yc + t * dy
        norma = sqrt(dx * dx + dy * dy + dz * dz)
        R = t * norma
        if x < 0.0:
            r, g, bl = 159.0, 211.0, 234.0
        elif tipo == AGUA:
            o = (1.0 + 0.10 * sin(1.9 * x + 0.9 * sin(0.7 * y))
                 + 0.06 * sin(3.3 * y - 0.8 * x))
            r, g, bl = 36.0 * o, 64.0 * o, 78.0 * o
            i, j = int(floor(x / celda)), int(floor(y / celda))
            h = _hash(i, j)
            if h & 1:
                cx = (i + 0.5 + 0.4 * (((h >> 1) & 1023) / 1023.0 - 0.5)) \
                    * celda
                cy = (j + 0.5 + 0.4 * (((h >> 11) & 1023) / 1023.0 - 0.5)) \
                    * celda
                pie = R * pie0 / sqrt(-dz / norma)
                re = max(rt, 0.5 * pie)
                lim = min(re, 0.3 * celda)
                if (x - cx) ** 2 + (y - cy) ** 2 <= lim * lim:
                    w = (rt / re) ** 2 * (0.7 + 0.3 * ((h >> 21) & 255) / 255.0)
                    r += (228.0 - r) * w
                    g += (228.0 - g) * w
                    bl += (215.0 - bl) * w
        elif tipo == TALUD:
            n = ((_hash(int(floor(x / 0.4)), int(floor(y / 0.4))) & 255)
                 / 255.0 - 0.5) * 18.0
            r, g, bl = 150.0 + n, 147.0 + n, 138.0 + n
        else:
            n = ((_hash(int(floor(x / 0.5)) + 7, int(floor(y / 0.5)))
                  & 255) / 255.0 - 0.5) * 26.0
            r, g, bl = 88.0 + n, 118.0 + n, 60.0 + 0.5 * n
        nb = 1.0 - exp(-R / 350.0)
        return (r + (186.0 - r) * nb, g + (196.0 - g) * nb,
                bl + (206.0 - bl) * nb)

    salida = bytearray()
    for v in vs:
        bs = [(H / 2.0 - (v + dv)) / k_v for dv in sub]
        for u in us:
            R = G = Bc = 0.0
            for b in bs:
                for du in sub:
                    c = muestra((u + du - W / 2.0) / k_h, b)
                    R += c[0]
                    G += c[1]
                    Bc += c[2]
            salida += bytes((max(0, min(255, int(R / n2))),
                             max(0, min(255, int(G / n2))),
                             max(0, min(255, int(Bc / n2)))))
    return salida


def simular(p, cam, segs, vista=None):
    """Imagen que produciria el sensor, como PNG en base64, encajada en
    vista = (Wd, Hd). Si el sensor tiene mas pixeles que la vista se traza a
    la resolucion de la vista (equivale a reducirla); si tiene menos, se
    traza a la del sensor y se amplia por bloques. Devuelve (b64, Wd, Hd)."""
    W, H = cam["W"], cam["H"]
    Wd, Hd = vista if vista is not None else (W, H)
    Wr, Hr = (W, H) if W * H <= Wd * Hd else (Wd, Hd)
    rgb = trazar(p, cam, segs,
                 [(i + 0.5) * W / Wr for i in range(Wr)],
                 [(j + 0.5) * H / Hr for j in range(Hr)],
                 escala=W / float(Wr))
    if (Wr, Hr) != (Wd, Hd):
        rgb = reescalar_rgb(rgb, Wr, Hr, Wd, Hd)
    return base64.b64encode(png_bytes(Wd, Hd, rgb, 3)).decode("ascii"), Wd, Hd


def lupa(p, cam, segs, centro, nw, nh, aumento):
    """Recorte de nw x nh pixeles del sensor alrededor de centro, trazado a
    la resolucion real con supermuestreo 3x3 y ampliado por aumento.
    Devuelve (b64, u0, v0) con la esquina superior izquierda del recorte."""
    u0 = int(round(min(max(centro[0] - nw / 2.0, 0), cam["W"] - nw)))
    v0 = int(round(min(max(centro[1] - nh / 2.0, 0), cam["H"] - nh)))
    rgb = trazar(p, cam, segs, [u0 + i + 0.5 for i in range(nw)],
                 [v0 + j + 0.5 for j in range(nh)], escala=1.0, ss=3)
    rgb = reescalar_rgb(rgb, nw, nh, nw * aumento, nh * aumento)
    png = png_bytes(nw * aumento, nh * aumento, rgb, 3)
    return base64.b64encode(png).decode("ascii"), u0, v0


# =============================================================================
# 7. INFORME NUMERICO
# =============================================================================

def _intervalo_txt(iv):
    if iv is None:
        return "en ningun tramo"
    hi = "sin limite" if iv[1] >= LEJOS * 0.99 else "%.1f m" % iv[1]
    return "de %.1f m a %s" % (iv[0], hi)


def informe(q, a, aviso=None):
    """Texto con todos los calculos."""
    L = []
    add = L.append
    cam, cob, lineas = a["cam"], a["cob"], a["lineas"]
    T, B = anchos(q)
    Hw = q["zcam"] - q["tirante"]
    validas = [ln for ln in lineas if ln["vel"]]

    add("1. CAMARA Y MONTAJE                            (F1, F2, F13)")
    add("   Sensor %d x %d px, FOV %.1f x %.1f grados, %g fps"
        % (q["res_h"], q["res_v"], q["fov_h"], q["fov_v"], q["fps"]))
    if incoherencia_fov(q) > 0.03:
        add("   AVISO: el FOV H y el V no son compatibles con pixeles"
            " cuadrados (%.0f %% de diferencia):" % (100 * incoherencia_fov(q)))
        add("   la imagen simulada se estira y la resolucion vertical no es"
            " la real.")
    add("   IFOV H / V            : %.3f / %.3f mrad"
        % (ifov_mrad(q["fov_h"], q["res_h"]), ifov_mrad(q["fov_v"],
                                                        q["res_v"])))
    add("   Camara                : %.2f m sobre el fondo, %.2f m sobre el agua,"
        " %+.2f m del eje" % (q["zcam"], Hw, q["ycam"]))
    if "h_puente" in q:
        add("   En el puente          : piso a %.2f m de la plantilla, camara"
            " %.2f m por encima del piso"
            % (q["hc"] + q["h_puente"], q["h_mastil"]))
    add("   Mira hacia            : %s" % q["mira"])
    add("   Inclinacion / giro    : %.1f / %+.1f grados  (%s)"
        % (q["incl"], q["giro"], "apuntado automatico al centro de la seccion"
           if q["auto_apuntar"] else "manual"))

    add("")
    add("2. CANAL                                       (F5)")
    add("   Trapecio: plantilla %.2f m, talud %.2f:1, bordes a %.2f m"
        % (q["b"], q["m"], q["hc"]))
    add("   Tirante %.2f m -> ancho de agua %.2f m, area mojada %.2f m2;"
        " borde a borde %.2f m"
        % (q["tirante"], T, (q["b"] + q["m"] * q["tirante"]) * q["tirante"], B))

    add("")
    add("3. COBERTURA                                   (F12)")
    add("   Agua visible en la columna central: desde %s hasta %s"
        % ("--" if cob["cerca"] is None else "%.1f m" % cob["cerca"],
           "el horizonte" if math.isinf(cob["lejos"])
           else "%.1f m" % cob["lejos"]))
    add("   Ancho de agua entero en la imagen : %s"
        % _intervalo_txt(cob["agua_entera"]))
    add("   Canal entero de borde a borde     : %s"
        % _intervalo_txt(cob["canal_entero"]))
    ys = cob["y_seccion"]
    add("   En la seccion (x = %.2f m) se ve el agua de y = %s a %s"
        " (orillas en +-%.2f m): %s"
        % (q["xs"], "--" if ys is None else "%.2f" % max(ys[0], -LEJOS),
           "--" if ys is None else "%.2f" % min(ys[1], LEJOS), T / 2.0,
           "ANCHO COMPLETO" if cob["orillas_ok"] else "INCOMPLETO"))
    add("   Seccion %s; lineas de %.1f m desde x = %.2f hasta %.2f m"
        % ("colocada automaticamente lo mas cerca posible del puente"
           if q["auto_seccion"] else "colocada a mano", q["largo"],
           q["xs"] - q["largo"] / 2.0, q["xs"] + q["largo"] / 2.0))
    if aviso:
        add("   AVISO: " + aviso)
    if not a["ok"]:
        add("   PROBLEMAS: " + "; ".join(a["motivos"]) + ".")

    add("")
    add("4. RESOLUCION EN LAS LINEAS DE BUSQUEDA [cm/px]   (F6, F8, F14)")
    add("   Linea     y     px de   flujo   flujo   flujo   ancho   trazador"
        "  en")
    add("            [m]   largo   medio   mejor   peor    centro  [px]    "
        "  imagen")
    for ln in lineas:
        if not ln["vel"]:
            add("   L%-3d %+7.2f   detras de la camara" % (ln["n"], ln["y"]))
            continue
        add("   L%-3d %+7.2f %7.0f %7.2f %7.2f %7.2f %7.2f %7.1f     %s"
            % (ln["n"], ln["y"], ln["px"], ln["g"] * 100, ln["gx_min"] * 100,
               ln["gx_max"] * 100, ln["gy"] * 100, ln["traz_px"],
               "si" if ln["dentro"] else "NO"))
    if validas:
        rel = max(ln["gx_max"] / ln["gx_min"] for ln in validas)
        add("   La resolucion a lo largo del flujo varia x%.2f dentro de una"
            " misma linea%s" % (rel, " (alta: la ortorrectificacion"
                                     " interpolara mucho en el extremo lejano)"
                                if rel > 1.5 else "."))

    add("")
    add("5. CHEQUEO STIV  (paso k = %d -> %.3f s entre imagenes usadas)"
        "   (F9, F10)" % (q["paso"], q["paso"] / q["fps"]))
    if a["sx"] is not None:
        add("   STI ortorrectificada a S_x = %.2f cm/px (%s): %.0f px por linea"
            % (a["sx"] * 100, "auto = peor GSD nativo" if q["auto_sx"]
               else "elegido", q["largo"] / a["sx"]))
        if a["sx"] < a["sx_nativo"] * 0.999:
            add("   AVISO: S_x mas fino que el GSD nativo del peor punto"
                " (%.2f cm/px): la STI interpola detalle que no existe."
                % (a["sx_nativo"] * 100))
    add("   Angulo de la STI desde el eje de tiempo; error de velocidad para"
        " %.2f grados de error angular." % q["dtheta"])
    add("   Linea   v = %.2f m/s: px/img  angulo  error |"
        "  v = %.2f m/s: px/img  angulo  error" % (q["vmin"], q["vmax"]))
    for ln in validas:
        c = []
        for r in ln["vel"]:
            c.append("%6.2f %6.1f %5.1f%%" % (r["desp"], r["th"],
                                               min(r["err"], 999.9)))
        add("   L%-3d %26s | %26s" % (ln["n"], c[0], c[1]))
    add("   Bueno entre %.0f y %.0f grados; aceptable entre %.0f y %.0f."
        % (ANGULO_BUENO + ANGULO_ACEPTABLE))

    add("")
    add("6. RECOMENDACIONES                             (F11)")
    if validas:
        sx = a["sx"]
        k_lento = q["fps"] * sx / q["vmin"]
        k_rapido = q["fps"] * sx / q["vmax"]
        add("   Para %.2f m/s a 45 grados: paso k ~ %d (una de cada %d"
            " imagenes)." % (q["vmin"], max(1, round(k_lento)),
                             max(1, round(k_lento))))
        if k_rapido >= 1.0:
            add("   Para %.2f m/s a 45 grados: paso k ~ %d."
                % (q["vmax"], max(1, round(k_rapido))))
        else:
            add("   Para %.2f m/s a 45 grados harian falta %.0f fps con k = 1"
                " y S_x = %.2f cm/px." % (q["vmax"], q["vmax"] / sx, sx * 100))
        fmin = fps_minimos(q, sx)
        add("   Para que %.2f m/s no pase de %.0f grados con k = %d hace falta"
            " una de estas:" % (q["vmax"], ANGULO_BUENO[1], q["paso"]))
        add("     - %.0f fps con S_x = %.2f cm/px%s"
            % (fmin, sx * 100, "  (la camara da %g: OK)" % q["fps"]
               if fmin <= q["fps"] else "  (la camara da %g)" % q["fps"]))
        smin = sx_minimo(q)
        add("     - S_x >= %.2f cm/px con %g fps, que deja %.0f px en cada"
            " linea de %.1f m%s"
            % (smin * 100, q["fps"], q["largo"] / smin, q["largo"],
               "" if q["largo"] / smin >= LINEA_PX[1]
               else " (pocos: alarga la linea)"))
        if q["vmax"] / q["vmin"] > (math.tan(math.radians(ANGULO_BUENO[1])) /
                                    math.tan(math.radians(ANGULO_BUENO[0]))):
            add("   El rango %.2f-%.2f m/s es mas ancho de lo que cabe entre %.0f"
                " y %.0f grados con un solo paso k:"
                % (q["vmin"], q["vmax"], ANGULO_BUENO[0], ANGULO_BUENO[1]))
            add("   conviene elegir k segun la velocidad (o el nivel) de cada"
                " aforo.")
        add("   Imagenes en cada STI: %d (%.1f s a %g fps con k = %d)."
            % (int(q["duracion"] * q["fps"] / q["paso"]), q["duracion"],
               q["fps"], q["paso"]))

    add("")
    add("7. VEREDICTO")
    for ln in lineas:
        if ln["calif"] == "FUERA":
            add("   L%d  FUERA DE IMAGEN O TAPADA." % ln["n"])
            continue
        c = ln["califs"]
        add("   L%d  %-9s (angulo %s, trazador %s, longitud %s)"
            % (ln["n"], ln["calif"], c["angulo"].lower(),
               c["trazador"].lower(), c["longitud"].lower()))
    add("")
    add("   Antes de instalar, comprueba en campo que haya textura en la")
    add("   superficie (oleaje, espuma, restos) y evita los reflejos del sol")
    add("   y la sombra del puente sobre las lineas. Mide puntos de control")
    add("   en las dos orillas para la ortorrectificacion.")
    return "\n".join(L)


# =============================================================================
# 8. MODELOS DE CAMARA
# =============================================================================
#
# Camaras genericas con el FOV teorico de un sensor y una focal tipicos, y
# las que guarda el usuario en camaras_visibles.json:
#     {nombre: {res_h, res_v, fov_h, fov_v, fps}}

RUTA_CAMARAS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "salidas",
                            "camaras_visibles.json")


def _fov(lado_mm, focal_mm):
    return round(math.degrees(2.0 * math.atan(lado_mm / (2.0 * focal_mm))), 1)


def _genericas():
    sensores = (("1080p 1/2.8in", 1920, 1080, 5.376, 3.024,
                 (2.8, 4.0, 6.0, 8.0, 12.0)),
                ("4K 1/1.8in", 3840, 2160, 7.68, 4.32, (4.0, 8.0, 12.0)))
    camaras = {}
    for nombre, w, h, sw, sh, focales in sensores:
        for f in focales:
            camaras["Generica %s f=%g mm" % (nombre, f)] = dict(
                res_h=w, res_v=h, fov_h=_fov(sw, f), fov_v=_fov(sh, f),
                fps=25.0)
    return camaras


GENERICAS = _genericas()

# Hikvision DS-2CD3646G2T-IZS/TPM (ficha tecnica): sensor 1/1.8", 2688 x 1520,
# lente motorizada 2.7-13.5 mm, 25 fps a 50 Hz y 30 fps a 60 Hz.
#
# Los FOV de la ficha NO se usan: son incoherentes entre si. Con pixeles
# cuadrados tan(HFOV/2) / tan(VFOV/2) tiene que valer 2688/1520 = 1.77, y la
# ficha da 2.58 a 2.7 mm (114.6 x 62.3) y 2.21 a 13.5 mm (43.8 x 20.6). Por
# eso el FOV se calcula de la focal y del tamano del pixel, como una lente
# sin distorsion (FOV = 2 atan(N p / 2f)). El pixel de 2.9 um es el de los
# sensores de 1/1.8" y 2688 x 1520; no figura en la ficha. A 2.7 mm la lente
# real tiene distorsion de barril (la ficha da 130.9 grados de diagonal frente
# a 117.7 sin distorsion): hacia los bordes de la imagen el modelo se aleja
# de la realidad. Para resultados exactos hay que calibrar la camara.
HIKVISION = "Hikvision DS-2CD3646G2T-IZS"
PIXEL_HIKVISION_MM = 0.0029      # >>> AJUSTABLE <<< no viene en la ficha


def fov_de_focal(n_pix, pixel_mm, focal_mm):
    """FOV [grados] de una lente sin distorsion: 2 atan(N p / (2 f))."""
    return math.degrees(2.0 * math.atan(n_pix * pixel_mm / (2.0 * focal_mm)))


for _f in (2.7, 4.0, 6.0, 8.0, 10.0, 13.5):
    GENERICAS["%s f=%g mm" % (HIKVISION, _f)] = dict(
        res_h=2688, res_v=1520,
        fov_h=round(fov_de_focal(2688, PIXEL_HIKVISION_MM, _f), 2),
        fov_v=round(fov_de_focal(1520, PIXEL_HIKVISION_MM, _f), 2),
        fps=30.0)


def incoherencia_fov(p):
    """Diferencia relativa entre tan(HFOV/2)/tan(VFOV/2) y W/H. Un sensor
    real (pixel cuadrado, sin distorsion) da 0."""
    r = (math.tan(math.radians(p["fov_h"]) / 2.0) /
         math.tan(math.radians(p["fov_v"]) / 2.0))
    return abs(r / (p["res_h"] / float(p["res_v"])) - 1.0)


def cargar_camaras(ruta=RUTA_CAMARAS):
    """Lee las camaras guardadas; {} si no hay fichero o esta danado.
    Descarta entradas incompletas."""
    try:
        with open(ruta, "r", encoding="utf-8") as fh:
            datos = json.load(fh)
    except (OSError, ValueError):
        return {}
    camaras = {}
    if isinstance(datos, dict):
        for nombre, c in datos.items():
            try:
                camaras[str(nombre)] = dict(
                    res_h=int(c["res_h"]), res_v=int(c["res_v"]),
                    fov_h=float(c["fov_h"]), fov_v=float(c["fov_v"]),
                    fps=float(c.get("fps", 25.0)))
            except (KeyError, TypeError, ValueError, AttributeError):
                continue
    return camaras


def guardar_camaras(camaras, ruta=RUTA_CAMARAS):
    """Escribe las camaras pasando por un temporal."""
    os.makedirs(os.path.dirname(os.path.abspath(ruta)), exist_ok=True)
    tmp = ruta + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(camaras, fh, indent=2, ensure_ascii=False, sort_keys=True)
    os.replace(tmp, ruta)


# =============================================================================
# 9. INTERFAZ GRAFICA
# =============================================================================

try:
    import tkinter as tk
    from tkinter import messagebox, ttk
    HAY_TK = True
except ImportError:
    HAY_TK = False

CAMARA_INICIAL = HIKVISION + " f=2.7 mm"

# (clave, etiqueta, valor inicial, tipo)
ENTRADAS_CAMARA = [
    ("fov_h", "FOV horizontal (grados)",
     "%g" % GENERICAS[CAMARA_INICIAL]["fov_h"], float),
    ("fov_v", "FOV vertical (grados)",
     "%g" % GENERICAS[CAMARA_INICIAL]["fov_v"], float),
    ("fps", "Imagenes por segundo (fps)", "30", float),
]
# Canal y puente de entradas/Medidas_canal_y_puente.pdf: 11.4 m entre bordes
# con el tirante maximo, 3 m de la plantilla al arranque del puente y 0.85 m
# de altura del puente.
# >>> AJUSTABLE <<< Sin medir: el talud (1.5:1 es un valor tipico; de el sale
# la plantilla), el tirante de operacion (2.0 m), la posicion lateral de la
# camara (centro del claro) y la distancia minima de las lineas al puente.
ENTRADAS_CANAL = [
    ("ancho_bordes", "Ancho entre bordes (m)", "11.4", float),
    ("m", "Talud (horizontal por 1 vertical)", "1.5", float),
    ("hc", "Altura de los bordes sobre la plantilla (m)", "3", float),
    ("tirante", "Tirante del agua (m)", "2.0", float),
]
ENTRADAS_MONTAJE = [
    ("h_puente", "Altura del puente sobre los bordes (m)", "0.85", float),
    ("ycam", "Posicion lateral desde el eje (m)", "0", float),
    ("x_puente", "Distancia minima al puente (m)", "2", float),
]
ENTRADAS_STIV = [
    ("vmin", "Velocidad minima (m/s)", "0.1", float),
    ("vmax", "Velocidad maxima (m/s)", "2", float),
    ("n_lineas", "Numero de lineas de busqueda", "5", int),
    ("largo", "Longitud de cada linea (m)", "3", float),
    ("xs", "Distancia de la seccion al puente (m)", "10", float),
    ("paso", "Paso de imagenes k", "1", int),
    ("sx", "Resolucion de la STI S_x (cm/px)", "1", float),
    ("trazador", "Tamano de los trazadores (cm)", "5", float),
    ("duracion", "Duracion de cada STI (s)", "10", float),
    ("dtheta", "Error angular del STIV (grados)", "1", float),
]
TODAS = ENTRADAS_CAMARA + ENTRADAS_CANAL + ENTRADAS_MONTAJE + ENTRADAS_STIV

RESOLUCIONES = ["640x480", "1280x720", "1280x960", "1920x1080", "2560x1440",
                "2688x1520", "3840x2160"]
MIRADAS = ("aguas arriba", "aguas abajo")
MAX_LINEAS = 15

ANCHO_VISTA, ALTO_VISTA = 480, 270
ANCHO_LADO = 236
LUPA_NW, LUPA_NH, LUPA_AUMENTO = 44, 30, 5

COLORES = {"BUENO": "#2a9d4b", "ACEPTABLE": "#e8a33d", "POBRE": "#d64545",
           "FUERA": "#888888"}
COLOR_AGUA = "#9cc9e6"
COLOR_TALUD = "#c9c6bd"
COLOR_TERRENO = "#d5e6c3"

# Pasarela de la foto de Medidas.pdf: armadura de acero azul de 0.85 m de
# canto (dato medido, h_puente) con piso arriba y baranda de postes y
# pasamanos. Las demas dimensiones no estan medidas: se estiman de la foto.
COLOR_PUENTE = "#3f8fc4"
COLOR_PISO = "#9fd3ea"
# >>> AJUSTABLE <<< Estimados a ojo de la foto; solo afectan al dibujo.
ANCHO_PISO = 1.2       # ancho de la pasarela [m], estimado
ALTO_BARANDA = 1.1     # pasamanos sobre el piso [m], estimado
PASO_PANEL = 0.85      # ancho de cada triangulo de la armadura [m], estimado
PASO_POSTE = 1.9       # separacion de los postes de la baranda [m], estimado
APOYO_PUENTE = 0.6     # tramo que apoya sobre cada borde del canal [m]


def leer_resolucion(texto):
    """'1920x1080' -> (1920, 1080); None si no es valida."""
    partes = texto.strip().lower().replace(" ", "").split("x")
    try:
        ancho, alto = (int(v) for v in partes)
    except ValueError:
        return None
    return (ancho, alto) if ancho > 0 and alto > 0 else None


def dibujar_pasarela(c, Y, Z, y0, y1, z_inf, canto, camara=None):
    """Alzado de la pasarela entre las abscisas y0 e y1: cordon inferior a
    z_inf, piso a z_inf + canto, armadura con montantes y diagonales en
    zigzag, y baranda de postes con pasamanos. camara = (y, z) dibuja la
    camara sujeta a un poste."""
    z_piso = z_inf + canto
    z_mano = z_piso + ALTO_BARANDA
    n = max(2, int(round((y1 - y0) / PASO_PANEL)))
    paso = (y1 - y0) / n
    for i in range(n + 1):
        y = y0 + i * paso
        c.create_line(Y(y), Z(z_inf), Y(y), Z(z_piso), fill=COLOR_PUENTE)
    for i in range(n):
        ya, yb = y0 + i * paso, y0 + (i + 1) * paso
        if i % 2 == 0:
            c.create_line(Y(ya), Z(z_inf), Y(yb), Z(z_piso), fill=COLOR_PUENTE)
        else:
            c.create_line(Y(ya), Z(z_piso), Y(yb), Z(z_inf), fill=COLOR_PUENTE)
    c.create_line(Y(y0), Z(z_inf), Y(y1), Z(z_inf), fill=COLOR_PUENTE, width=2)
    c.create_rectangle(Y(y0), Z(z_piso) - 3, Y(y1), Z(z_piso),
                       fill=COLOR_PISO, outline=COLOR_PUENTE)
    m = max(1, int(round((y1 - y0) / PASO_POSTE)))
    for i in range(m + 1):
        y = y0 + (y1 - y0) * i / m
        c.create_line(Y(y), Z(z_piso), Y(y), Z(z_mano), fill=COLOR_PUENTE,
                      width=2 if i in (0, m) else 1)
    c.create_line(Y(y0), Z(z_mano), Y(y1), Z(z_mano), fill=COLOR_PUENTE,
                  width=2)
    if camara is not None:
        cy, cz = camara
        c.create_line(Y(cy), Z(z_piso), Y(cy), Z(max(cz, z_piso)),
                      fill="#333", width=2)
        c.create_rectangle(Y(cy) - 6, Z(cz) - 4, Y(cy) + 6, Z(cz) + 4,
                           fill="#333", outline="#fff")


def tramos_en_imagen(cam, P0, P1, n=48):
    """Tramos (listas de (u, v)) de la recta P0-P1 que caen en la imagen."""
    tramos, actual = [], []
    for i in range(n + 1):
        s = i / float(n)
        uv = proyectar(cam, tuple(P0[k] + s * (P1[k] - P0[k])
                                  for k in range(3)))
        if en_imagen(cam, uv):
            actual.append(uv)
        else:
            if len(actual) >= 2:
                tramos.append(actual)
            actual = []
    if len(actual) >= 2:
        tramos.append(actual)
    return tramos


class App:

    def __init__(self, root):
        self.root = root
        root.title("Simulador de encuadre STIV - camara en puente sobre canal")
        self._pendiente = None
        self._img = None
        self._img_lupa = None

        raiz = ttk.Frame(root, padding=10)
        raiz.grid(row=0, column=0, sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # ---------------- columna izquierda: controles en pestanas ---------
        # Las pestanas y el panel STIV debajo mantienen la ventana dentro de
        # una pantalla de 1536 x 864 con escalado al 125 %.
        columna = ttk.Frame(raiz)
        columna.grid(row=0, column=0, sticky="nw", padx=(0, 12))
        cuaderno = ttk.Notebook(columna)
        cuaderno.grid(row=0, column=0, sticky="nw")
        self.ent = {}

        izq = ttk.Frame(cuaderno, padding=6)
        cuaderno.add(izq, text="Camara")
        fila = 0
        ttk.Label(izq, text="Modelo").grid(row=fila, column=0, sticky="w")
        fila += 1
        self.camaras = cargar_camaras()
        self.modelo = tk.StringVar(value=CAMARA_INICIAL)
        self.cb_modelo = ttk.Combobox(izq, textvariable=self.modelo, width=34)
        self.cb_modelo.grid(row=fila, column=0, columnspan=2, sticky="ew",
                            pady=1)
        self.cb_modelo.bind("<<ComboboxSelected>>",
                            lambda _e: self.cargar_modelo())
        self._refrescar_modelos()
        fila += 1
        botones = ttk.Frame(izq)
        botones.grid(row=fila, column=0, columnspan=2, sticky="w", pady=(2, 0))
        ttk.Button(botones, text="Guardar camara",
                   command=self.guardar_modelo).pack(side="left")
        ttk.Button(botones, text="Eliminar",
                   command=self.eliminar_modelo).pack(side="left", padx=(6, 0))
        fila += 1
        self.lbl_modelo = ttk.Label(izq, text="", foreground="#666",
                                    wraplength=250)
        self.lbl_modelo.grid(row=fila, column=0, columnspan=2, sticky="w")
        fila += 1

        ttk.Label(izq, text="Resolucion (px)").grid(row=fila, column=0,
                                                    sticky="w")
        self.resolucion = tk.StringVar(value="1920x1080")
        cb_res = ttk.Combobox(izq, textvariable=self.resolucion, width=10,
                              values=RESOLUCIONES)
        cb_res.grid(row=fila, column=1, sticky="e", padx=(8, 0), pady=1)
        cb_res.bind("<<ComboboxSelected>>", lambda _e: self.programar())
        cb_res.bind("<KeyRelease>", lambda _e: self.programar())
        fila += 1
        fila = self._entradas(izq, fila, ENTRADAS_CAMARA)
        self.guias = tk.BooleanVar(value=True)
        ttk.Checkbutton(izq, text="Mostrar guias sobre la imagen",
                        variable=self.guias,
                        command=self.programar).grid(
            row=fila, column=0, columnspan=2, sticky="w", pady=(6, 0))
        fila += 1

        izq = ttk.Frame(cuaderno, padding=6)
        cuaderno.add(izq, text="Canal y montaje")
        fila = self._titulo(izq, 0, "Canal trapezoidal", separador=False)
        fila = self._entradas(izq, fila, ENTRADAS_CANAL)

        fila = self._titulo(izq, fila, "Montaje en el puente")
        fila = self._entradas(izq, fila, ENTRADAS_MONTAJE)
        # >>> AJUSTABLE <<< Altura de montaje sin decidir: 1 m sobre el piso,
        # a la altura de la baranda.
        self.h_mastil = tk.DoubleVar(value=1.0)
        fila, _esc, _ent = self._deslizador(
            izq, fila, "Camara sobre el piso del puente (m)", self.h_mastil,
            0.0, 6.0, 0.05, "%.2f")
        ttk.Label(izq, text="Mira hacia").grid(row=fila, column=0, sticky="w")
        self.mira = tk.StringVar(value=MIRADAS[0])
        cb = ttk.Combobox(izq, textvariable=self.mira, width=12,
                          state="readonly", values=MIRADAS)
        cb.grid(row=fila, column=1, sticky="e", padx=(8, 0), pady=1)
        cb.bind("<<ComboboxSelected>>", lambda _e: self.programar())
        fila += 1
        self.incl = tk.DoubleVar(value=25.0)
        fila, self.esc_incl, self.ent_incl = self._deslizador(
            izq, fila, "Inclinacion hacia abajo (grados)", self.incl,
            0.0, 90.0, 0.1, "%.1f")
        self.giro = tk.DoubleVar(value=0.0)
        fila, self.esc_giro, self.ent_giro = self._deslizador(
            izq, fila, "Giro en planta (grados, + derecha)", self.giro,
            -60.0, 60.0, 0.1, "%+.1f")
        self.auto_apuntar = tk.BooleanVar(value=True)
        ttk.Checkbutton(izq, text="Apuntar al centro de la seccion",
                        variable=self.auto_apuntar,
                        command=self.programar).grid(
            row=fila, column=0, columnspan=2, sticky="w")
        fila += 1

        izq = ttk.Frame(cuaderno, padding=6)
        cuaderno.add(izq, text="STIV")
        fila = self._entradas(izq, 0, ENTRADAS_STIV)
        self.auto_seccion = tk.BooleanVar(value=True)
        ttk.Checkbutton(izq, text="Seccion lo mas cerca posible del puente",
                        variable=self.auto_seccion,
                        command=self.programar).grid(
            row=fila, column=0, columnspan=2, sticky="w")
        fila += 1
        self.auto_sx = tk.BooleanVar(value=True)
        ttk.Checkbutton(izq, text="S_x = GSD nativo del peor punto",
                        variable=self.auto_sx,
                        command=self.programar).grid(
            row=fila, column=0, columnspan=2, sticky="w")
        fila += 1

        ttk.Label(columna, text="STIV en la seccion").grid(
            row=1, column=0, sticky="w", pady=(8, 0))
        self.c_stiv = tk.Canvas(columna, width=ANCHO_LADO + 30, height=240,
                                highlightthickness=1,
                                highlightbackground="#999",
                                background="white")
        self.c_stiv.grid(row=2, column=0, sticky="nw", pady=(2, 0))

        # ---------------- vistas ------------------------------------------
        der = ttk.Frame(raiz)
        der.grid(row=0, column=1, sticky="nw")
        ttk.Label(der, text="Perfil longitudinal").grid(row=0, column=0,
                                                        sticky="w")
        ttk.Label(der, text="Planta").grid(row=0, column=1, sticky="w",
                                           padx=(6, 0))
        self.lbl_seccion = ttk.Label(der, text="Seccion transversal")
        self.lbl_seccion.grid(row=0, column=2, sticky="w", padx=(6, 0))

        self.c_lateral = self._lienzo(der, ANCHO_VISTA, 170, 1, 0)
        self.c_planta = self._lienzo(der, ANCHO_LADO, 170 + 26 + ALTO_VISTA,
                                     1, 1, rowspan=3)
        self.c_seccion = self._lienzo(der, ANCHO_LADO, 170, 1, 2)

        self.lbl_vista = ttk.Label(der, text="Lo que ve la camara")
        self.lbl_vista.grid(row=2, column=0, sticky="w", pady=(6, 0))
        self.lbl_lupa = ttk.Label(der, text="Lupa a resolucion real")
        self.lbl_lupa.grid(row=2, column=2, sticky="w", padx=(6, 0),
                           pady=(6, 0))
        self.c_vista = self._lienzo(der, ANCHO_VISTA, ALTO_VISTA, 3, 0)
        self.c_lupa = self._lienzo(der, ANCHO_LADO, ALTO_VISTA, 3, 2)

        ttk.Label(der, text="Calculos").grid(row=4, column=0, sticky="w",
                                             pady=(6, 0))
        marco = ttk.Frame(der)
        marco.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=(2, 0))
        marco.columnconfigure(0, weight=1)
        self.txt = tk.Text(marco, width=100, height=12, wrap="none",
                           font=("TkFixedFont", 9))
        self.txt.grid(row=0, column=0, sticky="nsew")
        barra = ttk.Scrollbar(marco, orient="vertical", command=self.txt.yview)
        barra.grid(row=0, column=1, sticky="ns")
        self.txt.configure(yscrollcommand=barra.set)

        self.cargar_modelo(silencioso=True)
        self.actualizar()

    # ------------------------------------------------------------------
    def _lienzo(self, padre, w, h, fila, col, rowspan=1):
        c = tk.Canvas(padre, width=w, height=h, highlightthickness=1,
                      highlightbackground="#999", background="white")
        c.grid(row=fila, column=col, rowspan=rowspan, sticky="nw",
               padx=(6, 0) if col else (0, 0), pady=(2, 0))
        return c

    def _titulo(self, padre, fila, texto, separador=True):
        if separador:
            ttk.Separator(padre, orient="horizontal").grid(
                row=fila, column=0, columnspan=2, sticky="ew", pady=6)
            fila += 1
        ttk.Label(padre, text=texto, font=("TkDefaultFont", 9, "bold")).grid(
            row=fila, column=0, columnspan=2, sticky="w", pady=(0, 3))
        return fila + 1

    def _entradas(self, padre, fila, lista):
        for clave, etiqueta, valor, _tipo in lista:
            ttk.Label(padre, text=etiqueta).grid(row=fila, column=0,
                                                 sticky="w")
            e = ttk.Entry(padre, width=9, justify="right")
            e.insert(0, valor)
            e.grid(row=fila, column=1, sticky="e", padx=(8, 0), pady=1)
            e.bind("<KeyRelease>", lambda _e: self.programar())
            self.ent[clave] = e
            fila += 1
        return fila

    def _deslizador(self, padre, fila, etiqueta, var, lo, hi, paso, fmt):
        """Etiqueta + Scale + campo de texto sincronizados."""
        ttk.Label(padre, text=etiqueta).grid(row=fila, column=0,
                                             columnspan=2, sticky="w")
        ent = ttk.Entry(padre, width=9, justify="right")
        ent.grid(row=fila + 1, column=1, sticky="e", padx=(8, 0))

        def escribir():
            estado = str(ent.cget("state"))
            ent.configure(state="normal")
            ent.delete(0, "end")
            ent.insert(0, fmt % var.get())
            ent.configure(state=estado)

        def desde_texto(_e=None):
            try:
                valor = float(ent.get().strip().replace(",", "."))
            except ValueError:
                escribir()
                return
            var.set(min(hi, max(lo, valor)))
            escribir()
            self.programar()

        esc = tk.Scale(padre, variable=var, from_=lo, to=hi, resolution=paso,
                       orient="horizontal", showvalue=0, length=160,
                       command=lambda _v: (escribir(), self.programar()))
        esc.grid(row=fila + 1, column=0, sticky="w")
        ent.bind("<Return>", desde_texto)
        ent.bind("<KP_Enter>", desde_texto)
        ent.bind("<FocusOut>", desde_texto)
        ent.escribir = escribir
        escribir()
        return fila + 2, esc, ent

    def _poner(self, clave, texto):
        e = self.ent[clave]
        estado = str(e.cget("state"))
        e.configure(state="normal")
        e.delete(0, "end")
        e.insert(0, texto)
        e.configure(state=estado)

    # ------------------------------------------------------------------
    def _todas_camaras(self):
        todas = dict(GENERICAS)
        todas.update(self.camaras)
        return todas

    def _refrescar_modelos(self):
        self.cb_modelo.configure(values=sorted(self._todas_camaras(),
                                               key=str.lower))

    def cargar_modelo(self, silencioso=False):
        nombre = self.modelo.get()
        datos = self._todas_camaras().get(nombre)
        if datos is None:
            return
        self.resolucion.set("%dx%d" % (datos["res_h"], datos["res_v"]))
        for clave in ("fov_h", "fov_v", "fps"):
            self._poner(clave, "%g" % datos[clave])
        if not silencioso:
            self.lbl_modelo.configure(text="Cargada '%s'." % nombre)
            self.programar()

    def leer_camara(self):
        res = leer_resolucion(self.resolucion.get())
        if res is None:
            return None, "Resolucion no valida."
        datos = dict(res_h=res[0], res_v=res[1])
        for clave in ("fov_h", "fov_v", "fps"):
            try:
                datos[clave] = float(self.ent[clave].get().replace(",", "."))
            except ValueError:
                return None, "Revisa el FOV y los fps."
        if not (0 < datos["fov_h"] < 180 and 0 < datos["fov_v"] < 180
                and datos["fps"] > 0):
            return None, "FOV entre 0 y 180 grados y fps mayores que cero."
        return datos, None

    def guardar_modelo(self):
        nombre = self.modelo.get().strip()
        if not nombre:
            self.lbl_modelo.configure(text="Escribe el nombre del modelo.")
            return
        datos, error = self.leer_camara()
        if error:
            self.lbl_modelo.configure(text=error)
            return
        previo = self.camaras.get(nombre)
        if previo is not None and previo != datos and not messagebox.askyesno(
                "Sobrescribir camara",
                "Ya existe '%s'. ¿Reemplazar sus datos?" % nombre):
            return
        camaras = dict(self.camaras)
        camaras[nombre] = datos
        try:
            guardar_camaras(camaras)
        except OSError as exc:
            self.lbl_modelo.configure(text="No se pudo guardar: %s" % exc)
            return
        self.camaras = camaras
        self._refrescar_modelos()
        self.lbl_modelo.configure(text="Guardada '%s'." % nombre)

    def eliminar_modelo(self):
        nombre = self.modelo.get().strip()
        if nombre not in self.camaras:
            self.lbl_modelo.configure(
                text="Las genericas no se eliminan." if nombre in GENERICAS
                else "No hay ninguna camara guardada con ese nombre.")
            return
        if not messagebox.askyesno("Eliminar camara",
                                   "¿Eliminar '%s'?" % nombre):
            return
        camaras = dict(self.camaras)
        del camaras[nombre]
        try:
            guardar_camaras(camaras)
        except OSError as exc:
            self.lbl_modelo.configure(text="No se pudo guardar: %s" % exc)
            return
        self.camaras = camaras
        self.modelo.set("")
        self._refrescar_modelos()
        self.lbl_modelo.configure(text="Eliminada '%s'." % nombre)

    # ------------------------------------------------------------------
    def leer(self):
        """Lee los controles. Devuelve (parametros, mensaje_de_error)."""
        p = {}
        for clave, etiqueta, _v, tipo in TODAS:
            texto = self.ent[clave].get().strip().replace(",", ".") or "0"
            try:
                p[clave] = tipo(float(texto))
            except ValueError:
                return None, "El campo '%s' no es un numero." % etiqueta
        res = leer_resolucion(self.resolucion.get())
        if res is None:
            return None, "Resolucion no valida: '%s'." % self.resolucion.get()
        p["res_h"], p["res_v"] = res
        p["h_mastil"] = self.h_mastil.get()
        p["b"] = p["ancho_bordes"] - 2.0 * p["m"] * p["hc"]
        p["zcam"] = p["hc"] + p["h_puente"] + p["h_mastil"]
        p.update(mira=self.mira.get(),
                 incl=self.incl.get(), giro=self.giro.get(),
                 auto_apuntar=self.auto_apuntar.get(),
                 auto_seccion=self.auto_seccion.get(),
                 auto_sx=self.auto_sx.get())

        if p["h_puente"] < 0:
            return None, "La altura del puente no puede ser negativa."
        if p["b"] <= 0:
            return None, ("Con ese talud la plantilla no tiene ancho: "
                          "%.2f - 2 x %.2f x %.2f = %.2f m."
                          % (p["ancho_bordes"], p["m"], p["hc"], p["b"]))
        for clave in ("fov_h", "fov_v", "fps", "ancho_bordes", "hc",
                      "tirante", "vmin",
                      "vmax", "largo", "xs", "trazador", "duracion",
                      "dtheta", "sx"):
            if p[clave] <= 0:
                etiqueta = next(e for c, e, _v, _t in TODAS if c == clave)
                return None, "'%s' debe ser mayor que cero." % etiqueta
        if p["fov_h"] >= 180 or p["fov_v"] >= 180:
            return None, "El FOV debe ser menor de 180 grados."
        if p["m"] < 0 or p["x_puente"] < 0:
            return None, "El talud y la distancia al puente no pueden ser" \
                         " negativos."
        if p["tirante"] > p["hc"]:
            return None, "El tirante no puede superar la altura de los bordes."
        if p["zcam"] <= p["hc"] + 0.05:
            return None, ("La camara debe quedar por encima de los bordes del"
                          " canal (%.2f m)." % p["hc"])
        if p["vmin"] >= p["vmax"]:
            return None, "La velocidad minima debe ser menor que la maxima."
        if not 1 <= p["n_lineas"] <= MAX_LINEAS:
            return None, "Entre 1 y %d lineas de busqueda." % MAX_LINEAS
        if p["paso"] < 1:
            return None, "El paso de imagenes k debe ser 1 o mas."
        if p["res_h"] * p["res_v"] > 50000000:
            return None, "Resolucion demasiado alta."
        return p, None

    def programar(self):
        if self._pendiente is not None:
            self.root.after_cancel(self._pendiente)
        self._pendiente = self.root.after(150, self.actualizar)

    def mensaje(self, texto):
        self.txt.delete("1.0", "end")
        self.txt.insert("1.0", texto)

    def actualizar(self):
        self._pendiente = None
        p, error = self.leer()
        if error:
            self.mensaje(error)
            return
        q, aviso = resolver(p)
        if p["auto_seccion"]:
            self._poner("xs", "%.2f" % q["xs"])
        self.ent["xs"].configure(state="disabled" if p["auto_seccion"]
                                 else "normal")
        if p["auto_apuntar"]:
            self.incl.set(round(q["incl"], 1))
            self.giro.set(round(q["giro"], 1))
        estado = "disabled" if p["auto_apuntar"] else "normal"
        for w in (self.esc_incl, self.ent_incl, self.esc_giro, self.ent_giro):
            w.configure(state=estado)
        self.ent_incl.escribir()
        self.ent_giro.escribir()

        a = analizar(q)
        if p["auto_sx"] and a["sx"] is not None:
            self._poner("sx", "%.2f" % (a["sx"] * 100))
        self.ent["sx"].configure(state="disabled" if p["auto_sx"]
                                 else "normal")
        self.pintar_lateral(q, a)
        self.pintar_planta(q, a)
        self.pintar_seccion(q, a)
        self.pintar_vista(q, a)
        self.pintar_stiv(q, a)
        self.pintar_lupa(q, a)
        self.mensaje(informe(q, a, aviso))

    def crear_imagen(self, datos_base64, nombre):
        try:
            return tk.PhotoImage(data=datos_base64)
        except tk.TclError:
            ruta = os.path.join(tempfile.gettempdir(), nombre)
            with open(ruta, "wb") as fh:
                fh.write(base64.b64decode(datos_base64))
            return tk.PhotoImage(file=ruta)

    # ------------------------------------------------------------------
    def _alcance_vista(self, q, a):
        """Distancia x hasta la que se dibujan perfil y planta."""
        x = q["xs"] + q["largo"] / 2.0
        lejos = a["cob"]["lejos"]
        if not math.isinf(lejos):
            x = max(x, min(lejos, 2.5 * x))
        return max(10.0, 1.2 * x)

    def pintar_lateral(self, q, a):
        """Perfil a lo largo del canal: fondo, agua, puente, camara, rayos
        de los bordes superior e inferior de la imagen y lineas de busqueda."""
        c = self.c_lateral
        c.delete("all")
        w, h = int(c["width"]), int(c["height"])
        cam = a["cam"]
        mg = 22
        x_min, x_max = -3.0, self._alcance_vista(q, a)
        hp = q.get("h_puente", 0.6)
        z_mano = q["hc"] + hp + ALTO_BARANDA
        z_max = max(q["zcam"], z_mano) * 1.2
        s = min((w - 2 * mg) / (x_max - x_min), (h - 2 * mg) / z_max)
        X = lambda x: mg + (x - x_min) * s
        Z = lambda z: h - mg - z * s
        d = q["tirante"]

        c.create_rectangle(X(x_min), Z(d), X(x_max), Z(0), fill=COLOR_AGUA,
                           outline="")
        c.create_line(X(x_min), Z(0), X(x_max), Z(0), fill="#666", width=2)
        c.create_line(X(x_min), Z(q["hc"]), X(x_max), Z(q["hc"]),
                      fill="#999", dash=(4, 3))
        c.create_text(X(x_max) - 2, Z(q["hc"]) - 7, anchor="e",
                      text="bordes", font=("TkDefaultFont", 7), fill="#777")
        # Pasarela en corte: una armadura a cada lado del piso, arriostradas
        # en X, y la baranda encima de cada armadura.
        z0, z1 = q["hc"], q["hc"] + hp
        xa, xb = -ANCHO_PISO, 0.0
        for x in (xa, xb):
            c.create_line(X(x), Z(z0), X(x), Z(z_mano), fill=COLOR_PUENTE,
                          width=3)
        c.create_line(X(xa), Z(z0), X(xb), Z(z1), fill=COLOR_PUENTE)
        c.create_line(X(xa), Z(z1), X(xb), Z(z0), fill=COLOR_PUENTE)
        c.create_line(X(xa), Z(z0), X(xb), Z(z0), fill=COLOR_PUENTE, width=2)
        c.create_rectangle(X(xa), Z(z1) - 3, X(xb), Z(z1), fill=COLOR_PISO,
                           outline=COLOR_PUENTE)
        for x in (xa, xb):
            c.create_oval(X(x) - 3, Z(z_mano) - 3, X(x) + 3, Z(z_mano) + 3,
                          fill=COLOR_PUENTE, outline="")
        c.create_line(X(0), Z(z1), X(0), Z(q["zcam"]), fill="#333", width=2)

        C = cam["C"]
        for v, color in ((0.0, "#aaa"), (cam["H"], "#aaa"),
                         (cam["H"] / 2.0, "#c86")):
            dd = rayo(cam, cam["W"] / 2.0, v)
            P = interseccion_agua(cam, dd, d)
            if P is None or P[0] > x_max:
                lh = math.hypot(dd[0], dd[1])
                t = (x_max - C[0]) / max(dd[0], 1e-9) if dd[0] > 0 else 0
                P = (C[0] + t * dd[0], 0, C[2] + t * dd[2]) if lh else None
            if P is not None:
                c.create_line(X(0), Z(q["zcam"]), X(P[0]), Z(P[2]),
                              fill=color, dash=() if color == "#c86"
                              else (3, 3))
        calif = peor(*(ln["calif"] for ln in a["lineas"]))
        x0, x1 = q["xs"] - q["largo"] / 2.0, q["xs"] + q["largo"] / 2.0
        c.create_line(X(x0), Z(d), X(x1), Z(d), fill=COLORES[calif], width=5)
        c.create_line(X(q["xs"]), Z(d) - 8, X(q["xs"]), Z(d) + 8, fill="#000")
        c.create_text(X(q["xs"]), Z(d) + 14, text="seccion %.1f m" % q["xs"],
                      font=("TkDefaultFont", 8))
        c.create_rectangle(X(0) - 6, Z(q["zcam"]) - 4, X(0) + 6,
                           Z(q["zcam"]) + 4, fill="#333", outline="")
        c.create_text(X(0) + 10, Z(q["zcam"]) - 2, anchor="w",
                      text="%.2f m sobre el agua, inclinacion %.1f grados"
                      % (q["zcam"] - d, q["incl"]),
                      font=("TkDefaultFont", 8))
        c.create_text(X(-ANCHO_PISO / 2), Z(z_mano) - 9, text="puente",
                      font=("TkDefaultFont", 7), fill=COLOR_PUENTE)

    def pintar_planta(self, q, a):
        """Planta (x hacia arriba): canal, puente, camara, huella del campo
        de vision sobre el agua, tramo con el ancho entero visible y lineas."""
        c = self.c_planta
        c.delete("all")
        w, h = int(c["width"]), int(c["height"])
        cam = a["cam"]
        T, B = anchos(q)
        mg = 14
        x_min, x_max = -3.0, self._alcance_vista(q, a)
        y_lim = max(B / 2.0 + 2.0, abs(q["ycam"]) + 1.0)
        s = min((w - 2 * mg) / (2 * y_lim), (h - 2 * mg) / (x_max - x_min))
        ox = w / 2.0
        Y = lambda y: ox + y * s
        X = lambda x: h - mg - (x - x_min) * s

        c.create_rectangle(0, 0, w, h, fill=COLOR_TERRENO, outline="")
        c.create_rectangle(Y(-B / 2), X(x_max + 50), Y(B / 2), X(0),
                           fill=COLOR_TALUD, outline="")
        c.create_rectangle(Y(-T / 2), X(x_max + 50), Y(T / 2), X(0),
                           fill=COLOR_AGUA, outline="")
        ya, yb = -B / 2 - APOYO_PUENTE, B / 2 + APOYO_PUENTE
        c.create_rectangle(Y(ya), X(0), Y(yb), X(-ANCHO_PISO),
                           fill=COLOR_PISO, outline="")
        for x in (0.0, -ANCHO_PISO):
            c.create_line(Y(ya), X(x), Y(yb), X(x), fill=COLOR_PUENTE,
                          width=2)
        m = max(1, int(round((yb - ya) / PASO_POSTE)))
        for i in range(m + 1):
            y = ya + (yb - ya) * i / m
            for x in (0.0, -ANCHO_PISO):
                c.create_rectangle(Y(y) - 1.5, X(x) - 1.5, Y(y) + 1.5,
                                   X(x) + 1.5, fill=COLOR_PUENTE, outline="")
        c.create_text(4, X(-ANCHO_PISO / 2), anchor="w", text="puente",
                      font=("TkDefaultFont", 7), fill=COLOR_PUENTE)

        paso = 5.0 if x_max <= 60 else (10.0 if x_max <= 150 else 25.0)
        k = 1
        while k * paso <= x_max:
            c.create_line(Y(-y_lim), X(k * paso), Y(-y_lim) + 6, X(k * paso),
                          fill="#555")
            c.create_text(Y(-y_lim) + 8, X(k * paso), anchor="w",
                          text="%g m" % (k * paso), font=("TkDefaultFont", 7),
                          fill="#555")
            k += 1

        pts = huella(cam, q["tirante"], (x_max - x_min) * 3.0)
        if len(pts) >= 3:
            c.create_polygon([coord for x, y in pts for coord in (Y(y), X(x))],
                             outline="#d07020", fill="", width=2, dash=(4, 2))

        iv = a["cob"]["agua_entera"]
        if iv is not None:
            hi = min(iv[1], x_max + 50)
            c.create_line(Y(y_lim) - 6, X(iv[0]), Y(y_lim) - 6, X(hi),
                          fill="#2a9d4b", width=4)
        for ln in a["lineas"]:
            c.create_line(Y(ln["y"]), X(ln["A"][0]), Y(ln["y"]), X(ln["B"][0]),
                          fill=COLORES[ln["calif"]], width=3)
        c.create_line(Y(-T / 2), X(q["xs"]), Y(T / 2), X(q["xs"]),
                      fill="#fff", dash=(3, 2))

        # Sentido del flujo.
        ya, xa = T / 2.0 - 0.6, min(x_max * 0.9, q["xs"] + q["largo"] + 3)
        dxa = -2.0 if q["mira"] == "aguas arriba" else 2.0
        c.create_line(Y(ya), X(xa), Y(ya), X(xa + dxa), arrow="last",
                      fill="#1b4f72", width=2)
        c.create_text(Y(ya) - 3, X(xa + dxa / 2), anchor="e", text="flujo",
                      font=("TkDefaultFont", 7), fill="#1b4f72")

        cy = cam["C"][1]
        c.create_oval(Y(cy) - 4, X(0) - 4, Y(cy) + 4, X(0) + 4, fill="#222",
                      outline="#fff")
        c.create_text(4, h - 7, anchor="w", font=("TkDefaultFont", 7),
                      fill="#444", text="naranja: campo de vision sobre el "
                                        "agua")
        c.create_text(w - 4, 8, anchor="e", font=("TkDefaultFont", 7),
                      fill="#2a9d4b", text="verde: ancho entero visible")

    def pintar_seccion(self, q, a):
        """Seccion transversal vista desde el puente: trapecio, agua,
        camara y tramo de agua visible en la seccion de medida."""
        c = self.c_seccion
        c.delete("all")
        w, h = int(c["width"]), int(c["height"])
        T, B = anchos(q)
        d, hc = q["tirante"], q["hc"]
        mg = 14
        y_lim = max(B / 2.0 + 1.5, abs(q["ycam"]) + 1.0)
        hp = q.get("h_puente", 0.6)
        z_max = max(q["zcam"], hc + hp + ALTO_BARANDA) * 1.08
        s = min((w - 2 * mg) / (2 * y_lim), (h - 2 * mg - 10) / (z_max + 0.3))
        Y = lambda y: w / 2.0 + y * s
        Z = lambda z: h - mg - 10 - z * s
        self.lbl_seccion.configure(text="Seccion a %.1f m, puente detras"
                                   % q["xs"])

        suelo = [(-y_lim, hc), (-B / 2, hc), (-q["b"] / 2, 0),
                 (q["b"] / 2, 0), (B / 2, hc), (y_lim, hc), (y_lim, -0.3),
                 (-y_lim, -0.3)]
        c.create_polygon([k for y, z in suelo for k in (Y(y), Z(z))],
                         fill="#d8d2c4", outline="#777")
        c.create_polygon(Y(-T / 2), Z(d), Y(T / 2), Z(d), Y(q["b"] / 2), Z(0),
                         Y(-q["b"] / 2), Z(0), fill=COLOR_AGUA, outline="")
        cy, cz = q["ycam"], q["zcam"]
        dibujar_pasarela(c, Y, Z, -B / 2 - APOYO_PUENTE, B / 2 + APOYO_PUENTE,
                         hc, hp, camara=(cy, cz))
        ys = a["cob"]["y_seccion"]
        if ys is not None:
            for y in (max(ys[0], -y_lim), min(ys[1], y_lim)):
                c.create_line(Y(cy), Z(cz), Y(y), Z(cota_superficie(q, y)),
                              fill="#aaa", dash=(3, 3))
            lo, hi = max(ys[0], -T / 2), min(ys[1], T / 2)
            if lo < hi:
                c.create_line(Y(lo), Z(d), Y(hi), Z(d), fill="#2a9d4b",
                              width=4)
        for y0, y1 in ((-T / 2, ys[0] if ys else T / 2),
                       (ys[1] if ys else T / 2, T / 2)):
            if y1 > y0 + 1e-6:
                c.create_line(Y(y0), Z(d), Y(min(y1, T / 2)), Z(d),
                              fill="#d64545", width=4)
        for ln in a["lineas"]:
            c.create_oval(Y(ln["y"]) - 3, Z(d) - 3, Y(ln["y"]) + 3,
                          Z(d) + 3, fill=COLORES[ln["calif"]], outline="")
        c.create_text(4, h - 8, anchor="w", font=("TkDefaultFont", 7),
                      fill="#444", text="verde: agua visible  rojo: fuera  "
                                        "T = %.2f m" % T)

    def pintar_vista(self, q, a):
        """Imagen simulada con las guias: distancias, orillas, bordes,
        seccion, lineas de busqueda y zona de la lupa."""
        c = self.c_vista
        c.delete("all")
        cam = a["cam"]
        W, H = cam["W"], cam["H"]
        Wd, Hd = tam_vista(W, H, ANCHO_VISTA, ALTO_VISTA)
        datos, Wd, Hd = simular(q, cam, a["segs"], (Wd, Hd))
        img = self.crear_imagen(datos, "stiv_vista.png")
        self._img = img
        ex, ey = Wd / float(W), Hd / float(H)
        ox, oy = (ANCHO_VISTA - Wd) // 2, (ALTO_VISTA - Hd) // 2
        U = lambda u: ox + u * ex
        V = lambda v: oy + v * ey
        c.create_rectangle(0, 0, ANCHO_VISTA + 2, ALTO_VISTA + 2,
                           fill="#202020", outline="")
        c.create_image(ox, oy, anchor="nw", image=img)
        self.lbl_vista.configure(text="Lo que ve la camara  (%d x %d px,"
                                      " escala x%.2f)" % (W, H, ex))
        if not self.guias.get():
            return

        def linea(P0, P1, **kw):
            for tramo in tramos_en_imagen(cam, P0, P1):
                c.create_line([k for u, v in tramo for k in (U(u), V(v))],
                              **kw)

        T, B = anchos(q)
        d = q["tirante"]
        x_far = 1.5 * self._alcance_vista(q, a) + 50
        for y in (-T / 2, T / 2):
            linea((0, y, d), (x_far, y, d), fill="#7fd4ff", dash=(4, 3))
        for y in (-B / 2, B / 2):
            linea((0, y, q["hc"]), (x_far, y, q["hc"]), fill="#e0e0e0",
                  dash=(2, 3))
        paso = 5.0 if x_far <= 120 else 10.0
        k = 1
        while k * paso < x_far:
            x = k * paso
            tr = tramos_en_imagen(cam, (x, -T / 2, d), (x, T / 2, d), n=12)
            for tramo in tr:
                c.create_line([kk for u, v in tramo for kk in (U(u), V(v))],
                              fill="#cccccc")
            if tr:
                u, v = tr[-1][-1]
                c.create_text(U(u) + 3, V(v), anchor="w", text="%g m" % x,
                              fill="#eeeeee", font=("TkDefaultFont", 7))
            k += 1
        linea((q["xs"], -T / 2, d), (q["xs"], T / 2, d), fill="#ffffff",
              width=1, dash=(6, 3))
        for ln in a["lineas"]:
            linea(ln["A"], ln["B"], fill=COLORES[ln["calif"]], width=3)
            if ln["uvB"] is not None and en_imagen(cam, ln["uvB"]):
                c.create_text(U(ln["uvB"][0]), V(ln["uvB"][1]) - 8,
                              text="L%d" % ln["n"],
                              fill=COLORES[ln["calif"]],
                              font=("TkDefaultFont", 8, "bold"))
        if a["peor"] is not None:
            uv = proyectar(cam, a["peor"][1])
            if en_imagen(cam, uv):
                u0 = min(max(uv[0] - LUPA_NW / 2.0, 0), W - LUPA_NW)
                v0 = min(max(uv[1] - LUPA_NH / 2.0, 0), H - LUPA_NH)
                c.create_rectangle(U(u0), V(v0), U(u0 + LUPA_NW),
                                   V(v0 + LUPA_NH), outline="#ffd400")

    def pintar_stiv(self, q, a):
        """Resumen STIV: resolucion en la linea central y angulos de la STI
        por linea para las velocidades extremas."""
        c = self.c_stiv
        c.delete("all")
        validas = [ln for ln in a["lineas"] if ln["vel"]]
        y = 12
        txt = lambda yy, t, **kw: c.create_text(
            8, yy, anchor="w", text=t, **dict(dict(font=("TkFixedFont", 8)),
                                              **kw))
        if not validas:
            txt(y, "Ninguna linea delante de la camara.")
            return
        centro = validas[len(validas) // 2]
        txt(y, "L%d (centro), a lo largo del flujo" % centro["n"],
            font=("TkDefaultFont", 8), fill="#666")
        y += 20
        txt(y, "%.2f cm/px" % (centro["g"] * 100),
            font=("TkDefaultFont", 14, "bold"), fill="#0a7")
        y += 20
        txt(y, "nativo; a lo ancho %.2f cm/px" % (centro["gy"] * 100),
            font=("TkDefaultFont", 8), fill="#666")
        y += 16
        txt(y, "STI: S_x %.2f cm/px, %d px por linea"
            % (a["sx"] * 100, q["largo"] / a["sx"]),
            font=("TkDefaultFont", 8), fill="#666")
        y += 14
        txt(y, "%g fps, k = %d: %.3f s entre imagenes"
            % (q["fps"], q["paso"], q["paso"] / q["fps"]),
            font=("TkDefaultFont", 8), fill="#666")
        y += 14
        c.create_line(8, y, ANCHO_LADO - 8, y, fill="#ccc")
        y += 12
        txt(y, "Angulo STI (grados)", font=("TkDefaultFont", 8, "bold"))
        y += 15
        txt(y, "    nativo  %4.2fm/s  %4.2fm/s" % (q["vmin"], q["vmax"]),
            fill="#666")
        y += 14
        for ln in a["lineas"]:
            if not ln["vel"]:
                txt(y, "L%-2d detras de la camara" % ln["n"])
            else:
                txt(y, "L%-2d %6.2f" % (ln["n"], ln["g"] * 100))
                # Cada angulo con el color de su calificacion.
                for i, r in enumerate(ln["vel"]):
                    c.create_text(118 + 62 * i, y, anchor="e",
                                  text="%.1f" % r["th"],
                                  fill=COLORES[r["calif"]],
                                  font=("TkFixedFont", 8, "bold"))
                c.create_rectangle(ANCHO_LADO - 16, y - 4, ANCHO_LADO - 8,
                                   y + 4, fill=COLORES[ln["calif"]],
                                   outline="")
            y += 14
        y += 4
        fmin = fps_minimos(q, a["sx"])
        txt(y, "fps minimos para %.2f m/s: %.0f" % (q["vmax"], fmin),
            fill="#d64545" if fmin > q["fps"] else "#2a9d4b",
            font=("TkDefaultFont", 8))
        y += 14
        if not a["ok"]:
            for m in a["motivos"]:
                c.create_text(8, y, anchor="nw", text="! " + m,
                              width=ANCHO_LADO - 16, fill="#d64545",
                              font=("TkDefaultFont", 7))
                y += 24
        c.configure(height=max(240, y + 10))

    def pintar_lupa(self, q, a):
        """Recorte a la resolucion real del sensor en el peor punto: el
        extremo de linea con mas centimetros por pixel."""
        c = self.c_lupa
        c.delete("all")
        if a["peor"] is None:
            return
        cam = a["cam"]
        ln, P = a["peor"]
        uv = proyectar(cam, P)
        if uv is None:
            return
        datos, u0, v0 = lupa(q, cam, a["segs"], uv, LUPA_NW, LUPA_NH,
                             LUPA_AUMENTO)
        img = self.crear_imagen(datos, "stiv_lupa.png")
        self._img_lupa = img
        ox, oy = (ANCHO_LADO - LUPA_NW * LUPA_AUMENTO) // 2, 6
        c.create_image(ox, oy, anchor="nw", image=img)
        U = lambda u: ox + (u - u0) * LUPA_AUMENTO
        V = lambda v: oy + (v - v0) * LUPA_AUMENTO
        uvA, uvB = ln["uvA"], ln["uvB"]
        if uvA is not None and uvB is not None:
            c.create_line(U(uvA[0]), V(uvA[1]), U(uvB[0]), V(uvB[1]),
                          fill=COLORES[ln["calif"]], width=1)
        self.lbl_lupa.configure(text="Lupa x%d: extremo lejano de L%d"
                                     % (LUPA_AUMENTO, ln["n"]))
        y = oy + LUPA_NH * LUPA_AUMENTO + 14
        gx, gy = gsd(cam, P, 0), gsd(cam, P, 1)
        for t in ("%d x %d pixeles del sensor" % (LUPA_NW, LUPA_NH),
                  "1 px = %.2f cm (flujo) x %.2f cm (ancho)"
                  % (gx * 100, gy * 100),
                  "trazador de %g cm = %.1f px" % (q["trazador"],
                                                   ln["traz_px"])):
            c.create_text(8, y, anchor="w", text=t, font=("TkDefaultFont", 8))
            y += 15


# =============================================================================
# 10. AUTOCOMPROBACION
# =============================================================================

def caso_base(**cambios):
    p = dict(res_h=1920, res_v=1080, fov_h=48.3, fov_v=28.3, fps=25.0,
             b=4.0, m=1.5, hc=2.5, tirante=1.0, zcam=5.2, ycam=0.0,
             x_puente=2.0, mira="aguas arriba", incl=25.0, giro=0.0,
             auto_apuntar=True, auto_seccion=True, vmin=0.1, vmax=2.0,
             n_lineas=5, largo=3.0, xs=10.0, paso=1, trazador=5.0,
             duracion=10.0, dtheta=1.0, sx=1.0, auto_sx=True)
    p.update(cambios)
    return p


def caso_sitio(**cambios):
    """Canal y puente de Medidas.pdf con la Hikvision DS-2CD3646G2T-IZS a
    2.7 mm, como en los valores iniciales de la interfaz."""
    cam = GENERICAS[CAMARA_INICIAL]
    p = caso_base(res_h=cam["res_h"], res_v=cam["res_v"], fov_h=cam["fov_h"],
                  fov_v=cam["fov_v"], fps=cam["fps"], m=1.5, hc=3.0,
                  tirante=2.0, h_puente=0.85, h_mastil=1.0, ancho_bordes=11.4)
    p.update(cambios)
    p["b"] = p["ancho_bordes"] - 2.0 * p["m"] * p["hc"]
    p["zcam"] = p["hc"] + p["h_puente"] + p["h_mastil"]
    return p


def autocomprobacion():
    """Verifica las formulas y el codificador PNG. Se ejecuta con --test y
    no necesita tkinter."""
    fallos = 0

    def check(nombre, ok, detalle=""):
        nonlocal fallos
        print("%-54s %s %s" % (nombre, "OK" if ok else "FALLO", detalle))
        if not ok:
            fallos += 1

    casos = [caso_base(incl=25.0, giro=0.0),
             caso_base(incl=40.0, giro=12.0, ycam=-3.0, zcam=8.0),
             caso_base(incl=10.0, giro=-20.0, ycam=6.0, zcam=12.0,
                       res_h=3840, res_v=2160, fov_h=87.7, fov_v=56.7),
             caso_base(incl=89.0, giro=5.0, zcam=4.0)]

    # (F2) ejes ortonormales.
    peor_v = 0.0
    for p in casos:
        cam = camara(p)
        f, r, up = cam["f"], cam["r"], cam["up"]
        for a_, b_ in ((f, r), (f, up), (r, up)):
            peor_v = max(peor_v, abs(_punto(a_, b_)))
        for a_ in (f, r, up):
            peor_v = max(peor_v, abs(_punto(a_, a_) - 1.0))
    check("F2 ejes de la camara ortonormales", peor_v < 1e-12,
          "error max %.1e" % peor_v)

    # (F3)/(F4) proyectar un punto del agua y volver a cortar su rayo con
    # el plano del agua devuelve el mismo punto.
    peor_v = 0.0
    for p in casos:
        cam = camara(p)
        for P in ((6.0, 0.5, 1.0), (15.0, -2.0, 1.0), (9.0, 3.0, 1.0)):
            uv = proyectar(cam, P)
            Q = interseccion_agua(cam, rayo(cam, *uv), P[2])
            peor_v = max(peor_v, max(abs(Q[k] - P[k]) for k in range(3)))
    check("F3/F4 proyeccion y rayo son reciprocos", peor_v < 1e-9,
          "error max %.1e m" % peor_v)

    # (F6) GSD analitico = diferencia finita.
    peor_v = 0.0
    for p in casos:
        cam = camara(p)
        for P in ((6.0, 0.5, 1.0), (20.0, -2.0, 1.0)):
            for eje in (0, 1):
                h = 1e-4
                P1 = list(P)
                P2 = list(P)
                P1[eje] -= h
                P2[eje] += h
                a_, b_ = proyectar(cam, P1), proyectar(cam, P2)
                num = 2 * h / math.hypot(b_[0] - a_[0], b_[1] - a_[1])
                peor_v = max(peor_v, abs(gsd(cam, P, eje) - num) / num * 100)
    check("F6 GSD analitico = diferencia finita", peor_v < 1e-4,
          "error max %.1e %%" % peor_v)

    # (F7) la formula cerrada coincide con F6 en el plano del eje.
    p = caso_base(incl=30.0, giro=0.0, ycam=0.0)
    cam = camara(p)
    peor_v = 0.0
    for x in (3.0, 8.0, 20.0, 50.0):
        gx, gy = gsd_plano_eje(p, x)
        P = (x, 0.0, p["tirante"])
        peor_v = max(peor_v, abs(gx - gsd(cam, P, 0)) / gx,
                     abs(gy - gsd(cam, P, 1)) / gy)
    check("F7 formula cerrada en el plano del eje = F6", peor_v < 1e-9,
          "error max %.1e" % peor_v)

    # (F7) en cenital: GSD = H_w / k.
    p = caso_base(incl=90.0, giro=0.0, ycam=0.0)
    cam = camara(p)
    Hw = p["zcam"] - p["tirante"]
    P = (1e-9, 0.0, p["tirante"])
    ok = (abs(gsd(cam, P, 0) - Hw / cam["k_v"]) < 1e-9 and
          abs(gsd(cam, P, 1) - Hw / cam["k_h"]) < 1e-9)
    check("F7 cenital: GSD = H_w / k", ok,
          "%.3f cm/px" % (100 * Hw / cam["k_v"]))

    # (F5) un rayo vertical sobre el agua corta a la altura del tirante; y
    # una camara baja fuera del canal no ve la orilla cercana tapada por el
    # talud, pero si la lejana.
    p = caso_base(incl=90.0, giro=0.0)
    cam = camara(p)
    segs = segmentos(p)
    imp = primer_impacto(0.0, p["zcam"], 0.0, -1.0, segs)
    ok = imp is not None and imp[1] == AGUA and \
        abs(imp[0] - (p["zcam"] - p["tirante"])) < 1e-12
    T, B = anchos(p)
    q = caso_base(ycam=B / 2 + 3.0, zcam=4.0, auto_apuntar=False, incl=20.0,
                  giro=-30.0)
    camq, segq = camara(q), segmentos(q)
    ok = ok and not es_visible(camq, segq, (5.0, T / 2, q["tirante"])) \
        and es_visible(camq, segq, (5.0, -T / 2, q["tirante"]))
    check("F5 corte con la seccion y ocultacion por el talud", ok)

    # (F12) los extremos del intervalo caen en el borde de la imagen.
    peor_v = 0.0
    for p in casos:
        cam = camara(p)
        T = anchos(p)[0]
        for y in (-T / 2, T / 2):
            iv = intervalo(cam, (0.0, y, p["tirante"]), (1.0, 0.0, 0.0),
                           0.0, LEJOS)
            if iv is None:
                continue
            for x in iv:
                if x <= 0.0 or x >= LEJOS * 0.99:
                    continue
                u, v = proyectar(cam, (x, y, p["tirante"]))
                peor_v = max(peor_v, min(abs(u), abs(u - cam["W"]), abs(v),
                                         abs(v - cam["H"])))
    check("F12 intervalo exacto: extremos en el borde", peor_v < 1e-6,
          "error max %.1e px" % peor_v)

    # (F13) el apuntado automatico lleva el centro de la seccion al centro
    # de la imagen.
    peor_v = 0.0
    for p in casos:
        q = orientar(dict(p, auto_apuntar=True), 12.0)
        cam = camara(q)
        u, v = proyectar(cam, (12.0, 0.0, q["tirante"]))
        peor_v = max(peor_v, abs(u - cam["W"] / 2), abs(v - cam["H"] / 2))
    check("F13 apuntado al centro de la seccion", peor_v < 1e-9,
          "error max %.1e px" % peor_v)

    # (F9)/(F10) 1 px por imagen = 45 grados con error minimo.
    desp, th = angulo_sti(0.5, 0.02, 25.0, 1)
    errs = [error_velocidad(t, 1.0) for t in (20.0, 45.0, 70.0)]
    check("F9/F10 45 grados con 1 px/imagen y error minimo",
          abs(desp - 1.0) < 1e-12 and abs(th - 45.0) < 1e-9
          and errs[1] < errs[0] and errs[1] < errs[2]
          and abs(errs[0] - errs[2]) < 1e-9,
          "dU/U a 45 = %.2f %%" % errs[1])

    # (F11) con k* la velocidad queda a 45 grados; con fps_min, a 70.
    g = 0.013
    k = 25.0 * g / 0.1
    ok = abs(angulo_sti(0.1, g, 25.0, k)[1] - 45.0) < 1e-9
    fmin = 2.0 / (g * math.tan(math.radians(70.0)))
    ok = ok and abs(angulo_sti(2.0, g, fmin, 1)[1] - 70.0) < 1e-9
    check("F11 paso k* y fps minimos", ok, "k* = %.2f, fps = %.1f" % (k, fmin))

    # La seccion automatica es el umbral: cabe en ella y no un poco antes.
    p = caso_base(zcam=4.0, fov_h=30.0, fov_v=17.0)
    xs = seccion_auto(p)
    ok = xs is not None and cabe_seccion(orientar(p, xs))[0] and \
        not cabe_seccion(orientar(p, xs - 0.02))[0]
    check("seccion automatica es el umbral", ok,
          "%.2f m" % (xs if xs else float("nan")))

    # Las camaras incluidas son coherentes (pixel cuadrado) y la ficha de la
    # Hikvision no lo es.
    ok = all(incoherencia_fov(c) < 0.01 for c in GENERICAS.values())
    ficha = dict(res_h=2688, res_v=1520, fov_h=114.6, fov_v=62.3)
    check("FOV incluidos coherentes; el de la ficha no",
          ok and incoherencia_fov(ficha) > 0.4,
          "ficha %.0f %%" % (100 * incoherencia_fov(ficha)))

    # Analisis completo del caso base sin errores.
    q, aviso = resolver(caso_base())
    a = analizar(q)
    texto = informe(q, a, aviso)
    check("analisis e informe del caso base",
          a["ok"] and all(ln["dentro"] for ln in a["lineas"])
          and "VEREDICTO" in texto, "seccion a %.2f m" % q["xs"])

    # (F9) S_x automatico = peor GSD nativo; S_x = 8 cm/px a 25 fps deja
    # 2 m/s a 45 grados en todas las lineas.
    ok = abs(a["sx"] - max(ln["gx_max"] for ln in a["lineas"])) < 1e-15
    a8 = analizar(dict(q, auto_sx=False, sx=8.0))
    ok = ok and all(abs(ln["vel"][1]["th"] - 45.0) < 1e-9
                    for ln in a8["lineas"])
    check("F9 S_x automatico y elegido", ok,
          "S_x auto = %.2f cm/px" % (a["sx"] * 100))

    # Caso real (Medidas.pdf y la Hikvision a 2.7 mm): la plantilla sale de
    # los 11.4 m entre bordes y con cualquier tirante hasta el maximo cabe
    # una seccion con el ancho de agua entero.
    ok = True
    for tir in (0.5, 1.5, 2.0, 2.8):
        p = caso_sitio(tirante=tir)
        qs, avs = resolver(p)
        a_s = analizar(qs)
        ok = ok and avs is None and a_s["ok"] and a_s["cob"]["orillas_ok"]
    check("caso real: canal de 11.4 m entero con la Hikvision",
          ok and abs(anchos(caso_sitio())[1] - 11.4) < 1e-9,
          "plantilla %.2f m" % caso_sitio()["b"])

    # PNG con firma y CRC correctos.
    png = png_bytes(4, 2, bytes(range(24)), 3)
    ok = png.startswith(b"\x89PNG\r\n\x1a\n")
    i, bloques = 8, []
    while i < len(png) and ok:
        ln_ = struct.unpack(">I", png[i:i + 4])[0]
        tipo = png[i + 4:i + 8]
        datos = png[i + 8:i + 8 + ln_]
        crc = struct.unpack(">I", png[i + 8 + ln_:i + 12 + ln_])[0]
        ok = ok and crc == zlib.crc32(tipo + datos) & 0xFFFFFFFF
        bloques.append(tipo.decode())
        i += 12 + ln_
    check("PNG con firma y CRC correctos",
          ok and bloques == ["IHDR", "IDAT", "IEND"], "bloques %s" % bloques)

    # La imagen simulada tiene el tamano pedido y agua en el centro.
    cam = a["cam"]
    datos, Wd, Hd = simular(q, cam, a["segs"], (96, 54))
    crudo = base64.b64decode(datos)
    rgb = trazar(q, cam, a["segs"], [cam["W"] / 2.0], [cam["H"] / 2.0])
    check("simular(): PNG del tamano pedido y agua en el centro",
          struct.unpack(">II", crudo[16:24]) == (96, 54)
          and rgb[2] > rgb[0], "centro RGB %s" % list(rgb))

    # Reescalado RGB por bloques.
    img = bytes(range(18))                      # 3 x 2 RGB
    out = reescalar_rgb(img, 3, 2, 6, 2)
    check("reescalado RGB por vecino mas proximo",
          out[:6] == img[:3] * 2 and len(out) == 36)

    # Camaras: guardar, leer y fichero danado.
    ruta = os.path.join(tempfile.gettempdir(), "stiv_camaras_test.json")
    camaras = {"Modelo Ñ-1": dict(res_h=1920, res_v=1080, fov_h=48.3,
                                  fov_v=28.3, fps=30.0)}
    guardar_camaras(camaras, ruta)
    ok = cargar_camaras(ruta) == camaras
    with open(ruta, "w", encoding="utf-8") as fh:
        fh.write("{no es json")
    ok = ok and cargar_camaras(ruta) == {}
    os.remove(ruta)
    check("camaras: guardar, leer y fichero danado", ok)

    print("\n%d fallo(s)." % fallos)
    return 0 if fallos == 0 else 1


# =============================================================================

def main():
    if "--test" in sys.argv:
        sys.exit(autocomprobacion())
    if not HAY_TK:
        print("Falta tkinter. En Windows viene con el instalador oficial de")
        print("Python; en Debian/Ubuntu: sudo apt install python3-tk")
        print("Mientras tanto puedes verificar las formulas con:  --test")
        sys.exit(1)
    raiz = tk.Tk()
    App(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()
