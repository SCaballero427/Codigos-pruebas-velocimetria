# 06 · Rio Bradano (HARMONIOUS) -- STIV sobre video ya ortorrectificado

**Que es.** Video de dron que el dataset entrega ya ortorrectificado, estabilizado y con su escala
declarada (0.009 m/px). Sin geometria que resolver, queda solo el metodo frente a una dificultad: el
trazador es escaso (particulas sueltas sobre agua casi negra).

| | |
|---|---|
| Metodo | STIV propio, con una **banda de 7 lineas** por estacion en vez de una |
| Video | 1920x1080, 24 fps, 600 fotogramas (25 s) |
| Resultado | **5 de 7 verticales medidas**, sesgo -3.1 %, RMSE 0.068 m/s, r = +0.996 |
| Referencia | velocidades publicadas por HARMONIOUS (solo se abren en la parte 7) |

**Datos.** Necesita `datos/externos/datasets vision velocimetria/data/RiverBradano/` (ver
`datos/externos/LEEME.md`).

**Como ejecutarlo.** Desde esta carpeta, con el entorno de `requirements_pyorc.txt`:
- `Bradano_STIV_pipeline.ipynb` -- el caso completo (~65 s).
- `python video_velocidad.py` -- video a tiempo real (~3.5 min).

**A tener en cuenta.**
- Las figuras y el video **estiran el contraste a proposito**: el agua tiene un brillo medio de
  0.12/255. Una figura nueva sin ese estiramiento sale negra, y no es un error de los datos.
- Aqui el control de calidad es el **brillo**, no el contraste temporal de Boneyard: la orilla de
  grava tiene mas contraste que el agua.
- Las 2 verticales que fallan son las pegadas a las orillas, en sombra y sin particulas.
- Sin batimetria no hay caudal, y las estaciones rechazadas no se rellenan.
