# Рецепти-патерни (react-ux-mechanics)

Код тут — скорочені робочі витяги з еталона `<еталонний репозиторій>`
(реліз 2.11, задеплоєно й перевірено в проді 2026-08-18). Повні файли — в еталоні.

## 1. Розріз бандла: lazy-маршрути + Suspense + ErrorBoundary

Каркас (Sidebar/TopBar) і сторінка входу — в головному чанку; кожна сторінка —
своїм чанком. У еталоні це зняло ~170 КБ з першого входу (949→780 КБ).

```tsx
import { lazy, Suspense } from 'react';

// React.lazy чекає default-експорт; хелпер знімає це для named-експортів
const lazyPage = <T,>(load: () => Promise<T>, pick: (m: T) => React.ComponentType) =>
  lazy(() => load().then((m) => ({ default: pick(m) })));

const OrgPage = lazyPage(() => import('@/pages/OrgPage'), (m) => m.OrgPage);
// ... всі сторінки так само

// у розмітці макета, навколо Outlet; fallback — свій лоадер або скелетон §7,
// асета для нього немає (він завжди брендований під проєкт)
<ErrorBoundary key={location.pathname} label="сторінку">
  <Suspense fallback={<div className="p-6 text-ink-soft">Завантаження розділу…</div>}>
    <Outlet />
  </Suspense>
</ErrorBoundary>
```

`key={location.pathname}` обовʼязковий: без нього помилка одної сторінки
лишається на екрані після переходу на іншу.

Прод-нюанс: після редеплою старі хешовані чанки зникають — відкрита давно
вкладка при переході ловить `Failed to fetch dynamically imported module`.
Тому фолбек огорожі МАРШРУТУ вартий другої кнопки «Перезавантажити сторінку»
(`location.reload()`), а не лише скидання стану.

## 2. Липка шапка таблиці

`position: sticky` на `th` НЕ працює, коли таблиця лежить у `overflow-x-auto`
обгортці — обгортка стає скрол-контейнером, і «стелі» для прилипання немає.
Рецепт: скрол віддати самій картці таблиці (обидва напрями), шапці — sticky:

```tsx
<div className="max-h-[calc(100vh-190px)] overflow-auto rounded-xl border border-line bg-card
                print:max-h-none print:overflow-visible">
  <table className="w-full min-w-[720px] border-collapse">
    <thead>
      <tr>
        {/* border-b тут НЕ можна: межі при border-collapse їдуть разом із
            прокруткою; замість неї — inset-тінь */}
        <th className="sticky top-0 z-10 bg-paper px-3 py-2 text-left
                       shadow-[inset_0_-1px_0_var(--color-line-strong,#b9c9d6)]">…</th>
      </tr>
    </thead>
    …
  </table>
</div>
```

`print:*` — обовʼязково, інакше друк обрізає таблицю до однієї «сторінки» скролу.
Бонус: стрічка місяців/фільтри над карткою тепер завжди на екрані.

`190px` у `max-h` — сумарна висота всього, що стоїть НАД карткою в еталоні
(шапка сторінки + стрічка місяців + відступи); перерахувати під свій макет,
щоб картка закінчувалась разом із вʼюпортом.

## 3. Дровер деталей із рядка таблиці

Клік по рядку → бічна панель із деталями (метрики, міні-діаграма, складові,
історія). Скелет:

```tsx
{drawerMetric && (
  <>
    <div className="drawer-fade fixed inset-0 z-40 bg-navy/30"
         onClick={() => setDrawerMetric(null)} />
    <aside className="drawer-in fixed inset-y-0 right-0 z-50 w-[min(500px,94vw)]
                      overflow-y-auto bg-card p-5 shadow-2xl"
           role="dialog" aria-modal="true">
      …вміст…
    </aside>
  </>
)}
```

- Escape закриває (і після закриття повернути фокус на рядок-джерело):

  ```ts
  useEffect(() => {
    if (!drawerMetric) return;
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && setDrawerMetric(null);
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [drawerMetric]);
  ```
- Рядок таблиці: `onClick={() => setDrawerMetric(m)}`; вкладені кнопки рядка
  (стрілка розгортання) — `e.stopPropagation()`, інакше кожен клік відкриває дровер.
- Секційні рядки (заголовки без даних) із кліку виключити.
- Дорогі дані дровера (історія внесень) — module-level кеш із TTL
  (`Map<orgId, {at, rows}>`, 60с), щоб повторні відкриття не били в API.

## 4. Оптимістичне збереження форми

Значення лягає в локальний стан ДО відповіді сервера; повний перезапит після
кожної клітинки прибрати. Дві частини:

```ts
// 1) у хуку даних — точковий patch замість reload():
const patch = useCallback((metricId, periodCode, scenario, value) => {
  setCells((prev) => {
    const i = prev.findIndex(/* той самий ключ */);
    if (i >= 0) { const next = [...prev]; next[i] = { ...next[i], value }; return next; }
    return [...prev, { metricId, periodCode, scenario, value, status: 'submitted' }];
  });
}, []);
```

```ts
// 2) у клітинці — patch до await, відкат при відмові:
const previous = current;
onValue(metricId, periodCode, scenario, parsed);   // оптимістично
try {
  await dataService.saveValue(…);
} catch {
  onValue(metricId, periodCode, scenario, previous); // відкат
  setDraft(sent);                                    // введене повернути в поле
  setFailed(true);                                   // border-crit bg-crit-soft + title з поясненням
}
```

Фрагменти — псевдокод із контрактом: `current` — значення клітинки до вводу,
`sent` — надіслане, `draft`/`setDraft` — локальний текст поля, `failed` —
стан «база відмовила» (червона рамка + title з поясненням; скидати при
наступному введенні). Тотали/Σ-контроль/повнота перераховуються самі, якщо
вони похідні від cells.

## 5. Зріз у URL: `?m=` місяць + `?focus=` глибокі посилання

Місяць в адресі → посилання відкриває колезі точний зріз, «назад» гортає місяці.
`useAppState` тут — БУДЬ-ЯКЕ джерело стану зрізу у твоєму застосунку
(useState вгорі, контекст, стор); контракт: `monthIndex: 0..11` +
`setMonthIndex`. URL стан ДУБЛЮЄ, а не замінює:

```ts
export function useMonthInUrl() {
  const { monthIndex, setMonthIndex } = useAppState();
  const [params, setParams] = useSearchParams();
  const urlM = params.get('m');

  // URL → стан: відкриття за посиланням і кнопка «назад»
  useEffect(() => {
    const n = urlM === null ? NaN : Number(urlM);
    if (Number.isInteger(n) && n >= 1 && n <= 12 && n - 1 !== monthIndex) setMonthIndex(n - 1);
  }, [urlM]); // стан → URL веде другий ефект

  // стан → URL: ПЕРШИЙ запис — replace (щоб «назад» одразу після відкриття
  // не вів на ту саму сторінку), далі — звичайні записи історії
  useEffect(() => {
    const target = String(monthIndex + 1);
    if (params.get('m') === target) return;
    const next = new URLSearchParams(params);
    next.set('m', target);
    setParams(next, { replace: params.get('m') === null });
  }, [monthIndex]);
}
```

Глибоке посилання на рядок (`/org/GTS?m=7&focus=<metricId>`) — з чіпів
відхилень аналітики. На цільовій сторінці:

```ts
// ефект СТРОГО над ранніми return (rules-of-hooks!)
useEffect(() => {
  if (!focusId) return;
  setExpanded((prev) => new Set([...prev, ...ancestorsOf(focusId)])); // розгорнути предків
  const t = setTimeout(() =>
    document.getElementById(`metric-row-${focusId}`)
      ?.scrollIntoView({ block: 'center', behavior: 'smooth' }), 120);
  return () => clearTimeout(t);
}, [focusId]);
// рядку: id={`metric-row-${m.id}`} + клас row-flash коли focused
```

Чіп: `<Link to={`/org/${code}?m=${monthIndex + 1}&focus=${d.m.id}`}>` — пастельна
плашка `rounded-full` із назвою (обрізаною `max-w-[28ch]`) і жирною дельтою.

## 6. Карта анімацій по типах діаграм

| Елемент | Клас | Каскад |
|---|---|---|
| стовпчики bar-чарта | `.anim-grow` на rect/обгортці | `animationDelay: i*26ms` |
| кроки водоспаду | `.anim-grow` | `i*45ms` |
| смуги виконання | `.anim-fill` + `transition-[width]` на живі зміни | — |
| лінія тренду/кумулятив | `pathLength={1}` + `.anim-draw` | план/область — `.anim-fade` |
| дуги кільця | `pathLength={1}` + `.anim-draw` | `delay: startFrac*450ms`, `duration: max(frac*450,140)ms` — кільце змальовується частками по колу |
| підписи, легенди, пунктири | `.anim-fade` | після головного |
| великі цифри | `useCountUp` | лише перша поява |
| блоки/картки | `.anim-rise` | `i*40..60ms` |

- Стек-колонки анімувати ЦІЛОЮ колонкою (`.anim-grow` на групі), не по
  сегментах — по-сегментна анімація лишає щілини між сегментами.
- `.anim-grow` задає transform: на елементі з власним transform
  (`-rotate-90` кільця) — вішати на обгортку.
- Політика повторів: entrance-анімації грають при МОНТУВАННІ. Перемикання
  зрізу (місяця/фільтра) свідомо НЕ переграє їх — постійне «переростання»
  втомлює (та сама логіка, що played-ref у useCountUp). Живі зміни значень
  вести transition-ами (`transition-[width]` на смугах). Якщо переграти
  дуже треба — ремаунт через `key`, але це виняток, не правило.

## 7. Скелетони завантаження

Замість «Завантаження…» — контур майбутнього вмісту (12 рядків-мерехтінь для
таблиці, сітка полів для форми):

```tsx
{loading ? (
  <div className="space-y-2 p-4">
    {Array.from({ length: 12 }, (_, i) => (
      <div key={i} className="h-9 animate-pulse rounded-md bg-select"
           style={{ animationDelay: `${i * 60}ms` }} />
    ))}
  </div>
) : (…)}
```

## 8. Клавіатура і мʼякі перемикання

```ts
// ←/→ гортають місяці; не красти стрілки в полів вводу
useEffect(() => {
  const onKey = (e: KeyboardEvent) => {
    const t = e.target as HTMLElement;
    if (/^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName) || t.isContentEditable) return;
    if (e.key === 'ArrowLeft') prevMonth();
    if (e.key === 'ArrowRight') nextMonth();
  };
  window.addEventListener('keydown', onKey);
  return () => window.removeEventListener('keydown', onKey);
}, [prevMonth, nextMonth]);
```

Стрічка перемикання періодів: `useTransition` — локальний стан `clicked`
підсвічує вибір миттєво, а важкий перерахунок сторінки їде транзишеном без
блокування кліку. Сайдбар: `<NavLink viewTransition>` (react-router-dom 7) —
плавний перехід між розділами задарма.

## 9. «Посилання» і «Зведення»

`CopyButton` (асет) + збирач тексту: кнопка «Посилання» копіює
`location.href` (URL уже містить зріз завдяки §5); «Зведення» — текстовий
підсумок місяця для листа: заголовок, головні показники з дельтами, «Гірше
плану найбільше: …», лінк. Українська множина — через `plural(n, 'один',
'два-чотири', 'пʼять+')` з правилом 11–14 (див. скіл ukrainian-ui-copy).
Збирач тримати чистою функцією + юніт-тести на відмінки й числа.

## 10. Компактна підказка значення (формат, затверджений замовником)

Підказка «факт окремо, план окремо, різниця окремо» зʼїдає пів екрана і
дублює сама себе. Робочий формат — заголовок з одиницею і рядки-порівняння,
кожен несе ПАРУ абсолютів і тоновану дельту окремою коміркою:

```
Дизельне паливо · тис. т
До плану      271,9 проти 286,4   −5,1%
До травня     271,9 проти 248,3   +9,5%
```

Правила:
- одиниця — ОДИН раз у заголовку (числа голі → рівний стовпчик);
- значення нейтральні, колір несе лише дельта (кольорове число серед чорних —
  половина плутанини);
- місяць після «до» — родовий відмінок (MONTH_GENITIVE, див. ukrainian-ui-copy);
- для відсоткових показників дельта в в. п., не «відсоток від відсотка»;
- порівняння неможливе (немає факту чи плану) → чесний фолбек рядками
  «Факт · місяць: не внесено» — пояснює, чому нема оцінки;
- пояснення «чому це добре/погано» (deviationNote) — полем `note` під рискою,
  НЕ вкладеною другою підказкою (дві картки одночасно збивають з пантелику).

Будівник тримати чистою функцією (`valueTipRich(input): RichTip`) в lib —
усі підказки застосунку успадковують формат однією правкою.

## 11. Правило доданої цінності + живий бокс замість підказок на точках

**Підказка існує лише тоді, коли додає щось, чого на екрані немає** —
порівняння, повну назву обрізаного підпису, пояснення оцінки. Підказка, що
повторює видимий підпис чи число, — шум, який дратує замовника. Реальні дублі,
зняті за фідбеком: кроки водоспаду (назва+значення вже підписані), виноски
кільця (факт·частка·план уже в тексті виноски), смужки збору (лічильник X/Y
поруч), бейдж періодичності («Місячна» і так написано). Механічний тест:
якщо текст підказки можна прочитати на екрані без неї — видалити.

**Живий бокс замість підказок на точках**: коли біля лінійного графіка вже є
бокс значень (план/факт/відхилення), не вішати підказки на точки — зробити
бокс живим: він, маркер розриву і рядок «станом на {місяць}» слідують за
наведеною точкою (crosshair уже показує, яку читаєш), а без наведення
показують крайню. Один рухомий readout замість двадцяти спливаючих карток.

```ts
const hoverFact = hover !== null ? series[hover]?.fact : null;
const shown = hover !== null && hoverFact != null ? { i: hover, v: hoverFact } : last;
const shownPlan = shown ? series[shown.i].plan : null;
// весь бокс/маркер/легенда рендеряться від shown, не від last
```

## Доповнення до §6: грануляція scroll-reveal

Reveal навколо ВИСОКОЇ сітки (2000px+) розкриває все одним рухом, щойно
верхній край + threshold потрапляє в кадр: каскаду немає, нижні ряди при
прокрутці вже застиглі — саме так виглядає скарга «анімації зникли або
занадто швидкі». Правильно: Reveal на КОЖНОМУ елементі сітки (обгортка стає
grid-елементом, картці всередині — h-full) з каскадним delay={i*60}; KPI-
стрічкам і хедерам — власний anim-rise, інакше верх сторінки «мертвий».
