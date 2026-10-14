# Serie: medir la velocidad del agua con una cámara, de LSPIV al programa para ALIAR

Cinco vídeos de unos 10 minutos (unos 50 minutos en total), grabados en una sola toma navegando
VS Code. Cada vídeo tiene su carpeta con **copias de los archivos originales tal como están**, con
sus resultados (notebooks con las salidas guardadas, figuras, CSV, JSON y vídeos), y un
`GUION.md` que dice qué abrir, a qué línea ir y qué decir.

Los números de línea de cada guion son los de **la copia de su carpeta**. Los originales pueden
seguir cambiando; las copias no.

| # | Carpeta | Qué cuenta |
|---|---|---|
| 1 | `video1_LSPIV_pyorc/` | La idea de LSPIV. Ngwerere como comprobación de que sé usar pyorc. El canal USGS: estabilizar el vídeo del dron, la escala con las dos orillas, el coste en memoria, y la regla de abrir la medición de campo solo al final. |
| 2 | `video2_STIV_y_comparacion/` | La imagen espacio-tiempo y el tensor de estructura. El mismo canal con STIV, y la comparación con LSPIV en error, tiempo y memoria. Por qué STIV pasa a ser el método principal. |
| 3 | `video3_casos_dificiles/` | Una lección por caso. Boneyard: cámara inclinada sin medidas, y los muros con coherencia alta. Hommerich: calibración completa, caudal en m³/s. Bradano y Arrow: el trazador. Canal de WhatsApp: compresión y límite de alcance. |
| 4 | `video4_programa_en_directo/` | `stiv_directo.py`: qué muestra, la configuración por cámara (la de ALIAR será una cámara nueva por RTSP), la geometría, los hilos, la medida y los problemas del directo ya resueltos. |
| 5 | `video5_validacion_e_instalacion/` | El mismo programa con vídeos que tienen medición de campo (canal USGS, Bradano, Heiskanen), las lecciones para el sitio de ALIAR, y la instalación en la Raspberry con su prueba en Docker. |

**Fuera de la serie:** la detección de nivel, el filtro adaptado, la simulación de sección
completa, el árbitro PTV en detalle y la noche mal medida del Myoshoji.

**No copiado (son entradas, no resultados, y pesan mucho):**
- los vídeos estabilizados `.mkv` del canal USGS (1.1 GB cada uno);
- las grabaciones de `validacion/grabaciones/` (13 GB);
- los datasets de `datasets vision velocimetria/` (45 GB).

**Vídeos `.mp4` de resultados:** VS Code no los reproduce. Si se quiere enseñar alguno, se abre
con el reproductor de Windows; en los guiones es un paso opcional.

**Git:** esta carpeta no está en `.gitignore`. Algunos `.mp4` de Boneyard superan los 100 MB,
el límite de GitHub, así que no conviene hacer `git add` de la carpeta entera.
