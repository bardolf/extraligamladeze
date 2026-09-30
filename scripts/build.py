"""Spočítá průměry top 5/10/15 a vyrobí data/seasons.json, CSV a HTML přehled."""
import collections
import csv
import html
import json
import pathlib
import re
import statistics as st

from download import SEASONS as SEASON_IDS

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
DATA = ROOT / "data"
TOPS = (1, 5, 10, 15)
SCORE = {"1": 1, "0": 0, "½": 0.5}
WINNER_FIX = {
    'BŠŠ FRÝDEK-MÍSTEK "A"': "BŠŠ Frýdek-Místek A",
    "Frýdek-Místek": "BŠŠ Frýdek-Místek",
    "Beskydská šachová škola Frýdek-Místek": "BŠŠ Frýdek-Místek",
}


def winner(y):
    s = open(RAW / f"s_{y}.html", encoding="utf-8").read()
    m = re.search(r"<tbody>\s*<tr><td>1</td><td><a[^>]*>(.*?)</a>", s, re.S)
    w = html.unescape(m.group(1).strip()) if m else None
    return WINNER_FIX.get(w, w)


def main():
    rosters = json.load(open(DATA / "rosters.json", encoding="utf-8"))
    boards = json.load(open(DATA / "boards.json", encoding="utf-8"))

    # počet partií a body každého hráče v ročníku, bez kontumací (1K/0K)
    games = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0.0]))
    for b in boards:
        if b["pid"] and b["res"] in SCORE:
            g = games[b["season"]][b["pid"]]
            g[0] += 1
            g[1] += SCORE[b["res"]]

    seasons = []
    for y, sid in SEASON_IDS.items():
        ros = [r for r in rosters if r["season"] == y]
        gm = games[y]
        bases = {"played": [r for r in ros if r["pid"] in gm], "roster": ros}

        def tops(rows, key):
            v = sorted([r[key] for r in rows if r[key]], reverse=True)
            return {str(n): (round(st.mean(v[:n])) if len(v) >= n else None) for n in TOPS}

        def top15(rows, key):
            rows = sorted([r for r in rows if r[key]], key=lambda r: -r[key])[:15]
            return [[r["name"], r["team"], r["nelo"], r["felo"], *gm.get(r["pid"], [0, 0])] for r in rows]

        seasons.append(dict(
            y=y, label=f"{y}/{str(y + 1)[2:]}", winner=winner(y), nPlayed=len(gm), nRoster=len(ros),
            m={b: {"N": tops(rows, "nelo"), "F": tops(rows, "felo")} for b, rows in bases.items()},
            top={b: {"N": top15(rows, "nelo"), "F": top15(rows, "felo")} for b, rows in bases.items()},
            id=sid,
        ))

    json.dump(seasons, open(DATA / "seasons.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    with open(ROOT / "sila-extraligy-mladeze.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rocnik", "vitez", "nastoupilo", "na_soupisce"] + [
            f"{b}_{s}_top{n}" for b in ("nastoupili", "soupiska") for s in ("CR", "FIDE") for n in TOPS])
        for s in seasons:
            row = [s["label"], s["winner"], s["nPlayed"], s["nRoster"]]
            for b in ("played", "roster"):
                for sy in ("N", "F"):
                    row += ["" if s["m"][b][sy][str(n)] is None else s["m"][b][sy][str(n)] for n in TOPS]
            w.writerow(row)

    tpl = open(ROOT / "report" / "template.html", encoding="utf-8").read()
    data = "const SEASONS=" + json.dumps(seasons, ensure_ascii=False, separators=(",", ":")) + ";"
    page = tpl.replace("/*__DATA__*/", data)
    open(ROOT / "sila-extraligy-mladeze.html", "w", encoding="utf-8").write(page)
    write_docs(page)
    print(len(seasons), "ročníků ->", "sila-extraligy-mladeze.html, sila-extraligy-mladeze.csv, docs/")


# Základ, který na claude.ai doplňuje obal artefaktu; na GitHub Pages ho musí dodat stránka sama.
RESET_CSS = """:root { color-scheme: light; }
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; }
img { max-width: 100%; }
[hidden] { display: none !important; }

"""


def write_docs(page):
    """Z fragmentu pro artefakt udělá samostatnou stránku pro GitHub Pages: docs/index.html + docs/style.css."""
    m = re.search(r"<style>\n(.*?)</style>\n", page, re.S)
    head, css, body = page[:m.start()], m.group(1), page[m.end():]
    desc = ("Vývoj síly MČR družstev mládeže (finále A) 2004/05–2025/26 podle průměrného Elo "
            "top 5, 10 a 15 hráčů, v ELO ČR i FIDE.")
    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)
    (docs / "style.css").write_text(RESET_CSS + css, encoding="utf-8")
    (docs / ".nojekyll").write_text("", encoding="utf-8")
    (docs / "index.html").write_text(
        '<!doctype html>\n<html lang="cs">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<meta name="description" content="{desc}">\n'
        + head.strip() + '\n<link rel="stylesheet" href="style.css">\n</head>\n<body>\n'
        + body.strip() + "\n</body>\n</html>\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
