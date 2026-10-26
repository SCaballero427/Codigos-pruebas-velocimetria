# Medicion de caudal por video

Espacio de investigacion para **estimar el caudal (o la velocidad superficial) de un rio o canal a
partir de un video**. Se prueban dos familias de metodos:

- **LSPIV** con la libreria [pyorc](https://github.com/localdevices/pyorc) (pyOpenRiverCam).
- **STIV** (Space-Time Image Velocimetry) programado desde cero sobre OpenCV, sin pyorc.

Cada caso toma un video, produce una velocidad o un caudal y, cuando hay datos de campo, lo compara
contra una referencia independiente (aforo ADV, ADCP, ejemplo publicado). La regla de todos los
casos: **la referencia se abre solo al final, una vez, y no se reajusta nada despues.**

---

## Por donde empezar

1. **Leer el informe** `docs/Informe_avances_medicion_caudal.docx` -- el resumen mas reciente del trabajo.
2. **Ver la tabla de casos** de abajo y abrir la carpeta que interese. Cada caso tiene su `README.md`
   (o `GUIA_DEL_NOTEBOOK.md`) y una carpeta `salidas/` con figuras, CSV y videos ya generados:
   no hace falta ejecutar nada para ver los resultados.
3. **Historia completa**: `docs/Resumen_cronologico_del_trabajo.md`.

**Videos.** El repositorio git no lleva los videos (pesan varios GB): solo las entradas pequenas que
hacen falta para ejecutar los casos. Los videos de entrada y de salida de cada caso estan en la carpeta
compartida *Resultados pruebas velocimetria*, con las mismas carpetas `01_...` a `09_...` que `casos/`.

---

## Mapa de carpetas

```
medicion_caudal_por_video/
|
|-- README.md                  <- este archivo
|-- requirements_pyorc.txt     <- librerias para los notebooks y scripts (Python 3.11)
|
|-- docs/                      informes .docx, resumen cronologico, ranking de datasets y notas tecnicas
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
|   `-- 09_directo_tokio/        programa en tiempo real sobre camaras en directo + Raspberry Pi
|
|-- evolucion_algoritmo_velocimetria/   los 9 casos como 9 versiones de un mismo codigo (v1 a v9),
|                              cada una con los cambios respecto a la anterior; ver su README.md
|-- codigo_stiv/               el STIV como modulo: version inicial (prueba 3) y completa (pruebas 4-8), con validar.py
|-- herramientas/              scripts sueltos reutilizables (estabilizar, convertir, marcar puntos, ffmpeg)
|-- tutoriales/                notebooks didacticos: STIV explicado paso a paso, primer notebook de pyorc
|-- datos/                     videos y mediciones de entrada (solo lectura)
|   `-- externos/              aqui va la carpeta de datasets de 46 GB (no copiada, ver LEEME.md)
|-- pendientes/                casos que tienen datos pero no tienen pipeline (Castor River, RIVeR)
|-- referencias/               copia de la libreria pyorc original, solo para consulta
`-- archivo/                   restos y versiones anteriores (p. ej. el caso 08 en 7 subcarpetas)
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

Lo que distingue a cada caso no es el rio sino **que informacion falta**: con geometria completa se
llega al caudal (01, 02, 03, 05); sin ella solo a la velocidad (04, 06, 08); y 07 demuestra cuando
el video no tiene nada que medir.

### El canal piloto Yaqui (`casos/08_canal_piloto_yaqui/`)

Un solo notebook, `Canal_piloto_Yaqui_pipeline.ipynb`, hace todo el caso paso a paso y termina
escribiendo el video con el formato del Bradano (vista de la camara y plano rectificado, a color).
Ojo: el video **no dice en pantalla** que 7 de las 13 flechas son deducidas por un modelo ni que
los m/s dependen de un ancho de canal supuesto (5 m); el notebook y su README si.

La version anterior, en siete subcarpetas (arbitro PTV, experimentos de alcance y de filtro,
modelo de seccion y tres videos), esta en `archivo/08_canal_piloto_yaqui/`.

`casos/08_canal_piloto_yaqui/simulador_camara_puente/` simula una camara fija en el puente del
canal (encuadre, cm/px y angulo de la STI) para decidir el montaje antes de instalarla. Solo
necesita Python con tkinter: `python simulador_stiv_puente.py`.

---

## Como ejecutar

Cada notebook y cada script se ejecuta **desde su propia carpeta** (todas las rutas son relativas).

**Notebooks y scripts de `casos/01` a `08`, `herramientas/` y `tutoriales/`** -- un entorno con pyorc:

```powershell
python -m venv entorno_pyorc            # Python 3.11
.\entorno_pyorc\Scripts\pip install -r requirements_pyorc.txt
.\entorno_pyorc\Scripts\Activate.ps1
cd casos\02_smc_pyorc
jupyter lab
```

**Programa en directo (`casos/09_directo_tokio`)**: doble clic en `arrancar.bat`. La primera vez crea
su propio entorno (`.venv`, solo numpy + OpenCV + yt-dlp) e instala lo necesario.

### Lo que hay que tener antes de ejecutar algunos casos

| Caso | Necesita | Como se consigue |
|---|---|---|
| 04, 05, 06, 07 y la validacion de 09 | los datasets descargados (46 GB) | moverlos a `datos/externos/` -- ver `datos/externos/LEEME.md` |
| 02 | `entradas/SMC_estabilizado.mkv` (ya esta copiado) | si se borra: `herramientas/estabilizar_video.py` |
| 03 | `entradas/SMC_estabilizado_stiv.mkv` (ya esta copiado) | si se borra: `herramientas/estabilizar_stiv.py` |

Los casos 01, 02, 03 y 08 tienen todos sus datos dentro de esta carpeta.

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

## Equivalencias con la estructura anterior

Esta carpeta es una copia reorganizada de `test_pyorc/`. Los textos dentro de los casos (README,
guias, comentarios del codigo) todavia citan los nombres antiguos; esta tabla los traduce. **Las
rutas del codigo ya estan actualizadas** y verificadas.

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

No se copiaron: los entornos de Python (`pyorc_env/`, `.venv/`; se regeneran) ni la copia duplicada
`test_pyorc/test_pyorc/`, cuyo contenido es el que esta repartido aqui.
