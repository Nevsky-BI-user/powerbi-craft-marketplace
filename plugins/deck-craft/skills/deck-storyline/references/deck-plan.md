# deck-storyline: deck-plan.json reference

> The storyboard as data. One file, `deck-plan.json` (schema id `deck-plan/1`), is read by `slide-design`
> (one archetype per slide), `html-deck` (`scaffold_deck.py`, `script#deck-data`, `[data-list]` rendering)
> and `deck-review` (`deck_lint.py --plan-only`, and the `--plan` input of every lint run). A complete
> passing sample is `assets/deck-plan.example.json`. Check IDs point to `deck-review` references/rubric.md,
> which owns every number; this file owns field names and meaning only. Lessons: L01-L11, L62, L72.

## §1. Shape at a glance

```json
{
  "schema": "deck-plan/1", "title": "...", "lang": "uk", "mode": "talk+appendix",
  "minutes": 20, "qa_minutes": 3, "canvas": "1280x720px", "engine": "html", "dash_policy": "hyphen",
  "audience": "...", "decision": "...", "promise": "...", "context": "...",
  "parts": [{"id": "risk", "title": "Ризики сьогодні", "question": "Чому таблиця паролів небезпечна?"}],
  "lists": {"steps": [{"id": "inventory", "label": "Інвентаризація", "icon": "list-check"}]},
  "slides": [{"n": 1, "id": "title", "archetype": "title", "part": null, "title": "...", "minutes": 0.5}],
  "close": {"takeaway": "...", "recap": ["Ризики сьогодні"], "next_step": "...", "url": "example.org/x"},
  "approval": {"version": 1, "status": "draft", "verdict": null, "date": null}
}
```

## §2. Deck-level fields

| Field | Type | Required | Meaning | Checks |
|---|---|---|---|---|
| `schema` | `"deck-plan/1"` | yes | contract version | |
| `title` | string | yes | deck title, also the HTML `<title>` | |
| `lang` | `uk` or `en` | yes | language of slide text; selects the T1 verb heuristic; the T3 budget follows the script of each title (§8) | T1 |
| `mode` | `talk`, `reading`, `talk+appendix` | yes | budgets for words and sizes; appendix slides of `talk+appendix` are judged as reading | N1 |
| `minutes` | number | talk modes | duration of the slot in minutes, Q&A included | N2, N12 |
| `qa_minutes` | number | no (0) | minutes reserved for questions | N12 |
| `canvas` | `1280x720px` or `960x540pt` | yes | HTML canvas or pptx/PDF page; 1 pt = 4/3 px | |
| `engine` | `html`, `pptx`, `slides-artifact` | yes | who builds it: `html-deck`, the `pptx` skill, or the claude.ai Slides artifact type | |
| `dash_policy` | `hyphen` or `en-dash` | yes | range form on slides; `hyphen` when the project bans dashes | T10 |
| `audience` | string | yes | who is in the room, one line | |
| `decision` | string or null | yes | the decision the talk serves (`data-storytelling` reference.md §1); null makes it a lecture, say so | |
| `promise` | string | talk modes | what the audience can do or decide afterwards; the title-slide subtitle | N3 |
| `context` | string | talk modes | the context line of the title slide (N3 `context_pt`): event, month, version | N3 |
| `families` | `{light, dark}` | no | role of each template family, at most 2 (K2) | K2 |
| `parts` | array | yes | §3 | N2, N13 |
| `lists` | object | no (`{}`) | §3 | N7, N13 |
| `slides` | array | yes | §4 | all |
| `close` | object | talk modes | §5 | N10 |
| `approval` | object | yes | §5 | |
| `inferred` | boolean | no (false) | true when `deck-review` reconstructed the plan from a finished deck (§10) | |

## §3. Parts and canonical lists

`parts` are the route, in order: `{id, title, question}`. `id` is a slug. `title` is the short label used on the
route slide, in eyebrows and in the close recap. `question` is the divider title of that part (a topic or
question within T1 `divider_words_max`). The part number n/N is generated, never stored.

`lists` holds every canonical list once (L62): `{"<name>": [{"id", "label", "icon"}]}` in display order.
`label` is the exact on-slide text; `icon` names an entry of the token sheet icon map (`slide-design`, V1) or is
null. Hub cards, spoke eyebrows, progress strips and recap lines are rendered from here (`html-deck`
`[data-list]`); a hand-typed copy is an N13 finding.

## §4. Slide fields

| Field | Type | Required | Meaning | Checks |
|---|---|---|---|---|
| `n` | integer | yes | 1-based position; must equal the array index + 1 | §7 |
| `id` | slug | yes | unique, `[a-z0-9][a-z0-9-]*`; becomes `section.slide#id` in HTML | |
| `archetype` | enum (§6) | yes | anatomy and budget owner (`slide-design`); class `.a-<id>` in HTML | D2 |
| `title` | string | yes | on-slide title; the caption for `photo` | T1, T3, T9, T10, T11 |
| `claim` | string | no | the full sentence the slide proves when the title is its shortened form; `claim-auditor` reads it | T1 |
| `title_verified` | `claim-auditor` or `manual` | no | a T1 verb suspect that `claim-auditor` (or, when it is unavailable, the manual Title test) passed as an assertion; T1 then skips only its verb test on this slide, never the divider word caps, and on a built deck only while the title still equals the plan title. Set it after that verdict, never to quiet the lint | T1 |
| `part` | part id or null | content slides | the part this slide belongs to; null for title, route, close and appendix | N2 |
| `eyebrow` | string or null | no | small line above the title: «Частина · кут» or «n / N · пункт» | T4, N13 |
| `dek` | string or null | no | one line under the title; on the title slide it carries the promise | N3 |
| `list` | list name or null | hub, route | the canonical list this slide renders | N7, N13 |
| `series` | `{list, item}` or null | series-item | which list and which item id this spoke shows | N7, N9, N13 |
| `proof_of` | slide id or null | proofs | the concept this slide proves; slides between concept and proof carry the same value | N11 |
| `pair` | `{id, role}` or null | bookends | `role` is `before`, `bridge` or `after`; both ends use one archetype | N4 |
| `demo` | `{id, role, minutes}` or null | demos | `role` is `entrance` (`demo-divider`), `proof` (`demo-still`) or `exit` (`demo-recap`); `minutes` on the entrance is the time box | N6, N12 |
| `appendix` | boolean | no (false) | true for every slide after the appendix divider | N1 |
| `minutes` | number | talk main flow | planned minutes on this slide; a demo entrance includes the live demo | N12 |
| `notes` | string | no | speaker notes: cue, script points, numbers with their base, transition, cumulative minute mark, backup answer (`references/demos-and-notes.md` §5; prose style: `plain-report`) | H6 |
| `media` | array | screenshots | `[{file, native_px, ui_px, placed_pt}]`: capture width, UI text px in the capture, placed width on the 960 pt page; feeds S1 on the PDF path | S1 |
| `status` | `{state, as_of}` or null | feature slides | `state` is `ga`, `preview` or `planned`; `as_of` is `YYYY-MM` | V8 |
| `shape` | boolean | no (false) | the slide uses a shape-as-hero figure; its inner labels are exempt from the Y1 floor | D4, Y1 |

Optional fields may be omitted instead of set to null. A titles-only draft (pre-flight step 5) needs only
`n`, `id`, `archetype`, `title`, `part` and, for talk modes, `minutes`; the structural fields (`list`, `series`,
`pair`, `demo`, `proof_of` and `appendix`) are what make N checks possible, so fill them before approval.
Without `appendix: true` on the slides after the `appendix-divider` they count as main flow, and N1, N9,
N10 or N12 fail on a plan that only lacks the flag.

## §5. Close and approval

`close` = `{takeaway, recap, next_step, url}`. `takeaway` is one sentence and usually the close slide title.
`recap` repeats part titles or list labels verbatim. `next_step` is one action, with a short URL, QR or contact
(L10). `url` is optional, within N10 `url_chars_max`, shown in a pill on the close or cta slide; full links go on
the close or in the appendix, and the notes may repeat them but never hold the only copy (H4).

`approval` = `{version, status, verdict, date}` with `status` in `draft`, `changes`, `approved`. The verdict
grammar is reused from `pbi-redesign-approval`; the plan itself is the record, there is no second ledger:

- «затверджую сторіборд vN» sets `status: approved`, `version: N`, `verdict` to that line, `date` to today.
- «правки сторіборду vN: ...» sets `status: changes` and keeps the comment in `verdict`; apply the edits as
  version N+1 with `status: draft`, rerun `--plan-only`, and stop again.

`scaffold_deck.py` warns when `status` is not `approved`; nothing past the storyboard is built before it.

## §6. Archetype enum

36 ids. The list is identical in `deck-review` references/rubric.md §13, `deck-review` scripts/thresholds.json
(`archetypes`), `slide-design` references/archetypes.md and the `<template data-archetype>` snippets of the
`html-deck` template; `selftest.py` asserts all four.

- Talk (27): `title`, `route`, `divider`, `thesis`, `journey`, `before-after`, `from-to`, `concept`, `map`,
  `zoom`, `hub`, `feature-hero`, `feature-shot`, `equation`, `worked-example`, `code-step`, `annotated-shot`,
  `concept-demo`, `photo`, `demo-divider`, `demo-still`, `demo-recap`, `series-item`, `ref-table`,
  `compare-table`, `close`, `cta`.
- Reading (8): `kpi-wall`, `trap-card`, `setup-step`, `glossary`, `matrix`, `error-log`, `risks`, `summary-card`.
- Either mode (1): `appendix-divider`.

`before-after` serves both ends of a bookend; `pair.role` tells them apart. A slide that fits no archetype is a
candidate to cut or move to the appendix (D2).

## §7. Schema rules (exit 2, no findings)

`deck_lint.py` refuses a plan that breaks the contract and prints every violation: unknown `schema`; a
missing required field for the mode; a value outside its enum; `n` out of sequence; a duplicate or malformed
`id`; a `part`, `list`, `series.item`, `proof_of`, `pair.id` or `demo.id` reference that does not resolve;
`demo.role` that does not match the archetype (entrance = `demo-divider`, proof = `demo-still`, exit =
`demo-recap`); a `pair.role` other than before, bridge, after; a `title_verified` other than `claim-auditor` or
`manual`. These are contract errors, not deck findings.

## §8. What `--plan-only` checks

Run `python3 <deck-review>/scripts/deck_lint.py --plan-only deck-plan.json` from the project folder, where
`<deck-review>` is the `deck-review` skill folder, until it exits 0 (it fails on бажано and above at this
stage). Rules on the plan, thresholds from the rubric:

| Check | Rule on the plan |
|---|---|
| N1 | appendix slides only after the `appendix-divider`, none before it |
| N2 | a `route` slide within the first `route_pos_max` slides; part count in range; the first main slide of each part is a `divider` |
| N3 | slide 1 is `title`; `promise` and `context` present |
| N4 | each pair has one before and one after with one archetype; at most `gap_max` slides between, each with role bridge |
| N5 | every `zoom` directly follows a `map` or another `zoom` |
| N6 | each demo id has one entrance, at least one proof, one exit, in that order; the entrance carries `minutes` |
| N7 | the `hub` showing a list comes before its spokes; spokes follow list order |
| N9 | at most `items_main_max` spokes per list on the talk main flow |
| N10 | the last main slide is `close` or `cta`; one-sentence takeaway; recap labels verbatim; a next step; url length |
| N11 | `proof_of` points to an earlier slide and every slide between carries the same value |
| N12 | content slides (not in the `structural` group) within the range for the available minutes; main-flow minutes plus Q&A within `minutes` |
| N13 | divider titles equal part questions; spoke eyebrows contain the item label; recap labels come from parts or lists |
| T1 | content titles contain a digit or a finite verb (heuristic, suspects go to `claim-auditor`; a slide with `title_verified` skips this test); divider and demo-divider word caps |
| T3 | content titles within the character budget (Cyrillic budget when the title has Cyrillic) |
| T9 | NBSP between a number and its unit in every on-slide string |
| T10 | no U+2013 or U+2014 in on-slide strings under `hyphen`; one range form under `en-dash` |
| T11 | no two slides share a title (a zoom may repeat its map title) |

N8 needs word counts, so it runs only on a built deck.

## §9. Modes in the plan

`talk`: every main slide is judged with talk budgets. `reading`: every slide with reading budgets, no demo or
timing checks. `talk+appendix`: main flow as talk, slides with `appendix: true` as reading; the appendix holds
reference tables, extra series items, backup screenshots and demo recap frames for the PDF reader. Converting
a reading deck to a talk: split by claim, move matrices, glossaries and runbooks behind the appendix divider,
and mark them in the plan (`references/arc-and-pacing.md` §1).

## §10. Inferred plans

A `deck-review` audit of a deck without a plan, or a teardown of someone else's deck, writes the same shape
with `"inferred": true`: archetypes, parts and pairs are guessed from the slides, `approval.status` stays
`draft`, and the report states that the plan was inferred. `--mode` on the lint command overrides `mode` when a
deck is judged against both budgets.

## §11. Strings

- Write NBSP as `\u00a0` in JSON so it stays visible in review (`за 20\u00a0хвилин`).
- Case, quotes and apostrophe follow `dashboard-copy` rule 9; numbers and dates follow `dashboard-copy`
  references/uk-formats.md.
- Product names stay Latin in the running font (T9); terms come from `dashboard-copy` glossaries.
- Under `dash_policy: hyphen` write ranges as `10-15` or «з 5 по 7»; the minus sign U+2212 is allowed.

## §12. See also

`references/arc-and-pacing.md` (arc and budgets in prose), `references/titles-and-copy.md` (title wording),
`references/demos-and-notes.md` (demo triple, notes), `slide-design` references/archetypes.md (anatomy),
`html-deck` scripts/scaffold_deck.py (plan to skeleton), `deck-review` references/rubric.md (numbers).
