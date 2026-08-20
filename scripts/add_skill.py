# -*- coding: utf-8 -*-
"""Ставить зовнішній скіл у ~/.claude/skills і реєструє його джерело для сайту.

Механіка одним кроком: приймає посилання на скіл у будь-якій зі звичних форм,
знаходить його теку в репозиторії, викачує всі файли, дописує джерело в
scripts/skill_sources.json і перебудовує site/src/inventory.json.

    python scripts/add_skill.py microsoftdocs/agent-skills@azure-devops
    python scripts/add_skill.py owner/repo/skills/some-skill
    python scripts/add_skill.py https://github.com/owner/repo/tree/main/skills/x
    python scripts/add_skill.py owner/repo            # покаже, які скіли є

Прозу (українську підказку і примітку джерела) скрипт не вигадує — лишає
заготовку й друкує, що дописати руками. Решта кроків (збірка сайту, коміт,
пуш, перевірка живого бандла) — у CLAUDE.md.
"""
import io
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# ADD_SKILL_HOME / ADD_SKILL_OVERLAY — гачки для перевірки скрипта на живому
# репозиторії без наслідків: ставлять скіл і реєстр у тимчасову теку.
SKILLS = os.environ.get("ADD_SKILL_HOME") or os.path.join(
    os.path.expanduser("~"), ".claude", "skills")
OVERLAY = os.environ.get("ADD_SKILL_OVERLAY") or os.path.join(
    ROOT, "scripts", "skill_sources.json")
BUILDER = os.path.join(ROOT, "scripts", "build_inventory.py")
UK = os.path.join(ROOT, "scripts", "uk_descriptions.json")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def die(msg, code=1):
    print(f"ПОМИЛКА: {msg}")
    sys.exit(code)


def api(path):
    """GitHub API через gh (авторизований, без ліміту анонімних запитів)."""
    try:
        out = subprocess.run(["gh", "api", path], capture_output=True, text=True,
                             encoding="utf-8", shell=(os.name == "nt"))
    except FileNotFoundError:
        die("не знайдено gh CLI — він потрібен для читання дерева репозиторію")
    if out.returncode != 0:
        die(f"gh api {path} → {out.stderr.strip()[:300]}")
    return json.loads(out.stdout)


def parse(spec):
    """→ (owner, repo, skill|None). Приймає owner/repo@skill, шлях або URL."""
    s = spec.strip().strip("`\"' ")
    s = re.sub(r"^Skill\s+", "", s, flags=re.I)
    m = re.match(r"^https?://github\.com/([^/]+)/([^/]+)(?:/tree/[^/]+/(.+))?/?$", s)
    if m:
        owner, repo, path = m.group(1), m.group(2), m.group(3)
        path = path.rstrip("/") if path else None
        return owner, repo, (path.split("/")[-1] if path else None), path
    if "@" in s:
        left, skill = s.rsplit("@", 1)
        parts = left.strip("/").split("/")
        if len(parts) < 2:
            die(f"не розібрав «{spec}»: очікую owner/repo@skill")
        return parts[0], parts[1], skill.strip(), None
    parts = s.strip("/").split("/")
    if len(parts) == 2:
        return parts[0], parts[1], None, None
    if len(parts) > 2:
        return parts[0], parts[1], parts[-1], "/".join(parts[2:])
    die(f"не розібрав «{spec}»")


def tree(owner, repo, branch):
    data = api(f"repos/{owner}/{repo}/git/trees/{branch}?recursive=1")
    if data.get("truncated"):
        print("! дерево репозиторію обрізане API — можливі пропуски файлів")
    return [t for t in data.get("tree", []) if t.get("type") == "blob"]


def main():
    if len(sys.argv) < 2:
        die("вкажіть скіл: owner/repo@skill, шлях у репо або URL", 2)
    owner, repo, skill, want_path = parse(" ".join(sys.argv[1:]))

    meta = api(f"repos/{owner}/{repo}")
    owner, repo = meta["full_name"].split("/", 1)  # канонічний регістр
    branch = meta.get("default_branch", "main")
    blobs = tree(owner, repo, branch)
    skill_files = [b["path"] for b in blobs if b["path"].endswith("SKILL.md")]

    if skill is None:
        names = sorted({p.rsplit("/", 2)[-2] for p in skill_files if "/" in p})
        print(f"{owner}/{repo}: {len(names)} скілів")
        for n in names[:80]:
            print("  ", n)
        if len(names) > 80:
            print(f"   … і ще {len(names) - 80}")
        sys.exit(2)

    matches = [p for p in skill_files if p.rsplit("/", 2)[-2] == skill] if skill_files else []
    if want_path:
        exact = [p for p in matches if p.rsplit("/", 1)[0] == want_path.strip("/")]
        if exact:
            matches = exact
        elif matches:
            print(f"! теки {want_path} нема — беру {matches[0].rsplit('/', 1)[0]}")
    if not matches:
        die(f"у {owner}/{repo} немає теки «{skill}» зі SKILL.md")
    if len(matches) > 1:
        die(f"кілька збігів для «{skill}»: {', '.join(matches)} — вкажіть повний шлях")

    skill_dir = matches[0].rsplit("/", 1)[0]          # напр. skills/azure-devops
    prefix = skill_dir.rsplit("/", 1)[0] if "/" in skill_dir else ""  # напр. skills
    files = [b["path"] for b in blobs if b["path"].startswith(skill_dir + "/")]

    dest = os.path.join(SKILLS, skill)
    existed = os.path.isdir(dest)
    for path in files:
        rel = path[len(skill_dir) + 1:]
        target = os.path.join(dest, *rel.split("/"))
        os.makedirs(os.path.dirname(target), exist_ok=True)
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                io.open(target, "wb").write(r.read())
        except urllib.error.URLError as e:
            die(f"не завантажився {path}: {e}")
    shown = dest.replace(os.path.expanduser("~"), "~").replace("\\", "/")
    print(f"{'оновлено' if existed else 'встановлено'}: {shown} "
          f"({len(files)} файл(ів) із {owner}/{repo}/{skill_dir}@{branch})")

    # Джерело: маркетплейс визначаємо за наявністю маніфесту в репо
    is_market = any(b["path"] == ".claude-plugin/marketplace.json" for b in blobs)
    src_id = re.sub(r"[^a-z0-9]+", "-", owner.lower()).strip("-")
    builder_text = io.open(BUILDER, encoding="utf-8").read()
    inline_repo = f'"repo": "{owner}/{repo}"' in builder_text
    inline_skill = f'"{skill}": "' in builder_text

    overlay = {"sources": {}, "skills": {}}
    if os.path.exists(OVERLAY):
        overlay = json.load(io.open(OVERLAY, encoding="utf-8"))
    todo = []
    if inline_repo:
        print(f"джерело {owner}/{repo} вже описане в build_inventory.py — не чіпаю")
    elif src_id in overlay["sources"] and overlay["sources"][src_id]["repo"] != f"{owner}/{repo}":
        src_id = re.sub(r"[^a-z0-9]+", "-", f"{owner}-{repo}".lower()).strip("-")
    if not inline_repo and src_id not in overlay["sources"]:
        overlay["sources"][src_id] = {
            "title": f"{owner} — {repo}",
            "repo": f"{owner}/{repo}",
            "dir": prefix if prefix else "",
            "marketplace": is_market,
            "note": (meta.get("description") or "").strip() or f"Скіли з {owner}/{repo}.",
        }
        todo.append(f"примітка джерела «{src_id}» у scripts/skill_sources.json — "
                    f"зараз там опис репозиторію англійською, перепишіть українською"
                    + (" і згадайте, що репо є маркетплейсом (плагін ставить усі скіли одразу)"
                       if is_market else ""))
    if not inline_skill:
        target_id = src_id if not inline_repo else None
        if target_id is None:
            m = re.search(r'"([a-z0-9-]+)":\s*\{[^}]*?"repo":\s*"' + re.escape(f"{owner}/{repo}"),
                          builder_text, re.S)
            target_id = m.group(1) if m else src_id
        overlay["skills"][skill] = target_id
    blob = json.dumps(overlay, ensure_ascii=False, indent=1, sort_keys=True)
    io.open(OVERLAY, "w", encoding="utf-8", newline="\n").write(blob + "\n")

    uk = json.load(io.open(UK, encoding="utf-8")) if os.path.exists(UK) else {}
    if skill not in uk:
        todo.append(f"український опис «{skill}» у scripts/uk_descriptions.json "
                    f"(без нього на картці буде англійський опис автора)")

    print("перебудова inventory.json…")
    env = dict(os.environ, PYTHONUTF8="1")
    r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "build_inventory.py")],
                       env=env, capture_output=True, text=True, encoding="utf-8")
    print((r.stdout or r.stderr).strip())
    if r.returncode != 0:
        die("build_inventory.py впав — inventory.json не оновлено")

    if todo:
        print("\nЛишилось дописати руками:")
        for t in todo:
            print("  •", t)
    print("\nДалі: npm --prefix site run build → коміт (scripts/ + site/src/inventory.json) "
          "→ пуш → перевірка CI і живого бандла.")


if __name__ == "__main__":
    main()
