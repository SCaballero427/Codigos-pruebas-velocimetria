# `presentaciones/estilo_bradano/` -- el canal con el formato del video del rio Bradano

Un fichero, `video_estilo_bradano.py`, y un producto, `salidas/velocidad_tiempo_real.mp4`: el canal
dibujado **igual que `casos/06_bradano_stiv/salidas/velocidad_tiempo_real.mp4`** -- un solo panel
cenital, lineas de busqueda verticales, una flecha por estacion con su valor en m/s, cuadros rojos
en las rechazadas, pie con `t`, mediana de la seccion y estaciones medidas, y barra de color.

## Lo que el video no dice

**Leer antes de usar el video para nada.** En pantalla no hay ningun aviso; es lo que se pidio.

| que se ve | de donde sale |
|---|---|
| **m/s, mm/px** | **escala simulada**: se supone una lamina de `ANCHO_LAMINA_M = 5.0 m` entre orillas. El caso no tiene ningun dato de campo y mide en alturas de camara; 5 m equivale a una camara a ~2.2 m sobre el agua |
| estaciones 8 a 13 | medida STIV directa (via `../seccion_completa/salidas/perfil_seccion.csv`) |
| estaciones 1 a 7 | **deducidas** del perfil Shiono-Knight escalado ventana a ventana por las que miden (ver `../seccion_completa/README.md`) |
| estaciones 0 y 14, cuadro rojo | rechazadas, y eso si es real: el caso las rechaza (coherencia y cota fisica la 0, orilla la 14) |
| "Canal piloto Yaqui" | nombre de la carpeta; el video de entrada es el mismo de WhatsApp de todo el caso 08 |

O sea: 6 de las 13 flechas son medida, 7 son modelo, y **todos los m/s dependen de un ancho que
nadie ha medido**. Cambiar `ANCHO_LAMINA_M` escala todos los valores en proporcion.

Resultado sobre las 138 ventanas: mediana de la seccion **0.137 m/s** (q05-q95 0.108 - 0.172).

**El CSV y el JSON si lo distinguen**: `config_video_velocidad.json` lleva
`ancho_lamina_m_SIMULADO`, `estaciones_con_medida_directa` y `estaciones_deducidas_del_modelo`.

## Diferencias de formato con el Bradano

- El panel es el plano del agua **rectificado** con `stiv_canal.Geometria` y estabilizado contra el
  primer fotograma (el Bradano ya venia ortorrectificado). Los triangulos negros de las esquinas
  son lo que cae fuera del encuadre del movil.
- Paleta de 0 a 0.2 m/s (el Bradano usa 1.5) y 900 px por m/s (el Bradano 190), para que flechas y
  colores ocupen lo mismo en pantalla con un agua casi 5 veces mas lenta.
- 15 estaciones en vez de 9, y ventana de 12 s en vez de 6.25 s: las del caso.

## Uso

```powershell
cd casos\08_canal_piloto_yaqui\presentaciones\estilo_bradano
python video_estilo_bradano.py                  # ~4.5 min
python video_estilo_bradano.py --muestra 900    # solo un PNG, para revisar el encuadre
```

No mide nada: lee las velocidades de `seccion_completa/` (que hay que haber ejecutado antes) e
importa la geometria, la estabilizacion y el escritor H.264 de `medicion/`.

| fichero | que es |
|---|---|
| `salidas/velocidad_tiempo_real.mp4` | 20 MB, 1920x770, 2429 fotogramas a tiempo real (81 s) |
| `salidas/velocidad_ventanas.csv` | mismo formato que el del Bradano, en m/s simulados |
| `salidas/config_video_velocidad.json` | configuracion, escala simulada y origen de cada estacion |
