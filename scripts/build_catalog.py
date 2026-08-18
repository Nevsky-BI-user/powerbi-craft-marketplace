"""Генерує site/src/catalog.json з plugins/**/SKILL.md + plugin.json + CHANGELOG.md.

Запускається в CI перед збіркою сайту і локально при зміні скілів.
Каталог — похідний артефакт; джерело істини — фронтматтери скілів.
"""
import glob
import io
import json
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site", "src", "catalog.json")

TAGLINES = {
    "pbi-visuals": "що малюємо",
    "pbi-report-ux": "як сторінка працює",
    "pbi-design-language": "як виглядає",
    "pbi-quality": "чи правильно",
    "report-storytelling": "що стверджує",
    "dax-craft": "обчислення й кодові візуали",
    "pbip-devops": "git-цикл PBIP",
    "azure-ops": "хмара довкола",
    "project-bootstrap": "старт проєктів",
}


def parse_frontmatter(path):
    t = io.open(path, encoding="utf-8").read()
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", t, re.S)
    if not m:
        raise SystemExit(f"{path}: немає фронтматтера")
    d = yaml.safe_load(m.group(1))
    if not isinstance(d, dict) or not d.get("name") or not d.get("description"):
        raise SystemExit(f"{path}: фронтматтер без name/description")
    return d


TRIGGER_RE = re.compile(r"(?:Triggers?\s*[-:]|Trigger on:|WHEN:)\s*")


def split_description(desc):
    """Коротка частина (до меж/тригерів) + список тригер-фраз.

    Точка зрізу і точка витягання тригерів — ОДИН регекс, щоб майбутній
    формат опису не показував список тригерів двічі.
    """
    desc = " ".join(str(desc).split())
    cut = len(desc)
    tm = TRIGGER_RE.search(desc)
    for marker in ("Do NOT trigger", "Do NOT USE", "NOT for "):
        i = desc.find(marker)
        if i > 40:
            cut = min(cut, i)
    if tm and tm.start() > 40:
        cut = min(cut, tm.start())
    short = desc[:cut].strip().rstrip("—-· ").strip()
    triggers = []
    if tm:
        tail = desc[tm.end():]
        triggers = re.findall(r"[\'\"«]([^\'\"«»]{2,60})[\'\"»]", tail)
        if not triggers:
            triggers = [p.strip(" .") for p in tail.split(",") if 2 <= len(p.strip()) <= 60][:12]
    return short, triggers[:12]


def parse_changelog():
    path = os.path.join(ROOT, "CHANGELOG.md")
    if not os.path.exists(path):
        return []
    entries = []
    cur = None
    for line in io.open(path, encoding="utf-8").read().splitlines():
        m = re.match(r"^##\s+([\d.]+)\s+—\s+(\S+)", line)
        if m:
            cur = {"version": m.group(1), "date": m.group(2), "title": "", "items": []}
            entries.append(cur)
            continue
        if cur is None:
            continue
        if line.startswith("- "):
            cur["items"].append(line[2:].strip())
        elif line.startswith("  ") and cur["items"]:
            cur["items"][-1] += " " + line.strip()
        elif line.strip() and not cur["title"] and not line.startswith("#"):
            cur["title"] = line.strip()
    return entries


# Українські короткі описи скілів (кураторський словник, scripts/uk_descriptions.json);
# скіли без запису чесно падають на англійський short у фронтенді
UK_PATH = os.path.join(ROOT, "scripts", "uk_descriptions.json")
UK = json.load(io.open(UK_PATH, encoding="utf-8")) if os.path.exists(UK_PATH) else {}

# Порядок і склад плагінів — з marketplace.json (джерело істини), не з TAGLINES
mp_manifest = json.load(io.open(
    os.path.join(ROOT, ".claude-plugin", "marketplace.json"), encoding="utf-8"))
plugin_order = [p["name"] for p in mp_manifest["plugins"]]
on_disk = {os.path.basename(d.rstrip("/\\"))
           for d in glob.glob(os.path.join(ROOT, "plugins", "*")) if os.path.isdir(d)}
if set(plugin_order) != on_disk:
    sys.exit(f"marketplace.json і plugins/ розійшлись: {set(plugin_order) ^ on_disk}")

plugins = []
total_skills = 0
for pname in plugin_order:
    proot = os.path.join(ROOT, "plugins", pname)
    pj = json.load(io.open(os.path.join(proot, ".claude-plugin", "plugin.json"), encoding="utf-8"))
    skills = []
    for sp in sorted(glob.glob(os.path.join(proot, "skills", "*", "SKILL.md"))):
        d = parse_frontmatter(sp)
        short, triggers = split_description(d["description"])
        skills.append({
            "name": d["name"],
            "short": short,
            "shortUk": UK.get(d["name"], ""),
            "description": " ".join(str(d["description"]).split()),
            "triggers": triggers,
        })
        total_skills += 1
    agents = [os.path.basename(a)[:-3] for a in glob.glob(os.path.join(proot, "agents", "*.md"))]
    plugins.append({
        "name": pname,
        "version": pj.get("version", "?"),
        "description": pj.get("description", ""),
        "tagline": TAGLINES.get(pname, ""),
        "hasHooks": os.path.isdir(os.path.join(proot, "hooks")),
        "agents": agents,
        "skills": skills,
    })

catalog = {
    "marketplace": {
        "name": mp_manifest["name"],
        "repo": "Nevsky-BI-user/powerbi-craft-marketplace",
        "description": mp_manifest.get("description", ""),
    },
    "totals": {"plugins": len(plugins), "skills": total_skills},
    "plugins": plugins,
    "changelog": parse_changelog(),
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
io.open(OUT, "w", encoding="utf-8", newline="\n").write(
    json.dumps(catalog, ensure_ascii=False, indent=1))
no_uk = [s["name"] for p in plugins for s in p["skills"] if not s["shortUk"]]
print(f"catalog.json: {len(plugins)} плагінів, {total_skills} скілів, "
      f"{len(catalog['changelog'])} записів changelog")
if no_uk:
    print(f"без українського опису ({len(no_uk)}): " + ", ".join(no_uk))
if total_skills < 40:
    sys.exit("ПІДОЗРІЛО МАЛО СКІЛІВ — перевір структуру plugins/")
