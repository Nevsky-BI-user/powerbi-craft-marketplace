"""Швидка перевірка PBIR-Legacy report.json після редагування.

1. Зовнішній JSON парситься.
2. Кожен вкладений config-рядок (сторінки, візуали, сам звіт) парситься.
3. Симетрія братніх букмарок у групах: однакова кількість
   options.targetVisualNames і однаковий suppressData у всіх дітей групи
   (розсинхрон = класичний баг «фільтр сусідньої вкладки програється»).

Мовчить, коли все чисто. exit 2 + повідомлення в stderr — Claude отримує
фідбек і лагодить одразу, а не на код-ревʼю.
"""
import io
import json
import sys

try:
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

path = sys.argv[1]
problems = []

try:
    raw = io.open(path, encoding="utf-8").read()
except OSError:
    sys.exit(0)

try:
    doc = json.loads(raw)
except Exception as e:
    print(f"report.json НЕ ПАРСИТЬСЯ після правки: {e}", file=sys.stderr)
    sys.exit(2)


def parse_config(holder, where):
    cfg = holder.get("config")
    if not isinstance(cfg, str):
        return cfg if isinstance(cfg, dict) else None
    try:
        return json.loads(cfg)
    except Exception as e:
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
        tvns = {s[1] for s in sigs}
        sups = {s[2] for s in sigs}
        if len(tvns) > 1:
            det = ", ".join(f"{n}={c}" for n, c, _ in sigs)
            problems.append(
                f"група букмарок «{gname}»: різна кількість targetVisualNames ({det}) — "
                f"сусідня вкладка програватиме чужий стан")
        if len(sups) > 1:
            det = ", ".join(f"{n}={s}" for n, _, s in sigs)
            problems.append(
                f"група букмарок «{gname}»: suppressData не однаковий ({det}) — "
                f"клік по вкладці скидатиме фільтри читача")

if problems:
    print("Перевірка report.json (hook pbi-report-ux):", file=sys.stderr)
    for p in problems:
        print(" - " + p, file=sys.stderr)
    sys.exit(2)
sys.exit(0)
