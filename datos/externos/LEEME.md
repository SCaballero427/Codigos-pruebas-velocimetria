# Datos externos (no copiados)

Aqui va la carpeta **`datasets vision velocimetria/`** (46 GB) con los datasets descargados. No se
copio para no duplicar 46 GB en el disco; sigue en la carpeta original
(`test_pyorc-20261009T172625Z-1-001\test_pyorc\datasets vision velocimetria\`).

Para que los casos que la usan funcionen, **mover** (no copiar) esa carpeta entera aqui, conservando
su nombre:

```
datos/externos/datasets vision velocimetria/
    Boneyardcreek/          -> casos/04_boneyard_stiv
    Hommerich/              -> casos/05_hommerich_stiv
    data/RiverBradano/      -> casos/06_bradano_stiv  y  casos/09_directo_tokio/validacion
    data/RiverArrow/        -> casos/07_arrow_siembra
    Heiskanen_et_al_.../    -> casos/09_directo_tokio/validacion
    data/ (13 rios HARMONIOUS), Field_Videos/, 15002591.zip, ...
```

El codigo ya apunta a estas rutas: no hay que tocar nada mas.

## De donde sale cada dataset

| Carpeta | Origen |
|---|---|
| `data/` | HARMONIOUS, intercomparacion de velocimetria por imagen (13 rios, videos ya ortorrectificados, sin batimetria) |
| `Boneyardcreek/` | USGS, Boneyard Creek at Urbana, doi:10.5066/P9VZ6VYM (61 videos + GH y Q por video) |
| `Hommerich/` | Geul en Hommerich (NL), muestra de pyorc con camara calibrada y 6 GCPs RTK |
| `Heiskanen_et_al_river_flow_camera_data/` | Oulankajoki (Finlandia), camara IP + ADCP |
