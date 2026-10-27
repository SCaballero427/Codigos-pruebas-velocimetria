# Medicion de caudal por video

Espacio de investigacion para **estimar el caudal (o la velocidad superficial) de un rio o canal a
partir de un video**. Se prueban dos familias de metodos:

- **LSPIV** con la libreria [pyorc](https://github.com/localdevices/pyorc) (pyOpenRiverCam).
- **STIV** (Space-Time Image Velocimetry) programado desde cero sobre OpenCV, sin pyorc.

Cada caso toma un video, produce una velocidad o un caudal y, cuando hay datos de campo, lo compara
contra una referencia independiente (aforo ADV, ADCP, ejemplo publicado). La regla de todos los
casos: **la referencia se abre solo al final, una vez, y no se reajusta nada despues.**

El repositorio lleva **solo los casos** y lo imprescindible para ejecutarlos: las entradas que leen
(`datos/`), las herramientas que usan (`herramientas/`) y el entorno (`requirements_pyorc.txt`).

---

## Por donde empezar

1. **Ver la tabla de casos** de abajo y abrir la carpeta que interese. Cada caso tiene su `README.md`
   (o `GUIA_DEL_NOTEBOOK.md`) y una carpeta `salidas/` con figuras y CSV ya generados: no hace falta
   ejecutar nada para ver los resultados.
2. Para ejecutarlo, ver [Como ejecutar](#como-ejecutar) y lo que hay que conseguir antes.

**Videos.** El repositorio no lleva los videos (pesan varios GB): solo las entradas pequenas que
hacen falta para ejecutar los casos. Los videos de entrada y de salida de cada caso estan en la carpeta
compartida *Resultados pruebas velocimetria*, con las mismas carpetas `01_...` que `casos/`.

---

## Mapa de carpetas

```
medicion_caudal_por_video/
|
|-- README.md                  <- este archivo
|-- requirements_pyorc.txt     <- librerias para los casos 01 a 08 y herramientas/ (Python 3.11)
|
|-- casos/                     UN CASO = UNA CARPETA. Numerados en orden de lectura
|   |-- 01_ngwerere_pyorc/       LSPIV con pyorc, camara fija oblicua (Zambia)
|   |-- 02_smc_pyorc/            LSPIV con pyorc, dron cenital (canal USGS)
|   |-- 03_smc_stiv/             STIV desde cero, MISMO video que 02 -> comparacion de metodos
|   |-- 04_boneyard_stiv/        STIV con camara oblicua y sin ninguna geometria
|   |-- 05_hommerich_stiv/       STIV metrico con camara calibrada (Paises Bajos)
|   |-- 06_bradano_stiv/         STIV sobre video ya ortorrectificado (Italia)
|   |-- 07_arrow_siembra/        experimento: el mismo rio con y sin trazador sembrado
|   |-- 08_canal_piloto_yaqui/   STIV sobre un video de movil de WhatsApp, un solo notebook
|   |-- 09_directo_tokio/        programa en tiempo real sobre camaras en directo
|   `-- 10_raspberry_pi/         el programa de 09 en una Raspberry Pi 4B: instalar, manejar y probar
|
|-- herramientas/              estabilizar los videos de entrada de 02 y 03; ffmpeg para escribir H.264
`-- datos/                     entradas de los casos (solo lectura)
    |-- ngwerere/  USGS/  canal_riego/
    `-- externos/              aqui va la carpeta de datasets de 46 GB (no esta en git, ver LEEME.md)
```

---

## Tabla de casos

| # | Carpeta | Metodo | Camara / video | Produce | Resultado | Referencia | Punto de entrada |
|---|---|---|---|---|---|---|---|
| 01 | `casos/01_ngwerere_pyorc` | LSPIV (pyorc) | fija, oblicua, 4 GCPs RTK | caudal | **0.1672 m3/s** (+1.9 %) | 0.164 m3/s, ejemplo publicado | `Ngwerere_pipeline_completo.ipynb` |
| 02 | `casos/02_smc_pyorc` | LSPIV (pyorc) | dron cenital 4K | caudal | **1.4565 m3/s** (+1.4 %) | 1.4362 m3/s, aforo ADV | `SMC_pipeline_completo.ipynb` |
| 03 | `casos/03_smc_stiv` | STIV propio | el mismo video que 02 | caudal | **1.4475 m3/s** (+0.8 %) | 1.4362 m3/s, aforo ADV | `SMC_STIV_pipeline.ipynb` |
| 04 | `casos/04_boneyard_stiv` | STIV propio | camara IP oblicua, sin geometria | velocidad en unidades relativas | **0.2427 alturas de camara/s** | Q del USGS, no usado para ajustar | `Boneyard_STIV_pipeline.ipynb` |
| 05 | `casos/05_hommerich_stiv` | STIV propio | oblicua, calibrada, 6 GCPs | caudal | **13.68 m3/s** | ninguna disponible | `video_velocidad.py` |
| 06 | `casos/06_bradano_stiv` | STIV propio | dron, ya ortorrectificado | velocidad m/s | 5 de 7 verticales, **sesgo -3.1 %**, r = 0.996 | velocidades HARMONIOUS | `Bradano_STIV_pipeline.ipynb` |
| 07 | `casos/07_arrow_siembra` | STIV propio (experimento) | GoPro en mastil, con y sin siembra | si el metodo mide o no | sin siembra: **0 de 49** estaciones; con siembra: media -6.7 % | velocidades HARMONIOUS + PIV arbitro | `Arrow_STIV_pipeline.ipynb` |
| 08 | `casos/08_canal_piloto_yaqui` | STIV propio | movil, WhatsApp, sin ningun dato de campo | velocidad (m/s con ancho supuesto) | **0.0590 alturas de camara/s**, 6 de 15 estaciones | arbitro PTV propio, r = 0.984 (version archivada) | `Canal_piloto_Yaqui_pipeline.ipynb` |
| 09 | `casos/09_directo_tokio` | STIV propio, en directo | camaras de rio de Tokio en YouTube | velocidad m/s cada segundo | Myoshoji de dia: **0.48 m/s** mediana | nivel oficial + aforos historicos; el mismo codigo validado con los videos de 03 (Q +1.2 %) y 06 | `arrancar.bat` |
| 10 | `casos/10_raspberry_pi` | el programa de 09, en una Raspberry Pi 4B | las de 09, o una camara IP por RTSP | lo mismo que 09, sin pantalla y con visor web | Pi 4B real: **tiempo real** (30 fps), ~0.47 s por medida, ~400 MB de RAM, sin frenado por calor | -- | `subir_a_raspberry.bat` |

Lo que distingue a cada caso no es el rio sino **que informacion falta**: con geometria completa se
llega al caudal (01, 02, 03, 05); sin ella solo a la velocidad (04, 06, 08); y 07 demuestra cuando
el video no tiene nada que medir. 09 y 10 llevan el metodo a una camara en directo.

### El canal piloto Yaqui (`casos/08_canal_piloto_yaqui/`)

Un solo notebook, `Canal_piloto_Yaqui_pipeline.ipynb`, hace todo el caso paso a paso y termina
escribiendo el video con el formato del Bradano (vista de la camara y plano rectificado, a color).
Ojo: el video **no dice en pantalla** que 7 de las 13 flechas son deducidas por un modelo ni que
los m/s dependen de un ancho de canal supuesto (5 m); el notebook y su README si.

`casos/08_canal_piloto_yaqui/simulador_camara_puente/` simula una camara fija en el puente del
canal (encuadre, cm/px y angulo de la STI) para decidir el montaje antes de instalarla. Solo
necesita Python con tkinter: `python simulador_stiv_puente.py`.

### La Raspberry Pi (`casos/10_raspberry_pi/`)

El programa no se duplica: vive en `casos/09_directo_tokio/`, y `subir_a_raspberry.bat` lo copia a
la Pi junto con las configs de camara y los dos videos de prueba de ese caso, y lo instala como
servicio que arranca solo al encender. `pruebas_docker/` prueba todo eso sin hardware (una Pi falsa
emulada y una camara RTSP simulada) y `salidas_raspberry/` guarda lo medido en la Pi real.

---

## Como ejecutar

Cada notebook y cada script se ejecuta **desde su propia carpeta** (todas las rutas son relativas).

**Notebooks y scripts de `casos/01` a `08` y `herramientas/`** -- un entorno con pyorc:

```powershell
python -m venv entorno_pyorc            # Python 3.11
.\entorno_pyorc\Scripts\pip install -r requirements_pyorc.txt
.\entorno_pyorc\Scripts\Activate.ps1
cd casos\02_smc_pyorc
jupyter lab
```

**Programa en directo (`casos/09_directo_tokio`)**: doble clic en `arrancar.bat`. La primera vez crea
su propio entorno (`.venv`, solo numpy + OpenCV + yt-dlp) e instala lo necesario.

**Raspberry Pi (`casos/10_raspberry_pi`)**: doble clic en `subir_a_raspberry.bat` desde el PC; la Pi
crea su propio entorno. Paso a paso en su `README.md`.

### Lo que hay que tener antes de ejecutar algunos casos

| Caso | Necesita | Como se consigue |
|---|---|---|
| 04, 05, 06, 07 y la validacion de 09 | los datasets descargados (46 GB) | moverlos a `datos/externos/` -- ver `datos/externos/LEEME.md` |
| 02, 03 y la validacion de 09 | el video del USGS, `datos/USGS/Video/SMC_D_RC_022_08172020_AC.mp4` | de la pagina de `datos/USGS/link.txt` (o de la carpeta compartida) |
| 02 | `entradas/SMC_estabilizado.mkv` | `herramientas/estabilizar_video.py` sobre ese video (ver `herramientas/LEEME.md`) |
| 03 | `entradas/SMC_estabilizado_stiv.mkv` | `herramientas/estabilizar_stiv.py` sobre ese video |
| 10 | una Raspberry Pi 4B con Raspberry Pi OS Lite de 64 bits | ver `casos/10_raspberry_pi/README.md`; sin placa, `pruebas_docker/` (Docker Desktop) |

Los casos 01 y 08 tienen todos sus datos en el repositorio.

---

## Convenciones del proyecto

- **Una carpeta por caso**, con `salidas/` para todo lo que se genera y `entradas/` si el caso
  necesita un video preprocesado. Las figuras se numeran `fig1_`, `fig2_`... en orden de creacion.
- **`>>> AJUSTABLE <<<`** marca los valores que dependen de juicio humano (puntos de control,
  zonas, umbrales). Todos estan al principio de la parte que los usa.
- **Comentarios y textos en espanol sin tildes.** Los comentarios explican *por que* se eligio un
  valor, no que hace la linea.
- **La referencia de campo se abre solo en la ultima parte.** Ningun parametro se ajusta para
  acercarse a ella.
- Cada notebook termina con sus **limitaciones conocidas**.

---

## Fuera del repositorio

La carpeta de trabajo tiene ademas `docs/` (informes y notas tecnicas), `tutoriales/`,
`evolucion_algoritmo_velocimetria/`, `codigo_stiv/`, `pendientes/`, `referencias/` y `archivo/`
(versiones anteriores, p. ej. el caso 08 en siete subcarpetas). No hacen falta para ejecutar los
casos y no se suben (`.gitignore` solo admite lo de arriba), aunque algunos textos de los casos los
citan. Tampoco `herramientas/pixel_locator.py` (marcar puntos sobre el primer fotograma) ni
`convertir_a_mp4.py`.

## Equivalencias con la estructura anterior

Esta carpeta es una copia reorganizada de `test_pyorc/`. Los textos dentro de los casos (README,
guias, comentarios del codigo) todavia citan los nombres antiguos; esta tabla los traduce. **Las
rutas del codigo ya estan actualizadas** y verificadas. Las carpetas `archivo/`, `tutoriales/`,
`pendientes/`, `referencias/` y `docs/` de la derecha no estan en el repositorio.

| Antes | Ahora |
|---|---|
| `analisis_ngwerere/` | `casos/01_ngwerere_pyorc/` |
| `analisis_USGS_SMC_pyorc/` | `casos/02_smc_pyorc/` |
| `analisis_USGS_SMC_stiv/` | `casos/03_smc_stiv/` |
| `analisis_boneyard_stiv/` | `casos/04_boneyard_stiv/` |
| `analisis_hommerich_stiv/` | `casos/05_hommerich_stiv/` |
| `analisis_bradano_stiv/` | `casos/06_bradano_stiv/` |
| `analisis_arrow_stiv/` | `casos/07_arrow_siembra/` |
| `analisis_canal_riego_stiv/` | `archivo/08_canal_piloto_yaqui/medicion/` |
| `analisis_canal_completo_stiv/` | `archivo/08_canal_piloto_yaqui/completo_con_modelo/` |
| `analisis_canal_lejano_stiv/` | `archivo/08_canal_piloto_yaqui/experimentos/alcance/` |
| `analisis_canal_filtro_adaptado/` | `archivo/08_canal_piloto_yaqui/experimentos/filtro/` |
| `analisis_canal_stiv_puro/` | `archivo/08_canal_piloto_yaqui/presentaciones/stiv_puro/` |
| `analisis_canal_seccion_completa/` | `archivo/08_canal_piloto_yaqui/presentaciones/seccion_completa/` |
| `casos/08_canal_riego/` | `casos/08_canal_piloto_yaqui/` (un notebook); sus subcarpetas, en `archivo/08_canal_piloto_yaqui/` |
| `analisis_kurome_directo_stiv/` | `casos/09_directo_tokio/` |
| `casos/09_directo_tokio/raspberry/`, `pruebas_docker/`, `salidas_raspberry/` | `casos/10_raspberry_pi/` (lo de `raspberry/`, suelto en la raiz del caso) |
| `casos/09_directo_tokio/raspberry/prueba/` | `casos/09_directo_tokio/prueba/` |
| `ngwerere/`, `USGS/` | `datos/ngwerere/`, `datos/USGS/` |
| `videos/WhatsApp Video ... .mp4` | `datos/canal_riego/` |
| `datasets vision velocimetria/` | `datos/externos/` (no copiado) |
| `estabilizar_video.py`, `estabilizar_stiv.py`, `convertir_a_mp4.py`, `pixel_locator.py` | `herramientas/` |
| `RIVeR-STIV_1.0/ffmpeg.exe` (lo usaban los casos para escribir video) | `herramientas/ffmpeg/` |
| `STIV_desde_cero.ipynb`, `Notebook_Analisis_Ngwerere.ipynb` | `tutoriales/` |
| `Prueba_Castor_River.ipynb`, `RIVeR-STIV_1.0/` | `pendientes/` |
| `pyorc_repo/` | `referencias/pyorc_repo/` |
| notas tecnicas de la raiz | `docs/notas_tecnicas_detalladas.md` |
| `test_pyorc.py`, `video_test.py`, `scratch_*.npy`, `GOPR3225_*` | `archivo/` |
