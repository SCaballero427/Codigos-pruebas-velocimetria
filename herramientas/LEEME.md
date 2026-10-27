# Herramientas

Lo que usan los casos y no es de ninguno en particular. Los scripts se ejecutan **desde la raiz del
proyecto**.

| Script | Que hace | Usado por |
|---|---|---|
| `estabilizar_video.py` | video tembloroso -> video estabilizado (FFV1 sin perdida), con las funciones de pyorc | `casos/02_smc_pyorc/entradas/` |
| `estabilizar_stiv.py` | lo mismo solo con OpenCV, sin pyorc; mas preciso (27x menos temblor frente a 4.9x) | `casos/03_smc_stiv/entradas/` y `video_velocidad.py` de ese caso |
| `ffmpeg/` | `ffmpeg.exe` (copiado de RIVeR). Los casos lo usan para escribir H.264, que el OpenCV de este entorno no puede | `video_velocidad.py` de 03, los `escritor_video.py` de 04 a 07 y el notebook de 08 |

Los dos `.mkv` estabilizados no estan en el repositorio (pesan ~1 GB): se rehacen asi, desde el
video del USGS (`datos/USGS/link.txt`):

```powershell
python herramientas/estabilizar_video.py datos/USGS/Video/SMC_D_RC_022_08172020_AC.mp4 `
    casos/02_smc_pyorc/entradas/SMC_estabilizado.mkv `
    --poligono "0,420 3840,420 3840,1500 0,1500" --fin 249

python herramientas/estabilizar_stiv.py datos/USGS/Video/SMC_D_RC_022_08172020_AC.mp4 `
    casos/03_smc_stiv/entradas/SMC_estabilizado_stiv.mkv `
    --poligono "0,420 3840,420 3840,1500 0,1500" --fin 249
```

No son intercambiables: distinto script, distinto temblor residual.

`--inicio` / `--fin` son indices de fotograma, ambos incluidos: 250 fotogramas es `--fin 249`.
