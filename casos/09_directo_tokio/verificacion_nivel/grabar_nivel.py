"""Registra el nivel oficial (y la lluvia, donde la hay) de las estaciones de las camaras durante N
minutos, para acompanar a las grabaciones de grabar_directo.py. Fuente: Sistema de informacion de
prevencion de inundaciones del Gobierno de Tokio (水防災総合情報システム, Oficina de Construccion).

    python grabar_nivel.py                          # las 4 camaras, 24 h
    python grabar_nivel.py --camaras myoshoji --minutos 120

La pagina de cada estacion (tsim0105g_<codigo>.html) da el nivel de los ultimos 24 min minuto a
minuto, de las ultimas 4 h cada 10 min y de las ultimas 24 h cada hora. Se consulta cada 5 min y se
anaden las lecturas nuevas (sin repetir) a grabaciones/<camara>_<AAAAMMDD_HHMM>JST_nivel.csv:
hora JST de la lectura, paso (1m/10m/1h), variable, valor tal cual (texto si es "欠測" = falta).
El .json de al lado guarda la ficha de la estacion (A.P. del cero, umbrales, notas de la pagina).
NO hay velocidad ni caudal: el sistema solo publica nivel y lluvia. Python puro, sin dependencias.
"""
import argparse, csv, json, os, re, sys, time, urllib.request
from datetime import datetime, timedelta, timezone

AQUI = os.path.dirname(os.path.abspath(__file__))
for _f in (sys.stdout, sys.stderr):
    _f.reconfigure(encoding="utf-8", errors="replace")

JST = timezone(timedelta(hours=9))
BASE = "https://www.kasen-suibo.metro.tokyo.lg.jp/im/uryosuii/tsim0105g_{}.html"
# camara -> codigo de la pagina integrada de la estacion (arrryTougouCd en tsim0102g.html). Las
# estaciones de nivel tienen el mismo nombre que la camara: 上高田上 (2C23), 降馬橋 (2L31),
# 下田橋 (2L27), 留原 (2H12); la de 留原 trae ademas la lluvia de 五日市.
ESTACIONES = {"myoshoji": "222013", "kurome": "228005", "shimoda": "228001", "akigawa": "327003"}
TABLAS = {"data1m_suii": "1m", "data10m_suii": "10m", "data1h_suii": "1h",
          "data1m_uryo": "1m", "data10m_uryo": "10m", "data1h_uryo": "1h"}
VARIABLES = {"水位": "nivel_m", "10分間雨量": "lluvia_10min_mm", "1分間雨量": "lluvia_1min_mm",
             "1時間雨量": "lluvia_1h_mm","累計雨量": "lluvia_acumulada_mm", "時間最大雨量": "lluvia_max_hora_mm"}
PASO_CONSULTA_S = 300                  # la tabla de 1 min cubre 24 min: 5 min deja margen de sobra


def leer(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")


def texto(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def leer_estacion(codigo):
    """(hora de la pagina, [(hora_jst, paso, variable, valor)], ficha)."""
    html = leer(BASE.format(codigo))
    m = re.search(r"(\d{4})/(\d{2})/(\d{2}) (\d{2}):(\d{2}) 時点", html)
    ref = datetime(*map(int, m.groups()), tzinfo=JST)
    lecturas = []
    for m in re.finditer(r'<table class="time_table" id="(\w+)"[^>]*>(.*?)</table>', html, re.S):
        if m.group(1) not in TABLAS:
            continue
        filas = {}
        for fila in re.findall(r"<tr[^>]*>(.*?)</tr>", m.group(2), re.S):
            th = re.search(r"<th[^>]*>(.*?)</th>", fila, re.S)
            if th:
                filas[texto(th.group(1))] = [texto(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", fila, re.S)]
        horas = filas.pop("観測日時", [])
        for etiqueta, valores in filas.items():
            for hm, v in zip(horas, valores):
                hh, mm = map(int, hm.split(":"))
                t = ref.replace(hour=hh, minute=mm)
                if t > ref:                    # las tablas solo dan HH:MM: lo posterior es de ayer
                    t -= timedelta(days=1)
                lecturas.append((t.isoformat(timespec="minutes"), TABLAS[m.group(1)],
                                 VARIABLES.get(etiqueta, etiqueta), v))
    s = texto(re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S))
    ficha = {"pagina": BASE.format(codigo), "hora_pagina_jst": ref.isoformat(timespec="minutes"),
             "nivel_actual": re.findall(r"現在の水位\(m\) (\S+) A\.P\.\(m\) (\S+) 天端下り\(m\) (\S+)", s),
             "umbrales_nivel_ap_bajo_coronacion": re.findall(r"(氾濫発生水位|80%水位|50%水位) (\S+) (\S+) (\S+)", s),
             "notas": re.findall(r"※[^※]{0,120}?(?=情報提供について|※|$)", s)}
    m = re.search(r"観測所 (\S+) 河川名 (\S+) 時間単位", s)
    if m:
        ficha["estacion"], ficha["rio"] = m.groups()
    return ref, lecturas, ficha


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--camaras", nargs="+", default=list(ESTACIONES), choices=list(ESTACIONES))
    ap.add_argument("--minutos", type=float, default=1440.0)
    a = ap.parse_args()

    carpeta = os.path.join(AQUI, "grabaciones")
    os.makedirs(carpeta, exist_ok=True)
    arranque = datetime.now(JST)
    salidas = {}
    for cam in a.camaras:
        base = os.path.join(carpeta, f"{cam}_{arranque:%Y%m%d_%H%M}JST_nivel")
        f = open(base + ".csv", "w", newline="", encoding="utf-8")
        w = csv.writer(f)
        w.writerow(["hora_jst", "paso", "variable", "valor", "consultado_jst"])
        salidas[cam] = {"base": base, "f": f, "w": w, "vistas": set(), "filas": 0, "errores": 0}

    fin = time.time() + a.minutos * 60
    try:
        while True:
            ahora = datetime.now(JST).isoformat(timespec="seconds")
            for cam, o in salidas.items():
                try:
                    ref, lecturas, ficha = leer_estacion(ESTACIONES[cam])
                except Exception as e:
                    o["errores"] += 1
                    print(f"  {cam}: {e}", file=sys.stderr)
                    continue
                nuevas = 0
                for lec in sorted(lecturas):
                    if lec[:3] not in o["vistas"]:
                        o["vistas"].add(lec[:3])
                        o["w"].writerow(list(lec) + [ahora])
                        nuevas += 1
                o["f"].flush()
                o["filas"] += nuevas
                ficha.update({"camara": cam, "csv": os.path.basename(o["base"]) + ".csv",
                              "arranque_jst": arranque.isoformat(timespec="seconds"), "ultima_consulta_jst": ahora,
                              "filas": o["filas"], "errores": o["errores"]})
                with open(o["base"] + ".json", "w", encoding="utf-8") as fj:
                    json.dump(ficha, fj, indent=2, ensure_ascii=False)
                nivel = ficha["nivel_actual"][0][0] if ficha["nivel_actual"] else "?"
                print(f"  {ahora[11:19]} JST {cam}: nivel {nivel} m ({ref:%H:%M}), {nuevas} lecturas nuevas")
            if time.time() + PASO_CONSULTA_S > fin:
                break
            time.sleep(PASO_CONSULTA_S)
    except KeyboardInterrupt:
        print("cortado con Ctrl+C")
    finally:
        for o in salidas.values():
            o["f"].close()
    print("listo:", ", ".join(f"{os.path.basename(o['base'])}.csv ({o['filas']} filas)" for o in salidas.values()))


if __name__ == "__main__":
    main()
