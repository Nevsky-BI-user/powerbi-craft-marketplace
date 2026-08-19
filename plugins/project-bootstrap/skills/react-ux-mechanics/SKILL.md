---
name: react-ux-mechanics
description: Use when building or polishing a React SPA (дешборд, звіт, форма внесення) and adding tooltips, side drawers, sticky table headers, chart entrance animations, optimistic saves, route code splitting, error boundaries, URL state, count-up numbers, skeletons — or when hitting symptoms - sticky th не липне в overflow-x-auto; підказку обрізає overflow; підказки дублюють видимі підписи («ніякої цінності»); hover/кольори «ріжуть очі»; анімації «зникли» бо reveal розкрив усю сітку одразу; generic T inferred as string (SetStateAction); SVG-лінія не «малює себе» (stroke-dasharray); цифри застигли на 0 у фоновій вкладці (requestAnimationFrame). Triggers - "живі підказки", "дровер", "липка шапка", "анімації графіків", "оптимістичне збереження", "React.lazy", "скелетон", "місяць в URL".
---

# UX-механіки React-застосунку

## Огляд

Набір механік, що робить дешборд «живим»: перевірений у проді
(Rayfin Operational Monitoring, реліз 2.11). Кожен рецепт уже пережив свої
граблі — таблиця нижче і є списком реальних падінь та їхніх ліків.
Портовані файли — в `assets/` цього скіла: копіювати в проєкт і перейменувати
токени Tailwind-теми під свою.

Токени, вжиті в асетах (роль → fallback, якщо своєї теми ще немає):
`navy` бренд-акцент №1 → `#0c375e` · `azure` акцент №2 → `#00a1df` ·
`azure-soft` підсвітка → `#e3f4fc` · `paper` тло сторінки → `#f4f7fa` ·
`card` тло картки → `#fff` · `select` тло скелетона → `#e9eff5` ·
`line`/`line-strong` рамки → `#dbe4ec`/`#b9c9d6` · `ink-soft`/`ink-faint`
другорядний текст → `#4a6076`/`#8199ad` · `ok`/`ok-soft` → `#047857`/`#e8f7f1` ·
`crit`/`crit-soft` → `#c9302c`/`#ffe9e8` · клас `.num` — моноширинні цифри
(`font-variant-numeric: tabular-nums`).

Z-драбина (домовленість, інакше свій хедер поховає підказки):
sticky-шапка `z-10` < тло дровера `z-40` < дровер `z-50` < HoverTip `z-[80]`.

## База нового застосунку — підключати з першого дня

1. `assets/animations.css` → у головний CSS (всі класи мають guard
   `prefers-reduced-motion`) + `assets/Reveal.tsx`: блоки з entrance-анімацією
   нижче згину екрана — в `<Reveal>`, інакше анімація відіграє невидимо до
   прокрутки.
2. Маршрути через `lazyPage` + `Suspense` + `ErrorBoundary key={pathname}`
   навколо `<Outlet/>` — [patterns.md](assets/patterns.md) §1.
3. `HoverTip` замість атрибута `title` — скрізь і одразу (портал у body), але
   за правилом доданої цінності (patterns §11): підказка, що повторює видимий
   підпис чи число, не вішається взагалі.
4. `ErrorBoundary` на кожен обчислювальний блок дешборда (падає блок, не сторінка).
5. Скелетони на місцях завантаження таблиць і форм (§7).
6. Демо-банер, якщо застосунок має демо-режим із згенерованими даними.

Решта — за потребою з каталогу. Дотягувати наявний застосунок — субагент
`ux-baseline-auditor` (read-only аудит проти цього списку; живе в
`~/.claude/agents/ux-baseline-auditor.md` — у чуже середовище копіювати
разом зі скілом).

## Каталог

| Механіка | Де | Навіщо |
|---|---|---|
| Жива підказка | `assets/HoverTip.tsx` | миттєва, у стилі бренду, не ріжеться overflow |
| Компактна rich-підказка чисел | patterns §10 + HoverTip.rich | «До плану: 271,9 проти 286,4 · −5,1%»: одиниця в заголовку, пари абсолютів, тонована дельта окремо |
| Правило цінності підказок + живий бокс | patterns §11 | дублі видимого — геть; біля лінії — рухомий readout замість підказок на точках |
| Сегментований перемикач | `assets/Segmented.tsx` | пари/трійки режимів замість select |
| Кнопка «Скопіювати ✓» | `assets/CopyButton.tsx` | посилання/зведення з видимим підтвердженням |
| Огорожа помилок | `assets/ErrorBoundary.tsx` | блок падає сам, сторінка живе |
| Докрут цифр | `assets/useCountUp.ts` | лише перша поява; фонова вкладка ок |
| Анімації появи | `assets/animations.css` | rise/grow/fill/draw/fade/drawer/row-flash/card-lift; лінії — лише в парі з `pathLength={1}` |
| Scroll-reveal | `assets/Reveal.tsx` + `.reveal-wait` в animations.css | анімація стартує при появі блока у вʼюпорті; спрацьовує раз; «пізній» reveal обнуляє каскадну затримку |
| Розріз бандла | patterns §1 | перший вхід без адмінки й довідки |
| Липка шапка таблиці | patterns §2 | шапка на місці, фільтри завжди видно |
| Дровер деталей | patterns §3 | клік по рядку → все про показник |
| Оптимістичне збереження | patterns §4 | значення одразу, відкат при відмові |
| Зріз у URL + deep-link | patterns §5 | `?m=` місяць, `?focus=` рядок зі спалахом |
| Карта анімацій діаграм | patterns §6 | який клас на який елемент, каскади |
| Скелетони | patterns §7 | контур замість «Завантаження…» |
| Клавіатура + transitions | patterns §8 | ←/→, useTransition, viewTransition |
| Посилання/Зведення | patterns §9 | текстовий підсумок для листа |

## Граблі (кожна коштувала реальної відладки)

| Симптом | Причина → лік |
|---|---|
| sticky th не липне | таблиця в `overflow-x-auto` — обгортка стала скрол-контейнером → скрол самій картці, `th` sticky + inset-тінь замість border (§2) |
| підказку обрізає | overflow-обгортки таблиць → портал у body (HoverTip) |
| generic T = `string` | inference з setState-колбека дає `SetStateAction<…>`, constraint падає → `NoInfer` на options І onChange, T виводиться лише з value (TS ≥ 5.4; старіший — явний generic на виклику) |
| лінія не малюється | dasharray у пікселях довжини → `pathLength={1}` на SVG-елементі + `.anim-draw` |
| цифри застигли на 0 | rAF не тікає у фоновій вкладці → страхувальний `setTimeout(ms+150)` (useCountUp) |
| цифри «танцюють» | докрут на кожну зміну → `played` ref: лише перша поява |
| щілини в стеку | анімація по сегментах → `.anim-grow` на колонці цілком (§6) |
| анімація «зʼїла» rotate | два transform на одному елементі → анімацію на обгортку |
| hover-ефект картки мовчки зник | Tailwind `transition-*` у шарі utilities перебиває `.card-lift` → не поєднувати |
| eslint rules-of-hooks | ефект deep-link після early return → всі хуки над ранніми `return` |
| блок тягне сторінку в білий екран | немає огорож → ErrorBoundary на маршрут і на блоки |
| помилка сторінки «прилипла» | ErrorBoundary без key → `key={location.pathname}` |
| «Failed to fetch dynamically imported module» | після редеплою хешовані чанки зникли, а вкладка стара → у фолбеку огорожі маршруту давати кнопку перезавантаження сторінки, не лише скидання стану |
| докрут не зіграв узагалі | KPI-компонент змонтовано до приходу даних (target=null зʼїв єдиний запуск) → тримати скелетон і монтувати KPI лише з готовими даними |
| reduced-motion → порожній графік | наївний guard `animation:none` для `.anim-draw` лишає dashoffset=1 → guard мусить ставити `stroke-dashoffset: 0` (в assets/animations.css уже так) |
| анімацію під згином ніхто не бачив | entrance-анімації грають при монтуванні → `Reveal` + `.reveal-wait` (пауза до появи в кадрі) |
| «анімації зникли/занадто швидкі» | Reveal на всій високій сітці — все розкривається одним рухом, щойно верхній край у кадрі → Reveal на кожному grid-елементі з каскадом (§6-доповнення) |
| «дублювання в підказках, ніякої цінності» | tooltip повторює видимий підпис/число (водоспад, виноски, лічильники) → правило §11: додає або видаляється |
| «підсвітка ріже очі» | hover = яскрава акцентна рамка + перефарбована назва + кольорова тінь → card-lift (підйом 2px, мʼяка тінь) + border-акцент на /40 прозорості; кольорові акценти лише там, де є ОЦІНКА |
| бокс значень «мертвий» при наведенні | readout біля графіка привʼязаний до крайньої точки → shown = hovered ?? last, весь бокс/маркер/легенда від shown (§11) |
| порожні плями в PDF | друк рендерить сторінку без прокрутки, reveal-блоки застигли у from-стані → guard у `@media print` знімає анімації і ставить dashoffset 0 (в assets уже є) |

Заборона сирого `title=` в JSX (замість HoverTip) — механічна перевірка, не
память ревʼюера. ESLint, лише для своїх компонентів (нативні кнопки-іконки
лишаються):

```js
'no-restricted-syntax': ['warn', {
  selector: "JSXOpeningElement[name.name=/^[A-Z]/] > JSXAttribute[name.name='title']",
  message: 'Використовуй HoverTip замість title: миттєво і в стилі бренду.',
}],
```

HoverTip — лише hover: на сенсорних і з клавіатури підказки немає (як не було
й з title). Дані, без яких не можна працювати, мають жити в дровері (§3) або
в самій розмітці — підказка тільки прискорює, не ховає.

## Еталон

`<еталонний репозиторій>`: `src/components/app/{HoverTip,
Segmented,CopyButton,ErrorBoundary,MetricDrawer}.tsx`,
`src/hooks/{useCountUp,useMonthInUrl}.ts`, `src/main.css` (@layer components),
`src/App.tsx` (lazyPage), `src/pages/OrgPage.tsx` (липка шапка, `?focus=`,
дровер), `src/pages/EntryPage.tsx` + `src/lib/useOrgData.ts` (оптимістичний
patch), `src/lib/summaryText.ts` (зведення).

Платформа Rayfin/Fabric — [[rayfin-bootstrap]]; система внесення показників і
палітри — [[kpi-data-entry-app]]; шаблонні українські рядки —
[[ukrainian-ui-copy]]; заявка сторінки й бази порівняння — [[data-storytelling]].
