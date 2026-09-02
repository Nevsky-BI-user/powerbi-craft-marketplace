#!/usr/bin/env python3
"""Validate PBIR (enhanced) bookmarks of a .Report folder: schema + references.

usage: python pbir_schema_validate.py <path/to/X.Report> [--no-net]
       (a trailing /definition is tolerated; flags may come in any order;
        a folder without definition/ fails with exit 1 instead of a false OK)

1. Every definition/bookmarks/*.bookmark.json and bookmarks.json is validated
   against the $schema URL it declares (needs `pip install jsonschema`; with
   --no-net or offline the schema step is skipped and reported as SKIPPED).
2. Referential checks that no schema can express:
   - every name in bookmarks.json (leaf or child) has a <name>.bookmark.json;
   - every <name>.bookmark.json is listed in bookmarks.json;
   - bookmarks.json items are exactly leaf {name} or group {name,displayName,children};
   - with applyOnlyToTargetVisuals, every id touched in explorationState is in
     targetVisualNames (the silent-ignore gotcha);
   - every targetVisualNames id exists as a visual or group on the captured page;
   - display.mode values are in the schema enum;
   - suppressData and suppressDisplay are not both true.
Exit 1 on any error; warnings never fail the run.
"""
import glob
import io
import json
import os
import sys
import urllib.request

MODE_ENUM = {"maximize", "spotlight", "elevation", "hidden"}
_schema_cache = {}


def load(p):
    return json.load(io.open(p, encoding="utf-8"))


def fetch_schema(url):
    if url in _schema_cache:
        return _schema_cache[url]
    with urllib.request.urlopen(url, timeout=20) as r:
        _schema_cache[url] = json.load(r)
    return _schema_cache[url]


def schema_check(doc, rel, use_net, errors, notes):
    url = doc.get("$schema")
    if not url:
        errors.append(f"{rel}: немає $schema")
        return
    if not use_net:
        notes.append(f"{rel}: schema SKIPPED (--no-net)")
        return
    try:
        import jsonschema  # noqa
    except ImportError:
        notes.append(f"{rel}: schema SKIPPED (pip install jsonschema)")
        return
    try:
        schema = fetch_schema(url)
    except Exception as e:  # noqa
        notes.append(f"{rel}: schema SKIPPED (не завантажилась: {e})")
        return
    from jsonschema import Draft7Validator
    for err in sorted(Draft7Validator(schema).iter_errors(doc), key=lambda e: list(e.path)):
        path = "/".join(str(x) for x in err.path) or "<root>"
        errors.append(f"{rel}: schema {path}: {err.message[:160]}")


def page_ids(report_dir, section):
    """All visual and group names on a page (by page folder name or page.json name)."""
    pages = os.path.join(report_dir, "definition", "pages")
    for pdir in glob.glob(os.path.join(pages, "*")):
        if not os.path.isdir(pdir):
            continue
        pj = os.path.join(pdir, "page.json")
        pname = os.path.basename(pdir)
        try:
            pname = load(pj).get("name", pname)
        except Exception:  # noqa
            pass
        if pname != section and os.path.basename(pdir) != section:
            continue
        ids = set()
        for vj in glob.glob(os.path.join(pdir, "visuals", "*", "visual.json")):
            try:
                ids.add(load(vj).get("name", os.path.basename(os.path.dirname(vj))))
            except Exception:  # noqa
                ids.add(os.path.basename(os.path.dirname(vj)))
        return ids
    return None


def walk_groups(node, out):
    for gid, g in (node or {}).items():
        out.add(gid)
        if isinstance(g, dict) and "children" in g:
            walk_groups(g["children"], out)


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__)
        return 1
    report_dir = os.path.normpath(paths[0])
    if os.path.basename(report_dir) == "definition":
        report_dir = os.path.dirname(report_dir)
    use_net = "--no-net" not in argv
    if not os.path.isdir(os.path.join(report_dir, "definition")):
        print(f"FAIL: {report_dir} не схожий на PBIR enhanced .Report (немає теки definition/)")
        return 1
    bdir = os.path.join(report_dir, "definition", "bookmarks")
    errors, warns, notes = [], [], []
    if not os.path.isdir(bdir):
        print(f"OK: {report_dir} не має definition/bookmarks — нічого перевіряти")
        return 0

    files = {os.path.basename(p)[:-len(".bookmark.json")]: p
             for p in glob.glob(os.path.join(bdir, "*.bookmark.json"))}
    index_path = os.path.join(bdir, "bookmarks.json")
    listed = set()
    if os.path.exists(index_path):
        idx = load(index_path)
        schema_check(idx, "bookmarks.json", use_net, errors, notes)
        for i, it in enumerate(idx.get("items") or []):
            keys = set(it.keys())
            if keys == {"name"}:
                listed.add(it["name"])
            elif keys == {"name", "displayName", "children"} and isinstance(it["children"], list):
                for ch in it["children"]:
                    listed.add(ch)
            else:
                errors.append(f"bookmarks.json items[{i}]: не leaf {{name}} і не group "
                              f"{{name,displayName,children}} (ключі {sorted(keys)}) — звіт не відкриється (І-22)")
        for n in listed:
            if n not in files:
                errors.append(f"bookmarks.json: «{n}» не має файлу {n}.bookmark.json")
    else:
        errors.append("немає definition/bookmarks/bookmarks.json — жодна букмарка не існує для Desktop")

    for name, p in sorted(files.items()):
        rel = os.path.basename(p)
        try:
            doc = load(p)
        except Exception as e:  # noqa
            errors.append(f"{rel}: JSON не парситься: {e}")
            continue
        schema_check(doc, rel, use_net, errors, notes)
        if doc.get("name") != name:
            warns.append(f"{rel}: name «{doc.get('name')}» ≠ імʼя файлу «{name}»")
        if name not in listed and os.path.exists(index_path):
            warns.append(f"{rel}: не зареєстрований у bookmarks.json — Desktop його не бачить")
        opts = doc.get("options") or {}
        if opts.get("suppressData") and opts.get("suppressDisplay"):
            warns.append(f"{rel}: suppressData і suppressDisplay разом — букмарка нічого не робить")
        targets = opts.get("targetVisualNames")
        only = bool(opts.get("applyOnlyToTargetVisuals"))
        if only and not targets:
            errors.append(f"{rel}: applyOnlyToTargetVisuals без targetVisualNames — букмарка нічого не змінює")
        touched, sections = set(), (doc.get("explorationState") or {}).get("sections") or {}
        for sec, body in sections.items():
            for vid, vc in (body.get("visualContainers") or {}).items():
                touched.add(vid)
                mode = (((vc or {}).get("singleVisual") or {}).get("display") or {}).get("mode")
                if mode and mode not in MODE_ENUM:
                    errors.append(f"{rel}: display.mode «{mode}» поза enum {sorted(MODE_ENUM)}")
            walk_groups(body.get("visualContainerGroups"), touched)
            ids = page_ids(report_dir, sec)
            if ids is None:
                warns.append(f"{rel}: сторінку «{sec}» не знайдено в definition/pages — перевірка id пропущена")
                continue
            for t in (targets or []):
                if t not in ids:
                    warns.append(f"{rel}: targetVisualNames «{t}» немає на сторінці «{sec}» (видалений візуал?)")
            for t in touched:
                if t not in ids:
                    warns.append(f"{rel}: explorationState торкається «{t}», якого немає на сторінці «{sec}»")
        if only and targets:
            missing = sorted(t for t in touched if t not in set(targets))
            for t in missing:
                errors.append(f"{rel}: «{t}» є в explorationState, але НЕ в targetVisualNames — зміна мовчки ігнорується")

    for n in notes:
        print("  · " + n)
    for w in warns:
        print("  ! " + w)
    if errors:
        print(f"FAIL: {len(errors)} помилок")
        for e in errors:
            print("  - " + e)
        return 1
    print(f"OK: {len(files)} букмарок, {len(warns)} попереджень")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
