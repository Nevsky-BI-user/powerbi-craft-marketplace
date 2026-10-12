# deck-review: report template

> Copy the skeleton below into the review report and fill every section. Headings and verdicts are in
> Ukrainian (the user reads them); check IDs, file names and field names stay as they are. Every finding
> cites a slide, a check ID and a measurement against its threshold; anything not measured or not seen
> is marked «неперевірено» and goes to «Не вдалося перевірити», never into the findings table. The example
> rows describe an invented 12-minute deck about a backup rule.

## Rules for filling it

- **Inventory first.** Counts come from the plan and the render, not from memory: slides, archetypes,
  main flow vs appendix, dividers, demos.
- **Render facts are commands plus their literal result** (exit code, page count, font modes); a command
  that did not run is a «Не вдалося перевірити» line, not a pass.
- **Findings** come from `findings.md` (grouped rows are fine) plus the reviewer's confirmations; mark
  each A+V finding «підтверджено» or «хибне спрацювання» with what is seen on the PNG.
- **Ranking** is by severity first (критично, бажано, косметика), then by how many slides one fix closes.
- **The verdict is one sentence**: ready, ready after the listed критично fixes, or not ready and why.
- No names from captures, no verbatim text longer than 6 words, no local paths.

## Skeleton

```markdown
# Рев'ю презентації: <назва деку>, ітерація <N>

## Інвентар
- Слайдів: <N> (основний потік <n>, додаток <n>); режим: <talk | reading | talk+appendix> (<з плану | відновлено, inferred: true>)
- Архетипи: <title 1, route 1, divider 2, ...>; демо: <id і слайди>; частин: <n>
- Джерело: <HTML з window.deck | HTML без контракту (--slide-selector ...) | PDF з pptx | PDF з Slides>

## Рендер
| Що | Команда | Результат |
|---|---|---|
| Рендер і вимір | `node scripts/html_deck_lint.mjs deck.html out --fonts both` | exit 0; 12 PNG native + 12 metric; print.pdf 12 сторінок 960x540 pt |
| Пікселі | `node scripts/pixels.mjs out/png out` | 1 контактний аркуш; 0 перемикань; 0 майже однакових пар |
| Суддя | `python3 scripts/deck_lint.py --plan deck-plan.json --metrics out/metrics.json --pixels out/pixels.json --out out` | exit 1 |
- PNG == слайдів == слайдів у плані: <12 == 12 == 12>
- Режими шрифтів: native (<які шрифти реально підставились>) і metric (Liberation)

## Лінт
Критично <n> · бажано <n> · косметика <n> · не вдалося перевірити <n>.
Найчастіші перевірки: <Y1 5, D1 3, C1 2, ...>

## Знахідки
| Слайд | Перевірка | Виміряно | Поріг | Урок | Власник | Що зробити | Очима |
|---|---|---|---|---|---|---|---|
| 7 | D1 | 96 слів | <= 80 | L49 | slide-design | таблицю в додаток | підтверджено |
| 4 | C1 | 2.06:1, #E8A33D на #FAFAF7 | >= 4.5 | L36 | slide-design | accent-text #9A5B00 (5.19:1) | підтверджено |
| 9 | S1 | 7.6 pt у скріншоті | >= 9 pt | L53 | slide-design | кроп до панелі, виноска 18 pt | підтверджено |
| 3 | T1 | заголовок-тема | дієслово або число | L12 | deck-storyline | переписати як твердження | claim-auditor: FAIL |

## Ранжування
1. критично: <слайд, перевірка, одна дія>
2. бажано: <...>
3. косметика: <...>

## Не вдалося перевірити
- <C1 на слайді 5: текст на фото, тло невідоме; перевірити на проекторі>
- <Шрифти машини доповідача: шрифт не вбудовано, перевірено лише native і metric>
- <Колір на проекторі: не вимірюється без проектора>

## Звіти агентів
- deck-reviewer: <підсумок, посилання на звіт | недоступний: §V перевірено вручну, див. «Не вдалося перевірити»>
- claim-auditor: <скільки заголовків FAIL, які | недоступний: Title test вручну, див. «Не вдалося перевірити»>

## Журнал ітерацій
| Ітерація | Критично | Бажано | Що змінено |
|---|---|---|---|
| 1 | 6 | 14 | старт |
| 2 | 2 | 9 | D1 на 7 і 11: таблиці в додаток; C1: accent-text |
| 3 | 0 | 4 | S1 на 9: кроп; решта бажано прийнято користувачем |

## Висновок
<Одне речення: готово до показу | готово після N критичних виправлень | не готово, бо ...>
```

## What «Не вдалося перевірити» usually holds

| Situation | Line to write |
|---|---|
| Tool missing (no LibreOffice, no full Chromium) | which checks were not run and why |
| No agent tool (a subagent run): `deck-reviewer` not dispatched | «deck-reviewer недоступний, §V перевірено вручну, свіжого погляду немає» |
| No agent tool: `claim-auditor` not dispatched | «claim-auditor недоступний, T1 перевірено вручну» |
| Gradient, photo or unknown background under text | C1 on those slides, with the slide numbers |
| `#000000` text on a dark PDF page | possibly gradient text (L78), C3 |
| PDF without `plan.slides[].media` | S1 effective size of screenshots |
| Fonts not embedded | the presenter's machine may reflow text; only native and metric modes were measured |
| Projector, room light, the back row | colour and size on the real screen are not measurable headless |
| Speaker notes and timing | read, not rehearsed |
