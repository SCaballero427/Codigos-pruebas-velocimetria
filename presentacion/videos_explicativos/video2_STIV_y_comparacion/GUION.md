# Vídeo 2 — STIV desde cero, y LSPIV frente a STIV

**Duración:** unos 10 minutos (unas 1450 palabras habladas), en una sola toma, sin edición. Si lees despacio o enseñas el vídeo opcional de la sección 7, puede irse a 11.

**Archivos que se abren, en este orden** (todas las rutas son relativas a
`videos_explicativos/video2_STIV_y_comparacion/`):

1. `STIV_desde_cero.ipynb`
2. `analisis_USGS_SMC_stiv/SMC_STIV_pipeline.ipynb`
3. `estabilizar_stiv.py`
4. `analisis_USGS_SMC_stiv/salidas/fig4_todas_las_sti.png`
5. `analisis_USGS_SMC_stiv/salidas/fig10_comparacion.png`
6. `analisis_USGS_SMC_stiv/video_velocidad.py`
7. *(Opcional, fuera de VS Code)* `analisis_USGS_SMC_stiv/salidas/video_velocimetria.mp4`

## Antes de grabar

- Cierra todas las pestañas: `Ctrl+K W`.
- Abre los archivos 1, 2, 3 y 6 en ese orden, para que queden como pestañas. Los PNG (4 y 5) se abren
  en el momento, desde el explorador lateral.
- Sube el zoom dos o tres veces (`Ctrl +`) hasta que el código se lea bien en la grabación.
- **No ejecutes ninguna celda.** Los dos cuadernos ya tienen guardados sus resultados y sus figuras.
  Si VS Code pide elegir un kernel, cierra el aviso y sigue.
- Activa "No molestar" en Windows y cierra correo y mensajería.
- Si te equivocas al hablar, di "me corrijo" y sigue. No pares la grabación.
- Deja ambos cuadernos con el principio a la vista (`Ctrl+Home` con el foco en el cuaderno).

**Cómo navegar:**

- En los `.py`: `Ctrl+G`, escribe el número de línea y `Enter`.
- En los `.ipynb`: haz clic en el margen del cuaderno (fuera de cualquier celda) para darle el foco,
  pulsa `Ctrl+F`, escribe el texto de búsqueda indicado, `Enter` y después `Esc`. Todos los textos de
  búsqueda de este guion se comprobaron: aparecen **una sola vez** en el código o el texto de su
  cuaderno y nunca en las salidas.
- Para ver la salida de una celda (texto o figura), haz scroll hacia abajo justo debajo de esa celda.
- Los PNG: clic en el archivo en el explorador lateral de VS Code.

---

## 1. De qué va este vídeo — 0:00 a 0:35

**Archivo:** `STIV_desde_cero.ipynb` (pestaña ya abierta, en la parte de arriba).

**Haz:** nada todavía. Deja a la vista el título del cuaderno.

**Di:**

> Hola. Este es el segundo vídeo de la serie.
> En el primero medimos el caudal de un canal del USGS con pyorc, que usa una técnica llamada LSPIV.
> Quedó un 1.4 % por encima del aforo, la medida de referencia hecha en el agua. Pero necesitó 13.7 gigas de memoria, y era una caja negra.
> Hoy, la alternativa que acabó siendo el método principal: STIV.
> Primero qué es; después, el mismo canal medido con STIV escrito desde cero; y al final, los dos lado a lado.

---

## 2. La idea de STIV, en lenguaje llano — 0:35 a 2:50

**Archivo:** `STIV_desde_cero.ipynb`

**Haz:**

1. `Ctrl+F` → `Si algo se mueve a lo largo` → `Enter`, `Esc`. Queda a la vista la explicación de la
   introducción. Señala con el ratón las dos viñetas "Eje horizontal… / Eje vertical…" que hay justo
   encima.

**Di:**

> Este cuaderno es mi primer STIV, sobre el río Ngwerere del vídeo uno.
> STIV significa velocimetría por imagen espacio-temporal. La idea es sencilla.
> Trazo una línea sobre el agua, en la dirección en la que corre.
> En cada fotograma leo los píxeles que hay debajo de esa línea, y apilo esas filas una debajo de otra.
> Sale una imagen nueva: en horizontal, la posición a lo largo de la línea; en vertical, el tiempo.
> A esa imagen la llamamos STI.

**Haz:**

2. `Ctrl+F` → `Paso 5: Visualizar una STI` → `Enter`, `Esc`. Haz scroll hacia abajo hasta la figura
   gris titulada "Imagen espacio-temporal (STI) — punto 3". Recorre con el ratón una de las rayas
   claras, de arriba a la izquierda hacia abajo a la derecha.

**Di:**

> Así se ve una STI de verdad. Fijaos en las rayas inclinadas.
> Cada raya es algo que flota: una burbuja, espuma. Lo llamamos trazador.
> Como baja con la corriente, en cada fila aparece un poco más a la derecha, y deja una raya inclinada.
> Ese es el truco: la inclinación de la raya es la velocidad.
> Raya casi vertical: agua lenta. Cuanto más se tumba, más rápido va.
> Todo el método se reduce a medir bien ese ángulo.

**Haz:**

3. `Ctrl+F` → `Jxt = np.mean(Gx * Gt)` → `Enter`, `Esc`. Queda a la vista la función
   `estimar_velocidad_stiv`. Señala primero las líneas de `Gt` y `Gx`, después las tres líneas
   `Jxx`, `Jtt`, `Jxt`, y por último `return ex / et`.

**Di:**

> Para medir el ángulo sin hacerlo a ojo uso el tensor de estructura. Suena complicado, pero no lo es.
> En cada punto miro cuánto cambia el brillo hacia los lados, Gx, y de una fila a la siguiente, Gt.
> Si sigo una raya, el brillo casi no cambia: siempre veo el mismo trazador. Si la cruzo, cambia mucho.
> El tensor resume esos cambios en una tablita de dos por dos, y su dirección de mínimo cambio es la de las rayas.
> De ahí sale la velocidad, en píxeles por fotograma.
> Además da gratis un número entre cero y uno, la coherencia, que dice cómo de clara es esa dirección.
> Uno: todas las rayas apuntan igual. Cero: solo hay ruido.
> Este tutorial aún no la usaba, y se apoyaba en pyorc para pasar a metros. En el canal, la coherencia será el control de calidad, y pyorc desaparece.

---

## 3. El mismo canal, con la misma configuración — 2:50 a 4:25

**Archivo:** `analisis_USGS_SMC_stiv/SMC_STIV_pipeline.ipynb`, después `estabilizar_stiv.py`.

**Haz:**

1. Pestaña `SMC_STIV_pipeline.ipynb`. `Ctrl+F` → `Que es STIV y en que se diferencia` → `Enter`, `Esc`.
   Baja un poco hasta la tabla "LSPIV (lo que hace pyorc) | STIV (este notebook)". Señala la fila
   **Memoria**.

**Di:**

> Ahora, el caso serio: el mismo vídeo de dron del canal del USGS del vídeo uno.
> La cámara mira desde arriba, en vertical; eso se llama vista cenital.
> Aquí no hay pyorc. OpenCV lee el vídeo, y todo lo demás está escrito en este cuaderno.
> La tabla resume la diferencia: LSPIV compara parches entre dos fotogramas y da un campo de flechas; STIV da una velocidad por línea.
> Y fijaos en la última fila, la memoria. Volveremos a ella.

**Haz:**

2. `Ctrl+F` → `FILA_AGUA_INF = 1463` → `Enter`, `Esc`. Señala `FILA_AGUA_SUP = 438`, `FILA_AGUA_INF = 1463`
   y `ANCHO_CANAL = 1.8288`. Después baja hasta la salida de la **celda siguiente**, donde pone
   `ESCALA = 1.7842 mm/px`, y señálala.

**Di:**

> Para que la comparación sea limpia, uso la misma configuración que el cuaderno de pyorc.
> Las mismas filas donde el agua toca cada muro, 438 y 1463, y el mismo ancho, 1.8288 metros.
> De ahí sale la escala: 1.78 milímetros por píxel. Y la misma sección del aforo, del mismo archivo.
> Así, si los resultados difieren, es por el algoritmo y no por la configuración.

**Haz:**

3. Pestaña `estabilizar_stiv.py`. `Ctrl+G` → `14`. Señala las líneas 16 a 23 ("Busca rasgos con
   esquinas marcadas… el error NO se acumula").
4. `Ctrl+G` → `156`. Señala la línea 159 (`p_ref = cv2.goodFeaturesToTrack(...)`).

**Di:**

> Antes de medir hay que quitar el temblor del dron, que se sumaría a la velocidad del agua.
> Este script lo hace solo con OpenCV.
> Busca puntos con esquinas marcadas fuera del agua, en el hormigón y el terreno, una sola vez, en el primer fotograma.
> Y sigue esos puntos hasta cada fotograma, comparando siempre con el primero, no con el anterior.
> Esa es la clave: encadenando fotogramas, los pequeños errores se irían sumando. Así no se acumulan.
> El resultado se guarda sin pérdida, para no meter ruido de compresión.

---

## 4. Cómo mide: paso de muestreo, antialias, bloques y calidad — 4:25 a 6:30

**Archivo:** `SMC_STIV_pipeline.ipynb`, con una parada en `fig4_todas_las_sti.png`.

**Haz:**

1. Pestaña `SMC_STIV_pipeline.ipynb`. `Ctrl+F` → `D_ESPERADO = V_ESPERADA * DT` → `Enter`, `Esc`.
   Sube unas líneas para señalar `V_ESPERADA = 0.95`. Luego baja hasta la salida de la celda y señala
   `17.74 px/fotograma`, `DS = 18 px` y `estelas a 44.6 grados`.

**Di:**

> Ahora, las decisiones del método. La primera: cada cuánto leo la línea.
> Le doy una velocidad estimada a ojo, 0.95 metros por segundo. A 30 fotogramas por segundo, el agua avanza unos 18 píxeles por fotograma.
> Así que leo un punto cada 18 píxeles, y las rayas quedan a 45 grados, donde un error de ángulo pesa menos.
> Leyendo píxel a píxel quedarían a 87 grados, y el mismo error pesaría 19 veces más.
> La salida lo confirma: rayas a 44.6 grados.

**Haz:**

2. Sin moverte, sube a la línea `SIGMA_ANTIALIAS = 0.5 * DS` y señálala. Después señala, más abajo en
   la misma celda, la línea `gris = cv2.GaussianBlur(gris, (0, 0), sigma)`.

**Di:**

> La segunda: antes de saltar píxeles, desenfoco un poco la imagen. Es el filtro antialias.
> Sin él aparecen dibujos falsos, con inclinaciones inventadas. Eso se llama aliasing.

**Haz:**

3. En el explorador lateral, abre `analisis_USGS_SMC_stiv/salidas/fig4_todas_las_sti.png`. Señala las
   verticales 5 a 8 (centro, rayas limpias) y luego la 1 y la 11.

**Di:**

> El resultado: trece STI, una por vertical del aforo. En el centro, rayas limpísimas.
> Junto a los muros, en la 1 y la 11, casi desaparecen: sombra, poca espuma y reflejos.

**Haz:**

4. Vuelve a la pestaña del cuaderno. `Ctrl+F` → `LADO_BLOQUE = 64` → `Enter`, `Esc`. Señala esa
   línea. Luego baja hasta el final de la celda, a la figura "La recta roja es lo que mide el tensor
   de estructura", y señala la leyenda "pendiente medida: 45.4 grados" y, encima de la figura, la
   línea `coherencia C = 0.9772`.

**Di:**

> La tercera: no aplico el tensor a la STI entera. La parto en bloques de 64 por 64 píxeles, solapados a la mitad.
> Mido cada bloque y me quedo con la mediana, dando más peso a los más coherentes.
> Así un solo reflejo brillante no puede imponer su ángulo.
> Abajo, la demostración en una vertical del centro: la recta roja es lo que mide el tensor. 45.4 grados, coherencia 0.977.

**Haz:**

5. `Ctrl+F` → `COH_MIN_ESTACION = 0.70` → `Enter`, `Esc`. Señala esa línea. Baja hasta la salida:
   `Verticales validas: 9 de las 11 medidas` y las dos líneas de las verticales 1 y 11. Sigue bajando
   hasta la figura "Perfil transversal de velocidad superficial" y señala la cruz roja de arriba a la
   derecha (vertical 11) y los dos cuadrados naranjas.

**Di:**

> Y el control de calidad: una vertical solo vale si su coherencia llega a 0.70.
> Pasan 9 de 11. Las dos que fallan son las pegadas a los muros.
> Mirad la 11: mide 1.34 metros por segundo, más que el centro del canal, que no pasa de 0.97. Imposible, y la coherencia lo caza sola.
> Las rechazadas toman el valor de la vertical medida más cercana: en la gráfica, cruces rojas lo medido, cuadrados naranjas el relleno.

---

## 5. El caudal, y la referencia al final — 6:30 a 8:00

**Archivo:** `SMC_STIV_pipeline.ipynb`, con una parada en `fig10_comparacion.png`.

**Haz:**

1. `Ctrl+F` → `ALFA = 0.92` → `Enter`, `Esc`. Señala la línea. **No leas el comentario de encima**
   (ver notas). Baja hasta la salida y señala `CAUDAL ESTIMADO POR STIV: Q = 1.4475 m3/s`.

**Di:**

> Con el perfil ya sale el caudal, con un paso más.
> La cámara solo ve la superficie, y el agua de abajo va más despacio por el roce con el fondo.
> Así que multiplico por un coeficiente, alfa, que aquí vale 0.92. Es el único número que no sale de la imagen, y es el mismo que usa pyorc.
> Multiplico por la profundidad, sumo de muro a muro, y salen 1.4475 metros cúbicos por segundo.

**Haz:**

2. `Ctrl+F` → `Q_AFORO = 1.4362` → `Enter`, `Esc`. Señala el comentario "Es la primera vez que
   aparecen en el notebook". Baja hasta la salida: señala `Diferencia : +0.8 %`. Sigue bajando a la
   celda siguiente, pasa la figura, y señala en su salida `Sesgo medio frente al ADV: -0.0040 m/s (-0.5 %)`
   y `RMSE: 0.0537 m/s`.

**Di:**

> Y solo ahora, en la última parte, abro la referencia: un aforo hecho dentro del agua con un ADV, un medidor acústico de velocidad.
> Dio 1.4362, con una incertidumbre declarada del 4.2 %. STIV queda un 0.8 % por encima.
> En las 9 verticales que STIV midió de verdad, el sesgo medio es de menos 0.5 %, y el error típico, unos 5 centímetros por segundo.
> Una advertencia honesta: el total depende de alfa. Con el 0.85 de manual saldría un 7 % por debajo.
> Por eso la referencia se abre al final, y no se vuelve atrás a ajustar nada.

**Haz:**

3. En el explorador lateral, abre `analisis_USGS_SMC_stiv/salidas/fig10_comparacion.png`. Señala en
   el panel izquierdo la curva negra discontinua (ADV) y la morada (STIV × 0.92). En el derecho,
   señala los puntos entre las líneas punteadas y luego el punto "2", fuera, abajo.

**Di:**

> A la izquierda, en negro el ADV y en morado STIV: casi pegados.
> A la derecha, vertical a vertical: todas dentro del más o menos 10 %, menos la 2.

---

## 6. Cuánto cuesta, y LSPIV frente a STIV — 8:00 a 8:55

**Archivo:** `SMC_STIV_pipeline.ipynb`

**Haz:**

1. Vuelve a la pestaña del cuaderno. `Ctrl+F` → `tabla_recursos = benchmark.tabla()` → `Enter`, `Esc`.
   Baja hasta la salida: señala `Tiempo total medido: 33.8 s` y `Pico de memoria del proceso: 869 MB`.
   Sigue bajando hasta la figura de barras y señala la barra azul larga y la tabla de debajo (columna
   `pct_tiempo`: 99.9 y 0.1).

**Di:**

> Ahora, los recursos. Todo el cálculo tardó 33.8 segundos, y el 99.9 % fue leer el vídeo 4K y desenfocar cada fotograma.
> El tensor, el corazón del método, tardó dos centésimas de segundo.
> Pico de memoria: 869 megas. STIV nunca guarda más de un fotograma: lee, toma sus líneas y lo tira.
> Los dos métodos lado a lado, mismo vídeo y misma configuración.
> pyorc, en el vídeo uno: 1.4 % por encima del aforo, unos 159 segundos y 13.7 gigas de pico.
> STIV: 0.8 % por encima, 34 segundos y menos de un giga.
> En precisión es un empate: los dos caen dentro del 4.2 % de incertidumbre del aforo.
> En coste no hay color: casi cinco veces más rápido y unas dieciséis veces menos memoria.

---

## 7. El vídeo entero, y la cota física — 8:55 a 9:55

**Archivo:** `analisis_USGS_SMC_stiv/video_velocidad.py`

**Haz:**

1. Pestaña `video_velocidad.py`. `Ctrl+G` → `1`. Señala las líneas 5 a 9 del docstring.
2. `Ctrl+G` → `83`. Señala las líneas 83 a 89 (el comentario y `V_MAX_FISICA = 3.0 * V_ESPERADA`).
   Después señala la línea 98, `VENTANA = 150`.

**Di:**

> Una última prueba. El cuaderno mide 250 fotogramas, unos 8 segundos.
> Este script repite el mismo STIV sobre los 22 segundos del vídeo, en ventanas de 5 segundos que se deslizan: 105 medidas.
> Y apareció algo nuevo. La vertical 11, la del muro en sombra, alguna vez coló una onda estacionaria:
> una ondulación que se queda quieta, no viaja con el agua, pero dibuja rayas muy limpias.
> Pasó la coherencia y daba 7 metros por segundo, en un canal que va a uno.
> Así que añadí una cota física: nada por encima de tres veces la velocidad esperada. Sale de mi estimación a ojo, no de la referencia.
> El resultado: caudal mediano 1.4493, y el 90 % de las ventanas entre 1.403 y 1.489. Lo mismo que el cuaderno.

**Haz (opcional, fuera de VS Code):** clic derecho sobre
`analisis_USGS_SMC_stiv/salidas/video_velocimetria.mp4` en el explorador → "Revelar en el Explorador
de archivos" → doble clic para abrirlo con el reproductor del sistema. Deja que corra 5 o 10
segundos mientras dices la frase de abajo, ciérralo y vuelve a VS Code. VS Code no reproduce este
archivo. Si no quieres salir de VS Code, sáltate este paso y la frase.

**Di (solo si enseñas el vídeo):**

> Así se ve: una flecha por vertical, que se mueve con el dron, y abajo el caudal en cada instante.

---

## 8. Conclusión y puente al vídeo 3 — 9:55 a 10:30

**Archivo:** el que esté abierto.

**Haz:** nada. Puedes dejar a la vista `video_velocidad.py`.

**Di:**

> Conclusión. En este canal STIV acierta igual que LSPIV, cuesta una fracción, y entiendo cada línea del código.
> Como su memoria no crece con la duración del vídeo, cabe en una Raspberry Pi, que es donde va a correr en ALIAR.
> Por eso pasó a ser el método principal.
> Pero hasta aquí todo ha sido fácil: cámara desde arriba y agua llena de espuma.
> En el próximo vídeo, los casos difíciles: cámaras inclinadas, vídeos sin medidas, agua sin trazador, un vídeo de móvil.
> Ahí es donde se aprendió de verdad. Nos vemos.

---

## Cifras a mano

| Lo que se dice | Valor | De dónde sale |
|---|---|---|
| Error de pyorc frente al aforo | +1.4 % | Vídeo 1. Coincide con `video1_LSPIV_pyorc/analisis_USGS_SMC_pyorc/salidas/caudal_resumen.csv` (1.4104 %) |
| Pico de memoria de pyorc | 13.7 GB | Vídeo 1. Coincide con el `benchmark_recursos.csv` del vídeo 1 (`get_piv`, 13670 MB) |
| Tiempo de pyorc | ~159 s | Vídeo 1. Suma de las etapas del `benchmark_recursos.csv` del vídeo 1 (159.08 s) |
| Filas del agua | 438 y 1463 | Parte 2 del cuaderno SMC (`FILA_AGUA_SUP`, `FILA_AGUA_INF`); `salidas/config_stiv.json`. La copia del cuaderno pyorc del vídeo 1 usa las mismas (y `V_CORR = 0.92`) |
| Ancho del canal | 1.8288 m | Parte 2; `config_stiv.json` |
| Escala | 1.78 mm/px (1.7842) | Salida de la Parte 2; `config_stiv.json` (`escala_m_px` 0.0017842) |
| Fotogramas por segundo | 30 (30.015) | Salida de la Parte 1; `config_stiv.json` |
| Velocidad esperada | 0.95 m/s | Parte 3 (`V_ESPERADA`); `config_stiv.json` |
| Avance por fotograma / paso DS | 17.74 px → 18 px | Salida de la Parte 3; `config_stiv.json` (`ds_px`) |
| Ángulo de las rayas | 44.6° | Salida de la Parte 3 |
| 87° y "19 veces más" | — | Texto de la Parte 3 del cuaderno SMC ("A 87 grados el mismo error de angulo pesaria 19 veces mas") |
| Tamaño de bloque | 64 × 64, solape 50 % | Parte 4 (`LADO_BLOQUE`); `config_stiv.json` |
| Demostración del tensor | 45.4°, coherencia 0.977 | Salida de la Parte 4 (45.39°, C = 0.9772); `fig5_tensor.png` |
| Umbral de coherencia | 0.70 | Parte 4b (`COH_MIN_ESTACION`); `config_stiv.json` |
| Verticales válidas | 9 de 11 | Salida de la Parte 4b; `salidas/caudal_resumen.csv` |
| Vertical 11 rechazada | 1.34 m/s (1.3448) | Salida de la Parte 4; `salidas/perfil_velocidades.csv` |
| Máximo del centro | 0.97 m/s (0.9738, vertical 6) | Salida de la Parte 4b; `perfil_velocidades.csv` |
| Alfa | 0.92 | Parte 5 (`ALFA`); `config_stiv.json`; `caudal_resumen.csv` |
| Caudal STIV | 1.4475 m³/s | Salida de la Parte 5; `caudal_resumen.csv`; `config_stiv.json` |
| Caudal del aforo | 1.4362 m³/s | Parte 7 (`Q_AFORO`); `caudal_resumen.csv` |
| Incertidumbre del aforo | 4.2 % | Parte 7; `caudal_resumen.csv` |
| Diferencia STIV − aforo | +0.8 % (0.7869 %) | Salida de la Parte 7; `caudal_resumen.csv` |
| Sesgo y RMSE por vertical | −0.5 %, 0.0537 m/s (≈ 5 cm/s) | Salida de la segunda celda de la Parte 7 (no está en ningún CSV) |
| Con alfa 0.85 | ≈ −7 % | Cálculo: 1.4475 × 0.85 / 0.92 = 1.337 m³/s → −6.9 % frente a 1.4362 (el caudal es proporcional a alfa) |
| Vertical 2 fuera del ±10 % | −15.6 % | Tabla "Vertical por vertical" de la Parte 7; `fig10_comparacion.png` |
| Tiempo total STIV | 33.8 s | Salida de la Parte 6; `salidas/benchmark_recursos.csv` (33.77 s) |
| Peso de leer el vídeo | 99.9 % | `benchmark_recursos.csv` (`pct_tiempo`) |
| Tiempo del tensor | 0.02 s | `benchmark_recursos.csv` |
| Pico de memoria STIV | 869 MB | Salida de la Parte 6; `benchmark_recursos.csv` (868.8 MB) |
| "Casi cinco veces más rápido" | 4.7× | 159.08 / 33.77 |
| "Unas dieciséis veces menos memoria" | 15.7× | 13670 / 869 |
| Fotogramas del cuaderno | 250, 8.3 s | Salida de la Parte 3 (`8.33 s`); `config_stiv.json` |
| Duración del vídeo completo | 22 s | Docstring de `video_velocidad.py` (línea 6) |
| Ventana deslizante | 150 fotogramas = 5 s | `video_velocidad.py`, líneas 95 y 98 |
| Número de medidas | 105 ventanas | Filas de `salidas/velocidad_ventanas.csv` |
| Onda estacionaria | 7 m/s, coherencia > 0.70, vertical 11 | Comentario de `video_velocidad.py`, líneas 83 a 86 |
| Cota física | 3 × velocidad esperada (2.85 m/s) | `video_velocidad.py`, línea 89 |
| Caudal mediano en el vídeo entero | 1.4493 m³/s | Mediana de la columna `Q_m3s` de `velocidad_ventanas.csv` |
| 90 % de las ventanas | 1.403 a 1.489 m³/s | Percentiles 5 y 95 de `Q_m3s` en `velocidad_ventanas.csv` |

---

## Notas para quien graba

1. **Las notas técnicas están desfasadas para este caso; el guion usa lo guardado.** Las notas dicen que este
   cuaderno da 1.2221 m³/s (−14.9 %) con alfa 0.85, y que la fila inferior es 1466 (1.7790 mm/px).
   Las salidas guardadas dicen otra cosa: 1.4475 m³/s (+0.8 %), alfa 0.92, fila 1463 y 1.7842 mm/px.
   Coinciden con la versión final que cuenta el resumen cronológico (sección 5).
2. **Dentro del propio cuaderno hay texto que contradice al código.** No lo leas en voz alta y no te
   pares en él:
   - El texto de la Parte 5 todavía pone `α = 0.85` y "0.85 es el valor estándar del USGS". El código usa 0.92.
   - El comentario justo encima de `ALFA = 0.92` dice "0.92 es el estandar de la practica del USGS".
     Eso no es cierto: el estándar es 0.85, como dice el texto. Por eso el guion no da ninguna
     justificación de "estándar" y sí avisa de que con 0.85 saldría un 7 % por debajo.
   - Las secciones finales ("Lectura del resultado" y "Limitaciones conocidas") todavía dicen "el
     notebook usó 0.85" y "un caudal por debajo del aforo". No bajes hasta el final del cuaderno.
3. **`GUIA_DEL_NOTEBOOK.md` también está desfasada**: da 1.2221 m³/s, −14.9 %, alfa 0.85 y fila 1466.
   Por eso el guion no la abre.
4. **La reducción del temblor no aparece en ninguno de estos archivos.** Las cifras 0.50 → 0.02 px (27
   veces) y la deriva de 25.6 px solo están en las notas técnicas (`docs/notas_tecnicas_detalladas.md`) y en el resumen cronológico (sección 4.2). El
   docstring de `estabilizar_stiv.py` no las da, y el script solo las imprime por consola al
   ejecutarse. Por eso la sección 3 lo explica sin números. Si quieres decirlo, la frase sería: "en
   este vídeo el temblor entre fotogramas bajó de medio píxel a dos centésimas", pero su fuente sería
   el resumen, no estos archivos.
5. **"2 de 1155" tampoco está en los archivos.** El resumen dice que la cota física actuó en 2 de 1155
   medidas, pero eso solo se imprime por consola. El CSV no guarda la coherencia ni el motivo del
   rechazo. El docstring dice "alguna vez", y eso es lo que dice el guion.
6. **El "relleno por interpolación lineal" de la figura 6 es, en la práctica, una copia.** Las
   verticales 1 y 11 quedan fuera del tramo medido, y `np.interp` mantiene ahí el valor del extremo:
   la 1 toma el 0.73 de la vertical 2, y la 11 el 0.85 de la vertical 10. Por eso el guion dice "el
   valor de la vertical medida más cercana".
7. **Coincidencia que puede confundir:** en la salida de la demostración del tensor (Parte 4), la
   coherencia es 0.9772 y la velocidad también es 0.9772 m/s. Son dos números distintos que
   casualmente coinciden. Señala la coherencia.
8. **El nombre del vídeo no coincide con el script.** `video_velocidad.py` escribe por defecto
   `salidas/velocidad_tiempo_real.mp4`, pero en la carpeta está `salidas/video_velocimetria.mp4`
   (671 fotogramas, 1920×844, 30 fps). Se comprobó que es la misma ejecución que el CSV: en t = 10.00 s
   el vídeo muestra Q = 1.433 m³/s y 0.836 m/s, igual que la ventana 45 de `velocidad_ventanas.csv`.
9. **Tiempos: se compara lo mismo con lo mismo.** Los 33.8 s de STIV y los ~159 s de pyorc son la suma
   de las etapas medidas por cada cuaderno, sin contar la estabilización. La ejecución completa del
   cuaderno STIV, con figuras, tarda 1 o 2 minutos. El resumen cronológico da 38 s para STIV porque es
   de otra ejecución; el guion usa los 33.8 s guardados.
10. **"Igual o más preciso" se dice como "igual de preciso".** El contenido aprobado decía "igual o
    más preciso". Pero +0.8 % frente a +1.4 % no es una diferencia real cuando el aforo tiene un 4.2 %
    de incertidumbre, y el total depende de alfa (el mismo 0.92 en los dos). Por eso el guion habla de
    empate en precisión.
11. **El tutorial de Ngwerere no tiene control de calidad**: 4 de sus 7 puntos dan velocidades de casi
    cero o negativas. El guion no enseña esa tabla ni su perfil; solo la STI y la función del tensor.
12. El docstring de `benchmark.py` dice que el tensor tarda "décimas de segundo"; lo medido son 0.02 s.
    El texto de la Parte 6 del cuaderno habla de "~14 GB" para pyorc; el guion usa 13.7 GB del vídeo 1.
13. `PLAN_DE_LA_SERIE.md` describe una serie de 7 vídeos que no es la de 5 vídeos que se está grabando.
    No afecta a este guion, pero está desfasado.
