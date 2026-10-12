# deck-review: rubric

> Single source of every deck threshold. Each check has an ID, a rule, thresholds per mode, how it is
> measured, a severity, the lesson it comes from and the skill that owns the fix. Numbers are mirrored in
> `scripts/thresholds.json`; `scripts/selftest.py` asserts that every table cell below equals that file, so
> change both in one commit. Evidence: a 52-slide vendor platform deck (960x540 pt PDF, "ref") and a 33-slide
> own HTML reading deck (1280x720 px canvas, "own deck"); lessons L01-L79 live in the teardown ledger that
> `references/teardown.md` describes. Budgets are house conventions calibrated on measured slides, not
> cognitive laws. Contrast is computed with the `pbi-color-accessibility` reference.md §1 formula.

## §1. Conventions

**Units.** pt are points on a 960x540 pt page; px are design px on the 1280x720 canvas, unscaled by the
viewport. 1 pt = 4/3 px, so 18 pt = 24 px, 14 pt = 18.67 px, 11 pt = 14.67 px, 9 pt = 12 px. Threshold keys
ending in `_pt` are pt (the judge converts HTML px with pt = px x 0.75), `_px` are canvas px, `_ms` are
milliseconds; other keys are ratios, counts, words or characters.

**Modes.** `talk` and `reading` columns hold the thresholds. A `talk+appendix` deck judges main-flow slides
with the talk column and appendix slides with the reading column. If no mode is declared, the deck is judged
as talk and N1 says so.

**Cells.** A threshold cell is a list of `key=value` items separated by "; ". `lo..hi` is an inclusive range,
`WxH` a size, `none` means the check has no numeric threshold (it still applies), `n/a` means the check does
not apply in that mode. Backticks are formatting only. These cells are parsed by `selftest.py`; keep the format.

**Measured by.** `A` automatic: a script measures and `deck_lint.py` decides. `V` visual: a reviewer decides on
the PNG and contact sheet (questions in §V). `A+V`: the script measures what it can and flags, a reviewer
confirms on the pixels or covers the part no script can see. **Auto in** lists the lint paths that run the
automatic part: `plan` (`deck_lint.py --plan-only`), `tokens` (`--tokens`), `html` (`--metrics` from
`html_deck_lint.mjs`), `pdf` (`--runs` from `pdf_text_runs.py` plus `pixels.json`).

**Severity.** критично: the audience cannot read it, it is wrong, it leaks, or it breaks in the PDF (below a
floor, failing contrast, overflow or clipping, off-canvas or hidden title, raster-only words, unscrubbed
identity, untitled slide, visible duplicate, viewport or print failure, a leftover `data-todo`). бажано:
structure and consistency. косметика: polish. A severity cell may name the condition that changes it.

**Fix owner.** The skill whose rules the fix follows: `deck-storyline` (what the deck says and in what order),
`slide-design` (everything visible), `html-deck` (the HTML engine), `deck-review` (copy proofreading and the
review itself). Scripts that enforce a rule cite its check ID and never restate its numbers.

**Measurement parameters** (not design rules; they tell the scripts how to see; only the geometry heuristics
that read text boxes, such as glyph boxes, line joining and centring, stay inside the scripts):

| Parameter | Value | Meaning |
|---|---|---|
| `tol_pt` | 0.5 | position and size comparisons where the rule says 0 (N5); below this the difference is rounding |
| `nonint_tol_pt` | 0.05 | a size counts as whole pt within this distance (Y2) |
| `scale_tol_pt` | 0.4 | HTML: a size counts as on the declared type scale within this distance (Y2) |
| `silent_words_max` | 5 | a slide with this many live words or fewer is silent (evidence: 11 near-silent slides) |
| `title_zone_top` | 0.3 | PDF: the title is the largest run whose baseline lies in the top 30% of the page |
| `pn_max_pt` | 12 | PDF: page-number candidates are digit-only runs at or below this size |
| `dark_bg_max` | 0.2 | a background colour below this relative luminance is dark: G7 judges strokes only there, a `#000000` run there goes to C3 could-not-verify (L78) |
| `lum_dark_max` | 0.35 | pixels: mean relative luminance at or below this is a dark slide (C4); plan convention: of the 5 flips the eye sees in the ref 27-33 run these classes catch 2 (27 is mid at 0.44, the photo 31 dark at 0.27) |
| `lum_light_min` | 0.6 | pixels: mean relative luminance at or above this is a light slide (C4) |
| `dup_hamming_max` | 6 | pixels: 64-bit dHash distance at or below this is a near-duplicate pair (T11) |
| `per_sheet` | 30 | pixels: slides per contact sheet |
| `ring_px` | 2 | pixels: width of the ring sampled around a PDF run for its background (C1) |

**Archetype groups** used by several checks (ids from §13):

| Group | Archetypes | Used by |
|---|---|---|
| `dividers` | title, divider, demo-divider, appendix-divider | C4 switch points, N8 and K1 exemptions, T3 one-line exemption |
| `structural` | title, divider, demo-divider, appendix-divider, route, demo-still, photo | not counted as content slides in N12 |
| `title_exempt` | title, divider, demo-divider, appendix-divider, route, photo, cta | T1 and T6 skip these titles |
| `title_box_exempt` | title, divider, demo-divider, appendix-divider, photo | G1 and K3 skip these slides |
| `raster_exempt` | title, divider, demo-divider, appendix-divider, photo, demo-still, annotated-shot | V4 raster suspicion skips these |

## §2. N: narrative

Owner `deck-storyline`. Most N checks run on the plan alone (`--plan-only`), before any slide exists.

| ID | Check | Talk | Reading | By | Auto in | Severity | Lesson | Fix owner |
|---|---|---|---|---|---|---|---|---|
| N1 | **Mode and budgets.** Mode declared (talk, reading, talk+appendix) and the main-flow median words within the mode budget; appendix slides only after the appendix divider. | `median_words_max=50` | `median_words_max=180` | A | plan, html, pdf | бажано | L01 | `deck-storyline` |
| N2 | **Route and dividers.** Route slide right after the title (a hook may come first); 3-5 numbered parts; every part opens with a divider of one style showing n/N. | `route_pos_max=4`; `parts=3..5`; `short_minutes=15`; `parts_short_min=2` | `route_pos_max=4` | A+V | plan, html, pdf | бажано | L02 | `deck-storyline` |
| N3 | **Title promise and context.** Title slide states a promise (what the audience can do or decide) and a 14-18 pt context line (date, event, version); title at least 1.5x the subtitle. | `title_ratio_min=1.5`; `context_pt=14..18` | `title_ratio_min=1.5`; `context_pt=14..18` | A+V | plan, html, pdf | бажано | L03 | `deck-storyline` |
| N4 | **Before/after bookend.** A before/after pair uses one archetype and grid with a matching title pattern; at most one declared bridge slide between them. | `gap_max=1` | `gap_max=1` | A+V | plan | бажано | L04 | `deck-storyline` |
| N5 | **Funnel and zoom.** Concept, then the map with one highlight, then a zoom that repeats the map layout with 0 pt title drift, then the demo divider carrying the token; never redraw in another style. | `drift_pt=0` | `drift_pt=0` | A+V | plan, html, pdf | бажано | L05 | `deck-storyline` |
| N6 | **Demo triple.** Every demo has an entrance (demo-divider), a proof (demo-still) and an exit (demo-recap) in that order with a time box; no two demos without an exit between. | none | n/a | A+V | plan | бажано | L06 | `deck-storyline` |
| N7 | **Hub before spokes.** The hub precedes its spokes; spokes follow the hub order and reuse its labels and icons; a progress strip marks the current item. | none | none | A+V | plan, html, pdf | бажано | L07 | `deck-storyline` |
| N8 | **Neighbour density.** Neighbouring main slides stay within 2x words (dividers exempt); a pair where the larger side has at most 25 words is ignored, so a silent slide is followed by a bridge of at most 25 words. | `ratio_max=2`; `bridge_words=25` | n/a | A | html, pdf | бажано | L08 | `deck-storyline` |
| N9 | **Series reduction.** In a talk a series shows its hub plus at most 2 items on the main flow; shared capabilities are stated once and the rest go to the appendix. | `items_main_max=2` | n/a | A | plan | бажано | L09 | `deck-storyline` |
| N10 | **Close.** The close carries a one-sentence takeaway, a recap using route or hub names verbatim and one next step; a URL of at most 25 chars sits in a pill of at least 18 pt; links are collected here, none underlined in body text. | `url_chars_max=25`; `pill_min_pt=18` | none | A+V | plan, html, pdf | бажано | L10 | `deck-storyline` |
| N11 | **Concept before proof.** A proof slide follows the concept it proves; every slide between them declares the same proof_of. | none | none | A+V | plan | бажано | L11 | `deck-storyline` |
| N12 | **Slides fit the minutes.** Content slides number between (minutes - Q&A - demo minutes) / 2 and / 1.5; main-flow slide minutes plus Q&A stay within the total. | `min_per_slide=1.5..2` | n/a | A | plan | бажано (косметика: fewer slides than the lower bound) | L09 | `deck-storyline` |
| N13 | **Lists from one source.** Parts, hub items and recap labels come from plan.parts and plan.lists and are rendered from that one source; labels match verbatim, divider titles equal part questions. | none | none | A | plan, html, pdf | бажано | L62 | `deck-storyline` |

Calibration (ref = reference deck, own = own deck):

- **N1** ref median 37.5 live words (stats 39) meets the talk budget, its defect is variance (N8, D1); own deck median 226 is above even the reading budget of 180, fires in both modes.
- **N2** ref first structure signal at slide 8, dividers only on 8 and 32, five parts start cold (15, 17, 28, 34, 45); own deck route on slide 2 with an audience hint, parts named in the eyebrow, no dividers.
- **N3** ref slide 1 sets two 48 pt lines in two colours with no date or context; own deck slide 1 pairs a thesis with 4 proof numbers (no context line measured).
- **N4** ref 4 and 6 share a title pattern but 5 interrupts and 6 changes layout; the talk-level bookend 28 and 52 is good (arc beat 5, judged visually); own deck has no pair.
- **N5** ref 29 and 30 hold the title at the same x and y (good); 6 + 7 redraw one platform in two styles (163 words, 47 images), 15 + 16 likewise; own deck has no zoom pair.
- **N6** ref four demo posters back to back (19-22), 31-33 enter without an exit, raw stills 47, 49, 51 run into the close; own deck has no demo.
- **N7** ref overview 34 arrives after a demo, index 36 lists items in reverse order and renames one, preview 44 precedes hub 45; own deck not applicable.
- **N8** ref 11 to 14 run 0, 48, 160, 252 live words (stats 0, 48, 165, 255); 28-33 total 58, then 34-36 total 354 (stats 357); own deck is uniformly dense (median 226), no whiplash.
- **N9** ref 36-42 run seven slides of one rhythm with one claim repeated on 4 of 6; own deck runs 8 setup steps (11-18), acceptable in reading mode.
- **N10** ref 52 closes on a metaphor with no takeaway or next step, the only CTA is the URL pill on 44, slide 14 carries five underlined 9 pt links; own deck 33 closes with a one-sentence summary card and a links table (good reading close).
- **N11** ref 23 then 24 (good); the catalog screenshot 11 follows security slide 10, two slides after its concept 9; own deck puts maps 8-10 before the procedure (good).
- **N12** timing from the evidence arc (1.5-2 min per content slide; a 45-minute talk holds 20-25 content slides), not a ledger lesson: L09 is cited as the related series cut; ref packs 52 slides; own deck is a reading deck, not judged.
- **N13** ref the workload list differs on 29 (6 tiles), 36 (7 items) and 37-42 (order, one rename); own deck types its rail part label by hand on all 33 slides and it disagrees with the slide section (`data-sect`, shown in the bar) on 1, 8, 9, 10, 27, 28; a slide without a rail is compared on its first eyebrow segment.

## §3. T: titles and copy

Owner `deck-storyline`, except T11 (`deck-review`). Claim grammar itself belongs to `data-storytelling`; titles also go to `claim-auditor`.

| ID | Check | Talk | Reading | By | Auto in | Severity | Lesson | Fix owner |
|---|---|---|---|---|---|---|---|---|
| T1 | **Assertion titles.** Content titles are assertions (a finite verb or a number); a divider title is a topic or question of at most 6 words, a demo divider an outcome of at most 5. | `divider_words_max=6`; `demo_divider_words_max=5` | `divider_words_max=6`; `demo_divider_words_max=5` | A+V | plan, html, pdf | бажано | L12 | `deck-storyline` |
| T2 | **Strongest sentence.** The strongest sentence on the slide is its title; no claim is left in a band, subtitle, why-box, callout or footer caption. | none | none | V | none | бажано | L13 | `deck-storyline` |
| T3 | **One-line titles.** Content titles fit one line within the character budget for their size (budget = chars x at_pt / size); never autofit; no one-word last line in a title or a dek (HTML `.dek`). | `chars_latin=45`; `chars_cyr=40`; `at_pt=36`; `logo_minus=5`; `lines_max=1`; `orphan_words_min=2` | `chars_latin=45`; `chars_cyr=40`; `at_pt=36`; `logo_minus=5`; `lines_max=1`; `orphan_words_min=2` | A | plan, html, pdf | бажано (косметика: one-word last line of a dek) | L14 | `deck-storyline` |
| T4 | **Claim is the largest text.** The title is the largest, highest-contrast text except a hero number; a repeated series label becomes an eyebrow in the running font. | `eyebrow_pt=12..16` | `eyebrow_pt=11..16` | A | html, pdf | бажано | L15 | `deck-storyline` |
| T5 | **Parallel siblings.** Sibling names and descriptions use one grammar (all verb-led or all noun phrases), each with a differentiator the others lack. | none | none | V | none | косметика | L16 | `deck-storyline` |
| T6 | **No restatement.** The first body line adds a number or outcome; content-word overlap with the title of 50% or more is a restatement. | `overlap_max=0.5` | `overlap_max=0.5` | A+V | html, pdf | косметика | L17 | `deck-storyline` |
| T7 | **Hero number.** A number that carries the claim is the hero: at least 2x body size, a label of at most 6 words, its base and method stated. | `hero_ratio_min=2`; `label_words_max=6` | `hero_ratio_min=2`; `label_words_max=6` | A+V | html | бажано | L18 | `deck-storyline` |
| T8 | **From-to outcomes.** From-to rows are equal in number with one arrow each; the "to" side is written as observable outcomes and the "from" side is muted. | none | none | A+V | html | косметика | L22 | `deck-storyline` |
| T9 | **Ukrainian slide copy.** NBSP between a number and its unit; product names in Latin in the running font, not mono; Cyrillic titles within the T3 budget. | none | none | A | plan, html, pdf | косметика | L71 | `deck-storyline` |
| T10 | **One dash form.** Ranges use one form per plan.dash_policy; under "hyphen" no U+2013 or U+2014 in slide text; the minus sign U+2212 is not a dash and stays. | none | none | A | plan, html, pdf | косметика | L72 | `deck-storyline` |
| T11 | **Duplicates and proofreading.** No two items share their first 5 words within a slide or across neighbouring slides (a zoom and a declared pair are exempt); no two slides share a title (a zoom may repeat its map title); no double spaces; no footnote marker without its note; no near-identical non-build slides; spelling read by a reviewer. | `prefix_words=5` | `prefix_words=5` | A+V | plan, html, pdf | критично (бажано: across neighbouring slides, repeated title, orphan marker, near-duplicate slides; косметика: double space) | L20, L73 | `deck-review` |

Calibration (ref = reference deck, own = own deck):

- **T1** ref assertion titles only on 3-7 and 13 of about 40 content slides; own deck titles are mostly assertions.
- **T2** ref 13 keeps its claim in an 11 pt footer caption under a generic 28 pt title, 34 in a band, 14 in a why-box, 10 in the subtitle; own deck not measured.
- **T3** ref one-word orphans on 4, 5, 35, autofit on 39 shrank the title to 32.1 pt and moved it 4 pt; own deck titles average 31.7 chars (max 63) with an orphan on 22, and the dek ends in a one-word line on 15, 22, 27, 31, 32 (косметика).
- **T4** ref 37-42 set the series label at 36 pt and the claim at 16 pt teal (2.09:1), a "Demo:" prefix eats about 40% of titles on 19, 20, 24 (both fire: the segment before `|` or `:` repeats on two or more titles); own deck eyebrow at 11 px (8.25 pt) uppercase mono.
- **T5** ref 45 card names mix verb and noun phrases and two promise one benefit, 3 and 13 are parallel (good); own deck not measured.
- **T6** ref 46 restates its title three times in 30 words (overlap 1.00), 10 repeats it in its largest body text (0.50); the plan's 0.6 cut missed 10, so the cut is 0.5 and fires at or above it (no extra row on the ref, the own deck or the fixtures); own deck 12 at 0.67.
- **T7** ref 9 hides a large user count in a 20 pt subtitle; own deck slide 4 shows proof tiles with a measurement-method note (good).
- **T8** ref 5 styles both sides identically and its targets read as slogans; own deck not measured.
- **T9** ref titles at 36 pt wrap above about 45 Latin chars (4, 5, 35); own deck sets product names in mono tags and titles reach 63 chars; NBSP not measured.
- **T10** not measured on either deck; the house rule bans dashes while dashboard-copy rule 9 prescribes one for ranges.
- **T11** ref 39 repeats a 13-word bullet, 9 and 10 share three identical bullets, 20 has a double space, 13 an orphan footnote marker, 19 and 21 are near-identical setup frames (dHash 11, above `dup_hamming_max`: caught on the contact sheet, the V part), 9 and 10 at dHash 10; `visual_hints` lists the five closest pairs above the cut (9/10, 29/30 zoom, 19/21, 21/24, 48/50). A pixel match is a lint row only when the text backs it (shared title head or prose overlap at the T6 cut): own deck 12/14/17/19 (dHash 5-6) and 15/18 (dHash 4) are setup steps with one terminal layout and different text, so they are hints, not rows.

## §4. G: grid and geometry

Owner `slide-design`.

| ID | Check | Talk | Reading | By | Auto in | Severity | Lesson | Fix owner |
|---|---|---|---|---|---|---|---|---|
| G1 | **Title box token.** Title box (x, baseline, size, weight, colour) is one token: drift at most 2 pt across content slides and one size; title x equals the content left edge. | `drift_pt=2`; `title_sizes_max=1` | `drift_pt=2`; `title_sizes_max=1` | A | html, pdf | бажано | L23 | `slide-design` |
| G2 | **Safe margin.** Nothing closer than 36 pt to a slide edge except full-bleed media; the footer band keeps at least 18 pt. | `margin_pt=36`; `footer_edge_pt=18` | `margin_pt=36`; `footer_edge_pt=18` | A+V | html, pdf | бажано | L24 | `slide-design` |
| G3 | **Decoration and brand corner.** Decoration keeps 16 pt clear of content; a brand corner of at least 60x60 pt is reserved; brand marks appear on all slides of a family or none. | `decoration_clear_pt=16`; `brand_corner_pt=60` | `decoration_clear_pt=16`; `brand_corner_pt=60` | A+V | html | косметика | L25 | `slide-design` |
| G4 | **Connectors at centres.** Card rows share one column grid and connectors attach at card centres within 2 pt; re-route after moving a card. | `offset_pt=2` | `offset_pt=2` | V | none | косметика | L26 | `slide-design` |
| G5 | **Empty space with small text.** If more than 25% of the slide height is empty below the content, or of a card's height between two of its blocks, while text sits below the body size, enlarge type or relayout; card bottom padding within 10% of the top padding. | `empty_ratio=0.25`; `card_pad_tol=0.1` | `empty_ratio=0.25`; `card_pad_tol=0.1` | A | html, pdf | бажано | L27 | `slide-design` |
| G6 | **Text and image split.** A text plus image split runs about 40/60, the image top and bottom align with the text zone within 2 pt, and the list holds at most 4 items. | `text_share=0.35..0.45`; `align_pt=2`; `items_max=4` | `text_share=0.35..0.45`; `align_pt=2`; `items_max=4` | A+V | html | косметика | L28 | `slide-design` |
| G7 | **Nesting and strokes.** At most 2 nesting levels (page frame + card); a stroke meant to be seen on dark is at least 1.5 pt and 3:1. | `nesting_max=2`; `stroke_min_pt=1.5`; `stroke_contrast=3` | `nesting_max=2`; `stroke_min_pt=1.5`; `stroke_contrast=3` | A+V | tokens, html | бажано | L29 | `slide-design` |
| G8 | **One process axis.** A process runs on one reading axis numbered 1..N; vertical position is used only when it encodes something. | none | none | V | none | косметика | L30 | `slide-design` |

Calibration (ref = reference deck, own = own deck):

- **G1** ref title x takes 10 values (7.2 to 155.4 pt plus centred) and 11 sizes, 25 sets its title 27 pt right of its table; own deck one title box on 32 of 33 slides.
- **G2** ref demo frames 19-24 put the title at x=7.2 pt and a pill about 3 pt from the edge, 13 keeps 23-26 pt side margins, a screenshot on 40 reaches 945 pt, the footer baseline sits 19.7 pt up; own deck top padding is 38 px (28.5 pt), so every eyebrow sits inside the margin; G2 fires on all 33 slides (the nearest a vertical rail label 10.9 pt from the edge).
- **G3** ref the corner mark overlaps step 4 on 3 and a screenshot card on 46, and appears only on 2-6; own deck has no brand mark.
- **G4** ref 34 bottom connectors land about 88 pt right of the card centres, top ones +16/-10/-56 pt (pixel-checked); own deck slide 9 has a connector crossing a label.
- **G5** ref 45 leaves about 58 pt empty under each hub card; 36 measures 22.6% empty below its lowest text with the footer band counted (16% above the band), under the 0.25 cut, so V only; own deck slides 2, 3, 4, 10 leave 214-237 px (30-33%) empty with text at 10-12.5 px, and equal-height cards pin a note with `margin-top:auto`, leaving dead space inside each card: 6 at 56% (238 of 429 px), 24 at 38-49% (171-221 of 450 px).
- **G6** ref 41 sets its image about 24 pt off the text zone; 37 runs 37/63 with 3 items (good, hence the 0.05 tolerance); own deck not applicable.
- **G7** ref 10 nests frame, card and ring and spends about 15% of the width on padding, 32 has a nearly invisible 1 px grey frame; own deck card borders are 3 px (not linted).
- **G8** ref 15 alternates stages between two rows, 3 uses a rising staircase for maturity (good), 28 flows top to bottom (good); own deck 29 is a deliberate loop.

## §5. Y: type

Owner `slide-design`. Roles in HTML come from the DOM contract (title, eyebrow, body, label, code, hero, footer); a PDF has no roles, so runs are judged against `floor_pt` and the share below `body_pt` is reported once per slide.

| ID | Check | Talk | Reading | By | Auto in | Severity | Lesson | Fix owner |
|---|---|---|---|---|---|---|---|---|
| Y1 | **Type scale and floors.** One type scale: every text at least the floor (eyebrow and footer have their own floors), body at the body size, one title size in the range, dividers in range, at least 1.3x between a heading and the text it heads. Text inside a declared shape-as-hero figure (D4) is exempt. | `floor_pt=14`; `body_pt=18`; `eyebrow_min_pt=12`; `footer_pt=9`; `title_pt=32..40`; `divider_pt=48..60`; `levels_ratio=1.3` | `floor_pt=11`; `body_pt=11`; `eyebrow_min_pt=11`; `footer_pt=9`; `levels_ratio=1.3` | A | html, pdf | критично (бажано: body below body_pt but at or above floor_pt, title or divider out of range, levels) | L31 | `slide-design` |
| Y2 | **One sans, one mono, sizes on the scale.** One sans plus one mono deck-wide (weight, style and optical-size names folded); every size on the declared type scale, or on whole pt of the 960x540 page when no scale is declared. | `families_max=2`; `offscale_words_max=0` | `families_max=2`; `offscale_words_max=0` | A | html, pdf | бажано | L32 | `slide-design` |
| Y3 | **Centred text.** Centre only labels of 1-2 lines; left-align anything longer. | `centred_lines_max=2` | `centred_lines_max=2` | A+V | html, pdf | бажано | L33 | `slide-design` |
| Y4 | **Measure.** Body lines of 35-60 characters, text columns at least 170 pt wide, a left-column statement of at most 12 words and 4 lines. | `line_chars=35..60`; `column_min_pt=170`; `statement_words_max=12`; `statement_lines_max=4` | `line_chars=35..60`; `column_min_pt=170`; `statement_words_max=12`; `statement_lines_max=4` | A+V | html | косметика | L34 | `slide-design` |
| Y5 | **One emphasis mechanism.** One emphasis style per slide (weight, or one solid accent that passes C1); accent leads only when the leads alone tell the story. | `emphasis_styles_max=1` | `emphasis_styles_max=1` | A+V | html | косметика | L35 | `slide-design` |
| Y6 | **Uppercase Cyrillic with digits.** No uppercase transform on Cyrillic text that mixes digits with з, о or б in a mono font; write "N / M". | `hits_max=0` | `hits_max=0` | A | html, pdf | критично | L70 | `slide-design` |

Calibration (ref = reference deck, own = own deck):

- **Y1** ref 26.2% of 2,449 words sit below 12 pt and 39.5% below 14 pt (stats, the SHARE line of `stats.txt`; 71.5% below 18 pt), its legible slides all at 17 pt or more, title 36 pt on light vs 32.1 or 34.7 pt on dark; own deck 97.0% of words below 13.6 px (about 10 pt), modal 12.5 px (9.4 pt), title 29 px (21.8 pt), SVG text down to 6.6 px.
- **Y2** ref 20 font names in the text layer and 258 words (10.5%) at non-integer sizes; own deck declares one sans stack in two optical sizes plus one mono (Windows-only), and sizes such as 12.5 and 13.5 px print off whole pt.
- **Y3** ref 3 centres 5-7-line paragraphs, 36 centres 5-9-line columns 118 pt wide; own deck is left-aligned (not measured).
- **Y4** ref 7 wraps a statement into 7 lines of 2-3 words, 36 sets six 118 pt columns; own deck lets the dek run to 104ch (not measured).
- **Y5** ref 48 and 50 carry about 14 words of story in their leads at 17 pt (good), 10 uses gradient emphasis at about 3.0-3.3:1 (approx.), 46 leaves its key terms at body weight; own deck emphasis in the accent colour fails C1.
- **Y6** ref not applicable; own deck eyebrows on 11-18 read «КРОК 2 3 7».

## §6. C: colour

Owner `slide-design`. Formula and audit method: `pbi-color-accessibility` reference.md §1 and §10. `deck_lint.py --tokens` rates the token pairs before slide 2 exists.

| ID | Check | Talk | Reading | By | Auto in | Severity | Lesson | Fix owner |
|---|---|---|---|---|---|---|---|---|
| C1 | **Text contrast.** Text at least 4.5:1 against its background; 3:1 only at 24 pt or 18.7 pt bold; a bright accent gets an accent-fill and a darker accent-text token per background. Unknown backgrounds go to could-not-verify. | `body=4.5`; `large=3`; `large_pt=24`; `large_bold_pt=18.7` | `body=4.5`; `large=3`; `large_pt=24`; `large_bold_pt=18.7` | A+V | tokens, html, pdf | критично | L36 | `slide-design` |
| C2 | **Table headers.** Table header text at least 4.5:1 on its fill; one header fill per table. | `header=4.5`; `header_fills_max=1` | `header=4.5`; `header_fills_max=1` | A+V | tokens, html | критично (бажано: more than one header fill) | L37 | `slide-design` |
| C3 | **Gradient text.** Gradient text only at 40 pt or more for at most 5 words; its contrast is judged at the worst stop (a failure there is a C1 finding). | `min_pt=40`; `words_max=5` | `min_pt=40`; `words_max=5` | A+V | html, pdf | бажано | L38 | `slide-design` |
| C4 | **One luminance per section.** Light and dark flip only into or out of a title, divider, demo divider or appendix divider; bright media in a dark section are dimmed, framed or scrimmed (30-40%). | `flips_max=0` | `flips_max=0` | A+V | html, pdf | бажано | L39 | `slide-design` |
| C5 | **Colour meaning.** Structure stays greyscale; saturated colour marks only the 1-4 entities the claim names; each colour keeps one meaning across slides and legends. | `entities_max=4` | `entities_max=4` | V | none | бажано | L40 | `slide-design` |
| C6 | **Zoom dimming.** A zoom or focus build dims the context to about 2:1 instead of deleting it, keeps active text at least 7:1 and reveals content at least as large as the repeated context. | `dim_target=2`; `active_min=7`; `reveal_ratio_min=1` | `dim_target=2`; `active_min=7`; `reveal_ratio_min=1` | A+V | tokens, html | бажано | L41 | `slide-design` |
| C7 | **Card separation.** Cards separate from the page by a fill step of at least 1.15:1 or a 1 pt border, never by shadow alone. | `card_step=1.15`; `border_pt=1` | `card_step=1.15`; `border_pt=1` | A+V | tokens, html | бажано | L42 | `slide-design` |

Calibration (ref = reference deck, own = own deck):

- **C1** ref #49C5B1 on #FFFDF9 2.09:1 on 98 words, black on that fill 9.90:1, the hue darkened to #2B766A 5.30:1; own deck #F2C811 on white 1.61:1 on 31 slides, #5CC8FF 1.88:1, red symptom lines 3.19:1.
- **C2** ref white on #0F9ED5 3.06:1 and on #00B0F0 2.48:1 (17, 18, 25), the second band lighter on 18 and 25; own deck table headers at 10 px mono (a Y1 failure, contrast not reported).
- **C3** ref 8 sets a 54 pt gradient divider that reads well, 10 uses gradient emphasis at 18 pt at about 3.0-3.3:1 (approx.), and the extractor reports gradient text as #000000; own deck has none.
- **C4** ref 5 of 6 transitions in 27-33 flip by eye (the mean-luminance classes catch 2: 27 is mid at 0.44, the photo 31 dark at 0.27), 6 flips in 45-52 (7 counting 44 to 45), a bright photo (31) between navy slides, a divider switch on 8 (good); own deck keeps one luminance.
- **C5** ref 28 colours only three marks and one hexagon (good), outline colours on 7 mean nothing; own deck four channel colours keep one meaning each (good).
- **C6** ref 30 dims labels to 2.21:1 (#3F5866 on #002134) with active white at 16.57:1 (good) but reveals its parts at 14 pt under a 32 pt header; own deck has no zoom.
- **C7** ref #FFFFFF cards on #FFFDF9 at 1.02:1 on 2, 34, 36; own deck card fill #F6F8FA on #FFFFFF at 1.06:1 (borders not linted).

## §7. V: devices and visual

Owner `slide-design`.

| ID | Check | Talk | Reading | By | Auto in | Severity | Lesson | Fix owner |
|---|---|---|---|---|---|---|---|---|
| V1 | **Device meaning.** Each device keeps one meaning (icon map in the token sheet); icons read literally against the claim; rails and number markers only for ordered sequences. | none | none | V | none | бажано | L43 | `slide-design` |
| V2 | **Drawn relationships.** Relationships are drawn: "+" for composition, a bracket for hierarchy, an arrow for flow; every result traces to its inputs. | none | none | V | none | косметика | L44 | `slide-design` |
| V3 | **Labels and anchors.** Every grouping device and relational edge is labelled; callouts sit within 12 pt of their anchor or on a leader line. | `anchor_pt=12` | `anchor_pt=12` | V | none | косметика | L45 | `slide-design` |
| V4 | **Live text on canvas.** All words are live text inside the canvas: nothing off-canvas or hidden; a slide outside the raster-exempt archetypes with 5 or fewer live words plus images is a raster suspect. | `raster_words_max=5` | `raster_words_max=5` | A+V | html, pdf | критично | L46 | `slide-design` |
| V5 | **Imports restyled.** Every imported visual is restyled to the host deck: background, radius, flat logos, no foreign gradients or lighting. | none | none | V | none | бажано | L47 | `slide-design` |
| V6 | **Architecture map.** A map shows at most 12 boxes, flows in reading direction, makes outcomes the largest text and highlights exactly one zone, found within 1 s at 25% thumbnail size. | `boxes_max=12`; `highlights=1`; `thumb_scale=0.25` | `boxes_max=12`; `highlights=1`; `thumb_scale=0.25` | A+V | html | бажано | L48 | `slide-design` |
| V7 | **Code line.** Code is one mono line under its claim, at the code size (hero line larger), with straight quotes, one mono family and colour only on the tokens that matter. | `code_pt=18`; `code_hero_pt=24`; `curly_quotes_max=0` | `code_pt=11`; `curly_quotes_max=0` | A+V | html, pdf | бажано (критично: curly quotes in code) | L21 | `slide-design` |
| V8 | **Status pill.** Release status uses one pill component (size, casing, position) with a distinct fill per status and a label of at least 4.5:1; roadmap claims carry an as-of date. | `pill_styles_max=1`; `label_contrast=4.5` | `pill_styles_max=1`; `label_contrast=4.5` | A+V | tokens, html | бажано | L19 | `slide-design` |

Calibration (ref = reference deck, own = own deck):

- **V1** ref numbered rings mean steps, problems and features, one concept gets 4 icons on 4 slides, an open padlock illustrates a security claim (10), dot rails mark unordered benefits; own deck markers keep one meaning (good).
- **V2** ref 52 uses "+" chips and a bracket (good), 12 shows A + B with a result bar linked to neither input; own deck not measured.
- **V3** ref 3 has an unlabeled dashed box, 16 undirected edges, 29 a fieldset-style group label (good); own deck slide 9 labels collide with box edges.
- **V4** ref 16 bakes about 170 words into an image and parks its title at y=553.1 on a 540 pt page, 28 parks a title at y=576, 23 has 0 live words; own deck diagrams are live SVG text.
- **V5** ref 23 keeps a glossy illustration on its own gradient, 25 a light document table over about 80% of a dark slide, 26 tilted 3D logos; own deck is one system.
- **V6** ref 6 carries 22 logos and 96 words mostly at 7-8 pt with outcomes smallest, 7 carries 25 images, 29 marks its focus with one 2 px outline (too subtle); own deck maps 8-9 set labels at 7.8-8.8 px.
- **V7** ref 17 and 26 pair claim and code (good), 26 uses curly quotes, 17 and 18 use two mono faces; own deck code at 12.5 px (9.4 pt) with a working copy button.
- **V8** ref status appears as an inline bullet, a 16 pt pill and a 12 pt pill, GA and preview share fill #6BE9BD, 26 names a future month without an as-of date; own deck pills at 10 px wrap on 10.

## §8. D: density

Owner `slide-design`. Words are visible live words (tokens with a letter or digit), excluding notes, chrome and page numbers.

| ID | Check | Talk | Reading | By | Auto in | Severity | Lesson | Fix owner |
|---|---|---|---|---|---|---|---|---|
| D1 | **Words and zones.** A talk slide holds at most 50 words (80 hard) and 5 zones and is flagged above 2x its series median; a reading slide holds at most 180 words and is split above. | `words_max=50`; `words_hard=80`; `zones_max=5`; `series_ratio=2` | `words_max=180` | A | html, pdf | бажано (критично: talk words above words_hard) | L49 | `slide-design` |
| D2 | **Archetype budgets.** Each archetype keeps its word and size budget (§13); a reading archetype on a talk main flow and a slide that fits no archetype are findings. | none | none | A | html, pdf | бажано | L50 | `slide-design` |
| D3 | **Stage tables.** A projected comparison table has at most 6 rows by 3 columns with cells at 14 pt or more, and repeated prefixes become subheads; ref-table follows its own budget (§13). | `rows_max=6`; `cols_max=3`; `cell_min_pt=14` | n/a | A+V | html | бажано | L51 | `slide-design` |
| D4 | **Shape as hero.** When the point is a shape, the shape is the hero with at most 4 takeaways at 20 pt or more linked by numbered callouts; labels inside it are exempt from Y1. | `takeaways_max=4`; `takeaway_min_pt=20` | n/a | V | none | косметика | L52 | `slide-design` |

Calibration (ref = reference deck, own = own deck):

- **D1** ref median 37.5 live words (stats 39), 7 slides above 80 (14 = 252, 13 = 160, 46 = 141; stats 255, 165, 145) against a series median near 58; own deck median 226, 10 slides above 250, max 347.
- **D2** ref best slides measure thesis 21 words, from-to about 40, feature lists 34-38 at 17-18 pt, hub about 40 at 20 pt, close 32; own deck reading archetypes run at median 226 words.
- **D3** ref 14 shows 9 rows of 9 pt cells repeating two prefixes about 13 times; own deck error log 7 x 3 (reading mode, allowed).
- **D4** ref 4 pairs a tangled diagram with 11 pt labels and 4 pains at 20 pt (good) but does not link them; own deck not applicable.

## §9. S: screenshots and demos

Owner `slide-design`. HTML screenshots declare `data-ui-px` and `data-native-width`; for a PDF the plan carries `slides[].media`.

| ID | Check | Talk | Reading | By | Auto in | Severity | Lesson | Fix owner |
|---|---|---|---|---|---|---|---|---|
| S1 | **Screenshot effective size.** Effective UI text = UI px x placed width pt / native width px; at least 9 pt, otherwise a crop, a zoom inset or a callout of at least 14 pt; capture at 150-200% app zoom. | `eff_min_pt=9`; `callout_min_pt=14` | `eff_min_pt=9`; `callout_min_pt=14` | A+V | html, pdf | критично | L53 | `slide-design` |
| S2 | **Result moment.** Stills show the result moment of the claim, never an empty, landing or setup state; a video poster is the result frame. | none | none | V | none | бажано | L54 | `slide-design` |
| S3 | **Annotation.** One highlight (stroke of at least 3 pt in a colour used nowhere else, covering 10-25% of the image), at most 3 callouts of at least 18 pt, number badges mapping bullets to regions. | `stroke_pt=3`; `area=0.1..0.25`; `callouts_max=3`; `callout_min_pt=18` | `stroke_pt=3`; `area=0.1..0.25`; `callouts_max=3`; `callout_min_pt=18` | A+V | html | бажано | L55 | `slide-design` |
| S4 | **Scrubbed captures.** Every capture is scrubbed: names, avatars, greetings, owner columns, tenant or workspace names, sensitivity labels, trial banners, notification counts, timestamps, cursors, terminal notices, URLs with IDs, e-mails; re-capture with synthetic data rather than blur. | none | none | V | none | критично | L56 | `slide-design` |
| S5 | **Crop and placement.** One screenshot per slide, cropped at UI boundaries, filling its zone in at least one dimension within 2 pt, in the slide theme; no collage, letterbox or mid-word crop. | `shots_max=1`; `fill_tol_pt=2` | `shots_max=1`; `fill_tol_pt=2` | A+V | html | косметика | L57 | `slide-design` |
| S6 | **Visible title or caption.** Every slide has a visible title or a caption of at most 10 words, never hidden behind an image; demo stills carry the deck demo marker. | `caption_words_max=10` | `caption_words_max=10` | A+V | html, pdf | критично | L58 | `slide-design` |

Calibration (ref = reference deck, own = own deck):

- **S1** ref a full window at 960 pt renders UI at about 7-9 pt (11, 19, 20), framed shots at 60% width at 4-5 pt (46, 48, 50), 33 at about 4 pt, while the crop on 42 and the zoomed capture on 49 reach 9-10 pt; own deck has no screenshots.
- **S2** ref 19 and 21 show setup cells with 35-40% blank, 22 an empty editor, 40 a landing page, while 39 (boxed output) and 41 (prompt plus chart) are good; own deck not applicable.
- **S3** ref 39 boxes about 25% of the image (good), 27 uses one outline and 3 arrows (good), 37 a 20x25 pt box on a 540 pt image (invisible), 11, 33, 43 none; own deck not applicable.
- **S4** ref personal names or greetings on 5 slides, owner columns on 3, classification labels on 4, trial banners on 3, cursors on 5, an auto-approval terminal notice on 44; own deck not applicable.
- **S5** ref 38 overlaps two shots, 39 leaves about 87 pt of letterbox, 27 cuts a word at the edge, 41 puts dark UI on a cream slide; own deck not applicable (SVG letterbox is H5).
- **S6** ref no title on 11, 31, 33, 43, 47, titles hidden behind images on 49 and 51, the demo divider of 32 never reused; own deck titles all 33 slides.

## §10. K: consistency components

Owner `slide-design`.

| ID | Check | Talk | Reading | By | Auto in | Severity | Lesson | Fix owner |
|---|---|---|---|---|---|---|---|---|
| K1 | **Page numbers.** A page number on every slide except the title and dividers, at one fixed position, at least 9 pt, equal to the slide index. | `pn_min_pt=9`; `pn_drift_pt=2` | `pn_min_pt=9`; `pn_drift_pt=2` | A | html, pdf | бажано | L59 | `slide-design` |
| K2 | **Template families.** At most 2 template families with fixed roles (for example light content and dark dividers), every import restyled to them. | `families_max=2` | `families_max=2` | A+V | html, pdf | бажано | L60 | `slide-design` |
| K3 | **Series frame lock.** A series or zoom pair locks its frame: title size and position, item count, body size, media box within 2 pt, one status component. | `frame_drift_pt=2` | `frame_drift_pt=2` | A+V | html, pdf | бажано | L61 | `slide-design` |

Calibration (ref = reference deck, own = own deck):

- **K1** ref page numbers on 15 of 52 slides, 8 pt at y25.4 on 35 vs 9 pt at y19.7 on 34, none on dark slides; own deck numbers all 33 slides by hand (H2).
- **K2** ref at least 9 families plus full-bleed stills; own deck 1 family.
- **K3** ref 37-42 switch body from 14 to 16 pt, 39 holds 4 items vs 3, image edges spread 26 and 56 pt, 22 sets its title at 28 vs 24 pt, 29 and 30 are pixel-locked (good); own deck steps 11-18 share one grammar.

## §11. H: HTML engine

Owner `html-deck`. Measured by `html_deck_lint.mjs`; not applicable to pptx or Slides decks.

| ID | Check | Talk | Reading | By | Auto in | Severity | Lesson | Fix owner |
|---|---|---|---|---|---|---|---|---|
| H1 | **Canvas fits every viewport.** A fixed 1280x720 canvas centred by translate plus scale with the control bar reserved; the slide box stays inside every acceptance viewport. | `viewports=390x844,1024x768,1280x720,1366x768,1600x900,1920x1080`; `fit_tol_px=1` | `viewports=390x844,1024x768,1280x720,1366x768,1600x900,1920x1080`; `fit_tol_px=1` | A | html | критично | L63 | `html-deck` |
| H2 | **Generated numbering.** Slide numbers, part labels, TOC ranges, totals and cross-references are generated from the DOM; no literal slide number in markup. | `literal_numbers_max=0` | `literal_numbers_max=0` | A | html | бажано | L64 | `html-deck` |
| H3 | **Fonts and bottom slack.** Embedded subset woff2 with Cyrillic or a metric-stable stack; QA in native and metric font modes; bottom slack on every slide in both modes (to the padding, plus the auto-margin or flex-grow space above the lowest content). | `bottom_slack_px=24`; `font_modes=2` | `bottom_slack_px=24`; `font_modes=2` | A | html | критично (бажано: slack between 0 and bottom_slack_px) | L65 | `html-deck` |
| H4 | **Exact print.** Print gives one slide per page of the canvas size, pages equal slides, chrome, copy buttons and notes are hidden, light tokens are forced, no code is clipped. | `page_pt=960x540`; `code_overflow_px=0` | `page_pt=960x540`; `code_overflow_px=0` | A | html | критично | L66 | `html-deck` |
| H5 | **SVG fit.** Each SVG viewBox matches its board aspect (letterbox at most 8%), its text stays inside the viewBox without overlapping other text or crossing a box edge, long captions live in HTML. | `letterbox_max=0.08`; `text_outside_max=0`; `text_overlap_max=0` | `letterbox_max=0.08`; `text_outside_max=0`; `text_overlap_max=0` | A | html | бажано (критично: text outside the viewBox or overlapping text or a box edge) | L67 | `html-deck` |
| H6 | **Notes and presenter view.** Talk decks: aside.notes on every main slide, a presenter view that follows navigation over file://, swipe, overview, theme restored in head before first paint. | `notes_missing_max=0`; `presenter_follow_ms=200` | n/a | A | html | бажано | L68 | `html-deck` |
| H7 | **CSS hygiene.** No inline style attributes in slide markup; pills never wrap; component CSS uses child selectors: no rule ending in a bare type after a descendant combinator sets a border, padding or margin on an element nested inside another match. | `inline_styles_max=0`; `pill_lines_max=1`; `descendant_leaks_max=0` | `inline_styles_max=0`; `pill_lines_max=1`; `descendant_leaks_max=0` | A | html | бажано | L69 | `html-deck` |
| H8 | **No scaffold leftovers.** No [data-todo] slot left from the scaffold. | `todo_max=0` | `todo_max=0` | A | html | критично | L73 | `html-deck` |

Calibration (ref = reference deck, own = own deck):

- **H1** own deck spans x=142..1138 at 1024x768 (114 px cut), lies wholly outside the viewport at 390x844 (slide box x 459..821, a blank page) and loses 3 px under the bar at 1280x720; ref not applicable (PDF).
- **H2** own deck hard-codes 33 page numbers, 16 TOC ranges, 10 prose references and 1 total, plus a typed rail part label on all 33 slides that disagrees with the bar section on 6 (N13).
- **H3** own deck with the Linux fallback (DejaVu) overflows the bottom padding by 14.5/37.1/41.7 px on 25/26/28, while Liberation (Arial metrics) keeps 55.4/16.9/13.3 px slack, so 26 and 28 stay below 24 px; 6 and 24 read 13 px to the padding but their equal-height cards keep 166-264 px of auto-margin space above it, so they pass.
- **H4** own deck prints 33 pages at 960x540 pt (pass) but prints copy buttons, clips commands by 234/233/117 px on 13/14/18, and dark tokens print washed out.
- **H5** own deck letterboxes 182/190/168 screen px on 21/22/29 with diagram text at 6.6-9.8 px, footnotes on 8 run past the viewBox; SVG text crosses box edges or other text on 8 and 9 (labels on box edges), 21 (a footnote drawn through a box) and, with DejaVu only, 20 (a bold caption runs into the next text). A deliberate fieldset-style label over a box edge is refuted on the PNG. The 8% cut is a plan convention.
- **H6** own deck has no notes, presenter view, swipe or overview, uses replaceState only and restores the theme at the end of body.
- **H7** own deck carries 79 inline styles, wraps pills on 10 and leaks a descendant selector into the proof numbers on 1 (`.hero .strip div`, 8 nested matches with a border and padding).
- **H8** the scaffold contract of `html-deck` (fixtures only), not a ledger lesson: L73 is cited for the pre-export lint that catches what a reader would see.

## §12. P: review process

Owner `deck-review`. These judge the review, not the slides.

| ID | Check | Talk | Reading | By | Auto in | Severity | Lesson | Fix owner |
|---|---|---|---|---|---|---|---|---|
| P1 | **Every slide rendered and viewed.** Every slide is rendered to PNG and opened at full size; PNG count equals slide count and plan slide count; every image on it loaded (HTML: no `img` with naturalWidth 0); text-layer results are confirmed on pixels. | `missing_max=0` | `missing_max=0` | A+V | html, pdf | критично | L74 | `deck-review` |
| P2 | **Lint loop.** The last loop iteration shows 0 критично and every бажано fixed, refuted on the pixels or accepted by the user; stop after 5 iterations and report what remains. | `critical_max=0`; `iterations_max=5` | `critical_max=0`; `iterations_max=5` | A | html, pdf | критично | L73 | `deck-review` |
| P3 | **Evidence report.** The report carries the inventory, findings with slide and measurement, severities, «Не вдалося перевірити» and a claim-auditor pass on the titles. | none | none | V | none | бажано | L75 | `deck-review` |

Calibration (ref = reference deck, own = own deck):

- **P1** ref the text layer reports 16-29 pt on 19-24 where the visible content is 7-9 pt raster, 23 has 0 live words; an HTML image whose data URI carries an unescaped `#` never loads, passes S1 on its declared size and shows only alt text on the PNG.
- **P2** ref each L73 check fires on it (duplicates, drift, numbering, contrast, margins, untitled, off-canvas, raster, orphan marker); the thumbnail pair 19 and 21 only on the contact sheet (dHash 11, above `dup_hamming_max`). The 5-iteration stop is a plan convention.
- **P3** the evidence pipeline (6 analysts, 11 slides spot-checked, 6 refinements recorded) is the model; own deck not applicable.

## §13. Archetype budgets (D2)

Word and size budgets per archetype on a talk slide (960x540 pt; px = pt x 4/3). `mode` in a cell means the
mode budget applies (D1 words, Y1 floor). `min_pt` is the smallest text the audience must read on that
archetype; it may sit below the Y1 body size (labels, captions) but never below the Y1 floor. Where an
archetype sets `min_pt` below `body_pt`, that archetype value is the Y1 body target on that slide. A talk
archetype on an appendix slide is judged with reading budgets; a reading archetype on a talk main flow is a
D2 finding. The id list is the archetype enum: it must equal `deck-storyline` references/deck-plan.md,
`slide-design` references/archetypes.md, `thresholds.json` `archetypes` and the `<template data-archetype>`
snippets of the `html-deck` template (selftest asserts all four). In HTML each id is also the class `.a-<id>`.

| Archetype | Mode | words_max | min_pt | Extra | Source |
|---|---|---|---|---|---|
| `title` | talk | 20 | 14 | `title_min_pt=40`; `subtitle_ratio_max=0.67` | catalog 1, L03 |
| `route` | talk | 40 | 18 | none | catalog 2, L02 |
| `divider` | talk | 8 | mode | `title_words_max=6`; `title_min_pt=48` | catalog 3 |
| `thesis` | talk | 25 | 24 | none | catalog 4, L50 (ref 2: 21 words) |
| `journey` | talk | mode | 18 | `step_words_max=12`; `steps=3..5` | catalog 5 |
| `before-after` | talk | 45 | mode | `takeaways_max=4`; `takeaway_min_pt=20` | catalog 6, L04, L52 |
| `from-to` | talk | 40 | 18 | none | catalog 7, L50 (ref 5) |
| `concept` | talk | 15 | 18 | none | catalog 8 |
| `map` | talk | 30 | 16 | `boxes_max=12`; `highlights=1` | catalog 9, L48 |
| `zoom` | talk | 20 | 14 | none | catalog 10, L41 |
| `hub` | talk | 45 | 20 | `cards=3..4` | catalog 11, L50 (ref 45) |
| `feature-hero` | talk | 45 | 18 | none | catalog 12 |
| `feature-shot` | talk | 40 | 18 | `items_max=4`; `shot_eff_min_pt=9` | catalog 13, L50 (ref 48, 50 at 17-18 pt), L28 |
| `equation` | talk | 30 | 14 | none | catalog 14, L44 |
| `worked-example` | talk | 60 | 18 | `code_hero_pt=24` | catalog 15, L21 |
| `code-step` | talk | 40 | 18 | none | catalog 16 |
| `annotated-shot` | talk | 30 | 18 | `callouts_max=3` | catalog 17, L55 |
| `concept-demo` | talk | 15 | 14 | none | catalog 18 |
| `photo` | talk | 6 | mode | none | catalog 19 |
| `demo-divider` | talk | 8 | mode | `title_words_max=5`; `title_min_pt=48` | catalog 20, L06 |
| `demo-still` | talk | 20 | 18 | `caption_words_max=10`; `shot_eff_min_pt=9` | catalog 21, L53, L58 |
| `demo-recap` | talk | 25 | 18 | `steps_max=3` | catalog 22 (40 words, unmeasured) cut to the L08 bridge of 25 |
| `series-item` | talk | 40 | mode | none | catalog 23, L61 |
| `ref-table` | talk | mode | 18 | `rows_max=8` | catalog 24 |
| `compare-table` | talk | 60 | 14 | `rows_max=6`; `cols_max=3` | catalog 25, L51 |
| `close` | talk | 35 | 16 | none | catalog 26, L50 (ref 52: 32 words) |
| `cta` | talk | 20 | mode | `url_chars_max=25`; `pill_min_pt=18` | catalog 27, L10 |
| `kpi-wall` | reading | 180 | 11 | none | R1, L01 |
| `trap-card` | reading | 180 | 11 | none | R1, L01 |
| `setup-step` | reading | 180 | 11 | none | R1, L01 |
| `glossary` | reading | 180 | 11 | none | R1, L01 |
| `matrix` | reading | 180 | 11 | none | R1, L01 |
| `error-log` | reading | 180 | 11 | none | R1, L01 |
| `risks` | reading | 180 | 11 | none | R1, L01 |
| `summary-card` | reading | 180 | 11 | none | R1, L01, L10 |
| `appendix-divider` | any | 8 | mode | `title_words_max=6` | catalog 3, L01 |

"catalog n" is entry n of `slide-design` references/archetypes.md (same order as this table); R1 is its §R
reading archetypes, modelled on the own deck. Measured best slides on the ref: thesis 21 words, from-to about
40, feature lists 34-38 at 17-18 pt, hub about 40 at 20 pt or more, close 32 (L50).

## §V. Visual checklist

One question per check measured `V` or `A+V`, answered with slide number and what is seen. The deck-reviewer
agent and step 4 of the review loop use this list; an `A+V` question also confirms or refutes each automatic
finding on the pixels.

- **N2** Do all part dividers share one style and show n/N?
- **N3** Does the title slide state a promise and carry a context line?
- **N4** Do the before and after slides share the grid and the title pattern?
- **N5** Does the zoom repeat the map exactly, with the highlighted element carried to the demo divider?
- **N6** Does each demo show an entrance, a result still and a recap?
- **N7** Does a progress strip mark the current spoke, with the hub names and icons reused?
- **N10** Does the close show one takeaway, the recap and one next step, with no underlined links elsewhere?
- **N11** Does each proof sit right after the concept it proves?
- **T1** Read the titles alone: do they tell the story? (claim-auditor verdict attached; the suspects in `visual_hints` first)
- **T2** Is the best sentence on the slide its title?
- **T5** Do siblings share one grammar, each with a differentiator?
- **T6** Does the first body line add a number or an outcome?
- **T7** Is the hero number stated with its base and method?
- **T8** Are the "to" items observable outcomes, with the "from" side muted?
- **T11** Any misspelling, clone leftover or near-duplicate slide on the contact sheet (the look-alike pairs in `visual_hints` first)?
- **G2** Does any image, pill or decoration touch the edge band?
- **G3** Does decoration collide with content; is the brand corner consistent?
- **G4** Do connectors meet card centres?
- **G6** Are the image and text zones aligned top and bottom?
- **G7** Are strokes on dark visible from the back row?
- **G8** Does the process read along one axis?
- **Y3** Any centred paragraph over 2 lines?
- **Y4** Any line far outside 35-60 characters or a column narrower than 170 pt?
- **Y5** Is there exactly one emphasis mechanism?
- **C1** Text on gradients, photos or unknown backgrounds: readable at the worst spot?
- **C2** Is the header readable with one header fill?
- **C3** Is gradient text only large and short?
- **C4** Any glare pulse: a bright slide or screenshot inside a dark section?
- **C5** Does each colour mean one thing across slides and legends?
- **C6** Is the context dimmed, not deleted, and the reveal at least as large?
- **C7** Are cards separated without relying on shadow?
- **V1** Does each icon and device keep one meaning and read literally?
- **V2** Are relationships drawn and results traceable to their inputs?
- **V3** Are groups and edges labelled and callouts anchored?
- **V4** Any words baked into an image, or a title hidden off-canvas or behind an image?
- **V5** Does any import keep a foreign background, gradient or lighting?
- **V6** At 25% thumbnail size, is the one highlight found within 1 s?
- **V7** Is colour in code limited to the tokens that matter?
- **V8** One pill style, distinct status fills, an as-of date on roadmap claims?
- **D3** Are repeated prefixes factored into subheads?
- **D4** Is the shape the hero, with takeaways linked by numbered callouts?
- **S1** Is screenshot text readable at its effective size (PDF path without media)?
- **S2** Does each still show the result moment?
- **S3** One highlight, few callouts, badges mapping bullets to regions?
- **S4** Scrub list (names, avatars, labels, banners, timestamps, cursors, IDs, e-mails): all clear?
- **S5** One shot per slide, no collage, letterbox or mid-word crop, theme-matched?
- **S6** Does every still carry a title or caption and the demo marker?
- **K2** How many template families does the contact sheet show?
- **K3** Do series siblings keep a locked frame?
- **P1** Was every PNG opened at full size?
- **P3** Does the report carry inventory, evidence, severities, the could-not-verify list and a verdict?

## §14. Calibration on the reference (local regression only)

The reference PDF and its renders stay local; only these measured numbers enter the repository. A bare lint
run (no plan) must reproduce the `deck_lint.py` values below; numbers marked "stats" are the analysts'
first-run statistics (`stats.txt`), kept for comparison and not asserted. `stats.txt` counts whitespace tokens;
the judge's D1, N1 and N8 values count live words, so page numbers and tokens without a letter or digit
(bullets, pipes) drop out (teardown §7):

- G1: title box drift on most content slides, 14 title x values and 12 title sizes (stats: 10 x values and
  11 sizes read from the first run of each slide, including the 48 pt title slide and the 54 pt dividers;
  the judge takes the largest run in the top `title_zone_top` instead);
- page numbers on 15 of 52 slides (K1);
- off-canvas runs on 2 slides at y=553.1 and y=576.0 (V4);
- Y2: 246 live words (10.3%) at non-integer sizes and 20 font names (stats: 258 whitespace tokens, 10.5%;
  teardown §7 explains the difference);
- 7 dense slides above 80 words and 11 silent slides at 5 words or fewer (D1, N8);
- a duplicate within one slide and 3 identical bullets across a sibling pair (T11); the near-identical
  setup frames 19 and 21 are not a lint row (dHash 11) but appear in `visual_hints` with 9 and 10 (dHash 10);
- #49C5B1 on #FFFDF9 at 2.09:1 and white on the header fill #0F9ED5 at 3.06:1, both C1 findings on the PDF
  path (C2 is automated on tokens and html only; the two header fills on 18 and 25 are a C2 visual check);
- C4: flips 28 to 29 and 32 to 33 in the 27-33 run (the eye sees 5 of 6, the other 3 are confirmed on the
  contact sheet) and all 7 from 44 to 52.

The own-deck regression (also local) must reproduce H1-H7, Y6, C1, G2, G5, T3 and reading-mode D1 at the
slides named in the calibration bullets above; any miss is a lint bug.

## §15. Adding a check

1. Pick the family and the next free ID; never reuse a retired ID.
2. Add the row here (rule, both mode cells, By, Auto in, severity, lesson, owner) and its calibration bullet.
3. Mirror the numbers in `scripts/thresholds.json` under `checks.<ID>`.
4. Add the measurement field to `html_deck_lint.mjs` or `pdf_text_runs.py` output if the check is automatic.
5. Seed one fixture slide in `scripts/fixtures/seeded.html` and an `expected.json` entry; keep `clean.html` clean.
6. If the check is `V` or `A+V`, add its question to §V.
7. Run `python3 scripts/selftest.py` until it passes.
