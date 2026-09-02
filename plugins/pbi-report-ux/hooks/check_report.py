"""Перевірка файлів Power BI звіту після редагування — обидва формати.

PBIR-Legacy (report.json з sections[]):
  1. Зовнішній JSON парситься; кожен вкладений config-рядок парситься.
  2. Симетрія братніх букмарок у групах (targetVisualNames, suppressData).

PBIR enhanced (definition/…):
  3. *.bookmark.json — $schema є; з applyOnlyToTargetVisuals кожен id зі
     explorationState є в targetVisualNames; display.mode у enum;
     suppressData+suppressDisplay разом — попередження.
  4. bookmarks.json — кожен item це leaf {name} або group
     {name, displayName, children}; кожне імʼя має файл.
  5. visual.json — visualLink.type відомий; navigationSection /
     drillthroughSection резолвиться в сторінку, bookmark — у файл букмарки;
     закон серіалізації (show без селектора, значення з селектором);
     навігатори: selector id лише default/hover/selected/disabled.
  6. page.json / pages.json / definition/report.json — парсяться.

Мовчить, коли все чисто. exit 2 + повідомлення в stderr — Claude отримує
фідбек і лагодить одразу. Попередження друкуються, але не блокують.
"""
import glob
import io
import json
import os
import sys

try:
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:  # noqa
    pass

MODE_ENUM = {"maximize", "spotlight", "elevation", "hidden"}
LINK_TYPES = {"PageNavigation", "Bookmark", "Drillthrough", "Back", "ClearAllSlicers",
              "ApplyAllSlicers", "WebUrl", "QnA"}
NAV_SELECTORS = {"default", "hover", "selected", "disabled"}

path = sys.argv[1]
problems, warns = [], []


def load(p):
    return json.load(io.open(p, encoding="utf-8"))


def literal(node):
    try:
        v = node["expr"]["Literal"]["Value"]
        return v.strip("'") if isinstance(v, str) else v
    except Exception:  # noqa
        return None


def report_root(p):
    """…/X.Report/definition/… → X.Report"""
    cur = os.path.abspath(p)
    while cur and cur != os.path.dirname(cur):
        if cur.lower().endswith(".report") and os.path.isdir(cur):
            return cur
        cur = os.path.dirname(cur)
    return None


def page_names(root):
    names = set()
    for pdir in glob.glob(os.path.join(root, "definition", "pages", "*")):
        if os.path.isdir(pdir):
            names.add(os.path.basename(pdir))
            try:
                names.add(load(os.path.join(pdir, "page.json")).get("name"))
            except Exception:  # noqa
                pass
    return names


def bookmark_names(root):
    return {os.path.basename(p)[:-len(".bookmark.json")]
            for p in glob.glob(os.path.join(root, "definition", "bookmarks", "*.bookmark.json"))}


def walk_groups(node, out):
    for gid, g in (node or {}).items():
        out.add(gid)
        if isinstance(g, dict) and "children" in g:
            walk_groups(g["children"], out)


# ---------- Legacy report.json ----------
def check_legacy(doc):
    def parse_config(holder, where):
        cfg = holder.get("config")
        if not isinstance(cfg, str):
            return cfg if isinstance(cfg, dict) else None
        try:
            return json.loads(cfg)
        except Exception as e:  # noqa
            problems.append(f"вкладений config не парситься ({where}): {e}")
            return None

    report_cfg = parse_config(doc, "звіт")
    for si, sec in enumerate(doc.get("sections") or []):
        parse_config(sec, f"сторінка #{si} {sec.get('displayName', '')}")
        for vi, vc in enumerate(sec.get("visualContainers") or []):
            parse_config(vc, f"сторінка #{si} візуал #{vi}")
    if isinstance(report_cfg, dict):
        for grp in report_cfg.get("bookmarks") or []:
            children = grp.get("children")
            if not children or len(children) < 2:
                continue
            gname = grp.get("displayName", grp.get("name", "?"))
            sigs = []
            for ch in children:
                opts = ch.get("options") or {}
                tvn = opts.get("targetVisualNames")
                sigs.append((ch.get("displayName", ch.get("name", "?")),
                             len(tvn) if isinstance(tvn, list) else None,
                             opts.get("suppressData")))
            if len({s[1] for s in sigs}) > 1:
                det = ", ".join(f"{n}={c}" for n, c, _ in sigs)
                problems.append(f"група букмарок «{gname}»: різна кількість targetVisualNames ({det}) — "
                                f"сусідня вкладка програватиме чужий стан")
            if len({s[2] for s in sigs}) > 1:
                det = ", ".join(f"{n}={s}" for n, _, s in sigs)
                problems.append(f"група букмарок «{gname}»: suppressData не однаковий ({det}) — "
                                f"клік по вкладці скидатиме фільтри читача")


# ---------- PBIR enhanced ----------
def check_bookmark(doc, root):
    rel = os.path.basename(path)
    if "$schema" not in doc:
        problems.append(f"{rel}: немає $schema — Desktop не відкриє файл")
    opts = doc.get("options") or {}
    if opts.get("suppressData") and opts.get("suppressDisplay"):
        warns.append(f"{rel}: suppressData і suppressDisplay разом — букмарка нічого не робить")
    targets = opts.get("targetVisualNames")
    only = bool(opts.get("applyOnlyToTargetVisuals"))
    if only and not targets:
        problems.append(f"{rel}: applyOnlyToTargetVisuals без targetVisualNames — букмарка нічого не змінює")
    touched = set()
    for sec, body in ((doc.get("explorationState") or {}).get("sections") or {}).items():
        for vid, vc in (body.get("visualContainers") or {}).items():
            touched.add(vid)
            mode = (((vc or {}).get("singleVisual") or {}).get("display") or {}).get("mode")
            if mode and mode not in MODE_ENUM:
                problems.append(f"{rel}: display.mode «{mode}» поза enum {sorted(MODE_ENUM)}")
        walk_groups(body.get("visualContainerGroups"), touched)
    if only and targets:
        for t in sorted(t for t in touched if t not in set(targets)):
            problems.append(f"{rel}: «{t}» є в explorationState, але НЕ в targetVisualNames — "
                            f"зміна мовчки ігнорується (гочча №1)")
    stem = os.path.basename(path)[:-len(".bookmark.json")]
    if doc.get("name") != stem:
        warns.append(f"{rel}: name «{doc.get('name')}» ≠ імʼя файлу «{stem}»")
    if root:
        idx = os.path.join(root, "definition", "bookmarks", "bookmarks.json")
        if os.path.exists(idx):
            try:
                listed = set()
                for it in load(idx).get("items") or []:
                    listed.add(it.get("name"))
                    for ch in it.get("children") or []:
                        listed.add(ch)
                if stem not in listed:
                    warns.append(f"{rel}: не зареєстрований у bookmarks.json — Desktop його не бачить")
            except Exception:  # noqa
                pass


def check_bookmarks_index(doc, root):
    rel = "bookmarks.json"
    if "$schema" not in doc:
        problems.append(f"{rel}: немає $schema")
    files = bookmark_names(root) if root else None
    for i, it in enumerate(doc.get("items") or []):
        keys = set(it.keys()) if isinstance(it, dict) else set()
        if keys == {"name"}:
            names = [it["name"]]
        elif keys == {"name", "displayName", "children"} and isinstance(it.get("children"), list):
            names = list(it["children"])
        else:
            problems.append(f"{rel} items[{i}]: не leaf {{name}} і не group {{name,displayName,children}} "
                            f"(ключі {sorted(keys)}) — звіт не відкриється (І-22)")
            continue
        if files is not None:
            for n in names:
                if n not in files:
                    problems.append(f"{rel}: «{n}» не має файлу {n}.bookmark.json")


def check_visual(doc, root):
    rel = os.path.relpath(path, root) if root else os.path.basename(path)
    vis = doc.get("visual") or {}
    vtype = vis.get("visualType")
    pages = page_names(root) if root else None
    bms = bookmark_names(root) if root else None
    for link in ((vis.get("visualContainerObjects") or {}).get("visualLink") or []):
        props = link.get("properties") or {}
        t = literal(props.get("type")) if "type" in props else None
        if t is None:
            continue
        if t not in LINK_TYPES:
            warns.append(f"{rel}: visualLink.type «{t}» невідомий — звір з Desktop-емітованим файлом")
        for key in ("navigationSection", "drillthroughSection"):
            if key in props:
                target = literal(props[key])
                if pages is not None and target not in pages:
                    problems.append(f"{rel}: {key} «{target}» не є name жодної сторінки в definition/pages "
                                    f"(displayName замість name?)")
        if "bookmark" in props:
            target = literal(props["bookmark"])
            if bms is not None and target not in bms:
                problems.append(f"{rel}: bookmark «{target}» не має файлу definition/bookmarks/{target}.bookmark.json")
        if t == "PageNavigation" and "navigationSection" not in props:
            problems.append(f"{rel}: PageNavigation без navigationSection")
        if t == "Bookmark" and "bookmark" not in props:
            problems.append(f"{rel}: type Bookmark без ключа bookmark")
        if t in ("ClearAllSlicers", "Back") and "bookmark" in props:
            problems.append(f"{rel}: {t} не приймає ключ bookmark — Desktop скине картку")
    for card, entries in (vis.get("objects") or {}).items():
        if not isinstance(entries, list):
            continue
        for e in entries:
            props = (e or {}).get("properties") or {}
            sel = (e or {}).get("selector")
            if set(props.keys()) == {"show"} and sel:
                warns.append(f"{rel}: objects.{card}: show із селектором — Desktop скине картку (закон серіалізації)")
            elif props and "show" not in props and not sel and vtype in ("actionButton", "shape", "image",
                                                                            "pageNavigator", "bookmarkNavigator"):
                warns.append(f"{rel}: objects.{card}: значення без selector — Desktop скине картку")
            sid = (sel or {}).get("id") if isinstance(sel, dict) else None
            if vtype in ("pageNavigator", "bookmarkNavigator") and sid and sid not in NAV_SELECTORS:
                problems.append(f"{rel}: навігатор із selector id «{sid}» — усі плитки зникнуть; "
                                f"дозволено {sorted(NAV_SELECTORS)}")


# ---------- dispatch ----------
try:
    raw = io.open(path, encoding="utf-8").read()
except OSError:
    sys.exit(0)
try:
    doc = json.loads(raw)
except Exception as e:  # noqa
    print(f"{os.path.basename(path)} НЕ ПАРСИТЬСЯ після правки: {e}", file=sys.stderr)
    sys.exit(2)

base = os.path.basename(path)
root = report_root(path)
if base.endswith(".bookmark.json"):
    check_bookmark(doc, root)
elif base == "bookmarks.json":
    check_bookmarks_index(doc, root)
elif base == "visual.json":
    check_visual(doc, root)
elif base == "report.json" and isinstance(doc.get("sections"), list):
    check_legacy(doc)
# page.json / pages.json / definition/report.json: parse-only

for w in warns:
    print(" ! " + w, file=sys.stderr)
if problems:
    print("Перевірка звіту (hook pbi-report-ux):", file=sys.stderr)
    for p in problems:
        print(" - " + p, file=sys.stderr)
    sys.exit(2)
sys.exit(0)
