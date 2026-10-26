# Noche: 24 h grabadas de las cuatro camaras (2026-10-24/25)

Objetivo: que cada camara mida de noche con velocidades **coherentes con las de dia al mismo nivel**.
Resultado: **ninguna lo consigue con estas imagenes**, y dos de ellas (Myoshoji y Shimoda) daban de
noche medidas falsas que el programa aceptaba. Se corrigio eso: ahora de noche las cuatro se abstienen.
De dia el programa mide exactamente lo mismo que antes (regresion 9 de 9 identica).

## Lo que se grabo

`verificacion_nivel/grabaciones/` (fuera de git, ~46 GB):

| Archivo | Contenido |
|---|---|
| `<camara>_20261024_0525JST.ts` / `_0537JST.ts` | el directo tal cual (segmentos HLS de YouTube, sin recomprimir), 05:25 del 24 a 05:24 JST del 25 |
| `..._segmentos.csv` | hora de descarga y bytes de cada segmento de 5 s |
| `..._JST.json` | resumen y huecos |
| `<camara>_20261024_0529JST_nivel.csv` / `.json` | nivel oficial (y lluvia en Akigawa) minuto a minuto: `verificacion_nivel/grabar_nivel.py` |

- Hueco de **09:24 a 11:33 JST** en las cuatro (el PC se suspendio); el resto, < 1.5 min perdidos por camara.
  La noche (17:30-05:24 JST) esta completa (11.8 h de 11.9).
- El sistema oficial (水防災総合情報システム) publica **solo nivel y lluvia**, no velocidad ni caudal.
  Kurome, Shimoda y Akigawa marcaron 0.00 m todo el dia (agua por debajo del sensor): no sirven.
- **Llovio de 8 a 14 h.** El Myoshoji paso de 1.21 m (manana) a 1.28-1.29 m (14-0 h) y volvio a
  1.21-1.23 m de madrugada. Por eso cada tramo de noche se compara con el dia **del mismo nivel**: la
  primera mitad de la noche con la tarde (15 y 16 h), la madrugada con la manana (6:30 y 7:30). Para las
  otras camaras (sin nivel util) se asume la misma evolucion. El Shimoda lo confirma: de dia paso de
  0.91-1.01 m/s en el centro (manana) a 1.24-1.36 (tarde).

## Como se analizo

- `tramo.py`: un tramo por hora JST. **En estas .ts no se puede saltar con `CAP_PROP_POS_MSEC`**: el PTS
  sigue al reloj real, los huecos son saltos de PTS y OpenCV cae en otro sitio (pedido 20000 s -> 25930 s).
  El tramo se copia byte a byte con el `_segmentos.csv` (cada segmento empieza por un fotograma clave):
  exacto y sin recomprimir.
- `barrido.py`: tramos de 3 min (se descartan los primeros 60 s, hasta llenar las tres escalas), por
  variante, en paralelo, un json por tramo en `resultados/<variante>/` (y el STI de la ultima medida).
  **Tramos de ajuste** (19:00, 23:00, 03:00) y **de comprobacion** (21:00, 01:00, 04:30) separados: las
  variantes se eligieron mirando solo los de ajuste.
- Referencia de dia con el programa de antes: tramos de 6:30, 7:30, 13:00, 15:00 y 16:00.

## Antes: lo que hacia el programa de noche (`resultados/base/`)

| Camara | Dia (m/s, estaciones que miden) | Noche con el programa de antes | |
|---|---|---|---|
| Myoshoji | 0.45-0.55 (0-5) | de 19 a 1 h la tomaba **por dia** (en color, brillo 83-86) y **aceptaba 0.05-0.10 m/s** en 3-4 estaciones (destellos de farola); de madrugada, modo noche y `noche_no_valida` | **falso** |
| Kurome | 0.71-1.00 (1-2, 7-8; tarde 1-8) | infrarrojo: `sin_textura` en todo | no mide |
| Shimoda | manana 0.50-1.01, tarde 0.74-1.36 | **aceptaba el 100 %** a 0.45-0.81: un 25-45 % menos que de dia, y casi igual toda la noche aunque el caudal cambio un 35 % | **falso** |
| Akigawa | no mide (coherencia) | no mide; la tomaba por dia (focos sobre el rio) | no mide |

## Variantes probadas (tramos de ajuste)

| Variante | Myoshoji | Kurome | Shimoda (centro, noche/dia) | Akigawa |
|---|---|---|---|---|
| proceso de noche forzado | se abstiene | sin textura | 0.6-0.7 | coherencia |
| proceso de dia forzado | destellos 0.05-0.09 | 1-37 % a 0.46-1.15, disperso | 0.75-0.85 | coherencia |
| dia + motas | destellos | disperso | igual | coherencia |
| dia sin reflejos (brillo > 60 o > 40 fuera) | destellos 0.06-0.08 | sin textura | 0.75-0.86 | sin textura |
| noche con actividad minima 0.2 (en vez de 0.5) | se abstiene | sin textura | 0.6-0.7 | coherencia |
| dia con actividad minima 0.2 | destellos | 1-31 %, 0.45-1.10 | 0.75-0.85 | coherencia |

Ninguna da valores de noche dentro de un +-10 % del dia en ninguna camara. Por que:

- **Myoshoji**: con farolas lo unico visible en el agua son destellos sobre ondulaciones casi fijas
  (lo que ya se vio el 2026-10-14 en `verificacion_nivel/`). Ningun proceso los convierte en corriente.
- **Shimoda**: en el STI de dia hay estelas finas y rapidas junto a otras mas inclinadas; de noche la
  farola solo ilumina una franja y solo quedan las inclinadas (ondas grandes, mas lentas que el agua).
- **Kurome**: el infrarrojo deja el agua lisa; el codec la congela y no hay textura que seguir.
- **Akigawa**: no mide ni de dia (ver el README del caso): sin referencia, no hay nada que comprobar.

## La prueba decisiva: el amanecer (`resultados/dia/`, `resultados/sol_menos6/`)

En 30-40 min el caudal no cambia y la luz si. Shimoda, estacion 4, proceso de dia:

| Hora JST | 05:26 | 05:40 | 05:55 | 06:10 | 06:30 |
|---|---|---|---|---|---|
| sol (grados) | -6 | -4 | -1 | +2 | +5 |
| v (m/s) | 0.75 | 0.79 | 0.92 | 0.94 | 1.02 |
| respecto a 06:30 | -25 % | -22 % | -10 % | -8 % | |

El valor sube con la luz: el sesgo es del metodo con poca luz, no del rio. Y el programa de antes ya
daba "dia" a las 05:40 (la imagen tenia brillo de sobra), aceptando un -22 %. Al atardecer pasa lo mismo
pero ahi el caudal tambien bajaba tras la lluvia, asi que no separa una cosa de la otra.

Un **factor de correccion noche/dia** no es defendible con esto: solo hay una transicion limpia (el
amanecer), y de noche el valor apenas sigue al caudal (0.85 a las 19 h, 0.78 a las 3 h, con el dia
pasando de 1.36 a 1.01). Haria falta comprobarlo en varias transiciones y con caudales distintos.

## Cambios

En `stiv_directo.py`:

- **La noche se decide tambien por el sol** (`altura_sol`, `SOL_NOCHE` = 0: de la puesta a la salida),
  con las coordenadas de cada camara (`lat`, `lon` en `CAMARAS`, de la ficha del sistema de Tokio) y la
  hora del fotograma (la del PC en directo; la de la grabacion con `--hora-inicio`). La imagen sigue
  valiendo como antes (infrarrojo u oscura); una camara sin coordenadas usa solo la imagen. 0 y no -6:
  ver la tabla del amanecer.
- **Shimoda `medir_noche: False`**, como el Myoshoji.
- `--hora-inicio` (con `--archivo`: hora real del primer fotograma; el CSV lleva entonces la hora de la
  grabacion y el sol se calcula a esa hora) y `--csv` (otro CSV que `salidas/<camara>/medidas_directo.csv`).

En el resto: `validacion/correr.py` admite `inicio_s` (saltar al empezar; **no sirve** en las .ts con
huecos, ver arriba) y `hora_inicio` (el sol tambien offline); `verificacion_nivel/grabar_directo.py`
reintenta un segmento que falla (un 503 suelto de YouTube corto la grabacion del Kurome a los 10 min);
`verificacion_nivel/grabar_nivel.py` es nuevo.

**Con el programa corregido** (`resultados/nuevo/`), en los tramos de ajuste y de comprobacion: de noche
las cuatro se abstienen (`noche_no_valida`, `sin_textura` o `coherencia`; solo el Kurome acepta un 2-7 %
a las 04:30, a 0.73-0.79, como de dia). De dia, igual que antes (06:10: Myoshoji 0.44-0.49, Kurome
0.74-0.86, Shimoda 0.48-0.96).

**Regresion** (`validacion/regresion.py`, los 9 casos de `validacion/regresion_casos.py`): identica en los
nueve (aceptadas y medianas por estacion), guardada antes en `validacion/salidas/antes_noche24h/`.

## STIV completo de las 24 h con el programa corregido (`reproduccion/`)

`python reproducir.py --rapido` (2026-10-25/26): `stiv_directo.py --archivo ... --hora-inicio ... --csv`
sobre las grabaciones, en 20 trozos paralelos. 16.3 h de reloj, de las que ~8 h el PC estuvo suspendido
(el lanzador pedia no suspender el sistema, pero no la pantalla: corregido); procesando, ~8 h. Un CSV
por camara (`reproduccion/<camara>.csv`, hora JST real en `hora_local`) y la tabla por horas en
`reproduccion/resumen_horario.csv`.

| Camara | Dia: estaciones-medida aceptadas | Noche: aceptadas | Dia, mediana de la seccion |
|---|---|---|---|
| Myoshoji | 74 % | 0.1 % (75 de 121 599) | 0.43-0.45 m/s con 1.21 m, 0.47-0.49 con 1.26-1.29 m |
| Kurome | 51 % (manana solo est. 1-2 y 7-8; tarde 1-8) | 0.2 % | 0.75-0.78 manana, 0.81-0.84 a las 13-15 h |
| Shimoda | 95 % | 0.1 % | 0.86-0.90 manana, 1.04-1.13 a las 13-16 h |
| Akigawa | 0.0 % | 0.0 % | no mide |

- **De dia la velocidad sigue al rio**: las tres camaras que miden suben a la vez tras la lluvia de 8-14 h
  (Shimoda +25 %, Kurome +10 %, Myoshoji +10 % con +8 cm de nivel) y vuelven al bajar.
- **De noche se abstienen**: lo que se acepta son medidas sueltas (< 0.2 %), sin peso en ninguna hora.
- En el Myoshoji las estaciones 6-8 (sombra junto al muro derecho) dan 0.05-0.09 m/s todo el dia: son
  las burbujas que mide el reintento de motas, ya descrito en el README del caso; no son la corriente
  principal.
- Sin `--tiempo-real` el programa mide cuando el hilo de medida queda libre: 300-3600 medidas por hora y
  camara segun la carga del PC, en vez de 3600.

## Lo que queda abierto

- Medir de noche necesita **otra imagen**, no otro proceso: iluminacion infrarroja propia que haga
  visible la textura del agua sin destellos fijos (lo mismo que dice el README del caso para ALIAR), o
  una camara termica.
- El crepusculo tiene sesgo aunque haya luz de sobra para la imagen (-8 a -10 % con el sol a -1/+2
  grados en el Shimoda). No se corrigio: `SOL_NOCHE` = 0 lo deja dentro.
- El factor noche/dia: acumular transiciones (cada amanecer y atardecer grabado) antes de pensar en el.

## Archivos de esta carpeta

| | |
|---|---|
| `tramo.py` | un tramo por hora JST (clip por bytes) por el programa; `--csv`, `--sti` |
| `barrido.py` | variantes x camaras x tramos en paralelo; `resumen <variante>` y `transicion <variante>` |
| `reproducir.py` | STIV completo de las 24 h con `stiv_directo.py`: `--rapido` (trozos en paralelo) o a velocidad real |
| `resultados/` | un json por variante, camara y tramo, y los STI |
| `clips/` | los tramos copiados (se pueden borrar: se rehacen solos) |
