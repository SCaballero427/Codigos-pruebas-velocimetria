# Evolucion del algoritmo de velocimetria

Los nueve casos de `casos/` reescritos como **nueve versiones de un mismo codigo**. La v1 es la
primera prueba (Ngwerere, LSPIV con pyorc) y cada version siguiente es **la anterior con los cambios
que obliga su caso, y solo esos**: lo que no hace falta tocar se queda igual, linea por linea. Cada
notebook explica al principio que cambia respecto a la version anterior y por que, y marca en el
codigo las lineas nuevas o cambiadas con `# [vN]`.

No sustituye a `casos/`: alli esta cada caso tal como se resolvio, con su propia rama de codigo. Aqui
el codigo es uno solo y los resultados pueden diferir algo de los originales; cada notebook lo dice.

## Las versiones

| Version | Carpeta | Caso | Lo que cambia (y lo obliga el caso) | Resultado | Caso original |
|---|---|---|---|---|---|
| v1 | `v1_ngwerere_lspiv` | Ngwerere, camara fija oblicua, 4 GCPs | (la prueba de partida: LSPIV con pyorc) | Q 0.1530 m3/s, -6.7 % frente al ejemplo publicado | 0.1672 (+1.9 %) |
| v2 | `v2_smc_lspiv` | Sile Main Canal, dron cenital | 2 GCPs en modo cenital, video ya estabilizado, mascara de angulo aplicada, seccion del aforo con `s=`, recursos y comparacion final con el aforo ADV | Q 1.4545 m3/s, **+1.3 %** | +1.4 % |
| v3 | `v3_smc_stiv` | el mismo video que v2 | **cambio de nucleo**: LSPIV -> STIV sobre OpenCV (lineas de busqueda, STI, tensor de estructura, coherencia, trapecios). Mismo video, escala, seccion y `V_CORR` | Q 1.4484 m3/s, **+0.9 %** | +0.8 % |
| v4 | `v4_boneyard_stiv` | Boneyard Creek, oblicua sin geometria | rectificacion por **punto de fuga**; derivadas por **diferencias centrales** con suavizado opcional (0 aqui: la Sobel de v3 dispersa el perfil con espuma fina); criterio de **contraste temporal** (los muros aprueban la coherencia con v = 0); sin seccion, sin caudal | 0.2375 alturas de camara/s, 9 de 21 | 0.2427, 15 de 21 |
| v5 | `v5_hommerich_stiv` | Geul, camara calibrada | `solvePnP` con distorsion y rectificacion por **mapa** (`remap`); bloque de 32 (video de 4 s); suavizado de vuelta a 1.5; contraste a 3.0; vuelve el caudal con relleno hacia las orillas naturales | Q 12.92 m3/s, sin referencia | 13.68 (otra configuracion) |
| v6 | `v6_bradano_stiv` | Bradano, ya ortorrectificado, trazador disperso | **banda** de lineas normalizadas y promediadas; video entero y bloque 64; el contraste se invierte y se sustituye por el **brillo** | 5 de 7 verticales, sesgo **-3.5 %**, r 0.994 | -3.1 %, r 0.996 |
| v7 | `v7_arrow_siembra` | Arrow, sembrado y sin sembrar | dos videos con la misma configuracion (`medir_video`); un angulo por seccion; **cobertura** por muestra; bloque 24; curva de decorrelacion y PIV ensemble como arbitro | sin sembrar **0 de 49**; sembrado 38 de 49; STIV-PIV r 0.975 | 0 de 49; 44 de 49; 0.974 |
| v8 | `v8_canal_yaqui` | canal de riego, movil y WhatsApp | orillas y punto de fuga (homografia de v4) con mapa de v5; **top-hat** contra el codec; **estabilizacion** sobre el mapa; **seleccion de bloques por senal**; densidad de trazador; coherencia 0.60 | 0.0571 alturas de camara/s, 6 de 15 | 0.0590, 6 de 15 |
| v9 | `v9_directo_tokio` | directo de Tokio (Myoshoji) | **motor en tiempo real**: presets por fuente, solo fotogramas reales (cadencia medida), cuadrilatero con dimensiones supuestas, muestreo directo en la imagen, buffer de 10 s y una medida por segundo, **mascara de actividad** contra el agua congelada por el codec | 0.472 m/s (escala supuesta), 6 de 9; **Sile sin estabilizar: Q +2.3 %** | 0.492 m/s; Sile +1.2 % |

## Que funciones del metodo cambian, y cuando

Lo genera `comparar_versiones.py` (en `cambios/resumen.txt`), comparando el codigo sin comentarios
ni marcas de version:

```
funcion                   v1      v2      v3      v4      v5      v6      v7      v8      v9
mapa_lineas                            nueva  cambia       =       =       =       =       =
mapa_banda                                                     nueva  cambia       =       =
construir_sti                          nueva  cambia  cambia       =       =  cambia
preparar_sti                           nueva       =       =       =       =       =       =
tensor_estructura                      nueva  cambia       =       =       =       =  cambia
medir_sti                              nueva  cambia       =       =  cambia  cambia  cambia
medir_video                                                            nueva  cambia
medir_ventana                                                                          nueva
medir_en_directo                                                                       nueva
```

`cambios/vN_a_vM.diff` tiene el diff completo de codigo entre cada par de versiones.

## Lo que la serie ensena

- **El nucleo apenas cambia.** STI por linea, tensor de estructura por bloques con 50 % de solape y
  mediana ponderada por coherencia: es el mismo de la v3 a la v9. `preparar_sti` no cambia nunca.
- **Lo que mas evoluciona es quien tiene derecho a votar**, y siempre por la misma trampa: algo que no
  se mueve dibuja una estela vertical perfecta (coherencia alta, velocidad cero). Muros (v4: contraste
  temporal), grava (v6: brillo), residuo de fondo bajo el top-hat (v8: solo bloques con particula) y
  agua congelada por el codec (v9: pixeles activos).
- **El suavizado previo a las derivadas es un parametro del caso, no del metodo.** Sin suavizado, las
  pendientes lejos de 45 grados se comprimen hacia 1 (Sile, Bradano); con suavizado, la espuma fina de
  Boneyard se pierde frente a estructuras mas gruesas. La v4 lo mide con las STI de la v3.
- **Los parametros de escala siguen al video**: el bloque del tensor va de 64 a 32 (122 fotogramas), a
  24 (99 fotogramas) y vuelve a 64.
- **Hallazgos de esta reescritura**: el LSPIV de pyorc sobre Ngwerere varia ~7 % entre ejecuciones
  identicas (no 1-2 %); y los directos de YouTube no repiten siempre igual los fotogramas (cada 2 en el
  video de prueba de Myoshoji, cada 3 en la grabacion de 60 s), asi que la cadencia fija por camara del
  programa original no vale para todas sus grabaciones.

## Como se ejecuta

Cada notebook se ejecuta **desde su propia carpeta**, con el entorno de `requirements_pyorc.txt`
(`entorno_pyorc/` en la raiz). Los notebooks ya estan ejecutados y `salidas/` tiene sus figuras y
tablas: no hace falta ejecutar nada para ver los resultados.

| Version | Necesita | Tiempo aproximado |
|---|---|---|
| v1 | `datos/ngwerere/` | 4-7 min |
| v2, v3 | `casos/02_smc_pyorc/entradas/SMC_estabilizado.mkv` y `datos/USGS/` | 12 min y 2-6 min |
| v4 a v7 | la carpeta de datasets externos (ver abajo) | 1-2 min cada una |
| v8 | `datos/canal_riego/` | 2-3 min |
| v9 | `casos/09_directo_tokio/raspberry/prueba/myoshoji_20s.mp4` y el video original del Sile en `datos/USGS/Video/` | 2 min |

**Datasets externos (v4 a v7).** Se buscan en `datos/externos/datasets vision velocimetria/`, despues
en la variable de entorno `DATASETS_VELOCIMETRIA` y por ultimo en la carpeta de la que se copio el
workspace (`../test_pyorc-20261009T172625Z-1-001/test_pyorc/datasets vision velocimetria`).

**Orden.** La v3 lee el resultado de la v2 para compararlos; la v4 reutiliza las STI de la v3 para su
prueba de regresion; la v9 lee el caudal de la v3. Sin ellos, esas celdas se saltan la comparacion.

Despues de cambiar cualquier notebook, `python comparar_versiones.py` (desde esta carpeta) regenera
`cambios/`.
