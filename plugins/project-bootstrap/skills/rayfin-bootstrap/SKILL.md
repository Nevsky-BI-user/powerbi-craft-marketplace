---
name: rayfin-bootstrap
description: Use when scaffolding, linking, recovering, or deploying a Rayfin project (Microsoft Fabric Apps preview, AppBackend + SQLDatabase items) — new app, lost-source recovery against a deployed item, local dev setup, or when hitting OperationNotSupportedForItem, AADSTS50057, or accidental-deploy risks. Triggers - "rayfin", "Fabric App", "AppBackend", "розгорни райфін", "перенеси середовище розробки", "fabricapps.net".
---

# Rayfin bootstrap (Fabric Apps)

## Що це

Rayfin SDK = Fabric Apps (Preview): TypeScript-схема з декораторами → автогенерована
SQL БД + GraphQL (DAB) + статичний хостинг (`*.webapp.fabricapps.net`) + Fabric SSO.
У сервісі це item **AppBackend** з дочірніми SQLDatabase/SQLEndpoint.

**Джерело коду з сервісу НЕ відновлюється**: `getDefinition` для AppBackend повертає
`OperationNotSupportedForItem`; команд pull/clone у CLI немає. Репозиторій — єдине
джерело істини. Кажи це користувачу одразу.

## Scaffold і привʼязка до наявного item

```bash
npx @microsoft/rayfin-cli init --template blankapp --workspace-id <ws-guid> --item-id <item-guid>
```

- `--template-name` без `--template <url>` падає — для стандартного шаблону писати саме `--template blankapp`.
- «directory not empty» — тимчасово винести `.claude`/сторонні файли, після init повернути.
- Привʼязка живе в `rayfin/.deployments.json` (fabricItemId, fabricWorkspaceId);
  endpoint і publishable key зʼявляються там після першого `rayfin up`.
- `rayfin.yml`: services auth (fabric provider, allowedRedirectUris додати `http://localhost:5173`),
  data (mssql), staticHosting (dist, команда збірки).

## Команди

| Команда | Дія |
|---|---|
| `npx rayfin up` | деплой УСЬОГО (БД + фронт) — питати дозвіл користувача |
| `npx rayfin up db apply` | лише схема БД |
| `npx rayfin up staticapp deploy` | лише фронт |
| `npx rayfin up status --json` | стан |
| `rayfin env --framework vite` | генерує .env.local (ставити в predev/prebuild) |
| `rayfin up --dry-run --verbose` | діф проти remote — джерело істини; рядок «Create in My Workspace» у dry-run оманливий, реальний деплой оновлює привʼязаний item |

## НЕБЕЗПЕКА: npm run dev деплоїть

Шаблонний `dev` = `rayfin up && vite` → пуш у ЖИВИЙ застосунок. Одразу додай демо-режим:

```json
"dev:ui": "vite --mode demo --port 5173 --strictPort"
```

і в bootstrap-коді: MODE==='demo' → DemoAuth + MockData, нуль звернень до бекенду.
`--strictPort` обовʼязково: деплой перезаписує .env.local і може змінити порт.

## Мультитенантність: AADSTS50057 і ctid

- AADSTS50057 («account is disabled») при scaffold/deploy = закешований обліковий запис
  ІНШОГО тенанта. Ціль — правильний tenant GUID (перевір `az account`/`fab auth`).
- SSO у продакшні: брокерний URL будується з VITE_FABRIC_PORTAL_URL — для мультитенантних
  користувачів **додати `?ctid=<tenant-guid>`** (інакше попап відкривається не в тому
  тенанті й висить до 5-хв таймауту). Робити це в bootstrap: якщо ctid відсутній —
  дописати з env tenant id (робочий приклад: `src/services/bootstrap.ts` в еталонному проєкті).

## Схема (rayfin-core)

`@entity() @authenticated('*')`; поля `@uuid @text @int @decimal({precision,scale})
@boolean @date` (+`{optional:true}`); `@one(() => X, {optional})` → колонка `<field>_id`.
Таблиця = плюралізована назва класу зі збереженням регістру. **`Users` (Id, Email) —
вбудована системна — не оголошувати.** Клієнт: `client.data.<Entity>.findMany({field:{eq:v}, and:[...]})`,
`create({...flat FK columns})`, `update({id},{fields})`.

## Відновлення схеми з OneLake-дзеркала

Коли source втрачено: SQLDatabase дзеркалиться в OneLake Delta-таблиці. `fab table schema`
або `fab cp` файлів `_delta_log` (metaData action містить повну схему колонок). Порожня БД =
нуль `add`-actions в усіх delta-логах. AppBackend невидимий для `fab ls` — шукати `fab find`,
читати `fab api "workspaces/<ws>/items/<id>"`.

## Windows-граблі

- fab/rayfin пишуть статуси в stderr → PowerShell 5.1 показує NativeCommandError — ігнорувати.
- `pip install --user ms-fabric-cli` (uv tool install падає); shim fab.cmd ламає URL з `&` — викликати fab.exe напряму.
- Багаторядкові commit message → `git commit -F <файл>`.

## Організація Claude Code у новому Rayfin-проєкті

Скаффолдити одразу після init; готові файли-еталони — `<еталонний репозиторій>\.claude`:

- **Path-scoped правила** `.claude/rules/*.md` з YAML-полем `paths:` — домен
  вантажиться лише при роботі з відповідними файлами. Мінімум: `schema-db.md`
  (rayfin/**: max на кожному `@text`, незмінні поля авторства через exclude
  справжніх КОЛОНОК `<fk>_id`, інспекція `.temp/dab-config.json` після
  `up db apply`) і `frontend.md` (src/**: типізований клієнт + явний
  `.select([...])`, три стани компонента, адаптивна розмітка). CLAUDE.md
  тримати коротким — лише завжди-актуальне; решта в правила.
- **Запобіжник деплою** в комітованому `.claude/settings.json`: PreToolUse-hook
  (stdin JSON → `jq -r '.tool_input.command'` → grep `rayfin up|npm run dev`,
  винятки `status`/`--dry-run`; exit 2 = блок) + `permissions.deny` на точні
  форми. Машинно-специфічні хуки (graphify тощо) — тільки в
  `.claude/settings.local.json`, який у .gitignore разом із `CLAUDE.local.md`.
- **Субагенти** `.claude/agents/`: `schema-reviewer`, `security-auditor`
  (tools: Read, Glob, Grep; model: sonnet) — важке читання коду в окремому
  контексті, повертають тільки звіт.
- **Скіли-процедури** `.claude/skills/`: `policy-review` (аудит політик перед
  деплоєм), `deploy-checklist` (деструктивна зміна схеми = стоп і явне
  підтвердження користувача; порядок БД → фронт → імпорт довідника).
- **UX-база фронтенду з першого дня** — скіл [[react-ux-mechanics]]:
  animations.css (всі класи з guard reduced-motion), lazy-маршрути +
  ErrorBoundary навколо Outlet, HoverTip замість `title`, скелетони,
  демо-банер. Портовані компоненти лежать у `assets/` того скіла — копіювати
  при скаффолді, а не «колись потім». Аудит уже наявного застосунку —
  глобальний субагент `ux-baseline-auditor`.

## Документація структури — обовʼязкова в кожному застосунку

Створювати `docs/architecture.md` одразу при скаффолді, оновлювати разом зі
структурою. Дві причини, чому тут це не «добре б», а обовʼязково:

1. Код із сервісу не відновлюється (`getDefinition` для AppBackend недоступний) —
   репозиторій єдине джерело істини, і структура має бути описана в ньому.
2. Половина контракту застосунку живе ПОЗА репозиторієм — у воркспейсі: item-и,
   семантична модель, її міри й одиниці виміру, ETL-ланцюг. Без документа ці
   звʼязки доводиться щоразу відкривати наново через CLI.

Обовʼязковий зміст (розділи можна дописувати, прибирати — ні):

1. Що це і для кого — споживач, хост, мова, прод-адреса, ключовий інваріант.
2. Артефакти у Fabric — таблиця `тип | назва | GUID` + де живе привʼязка
   (`rayfin/.deployments.json`, `fabric.yaml`).
3. Потік даних — схемою: джерела → dataflow/notebook → lakehouse → модель →
   споживачі. Прямо назвати, ДЕ саме лежить бізнес-логіка.
4. Джерело даних — таблиці/сутності, зерно, одиниці виміру.
5. Структура коду — дерево `src/` з призначенням кожного каталогу; окремо
   назвати шар, де живуть запити.
6. Конвенції — мова, формати чисел, кольори, три стани, заборона мок-даних.
7. Безпека — ланцюг авторизації, що потрапляє в бандл, ctid, що в .gitignore.
8. Збірка, перевірка, деплой — команди + хто натискає деплой.
9. Межі й відомі ризики — таблицею, з чесним «недоступно/не реалізовано».
10. Як подивитися на живий бекенд — конкретні команди (нижче).
11. Де що документовано ще — карта решти документів.

Правило чесності: перевірене наживо позначати ✔, неперевірене називати прямо.
Документ без цієї позначки за півроку читається як вигадка.

### Команди для розділу «як подивитися на живе»

`az` і `fab` можуть бути залогінені в РІЗНІ тенанти — і тоді SDK-шлях
(`npx fabric-app-data query`) падає з «Not signed in to Azure CLI», хоча
`az account show` показує акаунт. `fab` при цьому працює. Перевірка:
`fab auth status` проти `az account show`.

Читання опублікованої моделі без az:

```bash
fab api -A powerbi -X post "datasets/<datasetId>/executeQueries" -i '{"queries":[{"query":"EVALUATE ROW(\"ok\", 1)"}]}'
```

Метадані моделі — через `INFO.VIEW.*` (звичайні `INFO.*` цей канал відхиляє):
`INFO.VIEW.TABLES()`, `INFO.VIEW.MEASURES()`, `INFO.VIEW.COLUMNS()`.
Вирази мір не віддаються (`[Expression]` = null) — для них XMLA або Desktop.

Інвентар воркспейса: `fab api "workspaces/<ws>/items"` (JSON з GUID-ами).
`fab ls` теж працює, але кирилиця в назвах ламає шляхи CLI
(`[UnexpectedError] charmap`) — тому за ідентифікаторами через `fab api`.

Приклад готового документа: `<інший проєкт>\docs\architecture.md`.

## Еталонний проєкт

`<еталонний репозиторій>` — робочий приклад: schema.ts (9 сутностей),
bootstrap.ts (ctid-фікс), demo-режим, AdminPage-імпорт довідника, CLAUDE.md з процесом,
`.claude/` з правилами/агентами/скілами/запобіжником (структура вище).
Для системи внесення показників — скіл [[kpi-data-entry-app]].
