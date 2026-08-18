"""Валідатор фронтматтера SKILL.md для контриб'юторів цього маркетплейсу.

Ловить у момент редагування те, що рантайм губить МОВЧКИ: битий YAML
(класика — неквотована двокрапка в description). Так у v0.1.0 чотири скіли
місяцями втрачали метадані. Без PyYAML — тихий пас.
"""
import io
import re
import sys

try:
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    import yaml
except ImportError:
    sys.exit(0)

path = sys.argv[1]
try:
    text = io.open(path, encoding="utf-8").read()
except OSError:
    sys.exit(0)

m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
if not m:
    print(f"{path}: немає YAML-фронтматтера (--- ... ---)", file=sys.stderr)
    sys.exit(2)
try:
    data = yaml.safe_load(m.group(1))
except Exception as e:
    print(f"{path}: YAML битий — рантайм МОВЧКИ загубить опис. {e}\n"
          f"Найчастіша причина: двокрапка в неквотованому description — "
          f"візьміть значення в лапки.", file=sys.stderr)
    sys.exit(2)
for key in ("name", "description"):
    if not (isinstance(data, dict) and data.get(key)):
        print(f"{path}: у фронтматтері немає '{key}'", file=sys.stderr)
        sys.exit(2)
sys.exit(0)
