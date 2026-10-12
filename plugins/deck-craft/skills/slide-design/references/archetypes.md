# slide-design: archetype catalog

> One entry per slide archetype: what it is for, what it asserts, its anatomy, its budget, when not to use
> it, measured evidence and the checks that judge it. Evidence: a 52-slide vendor platform deck ("ref N" =
> its slide N, 960x540 pt) and a 33-slide own HTML reading deck ("own N", 1280x720 px). Lessons L01-L79 are
> the teardown ledger described in `deck-review` references/teardown.md; check IDs point to `deck-review`
> references/rubric.md, which owns every number.

## Provenance and format

- **Enum.** The 36 ids below, in this order, equal `deck-storyline` references/deck-plan.md §6, `deck-review`
  scripts/thresholds.json `archetypes`, rubric §13 and the `<template data-archetype>` snippets of the
  `html-deck` template; `deck-review` scripts/selftest.py asserts all four. Headings are `### <n>. <id>`
  (talk), `### R<k>. <id>` (reading) and `### appendix-divider`. Never rename an id here alone.
- **Budget line.** Copied from thresholds.json in the rubric cell grammar: `words_max` (visible live words,
  D1 counting rules), `min_pt` (smallest text the audience must read on that archetype), plus extras.
  `mode` means the mode budget applies: 50 words talk (D1), the Y1 floor of 14 pt talk. Sizes are pt on the
  960x540 page; px on the 1280x720 canvas = pt x 4/3 (18 pt = 24 px, 14 pt = 18.67 px).
- **Reading budget.** Any talk archetype placed behind the `appendix-divider` is judged with the reading
  budget (180 words, 11 pt floor); a reading archetype on a talk main flow is a D2 finding.
- **Where `min_pt` sits below 18 pt** (Y1 `body_pt`), that value is the body target on that slide; it never
  goes below the Y1 floor.
- **HTML.** Each id is the class `.a-<id>` on `section.slide[data-archetype="<id>"]`; the title archetype
  uses `h1.t`, every other `h2.t`. Geometry tokens (title box, grid, margins) live in `visual-system.md`.

Entry fields: **Purpose**, **Asserts**, **Anatomy**, **Budget (D2)**, **Not when**, **Evidence**,
**Checks**. Groups (rubric §1): `dividers` = title, divider, demo-divider, appendix-divider (C4 switch points,
K1 and N8 exempt); `title_box_exempt` = dividers + photo (G1, K3); `raster_exempt` = dividers + photo,
demo-still, annotated-shot (V4).

## Talk archetypes

### 1. title
- **Purpose:** topic, promise and context; also the first page of the PDF.
- **Asserts:** what the audience can do or decide afterwards (plan `promise`).
- **Anatomy:** h1 at the divider size (54 pt / 72 px); the promise as dek at body size; a context line
  (event, month, version) at 14-18 pt; art in its own zone of at least 40% of the width, never under text.
- **Budget (D2):** `words_max=20`; `min_pt=14`; `title_min_pt=40`; `subtitle_ratio_max=0.67`
- **Not when:** always slide 1; a topic label without a promise fails N3; words baked into cover art break
  the live-text rule of V4, which its raster heuristic skips on this archetype, so check them by eye.
- **Evidence:** good own 1 (thesis plus 4 proof numbers); anti ref 1 (two 48 pt lines in two colours, no
  promise, no date).
- **Checks:** N3, D2, C4 switch point, K1 exempt.

### 2. route
- **Purpose:** the parts and where the audience is.
- **Asserts:** the 3-5 questions the talk answers, in order.
- **Anatomy:** numbered parts from `plan.parts`, generated slide ranges, an audience hint; in HTML clickable.
- **Budget (D2):** `words_max=40`; `min_pt=18`
- **Not when:** never omitted in a talk; a talk under 15 minutes may route only 2 parts (N2).
- **Evidence:** good own 2 (numbered parts, ranges, audience hint); ref has none, its first structure
  signal arrives at slide 8.
- **Checks:** N2, N13, H2 (generated ranges), D2.

### 3. divider
- **Purpose:** open a part; the only place a theme may switch.
- **Asserts:** the part question (plan `parts[].question`).
- **Anatomy:** at most 6 words at the divider size (48-60 pt), a generated n/N marker, optional mode pill,
  optionally the icon of the concept the part opens (`icons` map, V1; HTML in `visual-system.md` §9); dark
  family when families are light content plus dark dividers.
- **Budget (D2):** `words_max=8`; `min_pt=mode`; `title_words_max=6`; `title_min_pt=48`
- **Not when:** never skip it for a new part; parts that start cold lose the audience.
- **Evidence:** good ref 8 (54 pt divider with a deliberate theme flip), 32; anti ref 15, 17, 28, 34, 45
  (parts start cold).
- **Checks:** N2, T1, Y1 divider range, C4, K2.

### 4. thesis
- **Purpose:** name the 2-3 layers or pillars the talk is about, or state one sentence alone.
- **Asserts:** the deck claim in at most 25 words.
- **Anatomy:** 2-3 parallel statements as full-width rows, each at the `card_heading` size (27 pt / 36 px):
  a lead of at most 3 words in the emphasis weight (Y5), then at most 8 words at the same size; or one
  sentence as a left-column statement at that size (Y4: at most 12 words, 4 lines); no picture needed
  (settled conflict in SKILL.md). In HTML each row is `li` with the lead in `b.nm` (`html-deck` thesis
  snippet). No heading level over the line: `card_heading` is the smallest sans role at or above
  `min_pt=24`, so a heading 1.3x above it (Y1) reaches the title size, which T4 keeps the largest. No
  columns: in three cards of 4 grid columns a 36 px statement breaks into lines of 10-12 characters (Y4
  asks 35-60).
- **Budget (D2):** `words_max=25`; `min_pt=24`
- **Not when:** a pillar needs proof on the same slide; give each pillar its own slide.
- **Evidence:** good ref 2 at 21 words (L50), every word at 28 pt or more; anti the same slide's teal
  headings run 2.09:1 and sit only 1.14x over their lines (32 over 28 pt, Y1 levels), ref 7 (a statement
  wrapped into 7 lines of 2-3 words).
- **Checks:** D2, Y1, Y4, Y5, C1, T4, T5.

### 5. journey
- **Purpose:** preview a sequence (roadmap, rollout, maturity).
- **Asserts:** the order and what each step delivers.
- **Anatomy:** 3-5 numbered nodes on one reading axis; vertical position only when it encodes something
  (maturity, layer); at most 12 words per step.
- **Budget (D2):** `words_max=mode`; `min_pt=18`; `step_words_max=12`; `steps=3..5`
- **Not when:** the items have no order; use hub cards without numbers (V1).
- **Evidence:** good ref 3 geometry (a rising staircase that encodes maturity) but 95 words; anti ref 15
  (stages alternate between two rows).
- **Checks:** G8, V1, D2.

### 6. before-after
- **Purpose:** show the mess, then the same frame fixed; both ends of a bookend.
- **Asserts:** what changes between the two states.
- **Anatomy:** a shape-as-message diagram (D4) plus at most 4 numbered takeaways at 20 pt or more linked to
  regions by number badges; both ends share one grid and one title pattern; `pair.role` is before, bridge
  or after.
- **Budget (D2):** `words_max=45`; `min_pt=mode`; `takeaways_max=4`; `takeaway_min_pt=20`
- **Not when:** the two states need different layouts; then it is two claims, not a pair.
- **Evidence:** good ref 4 (tangled diagram with 4 pains at 20 pt, though unlinked), ref 28 and 52 bookend
  the talk; anti ref 5 interrupts 4 and 6, and 6 changes layout.
- **Checks:** N4, D4, Y1 (labels inside the shape exempt).

### 7. from-to
- **Purpose:** restate a change as rows.
- **Asserts:** the target state as observable outcomes.
- **Anatomy:** equal row counts, one arrow per row, the "from" side muted (`ink-2` or an outline card, still
  at least 4.5:1), the "to" side in `ink` at the emphasis weight.
- **Budget (D2):** `words_max=40`; `min_pt=18`
- **Not when:** the "to" items are slogans; rewrite them as outcomes first (T8).
- **Evidence:** ref 5 measures about 40 words (L50) but styles both sides alike.
- **Checks:** T8, C1, D2.

### 8. concept
- **Purpose:** one mental model before details.
- **Asserts:** how the parts relate, in at most 15 words.
- **Anatomy:** at most 3 tiers or zones, one focal element, greyscale structure, colour only on the
  entities the claim names (C5), live text.
- **Budget (D2):** `words_max=15`; `min_pt=18`
- **Not when:** the model needs more than 3 zones; split into concept plus map.
- **Evidence:** good ref 28 (grey connectors, colour on three marks and one hexagon) though its title sits
  off-canvas at y=576.
- **Checks:** C5, V2, V4, D2.

### 9. map
- **Purpose:** locate the subject in the whole platform or process.
- **Asserts:** where the highlighted part sits and what it feeds.
- **Anatomy:** at most 12 boxes, flow in reading direction, outcomes as the largest text, exactly one
  highlighted zone (`.hl`) found within 1 s on a 25% thumbnail.
- **Budget (D2):** `words_max=30`; `min_pt=16`; `boxes_max=12`; `highlights=1`
- **Not when:** every box matters equally; that is an inventory for the appendix.
- **Evidence:** good ref 29 (one focus tile, but a 2 px outline is too subtle); anti ref 6 (22 logos, 96
  words at 7-8 pt, outcomes smallest), ref 7 (25 images), own 8-9 (labels at 7.8-8.8 px).
- **Checks:** V6, N5, C5, Y1.

### 10. zoom
- **Purpose:** expand one element of the map without losing orientation.
- **Asserts:** what is inside the highlighted part.
- **Anatomy:** the map layout repeated with 0 pt title drift; context dimmed to about 2:1 with the `dim`
  token, active text at least 7:1, revealed content at least as large as the repeated context.
- **Budget (D2):** `words_max=20`; `min_pt=14`
- **Not when:** the layout changes; a redraw in another style makes the audience re-learn the picture (N5).
- **Evidence:** good ref 30 (#3F5866 on #002134 at 2.21:1, active white 16.57:1, title pixel-locked to 29);
  anti the same slide reveals its parts at 14 pt under a 32 pt repeated header.
- **Checks:** C6, N5, K3.

### 11. hub
- **Purpose:** name the N spokes before the deep dives.
- **Asserts:** the set and one differentiator per item.
- **Anatomy:** 3 cards of 280 pt (4 columns each) or 4 of 204 pt (3 columns), sized to content; names and
  icons rendered from `plan.lists` verbatim; card name at the `card_heading` size (27 pt / 36 px: above
  body, under the title by 1.3x; ref 45 sets 28 pt names over 20 pt) and the emphasis weight; optional
  progress strip.
- **Budget (D2):** `words_max=45`; `min_pt=20`; `cards=3..4`
- **Not when:** more than 4 items; group them or move the tail to the appendix (N9).
- **Evidence:** good ref 45 (about 40 words at 20 pt or more); anti the same slide leaves about 58 pt empty
  under each card, own 24 leaves about 200 px dead gap per equal-height card.
- **Checks:** N7, N13, G5, C7, D2, Y1 (levels).

### 12. feature-hero
- **Purpose:** one feature, one benefit.
- **Asserts:** the outcome the feature produces.
- **Anatomy:** a hero third (icon plus one number or outcome) and two thirds of up to 3 icon rows; the hero
  number follows T7 (base and method stated).
- **Budget (D2):** `words_max=45`; `min_pt=18`
- **Not when:** two features share the slide; or the rows are cloned from a sibling (T11).
- **Evidence:** ref 10 (right anatomy; an open padlock on a security claim, gradient emphasis at about
  3.0-3.3:1, three bullets cloned from 9).
- **Checks:** V1, Y5, T7, T11.

### 13. feature-shot
- **Purpose:** claim plus visual proof.
- **Asserts:** the result the screenshot shows.
- **Anatomy:** 40/60 split: text in 5 grid columns (356 pt, share 0.40), screenshot in 7 (508 pt) aligned
  with the text zone within 2 pt; 3-4 items of "accent lead + plain qualifier"; one highlight on the shot.
- **Budget (D2):** `words_max=40`; `min_pt=18`; `items_max=4`; `shot_eff_min_pt=9`
- **Not when:** the shot is a full window; crop first (`screenshots-and-devices.md` §1).
- **Evidence:** good ref 48 and 50 text (34-38 words at 17-18 pt), 39 highlight, 41 input plus output, 42
  crop; anti ref 48 dot rail on unordered benefits, framed shots at about 60% width render UI at 4-5 pt.
- **Checks:** G6, S1, S3, S5, V1, D2.

### 14. equation
- **Purpose:** show complementarity (A + B = outcome).
- **Asserts:** the result needs both inputs.
- **Anatomy:** two equal shapes, an operator, a result band visibly traced to both inputs.
- **Budget (D2):** `words_max=30`; `min_pt=14`
- **Not when:** the result comes from one input; that is a from-to.
- **Evidence:** good ref 52 ("+" chips and a bracket); anti ref 12 (a result bar linked to neither input).
- **Checks:** V2, V3.

### 15. worked-example
- **Purpose:** teach an API or a feature by example.
- **Asserts:** this input becomes that output with one line.
- **Anatomy:** input table, one code line at the hero code size (24 pt), output table; sample data the
  audience already knows.
- **Budget (D2):** `words_max=60`; `min_pt=18`; `code_hero_pt=24`
- **Not when:** the code needs more than one line; use code-step slides.
- **Evidence:** good ref 17 (colour only on namespace and method); anti 17 and 18 use two mono faces.
- **Checks:** V7, Y2.

### 16. code-step
- **Purpose:** one configuration step.
- **Asserts:** the step and why it matters.
- **Anatomy:** a claim bullet at 18 pt or more, an indented mono line at the code size, straight quotes.
- **Budget (D2):** `words_max=40`; `min_pt=18`
- **Not when:** a runbook of many steps; that is the reading `setup-step` in the appendix.
- **Evidence:** good ref 26 and 27; anti ref 26 curly quotes that break copy-paste.
- **Checks:** V7 (curly quotes are критично), D2.

### 17. annotated-shot
- **Purpose:** point at the evidence inside a UI.
- **Asserts:** the one region that proves the claim.
- **Anatomy:** a crop at UI boundaries; one highlight (stroke at least 3 pt in a colour used nowhere else,
  10-25% of the image); at most 3 callouts at 18 pt or more; number badges map bullets to regions.
- **Budget (D2):** `words_max=30`; `min_pt=18`; `callouts_max=3`
- **Not when:** the highlight would cover most of the image; crop tighter instead.
- **Evidence:** good ref 39 (a box over about 25% of the image), 27 (one outline plus 3 arrows); anti ref 37
  (a 20x25 pt box on a 540 pt image).
- **Checks:** S1, S3, S4, S5.

### 18. concept-demo
- **Purpose:** the mental model for the next demo.
- **Asserts:** inputs, transform, outputs.
- **Anatomy:** three zones on one axis, one focal element, live text (never a picture of words).
- **Budget (D2):** `words_max=15`; `min_pt=14`
- **Not when:** the demo needs no model; go straight to the demo divider.
- **Evidence:** ref 23 has the right structure but 0 live words (raster), then 24 proves it (good pair).
- **Checks:** V4, N11.

### 19. photo
- **Purpose:** switch from the abstract to a scenario.
- **Asserts:** the situation the next slides address.
- **Anatomy:** one full-bleed photo; a caption of at most 6 words on a band that keeps 4.5:1 at the worst
  pixel (a black band of at least 54% over pure white, computed); in a dark section a dark-toned photo or a
  30-40% scrim (C4).
- **Budget (D2):** `words_max=6`; `min_pt=mode`
- **Not when:** the photo is decoration; cut it.
- **Evidence:** anti ref 31 (bright photo between navy slides, no caption).
- **Checks:** S6, C1, C4.

### 20. demo-divider
- **Purpose:** the demo entrance.
- **Asserts:** the outcome to watch for, in at most 5 words.
- **Anatomy:** title at the divider size, the deck demo marker (`.demo-pill`), the icon or colour of the
  concept's focal element or the map highlight, carried over (L05, N5; `proof_of` names the concept; HTML
  icon in `visual-system.md` §9); the time box lives in `plan.slides[].demo.minutes`.
- **Budget (D2):** `words_max=8`; `min_pt=mode`; `title_words_max=5`; `title_min_pt=48`
- **Not when:** never replace it with a "Demo:" prefix on a content title.
- **Evidence:** good ref 32 (never reused for later demos); anti a "Demo:" prefix eats about 40% of the
  titles on ref 19, 20, 24.
- **Checks:** N5, N6, T1, S6.

### 21. demo-still
- **Purpose:** the PDF record of a demo.
- **Asserts:** the result the demo produced.
- **Anatomy:** the result moment, a visible title or a caption of at most 10 words, the demo marker, one
  highlight, an 18 pt "what to notice" line, a scrubbed capture.
- **Budget (D2):** `words_max=20`; `min_pt=18`; `caption_words_max=10`; `shot_eff_min_pt=9`
- **Not when:** the capture shows setup or an empty state; re-capture at the result (S2).
- **Evidence:** closest ref 49 (zoomed capture, title hidden behind the image) and 24 (staged heading);
  anti ref 19 and 21 (setup frames, near-identical), 22 (empty editor), 47 (untitled).
- **Checks:** S1-S6, V4 exempt.

### 22. demo-recap
- **Purpose:** the demo exit and the low-density bridge back.
- **Asserts:** what was just shown, as up to 3 numbered steps or one outcome sentence.
- **Anatomy:** numbered steps reusing the demo still's badges, or one sentence at body size.
- **Budget (D2):** `words_max=25`; `min_pt=18`; `steps_max=3`
- **Not when:** never skipped; two demos without an exit between break N6.
- **Evidence:** absent in ref (31-33 enter without an exit; 47, 49, 51 run straight into the close). The
  catalog's 40 words were unmeasured and are cut to the L08 bridge of 25.
- **Checks:** N6, N8, D2.

### 23. series-item
- **Purpose:** one spoke of a hub.
- **Asserts:** the per-item claim, not the series name.
- **Anatomy:** the series label as a 12-16 pt eyebrow (T4), the claim as title, a frame locked to its
  siblings (title, item count, body size, media box within 2 pt), a progress strip from `plan.lists`.
- **Budget (D2):** `words_max=40`; `min_pt=mode`
- **Not when:** a talk already shows 2 spokes; the rest go to the appendix (N9).
- **Evidence:** good ref 37-42 share claim and body anchors, 48 and 50 share baselines; anti the series
  label at 36 pt over a 16 pt teal claim (2.09:1), body 14 vs 16 pt, 4 items vs 3, image edges spread 26
  and 56 pt.
- **Checks:** K3, N7, N9, T4.

### 24. ref-table
- **Purpose:** identifiers and defaults the audience needs to see once.
- **Asserts:** the count and what it covers (title states the count).
- **Anatomy:** mono names at the code size, sans descriptions at body size, one header fill at 4.5:1 or
  more, dark rows on dark slides.
- **Budget (D2):** `words_max=mode`; `min_pt=18`; `rows_max=8`
- **Not when:** more than 8 rows on stage; the full table goes to the appendix.
- **Evidence:** ref 18 (structure right; white on #00B0F0 header at 2.48:1).
- **Checks:** C2, V7, D2.

### 25. compare-table
- **Purpose:** a division of labour or a choice.
- **Asserts:** the "why" answer, written as the title.
- **Anatomy:** at most 6 rows by 3 columns, cells at 14 pt or more, repeated cell prefixes moved into
  column subheads.
- **Budget (D2):** `words_max=60`; `min_pt=14`; `rows_max=6`; `cols_max=3`
- **Not when:** the table is the reference itself; ship it in the appendix as is.
- **Evidence:** anti ref 14 (9 rows of 9 pt cells, two prefixes repeated about 13 times, 255 words, the
  answer in a 14 pt side box).
- **Checks:** D3, C2, T2.

### 26. close
- **Purpose:** what stays on screen during Q&A and the last page of the main flow (in `talk+appendix` the
  appendix follows).
- **Asserts:** one takeaway sentence (the title), a recap with route or hub names verbatim, one next step.
- **Anatomy:** takeaway title, recap line rendered from `plan.parts` or `plan.lists`, next step, optional
  metaphor drawn with "+" and a bracket; stays in the content family (C4).
- **Budget (D2):** `words_max=35`; `min_pt=16`
- **Not when:** the talk needs a call to action with a link; add a `cta` or put the URL pill here (N10).
- **Evidence:** ref 52 measures 32 words with drawn relationships (good) but has no takeaway or next step;
  own 33 closes on a one-sentence summary card (good reading close).
- **Checks:** N10, N13, V2, D2.

### 27. cta
- **Purpose:** what to do next.
- **Asserts:** one action and where to do it.
- **Anatomy:** one URL of at most 25 characters in a filled pill of at least 18 pt, optional QR and contact.
- **Budget (D2):** `words_max=20`; `min_pt=mode`; `url_chars_max=25`; `pill_min_pt=18`
- **Not when:** links are scattered and underlined across body slides; collect them here first.
- **Evidence:** ref 44 carries the deck's only URL pill, mid-deck; ref 14 carries five underlined 9 pt links.
- **Checks:** N10.

## §R. Reading archetypes

Modelled on the own deck, which is a reading deck (median 226 words). All share
`words_max=180`; `min_pt=11` (reading body 15 pt / 20 px in the token sheet). **Split rule:** above 180 words
split by claim into two slides of the same archetype, or move rows to the appendix; never shrink type.
On a talk main flow any of these is a D2 finding.

### R1. kpi-wall
- Stat tiles (`.stat > .v .l .m`), a headline row on the dark variant, and a note that says how each
  number was measured (T7). Evidence: own 4 (3 rows of 4 tiles, good, with the method note).
- **Budget (D2):** `words_max=180`; `min_pt=11`

### R2. trap-card
- A trap with a mandatory «Симптом:» line naming what the reader will observe; the symptom line keeps
  4.5:1 or more (the own deck sets its red symptom lines at 3.19:1). Evidence: own 11-18 side cards.
- **Budget (D2):** `words_max=180`; `min_pt=11`

### R3. setup-step
- Step number as «N / M» in sentence case (Y6), title, a copyable terminal (`.term > pre` + `button.copy`)
  with no horizontal overflow, side cards for the explainer and the trap. Evidence: own 11-18 (the uppercase
  eyebrow reads «КРОК 2 3 7», commands clipped by 117-234 px).
- **Budget (D2):** `words_max=180`; `min_pt=11`

### R4. glossary
- Three columns: term, what it really is, why it matters; zebra rows with a 1.15:1 step (C7). Evidence: own 7.
- **Budget (D2):** `words_max=180`; `min_pt=11`

### R5. matrix
- Layer, tool (Latin, running font, not mono: T9), required pill, does and does not. Evidence: own 10
  (pills wrap there: keep pills on one line, H7).
- **Budget (D2):** `words_max=180`; `min_pt=11`

### R6. error-log
- Columns symptom, reality, rule, at the reading body size. Evidence: own 28 (7 rows x 3 columns, 313
  words: split by claim).
- **Budget (D2):** `words_max=180`; `min_pt=11`

### R7. risks
- Each risk titled with the audience's own objection in quotes, then the answer. Evidence: own 31 (8 risk
  cards, 347 words: split into two slides of 4).
- **Budget (D2):** `words_max=180`; `min_pt=11`

### R8. summary-card
- One-sentence summary of the deck plus a links table; the reading counterpart of `close`. Evidence: own 33.
- **Budget (D2):** `words_max=180`; `min_pt=11`

## Either mode

### appendix-divider
- Marks the start of the appendix (N1: appendix slides only after it); same style as `divider`, at most 6
  words, a theme switch point. Everything behind it is judged with reading budgets.
- **Budget (D2):** `words_max=8`; `min_pt=mode`; `title_words_max=6`

## §A. Anti-archetypes on stage

| Seen | Evidence | Replace with |
|---|---|---|
| Capability inventory at about 10 pt | ref 13, 165 words | `hub` plus the inventory as `ref-table` in the appendix |
| Raster text slide | ref 16, about 170 words baked into an image, title at y=553.1 | `map` or `concept` in live text (V4) |
| Untitled full-window screenshot | ref 11, 33, 43, 47 | `demo-still` or `annotated-shot` with a title (S6) |
| Empty-state demo poster | ref 22, 44 | `demo-still` at the result moment (S2) |
| Tilted 3D logo wall | ref 26 | `map` with at most 12 flat, restyled logos (V5, V6) |

## §C. Density calibration

The D2 defaults come from the reference's most legible slides (L50): thesis 21 words (ref 2), from-to about
40 (ref 5), feature lists 34-38 at 17-18 pt (ref 48, 50), hub about 40 at 20 pt or more (ref 45), close 32
(ref 52). Thresholds round them to `thesis 25`, `from-to 40`, `feature-shot 40`, `hub 45`, `close 35`.
Two values were set by contract rather than measured: `demo-recap` 25 (the L08 bridge after a silent
still) and `feature-shot` `min_pt=18` (the L01 body size, so D2 and Y1 never disagree). Densities that
fail in both directions: ref 11-14 run 0, 48, 165, 255 words (N8 whiplash); own deck runs a uniform 226
(D1 in both modes). These are house conventions calibrated on measured slides, not cognitive laws.
