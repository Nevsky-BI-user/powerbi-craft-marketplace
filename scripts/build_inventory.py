"""Знімок ВСІХ скілів цієї машини (не лише powerbi-craft) → site/src/inventory.json.

Запускається ЛОКАЛЬНО на машині автора (CI цього ПК не бачить) — результат
комітиться в репо з датою знімка. Санітизація: жодних локальних шляхів у виході.

Групи (кольори на сайті):
  anthropic   — плагіни claude-plugins-official (бандл Anthropic)
  microsoft   — fabric-collection (microsoft/skills-for-fabric)
  goblin      — power-bi-agentic-development (data-goblin, Kurt Buhler)
  standalone  — окремі скіли ~/.claude/skills поза маркетплейсом powerbi-craft
  project     — проєктні скіли робочих репо (приватні, без встановлення)
"""
import datetime
import glob
import io
import json
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOME = os.path.expanduser("~")
CLAUDE = os.path.join(HOME, ".claude")
OUT = os.path.join(ROOT, "site", "src", "inventory.json")

MP_META = {
    "claude-plugins-official": {
        "group": "anthropic", "title": "Бандл Anthropic (офіційний маркетплейс)",
        "repo": "anthropics/claude-plugins-official", "addCmd": None,
    },
    "fabric-collection": {
        "group": "microsoft", "title": "Microsoft skills-for-fabric",
        "repo": "microsoft/skills-for-fabric",
        "addCmd": "claude plugin marketplace add microsoft/skills-for-fabric",
    },
    "power-bi-agentic-development": {
        "group": "goblin", "title": "Kurt Buhler — power-bi-agentic-development",
        "repo": "data-goblin/power-bi-agentic-development",
        "addCmd": "claude plugin marketplace add data-goblin/power-bi-agentic-development",
    },
}

# Відомі джерела окремих скілів (звідки їх ставили)
STANDALONE_SOURCES = {
    "fact-checker": "daymade/claude-code-skills",
    "grilling": "mattpocock/skills",
    "grill-me": "mattpocock/skills",
}

PROJECT_SKILL_DIRS = [
    # (публічна назва проєкту, тека) — вміст приватний, показуємо лише назви
    ("Rayfin Operational Monitoring (приватний)",
     r"C:\github\Rayfin_Operational_Monitoring\.claude\skills"),
]


def frontmatter(path):
    t = io.open(path, encoding="utf-8", errors="replace").read()
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", t, re.S)
    if not m:
        return None
    try:
        d = yaml.safe_load(m.group(1))
    except Exception:
        return None
    if not isinstance(d, dict) or not d.get("name"):
        return None
    return d


def short_desc(desc, limit=160):
    desc = " ".join(str(desc or "").split())
    for marker in ("Do NOT trigger", "Do NOT USE", "Triggers -", "Trigger on:", "WHEN:", "Dispatch"):
        i = desc.find(marker)
        if i > 30:
            desc = desc[:i]
    desc = desc.strip().rstrip("—-· ").strip()
    return desc[:limit] + ("…" if len(desc) > limit else "")


# 1. Власні скіли маркетплейсу — щоб виключити їх зі standalone
own = set()
for p in glob.glob(os.path.join(ROOT, "plugins", "*", "skills", "*")):
    own.add(os.path.basename(p))

# 2. Маркетплейси з кешу плагінів
groups = {}
for mp_name, meta in MP_META.items():
    plugins = []
    seen_plugins = {}
    for sk in sorted(glob.glob(os.path.join(
            CLAUDE, "plugins", "cache", mp_name, "*", "*", "skills", "*", "SKILL.md"))):
        parts = sk.replace("\\", "/").split("/")
        plugin_name = parts[-5]
        d = frontmatter(sk)
        if d is None:
            continue
        entry = seen_plugins.setdefault(plugin_name, {
            "name": plugin_name,
            "installCmd": f"claude plugin install {plugin_name}@{mp_name}",
            "skills": [],
        })
        if any(s["name"] == d["name"] for s in entry["skills"]):
            continue
        entry["skills"].append({"name": d["name"], "short": short_desc(d.get("description"))})
    plugins = [seen_plugins[k] for k in sorted(seen_plugins)]
    unique = {s["name"] for p in plugins for s in p["skills"]}
    groups[meta["group"]] = {
        "group": meta["group"], "title": meta["title"], "repo": meta["repo"],
        "addCmd": meta["addCmd"], "plugins": plugins,
        "skillCount": sum(len(p["skills"]) for p in plugins),
        "uniqueCount": len(unique),
    }

# 3. Окремі скіли ~/.claude/skills поза powerbi-craft
standalone = []
for sk in sorted(glob.glob(os.path.join(CLAUDE, "skills", "*", "SKILL.md"))):
    name = os.path.basename(os.path.dirname(sk))
    if name in own:
        continue
    d = frontmatter(sk)
    if d is None:
        continue
    src = STANDALONE_SOURCES.get(name)
    standalone.append({
        "name": name,
        "short": short_desc(d.get("description")),
        "source": src,
    })
groups["standalone"] = {
    "group": "standalone", "title": "Окремі скіли (поза маркетплейсами)",
    "repo": None, "addCmd": None, "plugins": [],
    "skills": standalone, "skillCount": len(standalone),
    "uniqueCount": len(standalone),
}

# 4. Проєктні скіли — лише назви, без описів (приватні репо)
project = []
for label, d in PROJECT_SKILL_DIRS:
    for sk in sorted(glob.glob(os.path.join(d, "*", "SKILL.md"))):
        project.append({"name": os.path.basename(os.path.dirname(sk)),
                        "short": f"проєктний скіл — {label}", "source": None})
groups["project"] = {
    "group": "project", "title": "Проєктні скіли (приватні репозиторії)",
    "repo": None, "addCmd": None, "plugins": [],
    "skills": project, "skillCount": len(project),
    "uniqueCount": len(project),
}

inventory = {
    "snapshotDate": datetime.date.today().isoformat(),
    "groups": [groups[g] for g in ("anthropic", "microsoft", "goblin", "standalone", "project")],
}

blob = json.dumps(inventory, ensure_ascii=False, indent=1)
for forbidden in ("HEAVY_METAL", "C:\\\\", "C:/", "Users\\\\"):
    if forbidden in blob:
        sys.exit(f"САНІТИЗАЦІЯ ПРОВАЛЕНА: у виході є «{forbidden}»")
io.open(OUT, "w", encoding="utf-8", newline="\n").write(blob)
total = sum(g["skillCount"] for g in inventory["groups"])
print(f"inventory.json: {total} скілів у {len(inventory['groups'])} групах — " +
      ", ".join(f"{g['group']}:{g['skillCount']}" for g in inventory["groups"]))
