#!/usr/bin/env python3
"""Перевірка битих посилань у DAX-виразах семантичної моделі (TMDL).

Ловить клас дефектів, який пропускають і BPA, і валідність JSON: міра або
колонка посилається на таблицю, якої в моделі немає ('Автотести витрати',
'AccessControl' — реальні продакшн-прецеденти). TOM такі вирази терпить,
візуал падає лише в рантаймі.

Використання:
    python check-model-refs.py <тека *.SemanticModel\\definition>

Вихід: 0 — чисто; 1 — є посилання на неіснуючі таблиці; 2 — помилка запуску.
Друкує по рядку на знахідку: <файл>:<рядок>  '<таблиця>'  (<контекст-об'єкт>)

Обмеження (свідомі, проти хибних спрацювань):
- Перевіряються лише КВОТОВАНІ посилання 'Table Name' — неквотовані імена без
  пробілів/кирилиці граматично невідрізнимі від функцій і змінних.
- Рядкові літерали "..." вирізаються до пошуку — 'X' усередині тексту
  повідомлення не вважається посиланням.
- Посилання на колонки за іменем не звіряються (це рівень dax-regression-tests
  live-тіру) — лише існування таблиці.
"""
import re
import sys
from pathlib import Path

QUOTED_TABLE = re.compile(r"'([^']+)'")
STRING_LIT = re.compile(r'"(?:[^"]|"")*"')


def collect_tables(def_dir: Path) -> set:
    tables = set()
    tables_dir = def_dir / "tables"
    if tables_dir.is_dir():
        for f in tables_dir.glob("*.tmdl"):
            text = f.read_text(encoding="utf-8-sig", errors="replace")
            m = re.search(r"^table\s+(?:'([^']+)'|(\S+))", text, re.M)
            if m:
                tables.add((m.group(1) or m.group(2)).strip())
    model = def_dir / "model.tmdl"
    if model.is_file():
        for m in re.finditer(r"^\s*ref table\s+(?:'([^']+)'|(\S+))",
                             model.read_text(encoding="utf-8-sig", errors="replace"), re.M):
            tables.add((m.group(1) or m.group(2)).strip())
    return tables


def iter_dax_expressions(text: str):
    """Пари (номер_рядка, ім'я_об'єкта, DAX-текст) для measure/column-виразів.

    TMDL: однорядковий вираз після '=', багаторядковий — у ``` ``` або з
    відступом наступних рядків. Партиції (M-код) пропускаються.
    """
    lines = text.split("\n")
    i = 0
    in_partition = False
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if re.match(r"^\t*partition\s", line):
            in_partition = True
        elif re.match(r"^\t*(measure|column|table|annotation|hierarchy)\b", line):
            in_partition = False
        m = re.match(r"^\t*measure\s+(?:'([^']+)'|([^\s=]+))\s*=(.*)$", line)
        if m and not in_partition:
            name = (m.group(1) or m.group(2)).strip()
            body = [m.group(3)]
            start = i + 1
            base_indent = len(line) - len(line.lstrip("\t"))
            j = start
            while j < len(lines):
                nxt = lines[j]
                if nxt.strip() == "":
                    body.append("")
                    j += 1
                    continue
                indent = len(nxt) - len(nxt.lstrip("\t"))
                if indent > base_indent:
                    body.append(nxt)
                    j += 1
                else:
                    break
            yield (i + 1, name, "\n".join(body))
            i = j
            continue
        i += 1


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    def_dir = Path(sys.argv[1])
    if not (def_dir / "tables").is_dir() and not (def_dir / "model.tmdl").is_file():
        print(f"check-model-refs: '{def_dir}' не схожа на теку definition "
              f"(немає tables/ і model.tmdl)", file=sys.stderr)
        return 2

    tables = collect_tables(def_dir)
    if not tables:
        print("check-model-refs: у моделі не знайдено жодної таблиці — "
              "нема з чим звіряти", file=sys.stderr)
        return 2

    broken = []
    for f in sorted((def_dir / "tables").glob("*.tmdl")):
        text = f.read_text(encoding="utf-8-sig", errors="replace")
        for line_no, obj_name, dax in iter_dax_expressions(text):
            # Порядок зачистки: рядкові літерали, потім коментарі — апостроф
            # у коментарі (//'c' = 'count') не є посиланням на таблицю.
            cleaned = STRING_LIT.sub('""', dax)
            cleaned = re.sub(r"/\*.*?\*/", " ", cleaned, flags=re.S)
            cleaned = re.sub(r"(?m)(//|--).*$", " ", cleaned)
            for ref in QUOTED_TABLE.finditer(cleaned):
                t = ref.group(1).strip()
                if t and t not in tables:
                    broken.append((f.name, line_no, t, obj_name))

    if broken:
        seen = set()
        for fname, line_no, t, obj in broken:
            key = (fname, t, obj)
            if key in seen:
                continue
            seen.add(key)
            print(f"{fname}:{line_no}  '{t}'  (measure '{obj}')")
        print(f"\ncheck-model-refs: {len(seen)} посилань на неіснуючі таблиці "
              f"(таблиць у моделі: {len(tables)})")
        return 1

    print(f"check-model-refs: OK — квотовані посилання на таблиці валідні "
          f"(таблиць: {len(tables)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
