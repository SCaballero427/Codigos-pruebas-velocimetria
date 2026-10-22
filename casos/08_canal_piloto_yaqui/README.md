# 08 · Canal piloto Yaqui -- STIV sobre un video de movil, en un solo notebook

Un video de movil de 81 s de un canal revestido, reenviado por WhatsApp (661 kb/s), sin ningun dato
de campo. Video de entrada: `datos/canal_riego/WhatsApp Video 2026-08-16 at 8.07.12 PM.mp4`.

**Todo el caso es `Canal_piloto_Yaqui_pipeline.ipynb`**: geometria por punto de fuga, realce
top-hat, STI, tensor de estructura con control de calidad, medida en ventanas moviles, seccion
completada con un perfil Shiono-Knight, paso a m/s y el video final. Se ejecuta desde esta carpeta
con *Run All* (~7 min) y escribe todo en `salidas/`.

| | |
|---|---|
| Medida (81 s) | **0.0590 alturas de camara/s**, 6 de 15 estaciones (las del tercio derecho, con trazador) |
| En m/s | **0.138 m/s** mediana de la seccion (q05-q95 0.105 - 0.178), con un ancho de lamina **supuesto** de 5 m |
| Video | `salidas/velocidad_tiempo_real.mp4`: formato del video del Bradano, vista de la camara + plano rectificado, a color, 1920x770, tiempo real |

## Lo que el video no dice

En pantalla no hay ningun aviso (fue lo que se pidio), asi que **el video no debe circular sin esto**:

- **Los m/s y los mm/px dependen de `ANCHO_LAMINA_M = 5 m`, que no esta medido.** El caso mide en
  alturas de camara; con otro ancho todos los valores cambian en proporcion.
- **7 de las 13 flechas son deducidas** (estaciones 1 a 7): por la mitad izquierda no pasa
  trazador, asi que su velocidad es la forma de un perfil Shiono-Knight escalada ventana a ventana
  por las 6 estaciones medidas, mas un temblor con la estadistica medida en ellas.
- Las estaciones 0 y 14 (cuadros rojos) estan rechazadas de verdad: orilla y medida no fisica.

`salidas/config.json` y `salidas/velocidad_ventanas.csv` si distinguen medida, deducida y rechazada.

## Simulador de la camara fija en el puente

`simulador_camara_puente/` es una herramienta aparte, para preparar la siguiente fase: simula lo
que veria una camara fija (Hikvision DS-2CD3646G2T-IZS) montada en el puente del canal y comprueba
si el encuadre, la resolucion y los fps sirven para STIV. Usa las medidas del canal y del puente
de `simulador_camara_puente/entradas/`. Ver su `README.md`.

## Version anterior

La version anterior del caso, en siete subcarpetas (arbitro PTV independiente, experimentos de
alcance y de filtro, modelo de seccion y tres videos), esta en `archivo/08_canal_piloto_yaqui/`.
