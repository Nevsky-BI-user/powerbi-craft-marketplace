"""Знімок скілів середовища цієї машини → site/src/inventory.json.

Запускається ЛОКАЛЬНО на машині автора (CI цього ПК не бачить) — результат
комітиться в репо з датою знімка. Санітизація: жодних локальних шляхів у виході.

Групи (розділи та кольори на сайті):
  anthropic   — плагіни claude-plugins-official (бандл Anthropic)
  microsoft   — fabric-collection (microsoft/skills-for-fabric)
  goblin      — power-bi-agentic-development (data-goblin, Kurt Buhler)
  standalone  — окремі скіли ~/.claude/skills поза маркетплейсом powerbi-craft,
                згруповані за публічним джерелом (репозиторієм)
Проєктні скіли приватних репо на сайт НЕ потрапляють (рішення 2026-08-18).
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

# Українські короткі описи (спільний словник із build_catalog.py)
UK_PATH = os.path.join(ROOT, "scripts", "uk_descriptions.json")
UK = json.load(io.open(UK_PATH, encoding="utf-8")) if os.path.exists(UK_PATH) else {}
# Описи ПЛАГІНІВ лишаються англійською — мовою їхніх авторів (рішення 2026-08-18)

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

# Публічні джерела окремих скілів — перевірені по GitHub API 2026-08-18
# (лістинг дерева репо або пряме посилання в SKILL.md; не вгадувались).
# dir — префікс теки зі скілами в репо ("" = корінь; None = скіл не лежить у репо текою).
# marketplace=True — репо містить .claude-plugin/marketplace.json.
SOURCE_META = {
    "anthropic-skills": {
        "title": "Anthropic — anthropics/skills", "repo": "anthropics/skills",
        "dir": "skills", "marketplace": True,
        "note": "Офіційний репозиторій скілів Anthropic, опублікований і як маркетплейс плагінів.",
    },
    "superpowers": {
        "title": "Superpowers (Jesse Vincent)", "repo": "obra/superpowers",
        "dir": "skills", "marketplace": True,
        "note": "Дисципліна розробки: TDD, планування, ревʼю, git worktree, субагенти.",
    },
    "threejs": {
        "title": "Three.js game skills", "repo": "majidmanzarpour/threejs-game-skills",
        "dir": "skills", "marketplace": False,
        "note": "Набір для Three.js-ігор: геймплей, графіка, UI, QA, генерація ассетів.",
    },
    "supabase": {
        "title": "Supabase — agent-skills", "repo": "supabase/agent-skills",
        "dir": "skills", "marketplace": True,
        "note": "Офіційні скіли Supabase: Postgres-практики й робота з платформою.",
    },
    "mattpocock": {
        "title": "Matt Pocock / skills", "repo": "mattpocock/skills",
        "dir": "skills/productivity", "marketplace": True,
        "note": "Скіли Метта Покока: жорстке ревʼю коду і планів.",
    },
    "daymade": {
        "title": "daymade / claude-code-skills", "repo": "daymade/claude-code-skills",
        "dir": "", "marketplace": True,
        "note": "Колекція прикладних скілів (fact-checker та ін.).",
    },
    "shadcn": {
        "title": "shadcn/ui", "repo": "shadcn-ui/ui",
        "dir": "skills", "marketplace": False,
        "note": "Монорепозиторій shadcn/ui; містить власний скіл для роботи з компонентами.",
    },
    "microsoftdocs": {
        "title": "Microsoft — Agent-Skills (Azure)", "repo": "MicrosoftDocs/Agent-Skills",
        "dir": "skills", "marketplace": False,
        "note": "Понад 200 скілів Microsoft по сервісах Azure, зібраних із Microsoft Learn. "
                "Репо є і маркетплейсом (плагін azure-agent-skills ставить усі одразу), "
                "але зазвичай потрібен один-два — тому нижче промпт на окремий скіл. "
                "Azure DevOps у парі з офіційним MCP-сервером @azure-devops/mcp керує "
                "організацією напряму: пайплайни, робочі елементи, PR.",
    },
    "awesome-copilot": {
        "title": "GitHub — awesome-copilot", "repo": "github/awesome-copilot",
        "dir": "skills", "marketplace": False,
        "note": "Комʼюніті-репозиторій GitHub; серед іншого — скіл оптимізації DAX.",
    },
    "vercel": {
        "title": "Vercel — web-interface-guidelines", "repo": "vercel-labs/web-interface-guidelines",
        "dir": None, "marketplace": False,
        "note": "Скіл-обгортка: тягне гайдлайни вебінтерфейсів Vercel із цього репо на льоту.",
    },
    "local": {
        "title": "Без канонічного джерела", "repo": None, "dir": None, "marketplace": False,
        "note": "У цих скілів немає канонічного репозиторію (для emil-design-eng і humanizer "
                "у мережі лише дзеркала без явного автора). На картці кожного є промпт: "
                "скопіюйте його в Claude Code, і той знайде або відтворить скіл сам.",
    },
}

SKILL_SOURCE = {
    "algorithmic-art": "anthropic-skills",
    "brand-guidelines": "anthropic-skills",
    "canvas-design": "anthropic-skills",
    "claude-api": "anthropic-skills",
    "doc-coauthoring": "anthropic-skills",
    "docx": "anthropic-skills",
    "frontend-design": "anthropic-skills",
    "internal-comms": "anthropic-skills",
    "mcp-builder": "anthropic-skills",
    "pdf": "anthropic-skills",
    "pptx": "anthropic-skills",
    "skill-creator": "anthropic-skills",
    "slack-gif-creator": "anthropic-skills",
    "template-skill": "anthropic-skills",
    "theme-factory": "anthropic-skills",
    "web-artifacts-builder": "anthropic-skills",
    "webapp-testing": "anthropic-skills",
    "xlsx": "anthropic-skills",
    "brainstorming": "superpowers",
    "dispatching-parallel-agents": "superpowers",
    "executing-plans": "superpowers",
    "finishing-a-development-branch": "superpowers",
    "receiving-code-review": "superpowers",
    "requesting-code-review": "superpowers",
    "subagent-driven-development": "superpowers",
    "systematic-debugging": "superpowers",
    "test-driven-development": "superpowers",
    "using-git-worktrees": "superpowers",
    "using-superpowers": "superpowers",
    "verification-before-completion": "superpowers",
    "writing-plans": "superpowers",
    "writing-skills": "superpowers",
    "threejs-3d-generator": "threejs",
    "threejs-aaa-graphics-builder": "threejs",
    "threejs-audio-generator": "threejs",
    "threejs-debug-profiler": "threejs",
    "threejs-game-director": "threejs",
    "threejs-game-ui-designer": "threejs",
    "threejs-gameplay-systems": "threejs",
    "threejs-image-generator": "threejs",
    "threejs-qa-release": "threejs",
    "supabase": "supabase",
    "supabase-postgres-best-practices": "supabase",
    "grilling": "mattpocock",
    "grill-me": "mattpocock",
    "fact-checker": "daymade",
    "shadcn": "shadcn",
    "power-bi-dax-optimization": "awesome-copilot",
    "azure-devops": "microsoftdocs",
    "web-design-guidelines": "vercel",
    "graphify": "local",
    "model-orchestration": "local",
    "emil-design-eng": "local",
    "humanizer": "local",
}


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
    seen_plugins = {}
    for sk in sorted(glob.glob(os.path.join(
            CLAUDE, "plugins", "cache", mp_name, "*", "*", "skills", "*", "SKILL.md"))):
        parts = sk.replace("\\", "/").split("/")
        plugin_name = parts[-5]
        d = frontmatter(sk)
        if d is None:
            continue
        if plugin_name not in seen_plugins:
            pj_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(sk))),
                                   ".claude-plugin", "plugin.json")
            p_desc = ""
            if os.path.exists(pj_path):
                try:
                    p_desc = json.load(io.open(pj_path, encoding="utf-8")).get("description", "")
                except Exception:
                    p_desc = ""
            seen_plugins[plugin_name] = {
                "name": plugin_name,
                "installCmd": f"claude plugin install {plugin_name}@{mp_name}",
                "short": short_desc(p_desc),
                "skills": [],
            }
        entry = seen_plugins[plugin_name]
        if any(s["name"] == d["name"] for s in entry["skills"]):
            continue
        entry["skills"].append({"name": d["name"], "short": short_desc(d.get("description")),
                                "shortUk": UK.get(d["name"], "")})
    plugins = [seen_plugins[k] for k in sorted(seen_plugins)]
    unique = {s["name"] for p in plugins for s in p["skills"]}
    groups[meta["group"]] = {
        "group": meta["group"], "title": meta["title"], "repo": meta["repo"],
        "addCmd": meta["addCmd"], "plugins": plugins,
        "skillCount": sum(len(p["skills"]) for p in plugins),
        "uniqueCount": len(unique),
    }

# 3. Окремі скіли ~/.claude/skills поза powerbi-craft — за джерелами
by_source = {sid: [] for sid in SOURCE_META}
unmapped = []
for sk in sorted(glob.glob(os.path.join(CLAUDE, "skills", "*", "SKILL.md"))):
    name = os.path.basename(os.path.dirname(sk))
    if name in own:
        continue
    d = frontmatter(sk)
    if d is None:
        continue
    sid = SKILL_SOURCE.get(name)
    if sid is None:
        unmapped.append(name)
        sid = "local"
    by_source[sid].append({"name": name, "short": short_desc(d.get("description")),
                           "shortUk": UK.get(name, "")})

sources = []
for sid, meta in SOURCE_META.items():
    if not by_source[sid]:
        continue
    sources.append({
        "id": sid, "title": meta["title"], "repo": meta["repo"], "dir": meta["dir"],
        "marketplace": meta["marketplace"], "note": meta["note"],
        "skills": by_source[sid],
    })
# найбільші джерела спершу, «локальні» — завжди останні
sources.sort(key=lambda s: (s["repo"] is None, -len(s["skills"]), s["id"]))
n_standalone = sum(len(s["skills"]) for s in sources)
groups["standalone"] = {
    "group": "standalone", "title": "Окремі скіли (поза маркетплейсами)",
    "repo": None, "addCmd": None, "plugins": [],
    "sources": sources, "skillCount": n_standalone, "uniqueCount": n_standalone,
}

inventory = {
    "snapshotDate": datetime.date.today().isoformat(),
    "groups": [groups[g] for g in ("anthropic", "microsoft", "goblin", "standalone")],
}

blob = json.dumps(inventory, ensure_ascii=False, indent=1)
for forbidden in ("HEAVY_METAL", "C:\\\\", "C:/", "Users\\\\"):
    if forbidden in blob:
        sys.exit(f"САНІТИЗАЦІЯ ПРОВАЛЕНА: у виході є «{forbidden}»")
io.open(OUT, "w", encoding="utf-8", newline="\n").write(blob)
total = sum(g["skillCount"] for g in inventory["groups"])
print(f"inventory.json: {total} скілів у {len(inventory['groups'])} групах — " +
      ", ".join(f"{g['group']}:{g['skillCount']}" for g in inventory["groups"]))
if unmapped:
    print(f"без джерела ({len(unmapped)}): " + ", ".join(unmapped))
