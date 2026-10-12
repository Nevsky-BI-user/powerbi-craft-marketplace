---
name: deck-storyline
description: Use when planning or rewriting a presentation as a whole (talk, reading deck, or talk plus appendix) - declaring the mode and its budgets, the arc over minutes, route slide and n/N part dividers, concept-to-proof funnel, demo entrance, proof and exit, hub-and-spoke series, a close with one takeaway and next step, slide titles as assertions, Ukrainian on-slide copy and range dashes, speaker notes. Writes deck-plan.json, the storyboard the other deck skills and the lint read, and stops for approval. Do NOT trigger for .pptx file mechanics (pptx), layout, type, colour or screenshots (slide-design), HTML engine code (html-deck), checking a finished deck (deck-review), report or dashboard headlines (data-storytelling), notes prose style (plain-report), posters or cover art (canvas-design). Triggers - 'зроби презентацію', 'доповідь на 20 хвилин', 'структура виступу', 'план слайдів', 'сторіборд', 'заголовок слайда', 'нотатки доповідача', 'демо в доповіді', 'talk outline', 'speaker notes'.
---

# Deck storyline: the talk layer

## Overview

This skill owns what a deck says over time and in what order: the mode, the minutes, the arc, the
demos, the close, slide titles and on-slide copy, and the speaker notes. Its one artifact is
`deck-plan.json` (`references/deck-plan.md`), which `slide-design`, `html-deck` and `deck-review` read.
Claim grammar belongs to `data-storytelling`, pixels to `slide-design`, the build to `html-deck`, `pptx`
or the Slides artifact type, the verdict to `deck-review`. Every rule cites a check ID of `deck-review`
references/rubric.md; the rubric owns every number and wins on conflict.

## When to Use

- Any "make a presentation" request, before a single slide exists: a talk, a reading deck, or both.
- Converting a reading deck into a talk or back, deciding what goes to the appendix, adding a live
  demo, rewriting slide titles, writing speaker notes.
- Symptoms: the first structure signal arrives at slide 8; four demos run back to back with no recap;
  the last slide asks for nothing; titles are product names; a 255-word slide sits in a talk; a reading
  deck at a 226-word median (above the reading budget too) is about to be shown in a hall.

**NOT for:** pixel values, type, colour, screenshots, archetype anatomy (`slide-design`); .pptx
mechanics and `addNotes` (`pptx`); engine code, numbering, print, presenter view (`html-deck`);
rendering or judging a finished or foreign deck (`deck-review`); report and dashboard headlines, claim
grammar (`data-storytelling`, `claim-auditor`); notes prose style (`plain-report`); terms and number
formats (`dashboard-copy`); posters and cover art (`canvas-design`).

## Mode first

Decide who reads the slides and where before anything else: one density cannot serve a hall and a
desk (L01). Budgets are the talk or reading column of these rubric checks, never restated here.
deck-plan.json must declare `mode` (`--plan-only` exits 2 without it); only a built deck judged with no
mode from a plan, `--mode` or the deck itself defaults to talk, and N1 says so.

| Mode | Choose when | Budgets in rubric.md |
|---|---|---|
| `talk` | presented to a room and the PDF hardly matters | talk column of N1, D1, Y1; archetype rows of §13 (D2) |
| `reading` | read at a desk: handout, pre-read, runbook; nobody presents it | reading column of N1, D1, Y1; reading archetypes |
| `talk+appendix` | presented, then sent as a PDF (the usual case) | talk on the main flow, reading after the `appendix-divider` |

- Unsure: choose `talk+appendix`. Matrices, glossaries, runbooks, parameter lists and extra series
  items go behind the appendix divider instead of shrinking type on stage (L01, L09).
- One density per flow: a 52-slide vendor platform deck swings 0, 48, 165, 255 words across four
  neighbours (N8); a 33-slide own deck at a 226-word median breaks even reading budgets (N1, D1, Y1).

## Pre-flight (mandatory: nothing is built before the verdict in step 6)

1. **Mode**, as above, into `plan.mode`.
2. **Audience and decision**, one sentence each (`data-storytelling` reference.md §1). No nameable
   decision: the talk is a lecture; set `decision: null` and say so.
3. **Engine.** No format named and the host offers the claude.ai Slides artifact type: Slides
   artifact. A .pptx named or a template given: `pptx` for file mechanics, `slide-design` for every
   visual rule. An offline file shown from a browser or printed to PDF: `html-deck`. Every engine ends
   in the `deck-review` loop.
4. **Minutes** (N12). Subtract Q&A and every demo time box from the slot, then budget content slides
   at N12 `min_per_slide`. Example: 20 minutes, 3 of Q&A and a 3-minute demo leave 14, so 7-9 content
   slides. Title, route, dividers, demo entrances, stills and photos do not count (rubric §1
   `structural` group); `demo-recap` and `close` do.
5. **Titles-only `deck-plan.json`**: `n`, `id`, `archetype`, `part`, `title`, `minutes`, plus the
   structural fields `list`, `series`, `pair`, `demo`, `proof_of` and `appendix` (true on every slide
   after the `appendix-divider`) that let the N checks run. Shape in `references/deck-plan.md`; a
   passing sample in `assets/deck-plan.example.json`.
6. **Gate.** Read the titles alone, in order, and dispatch `claim-auditor` on them; without an agent
   tool, apply its Title test yourself and write «claim-auditor недоступний, T1 перевірено вручну» under
   the storyboard. From the project folder run `python3 <deck-review>/scripts/deck_lint.py --plan-only
   deck-plan.json` (`<deck-review>`: the `deck-review` skill folder next to this one) until it exits 0 (it
   fails on бажано here). A T1 verb suspect that passed the Title test gets `title_verified`
   (`references/deck-plan.md` §4), never a reworded title. Then show the storyboard and STOP.

### Storyboard approval

Show a titles-only table (`n | part | archetype | title | min`) and the lint summary line, then wait.
Only «затверджую сторіборд vN» approves; «правки сторіборду vN: <список>» means apply the edits as vN+1
and rerun step 6. The verdict grammar is reused from `pbi-redesign-approval` and the plan's `approval`
object is the record, with no second ledger (`references/deck-plan.md` §5 Close and approval). Anything
else is not a verdict. No token sheet, scaffold or slide before `approved`.

## The arc

Seven beats for technical and product talks; slide counts are main flow (L02-L11). Depth, slot sizes
and the sag diagnosis: `references/arc-and-pacing.md`. Under N2 `short_minutes` the N12 budget holds
fewer content slides than beats: merge them as its §2 Short slots says.

1. **Title** (1): a promise of what the audience can do or decide, plus a context line with event,
   month or version (N3).
2. **Hook** (1-2): one concrete scenario or number, with its base.
3. **Route** (1): the numbered parts (N2 `parts`, fewer allowed under `short_minutes`) and an audience
   hint, «Частини I і II не потребують технічної підготовки» (N2).
4. **Each part**: divider n/N phrased as the part question, one concept, its place in the map, the
   proof (demo or annotated shot of the result), a one-sentence recap (N5, N11). At most one dense
   slide per part (`references/arc-and-pacing.md` §3 Pacing); reference detail goes to the appendix.
5. **Synthesis** (1): return to the opening model (bookend, judged visually; `pair` is only for
   adjacent before/after, N4) and name the items promised.
6. **Close** (1): takeaway, recap, next step (N10).
7. **Appendix**: behind its own `appendix-divider`, judged with reading budgets (N1).

## Quick Reference

| Rule | Test on the plan or the build | Check | Lesson |
|---|---|---|---|
| Route after the title; each part opens with one divider style showing n/N | route within `route_pos_max`; first main slide of a part is a `divider` | N2 | L02 |
| Title slide carries a promise and a context line | slide 1 is `title`; `promise` and `context` set | N3 | L03 |
| Before and after share one grid; only a declared bridge between | both ends `before-after`; at most `gap_max` slides with role bridge | N4 | L04 |
| Concept, map, zoom, demo carry one token; a zoom never redraws | `zoom` follows `map`; title drift within `drift_pt` | N5 | L05 |
| Every demo has entrance, proof, exit and a time box | `demo.role` triple in order; entrance has `minutes` | N6 | L06 |
| Hub before spokes; names, order, icons from `plan.lists` | hub precedes spokes; list order; labels verbatim | N7, N13 | L07, L62 |
| Neighbours within 2x words; a low bridge after a silent run | `ratio_max`, `bridge_words` (built deck only) | N8 | L08 |
| A talk series shows the hub and its 1-2 strongest items | spokes on the main flow within `items_main_max` | N9 | L09 |
| Close: takeaway, verbatim recap, one next step, links collected there | last main slide `close` or `cta`; `url_chars_max` | N10 | L10 |
| Each concept directly before its proof | `proof_of` points back, nothing interleaved | N11 | L11 |
| Slides fit the minutes | content count in the N12 range; minutes plus Q&A within the slot | N12 | L09 |
| Content titles are assertions; dividers are questions or topics | digit or finite verb; `divider_words_max` | T1 | L12 |
| The strongest sentence on the slide is its title | nothing better in a band, caption or why-box | T2 | L13 |
| One-line titles, never autofit, no one-word last line | within `chars_cyr` / `chars_latin` scaled by size | T3 | L14 |
| A repeated series label is an eyebrow; the claim is the largest text | eyebrow within `eyebrow_pt` | T4 | L15 |
| Siblings in parallel grammar, each with a differentiator | cover the names: still tell them apart? | T5 | L16 |
| The first body line adds a number or an outcome | overlap with the title within `overlap_max` | T6 | L17 |
| A number that carries the claim is the hero, with base and method | `hero_ratio_min`, `label_words_max` | T7 | L18 |
| From-to rows are outcomes; the "from" side is muted | equal rows, one arrow each | T8 | L22 |
| NBSP between number and unit; Latin product names in the running font | T9 unit pattern | T9 | L71 |
| One range form per `dash_policy` | no U+2013 or U+2014 under `hyphen` | T10 | L72 |

```text
bad:  «Сейф паролів: огляд можливостей»    a topic (the T1 regex even passes it; claim-auditor does not)
good: «Сейф шифрує паролі ще на ноутбуці»  an assertion, 33 characters, one line
```

Wording, the series eyebrow, more Ukrainian examples and the fix order: `references/titles-and-copy.md`.

## Demo choreography

- **Entrance** (`demo-divider`, `demo.role: entrance`, `demo.minutes` is the time box): an outcome title
  that says what to watch for (T1 `demo_divider_words_max`, L06), the deck's demo pill, and the
  concept's icon or colour carried over (N5); the «дивіться на ...» cue goes in the entrance notes.
- **Proof** (`demo-still`, `proof`): the result moment, never a setup or empty state, with a «що
  помітити» caption; captured and scrubbed per `slide-design` S1-S6.
- **Exit** (`demo-recap`, `exit`): three numbered steps or one outcome sentence. It is the bridge back
  to talk density (N8) and what the audience remembers (L06).
- **Fallback**: the proof still is both the PDF record and the live fallback; the notes carry the
  hard-stop cue and a fail line («якщо демо не стартує, показую результат на наступному слайді»).
- Never two demos without an exit between them (N6). Checklist and timing: `references/demos-and-notes.md`.

## The close

One takeaway sentence as the close title (N10, T3); a recap with the route or hub labels verbatim, never
a new triad (N13); one next step with a short URL in a pill, QR or contact (L10). Links live here or in
the appendix, never only in the notes (H4). It stays up through Q&A as the last main-flow page, so it
works without the speaker. Detail and the reading variant: `references/arc-and-pacing.md` §9 The close.

## Ukrainian slide copy

- Budget Ukrainian 10-15% longer than English, titles within the Cyrillic T3 budget (L71); NBSP
  between a number and its unit («за 20 хвилин», T9). Case, quotes and apostrophe: `dashboard-copy`
  rule 9; numbers, dates and `%`: `dashboard-copy` references/uk-formats.md; terms: `dashboard-copy`
  domain glossaries; plural forms and «слайд N»: `ukrainian-ui-copy`.
- Product names stay Latin in the running font, not mono: a slides-only exception to `plain-report`
  rule 3; mono is for code, commands and file names.
- Ranges (T10, L72): `dash_policy: hyphen` whenever the project CLAUDE.md bans dashes, so «10-15»,
  «з 5 по 7». This overrides `dashboard-copy` rule 9 for decks under such a rule; under `en-dash`
  follow rule 9 and never mix forms. The minus sign U+2212 is not a dash and stays.
- Uppercase Cyrillic with digits in a mono face is `slide-design` Y6: write «2 / 7».

## Speaker notes

Every main slide of a talk gets notes (H6 counts them in an HTML build). In order: the cue (what is on
screen, what to click); script points, not a script; numbers to say aloud, rounded, with their base
(L18); the transition sentence; the cumulative minute mark («Позначка 9:00») matching plan minutes
(N12); one backup answer, and for a demo the fail line. Prose style: `plain-report`. Placement:
`aside.notes` (`html-deck`) or `slide.addNotes()` (`pptx`). Print hides notes (H4), so nothing a PDF
reader needs lives only there. Worked example: `references/demos-and-notes.md` §5.

## Common Mistakes

| Mistake | Why bad | Correct |
|---|---|---|
| Topic or product titles on most content slides | Titles read alone tell nothing (T1) | An assertion per content slide; topics only on dividers |
| The claim in an 11 pt footer caption under a generic title | The best sentence sits where nobody reads (T2) | Promote it to the title |
| No route; the first divider at slide 8 | The audience cannot place itself (N2) | Route after the title, n/N dividers |
| Four demo posters back to back | Nothing to remember, nothing for the PDF reader (N6) | Entrance, proof and exit per demo |
| The overview after its deep dives | The hub promises too late (N7) | Hub first, spokes in its order |
| Seven identical series slides, one claim on 4 of 6 | Template fatigue and clone errors (N9, T11) | Hub plus 1-2 items, the rest in the appendix |
| Closing on a diagram with no ask | The Q&A slide asks for nothing (N10) | Takeaway, recap, next step |
| A reading deck presented as a talk | A 226-word median at about 10 pt in a hall (N1, D1) | Split by claim; reference behind the appendix divider |
| One platform redrawn in a second style | The audience re-learns the picture (N5) | Zoom into the same layout |
| Hub names typed by hand on every spoke | Items drift, get renamed and reordered (N13) | Render them from `plan.lists` |
| Shrinking text to fit the minutes | Breaks the mode floor (Y1) | Move slides to the appendix |

## Verify before done

`--plan-only` exits 0 → the titles read alone tell the story and pass `claim-auditor` (or its step 6
fallback) → «затверджую сторіборд vN» recorded in `approval` → `slide-design` token sheet passes `--tokens`
→ build (`html-deck`, `pptx` or the Slides artifact) → `deck-review` loop at 0 критично with every бажано
fixed, refuted or accepted (P2) → notes on every main slide → `git diff` matches intent.

Timing and delivery are verified only by a timed rehearsal: the lint checks the minutes the plan
claims, not the minutes the speaker takes. Say so instead of claiming the talk fits.
