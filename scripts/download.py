"""Stáhne soupisky, tabulky a výsledky po šachovnicích všech ročníků z chess.cz do raw/."""
import pathlib
import time
import urllib.request

# rok začátku ročníku -> id soutěže na chess.cz (2003/04 a 2026/27 nemají soupisky)
SEASONS = {
    2004: 179, 2005: 246, 2006: 407, 2007: 460, 2008: 557, 2009: 737, 2010: 808,
    2011: 937, 2012: 1073, 2013: 1211, 2014: 1361, 2015: 1511, 2016: 2134,
    2017: 2277, 2018: 2292, 2019: 2441, 2020: 2564, 2021: 2691, 2022: 2832,
    2023: 2985, 2024: 3120, 2025: 3253,
}
ROUNDS = range(1, 8)
BASE = "https://www.chess.cz/soutez"
RAW = pathlib.Path(__file__).resolve().parent.parent / "raw"


def fetch(url, path):
    if path.exists() and path.stat().st_size > 0:
        return
    with urllib.request.urlopen(url, timeout=60) as r:
        path.write_bytes(r.read())
    time.sleep(0.3)


def main():
    RAW.mkdir(exist_ok=True)
    for y, sid in SEASONS.items():
        fetch(f"{BASE}/druzstvo/{sid}/", RAW / f"sou_{y}.html")
        fetch(f"{BASE}/{sid}/", RAW / f"s_{y}.html")
        for k in ROUNDS:
            fetch(f"{BASE}/sachovnice/{sid}/kolo-{k}/", RAW / f"sach_{y}_{k}.html")
        print(y, "ok")


if __name__ == "__main__":
    main()
