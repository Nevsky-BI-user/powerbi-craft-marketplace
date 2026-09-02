#!/usr/bin/env python3
"""build_nav.py — put the chosen navigation on EVERY visible page of a PBIR (enhanced) report.

usage:
  python build_nav.py --report <X.Report> --config cfg.json [--variant V1] [--apply] [--out nav_coverage.md]

Config = the same JSON used by render_nav_previews.py (pages[{name,width,height,icon?}],
hero_page, palette, selected_style, icons, groups) plus optional:
  "variant": "V1"                       chosen variant (or --variant)
  "exclude_pages": ["Підказка"]         display names that get no menu item
  "icon_items": {"Огляд": "nav_home123.png"}   REGISTERED resource ItemName per page
                                        (register PNGs first → pbi-headers-icons-imagery §9)
  "geometry": {"1280x720": {"x":24,"y":8,"h":32,"item_w":140,"gap":8}}  per-canvas overrides

Emits, per visible page, one visualGroup "Navigation" + one actionButton per menu item
(V1 top bar, V2 left rail, V3 icon rail, V7 grouped bar) or one pageNavigator (V6).
V4 (hub) and V5 (hamburger overlay) are documented as manual builds and are not emitted.
Ids are deterministic (sha1 of variant+page+item) → re-runs overwrite in place (idempotent).
Default is a dry run; --apply writes files. stdlib only. Legacy report.json → exit 1.
"""
import argparse
import glob
import hashlib
import io
import json
import os
import subprocess
import sys

SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.10.0/schema.json"
HIDDEN_TYPES = {"Tooltip", "Drillthrough"}


def hid(*parts):
    return hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:20]


def lit(v):
    return {"expr": {"Literal": {"Value": v}}}


def color(hexv):
    return {"solid": {"color": lit(f"'{hexv}'")}}


def load(p):
    return json.load(io.open(p, encoding="utf-8"))


def dump(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


# ---------- report inventory ----------
def read_pages(report):
    pages_dir = os.path.join(report, "definition", "pages")
    if not os.path.isdir(pages_dir):
        sys.exit("Не PBIR enhanced (немає definition/pages) — Legacy report.json → powerbi-visuals")
    order = []
    pj = os.path.join(pages_dir, "pages.json")
    if os.path.exists(pj):
        order = load(pj).get("pageOrder") or []
    folders = [d for d in sorted(os.listdir(pages_dir)) if os.path.isdir(os.path.join(pages_dir, d))]
    ordered = [f for f in order if f in folders] + [f for f in folders if f not in order]
    pages = []
    for f in ordered:
        page = load(os.path.join(pages_dir, f, "page.json"))
        hidden = page.get("visibility") == "HiddenInViewMode" or page.get("type") in HIDDEN_TYPES \
            or (page.get("pageBinding") or {}).get("type") in HIDDEN_TYPES
        pages.append({"folder": f, "name": page.get("name", f), "displayName": page.get("displayName", f),
                      "width": page.get("width", 1280), "height": page.get("height", 720), "hidden": hidden})
    return pages


def existing_visuals(report, folder):
    out = []
    for vj in glob.glob(os.path.join(report, "definition", "pages", folder, "visuals", "*", "visual.json")):
        try:
            v = load(vj)
            out.append((v.get("name", os.path.basename(os.path.dirname(vj))), v.get("position") or {}, v.get("parentGroupName")))
        except Exception:  # noqa
            pass
    return out


# ---------- geometry ----------
def geometry(variant, w, h, n, overrides):
    g = dict(overrides.get(f"{int(w)}x{int(h)}") or {})
    if variant in ("V1", "V7"):
        gap = g.get("gap", 8)
        item_w = g.get("item_w") or min(200, max(96, (w - 48 - gap * (n - 1)) // max(n, 1)))
        return {"group": (g.get("x", 24), g.get("y", 8), item_w * n + gap * (n - 1), g.get("h", 32) + (28 if variant == "V7" else 0)),
                "item": (item_w, g.get("h", 32)), "gap": gap, "dir": "h"}
    if variant == "V2":
        return {"group": (0, 0, g.get("w", 240), h), "item": (g.get("item_w", 208), g.get("h", 32)),
                "gap": g.get("gap", 8), "dir": "v", "pad": (16, 24)}
    if variant == "V3":
        return {"group": (0, 0, g.get("w", 56), h), "item": (40, 40), "gap": 8, "dir": "v", "pad": (8, 16)}
    if variant == "V6":
        return {"group": (g.get("x", 24), g.get("y", 8), w - 48, g.get("h", 32))}
    return None


# ---------- emitters ----------
def button(name, label, target, x, y, w, h, pal, selected, icon_item, labeled, tab):
    text_entries = [{"properties": {"show": lit("true" if labeled else "false")}},
                    {"properties": {"text": lit(f"'{label}'"), "fontSize": lit("10D"),
                                    "fontColor": color(pal["inverse"] if selected else pal["text"]),
                                    "horizontalAlignment": lit("'center'")} | ({"bold": lit("true")} if selected else {}),
                     "selector": {"id": "default"}},
                    {"properties": {"fontColor": color(pal["inverse"] if selected else pal["text_hover"])},
                     "selector": {"id": "hover"}}]
    if icon_item and labeled:
        text_entries[1]["properties"]["leftMargin"] = lit("30L")
        text_entries[1]["properties"]["horizontalAlignment"] = lit("'left'")
    fill_entries = [{"properties": {"show": lit("true")}},
                    {"properties": {"fillColor": color(pal["selected"] if selected else pal["fill"]),
                                    "transparency": lit("0D" if selected else "100D")}, "selector": {"id": "default"}},
                    {"properties": {"fillColor": color(pal["selected"] if selected else pal["hover"]),
                                    "transparency": lit("0D")}, "selector": {"id": "hover"}}]
    objects = {"text": text_entries, "fill": fill_entries,
               "outline": [{"properties": {"show": lit("false")}}],
               "shape": [{"properties": {"roundEdge": lit("6L")}, "selector": {"id": "default"}}]}
    if icon_item:
        objects["icon"] = [{"properties": {"show": lit("true")}},
                           {"properties": {"shapeType": lit("'custom'"),
                                           "image": {"image": {"name": lit(f"'{icon_item}'"),
                                                               "url": {"expr": {"ResourcePackageItem": {"PackageName": "RegisteredResources", "PackageType": 1, "ItemName": icon_item}}},
                                                               "scaling": lit("'Normal'")}},
                                           "iconSize": lit("20D"), "placement": lit("'custom'"),
                                           "horizontalAlignment": lit("'center'" if not labeled else "'left'")},
                            "selector": {"id": "default"}}]
    return {"$schema": SCHEMA, "name": name,
            "position": {"x": x, "y": y, "z": 9000, "height": h, "width": w, "tabOrder": tab},
            "visual": {"visualType": "actionButton", "objects": objects,
                       "visualContainerObjects": {"visualLink": [{"properties": {
                           "show": lit("true"), "type": lit("'PageNavigation'"),
                           "navigationSection": lit(f"'{target}'")}}]},
                       "drillFilterOtherVisuals": True},
            "howCreated": "InsertVisualButton"}


def group_container(name, x, y, w, h, tab):
    return {"$schema": SCHEMA, "name": name,
            "position": {"x": x, "y": y, "z": 9000, "height": h, "width": w, "tabOrder": tab},
            "visualGroup": {"displayName": "Navigation", "groupMode": "ScaleMode"}}


def page_navigator(name, x, y, w, h, vertical):
    objects = {}
    if vertical:
        objects["layout"] = [{"properties": {"orientation": lit("1D")}}]
    return {"$schema": SCHEMA, "name": name,
            "position": {"x": x, "y": y, "z": 9000, "height": h, "width": w, "tabOrder": 100},
            "visual": {"visualType": "pageNavigator", "objects": objects, "drillFilterOtherVisuals": True},
            "howCreated": "InsertVisualButton"}


# ---------- main ----------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--report", required=True)
    ap.add_argument("--config", required=True)
    ap.add_argument("--variant")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--out", default="nav_coverage.md")
    a = ap.parse_args()

    cfg = load(a.config)
    variant = (a.variant or cfg.get("variant") or "").upper()
    if variant not in {"V1", "V2", "V3", "V4", "V5", "V6", "V7"}:
        sys.exit("Вкажи --variant V1..V7 (або 'variant' у конфігу)")
    if variant in ("V4", "V5"):
        print(f"{variant}: не генерується автоматично. V4 = хаб-сторінка з картками секцій + кнопка «home» на "
              f"кожній сторінці (pbi-buttons-actions); V5 = кнопка ☰ + overlay-група з букмарками "
              f"(pbi-filter-panel-bookmark pattern + powerbi-bookmarks). Побудуй за цими скілами.")
        return 0

    pal_in = cfg.get("palette") or {}
    pal = {"selected": pal_in.get("selected_fill") or pal_in.get("primary") or pal_in.get("accent") or "#063E61",
           "text": pal_in.get("text") or "#333333", "text_hover": pal_in.get("text_hover") or pal_in.get("text") or "#333333",
           "inverse": pal_in.get("text_inverse") or "#FFFFFF", "fill": pal_in.get("fill") or "#FFFFFF",
           "hover": pal_in.get("hover") or "#E6ECEF"}
    icons_mode = cfg.get("icons", "none")
    icon_items = cfg.get("icon_items") or {}
    if variant == "V3" and not icon_items:
        sys.exit("V3 (іконкова рейка) потребує 'icon_items' — зареєстровані PNG на кожну сторінку")
    labeled = icons_mode != "only" and variant != "V3"
    exclude = set(cfg.get("exclude_pages") or [])
    overrides = cfg.get("geometry") or {}

    pages = read_pages(a.report)
    by_disp = {p["displayName"]: p for p in pages}
    by_name = {p["name"]: p for p in pages}
    items, missing = [], []
    for cp in cfg.get("pages") or []:
        p = by_disp.get(cp["name"]) or by_name.get(cp["name"])
        if not p:
            missing.append(cp["name"]); continue
        if p["hidden"] or cp["name"] in exclude:
            continue
        items.append(p)
    if missing:
        sys.exit(f"Сторінки з конфігу відсутні у звіті: {missing}")
    if not items:
        sys.exit("Жодного пункту меню — усі сторінки приховані або виключені")
    targets = [p for p in pages if not p["hidden"]]
    groups = cfg.get("groups") if variant == "V7" else None

    plan, report_lines = [], []
    for page in targets:
        w, h = page["width"], page["height"]
        n = len(groups) if groups else len(items)
        geo = geometry(variant, w, h, n, overrides)
        gname = hid("nav", variant, page["name"], "group")
        vdir = os.path.join(a.report, "definition", "pages", page["folder"], "visuals")
        files = {}
        gx, gy, gw, gh = geo["group"]
        if variant == "V6":
            files[gname] = page_navigator(gname, gx, gy, gw, gh, vertical=False)
        else:
            files[gname] = group_container(gname, gx, gy, gw, gh, 100)
            iw, ih = geo["item"]
            gap = geo["gap"]
            px, py = geo.get("pad", (0, 0))
            row_items = items
            if groups:
                row_items = []
                for g in groups:
                    first = next((by_disp.get(nm) or by_name.get(nm) for nm in g["pages"] if (by_disp.get(nm) or by_name.get(nm))), None)
                    if first:
                        row_items.append({**first, "displayName": g["name"], "_group": g})
            for i, it in enumerate(row_items):
                x = px + (i * (iw + gap) if geo["dir"] == "h" else 0)
                y = py + (i * (ih + gap) if geo["dir"] == "v" else 0)
                bname = hid("nav", variant, page["name"], it["name"])
                selected = it["name"] == page["name"] or (groups and page["displayName"] in it.get("_group", {}).get("pages", []))
                files[bname] = {**button(bname, it["displayName"], it["name"], x, y, iw, ih, pal, bool(selected),
                                         icon_items.get(it["displayName"]) if icons_mode != "none" else None,
                                         labeled, 110 + i * 10), "parentGroupName": gname}
            if groups:  # second row: pages of the current page's group
                cur = next((g for g in groups if page["displayName"] in g["pages"]), None)
                if cur:
                    subs = [by_disp.get(nm) or by_name.get(nm) for nm in cur["pages"]]
                    subs = [s for s in subs if s and not s["hidden"]]
                    sw = min(160, max(80, (gw - gap * (len(subs) - 1)) // max(len(subs), 1)))
                    for j, s in enumerate(subs):
                        sname = hid("nav", variant, page["name"], "sub", s["name"])
                        files[sname] = {**button(sname, s["displayName"], s["name"], j * (sw + gap), ih + 8, sw, 28, pal,
                                                 s["name"] == page["name"], None, True, 300 + j * 10), "parentGroupName": gname}
        # overlap check against visuals we did not generate
        ours = set(files)
        overlaps = []
        for name, pos, _parent in existing_visuals(a.report, page["folder"]):
            if name in ours or not pos:
                continue
            ox, oy, ow, oh = pos.get("x", 0), pos.get("y", 0), pos.get("width", 0), pos.get("height", 0)
            if ox < gx + gw and ox + ow > gx and oy < gy + gh and oy + oh > gy:
                overlaps.append(name)
        selected_names = [f["name"] for f in files.values() if f.get("visual", {}).get("visualType") == "actionButton"
                          and f["visual"]["objects"]["fill"][1]["properties"]["fillColor"]["solid"]["color"]["expr"]["Literal"]["Value"] == f"'{pal['selected']}'"]
        plan.append((page, vdir, files))
        report_lines.append(f"| {page['displayName']} | {int(w)}×{int(h)} | {len(files)} | {len(selected_names)} | {', '.join(overlaps) or '—'} |")

    # write
    written = 0
    if a.apply:
        for page, vdir, files in plan:
            for name, obj in files.items():
                dump(os.path.join(vdir, name, "visual.json"), obj); written += 1

    hidden = [p["displayName"] for p in pages if p["hidden"]]
    md = [f"# Навігація {variant} — покриття", "",
          f"Звіт: `{os.path.basename(a.report)}` · пунктів меню: {len(items)} · видимих сторінок: {len(targets)} · "
          f"прихованих (без меню): {len(hidden)} · режим: {'ЗАПИСАНО' if a.apply else 'dry-run'}", "",
          "| Сторінка | Канвас | Файлів | Selected | Перекриття з наявними візуалами |", "|---|---|---|---|---|", *report_lines, ""]
    if hidden:
        md.append(f"Приховані сторінки без меню: {', '.join(hidden)}")
    not_in_menu = [p["displayName"] for p in targets if p not in items]
    if not_in_menu:
        md.append(f"⚠ Видимі сторінки, яких немає в меню: {', '.join(not_in_menu)}")
    if a.apply:
        hook = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "hooks", "check_report.py")
        bad = 0
        if os.path.exists(hook):
            for page, vdir, files in plan:
                for name in files:
                    r = subprocess.run([sys.executable, hook, os.path.join(vdir, name, "visual.json")], capture_output=True, text=True)
                    if r.returncode != 0:
                        bad += 1; md.append(f"- hook: {name}: {r.stderr.strip()[:200]}")
        md.append(f"\nЗаписано файлів: {written}; хук check_report.py: {'усі чисті' if bad == 0 else f'{bad} з помилками'}")
    text = "\n".join(md) + "\n"
    io.open(a.out, "w", encoding="utf-8", newline="\n").write(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
