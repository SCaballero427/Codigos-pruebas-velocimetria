# 02 · Sile Main Canal (USGS) -- LSPIV con pyorc, dron cenital

**Que es.** Caudal de un canal de hormigon filmado por un dron en 4K, con pyorc, comparado contra un
aforo ADV independiente. Forma pareja con `03_smc_stiv`: **mismo video, misma configuracion, otro
metodo**, para que la diferencia mida el algoritmo y no la preparacion.

| | |
|---|---|
| Metodo | LSPIV (pyorc 0.9.8) |
| Video | `datos/USGS/Video/SMC_D_RC_022_08172020_AC.mp4`, dron cenital, 4K, 250 fotogramas |
| Geometria | 2 puntos sobre la linea de agua + ancho conocido del canal (1.8288 m) -> 1.7790 mm/px |
| Resultado | **Q = 1.4565 m3/s** (cuantiles 0.05-0.95: 1.353-1.575) |
| Referencia | 1.4362 m3/s, aforo FlowTracker ADV -> **+1.4 %** |

**Como ejecutarlo.** Con el entorno de `requirements_pyorc.txt`, desde esta carpeta, abrir
`SMC_pipeline_completo.ipynb`. Tarda ~160 s y llega a **~14 GB de RAM**.
Necesita `entradas/SMC_estabilizado.mkv` (ya incluido). Si se borra, regenerarlo desde la raiz:

```powershell
python herramientas/estabilizar_video.py datos/USGS/Video/SMC_D_RC_022_08172020_AC.mp4 `
    casos/02_smc_pyorc/entradas/SMC_estabilizado.mkv --poligono "0,420 3840,420 3840,1500 0,1500" --fin 249
```

**Archivos.**
- `SMC_pipeline_completo.ipynb` -- partes 0-7: rutas, video, escala, camara, PIV, mascaras, caudal,
  recursos y, al final, la comparacion con el aforo.
- `benchmark.py` -- mide tiempo y memoria de cada bloque.
- `entradas/` -- video estabilizado (FFV1 sin perdida; el `_previsualizacion.mp4` es solo para mirar).
- `salidas/` -- `config_pyorc.json`, `perfil_transecto.csv` (vertical por vertical: medida o rellenada),
  `caudal_resumen.csv`, `benchmark_recursos.csv` y figuras `fig1_`...`fig12_`.

**A tener en cuenta.**
- El aforo **solo se abre en la parte 7**. `v_corr = 0.92` se fijo antes, por ser el que usa el caso STIV.
- La linea de agua inferior es una rampa de sombra de ~85 px: es la principal incertidumbre geometrica
  del caso, y la figura 2 existe para poder discutirla.
