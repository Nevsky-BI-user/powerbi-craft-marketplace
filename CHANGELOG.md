# Changelog

## 0.1.19 — 2026-08-27

- Новий скіл plain-report у плагіні agent-craft: правила простої української
  для звітів та інструкцій. Десять правил, кожне можна перевірити: одна думка
  на речення, активний стан, без мішанини мов в одному реченні, числа з базою
  порівняння, заголовки-висновки, головне — спочатку. У довідниках — словник
  замін для кальок (тригеритись, дрейф, канон, скоуп тощо) зі списком слів
  замовника, які не замінюються. Окремо — вижимка ділового стилю: The
  Economist Style Guide, піраміда Мінто, наративні мемо Amazon, настанови ONS
  щодо подання чисел, Google style guide для покрокових інструкцій.
- Виконавці exec-haiku, exec-sonnet, exec-opus і перевіряльник verify-skeptic
  тепер пишуть звіти за цими правилами — формат звіту кожного агента отримав
  окремий пункт про мову.
- Версії: agent-craft 0.2.0.

## 0.1.18 — 2026-08-25

- Новий плагін agent-craft: оркестрація моделей як скіл. model-orchestration
  переїхав з локальної машини в canonical — формула «рівень моделі = ціна
  помилки × неоднозначність, не розмір», п'ять умов «за» і чотири контрумови
  застосування, мапа задач Power BI-стеку на рівні haiku/sonnet/opus,
  шаблон брифу з шести обов'язкових полів (з механічним критерієм приймання),
  правила верифікації (механіка перша; автор не перевіряє себе; верифікатор
  не дешевший за автора) і п'ять готових рецептів — від релізу скіла до
  аудиту екосистеми.
- Чотири агенти при ньому: exec-haiku, exec-sonnet, exec-opus — виконавці з
  дисципліною брифу (зупиняються на неоднозначності, самі запускають критерій
  приймання, чесно звітують пропущене) — і verify-skeptic, незалежний
  адверсарійний перевіряльник для перед-публікаційних перевірок, який шукає
  тихі режими відмови і повертає знахідки з дослівними фіксами.
- validate_repo.py тепер перевіряє і фронтматтер агентів (plugins/*/agents/*.md)
  — той самий клас мовчазної відмови, що й у скілів: двокрапка в description
  ламає YAML, агент не завантажується, а CI досі був сліпий до цього. Знайдено
  адверсарійною перевіркою цього ж релізу — verify-skeptic зловив битий YAML
  у власному описі verify-skeptic.md до публікації.
- Версії: agent-craft 0.1.0.

## 0.1.17 — 2026-08-25

- Велика ревізія маршрутизації обчислювальних скілів після аудиту тригерингу
  на корпусі з 38 живих промптів. Описи шести скілів переписані за деревом
  «5 питань» з ексклюзивним володінням: вісь «комірка vs канва» стоїть першим
  реченням у dax-svg і deneb-vegalite (голе «намалюй» більше не перетягує
  Deneb-запити в SVG), dax-measures віддав «optimize» і отримав межі за
  наміром («спарклайн в таблиці» замість слова SVG, якого користувач не
  друкує), pbip-pr-reviewer скоуплений на наявність PBIP-артефактів і не
  стріляє в звичайних код-репозиторіях, icon-set-manager забрав «намалюй
  іконку» і скинув конфіг-деталі з опису в reference.
- Новий скіл dax-optimization — єдиний власник DAX-performance. Метод
  «спершу виміряй»: Performance Analyzer → server timings → клас вузького
  місця → переписування → повторний замір; довідник по FE/SE,
  CallbackDataID і патернах переписування з чесним звітуванням ефекту.
- Новий скіл dax-grill — допит постановки перед написанням міри (грануляція,
  filter context, зв'язки, очікувані totals, приклад приймання), за
  grilling-патерном Метта Покока; сам DAX не пише, передає в dax-measures.
- dax-svg нарешті отримав references/recipes.md, який reference.md §9 обіцяв
  від початку: десять повних copy-paste мір (бар, кільце, bullet, спарклайн,
  радар, бейдж, вафля, льодяник, heatmap-комірка, гаус) з правильним
  ланцюгом ескейпінгу і en-US FORMAT на кожній координаті.
- Версії: dax-craft 0.2.0, pbi-report-ux 0.1.7, pbi-design-language 0.1.4,
  pbip-devops 0.1.3.

## 0.1.16 — 2026-08-24

- ado-wi-new більше не наполягає, що елемент має існувати до роботи. На
  практиці оформлення посеред роботи збиває з думки, і команда відсунула
  його на окремий вечірній прохід. Скіл тепер байдужий до моменту: важать
  повні поля, відсутність дублікатів і години, пораховані за слідом, а не
  написані приблизно.
- Версії: azure-ops 0.2.5.

## 0.1.15 — 2026-08-21

- Порядок став явним: робочий елемент заводиться ДО роботи — до першого
  рядка коду, до тестів, до виправлення бага, — а не оформлюється заднім
  числом, коли години вже вигадуються, а причина забута. Гілка йде від
  номера наявного елемента, PR кріпиться до нього ж.
- ado-wi-close додав крок перед верифікацією: якщо робота змінила продукт,
  опис поточного стану має це відображати. Змін не було — так і сказати,
  документацію не чіпати.
- Версії: azure-ops 0.2.4.

## 0.1.14 — 2026-08-21

- ado-hygiene-inspection після першого живого прогону: перевірка порожніх
  годин застосовується лише до задач і багів, бо час обліковується на них,
  а порожнє поле в історії чи фічі — норма (інакше прогін давав девʼять
  хибних порушень). Коли сторінка конвенцій є, але порога для конкретної
  перевірки в ній немає, скіл бере дефолт із позначкою і окремим рядком
  пропонує внести поріг або прибрати перевірку.
- Версії: azure-ops 0.2.3.

## 0.1.13 — 2026-08-20

- ado-pr-flow: відсутність політик на цільовій гілці за замовчуванням і далі
  зупиняє злиття, але тепер має один явний виняток. Якщо конвенції проєкту
  прямо записали, що політик немає свідомо і злиття робляться без ревʼю,
  згода вважається даною і скіл не перепитує щоразу. Мовчання конвенцій
  винятку не утворює.
- Версії: azure-ops 0.2.2.

## 0.1.12 — 2026-08-20

- Скіли устрою Azure DevOps навчились двох правил, яких бракувало на
  практиці. Перше: працювати лише з проєктами поточного користувача —
  обліковку агент бере з сервера, а не з тексту розмови, і в чужі проєкти
  не заходить навіть маючи права. Друге: не лишати порожніх полів —
  виконавець, тип активності, дати початку й завершення та оцінка
  проставляються при створенні, а не доукомплектовуються руками.
- Версії: azure-ops 0.2.1.

## 0.1.11 — 2026-08-20

- Чотири нові скіли устрою Azure DevOps у плагіні azure-ops — універсальні,
  правила проєкту читають з вікі-сторінки «Конвенції» під час виконання:
  ado-wi-new (робочі елементи за конвенціями: теги зі словника, батько,
  поточний спринт), ado-wi-close (ритуал «закрив — залогуй»: години,
  підсумок, і лише потім стан), ado-pr-flow (PR від валідації імені гілки
  до злиття за класом гілки; без політик на target не мержить без явної
  згоди), ado-hygiene-inspection (read-only інспекція гігієни: хвости,
  PR без звʼязки, теги поза словником, застарілі документи).
- Версії: azure-ops 0.2.0.

## 0.1.10 — 2026-08-20

- Скіли тепер публікуються з майстер-копій одним скриптом
  (`scripts/sync_from_local.py`): він показує дрейф, переносить локальну
  версію в репо і дорогою знеособлює локальні шляхи, а на залишках
  конкретики зупиняється, не доводячи до CI.
- Довʼїхали правки, що жили лише в майстер-копіях: `rayfin-bootstrap` —
  розділ про обовʼязковий `docs/architecture.md` з переліком того, що в
  ньому має бути, і команди огляду живого бекенду; `react-ux-mechanics` —
  три граблі друку в PDF (повторена шапка таблиці не малює вміст
  форм-контролів, перевірка фіксу лише на живій сторінці, суцільне
  `break-inside: avoid` роздуває документ).
- Версії: project-bootstrap 0.1.5.

## 0.1.9 — 2026-08-19

- Took the project specifics out of the skills. Every skill was written against
  one production report and carried its internal name (42 mentions across 19
  files) plus internal task codes. The measurements stay — they are what makes
  the guidance credible — but they are now attributed to "a production report"
  / "an audited report" instead of a named one.
- Fixed 27 dead references. Skills pointed at internal research documents that
  are not part of the package, so anyone installing the plugin followed a link
  to nothing. The source is now named in prose, and the design-tokens document
  resolves to the shipped `pbi-design-system` skill.
- Versions: dax-craft 0.1.2, pbi-design-language 0.1.3,
  pbi-quality 0.1.2, pbi-report-ux 0.1.6,
  pbi-visuals 0.1.3.

## 0.1.8 — 2026-08-19

- Removed all brand assets from the repository: the 26 logo files (13 PNG,
  13 SVG) that shipped with the theme skill are gone. The skill keeps the
  registration mechanics and now expects you to drop your own
  `logo_full_light.png` / `logo_full_dark.png` / `logo_icon_*.png` into
  `assets/logos/`; missing files are skipped instead of crashing the script.
- Renamed two skills to neutral names: the theme skill is now
  `pbi-corporate-theme` (pbi-design-language 0.1.2) and the data-entry
  blueprint is now `kpi-data-entry-app` (project-bootstrap 0.1.3). Theme
  files and the `name` inside them follow: `corporate-classic.json`,
  "Corporate Classic". The palettes themselves are unchanged. If you
  installed 0.1.7, reinstall the two plugins to pick up the new folders.
- Second pass over every remaining brand string, this time case-insensitively:
  a Tailwind theme comment in `HoverTip.tsx`, a colour fallback comment in
  `animations.css`, a scenario-mapping heading in `data-storytelling`, and the
  name of the source report in `pbi-filter-panel-bookmark`. All now generic
  (pbi-report-ux 0.1.5, report-storytelling 0.1.3, project-bootstrap 0.1.4).
- Rationale: an MIT-licensed public repository represents that the author may
  license everything in it under those terms (GitHub ToS D.6), and no one can
  grant that over someone else's trademark. Shipping the mechanics without the
  marks removes the representation without losing the skill.

## 0.1.7 — 2026-08-19

- Verified the gate checker on real Linux (Ubuntu 24.04, WSL2, python 3.12), not
  just by reading the code: same output and same exit code as Windows on the same
  PBIP repo.
- Fix found by that run: `pbir.py` (powerbi-bookmarks 0.1.4 / powerbi-visuals
  0.1.2) assumed CRLF line endings, so `verify_roundtrip` reported a false
  mismatch on any LF checkout and the report gate failed with "edits were not made
  through pbir.py". It now reads the convention from the file and preserves it.
  Windows output is byte-identical to before.
- `check_gates.py`: the BPA warning no longer tells non-Windows users to set
  `$env:TE_PATH`.
- Site: the requirements note now states what was actually run where.

## 0.1.6 — 2026-08-19

- `pbip-bootstrap` (pbip-devops → 0.1.2): gate checker ported from PowerShell to
  python (`scripts/check_gates.py`, stdlib only, python 3.9+), so gates run on
  macOS and Linux too. Output was compared line by line with the PowerShell
  version on a live PBIP repo; exit codes match. Only the BPA step stays
  Windows-bound (Tabular Editor) and now degrades to a WARN instead of failing.
  `check-gates.ps1` stays in place for projects that already hook it.
- `react-ux-mechanics` (project-bootstrap → 0.1.2): tooltip value rule, reveal
  granularity, calmer hover, rich tooltips with explicit comparisons.
- `data-storytelling` (report-storytelling → 0.1.2): sharper trigger boundary.
- Site: section band replaces the sticky sidebar, per-plugin descriptions on
  every card, plugin picks highlight their card, new "Що потрібно системі"
  section covering Windows / macOS / Linux.

## 0.1.5 — 2026-08-18

- New skill `react-ux-mechanics` (project-bootstrap → 0.1.1): React SPA UX
  baseline — portal tooltips, sticky table headers, entrance animations with
  reduced-motion guards, error boundaries, lazy routes, optimistic saves,
  URL state, skeletons, count-up numbers; ships assets/patterns.md with nine
  ready recipes.
- New agent `ux-baseline-auditor` (project-bootstrap): read-only audit of an
  existing React app against that baseline; self-sufficient embedded
  checklist.
- Catalog site: full-environment inventory section (all skills of the
  author's machine grouped by source with per-group colors).

## 0.1.4 — 2026-08-18

Trigger coverage completed: all 51 skills now probed live.

- 39 previously untested skills probed with real `claude -p` router runs
  (PBIP repo cwd for report skills, clean Node repo for bootstrap/azure):
  37/39 hit on the first pass; azure-ops and project-bootstrap 6/6.
- The two systematic losers were rewritten and adversarially reviewed:
  `powerbi-visuals` (old prose description had no "Use when", no trigger list
  and no Ukrainian vocabulary — the router never picked it) and `pbi-tables`.
  Both now carry explicit trigger lists and reciprocal Do-NOT boundaries
  (tables ↔ typography/CF/matrix; visuals ↔ every design-skill sibling).
- Coexistence note: with power-bi-agentic-development installed alongside,
  generic report.json / PBIP-table wording may route to its broader
  `pbip`/`pbir-format` skills. In a powerbi-craft-only install,
  `powerbi-visuals` is the sole report.json-mechanics owner.
- `pbi-visuals` → 0.1.1; build script now preserves the marketplace-level
  description field on rebuild.

## 0.1.3 — 2026-08-18

Cross-platform hardening.

- `.gitattributes`: `*.sh` forced to LF — a Windows checkout with
  `autocrlf=true` used to receive CRLF hook scripts that crash bash on every
  report edit.
- `validate-report.sh`: python discovery now also tries the Windows `py -3`
  launcher (plain `python` is often the Microsoft Store stub); opt-out via
  `POWERBI_CRAFT_HOOKS=0`.
- Both agents are now self-sufficient: rulebooks embedded, no reliance on
  reading skill files by relative path (agents run in the user's cwd, not the
  plugin root).
- CI (GitHub Actions, ubuntu + windows): frontmatter YAML of all skills,
  sanitization scan, LF check for shell scripts, plugin/marketplace version
  consistency, and a live pipe-test of the report hook on fixtures.

## 0.1.2 — 2026-08-18

Hooks + agents.

- `pbi-report-ux`: PostToolUse hook validates `report.json` after every edit
  in `*.Report/` — outer/nested JSON parse and sibling-bookmark symmetry.
- `pbi-quality`: `report-design-reviewer` agent (read-only fresh-eyes QA).
- `report-storytelling`: `claim-auditor` agent (mechanical claim-layer checks).
- Contributor hook: SKILL.md frontmatter YAML validation on edit.

## 0.1.1 — 2026-08-18

- 10 oversized skills split into SKILL.md (66–102 lines) + `reference.md`;
  content moved verbatim, preservation verified deterministically.
- Removed `__pycache__` artifacts; affected plugins bumped.

## 0.1.0 — 2026-08-18

Initial release: 9 plugins, 51 skills. Fixed silently-broken YAML frontmatter
in 4 skills (unquoted colon in description).
