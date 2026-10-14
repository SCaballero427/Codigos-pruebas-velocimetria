# Vídeo 1 — LSPIV con pyorc: de un vídeo de dron a un caudal

**Duración:** ~10 min, una sola toma, sin edición.
**Serie:** 1 LSPIV con pyorc (este) · 2 STIV desde cero y comparación · 3 Casos difíciles · 4 El programa en directo para la cámara de ALIAR · 5 Validación e instalación en Raspberry.

Todas las rutas son relativas a `videos_explicativos/video1_LSPIV_pyorc/`.

## Archivos que se abren, en este orden

1. `analisis_ngwerere/Ngwerere_pipeline_completo.ipynb`
2. `analisis_ngwerere/salidas/fig1_reproyeccion.png`
3. `estabilizar_video.py`
4. `analisis_USGS_SMC_pyorc/SMC_pipeline_completo.ipynb`
5. `analisis_USGS_SMC_pyorc/salidas/fig2_puntos_control.png`
6. `analisis_USGS_SMC_pyorc/salidas/fig12_recursos.png`
7. `analisis_USGS_SMC_pyorc/salidas/fig13_comparacion.png`

## Antes de grabar

- Cierra todas las pestañas: `Ctrl+K W`.
- Abre en pestañas, en este orden: el notebook de Ngwerere, `estabilizar_video.py` y el notebook de SMC. Los PNG **no** se abren antes: se abren durante la grabación haciendo clic en el explorador. Deja desplegadas en el explorador las dos carpetas `salidas/`.
- Sube el zoom con `Ctrl +` (dos o tres veces) hasta que el código se lea bien en la grabación.
- **No ejecutes ninguna celda.** Todo lo que se enseña son resultados ya guardados. Si VS Code pide elegir un kernel, ignóralo o cierra el aviso.
- Activa "No molestar" en Windows y cierra notificaciones.
- Si te equivocas leyendo, di "me corrijo" y sigue. No se corta.

### Cómo se navega

- **En un `.py`:** `Ctrl+G`, escribe el número de línea, `Enter`.
- **En un `.ipynb`:** pulsa `Esc` para salir de cualquier celda, luego `Ctrl+F`, escribe el texto de búsqueda que pone el guion, `Enter` y `Esc` para cerrar el buscador. Todos los textos de búsqueda de este guion aparecen **una sola vez** en su notebook (comprobado sobre la copia, contando código, markdown y salidas). Si el buscador no salta, busca a mano el título de la sección que se indica.
- **Para ver la salida de una celda:** rueda del ratón hacia abajo, justo debajo del código de esa celda.
- **En un PNG:** clic en el archivo dentro de `salidas/` en el explorador.

---

## 1. Qué es LSPIV — 0:00 a 1:10

**Archivo:** `analisis_ngwerere/Ngwerere_pipeline_completo.ipynb`

**Haz:**
- Empieza con el notebook de Ngwerere abierto arriba del todo, en el título "Ngwerere: de video a caudal con pyorc".
- No hace falta mover nada mientras hablas. Si quieres, señala con el ratón la lista de pasos 1 a 5 de la primera celda.

**Di:**

> Hola. Este es el primero de cinco vídeos sobre cómo medir el caudal de un río a partir de un vídeo. Empiezo por donde empecé yo: con una librería que ya existe, pyorc, y un método que se llama LSPIV.
>
> La idea es sencilla. El agua lleva cosas flotando: espuma, hojas, burbujas. Tomo dos fotogramas seguidos, recorto un cuadradito del primero y lo busco en el segundo. Así sé cuántos píxeles se ha movido. Si sé cuántos metros mide un píxel y cuánto tiempo pasa entre fotogramas, eso ya es una velocidad. Lo repito en toda la superficie y tengo un mapa de velocidades.
>
> Con esa velocidad y la forma del cauce sale el caudal, en metros cúbicos por segundo.
>
> Lo difícil es saber cuántos metros mide un píxel, y quitar todo lo que se mueve y no es agua.

---

## 2. Ngwerere: comprobar que sé usar la herramienta — 1:10 a 2:20

**Archivo:** `analisis_ngwerere/Ngwerere_pipeline_completo.ipynb`, luego `analisis_ngwerere/salidas/fig1_reproyeccion.png`, luego otra vez el notebook.

**Haz:**
1. `Esc`, `Ctrl+F`, busca **`src=[`** (sección "Parte 2 - Puntos de control (GCPs)").
2. Señala con el ratón la lista `src` (cuatro pares de píxeles) y luego la lista `dst` (cuatro pares de coordenadas UTM).
3. Baja con la rueda hasta la imagen que hay debajo de la celda, con las cuatro cruces rojas.
4. Abre `analisis_ngwerere/salidas/fig1_reproyeccion.png` desde el explorador. Señala la mitad izquierda y luego la derecha. Señala las marcas de cuadros blancos y negros sobre el césped.
5. Vuelve a la pestaña del notebook. `Esc`, `Ctrl+F`, busca **`referencia = [0.07647424`** (Parte 5). Baja a la salida de esa celda y señala la línea `Caudal (mediana): 0.1672 m3/s   [esperado 0.1641 m3/s, dif. +1.9 %]`.

**Di:**

> Primero comprobé que sabía usar la herramienta, con el ejemplo oficial de pyorc: un río de Zambia, el Ngwerere, con una cámara fija en la orilla.
>
> Estos son los puntos de control, en inglés GCPs. "src" son cuatro marcas en la imagen, en píxeles. "dst" son esas mismas marcas sobre el terreno, medidas con GPS, en metros. Con esas parejas, pyorc calcula cómo pasar de la imagen inclinada de la cámara a una vista desde arriba. A eso se le llama reproyectar.
>
> A la izquierda, lo que ve la cámara. A la derecha, lo mismo visto desde arriba y en metros. Esos cuadros blancos y negros son puntos de control.
>
> Resultado: 0,1672 metros cúbicos por segundo de mediana, frente a 0,1641 publicados. Un 1,9 % de diferencia. Era solo una prueba: la herramienta funciona y sé manejarla. Ahora, un caso de verdad.

---

## 3. El canal del USGS y la estabilización — 2:20 a 3:45

**Archivo:** `analisis_USGS_SMC_pyorc/SMC_pipeline_completo.ipynb`, luego `estabilizar_video.py`.

**Haz:**
1. Pestaña del notebook de SMC. `Esc`, `Ctrl+F`, busca **`Parte 1 - Lectura del video`**.
2. Baja con la rueda, pasando el texto, hasta la imagen del primer fotograma (el canal visto desde arriba, con los conos naranjas). Señala el agua y los dos muros.
3. Pestaña `estabilizar_video.py`. `Ctrl+G` **20**: señala las líneas 20 a 23 (el polígono encierra el agua).
4. `Ctrl+G` **146**: señala `pyorc.cv.get_ms_gftt`. Luego `Ctrl+G` **173**: señala `pyorc.cv.transform`.
5. `Ctrl+G` **32**: señala el título "Por que el codec por defecto es FFV1 y no mp4v" y las líneas 35 a 41.
6. `Ctrl+G` **186**: señala el bloque "Comprobar la fidelidad de lo escrito". Luego baja un poco hasta la línea **204**, "Comprobar que la estabilizacion ha servido de algo".
7. No señales la línea 29: tiene una ruta antigua (ver notas).

**Di:**

> El caso de verdad es un canal de riego de Nuevo México, el Sile Main Canal, del servicio geológico de Estados Unidos, el USGS. Vídeo de dron, en 4K, mirando hacia abajo. Y ese mismo día alguien midió el caudal a mano, dentro del agua, con un correntímetro llamado ADV. Esa es mi referencia independiente. Regla de toda la serie: esa medición no se mira hasta el final.
>
> Primer problema: un dron tiembla. Y LSPIV mide justo cuánto se mueve la imagen entre fotogramas, así que el temblor se sumaría a la velocidad del agua.
>
> Por eso escribí este script. Le doy un polígono que encierra el agua. Lo de fuera, hormigón y hierba, se considera quieto. El script sigue puntos de esa zona, calcula cómo se movió la cámara y corrige cada fotograma. Uso las mismas funciones que pyorc por dentro, pero lo hago una sola vez y lo guardo en disco.
>
> Decisión importante: el formato del vídeo guardado. El habitual, mp4v, comprime con pérdida. El script deja anotado cuánto: unos dos niveles de gris, un 10 % del contraste de la espuma, que es justo lo que LSPIV compara. Así que guardo en FFV1, sin pérdida. Ocupa unas cinco veces más, pero se relee idéntico.
>
> Y el script lo comprueba: relee lo escrito y mide el temblor antes y después.

---

## 4. La escala: dos orillas y un ancho conocido — 3:45 a 5:05

**Archivo:** `analisis_USGS_SMC_pyorc/SMC_pipeline_completo.ipynb`, luego `analisis_USGS_SMC_pyorc/salidas/fig2_puntos_control.png`.

**Haz:**
1. Pestaña del notebook de SMC. `Esc`, `Ctrl+F`, busca **`FILA_AGUA_INF = 1463`** (sección "Parte 2 - Puntos de control: de pixeles a metros").
2. Señala, en este orden: `FILA_AGUA_SUP = 438`, `FILA_AGUA_INF = 1463`, `ANCHO_CANAL = 1.8288`. Luego, un poco más abajo, el bloque `gcps = dict(` con sus dos `src` y sus dos `dst`.
3. Baja a la salida de la celda y señala las tres líneas: `1025 px`, `1.784 mm/px` y `0.49 % en el caudal`.
4. Abre `analisis_USGS_SMC_pyorc/salidas/fig2_puntos_control.png` desde el explorador. Señala, en este orden: la imagen de arriba con las dos cruces; abajo a la izquierda, el perfil de brillo del muro superior (escalón en la línea roja); abajo a la derecha, el perfil del muro inferior (rampa, sin escalón).

**Di:**

> Segundo problema: cuántos metros mide un píxel. En Ngwerere hacían falta cuatro puntos con GPS, porque la cámara miraba de lado. Aquí el dron mira hacia abajo, y basta una distancia conocida: el canal mide 1,8288 metros de ancho, seis pies exactos, según el USGS.
>
> Así que pongo solo dos puntos, en la misma columna: donde el agua toca el muro de arriba, fila 438, y donde toca el de abajo, fila 1463. Con dos puntos, pyorc entiende que la cámara mira hacia abajo y solo calcula escala y giro.
>
> Son 1025 píxeles: 1,784 milímetros por píxel. Y todo el caudal es proporcional a este número. Cinco píxeles de error en una orilla mueven el caudal un 0,49 %.
>
> Esta figura está para comprobarlo. Abajo a la izquierda, el muro de arriba: el brillo da un escalón limpio en la fila 438. Abajo a la derecha, el muro de abajo: no hay escalón, hay una rampa. Ese muro está en sombra y se confunde con el agua. La fila 1463 sale de otro criterio: el agua se mueve y el hormigón no. Esta rampa es la incertidumbre real del caso, y la dejo a la vista.

---

## 5. El PIV: la configuración desde el JSON y un `get_piv` que no es perezoso — 5:05 a 6:10

**Archivo:** `analisis_USGS_SMC_pyorc/SMC_pipeline_completo.ipynb`

**Haz:**
1. `Esc`, `Ctrl+F`, busca **`lazy dask.array form`** (sección "Parte 4 - Velocidades superficiales con LSPIV"). Señala la frase de la documentación y luego la tabla de cuatro filas; detente en la fila `get_piv | numpy | calcula en el momento`.
2. Baja a la celda de código siguiente. `Esc`, `Ctrl+F`, busca **`cam_config = pyorc.load_camera_config`** y señala esa línea.
3. Señala después `da.frames.normalize()`, `frames.project(method="numpy")` y `piv = da_norm_proj.frames.get_piv()`.
4. **No bajes a la salida de esta celda.** Sus líneas `[bench]` (39.9 s, 77.8 s, 85.0 s, 11209 MB) son de **otra ejecución** que la tabla de la Parte 6. Si se ven en pantalla, no leas esos números.

**Di:**

> Con la escala, pyorc construye la configuración de la cámara y la guarda en un archivo JSON.
>
> Aquí encontré algo. La documentación de get_piv, la función que hace la correlación, dice que solo prepara el cálculo y que el trabajo se hace después, al guardar. Comprobé qué devuelve cada paso, y no es así: los tres primeros esperan, pero get_piv calcula en el momento.
>
> Fíjate en esta línea: antes de calcular, vuelvo a cargar la configuración desde el JSON. Si todo funciona leyendo solo ese archivo, el archivo está completo. Para una cámara fija es lo que quiero: calibrar una vez y reutilizar.
>
> Luego, la cadena de pyorc. Normalizar, que es quitar el fondo quieto para que solo quede la espuma. Reproyectar a metros. Y get_piv. Ahí se va el tiempo y la memoria; lo veremos en la Parte 6.

---

## 6. Las máscaras: quitar lo que no es agua — 6:10 a 7:00

**Archivo:** `analisis_USGS_SMC_pyorc/SMC_pipeline_completo.ipynb`

**Haz:**
1. `Esc`, `Ctrl+F`, busca **`ds_mask.velocimetry.mask.corr(inplace=True)`** (sección "Parte 4b - Filtrado de velocidades espurias").
2. Recorre con el ratón los cuatro bloques comentados: `1) mascaras sobre valores individuales`, `2) mascaras en el dominio del tiempo`, `3) direccion del flujo`, `4) mascaras que necesitan toda la serie`.
3. Baja a la salida y señala `Vectores validos antes del filtrado: 496375` y `Vectores validos despues: 281464 (56.7 %)`. Ignora la línea `[bench]`.
4. Baja un poco más hasta la imagen del campo filtrado y señala el centro (naranja) y los bordes (verde).

**Di:**

> LSPIV da un vector por cuadradito y por par de fotogramas. Muchos son basura: zonas sin espuma, reflejos, el borde del muro. Las máscaras los quitan.
>
> El orden importa, porque cada una trabaja sobre lo que dejó la anterior. Primero, valores sueltos: correlación baja, velocidades imposibles. Luego, la serie en el tiempo de cada punto. Luego, la dirección, que aquí sí aplico porque en un canal recto el agua va toda en el mismo sentido. Y al final, comparar cada punto con sus vecinos.
>
> Sobreviven 281 464 de 496 375 vectores: el 56,7 %. En Ngwerere, el 24 %. Aquí la espuma es mucho mejor trazador. Y el campo filtrado sale paralelo, más rápido en el centro y más lento junto a los muros.

---

## 7. El caudal y su banda de error — 7:00 a 8:00

**Archivo:** `analisis_USGS_SMC_pyorc/SMC_pipeline_completo.ipynb`

**Haz:**
1. `Esc`, `Ctrl+F`, busca **`V_CORR = 0.92`** (sección "Parte 5 - Seccion transversal y caudal"). Señala la línea y el comentario de encima ("Se fija aqui, antes de mirar ninguna referencia").
2. `Esc`, `Ctrl+F`, busca **`Q_PYORC = float(caudal.sel`**. Baja a la salida.
3. Señala `Caudal (mediana): 1.4565 m3/s` y la línea `Banda del PIV: P5 = 1.3532   P95 = 1.5754  (-7.1 % .. +8.2 %)`.
4. Baja a la tabla de debajo y señala la columna `origen`: las filas 1, 2 y 11 dicen `relleno log_interp`; de la 3 a la 10, `medida`.

**Di:**

> Para el caudal hacen falta dos cosas más. La sección, que leo tal cual del archivo del USGS: trece verticales de 1,073 metros de profundidad. Y un factor, v_corr, que pasa de la velocidad en superficie a la velocidad media, porque el agua del fondo va más despacio. Uso 0,92, fijado aquí antes de ver ningún resultado. Es el mismo que usa el método del vídeo 2, para que la comparación sea justa.
>
> El caudal: 1,4565 metros cúbicos por segundo de mediana. pyorc calcula también otros cuantiles de la velocidad en el tiempo. El 5 % y el 95 % dan una banda de 1,35 a 1,58: de menos 7,1 % a más 8,2 %. Esa es mi barra de error honesta.
>
> Y la letra pequeña: de las once verticales con agua, pyorc midió ocho. La 1, la 2 y la 11, junto a los muros, no tienen medida. Las rellena con un perfil logarítmico. Son relleno, no dato.

---

## 8. Lo que cuesta: tiempo y memoria — 8:00 a 8:45

**Archivo:** `analisis_USGS_SMC_pyorc/SMC_pipeline_completo.ipynb`, luego `analisis_USGS_SMC_pyorc/salidas/fig12_recursos.png`.

**Haz:**
1. `Esc`, `Ctrl+F`, busca **`tabla_recursos = benchmark.tabla()`** (sección "Parte 6 - Recursos consumidos"). Baja a la salida.
2. Señala `cpu_nucleos_fisicos: 8`, `Tiempo total medido: 159.1 s` y `Pico de memoria del proceso: 13670 MB`.
3. Abre `analisis_USGS_SMC_pyorc/salidas/fig12_recursos.png` desde el explorador. Señala las barras de arriba a abajo: `get_piv` 75.3 s (47 %), `normalize + project` 53.9 s (34 %), `abrir video y get_frames` 26.8 s (17 %), y la última, `to_netcdf` 0.2 s.
4. Usa solo estos números. Los de la salida de la Parte 4 son de otra ejecución.

**Di:**

> ¿Cuánto cuesta todo esto? En la máquina donde lo medí, con ocho núcleos, 159 segundos, y la memoria llega a 13 670 megas. Casi 14 gigas. Para 8,3 segundos de vídeo.
>
> Así se reparte el tiempo. get_piv, 75 segundos, el 47 %. Normalizar y reproyectar, 54. Leer el vídeo, 27. Y guardar a disco, que según la documentación sería lo caro, 0,2 segundos.
>
> Un aviso: debajo de la celda de la Parte 4 hay otros tiempos impresos, de otra ejecución. Los que valen son estos.

---

## 9. Por fin, la medición de campo — 8:45 a 9:50

**Archivo:** `analisis_USGS_SMC_pyorc/SMC_pipeline_completo.ipynb`, luego `analisis_USGS_SMC_pyorc/salidas/fig13_comparacion.png`.

**Haz:**
1. `Esc`, `Ctrl+F`, busca **`Q_AFORO = 1.4362`** (sección "Parte 7 - Comparacion con la referencia del dataset"). Señala el comentario de encima ("Es la primera vez que aparecen en el notebook") y la línea `Q_AFORO`.
2. Baja a la salida. Señala `Aforo FlowTracker (ADV) : 1.4362 m3/s (incertidumbre ISO 4.2 %)`, `Diferencia : +1.4 %` y `(-5.8 % .. +9.7 % frente al aforo)`.
3. En la tabla "Vertical por vertical" señala la fila de la vertical **1**: `0.7676` (pyorc), `0.6298` (ADV), `21.8788`, `relleno log_interp`.
4. `Esc`, `Ctrl+F`, busca **`v_corr_implicito = float`**. Baja a la salida (debajo de la imagen) y señala `Sesgo medio frente al ADV: +0.0017 m/s (+0.2 %)` y `v_corr implicito = 0.918  (el notebook uso 0.92)`.
5. Abre `analisis_USGS_SMC_pyorc/salidas/fig13_comparacion.png` desde el explorador. Señala el panel izquierdo (perfiles) y luego el derecho: los puntos azules junto a la diagonal, la 10 justo por fuera de la línea del −10 %, y el cuadrado naranja **1**, lejos.

**Di:**

> Y ahora, por primera vez en todo el notebook, abro la medición de campo. El comentario lo dice: es la primera vez que aparecen estos datos, y después no se toca nada.
>
> El aforo con ADV da 1,4362 metros cúbicos por segundo, con una incertidumbre declarada del 4,2 %. pyorc da 1,4565: un 1,4 % por encima. Y el aforo cae dentro de mi banda.
>
> Vertical a vertical, la que más se desvía es la 1, pegada al muro: pyorc pone 0,77 y el ADV midió 0,63. Un 22 % de más. Y es una vertical rellenada, no medida.
>
> En las ocho medidas, el sesgo es del 0,2 %. Y el v_corr que habría hecho falta sale 0,918; yo usé 0,92. Es una coincidencia y queda como diagnóstico, no como corrección. Una versión anterior probaba varios v_corr y miraba cuál se acercaba al aforo. La quité: eso es ajustar contra la referencia, y entonces ya no hay validación.
>
> A la izquierda, la forma del perfil sale bien. A la derecha, los puntos azules, medidos, están junto a la diagonal. Los naranjas son relleno, y el 1 se va lejos.

---

## 10. Cierre y puente al vídeo 2 — 9:50 a 10:30

**Archivo:** sigue en `fig13_comparacion.png`.

**Haz:**
- Nada. Deja la figura en pantalla mientras hablas.

**Di:**

> Resumen. pyorc funciona: un 1,4 % de diferencia con un aforo independiente, sin ajustar nada. Pero me quedé con tres problemas.
>
> Uno: casi 14 gigas de memoria para 8 segundos de vídeo. Para una cámara fija midiendo todo el día en un ordenador pequeño, no sirve.
>
> Dos: es una caja negra. Su documentación decía una cosa y hacía otra, y solo lo supe midiendo.
>
> Tres: las orillas no se miden, se rellenan.
>
> Por eso, en el siguiente vídeo, programo otro método desde cero, que se llama STIV, sobre este mismo vídeo y con la misma escala. Y comparo los dos.

---

## Cifras a mano

| Lo que se dice | Valor | De dónde sale |
|---|---|---|
| Ngwerere, caudal mediano | 0,1672 m³/s | Ngwerere, salida de la celda de la Parte 5 (`Caudal (mediana)`); `analisis_ngwerere/salidas/caudal_resumen.csv`, fila 0.5 |
| Ngwerere, valor publicado | 0,1641 m³/s | Misma salida (`esperado 0.1641`); CSV, `referencia_ejemplo_m3s` = 0.16405959 |
| Ngwerere, diferencia | +1,9 % | Misma salida (`dif. +1.9 %`) |
| Ngwerere, número de GCPs | 4 | Ngwerere, celda de la Parte 2 (listas `src` y `dst`) |
| Ngwerere, vectores que sobreviven a las máscaras | 24,0 % | Ngwerere, salida de la Parte 4b (`111124 (24.0 %)`) |
| mp4v: error de ~2 niveles de gris, ~10 % del contraste | 2,1 niveles, 10 % | `estabilizar_video.py`, docstring, líneas 35-37 (**texto, no salida guardada**: ver notas) |
| FFV1 ocupa ~5 veces más | ~5x | `estabilizar_video.py`, docstring, líneas 40-41 (**texto**) |
| Ancho del canal | 1,8288 m (6 ft) | SMC, celda de la Parte 2 (`ANCHO_CANAL`, "obtenido del dataset") |
| Filas de las orillas | 438 y 1463 | SMC, celda de la Parte 2; `salidas/config_pyorc.json`; títulos de `fig2_puntos_control.png` |
| Ancho en la imagen | 1025 px | SMC, salida de la Parte 2 |
| Escala | 1,784 mm/px | SMC, salida de la Parte 2; `config_pyorc.json` (`escala_m_px` = 0.0017842) |
| 5 px de error en la orilla → caudal | 0,49 % | SMC, salida de la Parte 2; `caudal_resumen.csv` (0.4878 %) |
| Vectores antes / después de las máscaras | 496 375 / 281 464 (56,7 %) | SMC, salida de la Parte 4b |
| Profundidad de las verticales | 1,073 m | SMC, salida de la Parte 5 (tabla del CSV) |
| Verticales | 13; 11 con agua; 8 medidas, 3 rellenadas (1, 2, 11) | SMC, salidas de la Parte 5; `salidas/perfil_transecto.csv` (columna `origen`); `caudal_resumen.csv` |
| `v_corr` usado | 0,92 | SMC, Parte 5 (`V_CORR`); `config_pyorc.json`; `caudal_resumen.csv` |
| Caudal mediano | 1,4565 m³/s | SMC, salida de la Parte 5; `caudal_resumen.csv` (1.45646) |
| Banda P5–P95 | 1,3532 – 1,5754 m³/s (−7,1 % / +8,2 % sobre la mediana) | SMC, salida de la Parte 5 (`Banda del PIV`) |
| Núcleos de la máquina | 8 físicos | SMC, salida de la Parte 6 (`cpu_nucleos_fisicos`) |
| Tiempo total | 159,1 s | SMC, salida de la Parte 6; suma de `salidas/benchmark_recursos.csv` |
| Pico de memoria | 13 670 MB ("casi 14 gigas") | SMC, salida de la Parte 6; `benchmark_recursos.csv`, `get_piv`, `ram_pico_mb` = 13670.3 |
| Duración procesada | 8,3 s | 250 pasos de PIV (salida de la Parte 4: `'time': 250`) a 30,015 fps (salida de la Parte 1) |
| `get_piv` | 75,3 s (47 %) | `fig12_recursos.png`; `benchmark_recursos.csv` (75.28 s, 47.3 %) |
| `normalize + project` | 53,9 s (34 %) | `fig12_recursos.png`; CSV (53.9 s, 33.9 %) |
| Leer vídeo (`get_frames`) | 26,8 s (17 %) | `fig12_recursos.png`; CSV (26.75 s, 16.8 %) |
| `to_netcdf` | 0,2 s | `fig12_recursos.png`; CSV (0.25 s) |
| Aforo ADV | 1,4362 m³/s, incertidumbre 4,2 % | SMC, Parte 7 (código y salida); `caudal_resumen.csv` |
| Diferencia pyorc vs aforo | +1,4 % | SMC, salida de la Parte 7; `caudal_resumen.csv` (1.4104 %) |
| Banda frente al aforo | −5,8 % / +9,7 % | SMC, salida de la Parte 7 |
| Vertical 1: pyorc vs ADV | 0,7676 vs 0,6298 m/s, +21,9 % ("un 22 %"), relleno | SMC, salida de la Parte 7 (tabla "Vertical por vertical"); `fig13_comparacion.png` |
| Vertical 10 (la medida que más se desvía) | −11,3 % | SMC, salida de la Parte 7; `fig13_comparacion.png` (justo en la línea del −10 %) |
| Sesgo sobre las 8 medidas | +0,0017 m/s (+0,2 %) | SMC, salida de la celda de `fig13` (Parte 7) |
| `v_corr` implícito | 0,918 | SMC, salida de la Parte 7; `caudal_resumen.csv` (0.91816) |

---

## Notas para quien graba

1. **Dos ejecuciones mezcladas en el notebook de SMC.** Las celdas de rutas, Parte 1, Parte 2 y Parte 3 (contadores 1 a 5) son de una ejecución posterior (3 de agosto) a la del resto (31 de julio, sin contador). La salida de la celda de la Parte 4 imprime `[bench]` con 39,9 s, 77,8 s, 85,0 s y 11 209 MB, que **no** coinciden con la tabla de la Parte 6, ni con `fig12_recursos.png`, ni con `benchmark_recursos.csv` (26,75 / 53,9 / 75,28 s y 13 670 MB). Los tres últimos sí coinciden entre sí: usa solo esos.
2. **`fig2_puntos_control.png` no la dibuja ninguna celda del notebook actual.** La celda de la Parte 2 solo imprime, aunque el markdown de encima habla de "la figura de abajo". El PNG (31 de julio) sí es coherente con las filas 438 y 1463, así que se puede enseñar. Pero no digas "esta celda dibuja la figura"; por eso se abre desde el explorador.
3. **Error en la Parte 5 del notebook (no se enseña):** `AREA_CAJA = 1.7988` está escrito a mano e imprime la "caja física" como 1,7988 m² (−0,2 %). El markdown de la misma parte dice que la caja mide 1,962 m² y es un 9 % mayor. La leyenda de `fig7_seccion.png` se construye con ese mismo valor erróneo. No cites el área de la caja.
4. **La celda final ("Lectura del resultado") remite a "la figura 12"** para los cuadrados naranjas. Es la `fig13_comparacion.png`. No la leas en voz alta.
5. **El vídeo estabilizado tiene 251 fotogramas** (salida de la Parte 1), no 250. pyorc lee 251 y el PIV da 250 pasos de tiempo. Por eso el guion habla de "8,3 segundos", nunca de "250 fotogramas del vídeo estabilizado".
6. **`estabilizar_video.py`, línea 29:** el ejemplo usa la ruta antigua `analisis_USGS_SMC/entradas/...`; la carpeta real es `analisis_USGS_SMC_pyorc`. No la señales.
7. **Cifras que salen de texto y no de una salida guardada:** el "2,1 niveles de gris / 10 %" de mp4v y el "unas 5 veces más" de FFV1 están en el docstring de `estabilizar_video.py` (líneas 35-41). No hay ninguna salida guardada de una ejecución del script en estas copias. Por eso el guion los presenta como "el propio script deja anotado".
8. **En el notebook de Ngwerere no bajes a la Parte 4.** Su comentario dice que "`to_netcdf` es lo que dispara realmente el calculo", justo lo contrario de lo que se cuenta en la sección 5. Además, sus salidas imprimen rutas `analisis_ngwerere_verificado\salidas` (se ejecutó en una carpeta con otro nombre): no las leas.
9. **Las notas técnicas (`docs/notas_tecnicas_detalladas.md`) no coinciden con las salidas guardadas** (manda la salida): dice fila inferior 1466 (la salida dice 1463), escala 1,7790 mm/px (1,7842), caudal 1,4507 m³/s y +1,0 % (1,4565 y +1,4 %), banda −5,4 % / +9,7 % (−5,8 % / +9,7 % frente al aforo), `v_corr` implícito 0,922 (0,918) y `get_piv` 74,3 s / 14,4 GB (75,28 s / 13 670 MB). Si alguien compara el vídeo con ese archivo, encontrará esas diferencias.
10. **Búsquedas con `Ctrl+F`:** todos los textos están verificados como únicos en su notebook. Si el buscador del notebook tiene desactivado "Markdown renderizado", la búsqueda `lazy dask.array form` (sección 5) puede no saltar. En ese caso, busca a mano el título "Parte 4 - Velocidades superficiales con LSPIV".
