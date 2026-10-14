# 07 · River Arrow (HARMONIOUS) -- experimento de siembra de trazador

**Que es.** **No es una medicion, es un experimento.** El dataset publica dos videos del mismo rio,
con la misma camara y el mismo encuadre, que solo se diferencian en si alguien sembro trazador en el
agua. Los dos se procesan con la **misma configuracion exacta**.

| | sin sembrar | sembrado |
|---|---|---|
| Estaciones aceptadas | **0 de 49** | 44 de 49 |
| Coherencia mediana | 0.196 | 0.927 |
| Velocidad media de la seccion | -- | 0.389 m/s frente a 0.417 de referencia (**-6.7 %**) |

**El resultado es negativo a proposito.** El video sin sembrar no se puede medir, y el notebook lo
demuestra sin que el argumento sea circular:
- la **parte 4c** prueba nueve variantes del metodo sobre el video sin sembrar y todas dan 0 de 49;
- la **curva de decorrelacion** muestra que sin siembra no hay patron que seguir ni siquiera entre
  dos fotogramas consecutivos. Lo que lo arreglaria es la adquisicion (sembrar), no el codigo.

En el video sembrado, un **PIV independiente** que no comparte codigo con STIV coincide con STIV a
3 cm/s (r = +0.974), y ambos discrepan de la misma forma del perfil de referencia. Eso apunta a la
referencia (probablemente promediada en profundidad), no al metodo.

**Datos.** Necesita `datos/externos/datasets vision velocimetria/data/RiverArrow/` (ver
`datos/externos/LEEME.md`).

**Como ejecutarlo.** Desde esta carpeta, con el entorno de `requirements_pyorc.txt`:
- `Arrow_STIV_pipeline.ipynb` -- el experimento completo (~50 s).
- `python video_velocidad.py` -- los dos videos lado a lado (~45 s).

Si un cambio llega a hacer que el video sin sembrar "mida", el problema esta en el cambio.
