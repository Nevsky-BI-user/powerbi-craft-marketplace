# Сайт-каталог (site/) — дизайн-нотатка

Затверджено 2026-08-18: каталог статичний з git, Supabase — лише лічильники;
опис скіла — клік-розгортання картки (варіант Б); сайт живе в site/ цього репо.

## Потік даних

```
plugins/**/SKILL.md + plugin.json + CHANGELOG.md
        │  (пуш у main)
        ▼
scripts/build_catalog.py  →  site/src/catalog.json   (CI, крок перед збіркою)
        ▼
vite build  →  site/dist  →  GitHub Pages
```

- Джерело істини — фронтматтери скілів. catalog.json — похідний артефакт;
  закомічена копія потрібна лише для локального dev, CI її перегенеровує.
- Додавання скіла в plugins/ оновлює сайт без жодного ручного кроку.
- Битий фронтматтер валить validate-воркфлоу і build_catalog (обидва парсять YAML).

## Supabase (опційний шар)

- `supabase/migration.sql`: таблиця copy_events (insert-only для anon, RLS),
  агрегат-вʼю copy_counts (security_invoker=off свідомо — віддає лише суми).
- Ключі приходять у збірку як repo variables `VITE_SUPABASE_URL`,
  `VITE_SUPABASE_ANON_KEY`. Anon key у публічному бандлі — нормально за таких
  політик; максимум зловживання — накрутка лічильника.
- Без ключів telemetryOn=false: сайт повний, лише без бейджів «топ».
- Події: marketplace / plugin / skill-view / skill-prompt / all-terminal / all-prompt.

## UX-рішення

- Чіп скіла → картка під рядком: короткий опис, тригери, install плагіна,
  «лише цей скіл» — промпт для Claude Code (CLI ставить лише плагіни цілком).
- Глибокі посилання: #<skill-name> відкриває картку і скролить до неї.
- «Встановити все»: таби термінал / промпт для агента.
- «Як почати» містить вмикання автооновлення (для сторонніх маркетплейсів
  воно вимкнене за замовчуванням) і disclosure про хук та субагентів.
- Темна тема — prefers-color-scheme, палітра з того ж фіолетового бренду чіпів.

## Підключення Supabase (одноразово)

1. Створити проєкт на supabase.com (безкоштовний тір достатній).
2. SQL Editor → виконати supabase/migration.sql.
3. Repo → Settings → Secrets and variables → Actions → Variables:
   `VITE_SUPABASE_URL` = https://<ref>.supabase.co,
   `VITE_SUPABASE_ANON_KEY` = anon public key (Settings → API).
4. Перезапустити воркфлоу pages (або будь-який пуш у main).
