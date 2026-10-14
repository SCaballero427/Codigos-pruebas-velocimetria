# Pendientes: datos preparados, sin pipeline

Nada de esta carpeta funciona todavia como caso. Que haya datos no significa que haya un notebook.

| Que | Estado | Que falta |
|---|---|---|
| `Prueba_Castor_River.ipynb` | copia del primer notebook de Ngwerere con las rutas cambiadas; **falla en la celda 2** | solo la ruta: los datos ya estan descargados en `datos/externos/datasets vision velocimetria/data/CastorRiver/20190709/Video4/`. Ademas conserva el titulo de Ngwerere y un comentario de CRS que no aplica |
| `RIVeR-STIV_1.0/` | la aplicacion RIVeR (ejecutable de MATLAB) con un ejemplo completo en `RIVeR_Example/`: video GoPro, 6 distancias medidas, seccion `Station_Stage.csv` y **la respuesta de RIVeR para ese mismo video** (`New_project.rvr`, `CS_0/`) | empezar el caso desde `casos/01_ngwerere_pyorc` (camara oblicua). La seccion viene como progresiva/profundidad, no x,y,z, asi que la parte de caudal hay que adaptarla |
| `RIVeR-STIV_1.0Summary.png` | imagen resumen de RIVeR | -- |

Los puntos que se marcaron sobre el video de RIVeR en el intento anterior estan en `archivo/GOPR3225_Trim_*`.

El `ffmpeg.exe` de RIVeR se usa en todo el proyecto para escribir video H.264; hay una copia en
`herramientas/ffmpeg/`, que es la que usa el codigo.
