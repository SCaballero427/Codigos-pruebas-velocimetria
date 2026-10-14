# Vídeo 3 — Lo que enseñaron los casos difíciles

**Duración prevista:** unos 10 min 45 s (≈ 1600 palabras habladas, más unas 20 del paso opcional, y las pausas de navegación).
**Toma:** una sola, sin edición, navegando VS Code.

## Archivos que se abren, en este orden (10 pestañas)

Todas las rutas son relativas a `videos_explicativos/video3_casos_dificiles/`.

| # | Archivo | Para qué |
|---|---|---|
| 1 | `analisis_boneyard_stiv/salidas/fig5_control_calidad.png` | la trampa de los muros |
| 2 | `analisis_boneyard_stiv/stiv_interactivo.py` | el cuadrilátero puesto a mano |
| 3 | `analisis_hommerich_stiv/README.md` | solvePnP, remap y el caudal |
| 4 | `analisis_bradano_stiv/salidas/fig8_comparacion.png` | STIV frente a la referencia |
| 5 | `analisis_arrow_stiv/salidas/fig5_rescate.png` | curva de decorrelación y las 9 variantes |
| 6 | `analisis_arrow_stiv/Arrow_STIV_pipeline.ipynb` | el árbitro PIV (solo una búsqueda) |
| 7 | `analisis_canal_riego_stiv/salidas/fig2_realce.png` | el top-hat contra los macrobloques |
| 8 | `analisis_canal_riego_stiv/README.md` | bloques con señal, densidad, focal, PTV |
| 9 | `analisis_canal_lejano_stiv/README.md` | el experimento de alcance |
| 10 | `analisis_canal_lejano_stiv/salidas/sti_lejos_N1.png` | la imagen espacio-tiempo lejana |

Opcional (fuera de VS Code): `analisis_canal_lejano_stiv/salidas/video_alcance.mp4` con el reproductor del sistema.

## Antes de grabar

1. Cerrar todas las pestañas: `Ctrl+K W`.
2. Abrir los 10 archivos de la tabla **en ese orden**, desde el explorador de VS Code (clic en cada uno). Así las pestañas quedan de izquierda a derecha en el orden del guion y basta con hacer clic en la siguiente.
3. Los `README.md` deben abrirse **como texto** (no en vista previa), para que funcione `Ctrl+G`. Si se abre la vista previa, clic derecho en el archivo → *Abrir con…* → *Editor de texto*.
4. Subir el zoom: `Ctrl +` dos o tres veces, hasta que se lea bien en la grabación.
5. **No ejecutar ninguna celda.** Si VS Code pide elegir kernel al abrir el notebook, cerrar el aviso e ignorarlo. Todo lo que se enseña son salidas ya guardadas.
6. Activar "No molestar" en Windows y cerrar notificaciones.
7. Si te equivocas, di "me corrijo" y sigue. No se corta.

**Cómo navegar:**
- En `.py` y `.md`: `Ctrl+G`, escribir el número de línea, `Enter`.
- En el `.ipynb`: `Ctrl+F` y el texto exacto que indica el guion (aparece **una sola vez** en ese notebook; comprobado).
- En los `.png`: clic en su pestaña (ya abiertos en el paso 2). Si se cerró alguno, volver a abrirlo desde el explorador.

---

## 0. Presentación — 0:00 a 0:35

**Archivo:** ninguno nuevo (pestaña 1 abierta de fondo).

**Haz:** nada; hablar a cámara con la pestaña 1 visible.

**Di:**

> Hola. Este es el tercer vídeo de la serie.
> En el anterior vimos STIV sobre un caso fácil: un dron mirando en vertical a un canal con mucho trazador, es decir, con espuma y restos flotando que la cámara puede seguir.
> Recuerdo la idea en una frase. STIV toma una línea en la dirección del agua en cada fotograma y las apila. Sale una imagen espacio-tiempo, y la inclinación de sus rayas es la velocidad.
> Hoy llevo STIV a casos difíciles. Son cinco, y de cada uno saco una sola lección. Todas acabaron dentro del programa en directo del vídeo cuatro.

---

## 1. Boneyard Creek: una cámara sin medidas y la trampa de los muros — 0:35 a 3:05

**Archivo:** pestaña 1, `analisis_boneyard_stiv/salidas/fig5_control_calidad.png`; luego pestaña 2, `analisis_boneyard_stiv/stiv_interactivo.py`.

**Haz:**
1. Con la figura en pantalla, señalar con el ratón el panel **derecho** y los tres puntos rojos de abajo a la derecha (est 0, est 19, est 20).
2. Señalar el panel **izquierdo**: las barras rojas y la línea discontinua de `CONTRASTE_MIN = 1.5`.
3. Clic en la pestaña 2. `Ctrl+G` → `5`. Dejar visibles las líneas 5 a 9.
4. `Ctrl+G` → `15`. Señalar las líneas 15 a 20.
5. `Ctrl+G` → `145`. Señalar la línea 150 (`cv2.getPerspectiveTransform`).

**Di:**

> Primer caso: Boneyard Creek, un arroyo en Illinois. Es una cámara fija del Servicio Geológico de Estados Unidos, que mira el cauce en oblicuo, en ángulo y no desde arriba.
> Lo difícil es que el sitio no tiene ni una medida: ni ancho, ni sección, ni puntos de control.
> Sin una longitud conocida no hay metros. Lo que sí hay son las hiladas de piedra de los muros. Son paralelas al canal, y en la imagen se juntan en un punto: el punto de fuga. Con él se calcula una homografía, una transformación que endereza la imagen como si la viéramos desde arriba.
> El resultado es correcto salvo una constante. Por eso la velocidad sale en una unidad rara: alturas de cámara por segundo. La mediana fue 0,2427, en 15 de 21 estaciones.
>
> Pero la lección está en esta figura. A la derecha, cada punto es una estación. En horizontal, la coherencia: un número de cero a uno que dice lo limpias y paralelas que son las rayas.
> Mirad los puntos rojos de abajo a la derecha. Son estaciones sobre los muros. Coherencia de 0,74 y 0,76, de las más altas de la sección. Y velocidad cero.
> Un muro quieto deja una raya vertical perfecta, y el filtro por coherencia, aquí en 0,40, lo aprueba.
> La solución está a la izquierda: el contraste temporal, cuánto cambia cada punto con el tiempo. El muro no cambia. Los muros quedan por debajo de 1, el agua aceptada va de 5,5 a 23, y el umbral está en 1,5.
> Primera lección: coherencia alta no es medida buena. Hace falta un segundo filtro.
>
> Una cosa más. El punto de fuga es frágil. Línea cinco: si está mal, todo lo de detrás está mal, y no se ve.
> Por eso hice esta herramienta. Línea quince: se arrastran a mano las cuatro esquinas de un cuadrilátero que en la realidad es un rectángulo sobre el agua, y se le dan sus medidas; aquí, unos seis metros de ancho.
> Y en la línea ciento cincuenta, una sola llamada de OpenCV convierte esas cuatro esquinas en la rectificación. Sin focal y sin punto de fuga. Si el cuadrilátero está mal, el canal sale torcido y se ve al momento.
> Ese cuadrilátero a mano es justo lo que usa el programa en directo.

---

## 2. Hommerich: la geometría completa, por fin metros — 3:05 a 4:05

**Archivo:** pestaña 3, `analisis_hommerich_stiv/README.md`.

**Haz:**
1. `Ctrl+G` → `44`. Señalar las líneas 44 y 45 (reproyección 0.56 px).
2. Bajar hasta las líneas 50 a 52 (`remap`).
3. `Ctrl+G` → `93`. Señalar las líneas 93 a 95 (tabla de resultado).
4. `Ctrl+G` → `106`. Señalar las líneas 106 a 107.

**Di:**

> Segundo caso, corto. El río Geul, en Hommerich, Países Bajos. Otra cámara oblicua, pero aquí el conjunto de datos lo trae todo: la calibración de la cámara, su distorsión y seis puntos de control medidos con GPS de precisión.
> Con eso, la función solvePnP de OpenCV calcula dónde está la cámara y hacia dónde mira. Al reproyectar los puntos, el error es de 0,56 píxeles de mediana.
> La distorsión es fuerte: la lente curva las rectas, el efecto barril. Una homografía no puede deshacer eso. Así que la imagen se rectifica píxel a píxel con remap, una tabla que dice de dónde sale cada píxel.
> Línea noventa y tres, el premio: metros. Velocidad superficial mediana de 0,943 metros por segundo, y caudal de 13,68 metros cúbicos por segundo.
> Pero, línea ciento seis: no hay aforo independiente. Nada valida ese número. Un número sin contraste es solo un número.

---

## 3. Bradano y Arrow: sin trazador no hay medida — 4:05 a 6:45

**Archivo:** pestaña 4, `analisis_bradano_stiv/salidas/fig8_comparacion.png`; pestaña 5, `analisis_arrow_stiv/salidas/fig5_rescate.png`; pestaña 6, `analisis_arrow_stiv/Arrow_STIV_pipeline.ipynb`.

**Haz:**
1. Pestaña 4. Señalar el panel izquierdo: línea negra (referencia), línea roja (STIV) y las dos cruces de los extremos. Luego el título del panel derecho (`r = +0.996, RMSE = 0.068 m/s`).
2. Pestaña 5. Señalar primero el panel derecho (las 9 barras, todas lejos de la línea discontinua de 0.7). Luego el izquierdo: curva azul y curva roja.
3. Pestaña 6. `Ctrl+F` → `coinciden hasta 3 cm/s` → `Enter`. Queda resaltado el punto 3 de **Conclusiones**. Cerrar la búsqueda con `Esc`.

**Di:**

> Tercer bloque: dos ríos del conjunto HARMONIOUS, una comparación europea de técnicas de velocimetría. Los vídeos vienen ya enderezados y con escala. Solo queda el método.
>
> El río Bradano, en Italia. Dron cenital. El agua sale casi negra, con un brillo medio de 0,12 sobre 255. Solo se ven partículas brillantes sueltas, y una línea de un píxel casi nunca pisa ninguna.
> La solución fue una banda: siete líneas paralelas, cada una normalizada por separado y luego promediadas.
> Y el filtro cambió otra vez. La estación de la orilla pisa grava: coherencia 0,82 y velocidad casi cero. La trampa de Boneyard. Pero aquí la grava es lo que más varía, así que el contraste no sirve. Separa el brillo: el agua no pasa de 0,42 y la grava da 12,34.
> El resultado, en esta figura. En negro la referencia, en rojo STIV. Mide 5 de las 7 verticales. Sesgo, el error medio, de menos 3,1 por ciento. Error típico de 0,068 metros por segundo. Y una correlación de 0,996. Las dos cruces son las orillas, sin partículas.
>
> Ahora el River Arrow, en Inglaterra. Dos vídeos idénticos de una GoPro: mismo río y mismo encuadre. Solo cambia que en uno echaron trazador al agua. Misma configuración exacta para los dos.
> Sembrado: 44 de 49 estaciones. Sin sembrar: cero.
> A la derecha, nueve intentos de rescatarlo. Ninguno llega al umbral.
> El porqué está a la izquierda: la curva de decorrelación, cuánto dura el dibujo de la superficie de un fotograma a otro. El sembrado, en azul, empieza en 0,72 y baja despacio. El sin sembrar, en rojo, está en 0,06 ya en el salto más corto, y es plano. No hay nada que seguir. De hecho, la grava quieta de la orilla varía más que el agua.
>
> Un detalle más. Sembrado, STIV acierta la media, un 6,7 por ciento por debajo, pero no la forma del perfil. ¿Culpa de STIV?
> Lo arbitré con un PIV, otro método sin una línea de código en común. El PIV discrepa de la referencia igual que STIV. Y entre ellos dos coinciden hasta 3 centímetros por segundo, con una correlación de 0,97. Lo más probable es que la referencia no mida lo mismo que la superficie.
> Lección doble: sin trazador no hay medida. Y cuando algo no cuadra, un árbitro independiente dice de quién es la culpa.

---

## 4. El canal de riego grabado con WhatsApp, y hasta dónde llega STIV — 6:45 a 9:55

**Archivo:** pestaña 7, `analisis_canal_riego_stiv/salidas/fig2_realce.png`; pestaña 8, `analisis_canal_riego_stiv/README.md`; pestaña 9, `analisis_canal_lejano_stiv/README.md`; pestaña 10, `analisis_canal_lejano_stiv/salidas/sti_lejos_N1.png`.

**Haz:**
1. Pestaña 7. Señalar el panel central (mosaico de bloques) y después el derecho (rayas limpias).
2. Pestaña 8. `Ctrl+G` → `79`. Señalar las líneas 79 a 83.
3. `Ctrl+G` → `232`. Señalar la tabla de las líneas 232 a 236.
4. `Ctrl+G` → `196`. Señalar la tabla de focales (196 a 202) y la línea 204 (`+52 %`).
5. `Ctrl+G` → `292`. Señalar la línea 292.
6. Pestaña 9. `Ctrl+G` → `22`. Señalar las líneas 22 y 23.
7. `Ctrl+G` → `29`. Señalar la tabla de las líneas 29 a 33.
8. Pestaña 10 (la imagen espacio-tiempo lejana). Dejarla unos segundos.
9. Volver a la pestaña 9. `Ctrl+G` → `61`. Señalar la tabla de las líneas 61 a 64.
10. `Ctrl+G` → `149`. Señalar las líneas 149 a 151.
11. *(Opcional, solo si vas bien de tiempo)*: en el explorador de VS Code, clic derecho sobre `analisis_canal_lejano_stiv/salidas/video_alcance.mp4` → *Revelar en el Explorador de archivos* → abrirlo con el reproductor del sistema, dejarlo correr 10 s y volver a VS Code. VS Code no lo reproduce.

**Di:**

> Cuarto caso, el más pobre de todos. Un vídeo de móvil, enviado por WhatsApp, de un canal de riego. Sin medidas ni aforo. Y muy comprimido: 661 kilobits por segundo.
> En el centro, la imagen espacio-tiempo en crudo. No es agua: es un mosaico de macrobloques, los cuadrados de dieciséis píxeles en los que el compresor divide la imagen.
> Pero había señal: restos vegetales flotando, de 2 a 4 píxeles. Un filtro top-hat de 5 píxeles se queda solo con lo que brilla más que su entorno inmediato. Un macrobloque es plano, así que desaparece. A la derecha, el resultado: rayas rectas y limpias.
>
> Línea setenta y nueve: casi todos los bloques solo ven el fondo quieto, otra vez la raya vertical, y salía cero en las 15 estaciones. Así que se mide solo en el 15 por ciento de bloques más brillantes: entre el 11 y el 21 por ciento contienen una partícula.
> Línea doscientos treinta y dos: el filtro aquí es la densidad de trazador, cuántas partículas pasan. Ni el contraste ni el brillo separaban. Quedan 6 de 15 estaciones, todas en el tercio derecho, por donde flotan los restos.
> Línea ciento noventa y seis: la mayor incertidumbre no es el algoritmo, es la focal, el zoom de la cámara. WhatsApp la borra y hubo que suponerla. De 600 a 1000 píxeles de focal, la velocidad cambia un 52 por ciento. Eso solo lo arregla una medida real: una cinta métrica.
> Y línea doscientos noventa y dos, el árbitro. Seguimiento de partículas una a una. Correlación de 0,984 y sesgo de más 13 por ciento. La forma coincide; ese 13 por ciento queda abierto.
>
> Y un experimento con el mismo vídeo: hasta dónde llega STIV canal arriba. Línea veintidós: es la misma agua cerca y lejos, así que tiene que dar la misma velocidad.
> Línea veintinueve. Cerca, 6 de 6 estaciones, en torno a 0,06. Lejos, hasta 1,86: unas 20 veces más, con signos que cambian entre vecinas. Y coherencia de 0,97 a 0,99, la más alta de todo el caso.
> Así es la imagen espacio-tiempo lejana: una estera de trazos casi horizontales. Muy coherente y completamente falsa.
> Línea sesenta y uno, el porqué. El paso de muestreo, DS, es la distancia entre muestras de la línea. Lejos valía 0,04 píxeles de imagen: 25 veces por debajo de un píxel. Eso produce aliasing, un patrón falso que nace de muestrear mal.
> Para comprobarlo tomé un fotograma de cada veinte. Una señal real no cambiaría. Esta cambió de signo, cayó unas veinte veces y la coherencia se hundió hasta 0,33.
> Línea ciento cuarenta y nueve, la regla: paso de muestreo de al menos 0,2 píxeles de imagen. Es pura geometría y se calcula antes de medir nada.

*(Si pones el vídeo opcional, añade:)*

> En este vídeo las flechas están coloreadas por coherencia, no por velocidad. El rojo, la mejor nota, cae justo donde la medida es absurda.

---

## 5. Cierre: lo que heredó el programa en directo — 9:55 a 10:45

**Archivo:** ninguno nuevo (dejar la pestaña 9 en pantalla).

**Haz:** nada; hablar a cámara.

**Di:**

> Resumo lo que me llevé de estos casos, porque todo acabó en el programa en directo.
> Uno: coherencia alta no es medida buena. Un muro, una orilla o un muestreo malo dan rayas perfectas. Siempre hace falta un segundo filtro.
> Dos: sin trazador no hay medida. Ningún algoritmo inventa lo que no está grabado.
> Tres: el alcance tiene un límite, y se calcula antes de medir.
> Cuatro: si no hay datos de campo, un árbitro independiente, otro algoritmo sobre el mismo vídeo.
> Y cinco: la geometría, a mano y a la vista, con un cuadrilátero sobre el agua y sus medidas reales.
> En el próximo vídeo abro el programa en directo que va a correr en la cámara fija de ALIAR, y veremos dónde está cada una de estas lecciones. Gracias.

---

## Cifras a mano

| Cifra que se dice | Qué es | De dónde sale |
|---|---|---|
| 0,2427 alturas de cámara/s | velocidad mediana, Boneyard | `Boneyard_STIV_pipeline.ipynb`, salida de la Parte 5 (y `salidas/velocidad_resumen.csv`) |
| 15 de 21 estaciones | aceptadas, Boneyard | misma salida de la Parte 4b/5 |
| 0,74 y 0,76 | coherencia de las estaciones de muro (0.735, 0.756, 0.756) | salida de la Parte 4b; `fig5_control_calidad.png` panel derecho |
| velocidad cero en los muros | −0.0006, −0.0003, 0.0000 | salida de la Parte 4b |
| umbral de coherencia 0,40 | `COH_MIN` | notebook, Parte 4b |
| muros < 1; agua aceptada 5,5 a 23; umbral 1,5 | contraste temporal (muros 0.00/0.94/0.87/0.74; aceptadas 5.49–23.46) | salida de la Parte 4b; `fig5` panel izquierdo |
| línea 5, 15, 150 | punto de fuga frágil, cuadrilátero, `getPerspectiveTransform` | `stiv_interactivo.py` líneas 5–9, 15–20, 145–150 |
| unos 6 m de ancho | ancho dado a mano, Boneyard | `stiv_interactivo.py` líneas 70–75 (y docstring 22–23) |
| 6 puntos de control | GCPs RTK, Hommerich | `analisis_hommerich_stiv/README.md` línea 26 y 36 |
| 0,56 px | reproyección mediana | README Hommerich línea 45; `config_stiv_hommerich.json` (0.555) |
| 0,943 m/s | v superficial mediana, Hommerich | README línea 94; JSON (0.9435) |
| 13,68 m³/s | Q mediana, Hommerich | README línea 95; JSON (13.683) |
| 0,12 sobre 255 | brillo medio del agua, Bradano | `Bradano_STIV_pipeline.ipynb`, celda de introducción |
| 7 líneas | banda, Bradano | salida de la Parte 3 ("Banda: 7 lineas paralelas…") |
| 0,82 y casi cero | estación 8: coherencia 0.818, v 0.005 m/s | salida de la Parte 4b |
| 0,42 y 12,34 | brillo máximo del agua (0.4230) y de la grava (12.3420) | tabla de salida de la Parte 4b |
| 5 de 7 verticales | medidas de las de validación | salida de la Parte 7; `salidas/resumen.csv` |
| −3,1 % | sesgo medio relativo (−3.08 %) | salida de la Parte 7; `resumen.csv` |
| 0,068 m/s | RMSE | salida de la Parte 7; `fig8_comparacion.png` |
| 0,996 | correlación r | salida de la Parte 7; `fig8_comparacion.png` |
| 44 de 49 / 0 de 49 | estaciones aceptadas, Arrow sembrado / sin sembrar | `Arrow_STIV_pipeline.ipynb`, salida de la Parte 4b y `salidas/resumen.csv` |
| nueve intentos, ninguno llega | variantes de rescate, 0 aceptadas en todas | salida de la Parte 4c; `fig5_rescate.png` panel derecho; `salidas/rescate_sin_sembrar.csv` |
| 0,72 (sembrado) | pico de correlación a 0,2 s (0.725) | salida de la Parte 4c; `salidas/decorrelacion.csv` |
| 0,06 (sin sembrar) | pico a 0,2 s (0.055) | ídem |
| la grava varía más que el agua | σ temporal 8.88 frente a 3.32 | salida de la Parte 4c |
| −6,7 % | media STIV sembrado frente a referencia (0.3891 vs 0.4172) | salida de la Parte 7 |
| 3 cm/s y 0,97 | STIV frente a PIV: RMSE 0.0339 m/s, r = +0.974 | salida de la Parte 7; Conclusiones punto 3 |
| 661 kb/s | bitrate del vídeo de WhatsApp | `analisis_canal_riego_stiv/README.md` línea 23 |
| 16 px (macrobloque), 2–4 px (restos), 5 px (top-hat) | tamaños | README canal líneas 58–61 |
| 15 estaciones a cero; 15 % de bloques; 11–21 % | selección de bloques por señal | README canal líneas 79–83 |
| 6 de 15, tercio derecho | estaciones aceptadas | README canal línea 28 y 250; `salidas/perfil_velocidades.csv` |
| 600 a 1000 px de focal, +52 % | barrido de focal | README canal líneas 196–204 |
| 0,984 y +13 % | PTV: r = +0.984, sesgo +13.1 % | README canal línea 292; `fig6_arbitro.png` |
| cerca 6 de 6, ~0,06 | banda cercana | `analisis_canal_lejano_stiv/README.md` línea 31; `salidas/alcance.csv` |
| hasta 1,86, unas 20 veces | banda lejana | README lejano líneas 33 y 35; `alcance.csv` (1.864) |
| 0,97 a 0,99 | coherencia lejana | README lejano línea 33; `alcance.csv` (0.973–0.985) |
| 0,04 px, 25 veces | DS lejano en px de imagen | README lejano línea 55; `alcance.csv` (0.036) |
| uno de cada veinte; hasta 0,33 | diezmado N = 20, coherencia 0.23–0.33 | README lejano líneas 61–66 |
| 0,2 px | regla de paso mínimo | README lejano línea 149 |

## Notas para quien graba

1. **Boneyard, prosa contra salida.** La celda Markdown de la Parte 4b del notebook dice que los muros dan "coherencia **0.99**"; la salida guardada dice **0.735–0.756**. El guion usa la salida (0,74 y 0,76) y por eso enseña la figura y no esa celda. No abrir esa parte del notebook en cámara.
2. **Boneyard, el "hueco de factor 5".** La misma celda habla de un hueco limpio de factor 5 en contraste; la estación 2 tiene contraste 1.98, dentro del hueco (la rechaza la coherencia). Por eso el guion dice "muros por debajo de 1, agua aceptada de 5,5 a 23" y no "factor 5".
3. **Boneyard, dos conjuntos de números.** `video_velocidad.py` (salida de la Parte 8) da contrastes algo distintos por estación (por ejemplo, 1.49 en la estación 1) y admite 17 de 21 por geometría y contraste. No se cita.
4. **`stiv_interactivo.py` no usa el mismo vídeo que el notebook**: su vídeo por defecto es `20171118-095500`, el notebook mide `20180610-082000`. Y `salidas/config_stiv_manual.json` guarda 6 × 6 m con 11 estaciones. En el guion solo se dice "unos seis metros de ancho", que es lo que pone el código.
5. **Bradano, 12.59 contra 12.34.** La Markdown de la Parte 4b y la tabla final dicen que la grava da brillo 12.59; la salida guardada dice 12.34. El guion usa 12,34. Además se rechazan **4** estaciones de 9 (0, 6, 7 y 8), pero solo 2 de ellas coinciden con verticales de validación; por eso se dice "5 de las 7 verticales".
6. **Arrow, 43 contra 44.** El notebook acepta **44 de 49** en el sembrado. El número 43 que aparece en la Parte 4c es otra cosa: la "referencia interna", con solo el criterio de coherencia. No mezclarlos.
7. **Arrow, una frase del notebook que no cuadra con su propia tabla.** La salida de la Parte 4c dice "El paso alto es el único que mueve la coherencia (0.196 → 0.452)"; en la tabla, 0.452 es la variante *paso alto + banda 30*, y el paso alto solo da 0.255 y además tiene la r más alta (+0.453). El guion no cita esa frase.
8. **Canal, focal.** El barrido de focal (`--barrer-focal`) usa 600 fotogramas, así que a F = 780 da 0.0548 y no el 0.0590 del resultado final. El guion solo cita el +52 %, que sale de esa tabla.
9. **Canal lejano, dos rangos de coherencia para N = 20.** La tabla de la línea 64 da 0.23–0.33 (tres estaciones); el párrafo de la línea 142 da 0.19–0.33 (las seis; el CSV dice 0.186–0.334). El guion dice "hasta 0,33", que vale para ambos.
10. **`sti_lejos_N1.png` no tiene título ni ejes.** Es una imagen espacio-tiempo en bruto: el guion solo dice "estera de trazos casi horizontales", que es como la describe el README (línea 71–72). No inventar qué estación es.
11. **Rutas de otra máquina.** Las salidas de los notebooks muestran rutas `C:\Users\Sergio\...` (el equipo donde se ejecutaron). Es normal; no se comenta.
12. El vídeo `video_alcance.mp4` no se ha reproducido al preparar el guion: la frase opcional sobre el color de las flechas sale del README del experimento (líneas 195–196). Si al verlo no se aprecia, omitirla.
