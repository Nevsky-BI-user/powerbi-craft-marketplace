# -*- coding: utf-8 -*-
"""Застосовує тему Нафтогаз до PBIP-звіту (PBIR enhanced).

Копіює тему й логотипи в RegisteredResources, оновлює themeCollection
та resourcePackages у definition/report.json. Старі теми не видаляє —
лише перемикає посилання customTheme.

Запуск:
  python apply_naftogaz_theme.py "<шлях до X.Report|X.pbip|папки>" --palette classic
  python apply_naftogaz_theme.py "<шлях>" --palette dark --no-logos
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
PALETTES = ("classic", "energy", "flame", "dark")
LOGOS = ("naftogaz_logo_full_light.png", "naftogaz_logo_full_dark.png",
         "naftogaz_logo_icon_light.png", "naftogaz_logo_icon_dark.png")


def find_report_dir(p: Path) -> Path:
    if p.suffix == ".pbip":
        p = p.parent
    if p.name.endswith(".Report"):
        rep = p
    else:
        found = sorted(p.glob("*.Report"))
        if len(found) != 1:
            sys.exit(f"ПОМИЛКА: у {p} знайдено {len(found)} папок *.Report — "
                     "вкажіть шлях точніше")
        rep = found[0]
    if not (rep / "definition" / "report.json").exists():
        sys.exit("ПОМИЛКА: немає definition/report.json — звіт не у форматі "
                 "PBIR enhanced. Для PBIR-Legacy див. pbi-theme-json/"
                 "reference.md §4 (рецепт wiring через config-рядок).")
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report", help="шлях до X.Report / X.pbip / папки проєкту")
    ap.add_argument("--palette", choices=PALETTES, default="classic")
    ap.add_argument("--no-logos", action="store_true",
                    help="не реєструвати PNG-логотипи")
    args = ap.parse_args()

    rep = find_report_dir(Path(args.report))
    theme_src = SKILL / "assets" / "themes" / f"naftogaz-{args.palette}.json"
    theme_name = theme_src.name
    rr = rep / "StaticResources" / "RegisteredResources"
    rr.mkdir(parents=True, exist_ok=True)

    report_json = rep / "definition" / "report.json"
    cfg = json.loads(report_json.read_text(encoding="utf-8-sig"))

    # 1. Файли: тема + логотипи
    shutil.copy2(theme_src, rr / theme_name)
    copied = [theme_name]
    if not args.no_logos:
        for logo in LOGOS:
            shutil.copy2(SKILL / "assets" / "logos" / logo, rr / logo)
            copied.append(logo)

    # 2. themeCollection: зберегти reportVersionAtImport від попередньої теми
    tc = cfg.setdefault("themeCollection", {})
    prev = tc.get("customTheme") or tc.get("baseTheme") or {}
    custom = {"name": theme_name, "type": "RegisteredResources"}
    if "reportVersionAtImport" in prev:
        custom["reportVersionAtImport"] = prev["reportVersionAtImport"]
    tc["customTheme"] = custom

    # 3. resourcePackages: дореєструвати тему та логотипи (без дублів)
    packages = cfg.setdefault("resourcePackages", [])
    rr_pkg = next((p for p in packages if p.get("type") == "RegisteredResources"),
                  None)
    if rr_pkg is None:
        rr_pkg = {"name": "RegisteredResources", "type": "RegisteredResources",
                  "items": []}
        packages.append(rr_pkg)
    items = rr_pkg.setdefault("items", [])
    have = {it["name"] for it in items}
    if theme_name not in have:
        items.append({"name": theme_name, "path": theme_name,
                      "type": "CustomTheme"})
    if not args.no_logos:
        for logo in LOGOS:
            if logo not in have:
                items.append({"name": logo, "path": logo, "type": "Image"})

    report_json.write_text(json.dumps(cfg, ensure_ascii=False, indent=2),
                           encoding="utf-8")

    print(f"Тема: {theme_name} -> customTheme ({rep.name})")
    print(f"Файли в RegisteredResources: {', '.join(copied)}")
    print("Далі: pbir_schema_validate.py, потім жива перевірка в Desktop.")


if __name__ == "__main__":
    main()
