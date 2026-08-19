---
name: kpi-data-entry-app
description: Use when building a metric/KPI data-entry web app (план/факт/прогноз, операційні показники) with corporate branding — on Rayfin/Fabric or any React stack. Covers theme selection, Excel dictionary parsing, entry windows, computation model. Triggers - "система внесення даних", "внесення показників", "план факт прогноз", "операційний моніторинг", "data entry app", "довідник показників з Excel".
---

# Система внесення показників (план/факт/прогноз)

## Крок 0 — палітра. Завжди питати (AskUserQuestion, не вгадувати)

| Ключ | Ядро | Коли |
|---|---|---|
| `classic` (Recommended) | navy `#0C375E`, azure `#00A1DF`, amber `#F2A900` | корпоративний стандарт |
| `apple-brand` | акцент `#0071E3`, семантика Apple-AA, решта як classic | синій Apple на бренді, мінімальний відхід |
| `apple-light` | фон `#FFFFFF`, сайдбар `#F5F5F7`, ink `#1D1D1F`, акцент `#0071E3` | світла Apple: навій зникає, чорні заголовки |
| `energy` | `#0C375E` `#FFD500` `#0057B7` | національні акценти |
| `flame` | `#0C375E` `#00A1DF` `#0E7490` | моно-синя |
| `dark` | фон `#0E1F33`, дані `#00A1DF` `#4FC3F7` | темний режим |

Apple-семантика дельт (`apple-brand`/`apple-light`), допрацьована під WCAG AA —
сирі системні `#34C759`/`#FF9500`/`#FF3B30` на світлих підкладках AA не тримають,
їм місце лише в заливках діаграм: ok `#1E7A35`/soft `#E8F7ED` · warn-ink
`#B25000`/soft `#FFF2E1` · crit `#D70015`/soft `#FFEBEC` · нейтральне (ціни/тарифи)
`#6D6D72` на `#F2F2F7`. `apple-light` додатково: line `#E8E8ED`, ink-soft `#5D5D63`,
ink-faint `#9A9AA0`, темна hero-панель `#1D1D1F`. Макети всіх пʼяти палітр на
реальних елементах — `assets/palette-guide.pdf` репозиторію скілів.

Tailwind 4 `@theme` токени; статуси: ok=зелений, amber=«не внесено/частково», crit=відхилення.
Шрифти IBM Plex Sans/Mono через fontsource (бандл — жодних CDN, CSP Fabric їх ріже).
Мова UI українська: «внесення», «показник», «підрозділ», «вікно внесення».

## Модель даних (перевірена)

Organization (kind division|plant, parent) · ReportingPeriod (code `2026-M07`/`2026-Q3`/`2026-Y`)
· MetricDefinition (unit, frequency annual|quarterly|monthly|daily, collection_mode manual|reference,
parent, display_order, source_sheet/row + модель обчислень: row_role total|component|section|standalone,
calc_rule input|sum_children|weighted_avg|balance|derived|alias|none, time_agg sum|avg|last|max|derived,
weight_metric, equals_metric, tolerance_pct) · Submission (status draft/submitted, по org+period+scenario)
· MetricValue (value decimal(28,8), scenario plan|fact|forecast, soft delete is_deleted/deleted_at,
user_id/email аудит) · AnnualMetricValue · UserAssignment · NotificationQueue.

## Парсинг Excel-довідника — граблі, які коштували днів

1. **Два механізми відступів одночасно**: пробіли на початку назви ТА alignment.indent
   клітинки. Ефективний рівень = `max(space_level, fmt_indent)`. Хто читає лише пробіли —
   отримує пласку ієрархію.
2. **Стабільні ID**: uuid5 від slug СИРОЇ назви (до чисток/виправлень одруків) —
   правки парсера не змінюють ID. Після регенерації звіряти `ids identical: True`.
3. **Жирний ≠ сума**: жирний = верхній рівень. Класифікувати кожен блок: Σ сума / Σ± неповна
   сума / ⌀ середньозважене (ціни! вага = парний обсяг) / → баланс зі знаками / ▤ альтернативний
   зріз (два розрізи однієї величини, тотали мають збігатися) / § секція / • самостійний.
4. **Дві осі агрегації**: за складовими (calc_rule) і за часом (time_agg). Залишки/запаси/ДЗ
   = last, середньодобові/% = avg, «максимальний добовий» = max. Всюди-sum дає хибний рік.
5. ● у колонці збору = показник здає ця компанія; фільтр видимості: manual + їхні предки.

## Механіки UI, які затвердив користувач

- **Вікно внесення**: факт за місяць M відкритий 1–10 числа M+1 (константа `ENTRY_WINDOW_DAYS`);
  квартальні здаються в бер/чер/вер/гру, річні — у грудні. Банер стану (відкрито/закрито/зарано).
  Активний місяць = останній завершений відносно поточної дати.
- Галочка **«Лише ті, що треба внести»** (default ON): вікно відкрите + бракує факту чи плану.
- Чипси періодичності (Усі/Денні/Місячні/Квартальні/Річні з лічильниками).
- **Річний план і прогноз — окрема вкладка** (період `-Y`), місячний план вноситься поруч із фактом.
- EntryCell: збереження на Enter/blur, кома→крапка, порожнє = soft delete, жовте = не внесено.
- Тотали: вносяться І тотал, І складові; бейдж `Σ≠` коли розбіжність понад tolerance_pct.
- Верхньорівневі рядки жирні, складові з відступом; плашки періодичності фіксованої ширини;
  заголовки колонок без дублювання назви місяця.
- Покроковий гайд-прожектор (EntryGuide): data-guide якорі, box-shadow 9999px виріз,
  автозапуск раз (localStorage) + кнопка «Як вносити дані».
- **`overflow-x-auto` всередині `grid` не працює без `min-w-0` на елементі сітки.**
  Елемент grid/flex має `min-width:auto`, тож колонка розтягується під найширший
  вміст (теплокарта з `min-w-[640px]`), обгортка ніколи не спрацьовує — і
  горизонтальний скрол їде на всю сторінку. Симптом: `document.scrollWidth`
  більший за viewport при 375px, хоча в компонента правильна обгортка.
- Текст, який **склеює код** (місяці, кількості, одиниці), — скіл
  [[ukrainian-ui-copy]]: «з червень» і «1 підприємств» проходять `tsc` і тести,
  ловляться лише очима в превʼю.
- **UX-база всього застосунку** (живі підказки замість `title`, дровер деталей
  із рядка таблиці, липкі шапки, оптимістичне збереження клітинок, анімації
  появи діаграм, зріз у URL `?m=`/`?focus=`, скелетони, lazy-маршрути з
  огорожами) — скіл [[react-ux-mechanics]] з портованими компонентами в
  assets/; підключати з першого дня, не «після релізу».

## Демо проти живого

MockDataService: детермінований hash(id) → стабільні числа, факти до «минулого місяця»,
~30% поточного пропущено. DemoAuthService. Імпорт довідника — AdminPage: create-missing +
sync-changed, батьки перед дітьми, чанки по 8, idempotent.

## Еталон

`<еталонний репозиторій>` (catalog.ts, entryWindow.ts, EntryPage.tsx,
seed/parse_dictionary.py, seed/build_structure.py, docs/metric-structure-analysis.md).
Розгортання платформи — скіл [[rayfin-bootstrap]]. Power BI-тема тієї ж палітри — pbi-corporate-theme.
