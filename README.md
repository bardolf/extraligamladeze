# Síla Extraligy mládeže

Jak se vyvíjela síla MČR družstev mládeže (finále A, dříve Extraliga dorostu) v ročnících
2004/05 – 2025/26, měřeno průměrným Elo 5, 10 a 15 nejsilnějších hráčů ročníku.

- `sila-extraligy-mladeze.html` – interaktivní přehled (graf, rozdíl FIDE − ČR, tabulka s top 15 hráči)
- `sila-extraligy-mladeze.csv` – průměry top 1/5/10/15 pro ELO ČR a FIDE, zvlášť pro hráče,
  kteří nastoupili, a pro celé soupisky
- `docs/` – stejný přehled jako samostatná stránka pro GitHub Pages (`index.html` + `style.css`),
  https://bardolf.github.io/extraligamladeze/
- `data/` – vyparsované soupisky (`rosters.json`), výsledky po šachovnicích (`boards.json`)
  a spočítané ročníky (`seasons.json`)

## Metodika

- Elo je převzaté ze soupisky daného ročníku, tj. hodnota z doby soutěže.
- ELO ČR je k dispozici pro všechny ročníky, FIDE Elo až od 2011/12.
- Standardně se počítají jen hráči s aspoň jednou odehranou partií (bez kontumací).
- U ročníku 2005/06 chybí na chess.cz výsledky 1.–3. kola.

## Přegenerování

```sh
python3 scripts/download.py   # stáhne stránky z chess.cz do raw/ (není v gitu)
python3 scripts/parse.py      # raw/ -> data/rosters.json, data/boards.json
python3 scripts/build.py      # data/ -> data/seasons.json, CSV, HTML a docs/ (z report/template.html)
```

Zdroj: https://www.chess.cz/soutez/11/
