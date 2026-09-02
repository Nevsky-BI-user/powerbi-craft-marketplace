---
name: pbip-bootstrap
description: Розгортає новий Power BI PBIP-репозиторій під ключ — git init, .gitignore/.gitattributes під PBIP, CLAUDE.md з правилами й гейтами, .claude/settings.json, скрипт гейтів, перший коміт, GitHub-remote за згодою; параметри проєкту питає через AskUserQuestion. Use whenever the user wants to start, scaffold or set up a new Power BI / PBIP / PBIR project or repo, or add git and working rules to an existing .pbip folder - "розгорни новий PBI-проєкт", "розгорни тут гіт репозиторій під Power BI", "створи новий звіт з нуля", "налаштуй репо для pbip", "start a new Power BI project", "set up a PBIP repo"; trigger even without the word PBIP ("розгорни репозиторій, тут буде Power BI"). Do NOT trigger for deploying an existing PBIP to Fabric (pbip-deploy), reviewing a PBIP pull request (pbip-pr-reviewer), CLAUDE.md for a non-Power-BI repo (claude-md-bootstrap), authoring pages or visuals inside the report (pbi-* skills).
---

# Розгортання нового PBIP-репозиторію

## Overview

Мета — за один прохід отримати репозиторій, у якому вже діють правила роботи,
гейти й git-налаштування під специфіку PBIP, а не «порожній git, розберемось потім».
Скіл ідемпотентний: його можна запустити повторно на тій самій теці, щоб дозаповнити
§0 після того, як користувач збереже PBIP з Desktop.

## When to Use

- Новий Power BI / PBIP-проєкт з нуля; git і правила роботи в наявну теку з `.pbip`;
  повторний запуск, щоб дозаповнити §0 CLAUDE.md з файлів.

Суміжні скіли (NOT for):

- **pbip** — структура PBIP, перейменування з каскадом, конвертація PBIX→PBIP.
- **powerbi-visuals**, **powerbi-bookmarks** — робота зі звітом після розгортання.
- **pbi-theme-json** — коли дійде до власної теми замість базової.

## Ключовий принцип: не питати те, що видно у файлах

Опитування має бути коротким. Спочатку **розвідка**, і тільки потім питання —
про те, чого у файлах немає. Питати «який у вас формат звіту?», коли поруч лежить
`report.json`, — марно витрачений хід користувача.

## Хід роботи

Порядок має значення: git спочатку, файли потім, коміт останнім.

1. **Розвідка** — стан теки до будь-яких дій і питань: git-стан, `gh auth status`,
   параметри з PBIP-файлів (формат Legacy/enhanced, канва, тема, культура); якщо
   PBIP ще немає — нормальний сценарій → reference.md §1.
2. **Опитування** — два раунди AskUserQuestion (гілка, remote, трекер, CLAUDE.md
   у git; джерела даних, RLS, інкремент) + текстове про бізнес-домен → reference.md §2.
3. **Розгортання** — `git init -b` (лише якщо ще не репозиторій), файли з `assets/`
   (таблиця нижче), підстановка плейсхолдерів → reference.md §3.
4. **Перший коміт** — `git add`, перевірка `check-ignore` до коміта, коміт-меседж,
   remote/push лише за вибором користувача → reference.md §4.
5. **Самоперевірка** — чекліст «Verify before done» нижче.

Наприкінці — короткий підсумок, що лишилось незаповненим, і три наступні кроки
користувачу → reference.md §6.

## Quick Reference — файли з `assets/`

| Шаблон | Куди | Призначення |
|---|---|---|
| `CLAUDE.md.template` | `CLAUDE.md` | правила, гейти G0–G4, довідник заборон |
| `gitignore.template` | `.gitignore` | локальний стан Desktop, секрети, ПДн |
| `gitattributes.template` | `.gitattributes` | eol, binary, `merge=ours` для згенерованих |
| `settings.json.template` | `.claude/settings.json` | allowlist read-only команд |
| `README.md.template` | `README.md` | що це, як відкрити, куди дивитись |
| `pull_request_template.md` | `.github/pull_request_template.md` | чекбокси гейтів G3/G4 |
| `../scripts/check_gates.py` | `scripts/check_gates.py` | автоперевірка гейтів (пер-типова матриця) |
| `../scripts/bpa-rules.json` | `scripts/bpa-rules.json` | правила BPA: Microsoft-набір (34) + хаус-правила (3) |
| `../scripts/check-model-refs.py` | `scripts/check-model-refs.py` | биті посилання DAX→таблиці (клас дефектів поза BPA) |

`check_gates.py` працює на Windows, macOS і Linux (python 3.9+, лише stdlib);
Windows-залежним лишається тільки крок BPA, бо Tabular Editor виходить лише під
Windows — без нього гейт показує WARN і не валить прогін. Старий
`scripts/check-gates.ps1` лишається в скілі для тих, хто вже повісив його на хук;
нові налаштування роблять на python.

`.claude/settings.json` комітиться свідомо: `.gitignore` виключає `.claude/`, але
`settings.json` — це проєктні дозволи для команди, тому в шаблоні `.gitignore`
є виняток `!.claude/settings.json`. Не прибирати його.

## Common Mistakes

| Помилка | Правильно |
|---|---|
| `git init` / перемикання гілки в наявному репозиторії | репозиторій уже є → `git init` не запускати, гілку не перемикати (reference.md §3) |
| Мовчки перезаписати наявні CLAUDE.md, `.gitignore`, settings.json | показати різницю і спитати: замінити / злити / лишити (reference.md §1) |
| Вигадати PBIP-скелет вручну | валідний PBIP надійно генерує лише Power BI Desktop; лишити `[заповнити]` (reference.md §1) |
| Вигадати значення за користувача | чесний плейсхолдер `[заповнити]` краще за правдоподібну вигадку (reference.md §2) |
| Публічний remote за замовчуванням | створення репо — публікація назовні; за замовчуванням **private** (reference.md §2) |
| Інлайн-коментар у `.gitignore` | git читає `#` лише на початку рядка; `check-ignore` до коміта (reference.md §4) |
| Прибрати `!.claude/settings.json` з `.gitignore` | виняток свідомий — не прибирати (Quick Reference вище) |
| Увімкнути блокуючий хук на коміт за замовчуванням | лише на явне прохання користувача (reference.md §7) |

## Verify before done

Скіл, який вимагає гейтів від інших, зобов'язаний пройти власний. Перед звітом
про завершення:

- [ ] `grep -c "{{" CLAUDE.md README.md` → **0** незамінених плейсхолдерів.
- [ ] `git check-ignore -v` ловить `localSettings.json` **і** `*.abf`.
- [ ] `git status --short` — чисто, локальні файли не в індексі.
- [ ] `git log -1 --stat` — у комі ті файли, що очікувались.
- [ ] Якщо створювався remote — `git status -sb` показує трекінг.
- [ ] `python scripts/check_gates.py` відпрацьовує без помилок
      (на порожньому проєкті частина перевірок пропускається — це очікувано).
- [ ] Якщо модель уже існує: BPA-гейт або пройшов, або його провал показано
      користувачу як беклог якості моделі (на легасі-моделі перший прогін
      майже напевно дасть Severity 3 — це очікувано; тюнінг: `scripts/bpa-rules.json`).

Деталі всіх фаз, опційний блокуючий хук на коміт і фінальне повідомлення
користувачу — [reference.md](reference.md).
