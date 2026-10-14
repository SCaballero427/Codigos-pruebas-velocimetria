# 04 · Boneyard Creek (USGS) -- STIV con camara oblicua y sin geometria

**Que es.** Una camara IP fija y oblicua de la que el dataset no publica **nada**: ni puntos de
control, ni ancho, ni seccion. Aun asi se mide la velocidad, en una unidad relativa (alturas de
camara por segundo), gracias a un resultado geometrico: rectificando con el horizonte del agua, la
velocidad queda bien salvo una sola constante global. **No llega a caudal, y ese es el resultado.**

| | |
|---|---|
| Metodo | STIV propio, rectificacion por punto de fuga |
| Video | 61 videos del USGS (doi:10.5066/P9VZ6VYM); se mide el de mayor caudal diurno |
| Resultado | **v = 0.2427 alturas de camara/s** (q05-q95 0.2244-0.2685), 15 de 21 estaciones |
| Referencia | Q = 368 cfs del USGS, **no** usado para ajustar nada |

**Datos.** Necesita `datos/externos/datasets vision velocimetria/Boneyardcreek/` (ver
`datos/externos/LEEME.md`).

**Como ejecutarlo.** Desde esta carpeta, con el entorno de `requirements_pyorc.txt`:
- `Boneyard_STIV_pipeline.ipynb` -- el caso completo (partes 0-8). Explicado en `GUIA_DEL_NOTEBOOK.md`.
- `python video_velocidad.py` -- video a tiempo real con las dos vistas (original y rectificada).
- `python stiv_interactivo.py` -- la misma medida con la geometria puesta **a mano** (se arrastra un
  cuadrilatero); da m/s suponiendo dimensiones reales.
- `velocidad_nivel*.py`, `velocidad_sin_nivel.py` -- variantes con el nivel del agua.

**La leccion del caso.** Las paredes devuelven coherencia alta con velocidad exactamente 0 (una
estructura quieta es una estria perfecta). Por eso el control de calidad es el **contraste temporal**,
no la coherencia. 11 de los 61 videos son nocturnos (infrarrojo) e inservibles.
