"""CI-валідація маркетплейсу. Самодостатня: лише stdlib + PyYAML.

Ловить класи багів, які вже стріляли в цьому репозиторії:
  A. Битий YAML-фронтматтер SKILL.md (рантайм губить його МОВЧКИ) — v0.1.0
     відвантажив 4 такі скіли.
  B. Локальні шляхи/імена в копіях (C:\\Users, C:\\github, HEAVY_METAL).
  C. CRLF у *.sh (bash на Windows-checkout падає на \\r).
  D. Розсинхрон версій plugin.json <-> marketplace.json.
  E. Плагін заявляє скіл, якого нема на диску (і навпаки).
"""
import glob
import io
import json
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors = []


def err(msg):
    errors.append(msg)


# A. фронтматтер кожного SKILL.md
for p in glob.glob(os.path.join(ROOT, "plugins", "*", "skills", "*", "SKILL.md")):
    rel = os.path.relpath(p, ROOT)
    t = io.open(p, encoding="utf-8").read()
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", t, re.S)
    if not m:
        err(f"{rel}: немає YAML-фронтматтера")
        continue
    try:
        d = yaml.safe_load(m.group(1))
    except Exception as e:
        err(f"{rel}: YAML битий ({str(e).splitlines()[0]})")
        continue
    if not isinstance(d, dict) or not d.get("name") or not d.get("description"):
        err(f"{rel}: фронтматтер без name/description")
        continue
    dirname = os.path.basename(os.path.dirname(p))
    if d["name"] != dirname:
        err(f"{rel}: name «{d['name']}» != тека «{dirname}»")

# B. санітизація текстових файлів плагінів
FORBIDDEN = [
    (re.compile(r"C:[\\/]+Users[\\/]+HEAVY", re.I), "локальний шлях C:\\Users\\HEAVY_METAL"),
    (re.compile(r"HEAVY_METAL"), "імʼя локального користувача"),
    (re.compile(r"C:[\\/]+github[\\/]+(?!icons|<)", re.I), "локальний шлях C:\\github"),
]
for p in glob.glob(os.path.join(ROOT, "plugins", "**", "*.*"), recursive=True):
    if not p.endswith((".md", ".json", ".yaml", ".yml", ".txt", ".sh", ".py")):
        continue
    rel = os.path.relpath(p, ROOT)
    try:
        t = io.open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        continue
    for pat, tag in FORBIDDEN:
        if pat.search(t):
            err(f"{rel}: {tag}")

# C. CRLF у shell-скриптах
for p in glob.glob(os.path.join(ROOT, "**", "*.sh"), recursive=True):
    rel = os.path.relpath(p, ROOT)
    if b"\r\n" in io.open(p, "rb").read():
        err(f"{rel}: CRLF — bash впаде на Windows-checkout (перевір .gitattributes)")

# D+E. узгодженість маніфестів
mp = json.load(io.open(os.path.join(ROOT, ".claude-plugin", "marketplace.json"), encoding="utf-8"))
listed = {e["name"]: e for e in mp["plugins"]}
on_disk = {os.path.basename(d.rstrip("/\\"))
           for d in glob.glob(os.path.join(ROOT, "plugins", "*")) if os.path.isdir(d)}
for name in sorted(listed.keys() | on_disk):
    if name not in on_disk:
        err(f"marketplace.json заявляє плагін «{name}», якого нема в plugins/")
        continue
    if name not in listed:
        err(f"plugins/{name} існує, але не заявлений у marketplace.json")
        continue
    pj_path = os.path.join(ROOT, "plugins", name, ".claude-plugin", "plugin.json")
    try:
        pj = json.load(io.open(pj_path, encoding="utf-8"))
    except Exception as e:
        err(f"plugins/{name}/plugin.json: {e}")
        continue
    if pj.get("version") != listed[name].get("version"):
        err(f"{name}: версія plugin.json ({pj.get('version')}) != marketplace.json ({listed[name].get('version')})")

if errors:
    print(f"FAIL: {len(errors)} проблем")
    for e in errors:
        print(" -", e)
    sys.exit(1)
n = len(glob.glob(os.path.join(ROOT, "plugins", "*", "skills", "*", "SKILL.md")))
print(f"OK: {n} скілів, {len(on_disk)} плагінів — фронтматтери, санітизація, LF, версії узгоджені")
