# Referencias

`pyorc_repo/` es un clon de la libreria pyorc original (version `v0.9.8-1-g4cc2628`), **solo para
consulta**: leer su codigo o sus tutoriales en `examples/`, de los que derivan los notebooks de
`casos/01` y `casos/02`. Editarlo no cambia nada; los notebooks usan el pyorc instalado con
`requirements_pyorc.txt`.

Los tutoriales de `examples/` tienen modificaciones locales sin confirmar (ver `git status` dentro de
la carpeta), mas `ngwerere.json`, `ngwerere.jpg` y `ngwerere_camconfig.jpg` sin rastrear.

Para ejecutar las pruebas de la propia libreria (solo para investigar su comportamiento):

```powershell
cd referencias\pyorc_repo
python -m pytest tests/test_velocimetry.py::nombre_del_test
```
