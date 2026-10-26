"""Diferencias de codigo entre versiones consecutivas de los notebooks de velocimetria.

Para cada par v(N-1) -> vN escribe en cambios/ el diff unificado de las celdas de codigo (sin
salidas ni texto) y resume cuantas lineas se anaden, se quitan y se conservan. Ademas sigue, version
a version, las funciones del nucleo del metodo (de `mapa_lineas` a `medir_sti`): si se crean, si
cambian o si pasan intactas. Las marcas `# [vN]` son anotaciones y no cuentan como cambio.

Uso, desde esta carpeta:  python comparar_versiones.py
"""
import ast
import difflib
import json
import re
from pathlib import Path

DIR = Path(__file__).resolve().parent
SALIDA = DIR / "cambios"

# Las funciones que son el metodo, en el orden en que actuan.
NUCLEO = ["mapa_lineas", "mapa_banda", "construir_sti", "preparar_sti", "tensor_estructura",
          "medir_sti", "medir_video", "medir_ventana", "medir_en_directo"]


def sin_marcas(linea):
    """Quita las anotaciones de version: '# [vN] ...' al final y '[vN] ' en los textos."""
    linea = re.sub(r"\s*# \[v\d\].*$", "", linea)
    return re.sub(r"\[v\d\] ?", "", linea).rstrip()


def codigo(notebook):
    """Lineas de codigo del notebook, celda tras celda, sin salidas ni marcas de version."""
    nb = json.loads(notebook.read_text(encoding="utf-8"))
    lineas = []
    for celda in nb["cells"]:
        if celda["cell_type"] == "code":
            fuente = celda["source"]
            texto = "".join(fuente) if isinstance(fuente, list) else fuente
            lineas += [sin_marcas(l) for l in texto.splitlines()] + [""]
    return lineas


def funciones(lineas):
    """{nombre: arbol} de las funciones de primer nivel, sin docstring: los comentarios y la
    documentacion no cuentan como cambio de codigo."""
    arbol = ast.parse("\n".join(lineas))
    salida = {}
    for n in arbol.body:
        if isinstance(n, ast.FunctionDef):
            cuerpo = n.body
            if cuerpo and isinstance(cuerpo[0], ast.Expr) and isinstance(cuerpo[0].value, ast.Constant):
                n.body = cuerpo[1:]
            salida[n.name] = ast.dump(n)
    return salida


def main():
    notebooks = sorted(DIR.glob("v*_*/velocimetria_v*.ipynb"),
                       key=lambda p: int(p.stem.rsplit("v", 1)[1]))
    SALIDA.mkdir(exist_ok=True)
    codigos = [codigo(nb) for nb in notebooks]
    nombres = [nb.parent.name for nb in notebooks]

    filas = []
    for i in range(1, len(notebooks)):
        a, b = codigos[i - 1], codigos[i]
        diff = list(difflib.unified_diff(a, b, nombres[i - 1], nombres[i], lineterm="", n=2))
        archivo = f"{nombres[i - 1].split('_')[0]}_a_{nombres[i].split('_')[0]}.diff"
        (SALIDA / archivo).write_text("\n".join(diff) + "\n", encoding="utf-8")
        anadidas = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
        quitadas = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
        iguales = sum(n for _, _, n in difflib.SequenceMatcher(None, a, b, autojunk=False)
                      .get_matching_blocks())
        filas.append((nombres[i - 1], nombres[i], len(b), anadidas, quitadas, iguales))

    cab = f"{'de':<20}{'a':<20}{'lineas':>8}{'anadidas':>10}{'quitadas':>10}{'conservadas':>13}"
    texto = ["Todo el codigo de cada notebook", "", cab, "-" * len(cab)]
    for de, a, n, mas, menos, igual in filas:
        texto.append(f"{de:<20}{a:<20}{n:>8}{mas:>10}{menos:>10}{100 * igual / n:>12.0f}%")

    # El nucleo: que version crea, cambia o hereda intacta cada funcion.
    fun = [funciones(c) for c in codigos]
    versiones = [n.split("_")[0] for n in nombres]
    texto += ["", "Funciones del nucleo ('nueva', 'cambia', '=' identica a la version anterior)", ""]
    cab = f"{'funcion':<20}" + "".join(f"{v:>8}" for v in versiones)
    texto += [cab, "-" * len(cab)]
    for nombre in NUCLEO:
        celdas, previa = [], None
        for f in fun:
            fuente = f.get(nombre)
            if fuente is None:
                celdas.append("")
            elif previa is None:
                celdas.append("nueva")
            else:
                celdas.append("=" if fuente == previa else "cambia")
            previa = fuente
        texto.append(f"{nombre:<20}" + "".join(f"{c:>8}" for c in celdas))

    (SALIDA / "resumen.txt").write_text("\n".join(texto) + "\n", encoding="utf-8")
    print("\n".join(texto))
    print(f"\nDiffs en {SALIDA}")


if __name__ == "__main__":
    main()
