# Herramientas

Scripts independientes que sirven a varios casos. Se ejecutan **desde la raiz del proyecto**.

| Script | Que hace | Usado por |
|---|---|---|
| `estabilizar_video.py` | video tembloroso -> video estabilizado (FFV1 sin perdida), con las funciones de pyorc | `casos/02_smc_pyorc/entradas/` |
| `estabilizar_stiv.py` | lo mismo solo con OpenCV, sin pyorc; mas preciso (27x menos temblor frente a 4.9x) | `casos/03_smc_stiv/entradas/` y `video_velocidad.py` de ese caso |
| `convertir_a_mp4.py` | cualquier video -> `.mp4` para mirarlo. Con perdida: **nunca** usarlo como entrada de un caso | -- |
| `pixel_locator.py` | abre un video, se hace clic sobre el primer fotograma y guarda las coordenadas en pixeles. Asi se obtienen los puntos de control y las zonas marcadas `>>> AJUSTABLE <<<` | -- |
| `ffmpeg/` | `ffmpeg.exe` y `ffprobe.exe` (copiados de RIVeR). Los casos lo usan para escribir H.264, que el OpenCV de este entorno no puede | todos los `escritor_video.py` |

Ejemplos:

```powershell
python herramientas/estabilizar_video.py datos/USGS/Video/SMC_D_RC_022_08172020_AC.mp4 `
    casos/02_smc_pyorc/entradas/SMC_estabilizado.mkv `
    --poligono "0,420 3840,420 3840,1500 0,1500" --fin 249

python herramientas/convertir_a_mp4.py casos/02_smc_pyorc/entradas/SMC_estabilizado.mkv --escala 0.5
```

`--inicio` / `--fin` son indices de fotograma, ambos incluidos: 250 fotogramas es `--fin 249`.
