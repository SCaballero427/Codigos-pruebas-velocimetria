# 08 · Canal de riego -- seis carpetas sobre un solo video de WhatsApp

Un video de movil de 81 s de un canal de riego revestido, sin ningun dato de campo: ni puntos de
control, ni ancho medido, ni seccion, ni aforo. Es el caso con menos informacion de todo el proyecto.
Video de entrada: `datos/canal_riego/WhatsApp Video 2026-08-16 at 8.07.12 PM.mp4`.

**Solo `medicion/` es el caso.** Las otras cinco carpetas son experimentos o presentaciones sobre el
mismo video, e **importan** el codigo de `medicion/` en vez de copiarlo: cambiar un parametro alli lo
cambia en todas.

| Orden de lectura | Carpeta | Tipo | Que aporta |
|---|---|---|---|
| 1 | `medicion/` | **caso** | v mediana **0.0590 alturas de camara/s**, 6 de 15 estaciones; arbitro PTV independiente r = +0.984 |
| 2 | `experimentos/alcance/` | experimento | hasta donde llega STIV aguas arriba: por debajo de ~0.2 px por paso todo es aliasing, con coherencia altisima |
| 3 | `experimentos/filtro/` | experimento | ultimo intento sobre el campo lejano; demuestra que lo borra la **resolucion**, no la compresion |
| 4 | `completo_con_modelo/` | caso + **simulacion** | barras de error por estacion y un modelo Shiono-Knight para el 64 % del ancho sin trazador |
| 5 | `presentaciones/stiv_puro/` | video | solo lo medido: flechas, la STI de cada flecha y huecos donde no se mide |
| 6 | `presentaciones/seccion_completa/` | video | flechas en las 15 estaciones, 9 de ellas **deducidas** y dibujadas igual que las medidas. Sin aviso en pantalla, por peticion expresa: no difundir el video sin su README |

Que codigo importa cada carpeta:

| Carpeta | Importa de |
|---|---|
| `experimentos/alcance/` | `medicion/` |
| `experimentos/filtro/` | `medicion/` |
| `completo_con_modelo/` | `medicion/` y `experimentos/filtro/` (el filtro adaptado) |
| `presentaciones/stiv_puro/` | `medicion/` |
| `presentaciones/seccion_completa/` | `medicion/` y `completo_con_modelo/` (la forma del perfil y su configuracion) |

Cada carpeta tiene su propio `README.md` con la explicacion completa. Todo se ejecuta desde la
carpeta correspondiente con el entorno de `requirements_pyorc.txt`.
