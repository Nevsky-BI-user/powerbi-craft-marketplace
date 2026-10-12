# slide-design: visual system

> The token sheet and the deck-wide rules it encodes: type scales, title box and grid, margins and brand,
> template families and luminance, colour tokens with computed pairs, typography, consistency, and the
> mapping to CSS custom properties, icon symbols and pptx THEME slots. Numbers and severities belong to `deck-review`
> references/rubric.md (check IDs in brackets); contrast is the `pbi-color-accessibility` reference.md §1
> formula. Every ratio printed here was computed with that formula from exact hex values. Evidence: a
> 52-slide vendor platform deck ("ref N") and a 33-slide own HTML reading deck ("own N").

## §1. Token sheet

`assets/tokens.example.json` (schema `deck-tokens/1`) is the shape. Fill it before slide 2 exists, then let
`deck-review` rate it from the project folder: `python3 <deck-review>/scripts/deck_lint.py --tokens tokens.json`,
where `<deck-review>` is the `deck-review` skill folder (or `--tokens deck.html`, which reads the CSS `:root`
blocks of §9). Exit 0 means every pair passes in every
theme; at this stage the lint fails on бажано by default; exit 2 is bad input.

| Field | Holds | Read by |
|---|---|---|
| `meta` | name, note, canvases | humans |
| `fonts` | `sans`, `mono` (family, fallback stack, weights, licence, Cyrillic), `pptx` pair | Y2, html-deck H3, pptx THEME |
| `type` | `talk` and `reading` scales, each in `pt` and `px`; weights; line heights | Y1, Y2, T4, V7 |
| `geometry` | `pt` and `px`: canvas, margin, footer edge, decoration clearance, eyebrow, title and content boxes, page number, brand corner; `grid` | G1-G3, G6, K1 |
| `families` | at most 2 template families and the archetypes each owns | K2, C4 |
| `themes` | `light` and `dark`: `colors` by role plus `pairs [{fg, bg, class, ratio}]` | C1, C2, C6, C7, G7 |
| `void` | always-dark code and diagram surfaces, identical in both themes | C1 |
| `status` | pill fills and inks per state, Ukrainian labels | V8 |
| `meaning`, `icons` | colour meaning map, concept to icon map | C5, V1 |
| `components` | pill, demo marker, card, highlight | V8, S6, C7, S3 |
| `css`, `pptx_theme` | engine mapping (§9) | html-deck, pptx |

**Pair classes.** `deck-review` scripts/thresholds.json `tokens.classes` points each class at its check key, so
the minimum is never restated in a second place:

| Class | Minimum (check key) | Used for |
|---|---|---|
| `body` | 4.5 (C1.body) | any text a reader must read |
| `large` | 3 (C1.large) | text at 24 pt or more, or 18.7 pt bold or more, only |
| `header` | 4.5 (C2.header) | table header text on its fill |
| `ui` | 3 (G7.stroke_contrast) | strokes, rules, icon lines on their background |
| `card` | 1.15 (C7.card_step) | card fill against the page |
| `active` | 7 (C6.active_min) | active text in a zoom build |
| `status` | 4.5 (V8.label_contrast) | pill label on its fill |
| `dim` | 2 (C6.dim_target) | zoom context; reported as info, never a failure |

`tokens.default_pairs` lists the 19 pairs the lint rates whenever both roles exist: ink and ink-2 on both
surfaces, accent-text on both surfaces, on-accent on accent-fill, link, header, line, card, active, dim, the
three void inks, and the three status pills.

**Fill order.** (1) Canvas and mode from deck-plan.json. (2) Fonts: Cyrillic coverage and licence first
(§7). (3) Type scale: copy §2 and change a value only within its floor. (4) Geometry (§3, §4). (5) Families
and the archetypes each owns (§5). (6) Colours per theme: surfaces and inks, then accent-fill, on-accent,
accent-text derived per surface, header, line, dim, highlight (§6). (7) Void and status. (8) Meaning and
icon maps. (9) Rate with `--tokens`; fix the token, never an individual slide.

## §2. Type scales (Y1, Y2, T4, V7; L31, L32)

| Role | Talk pt | Talk px | Reading pt | Reading px | Rule |
|---|---|---|---|---|---|
| `divider` | 54 | 72 | | | 48-60 pt (Y1); title slide h1 too |
| `title` | 36 | 48 | 30 | 40 | one size deck-wide, 32-40 pt in talk (Y1, G1) |
| `hero` | 60 | 80 | | | at least 2x body, only for a number that is the claim (T7) |
| `card_heading` | 27 | 36 | 21 | 28 | card and hub names over body text, a level between body and title (Y1 levels; ref 45: 28 over 20 pt); thesis rows (D2 `min_pt=24`) |
| `body` | 20 | 28 | 15 | 20 | 18 pt or more in talk (Y1 `body_pt`), 11 pt floor in reading |
| `label` | 18 | 24 | | | diagram and table labels; never below the 14 pt talk floor |
| `eyebrow` | 14 | 20 | 12 | 16 | 12-16 pt talk, 11-16 pt reading (T4) |
| `code`, `code_hero` | 18, 24 | 24, 32 | 12 | 16 | 18 pt talk, 11 pt reading, hero line 24 pt (V7) |
| `footer` | 10 | 16 | 9 | 12 | 9 pt or more (Y1, K1) |
| `dek`, `small` | | | 18, 12 | 24, 16 | reading only |

- **Two scales, one per canvas.** The pt column serves pptx and other 960x540 pt engines; the px column
  serves the 1280x720 HTML canvas. Every px value is a multiple of 4, so it prints at whole pt (x 0.75):
  28 px = 21 pt, 20 px = 15 pt, 16 px = 12 pt. They are not conversions of each other; a deck declares one
  and Y2 then allows no size off it (`offscale_words_max=0`).
- **Levels.** At least 1.3x between a heading and what it heads (Y1): title to body 1.8 (pt) and 1.71 (px),
  divider to title 1.5, hero to body 3.0 and 2.86. A card name is a third level: card heading to body 1.35
  and title to card heading 1.33 (pt); reading 1.4 and 1.43. In talk px no multiple of 4 holds both (36.4-36.9
  px needed), so 36 px keeps the title level at 1.33 and sits at 1.29x body; 40 px would leave the title 1.2x
  above the card names, which the lint flags. A card name at body size and bold weight is 1.0x (ref 52 sets
  21.4 over 18 pt, 1.19x; L31).
- **Cut words, not points.** Never autofit a title (T3) or shrink body below the floor; split the slide.
- **Title character budget** (T3, wording owned by `deck-storyline`): 45 Latin or 40 Cyrillic characters at
  36 pt, scaled by 36 / size, so 54 and 48 at the 30 pt reading title.
- **Evidence.** Ref uses 11 title sizes (24-54 pt), puts 26.2% of 2,449 words below 12 pt, and 258 words
  (10.5%) at non-integer sizes from scaled imports; its legible slides all sit at 17 pt or more. The own deck
  sets 97% of words below 13.6 px (about 10 pt), titles at 29 px (21.8 pt), and 12.5 and 13.5 px body sizes
  that print off whole pt.

## §3. Title box and grid (G1, G4-G6, G8, D1; L23, L26-L28, L30)

| Box (pt; px = x 4/3) | x | y | w | h | Note |
|---|---|---|---|---|---|
| eyebrow | 36 | 36 | 840 | 18 | only when it carries the part or the series item (L15) |
| title | 36 | 60 | 888 | 45 | 36 pt, weight 600, left, one line |
| content | 36 | 120 | 888 | 366 | at most 5 zones (D1) |

- **Title box is one token** (x, baseline, size, weight, colour, alignment): drift at most 2 pt across
  content slides, one size, and its x equals the left edge of the content block (G1). Title, dividers and
  photo are exempt (`title_box_exempt`) and may centre. Ref: title x takes 10 values (7.2 to 155.4 pt plus
  centred); ref 25 sets its title 27 pt right of its table. Own deck: one title box on 32 of 33 slides.
- **12-column grid.** 888 pt = 12 columns of 52 pt + 11 gutters of 24 pt (px: 69.33 and 32). Zones: 3
  columns 204 pt, 4 = 280, 5 = 356, 6 = 432, 7 = 508.
  - Text plus image split: text in 5 columns (share 0.40, inside G6 0.35-0.45), image in 7; image top and
    bottom aligned with the text zone within 2 pt; at most 4 items.
  - Hub: 3 cards of 4 columns or 4 cards of 3 columns.
  - Text columns at least 170 pt wide (Y4), so at most 4 text columns across the content box.
- **Connectors** attach at card centres within 2 pt; re-route after moving a card (G4). Ref 34: bottom
  connectors land about 88 pt right of the card centres (pixel-checked).
- **One process axis**, numbered 1..N; vertical position only when it encodes something (G8). Ref 15
  alternates rows; ref 3 rises to encode maturity (good).
- **Fill.** More than 25% empty below the content while text sits below body size: enlarge the type or
  relayout; card bottom padding within 10% of the top (G5). Own 2, 3, 4, 10 leave 30-33% empty with text at
  10-12.5 px; own 24 leaves about 200 px dead gap inside equal-height cards; ref 45 about 58 pt per card.

## §4. Margins and brand (G2, G3, K1; L24, L25, L59)

- **Safe margin 36 pt (48 px)** on every side, identical within a family; only full-bleed media cross it (G2).
- **Footer band:** the page-number baseline sits 18 pt (24 px) above the bottom edge (G2 `footer_edge_pt`);
  the page number uses the footer size of the declared scale (10 pt, or 16 px = 12 pt), right-aligned at the
  right margin, on every slide except the title and dividers (K1, position drift at most 2 pt).
- **Decoration** keeps 16 pt (22 px) clear of content (G3).
- **Brand corner** of at least 60x60 pt (80 px) in one fixed corner, reserved on every slide of the family
  that shows the mark, never on some and not others (G3). A title that runs into the corner loses 5
  characters of its budget (T3 `logo_minus`).
- **Evidence.** Ref 19-24 put the title at x=7.2 pt and a pill about 3 pt from the edge; ref 13 keeps 23-26
  pt side margins; a screenshot on ref 40 reaches 945 pt; the corner mark overlaps a step on ref 3 and a
  screenshot card on ref 46 and appears only on 2-6. Own deck top padding is 38 px (28.5 pt), so every
  eyebrow sits inside the margin.

## §5. Families and luminance (K2, C4, V5; L39, L47, L60)

- **At most 2 template families with fixed roles** (K2), declared in the token sheet `families` and in the
  plan. Default: light content, dark title and dividers (the dark family owns the `dividers` group).
- **One luminance per section.** Light and dark flip only into or out of a title, divider, demo divider or
  appendix divider (C4). The close stays in the content family.
- **Bright media in a dark section** are dimmed, framed or put under a 30-40% scrim (C4). A 40% black scrim
  over white gives #999999: it tames glare, but white text on it is only 2.85:1, so a caption needs its own
  band of at least 54% black (white on #757575 = 4.61:1). Blend math: `pbi-color-accessibility`
  reference.md §11.
- **Restyle every import** to a family: background, corner radius, flat logos, no foreign gradients or
  lighting (V5). Ref 23 keeps a glossy illustration on its own gradient, ref 25 a light document table over
  about 80% of a dark slide, ref 26 tilted 3D logos.
- **Deriving the dark family from the light one:** follow `pbi-design-system` reference.md §1.9 R1-R6
  (role-based map, one pass, then a programmatic audit of pair inequalities), then rate both themes with
  `--tokens`.
- **Evidence.** Ref uses at least 9 families plus full-bleed stills; with each switch the title moves, the
  hierarchy changes (title 36 pt on light vs 32.1 or 34.7 pt on dark) and page numbers vanish; 5 of 6
  transitions in ref 27-33 flip luminance and 6 flips run through 45-52 (7 counting 44 to 45); ref 8 switches at a divider (good).

## §6. Colour tokens (C1-C7, G7, V8; L36-L42)

| Role | Light | Dark | Meaning |
|---|---|---|---|
| `surface`, `surface-2` | #FFFFFF, #E6ECF1 | #0F1B26, #1B2C3B | page, card |
| `ink`, `ink-2` | #0D1A24, #41586A | #E3ECF2, #9DB2C0 | text, muted text |
| `line` | #7A8B97 | #5A7386 | strokes and rules (`ui`) |
| `accent-fill`, `on-accent` | #F2C811, #0D1A24 | same | the one element the claim names; its text |
| `accent-text` | #7A5F00 | #F2C811 | accent as text |
| `link` | #00668F | #5CC8FF | links, collected on the close |
| `header-fill`, `header-ink` | #0B6E99, #FFFFFF | same | table headers |
| `dim` | #A9B6C0 | #384E5F | zoom context |
| `hl`, `hl-ink` | #CC4410, #FFFFFF | same | screenshot highlight and number badges (S3) |
| `void`, `void-ink`, `void-ink-2`, `void-accent` | #0A1420, #DDE8EF, #9BBBCE, #F2C811 | same | code and diagram boards |

**Accent-fill vs accent-text (C1).** A bright accent is safe as a fill and fails as text on light:

| Accent | As text on light | As a fill, with dark text | Accent-text token on light |
|---|---|---|---|
| #F2C811 | 1.61 on #FFFFFF, 1.51 on #F6F8FA | #0D1A24 on it 10.96 | #7A5F00: 6.06 on #FFFFFF, 5.09 on #E6ECF1 |
| #49C5B1 | 2.09 on #FFFDF9 | #000000 on it 9.90 | #2B766A: 5.30 on #FFFDF9 |
| #5CC8FF | 1.88 on #FFFFFF | | #00668F: 6.37 on #FFFFFF |

- Derive accent-text by darkening the hue until it passes 4.5:1 on every light surface it sits on (surface
  and surface-2), then rate it. On dark the bright accent is its own accent-text (#F2C811 on #0F1B26 10.83;
  ref #8BF5E2 on #001927 13.91).
- Never set accent-text on accent-fill: #7A5F00 on #F2C811 is 3.77.
- 3:1 is allowed only for text at 24 pt or more, or 18.7 pt bold (C1 `large`); a bright accent at 2:1
  fails at any size.
- **Table headers** keep 4.5:1 with one fill per table (C2): white on #00B0F0 2.48 and on #0F9ED5 3.06 (ref
  17, 18, 25, with a lighter second band on 18 and 25) become white on #0B6E99 5.67.
- **Gradient text** only at 40 pt or more for at most 5 words, judged at its worst stop (C3). Ref 8 sets a 54
  pt gradient divider that reads well; ref 10 uses gradient emphasis at 18 pt at about 3.0-3.3:1. PDF
  extractors report gradient text as #000000 (L78), so the PDF path sends it to could-not-verify.
- **Cards** separate by a fill step of at least 1.15:1 or a 1 pt border, never by shadow alone (C7): white
  on #FFFDF9 is 1.02 (ref 2, 34, 36) and own #F6F8FA on white 1.06; the token sheet uses #E6ECF1 on white
  1.19 and #1B2C3B on #0F1B26 1.22 (or a fill such as #EDE7DA on #FFFDF9, 1.21).
- **Strokes** meant to be seen on dark are at least 1.5 pt (2 px) and 3:1 (G7): `line` 3.52 on white and
  3.51 on #0F1B26. Ref 32's 1 px grey frame nearly vanishes; ref 28's grey connectors #7D7E7F hold 4.07.
- **Zoom dimming** (C6): context at about 2:1 (`dim` #A9B6C0 on white 2.07, #384E5F on #0F1B26 2.01), active
  text at least 7:1 (ink 17.64 light, 14.56 dark). Ref 30: #3F5866 on #002134 2.21, active white 16.57.
- **Status pills** (V8): one fill per state, label at least 4.5:1: white on #1F7A50 5.31, #0B4F70 on #D7EAF6
  7.18, #41586A on #E3E8EC 6.02. Ref GA and preview pills share #6BE9BD.
- **Highlight** for screenshots (S3): `hl` #CC4410, used nowhere else; as a 3 pt stroke it holds 4.77 on
  white, 3.65 on #0F1B26 and 3.88 on the void board (`ui` class). Number badges set digits on it at the
  eyebrow size, below the C1 large size, so `hl-ink` on `hl` is a `body` pair: white 4.77. #D9480F failed
  that pair with either ink (white 4.30, #0D1A24 4.10).
- **Colour meaning map** (C5): structure stays greyscale; saturated colour marks only the 1-4 entities the
  claim names; each colour keeps one meaning across slides and legends, recorded in `meaning`. The own deck
  is the model: four channel colours keep one meaning across cards, diagram strokes and legends. They hold
  7.73-11.55 as strokes on its void board and 1.60-2.40 as text on white, so on light surfaces they stay
  fills behind ink text and chips, never text; a meaning stroke on light needs a darker variant of 3:1 or
  more (`ui` class), derived like accent-text. Ref 28 colours three marks and one hexagon (good); ref 7 uses
  outline colours that mean nothing.
- **No blanket 7:1.** The projector margin is the raised large-text size in C1 (24 pt and 18.7 pt bold,
  where WCAG uses 18 pt and 14 pt bold); 7:1 applies only to active text in a zoom (C6). Projector colour
  loss cannot be measured headless: say so in the review.

## §7. Typography (Y3-Y6, T9, V7; L33-L35, L70, L71)

- **Centring** only for labels of 1-2 lines; left-align anything longer (Y3). Ref 3 centres 5-7-line
  paragraphs; ref 36 centres 5-9-line columns 118 pt wide.
- **Measure:** body lines of 35-60 characters, columns at least 170 pt, a left-column statement of at most 12
  words and 4 lines (Y4). Ref 7 wraps a statement into 7 lines of 2-3 words; the own deck lets its dek run to
  104 characters.
- **One emphasis mechanism per slide** (Y5): weight, or one solid `accent-text` that passes C1. "Accent lead
  of 3-5 words + plain qualifier" is valid when the leads alone tell the story (ref 48 and 50 carry about 14
  words of story in their leads). No accent word inside titles: a `frontend-design` tell kept as a house
  rule, stricter than Y5, which accepts one accent that passes C1; the own deck's yellow title word fails C1
  at 1.61:1.
- **Cyrillic uppercase** (Y6): no `text-transform: uppercase` on Cyrillic strings that mix digits with з, о or
  б in a mono font; write «N / M». The own deck eyebrows on 11-18 read «КРОК 2 3 7». Beyond Y6, keep eyebrows
  and pills in sentence case and in the sans (a `frontend-design` house rule), and set an eyebrow only for
  the part or the series position, never a tracked eyebrow on every heading (L15); mono is for code only
  (V7), and product names stay Latin in the running font (T9).
- **Fonts per engine.** One sans plus one mono deck-wide (Y2).

| Engine | Sans | Mono | Why |
|---|---|---|---|
| HTML | an OFL face with Cyrillic, embedded as a subset woff2 (Inter in the example); fallback Arial, Arimo, Liberation Sans | JetBrains Mono; fallback Courier New, Cousine, Liberation Mono | metric-stable layout on every machine (`html-deck` H3) |
| pptx | Arial or Calibri (Cambria for a serif head) | Courier New | the `pptx` safe list renders true-to-width in LibreOffice QA, and these faces carry Cyrillic |

- Segoe UI and Cascadia are installed only on Windows: on Linux the own deck fell back to DejaVu and overflowed
  `.body` by 14, 37 and 43 px on 25, 26, 28, while Arial-metric fonts left 109, 71 and 67 px free (L65).
- Consolas is QA-unreliable in the `pptx` skill, and ref 17 and 18 set code in two mono faces (Y2, V7).
- Check Cyrillic coverage of any other safe-list face before use; check licence before embedding.

## §8. Consistency (K1, K3, G1; L59, L61)

- **Page number** is a token: every slide except the title and dividers, one fixed position, at least 9 pt,
  generated rather than typed (K1, `html-deck` H2). Ref numbers 15 of 52 slides, drifts from 9 pt at y19.7 to
  8 pt at y25.4, and drops numbers on every dark slide; the own deck types all 33 by hand.
- **Series frame lock** (K3): a series or a zoom pair shares title size and position, item count, body size,
  media box within 2 pt and one status component; build twins from one template with a state class. Ref
  37-42 switch body from 14 to 16 pt, hold 4 items on 39 vs 3 elsewhere, and spread image edges by 26 and 56
  pt; ref 22 sets its title at 28 vs 24 pt; ref 29 and 30 are pixel-locked (good).

## §9. Engine mapping

**CSS custom properties** (`html-deck` writes them into `:root`; `deck_lint.py --tokens deck.html` reads them
back). Every theme role becomes `--<role>`; light values on `:root`, dark on `:root[data-theme="dark"]`; void
and status roles are global; type roles become `--fs-<role>` in px (underscore to hyphen), talk on `:root`,
reading on `[data-mode="reading"]`. The block below equals `assets/tokens.example.json` and passes every
default pair:

```css
:root{
  --surface:#FFFFFF; --surface-2:#E6ECF1; --ink:#0D1A24; --ink-2:#41586A; --line:#7A8B97;
  --accent-fill:#F2C811; --on-accent:#0D1A24; --accent-text:#7A5F00; --link:#00668F;
  --header-fill:#0B6E99; --header-ink:#FFFFFF; --dim:#A9B6C0; --hl:#CC4410; --hl-ink:#FFFFFF;
  --void:#0A1420; --void-ink:#DDE8EF; --void-ink-2:#9BBBCE; --void-accent:#F2C811;
  --ga-fill:#1F7A50; --ga-ink:#FFFFFF; --preview-fill:#D7EAF6; --preview-ink:#0B4F70;
  --planned-fill:#E3E8EC; --planned-ink:#41586A;
  --fs-divider:72px; --fs-title:48px; --fs-hero:80px; --fs-card-heading:36px; --fs-body:28px;
  --fs-label:24px; --fs-eyebrow:20px; --fs-code:24px; --fs-code-hero:32px; --fs-footer:16px;
}
:root[data-theme="dark"]{
  --surface:#0F1B26; --surface-2:#1B2C3B; --ink:#E3ECF2; --ink-2:#9DB2C0; --line:#5A7386;
  --accent-text:#F2C811; --link:#5CC8FF; --dim:#384E5F;
}
[data-mode="reading"]{
  --fs-title:40px; --fs-card-heading:28px; --fs-dek:24px; --fs-body:20px; --fs-small:16px;
  --fs-eyebrow:16px; --fs-code:16px; --fs-footer:12px;
}
```

In SVG reference the variables (`stroke="var(--line)"`), never hex copies of them (the own deck duplicates
its tokens as hex in 7 diagrams).

**Icons** (`icons` map, V1): each entry is one `<symbol id="i-<name>">` held once in the page, used as
`<svg class="ic" aria-hidden="true"><use href="#i-<name>"/></svg>`. The `html-deck` engine renders that
element for `[data-list]` cards and steps, and nothing when the symbol is missing (`html-deck`
references/engine.md §2); a divider or demo divider that carries an icon gets the symbol and the `svg.ic`
by hand. Keep every shape inside the viewBox: H5 measures only text against it, so a clipped icon shows
only on the PNG (P1).

**pptx THEME slots** (`pptx_theme` in the token sheet; pptxgenjs mechanics, hex without `#`, slide masters
and placeholders belong to `pptx`):

| Slot | Role | Example |
|---|---|---|
| `dk1`, `lt1` | ink, surface | 0D1A24, FFFFFF |
| `dk2`, `lt2` | ink-2, surface-2 | 41586A, E6ECF1 |
| `accent1` | accent-fill | F2C811 |
| `accent2` | accent-text | 7A5F00 |
| `accent3` | header-fill | 0B6E99 |
| `accent4`-`accent6` | up to 3 meaning colours from `meaning` | |
| `hlink`, `folHlink` | link | 00668F |

- THEME holds the light family; the dark family is a second slide master whose placeholders carry the dark
  values explicitly. Status pill fills are explicit colours on the pill shape.
- `headFontFace` and `bodyFontFace` take `fonts.pptx.sans`; code runs name `fonts.pptx.mono` explicitly.

**theme-factory presets** are 4 hex plus 2 fonts with no roles and no contrast check: map the lightest
neutral to `surface`, the darkest to `ink`, the saturated colour to `accent-fill`; pick `on-accent` (ink or
white, whichever passes); derive `accent-text` per surface (§6); replace a font without Cyrillic or outside
the pptx safe list for that engine; then rate with `--tokens`.

## §10. Contested claims

| Claim | Verdict here |
|---|---|
| "Projectors need 7:1 for all text" | Not adopted: no general 7:1. The margin is the raised large-text size (C1); 7:1 only for active zoom text (C6). |
| "Dark slides are always better" | Not adopted: the measured harm is the flip (C4), not the polarity. Choose by the room, then hold one luminance per section. |
| "An accent line under the title looks designed" | Rejected: the `pptx` avoid list bans it, and it moves with every title wrap (G1). |
| "Colour alone can carry status" | Rejected: one pill with a text label (V8); colour never alone (`pbi-color-accessibility` §7). |
| "Every slide needs a visual" | Settled in SKILL.md: a text-only `thesis` slide (2-3 statement rows or one sentence) is valid in a talk. |
| "The 8 pt report floor works on slides" | Rejected: `pbi-typography` and `pbi-design-system` floors are screen-report densities; talk text floors at 14 pt (Y1). |
