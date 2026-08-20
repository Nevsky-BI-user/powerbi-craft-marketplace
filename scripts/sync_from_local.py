# -*- coding: utf-8 -*-
"""Публікує скіли з майстер-копій ~/.claude/skills у плагіни цього репо.

Джерело правди — локальна тека: скіли правляться в роботі, а репозиторій є
знімком для інших. Скрипт показує дрейф і за командою переносить локальну
версію в репо, дорогою знеособлюючи те, що не має їхати в публічне:

    python scripts/sync_from_local.py                    # звіт про дрейф
    python scripts/sync_from_local.py --apply pbi-tables # перенести названі
    python scripts/sync_from_local.py --apply-all        # перенести всі, що розійшлись

Односторонній свідомо: зворотний напрямок (репо → локально) колись уже
затирав свіжі майстер-копії, тож переносити назад — руками й прицільно.
"""
import io
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCAL = Path.home()/".claude"/"skills"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Скіли, у яких різниця з репо навмисна і синхронізації НЕ підлягає.
KEEP_DIFFERENT = {
    # локальна копія знає справжні шляхи й репозиторій іконок, публічна — плейсхолдери
    "icon-set-manager": "локальні шляхи проти плейсхолдерів",
    # логотипи компанії лишаються лише локально (див. CLAUDE.md)
    "pbi-corporate-theme": "бренд-активи не публікуються",
}

# Знеособлення на льоту: локальна конкретика → плейсхолдер репозиторію.
SUBSTITUTIONS = [
    (r"C:\\github\\Rayfin_Operational_Monitoring", "<еталонний репозиторій>"),
    (r"C:\\github\\Финплан_app", "<інший проєкт>"),
]

# Те, що не має потрапити в репо за жодних умов (ті самі правила, що у validate_repo).
FORBIDDEN = [
    (re.compile(r"C:[\\/]+Users[\\/]+HEAVY", re.I), "локальний шлях до профілю"),
    (re.compile(r"HEAVY_METAL"), "імʼя локального користувача"),
    (re.compile(r"C:[\\/]+github[\\/]+(?!icons|<)", re.I), "локальний шлях C:\\github"),
]

SKIP_PARTS = {"__pycache__", "logos"}
TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".py", ".sh", ".css", ".ts", ".tsx"}


def files_of(d: Path):
    out = {}
    for p in sorted(d.rglob("*")):
        if p.is_file() and not (SKIP_PARTS & set(p.parts)):
            out[p.relative_to(d).as_posix()] = p
    return out


def body(p: Path) -> bytes:
    return p.read_bytes().replace(b"\r\n", b"\n")


def despecify(text: str) -> str:
    for pat, repl in SUBSTITUTIONS:
        text = re.sub(pat, repl, text)
    return text


def repo_skills():
    for p in sorted(ROOT.glob("plugins/*/skills/*")):
        if p.is_dir():
            yield p.name, p


def drift(name: str, repo_dir: Path):
    """→ (стан, деталі). Порівнюємо вміст після знеособлення: різниця, яку
    скрипт і так прибрав би, дрейфом не є."""
    loc = LOCAL/name
    if not loc.exists():
        return "нема локально", ""
    a, b = files_of(loc), files_of(repo_dir)
    changed = []
    for rel, p in a.items():
        if rel not in b:
            changed.append(f"+{rel}")
            continue
        la = despecify(body(p).decode("utf-8", "replace")) if p.suffix in TEXT_SUFFIXES else None
        if la is None:
            if body(p) != body(b[rel]):
                changed.append(f"~{rel}")
        elif la != body(b[rel]).decode("utf-8", "replace"):
            changed.append(f"~{rel}")
    changed += [f"-{rel}" for rel in b if rel not in a]
    return ("збігається", "") if not changed else ("розійшлось", ", ".join(changed[:6]))


def apply(name: str, repo_dir: Path) -> list:
    """Переносить локальну версію в репо. Повертає список проблем."""
    loc = LOCAL/name
    a, b = files_of(loc), files_of(repo_dir)
    problems = []
    for rel, p in a.items():
        target = repo_dir/rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if p.suffix in TEXT_SUFFIXES:
            text = despecify(p.read_text(encoding="utf-8", errors="replace"))
            for pat, tag in FORBIDDEN:
                if pat.search(text):
                    problems.append(f"{name}/{rel}: {tag}")
            io.open(target, "w", encoding="utf-8", newline="\n").write(text)
        else:
            shutil.copy2(p, target)
    for rel in b:
        if rel not in a:
            (repo_dir/rel).unlink()
    return problems


def main():
    args = sys.argv[1:]
    apply_all = "--apply-all" in args
    named = [a for a in args if not a.startswith("--")]
    do_apply = apply_all or "--apply" in args

    rows, dirty = [], []
    for name, repo_dir in repo_skills():
        if name in KEEP_DIFFERENT:
            rows.append((name, "навмисно різні", KEEP_DIFFERENT[name]))
            continue
        state, details = drift(name, repo_dir)
        rows.append((name, state, details))
        if state == "розійшлось":
            dirty.append((name, repo_dir))

    if not do_apply:
        for name, state, details in rows:
            if state != "збігається":
                print(f"{name:26} {state:16} {details}")
        n_ok = sum(1 for r in rows if r[1] == "збігається")
        print(f"\nзбігається {n_ok} із {len(rows)}; розійшлось {len(dirty)}")
        if dirty:
            print("перенести все: python scripts/sync_from_local.py --apply-all")
        return

    todo = dirty if apply_all else [(n, d) for n, d in dirty if n in named]
    skipped = [n for n in named if n in KEEP_DIFFERENT]
    problems = []
    for name, repo_dir in todo:
        problems += apply(name, repo_dir)
        print(f"перенесено: {name}")
    for n in skipped:
        print(f"пропущено (навмисно різні): {n}")
    if problems:
        print("\nЗАЛИШКИ КОНКРЕТИКИ — виправити руками, інакше CI не пропустить:")
        for p in problems:
            print("  •", p)
        sys.exit(1)
    if todo:
        r = subprocess.run([sys.executable, str(ROOT/"scripts"/"validate_repo.py")],
                           env=dict(os.environ, PYTHONUTF8="1"),
                           capture_output=True, text=True, encoding="utf-8")
        print((r.stdout or r.stderr).strip())
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
