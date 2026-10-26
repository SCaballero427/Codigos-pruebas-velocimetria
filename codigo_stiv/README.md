# Codigo STIV: version inicial y version completa

Dos modulos de Python con el metodo STIV propio (solo numpy y OpenCV, sin pyorc):

| Archivo | Que es |
|---|---|
| `stiv_inicial.py` | El STIV tal como nacio en la prueba 3 (Sile Main Canal, julio): video cenital, escala conocida, una linea de 1 px por vertical, control de calidad solo por coherencia, relleno junto a muros y caudal. |
| `stiv_completo.py` | El mismo metodo con todas las mejoras de julio y agosto (pruebas 4 a 8), cada una opcional. Con las opciones apagadas y `derivadas="sobel"` da exactamente lo mismo que la version inicial. |
| `validar.py` | Reproduce con los dos modulos los resultados de las pruebas 3, 5, 6, 7 y 8 y los compara con los de sus notebooks. |

Salen de los notebooks de `evolucion_algoritmo_velocimetria/` (v3 a v8): el codigo es el mismo, solo
que ordenado como modulo reutilizable en vez de repartido en celdas.

## Que anade la version completa

| Version | Mejora | Tipo |
|---|---|---|
| v4 | Correccion de perspectiva de cada fotograma antes de leer las lineas | general |
| v4 | Lineas con centro, angulo y largo propios (`mapa_lineas`) | general |
| v4 | Velocidad aproximada medida por correlacion de fase (`velocidad_esperada`) | general |
| v4 | Suavizado opcional antes de medir la inclinacion (`sigma_derivada = 0`) | general |
| v4 | Regla de cambio con el tiempo contra muros y objetos quietos (`contraste_min`) | general |
| v5 | Posicion de la camara con puntos medidos y la lente (`pose_camara`) | general |
| v5 | Mapa pixel a pixel de la vista desde arriba, con la lente (`mapa_plano`) | general |
| v5 | Relleno en orillas en rampa ademas de muros (`rellenar(..., "rampa")`) y caudal | general |
| v6 | Banda de lineas paralelas por punto, igualadas y promediadas (`mapa_banda`) | general |
| v6 | Reglas de calidad que se apagan con `None` (`control_calidad`) | general |
| v7 | Un angulo por punto y lineas que se salen de la imagen (`cobertura`, `valido`) | general |
| v7 | Todo el proceso en una funcion para varios videos (`medir_video`) | general |
| v7 | Curva de decorrelacion: si el agua tiene algo que seguir (`curva_decorrelacion`) | comprobacion |
| v8 | Solo votan los trozos con algo flotando (`cuantil_senal`) | general |
| v6 | Brillo maximo del agua (`brillo_max_agua`) | ajuste del video |
| v8 | Filtro de restos flotantes contra la compresion (`realce_tophat`) | ajuste del video |
| v8 | Compensacion del movimiento de la camara, aplicada al mapa (`Estabilizador`) | ajuste del video |
| v8 | Restos que pasan por cada punto (`densidad_min`, `densidad_max`) | ajuste del video |
| v4, v8 | Perspectiva sin medidas: punto de fuga, focal supuesta (`orillas_punto_fuga`, `homografia_horizonte`) | ajuste sin datos del lugar |

Unica diferencia de calculo con la version inicial: por defecto las derivadas del tensor son
diferencias centrales (v4) en lugar de Sobel. No dan exactamente lo mismo: en el Sile Main Canal el
caudal pasa de 1.4484 a 1.4672 m3/s (+1.3 %; aforo 1.4362 m3/s, margen 4.2 %), con las mismas 9
verticales medidas. `Configuracion(derivadas="sobel")` vuelve al calculo de la version inicial.

## Uso

```python
import stiv_completo as st

# lineas: una banda de 7 lineas por punto, en px del plano (o de la imagen si es cenital)
mapx, mapy, nb = st.mapa_banda(centros, angulos, ds, largo, ancho_banda, 7)
cfg = st.Configuracion(ds=ds, escala=m_por_px, dt=1 / fps, n_frames=600, brillo_max_agua=None)
r = st.medir_video(video, mapx, mapy, nb, cfg, mapa_rect=mapa)   # mapa = None si es cenital
medida, motivos = st.control_calidad(r, cfg, es_contorno=prof == 0)
v_eff = st.rellenar(s, r["v"], medida, prof == 0, "rampa")
q, q_por_vertical = st.caudal(s, v_eff, prof, alfa=0.85)
```

`validar.py` tiene un ejemplo completo por cada tipo de camara: cenital con escala conocida (Sile),
inclinada con puntos de control y lente (Hommerich), video ya rectificado (Bradano, Arrow) y movil sin
ninguna medida (canal Yaqui).

## Validacion

`python validar.py` (desde esta carpeta, con el entorno de `requirements_pyorc.txt`). Las pruebas 5 a
7 necesitan los datasets externos (`datos/externos/LEEME.md`).

| Prueba | Valor | stiv_completo | Notebook |
|---|---|---|---|
| 3, Sile (stiv_inicial) | caudal; verticales medidas | 1.4484 m3/s; 9 de 11 | 1.4484 m3/s; 9 de 11 |
| 3, Sile (derivadas sobel) | caudal; verticales medidas | 1.4484 m3/s; 9 de 11 | 1.4484 m3/s; 9 de 11 |
| 3, Sile (derivadas centrales) | caudal | 1.4672 m3/s | (no hay notebook: v4 en adelante) |
| 5, Hommerich | caudal; verticales medidas | 12.922 m3/s; 12 de 16 | 12.922 m3/s; 12 de 16 |
| 6, Bradano | puntos medidos; velocidad | 1 a 5; 0.7428 m/s | 1 a 5; 0.7428 m/s |
| 7, Arrow | sin sembrar; sembrado | 0 de 49; 38 de 49, 0.3978 m/s | 0 de 49; 38 de 49, 0.3978 m/s |
| 7, Arrow | curva de decorrelacion, sembrado | 0.725 0.559 0.337 0.154 | 0.725 0.559 0.337 0.154 |
| 8, canal Yaqui | puntos medidos; velocidad | 8 a 13; 0.0571 alt. camara/s | 8 a 13; 0.0571 alt. camara/s |
| 8, canal Yaqui | punto de fuga; movimiento del movil | (519.0, -53.1); 6.70 px | (519.0, -53.1); 6.70 px |

Tiempos en el ordenador del proyecto: Sile 1.5 a 2.5 min por version (video 4K), canal Yaqui unos 2
min, el resto menos de 1 min.
