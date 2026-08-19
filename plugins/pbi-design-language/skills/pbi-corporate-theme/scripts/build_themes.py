# -*- coding: utf-8 -*-
"""Генерує 4 корпоративні теми з master-theme.json (pbi-theme-json).

Світлі палітри: заміна бренд-хексів + явне встановлення dataColors/semantic.
Темна: контекстний обхід — fontColor-властивості лишаються світлими,
back/fill-властивості темніють (pbi-theme-json/reference.md §7).

Запуск:  python build_themes.py            # пише assets/themes/*.json
"""
import json
import re
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
MASTER = SKILL.parent / "pbi-theme-json" / "assets" / "master-theme.json"
OUT = SKILL / "assets" / "themes"

NAVY = "#0C375E"       # основний бренд-колір (навій)
AZURE = "#00A1DF"      # акцентний блакитний

# --- світлі палітри: явні слоти + структурна заміна навію -------------------
LIGHT_PALETTES = {
    "classic": dict(
        name="Corporate Classic",
        dataColors=[NAVY, AZURE, "#F2A900", "#2B9348", "#D64550",
                    "#41648C", "#7FC5EA", "#8F6A00"],
        accent=AZURE, hyperlink=AZURE, visitedHyperlink="#41648C",
        neutral="#F2A900",
    ),
    "energy": dict(
        name="Corporate Energy",
        dataColors=[NAVY, "#FFD500", "#0057B7", AZURE, "#2B9348",
                    "#D64550", "#41648C", "#B08900"],
        accent="#0057B7", hyperlink="#0057B7", visitedHyperlink="#41648C",
        neutral="#FFD500",
    ),
    "flame": dict(
        name="Corporate Flame",
        dataColors=[NAVY, AZURE, "#0E7490", "#38BDF8", "#155E75",
                    "#5B7C99", "#7DD3FC", "#0369A1"],
        accent=AZURE, hyperlink=AZURE, visitedHyperlink="#5B7C99",
        neutral="#F2A900",
    ),
}

# --- темна палітра ----------------------------------------------------------
DARK = dict(
    name="Corporate Dark",
    canvas="#0E1F33",      # полотно сторінки
    outspace="#0A1826",    # поза полотном
    surface="#14293F",     # фон візуалів
    surfaceAlt="#182F48",  # смуги/другорядний фон
    surfaceAlt2="#122841",
    line="#2C425C",        # межі, сітка
    textPrimary="#E9F0F6",
    textSecondary="#A7B9CB",
    textTitle="#7FC5EA",   # заголовки замість навію
    disabled="#6A7F93",
    center="#1B3350",
    dataColors=[AZURE, "#4FC3F7", "#FFD166", "#57C785", "#FF7A7A",
                "#8FA8C8", "#9BDBFF", "#C9A227"],
    good="#57C785", bad="#FF7A7A", neutral="#FFD166",
    maximum="#66BB6A", minimum="#EF5350",
    accent="#4FC3F7", hyperlink="#4FC3F7", visitedHyperlink="#8FA8C8",
    tableAccent=AZURE,
)

# властивості-шрифти: значення лишаються світлими у темній темі
FONT_PROPS = re.compile(r"fontColor|labelColor|titleColor", re.I)


def load_master():
    return json.loads(MASTER.read_text(encoding="utf-8-sig"))


def set_semantics(t, p):
    t["name"] = p["name"]
    t["dataColors"] = p["dataColors"]
    for k in ("accent", "hyperlink", "visitedHyperlink"):
        t[k] = p[k]
    t["neutral"] = p["neutral"]
    t["tableAccent"] = p.get("tableAccent", p["dataColors"][0])


def build_light(key, p):
    raw = MASTER.read_text(encoding="utf-8-sig")
    # структурна заміна бренду (заголовки, хедери таблиць, fill кнопок)
    raw = raw.replace("#063E61", NAVY)
    t = json.loads(raw)
    set_semantics(t, p)
    return t


def dark_map(hexval, prop_names):
    """Контекстна мапа світлий→темний. prop_names — імена ключів шляху."""
    is_font = any(FONT_PROPS.search(n) for n in prop_names) or \
        "textClasses" in prop_names
    h = hexval.upper()
    if h == "#FFFFFF":
        return "#FFFFFF" if is_font else DARK["surface"]
    if h == "#063E61":
        return DARK["textTitle"] if is_font else NAVY
    table = {
        "#333333": DARK["textPrimary"], "#605E5C": DARK["textSecondary"],
        "#E6E6E6": DARK["line"], "#9E9F9F": DARK["disabled"],
        "#F5F4F2": DARK["surfaceAlt"], "#FAFAFA": DARK["surfaceAlt2"],
        "#E6ECEF": DARK["canvas"], "#F3F2F1": DARK["center"],
    }
    return table.get(h, hexval)


def build_dark():
    t = load_master()

    def walk(node, names):
        if isinstance(node, dict):
            return {k: walk(v, names + [k]) for k, v in node.items()}
        if isinstance(node, list):
            return [walk(v, names) for v in node]
        if isinstance(node, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", node):
            return dark_map(node, names)
        return node

    t = walk(t, [])
    set_semantics(t, DARK)
    for k, v in (("good", "good"), ("bad", "bad"), ("neutral", "neutral"),
                 ("maximum", "maximum"), ("minimum", "minimum"),
                 ("center", "center"), ("null", "disabled")):
        t[k] = DARK[v]
    # структурні класи
    t["firstLevelElements"] = DARK["textPrimary"]
    t["secondLevelElements"] = DARK["textSecondary"]
    t["thirdLevelElements"] = DARK["line"]
    t["fourthLevelElements"] = DARK["disabled"]
    t["background"] = DARK["surface"]
    t["secondaryBackground"] = DARK["surfaceAlt"]
    t["shapeStroke"] = DARK["line"]
    t["disabledText"] = DARK["disabled"]
    # сторінка: полотно темніше за візуали, outspace ще темніший, transparency 0
    page = t["visualStyles"]["page"]["*"]
    for entry in page.get("background", []):
        entry["color"] = {"solid": {"color": DARK["canvas"]}}
        entry["transparency"] = 0
    for entry in page.get("outspace", []):
        entry["color"] = {"solid": {"color": DARK["outspace"]}}
        entry["transparency"] = 0
    return t


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    themes = {k: build_light(k, p) for k, p in LIGHT_PALETTES.items()}
    themes["dark"] = build_dark()
    for key, theme in themes.items():
        path = OUT / f"corporate-{key}.json"
        path.write_text(json.dumps(theme, ensure_ascii=False, indent=2),
                        encoding="utf-8")
        print(f"{path.name}: dataColors={theme['dataColors'][:3]}...")


if __name__ == "__main__":
    main()
