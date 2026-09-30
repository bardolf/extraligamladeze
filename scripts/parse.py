"""Z raw/ vytáhne soupisky a výsledky po šachovnicích do data/rosters.json a data/boards.json."""
import glob
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
DATA = ROOT / "data"


def txt(x):
    return html.unescape(re.sub("<[^>]+>", "", x)).strip()


def num(x):
    x = txt(x)
    return int(x) if x.isdigit() else None


def parse_rosters():
    out = []
    for f in sorted(glob.glob(str(RAW / "sou_*.html"))):
        y = int(pathlib.Path(f).stem.split("_")[1])
        s = open(f, encoding="utf-8").read()
        for tb in re.findall(r"<table>(.*?)</table>", s, re.S):
            cap = re.search(r'<caption.*?<a href="[^"]*/(\d+)/">\s*(.*?)\s*</a>', tb, re.S)
            if not cap:
                continue
            for tr in re.findall(r"<tr>(.*?)</tr>", tb, re.S):
                tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
                m = re.search(r"hrac/(\d+)/", tr)
                if not m or len(tds) < 5:
                    continue
                out.append(dict(
                    season=y, team=html.unescape(cap.group(2).strip()), tid=cap.group(1),
                    board=re.sub(r"\D", "", tds[0]), pid=int(m.group(1)), name=txt(tds[1]),
                    typ=txt(tds[2]), nelo=num(tds[3]), felo=num(tds[4]),
                ))
    return out


def parse_boards():
    out = []
    for f in sorted(glob.glob(str(RAW / "sach_*.html"))):
        _, y, k = pathlib.Path(f).stem.split("_")
        s = open(f, encoding="utf-8").read()
        for tb in re.findall(r"<table>(.*?)</table>", s, re.S):
            teams = re.findall(r'druzstvo/\d+/(\d+)/">\s*(.*?)\s*</a>', tb, re.S)
            body = re.search(r"<tbody>(.*?)</tbody>", tb, re.S)
            if len(teams) < 2 or not body:
                continue
            for bi, tr in enumerate(re.findall(r"<tr>(.*?)</tr>", body.group(1), re.S), 1):
                tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
                if len(tds) < 7:
                    continue
                # levý hráč: jméno, elo, výsledek; pravý hráč zrcadlově
                for side, (ni, ei, ri) in enumerate([(0, 1, 2), (6, 5, 4)]):
                    m = re.search(r"hrac/(\d+)/", tds[ni])
                    out.append(dict(
                        season=int(y), round=int(k), board=bi, team=txt(teams[side][1]),
                        tid=teams[side][0], pid=int(m.group(1)) if m else None,
                        name=txt(tds[ni]), elo=num(tds[ei]), res=txt(tds[ri]),
                    ))
    return out


def main():
    DATA.mkdir(exist_ok=True)
    rosters, boards = parse_rosters(), parse_boards()
    json.dump(rosters, open(DATA / "rosters.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump(boards, open(DATA / "boards.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(len(rosters), "řádků soupisek,", len(boards), "partií (po hráčích)")


if __name__ == "__main__":
    main()
