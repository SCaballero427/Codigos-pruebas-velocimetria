# Vídeo 5 — Validación e instalación

**Duración:** ~10 min, una sola toma, sin edición.
**Último vídeo de la serie** (1 LSPIV con pyorc · 2 STIV desde cero · 3 Casos difíciles · 4 El programa en directo · 5 este).

Todas las rutas son relativas a
`videos_explicativos/video5_validacion_e_instalacion/analisis_kurome_directo_stiv/`.
**Los números de línea son los de la COPIA de esta carpeta**, no los del `analisis_kurome_directo_stiv/`
de la raíz del workspace, que sigue cambiando.

## Pestañas, en este orden (8)

1. `validacion/README.md`
2. `validacion/correr.py`
3. `validacion/salidas/sile.txt`
4. `validacion/salidas/heiskanen.txt`
5. `raspberry/LEEME.md`
6. `raspberry/subir_a_raspberry.ps1`
7. `raspberry/instalar.sh`
8. `pruebas_docker/docker-compose.yml`

## Antes de grabar

- Cierra todas las pestañas: `Ctrl+K` y luego `W`.
- Abre las 8 en el orden de arriba con `Ctrl+P`. **Mira la ruta que sale debajo del nombre**: tiene
  que poner `videos_explicativos\video5_validacion_e_instalacion\...`. Si coges el `README.md` o el
  `LEEME.md` de la raíz del workspace, las líneas no cuadran.
- Los `.md` tienen que abrirse **como texto**, no en vista previa (si sale la vista previa: clic
  derecho en la pestaña → *Reopen Editor With…* → *Text Editor*).
- En `heiskanen.txt` activa el ajuste de línea (`Alt+Z`): sus líneas 5, 13 y 25 son muy largas.
- Zoom: `Ctrl +` dos o tres veces, hasta que se lea bien en la grabación.
- Activa "No molestar" en Windows (y cierra Teams, correo, WhatsApp).
- Navegación: `Ctrl+G`, escribe el número de línea, `Enter`. Para "señalar" un rango, selecciónalo
  con el ratón (clic en la primera línea, `Shift`+clic en la última).
- Si te equivocas: di "me corrijo" y sigue. No se para la toma.

---

## 1. Qué vamos a ver — 0:00 a 0:45

**Archivo:** `validacion/README.md`

**Haz:**
- `Ctrl+G` → `1`. Señala las líneas 1 a 10 mientras hablas.
- Al decir "la idea entera", señala la línea 10 (`correr.py` importa el programa de verdad).

**Di:**

> Hola. Este es el quinto y último vídeo de la serie.
> En el anterior vimos el programa en directo, stiv_directo.py, midiendo cámaras públicas de ríos de Tokio.
> Pero allí nadie midió el río a mano a la vez. No sabemos si esos números son buenos.
> Hoy hago dos cosas.
> Primero, la validación: comparar el programa con mediciones de campo de verdad.
> Y segundo, la instalación en una Raspberry Pi, el ordenador pequeño que irá junto a la cámara de ALIAR.
> Este es el README de la validación. En estas diez líneas está la idea entera.

---

## 2. El mismo código que corre en directo — 0:45 a 1:45

**Archivo:** `validacion/correr.py`

**Haz:**
- `Ctrl+G` → `7`. Señala las líneas 7 a 9 (el `import stiv_directo as sd`).
- `Ctrl+G` → `11`. Señala las líneas 11 y 12 (`POR_CAMARA`).
- `Ctrl+G` → `18`. Señala las líneas 18 a 21; deja el cursor en la 20 (`raise ValueError`).

**Di:**

> La idea es sencilla.
> Cojo vídeos de ríos donde alguien midió la velocidad del agua con instrumentos.
> Y los paso por el mismo código del programa en directo. No por una copia.
> Línea nueve: correr.py importa stiv_directo.py, el programa de verdad.
> Lo que valido es lo que va a correr en la Raspberry.
> Líneas once y doce: lo único que puedo cambiar de una cámara a otra. Cuántas estaciones, el largo de la línea, la velocidad esperada.
> Si intento cambiar otra cosa, la línea veinte da un error.
> El método, los bloques, la coherencia, las escalas de tiempo, se queda como está.
> Y otra regla: la medición de referencia solo se abre al final de cada script.
> Así no puedo retocar nada para que cuadre.

---

## 3. Canal del USGS: el mejor resultado — 1:45 a 2:55

**Archivo:** `validacion/salidas/sile.txt`

**Haz:**
- `Ctrl+G` → `6`. Señala las líneas 6 a 16 (las once verticales).
- Señala la línea 6 (coh 0.64) y luego la 16 (coh 0.59).
- `Ctrl+G` → `30`. Señala la línea 30.
- `Ctrl+G` → `32`. Señala la línea 32.

**Di:**

> Primer caso: el canal del USGS, el servicio geológico de Estados Unidos. El mismo de los vídeos uno y dos.
> Esta vez con el vídeo original, sin estabilizar. El programa en directo no estabiliza, así que lo pruebo tal como llegaría de una cámara.
> Líneas seis a dieciséis: las once verticales. Miden las once.
> Fijaos en la primera y la última, junto a los muros: coherencia 0.64 y 0.59.
> El caso del vídeo dos las rechazaba. Aquí pasan, y coinciden con el ADV.
> El ADV es un correntómetro acústico: un sensor que se mete en el agua y mide la velocidad con ultrasonido.
> Línea treinta: con la velocidad de superficie por 0.92, que es pasar a la velocidad media de la vertical, el sesgo frente al ADV es de más 1.6 %.
> Y línea treinta y dos: el caudal sale 1.4537 metros cúbicos por segundo.
> El aforo dice 1.4362. Un 1.2 % de diferencia.

---

## 4. Bradano: el programa no veía un trazador disperso — 2:55 a 3:55

**Archivo:** `validacion/README.md`

**Haz:**
- `Ctrl+G` → `44`. Señala las líneas 44 y 45.
- `Ctrl+G` → `55`. Señala las líneas 55 a 59.
- `Ctrl+G` → `86`. Señala las líneas 86 y 87.
- `Ctrl+G` → `92`. Señala las líneas 92 a 95.

**Di:**

> Segundo caso: el río Bradano, en Italia. Aquí hubo sorpresa.
> Línea cuarenta y cuatro: con el programa como estaba, medía una vertical de siete.
> ¿Por qué? Líneas cincuenta y cinco a cincuenta y ocho.
> El programa se defiende de YouTube, que congela el agua lisa y la hace parecer quieta.
> Para eso exigía que cambiase la mitad de los píxeles de cada bloque.
> Pero el Bradano es agua casi negra con partículas sueltas. Casi nada cambia. Ningún bloque llegaba a la mitad.
> Además el vídeo es gris, y el programa trata una imagen gris como noche, como una cámara en infrarrojo.
> El arreglo, línea ochenta y siete: de noche basta con el diez por ciento.
> Con eso, cinco de siete verticales, y un sesgo de menos 4.5 %.
> ¿Por qué solo de noche? Líneas noventa y dos a noventa y cinco.
> La primera versión lo bajaba siempre. Y con el sol de cara, en el caso siguiente, aceptó catorce estaciones de veinte, con más de un 36 % de error.
> El cincuenta por ciento nos protegía de eso sin que lo supiéramos.

---

## 5. Heiskanen: la cámara más parecida a la de ALIAR — 3:55 a 5:15

**Archivo:** `validacion/salidas/heiskanen.txt`

**Haz:**
- `Ctrl+G` → `48`. Señala las líneas 48 y 49.
- Señala la línea 50, y luego la 51 y 52.
- Señala la línea 53 y déjala seleccionada mientras terminas.

**Di:**

> Tercer caso, el más importante: Heiskanen, un río de Finlandia.
> Datos publicados por unos investigadores, con una cámara IP fija en la orilla. Lo más parecido a ALIAR.
> La referencia es un ADCP: un perfilador acústico que va en una barca y mide con ultrasonido la velocidad en toda la sección.
> Seis vídeos, de las ocho de la mañana a la una.
> Líneas cuarenta y ocho y cuarenta y nueve: a las ocho y a las nueve mide siete u ocho estaciones de veinte, el tercio más cercano.
> Y se queda entre un 14 y un 18 % por debajo del ADCP. Eso aún no está explicado.
> Línea cincuenta: a las diez el sol da de cara, el agua sale blanca, y mide solo tres estaciones. A las once y a las doce, una.
> Eso está bien: no inventa.
> Y ahora la línea cincuenta y tres. A la una: quince estaciones, un 35 % por encima, con coherencia alta.
> No es una crecida: ese día el caudal bajaba. Son destellos del sol en las ondas.
> Es el caso peligroso: un error que parece una buena medida. De día, el programa no se defiende de eso.

---

## 6. Zona lejana, lecciones y regresión — 5:15 a 6:05

**Archivo:** `validacion/README.md`

**Haz:**
- `Ctrl+G` → `71`. Señala las líneas 71 a 73.
- `Ctrl+G` → `81`. Señala las líneas 81 y 82.
- `Ctrl+G` → `122`. Señala las líneas 122 a 127.
- `Ctrl+G` → `105`. Señala la tabla, líneas 105 a 120.

**Di:**

> Vuelvo al README. Línea setenta y uno: la zona lejana, de veinte a cuarenta metros, se rechaza siempre.
> Ahí el STIV de los propios autores da menos de la mitad que el ADCP. El programa se abstiene donde ellos se equivocan.
> Las lecciones para ALIAR, líneas ochenta y uno y ochenta y dos.
> Que la cámara no mire al sol: aquí se perdieron tres horas de seis.
> Que esté cerca del agua: lejos, el agua lisa no se mide ni en 4K.
> Y probablemente con un polarizador, un filtro que quita reflejos.
> Último punto, línea ciento veintidós: la regresión.
> Es comprobar que un cambio no estropea lo que ya funcionaba.
> regresion.py vuelve a pasar por el programa los directos de Tokio que grabé.
> La tabla de la línea ciento cinco tiene el antes y el después del arreglo del Bradano. De día, todo idéntico.

---

## 7. Del PC a la Raspberry — 6:05 a 7:10

**Archivo:** `raspberry/LEEME.md`, después `raspberry/subir_a_raspberry.ps1`

**Haz:**
- En `LEEME.md`: `Ctrl+G` → `1`. Señala las líneas 1 a 4.
- `Ctrl+G` → `24`. Señala las líneas 24 a 26 (64 bits).
- `Ctrl+G` → `39`. Señala las líneas 39 a 42.
- `Ctrl+G` → `49`. Señala las líneas 49 y 50.
- Cambia a la pestaña `subir_a_raspberry.ps1`. `Ctrl+G` → `43`. Señala las líneas 43 a 58.
- `Ctrl+G` → `60`. Señala las líneas 60 a 66.
- `Ctrl+G` → `88`. Señala las líneas 88 a 94.
- `Ctrl+G` → `96`. Señala las líneas 96 a 106.

**Di:**

> Segunda parte: la instalación.
> Esta es la guía, el LEEME de la carpeta raspberry. Escrita para alguien que nunca ha usado una Raspberry.
> Paso uno: grabar el sistema en la tarjeta, Raspberry Pi OS Lite de 64 bits.
> Paso dos: conectarla por cable al router y comprobar que el PC la ve por SSH.
> SSH es manejar otro ordenador desde una terminal, por la red.
> Paso tres, línea cuarenta y nueve: doble clic en subir_a_raspberry. La primera vez, unos diez minutos.
> Ese script hace tres cosas.
> Desde la línea cuarenta y tres, prepara un paquete: el programa y las configuraciones de cámara.
> En la línea sesenta pasa los finales de línea al formato de Linux; si no, los scripts fallan en la Pi.
> Línea ochenta y ocho: lo copia con scp, que es copiar archivos por SSH.
> Y línea noventa y seis: entra en la Pi y ejecuta instalar.sh.

---

## 8. En la Raspberry: instalar, el servicio y nuestra cámara — 7:10 a 8:15

**Archivo:** `raspberry/instalar.sh`, después `raspberry/LEEME.md`

**Haz:**
- En `instalar.sh`: `Ctrl+G` → `1`. Señala las líneas 2 y 3.
- `Ctrl+G` → `28`. Señala las líneas 28 a 30.
- `Ctrl+G` → `32`. Señala las líneas 32 a 35.
- `Ctrl+G` → `38`. Señala las líneas 38 a 44.
- `Ctrl+G` → `62`. Señala las líneas 62 a 72.
- Cambia a `LEEME.md`. `Ctrl+G` → `100`. Señala las líneas 100 y 101.
- `Ctrl+G` → `113`. Señala la tabla, líneas 113 a 127.
- `Ctrl+G` → `137`. Señala la línea 138 (la dirección `rtsp://`).
- `Ctrl+G` → `157`. Señala las líneas 157 y 158.

**Di:**

> Esto es instalar.sh, lo que corre dentro de la Pi.
> Se puede repetir sin miedo: lo que ya está, lo actualiza.
> Línea veintiocho: instala lo que falta con apt, el instalador de programas de Linux.
> Línea treinta y dos: un entorno de Python propio, con OpenCV sin pantalla, porque la Pi no tendrá monitor.
> Línea treinta y ocho: crea la configuración, stiv.conf, solo si no existe. Una actualización nunca la pisa.
> Línea sesenta y dos: el servicio. Usa systemd, la parte de Linux que arranca programas al encender.
> En el LEEME, línea cien: si el programa se cae, systemd lo relanza a los quince segundos.
> Para el día a día, stiv.sh. Línea ciento trece: prueba, activar, estado, registro, medidas, salud.
> Línea ciento treinta y siete: nuestra cámara.
> Una cámara IP manda su vídeo por RTSP, el protocolo estándar de las cámaras de vigilancia.
> Esa dirección va en stiv.conf, línea ciento cincuenta y siete, y se reinicia el servicio.

---

## 9. Una Raspberry falsa en Docker — 8:15 a 9:30

**Archivo:** `pruebas_docker/docker-compose.yml`, después `raspberry/LEEME.md`

**Haz:**
- En `docker-compose.yml`: `Ctrl+G` → `5`. Señala las líneas 5 a 10.
- `Ctrl+G` → `19`. Señala la línea 19 (`platform: linux/arm64`).
- Cambia a `LEEME.md`. `Ctrl+G` → `183`. Señala las líneas 183 a 193.
- `Ctrl+G` → `194`. Señala las líneas 194 a 196.
- `Ctrl+G` → `198`. Señala las líneas 198 a 205.

**Di:**

> ¿Cómo lo he probado sin la Raspberry? Con Docker.
> Docker monta dentro del PC ordenadores de mentira, que se llaman contenedores.
> Líneas cinco a diez: son tres.
> Una Raspberry falsa: Linux para ARM, el procesador de la Pi, con systemd y SSH.
> Un servidor RTSP. Y una cámara simulada que emite el vídeo de prueba en bucle.
> Instalo con los mismos scripts que usaré con la Pi de verdad.
> En el LEEME, línea ciento ochenta y tres: instala desde cero, el servicio arranca solo al reiniciar, y si corto la cámara ocho segundos, reconecta y vuelve a medir.
> La prueba encontró cuatro fallos, ya corregidos. Tres en la línea ciento noventa y cuatro.
> Una función de OpenCV que falla sin pantalla.
> Un reloj que volvía a cero al reconectar, y entonces no medía.
> Y una cola de seiscientos fotogramas que llevaba la memoria a 1.3 gigas. Ahora son ciento cincuenta, unos 626 megas.
> El cuarto, en el script de subida: una función se llamaba Ssh, y como PowerShell no distingue mayúsculas, se llamaba a sí misma sin fin.
> Línea ciento noventa y ocho: lo que no está probado.
> Cuánto tarda una Pi 4 de verdad, porque la emulación no lo dice. Y una cámara real.

---

## 10. Cierre de la serie — 9:30 a 10:00

**Archivo:** `raspberry/LEEME.md`

**Haz:**
- `Ctrl+G` → `151`. Señala las líneas 151 a 153 (`largo_m`, `ancho_m`, `escala_verificada`).
- `Ctrl+G` → `160`. Señala las líneas 160 a 163 y déjalo ahí hasta el final.

**Di:**

> Y con esto termina la serie.
> Empezamos con pyorc y LSPIV, que mide bien pero pide mucha memoria.
> Pasamos a STIV desde cero, mucho más ligero.
> Vimos los casos difíciles, y que el método sabe cuándo no medir.
> Construimos el programa en directo.
> Y hoy lo hemos comparado con mediciones de campo: un 1.2 % en el canal, y también dónde falla, con los destellos del sol.
> El siguiente paso es ALIAR: instalar la cámara y la Raspberry.
> Medir en el sitio dos distancias, el largo y el ancho del rectángulo sobre el agua, para fijar la escala.
> Volver a ajustar el umbral de actividad con esa cámara.
> Y comprobar cómo mide de día y de noche.
> Gracias por verlo.

---

## Cifras a mano

Rutas relativas a `video5_validacion_e_instalacion/analisis_kurome_directo_stiv/`.

| Cifra que se dice | De dónde sale |
|---|---|
| Sile: 11 de 11 verticales | `validacion/salidas/sile.txt` líneas 6-16 y 30; `validacion/README.md` línea 43 |
| Verticales junto a los muros: coherencia 0.64 y 0.59 | `sile.txt` líneas 6 y 16; `README.md` líneas 52-53 |
| 0.92 × velocidad superficial; sesgo +1.6 % frente al ADV | `sile.txt` línea 30; `README.md` línea 43 |
| Q 1.4537 m³/s frente al aforo 1.4362 → +1.2 % | `sile.txt` línea 32; `README.md` línea 43 |
| Bradano antes: 1 de 7 verticales | `README.md` línea 44 |
| Bradano: mitad de los píxeles del bloque (0.5) | `README.md` líneas 55-56 y 86 |
| `FRACCION_ACTIVA_NOCHE` = 0.1 (diez por ciento) | `README.md` líneas 84 y 87 |
| Bradano ahora: 5 de 7, sesgo −4.5 % | `README.md` línea 45; `validacion/salidas/bradano.txt` línea 22 |
| Con 0.1 de día: 14 de 20 estaciones a +36 % (Heiskanen 10 h) | `README.md` líneas 93-95 |
| Heiskanen: 20 estaciones | `validacion/salidas/heiskanen.txt` línea 1 |
| Heiskanen: 6 vídeos, de 08 a 13 h | `heiskanen.txt` líneas 2-25 |
| 08 h: 7/20, −18.4 %; 09 h: 8/20, −13.8 % ("entre 14 y 18 %") | `heiskanen.txt` líneas 48-49; `README.md` línea 46 |
| 10 h: 3 de 20; 11 h y 12 h: 1 estación | `heiskanen.txt` líneas 50-52 |
| 13 h: 15 de 20, +34.7 % ("un 35 %") | `heiskanen.txt` línea 53; `README.md` línea 118 (+35 %) |
| El caudal bajaba ese día (141 → 120 m³/s; no se dice la cifra) | `README.md` línea 78 |
| Zona lejana 20-40 m rechazada; autores 0.24-0.46 donde el ADCP mide ~1.0 ("menos de la mitad") | `README.md` líneas 71-73 |
| 3 de 6 horas sin datos por el sol; "ni en 4K"; polarizador | `README.md` líneas 81-82 |
| Regresión: de día idéntico, el cambio solo toca la noche | `README.md` líneas 105-120 |
| Raspberry Pi OS Lite de 64 bits | `raspberry/LEEME.md` líneas 25-26 |
| Primera subida: unos 10 minutos | `LEEME.md` línea 49 |
| Paquete, finales de línea LF, scp, instalar.sh | `raspberry/subir_a_raspberry.ps1` líneas 43-71, 60-66, 88-94, 96-106 |
| apt, entorno Python con OpenCV sin pantalla, stiv.conf solo si no existe, servicio | `raspberry/instalar.sh` líneas 28-30, 32-36, 39-44, 62-75; `raspberry/requirements-raspberry.txt` línea 2 |
| systemd relanza a los 15 s | `LEEME.md` líneas 100-101 (y `raspberry/stiv.service` líneas 15-16, `RestartSec=15`) |
| Órdenes de stiv.sh | `LEEME.md` líneas 113-127 |
| Dirección RTSP de la cámara; stiv.conf, línea 3) | `LEEME.md` líneas 137-138 y 157-158 |
| Tres contenedores: Pi falsa ARM64, servidor RTSP, cámara simulada | `pruebas_docker/docker-compose.yml` líneas 5-10 y 19 |
| Corte de 8 s: reconecta y vuelve a medir | `LEEME.md` líneas 191-193 |
| Fallos: destroyAllWindows, reloj tras reconectar, cola 600 → 150, 1.3 GB → ~626 MB | `LEEME.md` líneas 194-196 |
| Fallo de la función `Ssh` recursiva | **No está en las copias.** Fuente: `Resumen_cronologico_del_trabajo.md` sección 12.2 (raíz del workspace). En la copia, la función ya se llama `EnPi`: `subir_a_raspberry.ps1` línea 37 |
| No probado: velocidad de la Pi 4, cámara real | `LEEME.md` líneas 198-205 |
| Medir largo y ancho; `escala_verificada` | `LEEME.md` líneas 151-153 |
| Volver a medir `ACTIVIDAD_MIN` con la cámara propia | `LEEME.md` líneas 160-163 |

## Notas para quien graba

- **Heiskanen a la 13 h tiene dos versiones.** La tabla del README (línea 48) dice "16 de 20, +33 %";
  la salida actual (`heiskanen.txt` línea 53) dice "15/20, +34.7 %", y la tabla de regresión del
  mismo README (línea 118) dice "+35 %". El guion dice "quince" y "un 35 %" porque se enseña el
  `.txt`. No señales la línea 48 del README en ese momento.
- **El fallo de la función `Ssh` no está escrito en ningún archivo de esta carpeta.** El LEEME
  (líneas 194-196) solo lista tres fallos. Por eso en la sección 9 se dice de palabra, sin señalar
  nada.
- **`stiv_directo.py` no está en la copia.** No lo busques con `Ctrl+P`: abrirías el de la raíz, con
  otras líneas. `FRACCION_ACTIVA_NOCHE` se enseña solo en el README.
- `Ctrl+P` encuentra varios `README.md` y `LEEME.md` en el workspace. Comprueba siempre la ruta
  antes de abrir.
- En el README de validación hay dos tablas parecidas (líneas 41-48 y 105-120). En la sección 4 vas
  a la 44; en la sección 6, a la 105.
- Las cifras 1.4537 y 1.4362 se leen "uno coma cuatro cinco tres siete" y "uno coma cuatro tres seis
  dos". Si se te traban, basta con "un 1.2 % de diferencia".
- Las grabaciones de los directos (13 GB) no se copiaron: `regresion.py` no se puede ejecutar desde
  esta carpeta. En el vídeo solo se enseña, no se ejecuta.
