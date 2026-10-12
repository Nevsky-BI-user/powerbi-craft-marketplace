# deck-storyline: titles and on-slide copy reference

> Slide-copy rules with Ukrainian good and bad examples on invented topics (a password vault, room
> booking, expense claims, onboarding). Lessons L12-L18, L22, L71, L72; checks T1-T10 of `deck-review`
> references/rubric.md §3, which owns every number. Claim grammar itself (entity, verb, magnitude, base,
> period) belongs to `data-storytelling` reference.md §2; this file adds only what a slide changes:
> one line, a room, a speaker, a PDF. Non-breaking spaces in the examples are real U+00A0 characters.

## §1. Title type by archetype (T1, L12)

| Archetype | The title is | Check |
|---|---|---|
| content archetypes (thesis, concept, hub, series-item, before-after, demo-still, ...) | an assertion: a finite verb, a number or a named outcome | T1 |
| `title` | the deck title; the promise goes in the dek, the context line under it | N3 |
| `route` | a label for the agenda («Три питання за 20 хвилин») | exempt (`title_exempt`) |
| `divider` | the part question, identical to `parts[].question` | T1 `divider_words_max`, N13 |
| `demo-divider` | the outcome to watch for | T1 `demo_divider_words_max` |
| `photo` | a caption | S6 `caption_words_max` |
| `close` | the takeaway sentence | N10 |
| `cta` | the action | exempt |
| `appendix-divider` | «Додаток» | T1 `divider_words_max` |

Read the titles alone, in order, before anything else is written: they must tell the story. Then hand
them to `claim-auditor`.

| Topic title (bad) | Assertion title (good) |
|---|---|
| «Бронювання переговорних» | «Переговорну тепер бронюють за 1 хвилину» |
| «Сейф паролів: огляд можливостей» | «Сейф шифрує паролі ще на ноутбуці» |
| «Адаптація нових працівників» | «Новачок отримує доступи в перший день» |
| «Звіти про витрати» | «Звіт про витрати подають з телефона» |
| «Результати пілоту» | «Час на заявку впав з 3 днів до 4 годин» |

**The T1 heuristic** in `--plan-only` and the lint passes a title with a digit or a token that looks like
a finite verb (the pattern lives in `deck-review` scripts/deck_lint.py). It only nominates suspects. It
falsely passes noun phrases with verb-like endings («Правила користування сейфом», «Адаптація нових
працівників») and misses real assertions in impersonal or consonant-stem forms («Усі паролі знайдено
за тиждень», «Ми знайшли всі паролі»). `claim-auditor` decides; never bend a good title to please the
regex. When it passes a suspect, set `"title_verified": "claim-auditor"` on that slide (`"manual"` after
the manual Title test when `claim-auditor` is unavailable); the plan gate then exits 0 with the title
unchanged (`references/deck-plan.md` §4).

## §2. Length: one line (T3, L14)

Budget = T3 `chars_cyr` (Cyrillic) or `chars_latin` x `at_pt` / title size, minus `logo_minus` with a
logo lockup. Worked with the rubric values at the time of writing (40 Cyrillic and 45 Latin characters
at 36 pt): a 32 pt title allows 45 Cyrillic characters, a 40 pt title 36. `--plan-only` measures the
plan string; the built deck is measured again at its real size.

Fix order when a title is too long:

1. Shorten words, keep the claim.
2. Drop what the eyebrow already says.
3. Move the detail to the dek or the first body line.

| Step | Title | Chars |
|---|---|---|
| draft | «Бронювання переговорних кімнат тепер займає лише одну хвилину замість десяти» | 76 |
| 1, shorter words | «Переговорну бронюють за хвилину, а не за десять» | 47 |
| 2, eyebrow «Бронювання · результат» carries the topic | «Бронь займає 1 хвилину замість 10» | 33 |
| 3, detail to the dek | title «Бронь займає 1 хвилину», dek «Було 10 хвилин; пілот у двох офісах» | 22 |

Never autofit: the ref autofit shrank one title to 32.1 pt and moved it 4 pt, breaking the series
alignment (G1, K3). Never leave a one-word last line (`orphan_words_min`); the ref has orphans on 4, 5
and 35, the own deck on 22.

## §3. Hierarchy: eyebrow, title, dek (T4, L15)

- **Eyebrow**: «Частина · кут» («План переходу · огляд») or «n / N · пункт» («2 / 3 · Перенесення»),
  within T4 `eyebrow_pt`, sentence case in the running font. Uppercase mono Cyrillic with digits is a
  Y6 defect: the own deck's step eyebrows read as «КРОК 2 3 7».
- **Title**: the per-slide claim, the largest and highest-contrast text on the slide except a hero
  number.
- **Dek**: one optional line under the title; on the title slide it carries the promise (N3). In talk
  mode it is usually omitted.

| Bad | Good |
|---|---|
| title «Автоматизація звітності» on every slide of a series, the real point in a small coloured line underneath | eyebrow «2 / 4 · Звітність», title «Звіт збирається сам щопонеділка о 9:00» |
| a «Демо:» prefix eating the start of every demo title | the demo pill marks the mode; the title states the outcome |

Evidence: ref 37-42 set the series label at 36 pt and the claim at 16 pt in a 2.09:1 accent; a demo
prefix takes about 40% of the title on 19, 20, 24. The own deck's «part · angle» eyebrow plus an
assertion title is the model.

## §4. The strongest sentence (T2, L13)

Read every text block on the slide and pick the one sentence you would keep if only one survived. If it
is not the title, swap them. Claims hide in bands, subtitles, why-boxes, callouts and footer captions.

| Before | After |
|---|---|
| title «Результати пілоту», footer caption «Час на заявку впав з 3 днів до 4 годин» | title «Час на заявку впав з 3 днів до 4 годин», the caption becomes the method line |

Evidence: ref 13 keeps its claim in an 11 pt footer caption under a generic 28 pt title; 34 in a band;
14 in a why-box; 10 in the subtitle.

## §5. Body lines (T5, T6, L16, L17)

**No restatement** (T6): the first body line adds a number or an outcome. Content-word overlap with the
title above T6 `overlap_max` is a restatement.

| Title | Bad first line | Good first line |
|---|---|---|
| «Сейф шифрує паролі ще на ноутбуці» | «Сейф шифрує всі паролі на ноутбуці користувача» | «Сервер бачить лише шифр, тому викрадена база нічого не дає» |

**Parallel siblings** (T5): sibling names use one grammar, all verb-led or all noun phrases, and each
has a differentiator the others lack. Cover the names and read only the descriptions: if two cards could
swap, they are not differentiated.

| Bad (mixed forms) | Good (one form) |
|---|---|
| «Інвентаризація» · «Переносимо паролі» · «Прибирання старих таблиць» | «Знайти всі паролі» · «Перенести в сейф» · «Видалити таблиці» |

An «accent lead + plain qualifier» list item works only when the leads alone tell the story; the emphasis
mechanism itself is `slide-design` Y5.

## §6. Numbers (T7, L18)

A number that carries the claim is the hero: at least T7 `hero_ratio_min` x body size, a label of at most
`label_words_max` words, its base in words and a method line. Big numbers that are not the claim stay
body-sized (`slide-design`, settled conflicts).

| Bad | Good |
|---|---|
| «У жовтні служба підтримки закрила 412 заявок» mid-paragraph | hero «412», label «заявок закрито в жовтні», base «+18% до попереднього місяця», method «як рахували: журнал служби підтримки, без дублікатів» |

- Base words come from `data-storytelling` reference.md §3 and §9.1 («до плану», «до попереднього
  місяця», «з початку року»); a difference between two percentages is written in «в. п.».
- Formats (decimal separator, thousands, «тис.», «млн», `%`) follow `dashboard-copy`
  references/uk-formats.md; this file does not repeat them.
- Spoken numbers in the notes are rounded and said with their base (`references/demos-and-notes.md` §5).

Evidence: ref 9 hides a very large user count inside a 20 pt subtitle; the own deck's proof tiles plus a
measurement note are the model.

## §7. From-to (T8, L22)

Equal row counts, one arrow per row, the "to" side written as observable outcomes, the "from" side
muted (styling: `slide-design`).

| From (muted) | To (bad, a slogan) | To (good, observable) |
|---|---|---|
| «Паролі в трьох таблицях» | «Безпека нового рівня» | «Кожен пароль має власника» |
| «Доступ через чат» | «Сучасний підхід до доступів» | «Доступ видають за 10 хвилин» |

## §8. Ukrainian specifics (T9, L71)

- **Length**: Ukrainian runs 10-15% longer than English; plan for the Cyrillic T3 budget from the first
  draft, not after the build wraps.
- **NBSP** between a number and its unit: «за 20 хвилин», «4 години», «12 тис. грн» (T9 lists the
  units it scans for). In JSON write `\u00a0` so it stays visible in review (`за 20\u00a0хвилин`),
  as `references/deck-plan.md` §11 says.
- **Product names** stay Latin in the running font, not monospace: «Зміни в Git перевіряє бот». Mono is
  for code, commands and file names (`git log --oneline`). This is a slides-only exception to
  `plain-report` rule 3.
- **Terms** come from the `dashboard-copy` domain glossaries; plural after a number and «слайд N» from
  `ukrainian-ui-copy` (`plural()`): «1 крок», «3 кроки», «5 кроків».
- **Case and punctuation**: `dashboard-copy` rule 9; a slide title follows it as a caption does (no
  trailing period).

## §9. Range dashes (T10, L72), settled

`plan.dash_policy` picks one form for the whole deck, and the lint flags a mixed deck.

| Policy | When | Write |
|---|---|---|
| `hyphen` | the project CLAUDE.md (or house style) bans long and short dashes | «10-15 хвилин», «з 5 по 7 листопада», «2024-2026» |
| `en-dash` | no such rule | `dashboard-copy` rule 9 |

Under `hyphen`, any U+2013 or U+2014 in slide text is a T10 finding; this overrides `dashboard-copy` rule
9 for decks under a no-dash rule. The minus sign U+2212 is not a dash and stays: «−3 в. п.».

A number group («3-2-1», «10-15», «2024-2026») never breaks across lines, whatever the policy: browsers
break after a hyphen or an en dash, and an eval divider at 72 px read «3-2-» / «1» (number splits look
broken, L71). `html-deck` keeps groups whole in titles, deks and generated labels; body text takes
`<span class="nw">` (`html-deck` references/engine.md §10). Not U+2011: Liberation Sans has no glyph for it.

## §10. Links and dates

- No underlined links in body text (N10): the ref's slide 14 carries five underlined 9 pt links.
- Full URLs go on the close or in the appendix; the notes may repeat them but never hold the only copy
  (print hides notes, H4). The close or cta shows one short URL in a pill within N10 `url_chars_max`
  (`example.org/sejf`).
- Roadmap claims carry their date («станом на жовтень 2026») and a status pill; the plan records it in
  `slides[].status` (`state`, `as_of`), the pill component is `slide-design` V8.

## §11. See also

`references/arc-and-pacing.md` · `references/demos-and-notes.md` · `data-storytelling` reference.md §2,
§3, §9.1 · `claim-auditor` · `dashboard-copy` (glossaries, uk-formats.md, rule 9) · `ukrainian-ui-copy`
· `plain-report` · `slide-design` Y5, Y6, V8.
