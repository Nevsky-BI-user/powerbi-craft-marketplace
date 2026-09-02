---
name: add-skill
description: Додати зовнішній скіл, який кинув користувач, і зареєструвати його для сайту — ритуал із CLAUDE.md
argument-hint: "owner/repo@skill | owner/repo/skills/name | URL теки в GitHub"
disable-model-invocation: true
allowed-tools:
  - Bash(python scripts/add_skill.py *)
  - Bash(python3 scripts/add_skill.py *)
  - Bash(python scripts/build_inventory.py)
  - Bash(python3 scripts/build_inventory.py)
  - Bash(python scripts/validate_repo.py)
  - Bash(python3 scripts/validate_repo.py)
  - Bash(npm --prefix site run build)
  - Bash(git grep *)
---

Додай скіл за посиланням, яке кинув користувач: `$ARGUMENTS`

Це ритуал «Додати скіл, який кинув користувач» із CLAUDE.md. Посилання
приймається в будь-якій формі (`owner/repo@skill`, `owner/repo/skills/name`,
URL на теку в GitHub) — далі все робиться самостійно, нічого не перепитуючи.
Форма `owner/repo` без назви скіла показує список доступних скілів і нічого
не ставить — у такому разі покажи список і зупинись.

## Скрипт

```bash
python scripts/add_skill.py $ARGUMENTS
```

Скрипт знаходить теку скіла в репозиторії, викачує **всі** її файли в
`~/.claude/skills/<скіл>/`, визначає, чи репо є маркетплейсом, реєструє джерело
в `scripts/skill_sources.json` і перебудовує `site/src/inventory.json`. Прочитай,
що він надрукував: там сказано, що дописати руками.

## Далі — те, чого скрипт не робить, бо це проза й перевірка

1. **Український опис скіла** в `scripts/uk_descriptions.json` (без нього на
   картці буде англійський опис автора). Одне речення: що робить, коли корисний.
2. **Примітка джерела** в `scripts/skill_sources.json`, якщо джерело нове —
   скрипт кладе туди англійський опис репо з GitHub. Переписати українською;
   якщо репо є маркетплейсом, але його плагін тягне десятки зайвих скілів,
   сказати це прямо і лишити `marketplace: false`, щоб на картці був промпт на
   один скіл, а не команда, що ставить усе.
3. `python scripts/build_inventory.py` ще раз (описи потрапляють у знімок).
4. `npm --prefix site run build` — має пройти без помилок tsc.

## Перевірка перед комітом

- `git grep -i` за залишками конкретики (локальні шляхи, імʼя користувача,
  назви бойових звітів) — шукати **завжди** регістронезалежно.
- `python scripts/validate_repo.py` — той самий скрипт, що й у CI (workflow
  `validate`, Ubuntu + Windows). Має надрукувати `OK`. Без `OK` не комітити.

## Коміт і публікація

5. Коміт (`site:` у першому рядку) зі `scripts/*` і `site/src/inventory.json`,
   пуш, дочекатись обох перевірок CI, перевірити живий бандл на наявність
   нової назви (сторінка кешується — тягнути з `?v=<timestamp>`).
   Багаторядкове повідомлення — через `git commit -F <файл>` (розділ Git у
   CLAUDE.md).

MCP-сервери, які часом ідуть у парі зі скілом, **не** налаштовуй сам: це зміна
конфігурації користувача. Скажи, що саме поставити, і лиши рішення йому.

Наприкінці коротко звітуй: що поставлено, що дописано в `uk_descriptions.json`
і `skill_sources.json`, результат `npm run build` і валідатора, стан CI.
