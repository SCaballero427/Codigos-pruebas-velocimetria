# 03 · Sile Main Canal (USGS) -- STIV desde cero, mismo video que 02

**Que es.** El mismo video y la misma configuracion que `02_smc_pyorc`, pero midiendo con **STIV
programado desde cero sobre OpenCV** (pyorc no se importa). Es la comparacion controlada entre metodos.

| | |
|---|---|
| Metodo | STIV: imagen espacio-tiempo + tensor de estructura |
| Video | el mismo de 02, estabilizado con `herramientas/estabilizar_stiv.py` |
| Resultado | **Q = 1.4475 m3/s** (9 de 11 verticales medidas, 2 rellenadas) |
| Referencia | 1.4362 m3/s, aforo ADV -> **+0.8 %** |
| Recursos | ~1-2 min y **870 MB de RAM**, frente a ~14 GB del caso 02 |

**Como ejecutarlo.** Con el entorno de `requirements_pyorc.txt`, desde esta carpeta:
- `SMC_STIV_pipeline.ipynb` -- el caso completo (partes 0-7).
- `python video_velocidad.py` -- la misma medida sobre los 22 s del video, con el video de flechas
  `salidas/video_velocimetria.mp4` (~9 min).

Necesita `entradas/SMC_estabilizado_stiv.mkv` (ya incluido; **no** es intercambiable con el de 02).

**Lee primero `GUIA_DEL_NOTEBOOK.md`**: explica cada parte en lenguaje sencillo, que mirar en cada
figura y que se puede cambiar sin romper nada.

**A tener en cuenta.** Las estaciones pegadas a las paredes (1 y 11) siempre fallan y se rellenan
por interpolacion lineal. Sobre el video completo, la mediana coincide con la de los 8 s del notebook
al 0.1 %: la ventana elegida no es una casualidad.
