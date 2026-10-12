---
name: slide-design
description: Use when designing or fixing how slides look in any engine (HTML, pptx, Slides) - archetype anatomy and budgets (title, route, divider, concept, map, zoom, hub, feature shot, table, demo still, close), projection type scale, title box and safe margins, at most two template families, accent-fill vs accent-text pairs checked before building, one luminance per section, icons and devices, screenshot crop, annotation, scrubbing, code and status components. Symptoms - talk text under 18 pt, a title that jumps between slides, a bright accent used as text, an unreadable full-window screenshot. Do NOT trigger for storyline or title wording (deck-storyline), .pptx mechanics (pptx), HTML engine code (html-deck), Power BI report pages (pbi-design-system, pbi-typography), chart internals (dataviz), checking a finished deck (deck-review). Triggers - 'дизайн слайдів', 'макет слайда', 'шрифт на слайді', 'слайд перевантажений', 'скріншот на слайді', 'контраст на проекторі', 'slide design'.
---

# Slide design: legible in the room, consistent across the deck

## Overview

Engine-neutral rules for everything visible on a slide, plus the deck-wide token sheet that makes its colour
pairs checkable before the first slide is built. Every threshold comes from `deck-review` references/rubric.md;
token values from `assets/tokens.example.json`, ratios from the `pbi-color-accessibility` reference.md §1
formula. A check ID in brackets (Y1, C1) routes a lint finding back here. Detail: `references/archetypes.md`
(36 archetypes, budgets), `references/visual-system.md` (tokens, type, grid, colour, engine mapping) and
`references/screenshots-and-devices.md` (screenshots, devices, components).

Routing: contrast formula and audit -> `pbi-color-accessibility` reference.md §1, §10, blending §11;
dark/light inversion -> `pbi-design-system` reference.md §1.9 R1-R6; a palette without a brand ->
`theme-factory`, then roles here; chart marks and palettes -> `dataviz`; visual direction and AI-default
tells -> `frontend-design`; .pptx mechanics and the safe-font list -> `pptx`; cover art -> `canvas-design`.

## When to Use

- Laying out slides in HTML, pptx or the Slides artifact type, or restyling an existing deck.
- Choosing the type scale, colours, title box, grid and template families of a deck.
- Placing screenshots, diagrams, icons, code lines, status pills, tables.
- Fixing a `deck-review` finding in families G, Y, C, V, D, S or K.
- Symptoms, measured on a 52-slide vendor platform deck: 26% of words under 12 pt; the title at 10 x
  positions and 11 sizes; a teal accent as text at 2.09:1 (an own deck: yellow at 1.61:1); full-window
  screenshots at 4-9 pt effective; 9 template families.

**NOT for:** what the deck says, its order, title wording and notes (`deck-storyline`); .pptx files, XML,
templates and render QA (`pptx`); HTML engine code, print CSS, font embedding (`html-deck`); Power BI report
pages and their 8 pt floor (`pbi-design-system`, `pbi-typography`); chart internals (`dataviz`); chart choice
(`pbi-visualization-strategy`); scoring a finished deck (`deck-review`).

## Pre-flight

1. Read `mode`, `canvas` and `engine` from deck-plan.json (`deck-storyline`). No plan (restyling an existing
   deck): write an inferred plan with `"inferred": true` per `deck-storyline` references/deck-plan.md §10, or
   run `deck-storyline` first; without a plan, step 4 and D2 cannot run. Units: 960x540 pt = 1280x720 px,
   1 px = 0.75 pt, so 18 pt = 24 px and 14 pt = 18.67 px.
2. Fill the token sheet before slide 2: shape `assets/tokens.example.json`, fields and fill order in
   `references/visual-system.md` §1.
3. Rate it from the project folder: `python3 <deck-review>/scripts/deck_lint.py --tokens tokens.json`, where
   `<deck-review>` is the `deck-review` skill folder next to this one (or `--tokens deck.html` for the CSS
   `:root` blocks), until it exits 0 in every theme. Accent-as-text fails here, before any slide exists.
   `--tokens` rates colour pairs only: check `type`, `geometry` and `families` by hand against the Quick
   Reference (Y1 floors and title range, G2 margin, K2 at most 2 families).
4. Give every plan slide one archetype from `references/archetypes.md`. A slide that fits none is a
   candidate to cut or to move behind the appendix divider (D2).

## Quick Reference: type and placement

"Scale" values are the token sheet's two scales, pt for 960x540 pt engines and px for the 1280x720 HTML
canvas; they are separate scales on whole pt, not conversions (`references/visual-system.md` §2).

| Token or rule | Talk | Reading | Check | Lesson |
|---|---|---|---|---|
| Text floor | 14 pt (18.67 px); eyebrow 12, footer 9 | 11 pt (14.67 px); eyebrow 11, footer 9 | Y1 | L31 |
| Body size | 18 pt (24 px) or more; scale 20 pt / 28 px | scale 15 pt / 20 px | Y1 | L01, L31 |
| Title | one size, 32-40 pt; scale 36 pt / 48 px | one size; scale 30 pt / 40 px | Y1, G1 | L31 |
| Divider | 48-60 pt; scale 54 pt / 72 px | no range | Y1 | L31 |
| Levels | 1.3x or more between a heading and its text; card names 27 pt / 36 px | same; card names 21 pt / 28 px | Y1 | L31 |
| Families and sizes | one sans + one mono; sizes on the declared scale (whole pt when none) | same | Y2 | L32 |
| Title box | drift 2 pt or less; x = content left edge | same | G1 | L23 |
| Safe margin | 36 pt (48 px); footer baseline 18 pt up | same | G2 | L24 |
| Decoration, brand | 16 pt clear; brand corner 60x60 pt; marks all-or-none | same | G3 | L25 |
| Connectors | at card centres within 2 pt | same | G4 | L26 |
| Empty space | over 25% empty with small text: enlarge or relayout | same | G5 | L27 |
| Text plus image | text 35-45% (5 of 12 columns), aligned within 2 pt, 4 items or fewer | same | G6 | L28 |
| Nesting, strokes | 2 levels; strokes on dark 1.5 pt and 3:1 | same | G7 | L29 |
| Process | one reading axis, numbered 1..N | same | G8 | L30 |

## Quick Reference: colour, type, density, consistency

| Rule | Threshold | Check | Lesson |
|---|---|---|---|
| Text contrast | 4.5:1; 3:1 only at 24 pt or 18.7 pt bold; accent-fill and accent-text per background | C1 | L36 |
| Table header | 4.5:1, one fill per table | C2 | L37 |
| Gradient text | 40 pt or more, 5 words or fewer, judged at the worst stop | C3 | L38 |
| Luminance | one per section; flips only at title or dividers; bright media dimmed or 30-40% scrim | C4 | L39 |
| Colour meaning | saturated colour on 1-4 named entities, one meaning each | C5 | L40 |
| Zoom | context dimmed to about 2:1, active text 7:1, reveal as large as the context | C6 | L41 |
| Cards | fill step 1.15:1 or a 1 pt border, never shadow alone | C7 | L42 |
| Centring | only labels of 1-2 lines | Y3 | L33 |
| Measure | lines 35-60 characters, columns 170 pt, statement 12 words / 4 lines | Y4 | L34 |
| Emphasis | one mechanism per slide | Y5 | L35 |
| Cyrillic | no uppercase transform on Cyrillic with digits in mono; write «N / M» | Y6 | L70 |
| Words, zones | talk 50 (80 hard), 5 zones, flag above 2x series median; reading 180 | D1 | L49 |
| Archetype budget | words and min size per archetype (index below) | D2 | L50 |
| Stage table | talk: 6 rows x 3 columns at 14 pt | D3 | L51 |
| Shape as hero | 4 takeaways or fewer at 20 pt, numbered callouts | D4 | L52 |
| Page number | every slide but title and dividers, 9 pt, fixed (2 pt drift) | K1 | L59 |
| Families | 2 or fewer, fixed roles; imports restyled | K2, V5 | L60, L47 |
| Series frame | title, items, body size, media box locked within 2 pt | K3 | L61 |

## Archetype index

20 of the 36 archetypes; budgets from thresholds.json (`mode` = the D1 / Y1 mode budget). In HTML each id is
the class `.a-<id>`. Anatomy, reading archetypes and anti-archetypes: `references/archetypes.md`.

| Archetype | Words | Min pt | Key anatomy | Checks |
|---|---|---|---|---|
| `title` | 20 | 14 | h1 40 pt or more, promise, 14-18 pt context line | N3 |
| `route` | 40 | 18 | numbered parts, generated ranges, audience hint | N2 |
| `divider` | 8 | mode | 6 words at 48 pt or more, n/N, theme switch point | N2, C4 |
| `thesis` | 25 | 24 | 2-3 full-width rows at `card_heading` or one statement, no picture | D2, Y4 |
| `concept` | 15 | 18 | 3 zones or fewer, one focal element, greyscale | C5 |
| `map` | 30 | 16 | 12 boxes or fewer, exactly one highlight | V6 |
| `zoom` | 20 | 14 | map layout at 0 pt drift, dimmed context | C6, N5 |
| `hub` | 45 | 20 | 3-4 cards from `plan.lists`, names at `card_heading` | N7, Y1 |
| `feature-shot` | 40 | 18 | 40/60 split, 4 items, shot 9 pt effective | G6, S1 |
| `worked-example` | 60 | 18 | input, one 24 pt code line, output | V7 |
| `code-step` | 40 | 18 | claim plus one mono line, straight quotes | V7 |
| `annotated-shot` | 30 | 18 | crop, one highlight, 3 callouts or fewer | S3 |
| `demo-divider` | 8 | mode | outcome in 5 words, demo marker | N6 |
| `demo-still` | 20 | 18 | result moment, caption of 10 words, shot 9 pt | S1-S6 |
| `demo-recap` | 25 | 18 | 3 numbered steps or one sentence | N6, N8 |
| `series-item` | 40 | mode | eyebrow label, locked frame, progress strip | K3 |
| `ref-table` | mode | 18 | 8 rows or fewer on stage, count in the title | C2 |
| `compare-table` | 60 | 14 | 6 x 3, the answer as title, prefixes as subheads | D3 |
| `close` | 35 | 16 | takeaway, verbatim recap, one next step | N10 |
| `cta` | 20 | mode | URL of 25 characters in an 18 pt pill | N10 |

## Screenshots in six steps (S1-S6)

1. **Capture** on a demo account with synthetic data at 150-200% app zoom, at the **result moment** of the
   claim, never a setup, landing or empty state (S2).
2. **Crop** to the panel that proves the claim, at UI boundaries; one shot per slide, no collage or
   letterbox (S5).
3. **Compute** effective size = UI px x placed width pt / native width px. Below 9 pt crop tighter, add a
   zoom inset or a callout (18 pt per S3; S1 alone accepts 14 pt). A 1920 px window with 12 px UI is 6 pt at
   slide width (200% zoom fixes it) but 3.2 pt in the 7-column media zone, where even 200% zoom gives 6.35
   pt: zoom and crop together.
4. **Annotate:** one highlight of 3 pt or more in a colour used nowhere else, covering 10-25% of the image; at
   most 3 callouts of 18 pt or more; number badges map bullets to regions (S3).
5. **Scrub** with the checklist in `references/screenshots-and-devices.md` §3; re-capture rather than blur (S4).
6. **Title** it: a visible title or a caption of at most 10 words, plus the deck demo marker on demo
   stills (S6).

## Devices and diagrams (V1-V6)

- One meaning per device, recorded in the token sheet `icons` map; read every icon literally against its
  claim (an open padlock contradicts a security claim). Numbers and rails only for ordered sequences (V1).
- Draw relationships: "+" for composition, a bracket for hierarchy, an arrow for flow, a result band traced
  to both inputs (V2). Label every group and relational edge; callouts within 12 pt of their anchor (V3).
- Every word is live text inside the canvas (V4); every import restyled to the host family (V5).
- A map holds 12 boxes or fewer with one highlight that a 25% thumbnail shows within 1 s (V6).

## Components (V7, V8, K1, K3)

- **Code line:** one mono family, 18 pt (24 pt hero), straight quotes, colour on key tokens only (V7).
- **Status pill:** one style, a distinct fill per state, label 4.5:1, an as-of date on roadmap claims (V8).
- **Page number** and **series frame** are tokens, generated or templated, never typed per slide (K1, K3).
- Specs, Ukrainian labels and computed ratios: `references/screenshots-and-devices.md` §11.

## Settled conflicts

- **`pptx` document floors.** Its 14-16 pt body and 10-12 pt captions are document sizes: talk raises body to
  18 pt and every readable text to 14 pt (Y1); reading mode accepts the 14-16 pt body and 11-12 pt captions,
  and a 10 pt caption is below the 11 pt reading floor (Y1, критично). Its 36-44 pt title overlaps Y1's
  32-40 pt at 36-40; the token sheet uses 36. WCAG large text (18 pt, 14 pt bold) is raised to 24 pt and
  18.7 pt bold (C1).
- **"Every slide needs a visual"** (`pptx`) yields to a text-only `thesis` slide, 2-3 statement rows or one
  sentence, in a talk (L50: ref 2, two pillars with no picture, 21 words).
- **Big numbers.** A 60-72 pt stat callout (`pptx`) is a `frontend-design` default tell: hero size only for the
  number that is the claim, with its base and method (T7).
- **Kept from the `pptx` avoid list** (its ban on accent lines, edge stripes and single-side borders on
  cards): no accent line under titles, no single-side stripe on a card. A meaning colour (L40), such as the own
  deck's 3 px channel edges, moves to a chip, an icon or a full border of 1 pt or more, and a card never relies
  on a shadow (C7); `html-deck` marks a trap card with a full border plus the «Симптом:» line.
- **Sandwich.** A dark title and close around light content would flip luminance at the close: the close
  stays in the content family; only title and dividers switch (C4).
- **Centred titles.** Content titles align with the content left edge (G1); only title and dividers centre.
- **`frontend-design` tells** stay banned as house rules: all-caps labels, a tracked eyebrow on every heading,
  mono for labels, an accent word inside a title (Y5, Y6, T9, L15; `references/visual-system.md` §7).

## Common Mistakes

| Mistake | Measured | Correct |
|---|---|---|
| Bright accent as text on light | #49C5B1 on #FFFDF9 2.09:1 | accent-text #2B766A, 5.30:1 |
| Yellow accent as text on white | #F2C811 1.61:1 | #7A5F00 6.06:1; #F2C811 only as a fill under #0D1A24 (10.96) |
| White on a mid-cyan header | 2.48:1 on #00B0F0, 3.06:1 on #0F9ED5 | white on #0B6E99, 5.67:1 |
| Title box per template | 10 x positions, 11 sizes | one title box token (G1) |
| Page numbers on some templates | 15 of 52 slides | every slide but title and dividers (K1) |
| Imports keep their fonts and scale | 20 font names, 10.5% of words off whole pt | one sans + one mono, sizes on the scale (Y2) |
| Full-window screenshot | UI at 7-9 pt, framed at 60% width 4-5 pt | zoom and crop to 9 pt or more (S1) |
| Setup-state demo poster | 35-40% blank setup cells | the result moment (S2) |
| Untitled still | 4 stills untitled (plus a photo), 2 titles hidden behind the image | title or 10-word caption plus demo marker (S6) |
| Logo wall | 22 logos at 7-8 pt | 12 boxes or fewer, one highlight (V6) |
| White card on off-white | 1.02:1 | fill step 1.15:1 or a 1 pt border (C7) |
| Uppercase Cyrillic with digits | «з» read as «3» | sentence case, «N / M» (Y6) |

## Verify before done

`deck_lint.py --tokens` exits 0 in every theme -> every plan slide carries an archetype -> the `deck-review`
loop reaches 0 критично and every бажано is fixed or accepted -> state what a headless check cannot verify:
projector colour loss, viewing distance, and Windows font metrics when rendering on Linux.
