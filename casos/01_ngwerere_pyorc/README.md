# 01 · Ngwerere -- LSPIV con pyorc, camara fija oblicua

**Que es.** El primer caso: reproducir con pyorc el ejemplo publicado del rio Ngwerere (Zambia).
Sirve de plantilla para cualquier camara fija oblicua con 4 o mas puntos de control.

| | |
|---|---|
| Metodo | LSPIV (pyorc 0.9.8) |
| Video | `datos/ngwerere/ngwerere_20191103.mp4`, camara fija, 1920x1080, 125 fotogramas |
| Geometria | 4 puntos de control RTK en UTM 35S, seccion de 27 puntos topografiados |
| Resultado | **Q mediana 0.1672 m3/s** (cuantiles 0.05-0.95: 0.076-0.240) |
| Referencia | 0.164 m3/s del ejemplo publicado de pyorc -> **+1.9 %** |

**Como ejecutarlo.** Con el entorno de `requirements_pyorc.txt`, desde esta carpeta:
abrir `Ngwerere_pipeline_completo.ipynb` y ejecutar de arriba abajo.

**Archivos.**
- `Ngwerere_pipeline_completo.ipynb` -- el pipeline completo en 6 partes: rutas, video, puntos de
  control, configuracion de camara, PIV + mascaras, caudal.
- `salidas/` -- configuracion de camara, resultados PIV (`.nc`), transecto, `caudal_resumen.csv` y figuras.

**A tener en cuenta.**
- `mask.angle()` se llama **sin** `inplace=True` a proposito, para reproducir el 0.164 publicado
  (aplicarla subiria la mediana a ~0.174). No es un error.
- La reproduccion exacta no es posible: pyorc estima la focal por optimizacion y ffpiv redondea la
  ventana a par (25 -> 26).
- `tutoriales/Notebook_Analisis_Ngwerere.ipynb` es la primera version exploratoria de este caso.
