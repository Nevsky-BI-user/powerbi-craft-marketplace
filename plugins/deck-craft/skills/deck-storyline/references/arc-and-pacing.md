# deck-storyline: arc and pacing reference

> Depth for the mode decision, the recommended arc, pacing, the funnel, hub and spoke, series
> reduction, bookends, concept before proof and the close. Evidence comes from a 52-slide vendor
> platform deck (960x540 pt PDF, "ref") and a 33-slide own HTML reading deck (1280x720 px canvas, "own
> deck"); lessons L01-L11 and L62. Every number belongs to `deck-review` references/rubric.md, which
> wins on conflict; this file names the check and its key instead of restating the value, except in
> worked examples, which say so. Budgets are house conventions calibrated on measured slides, not
> cognitive laws.

## §1. Modes

| | `talk` | `reading` | `talk+appendix` |
|---|---|---|---|
| Who reads it, where | a room, from a screen, while you speak | one person at a desk, at their pace | the room first, then the PDF reader |
| Words per slide | D1 talk `words_max`, `words_hard`; N1 talk `median_words_max` | D1 reading `words_max`; N1 reading `median_words_max` | talk on the main flow, reading after the `appendix-divider` |
| Smallest text | Y1 talk `body_pt`, `floor_pt`; archetype `min_pt` (§13) | Y1 reading `floor_pt` | per slide, by its side of the divider |
| Zones and tables | D1 `zones_max`; D3 stage tables | split a slide above the reading budget | stage tables on the main flow, full tables in the appendix |
| Speaker notes | carry script points, cue, numbers with base, transition and minute mark (H6) | not needed; the slide says everything | on every main slide |
| What the PDF must carry | titles that tell the story, demo stills, the close | everything | main flow plus the reference the talk left out |

Archetypes follow the mode: a reading archetype on a talk main flow is a D2 finding, and a talk
archetype placed in the appendix is judged with reading budgets (rubric §13).

**Converting a reading deck into a talk** (L01, L09):

1. Write one claim per future slide (`data-storytelling` reference.md §1, the paper storyboard).
2. Split every slide that carries more than one claim into one talk slide per claim; what remains is
   reference and becomes an appendix page.
3. Move matrices, glossaries, runbooks, error logs, parameter lists and the series items beyond N9
   `items_main_max` behind the `appendix-divider`; set `appendix: true` on each.
4. Keep the reading deck's strengths: assertion titles, part labels in the eyebrow, a route with an
   audience hint, a measurement note under proof numbers.
5. Rerun `--plan-only`; the content count now has to fit N12.

**Converting a talk into a handout**: keep the order and titles, set `mode: reading`, turn the spoken
script into visible text within the reading budget, and use the reading archetypes of `slide-design`
references/archetypes.md (§6 of `references/demos-and-notes.md`).

Evidence: ref neighbours 11-14 run 0, 48, 165, 255 words, and 14 sets 255 words at 9 pt while hub 45 holds
40 words at 20 pt or more; the own deck has a median of 226 words per slide and 97% of its words at
or below 13.6 px (about 10 pt). The two fail in opposite directions: the ref swings, the own deck is
uniformly dense.

## §2. The arc for technical and product talks

| Beat | Purpose | Main-flow slides | Plan fields | Checks |
|---|---|---|---|---|
| 1. Title | promise and context; the PDF can be placed later | 1 | `promise`, `context`, slide 1 `title` | N3 |
| 2. Hook | one concrete scenario or number with its base | 1-2 | `thesis` or `feature-hero`; `before-after` only as an adjacent pair filling both hook slides (§7) | T1, T7 |
| 3. Route | the parts, numbered, with an audience hint | 1 | `route` within `route_pos_max`, `parts` | N2 |
| 4. Part (repeat) | divider, concept, map, proof, one-sentence recap | see §3 | `part`, `proof_of`, `demo`, `list` | N2, N5, N6, N11 |
| 5. Synthesis | return to the opening model, name the items | 1 | a slide that reuses the hook's grid and title pattern, or a `hub` reprise with a new title; no `pair` across the talk | judged visually (§7) |
| 6. Close | takeaway, recap, next step | 1 | `close` | N10 |
| 7. Appendix | reference for the PDF reader | any | `appendix-divider`, `appendix: true` | N1 |

- **Parts**: N2 `parts`, with `parts_short_min` allowed under `short_minutes`. Each part opens with a
  divider whose title is the part question, at most T1 `divider_words_max` words, equal to
  `parts[].question` (N13). n/N is generated, never typed.
- **Route audience hint** pattern: «Частини I і II не потребують технічної підготовки»,
  «Код є тільки в частині III». The own deck's route slide does this well.
- **Per-part micro-arc**: divider (question) → one concept model → its place in the map → proof that
  shows the result → one-sentence recap. At most one dense slide per part (§3).
- **Appendix contents**: reference tables, parameter lists, comparison matrices, backup screenshots,
  the series items cut by N9, demo recap frames for the PDF reader.

**Slot sizes** (N12): available minutes = slot - Q&A - demo time boxes; content slides between
available / 2 and available / 1.5 (worked with the rubric `min_per_slide` at the time of writing;
`--plan-only` recomputes from the live value). Only the rubric `structural` group is extra: title,
route, dividers, demo entrances, stills and photos. `demo-recap`, `close` and every other main slide
count as content.

| Slot | Q&A | Demos | Available | Content slides |
|---|---|---|---|---|
| 10 min | 2 | none | 8 | 4-5 |
| 12 min | 2 | one of 3 min | 7 | 4 |
| 20 min | 3 | one of 3 min | 14 | 7-9 |
| 30 min | 5 | one of 5 min | 20 | 10-13 |
| 45 min | 5 | none | 40 | 20-26 |
| 45 min | 5 | two of 5 min | 30 | 15-20 |

The ref packs 52 slides into a talk slot; the evidence arc puts a 45-minute talk at about 20-25 content
slides plus dividers.

**Short slots** (N2 `short_minutes`, N12). When the N12 content count is below the number of beats,
merge beats; the route and the dividers stay, since they cost no content slide.

1. Parts drop to N2 `parts_short_min`.
2. The hook moves inside part I as its first content slide, after the divider: a `thesis` or
   `feature-hero` with its number and base. A lone `before-after` does not fit: it is one end of an N4
   pair (§7).
3. In the part with the demo, the concept sits directly before the entrance (N11, `proof_of` on the
   entrance and the stills) and the `demo-recap` is that part's recap (L06); map and zoom go to the
   appendix.
4. The synthesis folds into the close: the takeaway is the close title and the recap names the parts
   verbatim (N10, N13).

Worked example, the 12-minute row: title · route · divider I · `thesis` (the hook, all of part I) ·
divider II · `concept` · `demo-divider` · `demo-still` · `demo-recap` · `close`. Four content slides;
the plan minutes 0.5, 0.5, 0.25, 1.5, 0.25, 1.5, 3, 0.5, 1, 1 plus 2 of Q&A fill the 12 minutes and pass
`--plan-only`.

## §3. Pacing

- **Minutes per slide**: plan `minutes` on every main slide; a demo entrance carries the whole time
  box. The sum plus `qa_minutes` stays within `minutes` (N12).
- **Neighbour density** (N8, L08): neighbouring main slides stay within `ratio_max` of each other's
  words; dividers are exempt. After a silent run (demo stills, photos), re-enter through a bridge of at
  most `bridge_words` (a `demo-recap` or a `concept`), never straight into a dense slide. Evidence: ref
  28-33 total 58 words over six slides, then 34-36 total 357 over three.
- **One change per step** (`data-storytelling` reference.md §5): from one slide to the next, change the
  period, the measure, the entity or the grain, not two at once.
- **Theme switches only at dividers** (`slide-design` C4): plan the dark and light families by part
  (`families`), so the switch points are dividers.
- **Dense slides**: above D1 talk `words_max`, or an archetype budgeted above it (`worked-example`,
  `compare-table`). At most one per part on the main flow; a second one goes to the appendix. This
  comes from the evidence arc behind §2; no check enforces it.

## §4. Funnel and zoom (L05, N5)

Concept model → the full map with one highlighted element → a `zoom` that repeats the map layout with
title drift within N5 `drift_pt` → a `demo-divider` that reuses the highlighted element's icon or colour.
In the plan: `concept`, then `map`, then `zoom` (directly after the map or another zoom), then the demo
entrance, with `proof_of` on the slides that prove the concept. A second view zooms into the first; it
never redraws the same thing in another style.

Evidence: ref 28, 29, 30, 32 form the best funnel in the deck, with the title at the same x and y on the
map and the zoom. The counter-example is 6 and 7: one platform drawn twice in two styles, 163 words and
47 images; 15 and 16 repeat the mistake.

## §5. Hub and spoke (L07, L62, N7, N13)

- The hub comes before the spokes it indexes; spokes follow its order.
- Names, order and icons live once in `plan.lists` and are rendered from there (`html-deck`
  `[data-list]`); a hand-typed copy is an N13 finding.
- Spoke eyebrow: «2 / 3 · Перенесення» (item label verbatim, n / N written with spaces, Y6-safe).
- A progress strip marking the current item is a house convention for orientation. No measured gain is
  claimed: `data-storytelling` reference.md §12 records that stepper vs scroller showed no engagement
  effect and that the progress-bar preference rests on 3 readers in an 8-person pilot.
- Evidence: the ref overview 34 arrives after a demo; index 36 lists items in the reverse order of 37-42
  and renames one; a preview at 44 precedes the hub at 45; the workload list differs on 29, 36 and
  37-42.

## §6. Series reduction (L09, N9)

In a talk an N-item series shows the hub plus at most N9 `items_main_max` items on the main flow: the
most differentiated ones, or one live demo. Capabilities the items share are stated once, on the hub.
The remaining items become appendix one-pagers in the same locked frame (`slide-design` K3), still
rendered from `plan.lists`. Evidence: ref 36-42 run seven slides of one rhythm; one claim repeats on 4
of the 6 deep dives and a 13-word bullet is duplicated on one of them (T11).

## §7. Bookends (L04, N4)

A before/after pair uses one archetype, `before-after`, with `pair.role` set to `before` and `after`
and the same `pair.id`; the title pattern matches («Сьогодні ...» / «Через місяць ...»). Nothing goes
between them except at most N4 `gap_max` slides with role `bridge`. A talk-level bookend (synthesis
returns to the hook) is judged visually and never declared as a `pair`, since N4 would fail on the
slides between the ends. Evidence: ref 4 and 6 share a title pattern but 5 interrupts
and 6 changes layout; 28 and 52 bookend the talk with the same three elements (good).

## §8. Concept before proof (L11, N11)

Each proof (demo, screenshot, worked example) sits directly after the concept it explains, with
`proof_of` pointing back to the concept slide id; every slide between them carries the same
`proof_of` (the demo entrance does). A proof without its concept is noise; a concept without proof is a
claim. Evidence: ref 23 then 24 (good); the catalog screenshot 11 follows the security slide 10, two
slides after its concept 9; a bullet on 37 names a feature explained only on 46.

## §9. The close (L10, N10)

- **Takeaway**: one sentence, usually the close title, within the T3 budget.
- **Recap**: the route parts or hub items, verbatim from `parts[].title` or `lists` labels (N13), in
  the route order. A new triad at the end breaks the promise of the route.
- **Next step**: one action («Затвердити пілот до 1 листопада») plus a short URL in a pill (N10
  `url_chars_max`, `pill_min_pt`), a QR code that was scanned once with a phone before the talk, or a
  contact (L10).
- **Links**: collected here or in the appendix, never only in the notes (print hides them, H4); none
  underlined in body text on other slides.
- **Q&A**: the close stays on screen during questions and is the last page of the main flow (in
  `talk+appendix` the appendix follows), so it must stand alone.
- **Reading variant**: a one-sentence `summary-card` plus a links table.
- Evidence: the ref closes on a metaphor with no takeaway or next step and on a different triad than
  its hub; its only call to action is a URL pill on 44; 14 carries five underlined 9 pt links. The own
  deck closes with a one-sentence summary card and a links table, a good reading close.

## §10. Where decks sag

| Sag (ref slides) | What happened | Check that catches it | Fix |
|---|---|---|---|
| 12-14 | three reference slides in a row, 48, 165, 255 words; claims in a footer caption and a why-box | N8, D1, T2 | split by claim, table to the appendix, promote the claim |
| 18-22 | a reference table, then four setup-frame demo posters; a PDF reader learns nothing | N6, S2 | one demo triple with a result still |
| 25-27 | a part ends on parameters and configuration, no takeaway | none automatic; arc beat 4 recap, judged on the plan | a one-sentence recap; parameters to the appendix |
| 36-42 | seven slides of one rhythm, one claim repeated | N9, T11, K3 | hub plus 1-2 items |
| 43-44 | an untitled screenshot, then a preview before its hub | S6, N7 | caption the still; hub first |
| 52 | the talk ends on a diagram with no ask | N10 | takeaway, recap, next step |
| own deck | every slide above even the reading budget, shown to a room | N1, D1 | `talk+appendix`, split by claim |

## §11. Contested: do not reintroduce

| Claim | Why excluded | What this skill says instead |
|---|---|---|
| "10/20/30" or "6x6" as laws | no evidence in this analysis; slogans, not measurements | mode budgets from the rubric, calibrated on measured slides |
| "7±2 items per slide" | `data-storytelling` reference.md §12 | budget words and zones (D1), not item counts |
| "Every slide needs a visual" | a one-sentence statement slide is legitimate in a talk; settled in `slide-design` | archetype by purpose (D2) |
| "One minute per slide" | not in the evidence; the evidence arc budgets 1.5-2 min per content slide (§2) | N12 |
| "A progress bar improves engagement" | `data-storytelling` reference.md §12 | progress strip as orientation only (§5) |

## §12. See also

`references/titles-and-copy.md` (wording) · `references/demos-and-notes.md` (demos, notes, rehearsal)
· `references/deck-plan.md` (fields) · `deck-review` references/rubric.md §2 and §13 (numbers) ·
`slide-design` references/archetypes.md (anatomy) · `data-storytelling` reference.md §1, §5, §12.
