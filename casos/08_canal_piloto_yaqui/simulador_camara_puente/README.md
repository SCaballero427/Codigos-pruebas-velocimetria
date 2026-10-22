# 08 · Simulador de la camara fija en el puente del canal Yaqui

Herramienta para decidir **donde y como montar una camara fija en el puente del canal** antes de
instalarla, para medir con STIV. No mide nada: simula lo que veria la camara y comprueba si el
encuadre, la resolucion y los fps sirven para el algoritmo.

```powershell
cd casos\08_canal_piloto_yaqui\simulador_camara_puente
python simulador_stiv_puente.py          # interfaz
python simulador_stiv_puente.py --test   # autocomprobacion (19 pruebas), sin interfaz
```

Solo usa la biblioteca estandar de Python 3 (tkinter incluido). No necesita el entorno de pyorc.

## Que responde

1. **Cobertura**: si se ve el ancho de agua entero y el canal de borde a borde, y en que tramo
   desde el puente.
2. **Resolucion en el agua** (cm/px), a lo largo del flujo y a lo ancho, en cada linea de busqueda.
3. **Chequeo STIV**: desplazamiento en px/imagen y angulo del patron en la STI para la velocidad
   minima y maxima, error de velocidad, y que paso de imagenes k, fps o S_x hacen falta.

Vistas: perfil longitudinal, planta con la huella del campo de vision, seccion transversal con la
pasarela, imagen simulada con las lineas, lupa a la resolucion real del sensor y panel STIV. Las
formulas (F1-F14) estan en la cabecera del script.

## Entradas (`entradas/`)

| Archivo | Datos que se usan |
|---|---|
| `Medidas_canal_y_puente.pdf` | 11.4 m entre bordes, 3 m de la plantilla al puente, puente de 0.85 m |
| `DS-2CD3646G2T-IZS_TPM_Datasheet_20261204.pdf` | sensor 1/1.8", 2688 x 1520, lente 2.7-13.5 mm, 30 fps (60 Hz) o 25 fps (50 Hz) |

**Los FOV de la ficha no se usan**: son incoherentes entre si (con pixel cuadrado,
tan(HFOV/2)/tan(VFOV/2) debe valer 1.77 y la ficha da 2.58 a 2.7 mm). El FOV se calcula de la
focal y de un pixel de 2.9 um (el de los sensores 1/1.8" de 2688 x 1520; no viene en la ficha):
110.6 x 78.5 grados a 2.7 mm.

## Valores supuestos (`>>> AJUSTABLE <<<`)

No estan medidos y cambian los resultados; hay que sustituirlos por medidas de campo:

| Valor | Supuesto | Efecto |
|---|---|---|
| Talud | 1.5:1 | de el sale la plantilla: 11.4 - 2 x 1.5 x 3 = 2.40 m |
| Tirante de operacion | 2.0 m | ancho de agua 8.40 m |
| Camara sobre el piso del puente | 1.0 m | 4.85 m sobre la plantilla |
| Posicion | centro del claro, mirando aguas arriba | |
| Pixel del sensor | 2.9 um | FOV calculado |
| Umbrales de calificacion | angulo 20-70 / 10-80 grados, trazador 2/1 px, linea 60/30 px | criterio propio, no norma |
| Dibujo de la pasarela | piso 1.2 m, baranda 1.1 m, paneles 0.85 m | solo el dibujo |

Tambien es una interpretacion que los 11.4 m son de borde a borde y los 3 m la altura de los bordes.

## Resultado con los valores iniciales (2.7 mm, 30 fps)

- Seccion de medida a 3.5 m del puente, camara inclinada 39.2 grados.
- Ancho de agua entero visible desde 1.4 m; el borde superior de la imagen llega al horizonte.
- 0.72 cm/px a lo largo del flujo en la linea central.
- 0.1 m/s queda a 15 grados en la STI y 2 m/s a 80: con un solo ajuste no se cubre todo el rango;
  para 2 m/s hace falta S_x >= 2.4 cm/px o mas fps, y para 0.1 m/s un paso k de ~3.

Con talud 1.0-2.0, tirante 0.5-2.8 m, camara 0.5-1.5 m sobre el piso, +-3 grados de error de
instalacion o focal real 2.6-2.85 mm, las lineas siguen cabiendo y el ancho de agua se ve entero;
la resolucion queda entre 0.68 y 0.92 cm/px.

## Verificacion

Ademas de `--test`, la geometria se comprobo contra un calculo a mano, una reimplementacion de la
proyeccion con matrices de rotacion (convencion OpenCV, 20 000 puntos: diferencia < 1e-8 px), un
barrido por fuerza bruta de la cobertura y las orillas de la imagen renderizada (< 0.5 px).

## Limitaciones conocidas

- **Lente sin distorsion.** A 2.7 mm la lente real tiene distorsion de barril (la ficha da 130.9
  grados de diagonal frente a 117.7 sin distorsion): hacia los bordes de la imagen las orillas se
  veran curvas y la escala cambia. Para resultados exactos hay que **calibrar la camara** (tablero
  de ajedrez + OpenCV) con el zoom elegido.
- El puente no tapa nada en la simulacion: si la camara va por dentro de la baranda y mira muy
  inclinada, en el borde inferior de la imagen se vera el piso o la armadura.
- Canal recto y prismatico, agua plana; sin compresion de video, desenfoque por obturacion,
  reflejos ni sombras.
- Antes de dar por buena la instalacion, poner marcas a distancias conocidas en las dos orillas y
  comparar su posicion en la imagen real con la simulada.
