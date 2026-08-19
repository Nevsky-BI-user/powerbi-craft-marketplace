#!/usr/bin/env python3
"""Автоматична частина гейтів G1/G3 для PBIP-репозиторію — пер-типова матриця.

Визначає з git, які типи файлів змінено, і жене лише релевантні гейти:

  завжди          гілка, заборонені файли в індексі, .gitignore
  модель (*.tmdl) TMDL-коментарі + BPA (Tabular Editor 2, scripts/bpa-rules.json)
  звіт (*.Report) валідність JSON, roundtrip і геометрія через pbir.py,
                  нагадування про діагностику закладок при їх зміні
  тема            валідність JSON + нагадування про повне перевідкриття Desktop
  лише docs       важкі перевірки пропускаються (про це сказано явно)

Чисте дерево = повний аудит (усі гейти).
Кожен пропуск гейта — гучний (WARN з причиною), ніколи мовчазний.

Вихідний код: 1 — є провалені перевірки, 0 — ні. Попередження код не змінюють.
Код 2 — тека не є git-репозиторієм.

Кросплатформений порт scripts/check-gates.ps1 (python 3.9+, лише stdlib).
Єдиний крок, що лишається Windows-залежним, — BPA через Tabular Editor 2:
TE2 існує тільки під Windows. Не знайдено → WARN, код виходу не змінюється.

Використання:
    python scripts/check_gates.py [--repo-root <шлях>] [--quiet] [--skip-bpa]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# PowerShell -match / -eq регістронечутливі — усі перенесені регекси теж.
IC = re.IGNORECASE

RE_MODEL = (re.compile(r"\.tmdl$", IC), re.compile(r"\.SemanticModel/", IC))
RE_REPORT = (re.compile(r"\.Report/", IC), re.compile(r"report\.json$", IC),
             re.compile(r"\.pbir$", IC))
RE_THEME = re.compile(r"\.Report/StaticResources/.*\.json$", IC)
RE_DOCS = re.compile(r"\.(md|txt)$", IC)
RE_FORBIDDEN = (re.compile(r"\.pbi/localSettings\.json$", IC), re.compile(r"\.abf$", IC),
                re.compile(r"\.pbix$", IC), re.compile(r"\.pbit$", IC))
RE_INTEGRATION = re.compile(r"^\|\s*Інтеграційна гілка\s*\|\s*`([^`]+)`", re.M | IC)
RE_INLINE_COMMENT = re.compile(r"\s#")
RE_BPA_LOAD_ERROR = re.compile(r"Error loading file|File not found", IC)
RE_BPA_SEV3 = re.compile(r"^::error::", IC)
RE_BPA_SEV2 = re.compile(r"^::warning::", IC)
RE_BPA_SEV3_PREFIX = re.compile(r"^::error::\s*", IC)
RE_ROUNDTRIP = re.compile(r"roundtrip:\s*(\w+)", IC)
RE_GEOMETRY = re.compile(r"geometry mismatches[^:]*:\s*(\d+)", IC)
RE_REFS_LINE = re.compile(r":\d+")

FAILURES: list[str] = []
WARNINGS: list[str] = []
PASSES: list[str] = []


def add_fail(m: str) -> None:
    FAILURES.append(m)


def add_warn(m: str) -> None:
    WARNINGS.append(m)


def add_pass(m: str) -> None:
    PASSES.append(m)


# ── Дрібні кросплатформені помічники ────────────────────────────────────────

def git(repo_root: Path, *args: str, quotepath: bool = False) -> tuple[int, list[str]]:
    """git -C <root> [-c core.quotepath=false] <args>. Повертає (код, рядки stdout).

    core.quotepath=false ОБОВ'ЯЗКОВО для переліків файлів: інакше git огортає
    кириличні шляхи в лапки з вісімковим екрануванням ("\\320\\227...json"),
    і всі кінець-заякорені регекси ($ на розширенні) мовчки перестають матчитись.
    """
    cmd = ["git", "-C", str(repo_root)]
    if quotepath:
        cmd += ["-c", "core.quotepath=false"]
    cmd += list(args)
    try:
        proc = subprocess.run(cmd, capture_output=True)
    except OSError:
        return 127, []
    text = proc.stdout.decode("utf-8", errors="replace")
    lines = [ln.rstrip("\r") for ln in text.split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return proc.returncode, lines


def read_text(path: Path) -> str:
    """Читання з явним utf-8 (BOM зʼїдається): у PBIP багато кирилиці."""
    return path.read_text(encoding="utf-8-sig", errors="replace")


def json_valid(path: Path) -> bool:
    try:
        with open(path, encoding="utf-8-sig") as fh:
            json.load(fh)
        return True
    except (OSError, ValueError):
        return False


def dirs_with_suffix(root: Path, suffix: str) -> list[Path]:
    """Теки першого рівня з заданим суфіксом (регістронечутливо, як -Filter)."""
    try:
        entries = [p for p in root.iterdir()
                   if p.is_dir() and p.name.lower().endswith(suffix.lower())]
    except OSError:
        return []
    return sorted(entries, key=lambda p: p.name.lower())


def is_hidden_dir(path: Path) -> bool:
    """Прихована тека — як її бачить Get-ChildItem без -Force.

    На Windows — атрибут FILE_ATTRIBUTE_HIDDEN (git ставить його на .git).
    На інших ОС атрибута немає, тож ловимо '.git' за іменем — щоб обхід не
    заходив у службову теку git там теж.
    """
    if path.name == ".git":
        return True
    try:
        attrs = path.stat().st_file_attributes  # лише Windows
    except (AttributeError, OSError):
        return False
    return bool(attrs & 2)  # FILE_ATTRIBUTE_HIDDEN


def walk_files(root: Path):
    """Рекурсивний обхід файлів у детермінованому порядку, без прихованих тек."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted((d for d in dirnames
                              if not is_hidden_dir(Path(dirpath) / d)), key=str.lower)
        for name in sorted(filenames, key=str.lower):
            yield Path(dirpath) / name


def bookmarks_state(repo_root: Path, rel: str, report_json: Path) -> str:
    """CHANGED / SAME / UNKNOWN — масив bookmarks у report.json проти HEAD.

    Грепати сирий дифф не можна: у Legacy report.json увесь config — один рядок
    ~1.8 млн символів, де зміна самого лише activeSectionIndex (перезаписується
    майже кожним Desktop-save) переписує ту саму лінію, що містить "bookmarks".
    Тому порівнюємо КОНКРЕТНО масив bookmarks.
    """
    def bookmarks(txt: str) -> str:
        cfg = json.loads(json.loads(txt)["config"])
        return json.dumps(cfg.get("bookmarks"), sort_keys=True, ensure_ascii=False)

    try:
        proc = subprocess.run(["git", "-C", str(repo_root), "show", "HEAD:" + rel],
                              capture_output=True, check=True)
        old_raw = proc.stdout.decode("utf-8-sig", errors="replace")
        with open(report_json, encoding="utf-8-sig") as fh:
            new_raw = fh.read()
        return "CHANGED" if bookmarks(old_raw) != bookmarks(new_raw) else "SAME"
    except Exception:
        return "UNKNOWN"


# ── Основний прогін ─────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="check_gates.py",
        description="Автоматична частина гейтів G1/G3 для PBIP-репозиторію.")
    parser.add_argument("--repo-root", default=None,
                        help="Корінь репозиторію. За замовчуванням — поточна тека.")
    parser.add_argument("--quiet", action="store_true",
                        help="Показувати лише проблеми, без списку успішних перевірок.")
    parser.add_argument("--skip-bpa", action="store_true",
                        help="Пропустити BPA-гейт (пропуск усе одно показаний як WARN).")
    args = parser.parse_args()

    repo_root = Path(args.repo_root) if args.repo_root else Path.cwd()

    # ── 0. Чи це взагалі репозиторій ────────────────────────────────────────
    code, _ = git(repo_root, "rev-parse", "--is-inside-work-tree")
    if code != 0:
        print(f"check-gates: '{repo_root}' не є git-репозиторієм.")
        return 2

    commit_count = 0
    code, cc = git(repo_root, "rev-list", "--count", "HEAD")
    if code == 0 and cc:
        try:
            commit_count = int(cc[0].strip())
        except ValueError:
            commit_count = 0

    # ── 0.1 Що змінено → які типи задач зачеплені ──────────────────────────
    # Об'єднання: незакомічені зміни проти HEAD + нові (untracked) файли.
    changed: list[str] = []
    code, diff_names = git(repo_root, "diff", "--name-only", "HEAD", quotepath=True)
    if code == 0 and diff_names:
        changed += diff_names
    code, untracked = git(repo_root, "ls-files", "--others", "--exclude-standard",
                          quotepath=True)
    if code == 0 and untracked:
        changed += untracked
    changed = list(dict.fromkeys(p for p in changed if p))

    full_audit = len(changed) == 0

    model_touched = any(r.search(p) for p in changed for r in RE_MODEL)
    report_touched = any(r.search(p) for p in changed for r in RE_REPORT)
    theme_touched = any(RE_THEME.search(p) for p in changed)
    docs_only = False
    if not full_audit:
        non_docs = [p for p in changed if not RE_DOCS.search(p)]
        docs_only = len(non_docs) == 0

    if full_audit:
        add_pass("Дерево чисте — повний аудит (усі гейти).")
        model_touched = report_touched = theme_touched = True
    elif docs_only:
        add_pass(f"Змінено лише документацію ({len(changed)} файл(ів)) — "
                 "гейти моделі/звіту не застосовні.")
    else:
        kinds = []
        if model_touched:
            kinds.append("модель")
        if report_touched:
            kinds.append("звіт")
        if theme_touched:
            kinds.append("тема")
        if not kinds:
            kinds.append("інфраструктура")
        add_pass(f"Змінено файлів: {len(changed)}; типи задач: {', '.join(kinds)}.")

    # ── 1. ЗАВЖДИ: гілка не інтеграційна ────────────────────────────────────
    # Назву інтеграційної гілки беремо з таблиці §0 у CLAUDE.md, щоб скрипт не
    # треба було правити під кожен проєкт.
    integration = "main"
    claude_path = repo_root / "CLAUDE.md"
    if claude_path.is_file():
        m = RE_INTEGRATION.search(read_text(claude_path))
        if m:
            integration = m.group(1).strip()

    _, branch_lines = git(repo_root, "branch", "--show-current")
    branch = branch_lines[0].strip() if branch_lines else ""
    if not branch.strip():
        add_warn("Гілку визначити не вдалось (detached HEAD?).")
    elif branch == integration or branch == "prod":
        if commit_count <= 1:
            add_warn(f"Гілка '{branch}' — інтеграційна, але репозиторій ще на "
                     f"bootstrap ({commit_count} коміт). Далі — фіча-гілка.")
        else:
            add_fail(f"Гілка '{branch}' — інтеграційна. "
                     "Відгалузитись: git checkout -b feature/<опис>")
    else:
        add_pass(f"Гілка '{branch}' — не інтеграційна.")

    # ── 2. ЗАВЖДИ: заборонені файли під версійним контролем ────────────────
    _, tracked = git(repo_root, "ls-files", quotepath=True)
    forbidden = [p for p in tracked if any(r.search(p) for r in RE_FORBIDDEN)]
    if forbidden:
        add_fail("Локальні/бінарні файли потрапили під git: " + ", ".join(forbidden))
    else:
        add_pass("Локальний стан Desktop і бінарні артефакти не відстежуються.")

    # ── 3. ЗАВЖДИ: .gitignore без інлайн-коментарів ────────────────────────
    # git читає '#' лише на початку рядка; в інших позиціях він стає частиною
    # патерну, і правило мовчки перестає діяти.
    gi_path = repo_root / ".gitignore"
    if gi_path.is_file():
        bad_lines = []
        for line_no, line in enumerate(read_text(gi_path).splitlines(), start=1):
            t = line.strip()
            if not t or t.startswith("#"):
                continue
            if RE_INLINE_COMMENT.search(t):
                bad_lines.append(f"рядок {line_no}: {t}")
        if bad_lines:
            add_fail(".gitignore має інлайн-коментарі — правила не діють: "
                     + "; ".join(bad_lines))
        else:
            add_pass(".gitignore без інлайн-коментарів.")
    else:
        add_warn(".gitignore відсутній.")

    # ── 4. ЗВІТ: валідність JSON ────────────────────────────────────────────
    # Валідація в процесі через json — без ліміту ~2 МБ, який мав
    # ConvertFrom-Json у PowerShell 5.1, і без зовнішнього виклику python.
    report_dirs = dirs_with_suffix(repo_root, ".Report")
    if report_touched and len(report_dirs) > 1:
        add_warn("У репозиторії кілька тек *.Report — перевірки звіту підуть "
                 f"лише по першій: {report_dirs[0].name}")
    report_json = None
    if report_dirs:
        candidate = report_dirs[0] / "report.json"
        if candidate.is_file():
            report_json = candidate

    if not report_touched:
        add_pass("Звіт не змінювався — гейти звіту (JSON, roundtrip, геометрія) "
                 "не застосовні.")
    elif not report_dirs:
        add_warn("Теки *.Report немає — перевірки звіту пропущено "
                 "(проєкт ще не збережено з Desktop?).")
    else:
        json_files = [f for f in walk_files(report_dirs[0])
                      if f.suffix.lower() in (".json", ".pbir")
                      and ".pbi" not in [part.lower() for part in f.parent.parts]]
        bad_json = [f.name for f in json_files if not json_valid(f)]
        if bad_json:
            add_fail("Невалідний JSON: " + ", ".join(bad_json))
        else:
            add_pass(f"JSON валідний ({len(json_files)} файлів).")

    # ── 5. МОДЕЛЬ: блокові коментарі TMDL ──────────────────────────────────
    # TMDL не приймає /* */ — Desktop відмовляється відкрити проєкт. Але всередині
    # партицій живе M-код, де /* */ легальні, тому це попередження, а не провал:
    # перевірити треба очима, чи знахідка поза partition-блоком.
    if model_touched:
        tmdl_files = [f for f in walk_files(repo_root) if f.suffix.lower() == ".tmdl"]
        if tmdl_files:
            with_block_comment = [f for f in tmdl_files if "/*" in read_text(f)]
            if with_block_comment:
                add_warn("Знайдено '/*' у TMDL — легально лише всередині "
                         "M-партицій, перевірити: "
                         + ", ".join(f.name for f in with_block_comment))
            else:
                add_pass(f"TMDL без блокових коментарів ({len(tmdl_files)} файлів).")

    # ── 6. МОДЕЛЬ: BPA через Tabular Editor 2 ──────────────────────────────
    # Правила: спершу scripts/bpa-rules.json репозиторію (проєктний тюнінг),
    # інакше глобальний %LocalAppData%\TabularEditor\BPARules.json.
    # Exit code TE2: 1 лише при порушеннях Severity >= 3 (або фатальній помилці);
    # -G дає розмітку ::error:: (Sev3) / ::warning:: (Sev2) для підрахунку.
    # WINDOWS-ONLY: Tabular Editor 2 існує лише під Windows. На інших ОС
    # виконуваного файлу просто не буде → WARN, код виходу не змінюється.
    if not model_touched:
        add_pass("Модель не змінювалась — BPA не застосовний.")
    elif args.skip_bpa:
        add_warn("BPA пропущено на вимогу (--skip-bpa).")
    else:
        te_env = os.environ.get("TE_PATH")
        te = Path(te_env) if te_env and Path(te_env).exists() else \
            Path(r"C:\Program Files (x86)\Tabular Editor\TabularEditor.exe")
        if not te.exists():
            te = Path(r"C:\Program Files\Tabular Editor\TabularEditor.exe")

        rules = repo_root / "scripts" / "bpa-rules.json"
        if not rules.exists():
            local_app = os.environ.get("LOCALAPPDATA")
            rules = Path(local_app) / "TabularEditor" / "BPARules.json" if local_app \
                else repo_root / "scripts" / "bpa-rules.json"

        model_dirs = dirs_with_suffix(repo_root, ".SemanticModel")
        if len(model_dirs) > 1:
            add_warn("У репозиторії кілька тек *.SemanticModel — BPA піде лише "
                     f"по першій: {model_dirs[0].name}")
        model_def = None
        if model_dirs:
            candidate = model_dirs[0] / "definition"
            if (candidate / "database.tmdl").is_file():
                model_def = candidate
            elif (model_dirs[0] / "model.bim").is_file():
                model_def = model_dirs[0] / "model.bim"

        # Зіпсований rules-файл TE2 мовчки трактує як «0 правил» і повертає exit 0 —
        # зелений гейт при непрацюючих правилах. Тому JSON правил валідуємо самі.
        rules_valid = True
        if rules.exists():
            rules_valid = json_valid(rules)

        if not te.exists():
            add_warn("BPA пропущено: TabularEditor.exe не знайдено "
                     "(встанови Tabular Editor 2 або задай змінну TE_PATH).")
        elif not rules.exists():
            add_warn("BPA пропущено: файл правил не знайдено (очікується "
                     "scripts/bpa-rules.json або "
                     "%LocalAppData%\\TabularEditor\\BPARules.json).")
        elif not rules_valid:
            add_fail(f"BPA: файл правил '{rules}' — невалідний JSON. TE2 мовчки "
                     "проігнорує його і дасть хибно-зелений результат; "
                     "полагодити файл до коміта.")
        elif not model_def:
            add_warn("BPA пропущено: теки *.SemanticModel\\definition "
                     "(чи model.bim) немає — модель ще не збережена з Desktop?")
        else:
            bpa_out = Path(tempfile.gettempdir()) / "check-gates-bpa.txt"
            # subprocess.run чекає завершення процесу навіть для WinForms-застосунку,
            # тому обхід через `cmd /c ... >` з PowerShell-версії не потрібен.
            try:
                with open(bpa_out, "wb") as fh:
                    bpa_exit = subprocess.run(
                        [str(te), str(model_def), "-A", str(rules), "-G"],
                        stdout=fh, stderr=subprocess.STDOUT).returncode
            except OSError as exc:
                bpa_exit = -1
                bpa_out.write_text(f"TE2 launch failed: {exc}\n", encoding="utf-8")
            bpa_lines = read_text(bpa_out).splitlines() if bpa_out.exists() else []

            load_error = any(RE_BPA_LOAD_ERROR.search(ln) for ln in bpa_lines)
            sev3 = [ln for ln in bpa_lines if RE_BPA_SEV3.search(ln)]
            sev2 = [ln for ln in bpa_lines if RE_BPA_SEV2.search(ln)]

            if load_error:
                add_fail(f"BPA: TE2 не зміг завантажити модель '{model_def}' — "
                         f"див. {bpa_out}")
            elif bpa_exit != 0 and not sev3:
                add_fail(f"BPA: TE2 завершився з кодом {bpa_exit} без розпізнаних "
                         f"анотацій порушень — ймовірно збій самого TE2, див. {bpa_out}")
            elif bpa_exit != 0:
                top = "; ".join(RE_BPA_SEV3_PREFIX.sub("", ln) for ln in sev3[:5])
                add_fail(f"BPA: {len(sev3)} порушень Severity 3 (блокують коміт). "
                         f"Перші: {top} | Повний лог: {bpa_out}")
            else:
                if sev2:
                    add_warn(f"BPA: Severity 3 — чисто; попереджень Severity 2: "
                             f"{len(sev2)} (див. {bpa_out}).")
                else:
                    add_pass("BPA: жодного порушення Severity 2–3.")

    # ── 6.1 МОДЕЛЬ: биті посилання на таблиці в DAX ────────────────────────
    # Клас дефектів, який пропускають і BPA, і JSON-валідність: міра посилається
    # на таблицю, якої немає в моделі (реальні прецеденти: 'Автотести витрати',
    # 'AccessControl'). TOM це терпить, візуал падає лише в рантаймі.
    if model_touched:
        refs_script = Path(__file__).resolve().parent / "check-model-refs.py"
        model_dirs2 = dirs_with_suffix(repo_root, ".SemanticModel")
        if refs_script.is_file() and model_dirs2:
            def_dir = model_dirs2[0] / "definition"
            if (def_dir / "tables").is_dir():
                proc = subprocess.run([sys.executable, str(refs_script), str(def_dir)],
                                      capture_output=True)
                refs_out = proc.stdout.decode("utf-8", errors="replace").splitlines()
                refs_exit = proc.returncode
                if refs_exit == 0:
                    add_pass("Посилання DAX→таблиці: усі квотовані посилання валідні.")
                elif refs_exit == 1:
                    lines = [ln for ln in refs_out if RE_REFS_LINE.search(ln)][:5]
                    add_fail("Биті посилання на неіснуючі таблиці в DAX: "
                             + "; ".join(lines))
                else:
                    add_warn("check-model-refs.py не зміг проаналізувати модель "
                             f"(код {refs_exit}).")
        elif not refs_script.is_file():
            add_warn("check-model-refs.py не знайдено поруч зі скриптом гейтів — "
                     "перевірку посилань пропущено.")

    # ── 7. ЗВІТ: pbir.py — roundtrip і геометрія (лише PBIR-Legacy) ────────
    pbir = Path.home() / ".claude" / "skills" / "powerbi-bookmarks" / "pbir.py"
    if not report_touched:
        # Гейт уже позначений «не застосовний» у секції 4 — тут мовчимо,
        # щоб не дублювати.
        pass
    elif report_json and pbir.is_file():
        proc = subprocess.run([sys.executable, str(pbir), str(report_json)],
                              stdout=subprocess.PIPE)
        text = proc.stdout.decode("utf-8", errors="replace")

        rt = RE_ROUNDTRIP.search(text)
        if rt and rt.group(1).lower() == "true":
            add_pass("report.json: byte-identical roundtrip.")
        else:
            add_fail("report.json: roundtrip не byte-identical — правки зроблені "
                     "не через pbir.py.")

        gm = RE_GEOMETRY.search(text)
        if gm:
            if int(gm.group(1)) == 0:
                add_pass("Геометрія: дзеркало і layouts[0].position збігаються.")
            else:
                add_fail(f"Геометрія: {gm.group(1)} розбіжностей між vc['x'] і "
                         "config.layouts[0].position — Desktop рендерить з config.")
    elif report_json and not pbir.is_file():
        add_warn("pbir.py не знайдено — перевірку roundtrip і геометрії пропущено.")
    elif report_dirs and not report_json:
        # Пропуск має бути гучним: інакше кількість пройдених перевірок мовчки падає,
        # і це читається як «усе гаразд», хоча дві перевірки просто не виконались.
        add_pass("PBIR enhanced (немає report.json) — roundtrip і подвійна "
                 "геометрія не застосовні; позиція живе в visual.json у єдиному "
                 "екземплярі.")

    # ── 8. ЗВІТ: закладки зачеплені → нагадування про діагностику ──────────
    if report_touched and report_json and not full_audit:
        # git-pathspec приймаємо лише з прямими слешами: зворотні на Windows git
        # трактує як екранування, і 'git show' мовчки не знаходить файл.
        report_rel = os.path.relpath(report_json, repo_root).replace(os.sep, "/")
        bm_result = bookmarks_state(repo_root, report_rel, report_json)
        if bm_result == "CHANGED":
            add_warn("Масив bookmarks у report.json змінився проти HEAD — прогнати "
                     "діагностику powerbi-bookmarks по всіх зачеплених id "
                     "(симетрія сестринських закладок, скоуп targetVisualNames, G1).")
        elif bm_result == "UNKNOWN":
            add_warn("Не вдалося порівняти закладки report.json (HEAD vs робоча "
                     "копія — новий файл або нечитабельний config) — якщо правили "
                     "закладки/видимість, діагностика powerbi-bookmarks вручну.")

    # ── 9. ТЕМА: повне перевідкриття Desktop ───────────────────────────────
    if theme_touched and not full_audit:
        add_warn("Змінено файли теми (StaticResources) — зміна теми потребує "
                 "ПОВНОГО перевідкриття Desktop; bridge-reload її не підхопить.")

    # ── Підсумок ────────────────────────────────────────────────────────────
    print("")
    if not args.quiet:
        for p in PASSES:
            print(f"  OK   {p}")
    for w in WARNINGS:
        print(f"  WARN {w}")
    for f in FAILURES:
        print(f"  FAIL {f}")

    print("")
    print(f"Гейти: {len(PASSES)} пройдено, {len(WARNINGS)} попереджень, "
          f"{len(FAILURES)} провалено.")

    return 1 if FAILURES else 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    sys.exit(main())
