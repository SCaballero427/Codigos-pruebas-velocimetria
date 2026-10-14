# Vídeo 4 — El programa en directo para la cámara de ALIAR

**Duración:** ~10 min, una sola toma, sin edición.

**Carpeta:** `videos_explicativos/video4_programa_en_directo/analisis_kurome_directo_stiv/`
(todos los archivos de abajo están dentro de ella).

**Archivos que se abren, en este orden:**

1. `salidas/shimoda/ultima_vista.png`
2. `stiv_directo.py`
3. `salidas/shimoda/config_stiv_directo.json`
4. `fuentes.json`
5. `stiv_directo.py` (otra vez, ya abierto)
6. `README.md`

> **Los números de línea son los de la COPIA de esta carpeta**, no los del
> `analisis_kurome_directo_stiv/` de la raíz del workspace, que sigue cambiando.

## Antes de grabar

- Cerrar todas las pestañas: `Ctrl+K W`.
- Abrir los archivos **en el orden de arriba**, desde el explorador de la carpeta de este vídeo
  (cinco pestañas: el `.py` se reutiliza). Dejar activa la pestaña de la imagen.
- Subir el zoom de VS Code con `Ctrl +` (dos o tres pulsaciones) hasta que el código se lea bien en
  la grabación.
- Activar "No molestar" en Windows y cerrar los avisos de VS Code.
- Desactivar el ajuste de línea si está puesto (`Alt+Z`), para que los números de línea casen con lo
  que se ve.
- Si te equivocas al hablar, di "me corrijo" y sigue. No se para la grabación.

**Cómo navegar:** en `.py`, `.md` y `.json`, `Ctrl+G`, el número de línea y `Enter`. La imagen se
abre con un clic en el explorador (en la pestaña de la imagen `Ctrl+G` no hace nada: cambiar antes
de pestaña).

**Cómo leer este guion:** lo que va en el bloque `>` se lee en voz alta. Lo que va entre corchetes y
en cursiva, *[así]*, es una acción y **no se lee**.

---

## 1. Qué produce el programa — 0:00 a 1:40

**Archivo:** `salidas/shimoda/ultima_vista.png`

**Haz:**

1. Con la imagen en pantalla, señalar con el ratón la vista de la izquierda (el directo): las líneas
   verdes numeradas 0 a 8 y las flechas amarillas.
2. Señalar la vista de la derecha ("VISTA RECTIFICADA") y la barra blanca de "1 m", abajo a su
   izquierda.
3. Señalar la cabecera de arriba a la izquierda: la línea "mediana seccion: 1.091 m/s (9/9
   estaciones)" y la línea naranja "ESCALA SUPUESTA".
4. Señalar el panel de abajo: los nueve recuadros grises con la línea verde encima.
5. Señalar la etiqueta del primer recuadro: `0: +0.520 m/s c0.52 b8 10s`.

**Di:**

> Este es el cuarto vídeo. Hoy enseño el programa que mide en directo, el que irá en la cámara de
> ALIAR: una cámara IP fija conectada a una Raspberry Pi, que es un ordenador pequeño. Mientras
> llega, lo he desarrollado con cámaras públicas que vigilan ríos de Tokio y emiten por YouTube.
>
> Empiezo por el resultado, que el programa guarda como imagen: el río Kurome, en el puente Shimoda.
> *[señalar la vista izquierda]*
>
> A la izquierda, la imagen tal como llega. Las líneas verdes son nueve estaciones: nueve sitios, a
> lo ancho del río, donde se mide. Cada flecha amarilla es la velocidad de la superficie ahí.
> *[señalar la vista derecha]*
>
> A la derecha, la misma imagen rectificada: vista en planta, como desde arriba, con el agua de
> izquierda a derecha. Abajo, una barra de un metro. *[señalar la cabecera]*
>
> Arriba, la mediana de la sección: 1,091 metros por segundo, con nueve de nueve estaciones. Y en
> naranja: escala supuesta. Los metros de esta cámara no están medidos. *[señalar el panel]*
>
> Abajo, lo más importante: el STI de cada estación, la imagen espacio-tiempo. En horizontal, la
> posición en la línea; en vertical, el tiempo. Lo que flota deja rayas inclinadas, y la inclinación
> es la velocidad. La línea verde es la medida. Si no sigue las rayas, el número no vale. Así cada
> flecha se puede revisar. *[señalar la etiqueta de la estación 0]*
>
> En la etiqueta: la velocidad; "c", la coherencia, lo ordenadas que están las rayas, de cero a uno;
> "b", los bloques activos, trozos con agua que se mueve de verdad; y la escala, 10 segundos. La
> estación 0 pasa con 8 bloques; el mínimo son 6. Va justa.

---

## 2. Qué hace y cómo se lanza — 1:40 a 2:35

**Archivo:** `stiv_directo.py`

**Haz:**

| `Ctrl+G` | Qué se ve | Qué señalar |
|---|---|---|
| 1 | primera línea del docstring | líneas 1 a 7 (las cuatro cámaras) |
| 9 | qué hace | líneas 9 a 12 |
| 14 | cómo se lanza | líneas 14 a 18 |
| 19 | cámara propia por RTSP | líneas 19 a 21 |
| 23 | Raspberry sin pantalla | líneas 23 y 24 |
| 44 | aviso de escala | líneas 44 a 46 |

**Di:**

> *[pestaña stiv_directo.py, Ctrl+G 1]*
> Ahora el código. Todo el programa es un archivo, stiv_directo.py, de unas mil cuatrocientas
> líneas. *[Ctrl+G 9]*
>
> Abre el directo y mide enseguida: cada fotograma se lee a lo largo de las líneas, las filas se
> apilan en un STI y cada poco se recalcula la velocidad. No usa pyorc. *[Ctrl+G 14]*
>
> Sin nada más, mide la cámara por defecto; con "--archivo", un vídeo grabado. En Windows, doble clic
> en arrancar.bat. *[Ctrl+G 19]*
>
> Esta línea es la de ALIAR: un nombre de cámara nuevo y una dirección RTSP. RTSP es el protocolo
> con el que las cámaras IP mandan el vídeo por la red. *[Ctrl+G 23]*
>
> En la Raspberry no hay pantalla: "--sin-ventana", y "--vista-cada 30" guarda cada 30 segundos la
> imagen que acabamos de ver. *[Ctrl+G 44]*
>
> Y el aviso: sin la escala verificada, la forma del perfil vale, pero los metros por segundo
> dependen de unas medidas supuestas.

---

## 3. Configurar una cámara — 2:35 a 4:15

**Archivos:** `stiv_directo.py` → `salidas/shimoda/config_stiv_directo.json` → `fuentes.json`

**Haz:**

| Archivo | `Ctrl+G` | Qué se ve | Qué señalar |
|---|---|---|---|
| `stiv_directo.py` | 83 | recuadro `>>> AJUSTABLE <<<` y `CAMARAS` | líneas 86 y 87 (qué es el cuadrilátero), 92 |
| `stiv_directo.py` | 127 | la entrada `"shimoda"` | línea 138 (cuadrilátero), 139 (largo y ancho), 140 (`v_esperada`), 147 (`filtro_direccional`) |
| `stiv_directo.py` | 168 | `CAMARA_NUEVA` | líneas 168 a 179 |
| `stiv_directo.py` | 267 | `elegir_camara` | líneas 270 a 273 (docstring), luego línea 311 |
| `config_stiv_directo.json` | 5 | lo guardado del Shimoda | líneas 5 a 25; parar en la 25 |
| `fuentes.json` | 12 | la entrada del Shimoda | líneas 12 a 16 |

**Di:**

> *[Ctrl+G 83]*
> Lo que cambia entre cámaras está aquí, en CAMARAS: un diccionario, es decir, nombres con sus
> valores. Lo principal es el cuadrilátero: cuatro esquinas, en píxeles, de algo que en la realidad
> es un rectángulo sobre el agua. Como vimos en el vídeo 3, se dibuja a mano. *[Ctrl+G 127]*
>
> El Shimoda: sus cuatro esquinas, y largo 12 metros por ancho 5, supuestos. "v_esperada", 0,6
> metros por segundo, solo sirve para elegir el muestreo. Y el filtro direccional, que veremos al
> final. *[Ctrl+G 168]*
>
> CAMARA_NUEVA es la plantilla para una cámara que no está en la lista: la de ALIAR. Empieza con un
> rectángulo en el centro, que se arrastra sobre el agua con la tecla "e" y se guarda con la "g".
> "fps_camara None" quiere decir que la cámara no repite fotogramas, como sí hace YouTube.
> *[Ctrl+G 267]*
>
> elegir_camara carga esos valores. Una cámara nueva con configuración guardada los toma de su
> archivo: la Raspberry se configura editando solo ese archivo. *[señalar línea 311]* Aquí, el tope:
> tres veces la velocidad esperada. *[pestaña config_stiv_directo.json, Ctrl+G 5]*
>
> Este es el archivo del Shimoda: las esquinas, largo 12, ancho 5 y "escala_verificada: false". Por
> eso el aviso naranja. En ALIAR habrá que medir dos distancias reales y ponerlo a true.
> *[pestaña fuentes.json, Ctrl+G 12]*
>
> Y fuentes.json es la lista de directos y vídeos entre los que se puede cambiar. Añadir la cámara de
> ALIAR es añadir una entrada aquí.

---

## 4. La geometría — 4:15 a 5:30

**Archivo:** `stiv_directo.py` (volver a su pestaña)

**Haz:**

| `Ctrl+G` | Qué se ve | Qué señalar |
|---|---|---|
| 412 | `class Geometria` | líneas 418 y 419 (homografía) |
| 420 | `k_real` | líneas 420 a 422 |
| 423 | `self.ds` | líneas 423 y 424 |
| 427 | estaciones y banda | líneas 427 a 430 |
| 431 | mapa de `remap` | líneas 431 a 435 |
| 436 | `px_por_muestra` | líneas 436 a 438 |
| 1198 | aviso de aliasing | líneas 1198 y 1199 |

**Di:**

> *[pestaña stiv_directo.py, Ctrl+G 412]*
> Geometria traduce entre metros y píxeles. Primero, la homografía: la fórmula que lleva un punto del
> rectángulo real, en metros, a su píxel en la imagen. OpenCV la saca de las cuatro esquinas.
> *[Ctrl+G 420]*
>
> Segundo, k_real. Las cámaras de Tokio dan 15 fotogramas por segundo, y YouTube repite cada uno para
> llegar a 30. k_real vale 2: una fila por fotograma real. *[Ctrl+G 423]*
>
> Tercero, DS, el paso entre muestras a lo largo de la línea: la velocidad esperada por el tiempo
> entre fotogramas. Así el agua avanza una muestra por fotograma, y las rayas salen a 45 grados,
> donde el error pesa menos. En el Shimoda, 4 centímetros. *[Ctrl+G 427]*
>
> Cuarto, nueve estaciones a lo ancho, con un 6 % libre junto a cada orilla. Cada una es una banda de
> siete líneas paralelas que se promedian: más señal. *[Ctrl+G 431]*
>
> Luego, el mapa: el píxel de cada muestra se calcula una sola vez, y en cada fotograma OpenCV solo
> tiene que leerlo. Eso es remap. *[Ctrl+G 436]*
>
> Y aquí, cuántos píxeles de imagen hay entre muestra y muestra. *[Ctrl+G 1198]* Si bajan de 0,2, el
> programa avisa al arrancar: es el límite de aliasing del vídeo 3. El Shimoda tenía 2. Holgado.

---

## 5. Por dónde viaja un fotograma — 5:30 a 7:00

**Archivo:** `stiv_directo.py`

**Haz:**

| `Ctrl+G` | Qué se ve | Qué señalar |
|---|---|---|
| 706 | `class Lector` | líneas 714 a 717 (la cola de 150) |
| 774 | reconexión | líneas 774 y 775 |
| 468 | `Geometria.procesar` | líneas 469 a 471 |
| 791 | `class Buffers` | líneas 792 a 794 |
| 234 | `ESCALAS` | línea 234 |
| 845 | `class Medidor` | línea 846 |
| 1307 | huecos y saltos de PTS | líneas 1307 a 1322 |
| 1328 | entrega al Medidor | líneas 1328 a 1332 |

**Di:**

> *[Ctrl+G 706]*
> Ahora, el camino de un fotograma. Varias partes trabajan a la vez, cada una en un hilo: un trozo del
> programa que corre en paralelo.
>
> El Lector solo lee fotogramas y los mete en una cola de 150, unos cinco segundos. Con 600, la
> memoria llegaba a 1,3 gigas: demasiado para una Raspberry. *[Ctrl+G 774]* Si el directo se corta,
> vuelve a conectar solo. *[Ctrl+G 468]*
>
> En el hilo principal, "procesar" pasa el fotograma a gris y lo suaviza contra el aliasing, pero solo
> en el recuadro que tocan las líneas. En la Raspberry, suavizar la imagen entera era casi todo el
> coste. *[Ctrl+G 791]*
>
> Buffers guarda las filas en tres escalas de tiempo. *[Ctrl+G 234]* Diez segundos, fotograma a
> fotograma; treinta, con una fila cada 0,133 segundos; y sesenta, con una cada medio segundo.
> *[Ctrl+G 845]*
>
> El Medidor va en otro hilo porque medir cuesta mucho más que un fotograma: el comentario dice unos
> 140 milisegundos, y llega un fotograma cada 33. *[Ctrl+G 1307]*
>
> Y el tiempo. Cada fotograma trae su marca de tiempo, el PTS. El STI necesita filas a intervalos
> iguales: si falta un fotograma, se repite la última fila. Si el tiempo salta más de un segundo, o
> va hacia atrás porque la cámara se ha reiniciado, se vacía el STI y se vuelve a anclar el reloj.
> *[Ctrl+G 1328]* Cada segundo, si el Medidor está libre, recibe las filas.

---

## 6. La medida — 7:00 a 8:45

**Archivo:** `stiv_directo.py`

**Haz:**

| `Ctrl+G` | Qué se ve | Qué señalar |
|---|---|---|
| 574 | `construir_stis` | líneas 584 a 590 (normalización) |
| 591 | actividad | líneas 591 a 595 |
| 525 | `pendiente_tensor` | líneas 525 a 531 (docstring) |
| 200 | `ACTIVIDAD_MIN` | líneas 200 a 203 |
| 534 | máscara por píxel | líneas 534 a 536 |
| 555 | coherencia y mediana | líneas 555 y 556, luego 565 a 570 |
| 643 | `cascada` dentro de `medir` | líneas 643 a 662 |
| 676 | velocidad y motivos de rechazo | líneas 677 a 684 |

**Di:**

> *[Ctrl+G 574]*
> La medida. construir_stis resta a cada posición su media en el tiempo y la divide por lo que varía.
> Lo que no se mueve, como piedras, reflejos fijos o hierba, desaparece sin ningún parámetro.
> *[Ctrl+G 591]* Y calcula la actividad: cuánto cambia cada punto entre dos fotogramas reales
> seguidos. *[Ctrl+G 525]*
>
> pendiente_tensor mide la inclinación con el tensor de estructura: una cuenta que mira hacia dónde
> cambia más la imagen; la raya va en perpendicular. Se hace por bloques de 48 por 48.
> *[Ctrl+G 200]*
>
> Esto es clave. El compresor de YouTube, el códec, congela el agua lisa: en el STI, rayas verticales
> perfectas, velocidad cero con mucha coherencia. La trampa del vídeo 3. Pero el agua congelada tiene
> actividad exactamente 0,00, y la que tiene textura, de 0,7 a 5,6. El umbral es 0,5.
> *[Ctrl+G 534]* Se aplica píxel a píxel: lo congelado no cuenta. *[Ctrl+G 555]*
>
> La respuesta es la mediana de los bloques, ponderada por su coherencia: un bloque raro no manda.
> *[Ctrl+G 643]*
>
> medir decide. Cada estación prueba la escala de 10 segundos; si el agua sale demasiado lenta o sin
> textura, baja a la de 30, y luego a la de 60. En las lentas, una raya casi horizontal se rechaza
> como "ambiguo": puede ser agua rápida mal muestreada. *[Ctrl+G 676]*
>
> La velocidad es la pendiente por DS, entre el tiempo por fila. Motivos de rechazo: "coherencia",
> bajo 0,40; "sin_textura", menos de 6 bloques activos; "lento"; "ambiguo"; "v_max", sobre el tope; y
> "fuera_de_campo", si menos del 80 % de la línea cae en la imagen.

---

## 7. Problemas ya resueltos — 8:45 a 9:55

**Archivo:** `stiv_directo.py`

**Haz:**

| `Ctrl+G` | Qué se ve | Qué señalar |
|---|---|---|
| 196 | fotogramas duplicados | líneas 196 a 199 |
| 239 | modo noche | líneas 240 a 244, luego 251 y 259 |
| 667 | reintento con motas | líneas 668 a 675 |
| 604 | `filtro_direccional` | líneas 605 a 610 |
| 141 | el caso del Shimoda | líneas 141 a 147 |

**Di:**

> Para acabar, problemas ya resueltos. *[Ctrl+G 196]* Los fotogramas repetidos de YouTube: con ellos
> el STI se vuelve una escalera. En una prueba con pendiente 2,5, el tensor daba 3,15, un 26 % de
> más. Por eso, una fila por fotograma real. *[Ctrl+G 239]*
>
> La noche. Si la imagen pierde el color o se oscurece, pasa a modo noche: un top-hat, que es un
> filtro que deja solo los puntitos más brillantes que su entorno, y fuera los destellos de las
> farolas. De noche hay que comprobarlo con la cámara real; por eso cada cámara tiene "medir_noche".
> *[Ctrl+G 667]*
>
> De día, una estación que falla se reintenta con ese mismo realce. Así se miden burbujas sueltas
> junto a un muro en sombra. *[Ctrl+G 604]*
>
> Y el filtro direccional. A 15 fotogramas por segundo, en agua rápida, las ondas pueden parecer ir
> hacia atrás, como las ruedas en el cine. El filtro borra lo que va aguas arriba. *[Ctrl+G 141]* En
> el Shimoda, en 90 segundos, pasó de entre 0 y 6 medidas aceptadas a más de 150. Va por cámara,
> porque impone el sentido del flujo.

---

## 8. Cierre — 9:55 a 10:30

**Archivo:** `README.md`

**Haz:**

1. Abrir la pestaña de `README.md`. `Ctrl+G` → **364** ("Limites conocidos").
2. Señalar las líneas 366 a 368 (la noche y ALIAR).
3. Señalar la línea 377 ("Escala supuesta… la mayor incertidumbre").

**Di:**

> Resumo. El programa lee el directo, construye un STI por estación, mide la inclinación de las rayas
> y descarta lo que no se puede creer. Y todo se puede revisar en pantalla.
>
> Lo que falta lo dice el propio README. *[señalar 366 a 368]* La noche hay que comprobarla con la
> cámara de ALIAR. *[señalar 377]* Y la escala es un supuesto: es, de lejos, la mayor incertidumbre.
>
> En el vídeo 5 cierro las dos cosas: la validación, pasando este mismo código por vídeos con
> mediciones de campo, y la instalación en la Raspberry Pi. Gracias.

---

## Cifras a mano

| Lo que se dice | Valor | De dónde sale |
|---|---|---|
| Estaciones | 9 | `stiv_directo.py` l. 184 (`N_ESTACIONES = 9`); imagen, cabecera "9/9 estaciones" |
| Mediana de la sección (Shimoda) | 1,091 m/s, 9 de 9 | `ultima_vista.png`, cabecera; `salidas/shimoda/medidas_directo.csv`, últimas 9 filas (mediana de 0.5199 … 1.5115 = 1.0913) |
| Estación 0 | +0,520 m/s, c 0,52, b 8, escala 10 s | `ultima_vista.png`, primera etiqueta del panel; CSV, última medida de la estación 0 (0.5199, 0.517, 8) |
| Mínimo de bloques activos | 6 | l. 216 (`N_BLOQUES_MIN = 6`) |
| Tamaño del programa | ~1400 líneas | `stiv_directo.py` tiene 1435 |
| Guardar imagen sin pantalla | `--vista-cada 30` | l. 23–24 |
| Medidas supuestas del Shimoda | 12 × 5 m | l. 139; `config_stiv_directo.json` l. 23–24 |
| `v_esperada` del Shimoda | 0,6 m/s | l. 140 |
| Tope de velocidad | 3 × `v_esperada` (1,8 m/s en el Shimoda; no se dice) | l. 311; JSON `V_MAX_FISICA` 1.8 |
| `escala_verificada` | false | l. 395; `config_stiv_directo.json` l. 25 |
| Fotogramas de la cámara / de YouTube | 15 / 30 | l. 192–193; `fps_camara` 15.0 en l. 147 |
| `k_real` | 2 | l. 421 (30 / 15) |
| DS del Shimoda | 4 cm | l. 422 y 424: 0,6 m/s × (2/30) s = 0,04 m |
| Rayas a | 45 grados | l. 423 |
| Margen junto a cada orilla | 6 % | l. 185 (`MARGEN_ORILLA = 0.06`) |
| Líneas por banda | 7 | l. 186 (`LINEAS_BANDA = 7`) |
| Límite de aliasing | 0,2 px de imagen por muestra | l. 1198–1199 |
| Píxeles por muestra (Shimoda) | 2 (la cabecera dice 2.00) | `ultima_vista.png`, segunda línea de la cabecera |
| Cola del Lector | 150 fotogramas ≈ 5 s; con 600, 1,3 GB | l. 714–717 |
| Escalas de tiempo | 10 s; 30 s con fila cada 0,133 s; 60 s con fila cada 0,5 s | l. 234 |
| Coste de una medida / intervalo entre fotogramas | ~140 ms / 33 ms | l. 846 (ver Notas: hoy cuesta más) |
| Salto que vacía el STI | más de 1 s, o tiempo hacia atrás | l. 1308–1315 |
| Medida cada | 1 s | l. 189 (`PASO_MEDIDA_S = 1.0`), l. 1328 |
| Bloques del tensor | 48 × 48, solape del 50 % | l. 190 |
| Actividad: agua congelada / con textura / umbral | 0,00 / 0,7–5,6 / 0,5 | l. 200–203 |
| Coherencia mínima | 0,40 | l. 220 |
| Cobertura mínima | 80 % | l. 681 (`cobertura[i] < 0.8`) |
| Escalas siguientes | 30 y 60 s | l. 234; cascada l. 643–662 |
| Duplicados en STI de prueba | 2,5 → 3,15, +26 % | l. 198 |
| Filtro direccional en el Shimoda | de 0–6 a 156–162 medidas aceptadas en 90 s ("más de 150") | l. 143–146 |
| Fotogramas por segundo de la cámara | 15 | l. 141–147 (comentario y `fps_camara`) |

## Notas para quien graba

- **Hay dos carpetas con el mismo nombre.** `analisis_kurome_directo_stiv/` existe también en la raíz
  del workspace, con otros números de línea. Abrir siempre la de
  `videos_explicativos/video4_programa_en_directo/`. Con `Ctrl+P` salen las dos: mirar la ruta.
- **`Ctrl+G` no funciona en la pestaña de la imagen.** Cambiar antes a la pestaña del `.py`.
- **El 140 ms está desfasado.** El comentario de la l. 846 dice ~140 ms, pero el `README.md` (l. 253
  y 280) dice que, con las tres escalas y el reintento con motas, la medida pasó a ~0,3 s y luego a
  ~0,7 s en este PC. Por eso el guion dice "el comentario dice". La idea no cambia: medir cuesta mucho
  más que los 33 ms entre fotogramas.
- **No bajar más allá de la l. 25 del JSON del Shimoda.** El bloque `"parametros"` es una foto antigua:
  le faltan `FRACCION_ACTIVA`, `BRILLO_NOCHE`, `FILTRO_DIRECCIONAL` y `MEDIR_NOCHE`. Para las cámaras
  de `CAMARAS` esos valores salen del código (l. 283–284), no del JSON; el JSON sí manda en el
  cuadrilátero y las medidas (l. 390–393).
- **El comentario de la l. 88–89 dice "en las dos camaras"**, pero hoy hay cuatro. No señalarlo.
- **La cifra del Shimoda no es una sola.** La imagen dice 1,091 m/s con 9 de 9; el comentario de las
  l. 145–146 dice 0,94–1,00 m/s en otra grabación, y el README (l. 286–287) habla de las estaciones
  4–8 a ~1,35 m/s antes del filtro. Son momentos distintos, con escala supuesta. En el vídeo solo se
  dice el de la imagen.
- **La cabecera de la imagen dice t=17.2s** y el CSV 16.97 s: la imagen se guarda al salir, un poco
  después de la última medida. No es un error.
- **Las flechas de la vista directa apuntan a la izquierda** (en el Shimoda el agua va hacia el
  puente); en la rectificada siempre van a la derecha. Si alguien lo nota, esa es la razón.
- Las líneas 1050–1052 (la etiqueta del panel) son largas: con el zoom alto no caben. El guion no las
  enseña.
- Tiempos: ~1550 palabras habladas; a ritmo tranquilo salen unos 10 min y medio. Si vas largo, lo
  primero que sobra es la frase del remap (sección 4) y la de las burbujas junto al muro (sección 7).
- El salto de PTS que vacía el STI se descubrió cortando a propósito un servidor RTSP de prueba (lo
  dice el comentario de las l. 1309–1311). No está en el texto hablado por tiempo; si sobra tiempo,
  se puede añadir en la sección 5.
