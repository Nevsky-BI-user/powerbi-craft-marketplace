# pbi-design-system — Token Reference

> **Design tokens live in `pbi-design-system`** — this file is the synced copy.
> If values ever differ, `pbi-design-system` wins — re-sync this file.
> Units: **typography in pt** (Power BI native), **layout in px** (report JSON coordinates).
> Formats: PBIP; report **PBIR-Legacy (single report.json) OR PBIR enhanced**; model TMDL.
> Exact theme property/visual-type names come from the verified schema reference
> (the theme-schema introspection notes) — never from memory.

---

## 1. Color

### 1.1 Core palette (roles)

| Token | HEX | Usage |
|---|---|---|
| `color/brand` | `#063E61` | Hero KPI, titles, selected tab, primary series, table headers |
| `color/accent` | `#3781F0` | Interactive elements, links, highlight series, focus |
| `color/warning` | `#FFC107` | Watchlist states, secondary accent (dark text only on it) |
| `color/warning-text` | `#916400` | Warning as TEXT on white (5.2:1 AA) |
| `color/good` | `#2B9348` | Positive marks/fills (3.9:1 — marks & large text only) |
| `color/good-text` | `#107C10` | Positive as small text on white (5.4:1) |
| `color/bad` | `#D64550` | Negative marks/fills (4.3:1 — marks & large text) |
| `color/bad-text` | `#D13438` | Negative as small text on white (4.9:1) |
| `color/neutral-data` | `#3C648A` | Context series, "other", non-focus data |

**Brand navy drift (MUST READ).** Canonical brand = **`#063E61`** (icon library, all NEW
themes/reports). One audited production report uses `#003A5D` as `dataColors[0]`
(= `ThemeDataColor ColorId 2` in its report.json).

- New theme / new report → `dataColors[0] = #063E61`.
- Editing an existing report → resolve `color/brand` to the *report's own theme* via
  `ThemeDataColor`; never introduce a second navy hex. One report = one navy.
- Those near-navies (`#0C3350 #0B4467 #0A3D91 #002C46 #001D2F #1B3A5C`) are drift, not tokens.

### 1.2 Sequential brand ramp (`ramp/brand-seq`)

White-mix tints of `#063E61`, lightness monotonic. For ordinal categories, heat maps,
gradient CF. Dark = more. Never rainbow.

```
#E6ECEF  #C1CFD8  #9BB2C0  #6A8BA0  #386581  #063E61
(seq-100) (seq-200) (seq-300) (seq-400) (seq-500) (seq-600 = brand)
```

### 1.3 Diverging & RAG

| Token | Value | Notes |
|---|---|---|
| `ramp/diverging` | `#D13438` ← `#F3F2F1` → `#107C10` | Midpoint anchored at the *meaningful* center (0, 100 % of plan), never the data mean |
| `color/null` | `#9E9F9F` | Divergent/gauge "no data" stop (theme `"null"` key) — same value as `color/text-disabled` |
| `ramp/rag` | `#009051 #02BD3D #C2E330 #FFE521 #FF7E0D #F23711` | 6-step green→red CF ramp. Reference from here — never re-hardcode per visual |

Red/green NEVER alone: pair with icons (▲▼ via `icon-set-manager`), labels, or position.
Binary comparisons prefer blue vs orange (`#063E61` vs `#FFC107`/`#E69F00`) — colorblind-safe.

**Why `ramp/rag` steps are emitted as hex literals.** The six step values are design-system
tokens only — they are NOT theme keys (unlike `good`/`neutral`/`bad`), so a CF rule using them
cites the hex from the table above verbatim. This is the pattern §8 rule 8 already prescribes
(«Ramps referenced from §1.2–1.3, never inlined ad hoc»): the token lives here, the hex is its
value. Never invent a seventh step or re-tint one per visual.

### 1.4 Neutrals: text, surfaces, borders

| Token | HEX | Contrast on white | Usage |
|---|---|---|---|
| `color/text-title` | `#063E61` | 10+ : 1 | Page/section/card titles |
| `color/text-body` | `#333333` | 12.6 : 1 | Values, labels, table body. In report JSON: `ThemeDataColor {ColorId 1, Percent 0.2}` |
| `color/text-secondary` | `#605E5C` | 4.6 : 1 (AA) | Captions, axis labels, legend, unselected tabs |
| `color/text-disabled` | `#9E9F9F` | 2.5 : 1 (fails AA) | Disabled/inactive ONLY |
| `color/text-inverse` | `#FFFFFF` | — | Text on brand/dark fills |
| `color/surface` | `#FFFFFF` | — | Card/visual background |
| `color/surface-alt` | `#FAFAFA` | — | Zebra rows (tableEx `backColorSecondary`) |
| `color/page-bg` | `#F5F4F2` | — | Page canvas — the ONE page gray |
| `color/border` | `#E6E6E6` | — | Card borders, dividers, gridlines — the ONE border gray |
| `color/hover-tint` | `#E6ECEF` | — | Button/tab hover fill (10 % brand) |
| `color/pressed-tint` | `#CDD8DF` | — | Pressed state (20 % brand) |
| `color/selection-tint` | `#C9DDFB` | — | Selected slicer chips, row selection |

### 1.5 Theme `dataColors` order (categorical)

Brand first, hue-separated, max 6–8 categories before grouping into "Other":

```json
"dataColors": ["#063E61", "#3781F0", "#FFC107", "#2B9348",
               "#D64550", "#3C648A", "#79B0FF", "#916400"]
```

Sentiment keys: `"good": "#2B9348", "neutral": "#FFC107", "bad": "#D64550"`;
divergent stops: `"minimum": "#D13438", "center": "#F3F2F1", "maximum": "#107C10"`.

### 1.6 Structural theme colors (theme JSON top level, preferred names only)

```json
"firstLevelElements":  "#333333",
"secondLevelElements": "#605E5C",
"thirdLevelElements":  "#E6E6E6",
"fourthLevelElements": "#9E9F9F",
"background":          "#FFFFFF",
"secondaryBackground": "#F5F4F2",
"tableAccent":         "#063E61"
```

Never mix with legacy aliases (`foreground`, `backgroundLight`, …) in one theme.

### 1.7 Color encoding rules (WHERE each syntax is legal)

| Location | Syntax | Example |
|---|---|---|
| Theme top level, `textClasses` | plain hex string | `"color": "#333333"` |
| Theme `visualStyles` cards | fill object | `{"solid": {"color": "#E6E6E6"}}` or named `{"solid": {"color": "good"}}` |
| report.json / visual.json `objects` | `ThemeDataColor` expr **preferred** | `{"expr":{"ThemeDataColor":{"ColorId":2,"Percent":0}}}` |
| DAX field-value CF | named theme color string | `"good"`, `"bad"`, `"maxColor"`, `"midColor"`, `"minColor"`, `"nullColor"` |

`ColorId` mapping (verified on a production report): `0` = background (white), `1` = foreground (black;
`Percent 0.2` renders `#333333`), `N≥2` = `dataColors[N−2]`. **Verify against the target
report's actual theme before emitting.** Hex literals only for colors genuinely absent
from the theme (e.g. `ramp/rag` steps).

### 1.8 Hyperlink colors (theme top-level keys)

| Token | HEX | Theme key |
|---|---|---|
| `color/hyperlink` | `#3781F0` | `"hyperlink"` — reuses `color/accent` |
| `color/hyperlink-visited` | `#3C648A` | `"visitedHyperlink"` — reuses `color/neutral-data` |

### 1.9 Theme inversion (dark ↔ light)

Verified converting a 30-page / 270-visual report (195 files + 8 TMDL) from `sqlbi-dark` to
`sqlbi-light`. **Six binding rules. R1–R4 govern the sweep, R5–R6 run after it.** Each is a
rule, not an illustration — read them as instructions.

#### R1 — Neutrals MIRROR the ramp; accents / brand / semantics DEEPEN. Never mirror an accent.

Classify every hex **by role before touching it**, then apply the operation for that role:

| Role | Operation | Verified map (dark → light) |
|---|---|---|
| **Neutral** — text, surface, border, gridline, page-bg | **mirror** its position on the lightness ramp | `e2e8f0↔0f172a`, `cbd5e1↔334155`, `94a3b8→475569`, `334155→e2e8f0`, `1e293b→ffffff`, `0f172a→f1f5f9` |
| **Accent / brand / good-bad-warning** | **deepen** one–two tailwind steps: **−400 → −600/−700**, hue kept | `818cf8→4f46e5`, `34d399→047857`, `fbbf24→b45309`, `f87171→b91c1c`, `22d3ee→0e7490` |

**Reason (this is why the rule exists):** a tailwind-**400** is tuned to read on a dark canvas;
on white it **fails 4.5:1**. Mirroring it would make it *lighter still* — the opposite of what a
light theme needs. Symmetry is a property of neutrals only; accents move in one direction.

#### R2 — ONE map-driven pass per file. Never a chain of sequential find-replace.

Build the complete old→new map first, then apply it in a **single** regex pass (one alternation,
or one `re.sub` with a lookup callback). Sequential replacements compose: running `A→B` and then
`B→C` over the same file turns the original **A into C**. The corruption is silent — the file
still parses and still looks like valid colors.

#### R3 — The sweep must catch `%23`, and colors that are not hex at all.

- **`%23` — the URL-encoded `#`.** TMDL SVG measures encode `#` as `%23` inside the data-URI, so
  the same navy exists as `#1e293b` in JSON and `%231e293b` in a measure. Match **both forms in
  the same pass** (`(#|%23)hex`), or every SVG-measure visual stays dark after conversion.
- **Page wallpaper can live in the THEME as a base64 data-URI, not as a color:**
  `visualStyles.page["*"].background.image` =
  `{"name": "ModernGradient", "scaling": "Fit", "url": "data:image/png;base64,iVBORw0…"}`.
  One such key bloats theme.json to ~1.8 MB, and a hex sweep cannot touch it in principle —
  the asset must be **regenerated or removed**. Symptom: after a "complete" sweep every page
  still has a dark background under light content. Do not look for wallpaper in page.json.
- **Adjacent theme trap:** `page["*"].outspace` with `"transparency": 100` **switches the color
  off** — the theme names a light color but paints nothing, and Desktop's own dark canvas shows
  through as a black frame around the page. Theme-file mechanics → `pbi-theme-json`.

#### R4 — Semantic theme roles are NOT inverted mechanically. Invert values, never assignments.

| Key | After converting to light | Why |
|---|---|---|
| `foregroundSelected` | stays **LIGHT** | it sits on the accent fill, not on the canvas |
| `foregroundLight`, `foregroundNeutralLight` | stay **DARK** | they are low-emphasis text on the light surface |

Flipping these along with everything else is how a converted theme ends up with white text on
white chips. Exclude them from the map explicitly.

#### R5 — After the sweep run a PROGRAMMATIC luminance audit. "Check the contrast" is not a step.

Script it as a separate pass over the swept files:

1. Walk every color literal in JSON/TMDL and **classify each hex by its own JSON path** —
   `fontColor` / `textStyle` → **text**; `background` / `fill` → **surface**.
2. Pair each text color with the surface it actually sits on and compute the ratio
   (text ≥ 4.5:1, ≥ 3:1 large; non-text marks ≥ 3:1).
3. **Score against the REAL canvas, never against white.** `#dc2626` on canvas `#f1f5f9` =
   **4.41:1 — an AA failure** that looks like a pass when computed vs `#ffffff`; deepened to
   `#b91c1c` (5.91:1). A tinted canvas eats ~0.2–0.3 of the vs-white figure — the whole width
   of the AA margin.

This audit found **11 defects in 4 visuals** after the sweep already "looked complete" — opening
the report in Desktop had surfaced only two problems (a black frame around the page, an invisible
matrix header). Eyeballing is not a substitute for the audit.

#### R6 — Inversion preserves equalities → verify INEQUALITIES of pairs, not values.

`border.color` == `background.color` (`#1e293b`/`#1e293b` — border deliberately suppressed, the
card held by its shadow) inverts to `#ffffff`/`#ffffff`: still invisible. Assert
`border ≠ background`, `gridline ≠ background`, `text ≠ its own surface` programmatically, not by
eye — and remember the equality may have been **intentional** in the source theme.

#### Swatch trap — SYMMETRIC, so it is not created by the conversion

A swatch painted in the token it demonstrates vanishes when the surface flips. On a white card,
`surface #ffffff`, `border #cbd5e1`, `page-bg #f1f5f9` and ramp mid `#e2e8f0` scored
**1.18–1.24:1** as `■`/`●`/`██` glyphs.

**The trap is symmetric:** on the dark theme the DARK neutrals vanished exactly the same way, so
the defect **predates the conversion** — inversion only swaps which end of the ramp disappears.
Never report it as "the conversion broke it", and never assume the other direction was clean:
audit swatches in both themes.

Fix for any swatch under 3:1 against its OWN surface: outline glyph (`◻`/`○`) in a readable
neutral + the hex in the label. A label demonstrating a text color (`min: white text 6.18:1`
painted `#f1f5f9`) sits on the card, not on the fill — paint it a neutral.

---

## 2. Typography

**Segoe UI family only.** Emphasis = switch family to `"Segoe UI Semibold"` where the
property is a font family; `bold: true` only where no family switch exists. Never both;
never external web-font stacks. Sizes in **pt**; hard floor **8 pt**; ramp ratio ≈ 1.2–1.25.

| Token | Size | Family | Color | Usage |
|---|---|---|---|---|
| `type/callout-hero` | 28 pt | Segoe UI | `color/text-body` | Hero KPI value (one per page); value:label ≈ 3:1 |
| `type/hero` | 18 pt | Segoe UI Semibold | `color/text-title` | Page title (one per page, top-left) |
| `type/header` | 14 pt | Segoe UI Semibold | `color/text-title` | Section headers |
| `type/title` | 12 pt | Segoe UI Semibold | `color/text-title` | Visual & KPI-card titles |
| `type/value` | 12 pt | Segoe UI | `color/text-body` | Dense-grid card values |
| `type/label` | 10 pt | Segoe UI | `color/text-body` | Field labels, table body (buttons: 10 pt but Semibold/`text-secondary` per master-theme actionButton) |
| `type/small` | 9 pt | Segoe UI | `color/text-secondary` | Axis labels, legend, captions, slicer items (as shipped in master-theme) — never below 8 pt |

### 2.1 Theme `textClasses` block (canonical)

```json
"textClasses": {
  "callout":    { "fontFace": "Segoe UI",          "fontSize": 28, "color": "#333333" },
  "title":      { "fontFace": "Segoe UI Semibold", "fontSize": 12, "color": "#063E61" },
  "header":     { "fontFace": "Segoe UI Semibold", "fontSize": 14, "color": "#063E61" },
  "label":      { "fontFace": "Segoe UI",          "fontSize": 10, "color": "#333333" },
  "largeTitle": { "fontFace": "Segoe UI Semibold", "fontSize": 12, "color": "#063E61" },
  "smallLabel": { "fontFace": "Segoe UI",          "fontSize": 9,  "color": "#605E5C" },
  "lightLabel": { "fontFace": "Segoe UI",          "fontSize": 10, "color": "#605E5C" }
}
```

`largeTitle` (visual titles) does NOT scale with `title` — default is absolute 14 pt, so it
is pinned to 12 explicitly. `fontFace` in textClasses vs `fontFamily` in visualStyles.

---

## 3. Layout — 8 px grid

### 3.1 Canvas

| Token | Value | Notes |
|---|---|---|
| `grid/canvas` | **1280 × 720 px** | Default 16:9, `displayOption` FitToPage. ALWAYS read the actual page `width/height` first |
| `grid/canvas-tooltip` | 320 × 240 (up to 550 × 500) | Custom tooltip pages, ActualSize |
| `grid/margin` | 24 px | All four edges → usable 1232 × 672 |
| `grid/columns` | 12 × 88 px + 11 × 16 px gutters = 1232 | Mental column grid |
| `grid/gutter` | 16 px | Between cards/visuals; **8 px** inside one visual group |
| `grid/section-gap` | 24–32 px | Between page sections |

Spacing scale: **4 / 8 / 16 / 24 / 32 only.** Label→value 4; title→chart 8; card→card 8–16;
section→section 24–32. Snap every `x, y, width, height` to integer multiples of 8.
Visuals in a row share `y` + `height`; in a column share `x` + `width`.

### 3.2 Standard component sizes (Σ = 1232, verified)

| Component | Size (px) | Grid math |
|---|---|---|
| KPI card, 6-up row | **192 × 104** | span 2 cols; 6·192+5·16 = 1232 |
| KPI card, 4-up row | **296 × 136** | span 3 cols; 4·296+3·16 = 1232 |
| Hero KPI card | 296 × 176 | span 3, tall |
| Half-width block | 608 × … | span 6; 2·608+16 = 1232 |
| Third-width block | 400 × … | span 4; 3·400+2·16 = 1232 |
| Chart row height | 240 / 280 / 320 | |
| Nav bar / tab strip | full width × **40** | top of page |
| Nav tab / button | 96–200 × **32** | min hit target 32×32 (WCAG 2.2 floor 24) |
| Icon button | 32 × 32 | |
| Dropdown slicer | 192 × 48 (header) / 192 × 32 (headerless) | |
| Filter left rail | **200** wide × full height | when top strip is not enough |
| Card heights | compact **104** / standard **136** / tall **176** | |

### 3.3 Worked vertical stack (1280 × 720 — sums exactly to 720)

```
24 margin + 40 nav/title + 16 + 104 KPI row + 16 + 280 chart row + 16 + 200 table + 24 margin = 720
```

### 3.4 Page anatomy (F-pattern)

Top-left = page title + most important number. Top row = KPI cards. Middle = trends.
Bottom = detail tables. Filters = top strip under title OR 200 px left rail. Logo/refresh
stamp = top-right or bottom-right. **One focal point per page** — one saturated accent.
Hierarchy strength: position > size > weight > color > enclosure. `tabOrder` = reading
order; decorative shapes at low `z`.

---

## 4. Shape: radius, borders, shadows, padding

| Token | Value | Rule |
|---|---|---|
| `shape/radius` | **8 px** | ONE radius per report. cardVisual in THEME: `layout.rectangleRoundedCurve: 8` (master-theme + pbi-theme-json/references/theme-visuals.md §6.6); in per-visual report.json `objects` that report uses `shapeCustomRectangle.rectangleRoundedCurve`; others: `border.radius: 8` |
| `shape/border` | 1 px `color/border` | Default card delimiter |
| `shape/shadow` | **none** | Flat design. Border OR shadow, never both |
| `shape/shadow-optional` | outer, `#000000` @ 88 % transparency, blur 10, distance 2, angle 90° | Only when card sits on a white page and border is insufficient |
| `shape/card-padding` | 12–16 px inner | Content never touches the card edge |

Separation: surface contrast first (`page-bg` vs `surface`), border second, shadow last.
Never an invisible white border as a radius carrier — set radius on the proper property.

### 4.1 Never two edges — and "exactly one" is the wrong invariant

A visual's container `border` and the visual's own `outline` (e.g. its
`shapeCustomRectangle`/outline card) are INDEPENDENT properties, set by different objects.
Both on = the double-border complaint. But the naive fix — "give every visual exactly one
edge" — is wrong, and was caught empirically: a report-wide sweep of **280 visuals** found
only **1** genuine double edge, and **110** visuals with no edge at all — all captions,
icons, labels and dividers, which are borderless BY DESIGN.

The rule has two independent halves:

- **Never two**: if a visual paints its own outline, switch its container border off.
- **Whether it gets an edge at all depends on what it IS**: a **tile** (presents data as a
  card — card, table, matrix, KPI, chart) needs exactly one edge; a **label** (text, icon,
  divider, decorative shape) needs none.

Generalizable lesson: **"exactly one X" invariants are usually wrong** — an audit built on
one flags false positives on every borderless-by-design element. The real invariant is
"never two," plus a separate question of whether X is wanted at all for that element's role.

### 4.2 Shadow is a contrast, not a default — and `Center` is fog

Applying a drop shadow to every visual (e.g. a theme-wide `visualStyles.*.*.dropShadow`
entry) means nothing reads as raised — the shadow stops carrying information. Reserve
`shape/shadow-optional` for what genuinely floats above the page: an overlay panel, dialog,
or flyout — never as a report-wide default.

Second, specific trap: a shadow using the **`Center` preset** renders as a symmetric halo.
Sitting just outside a 1 px border, that halo reads as **a second, softer border** — a
common hidden cause of a "double border" complaint where the JSON shows only one `border`
object. Use a directional preset (`BottomRight`) for genuine elevation; `Center` is fog, not
depth.

---

### 4.3 Two shadows on a shape — and which one an overlay needs

A `shape` visual carries two independent shadows, and they are not interchangeable:

- **Style shadow** (`visual.objects.shadow`, bare `show` + values under `{"id":"default"}`):
  draws **inside** the visual's container and follows the rounded geometry. Because it draws
  inside, it **eats canvas** — the visible shape shrinks by the shadow's margin.
- **Container shadow** (`visualContainerObjects.dropShadow`): draws around the rectangular
  container box, ignoring the shape's radius.

For a rounded overlay (filter panel, dialog): style shadow ON, container shadow OFF, and the
container grows by the shadow margins so the visible rect keeps its intended size — measured
working values at blur 20: left 6, right 6, top 0, bottom 4 (user-calibrated in Desktop,
reproduced byte-exactly by the layout engine; see pbi-filter-panel-bookmark §3.6.1 for the
full geometry).

Corollary for the grid: **the 8-px grid is an optical law — it governs the visible rect, not
the container.** A container inflated by shadow padding legitimately sits off-grid while the
visible edge stays aligned and flush.

## 5. Interactive element states

Power BI has no animation — **states carry all feedback**. Theme `$id` enum for
`actionButton` state cards (`fill`/`text`/`icon`/`outline`): `default | hover | selected |
disabled` — **no** `press`. (`shape` cards take NO `$id` in schema 2.155 — single-element
arrays only; shape hover/selected feedback is per-visual `objects` territory)
in the theme ("On press" exists only per-visual in visual JSON).

| State | Fill | Text | Border | `$id` |
|---|---|---|---|---|
| Default (unselected) | transparent or `color/surface` | `color/text-secondary` | 1 px `color/border` | `default` |
| Hover | `color/hover-tint` `#E6ECEF` | `color/text-body` | — | `hover` |
| Selected / active | `color/brand` `#063E61` | `#FFFFFF` | none | `selected` |
| Pressed (per-visual only) | `color/pressed-tint` `#CDD8DF` | `color/text-body` | — | n/a in theme |
| Disabled | transparent | `color/text-disabled` | none | `disabled` |

Rules: selected ≠ hover (selected is stronger); state never by color alone — add weight
change or a 3 px underline bar; labels sentence case, verb-first; hit target ≥ 24 px
(standard 32). Prefer built-in **Bookmark navigator / Page navigator** visuals over N
hand-made buttons; mechanics → `powerbi-bookmarks`.

---

## 6. Component quick recipes (token bindings)

- **KPI card** = `cardVisual` (classic `card` only for legacy edits): title `type/title`,
  value `type/value` (hero: `type/callout-hero`), fill `color/surface`, radius
  `shape/radius`, border `shape/border`, `visualHeader.show: false`, 4 px label rhythm,
  delta colored `good`/`bad` + icon. Sparkline → `dax-svg`.
- **Table** = `tableEx` (never `table`): header fill `color/brand`, header text `#FFFFFF`
  10 pt bold, body `type/label`/`type/small`, zebra `color/surface-alt`, horizontal-only
  gridlines `color/border`, numbers right-aligned, display units K/M, 0–1 decimals.
- **Matrix** = `pivotTable` (never `matrix`); same tokens + stepped layout, bold subtotals.
- **Slicers**: `advancedSlicerVisual`/`listSlicer` for new work; classic `slicer`
  (Dropdown) acceptable in strips; selection `color/selection-tint`.
- **Charts**: vertical gridlines OFF; horizontal `color/border` 1 px or off when data
  labels on; axis titles off when the title covers them; legend off for single series;
  bars sorted by value unless ordinal axis; one saturated series (`color/brand`),
  context series gray.
- **Theme skeleton** (`visualStyles."*"."*"`): background `color/surface`, border 1 px
  `color/border` radius 8, dropShadow off, visualHeader off. Generation → `pbi-theme-json`.

---

## 7. Legacy 1440 compatibility profile (existing wide report ONLY)

| Parameter | Value |
|---|---|
| Canvas | 1440 × 675 (dashboards, FitToWidth) / 1440 × 720 (drill-through) / 1440 × 3400–3800 (scroll) |
| Page margin | 70 px; content width 1300 |
| Columns | 5 × 248 px + 4 × 15 px gutters (= 1300) |
| Card heights | 106 / 140 / 178 |
| Half-blocks | 642 px + 16 px center gutter |
| Brand navy | theme's `ColorId 2` (`#003A5D`) via `ThemeDataColor` |

Everything else (typography, states, shape, semantic colors) follows canonical tokens.

**ColorId worked example — new report vs a legacy one.** The same expr resolves differently per host
theme: in a NEW report on `master-theme.json`, brand `#063E61` = `dataColors[0]` →
`ThemeDataColor { ColorId: 2 }` (objects mapping: `0`=background, `1`=foreground,
`N≥2`=`dataColors[N−2]`, §1.7); in that legacy report the same `ColorId: 2` resolves to ITS navy `#003A5D`.
The expr is portable, the rendered color follows the host theme — verify the mapping against
the actual theme before emitting.

---

## 8. Anti-drift rules (binding)

1. Theme colors → `ThemeDataColor` / named theme colors, never duplicated hex.
2. One navy per report; canonical `#063E61` for new work.
3. One title size per card tier — `type/title` = 12 pt.
4. Integer 8-px-snapped coordinates; no eyeballing.
5. One `page-bg`, one `surface`, one `border` gray.
6. Defaults live in the theme's `visualStyles`, not re-declared per visual.
7. One emphasis mechanism: Semibold family (or `bold:true` where family unavailable).
8. Ramps referenced from §1.2–1.3, never inlined ad hoc.
9. No tab-character pseudo-layouts inside textboxes — separate visuals.
10. New work uses modern visuals: `cardVisual`, `advancedSlicerVisual`, navigators.
11. Contrast: text ≥ 4.5:1 (≥ 3:1 for ≥ 18 pt / 14 pt bold); non-text marks ≥ 3:1;
    meaning never by color alone.
12. Converting a theme dark↔light = §1.9 R1–R6, all six: role-based map (neutrals mirror,
    accents deepen), one map-driven pass covering `#hex` + `%23hex`, semantic roles left
    alone, programmatic luminance audit against the real canvas, pair inequalities asserted.
13. Container border and own outline are independent — never both on; tiles get one edge,
    labels get none (§4.1); shadow is elevation only, never a default, never `Center` (§4.2).

---

## 9. Compliance checklist (run before reporting done; cite evidence per item)

- [ ] **Pre-flight done**: format detected; theme + `ColorId` mapping verified; actual page
      size read; ground-truth visual read.
- [ ] **Color**: every color maps to a §1 token; report-JSON colors via `ThemeDataColor`;
      one navy; hex literals only for non-theme ramp steps.
- [ ] **Contrast**: text ≥ 4.5:1 (≥ 3:1 large); marks ≥ 3:1; red/green paired with
      icon/label/position.
- [ ] **Typography**: only ramp sizes (§2); Segoe UI family; one emphasis mechanism;
      nothing < 8 pt.
- [ ] **Layout**: all `x/y/width/height` integer multiples of 8; 24 px margins; rows share
      `y`+`height`, columns share `x`+`width`; gaps from {4, 8, 16, 24, 32}; one focal point.
- [ ] **Shape**: one radius (8 px); never two edges — tile gets one, label gets none (§4.1);
      shadow only on floating overlays, directional preset not `Center` (§4.2); padding 12–16 px.
- [ ] **States**: all four distinct per §5; selected ≠ hover; hit targets ≥ 24 px.
- [ ] **Components**: modern visuals (§6); shared defaults in theme, not per visual.
- [ ] **Theme inversion** (only if one happened) — §1.9 R1–R6, each cited separately:
      R1 neutrals mirrored / accents deepened −400→−600-700; R2 one map-driven pass, no
      chained replaces; R3 `%23` forms swept and `page.background.image` data-URI handled;
      R4 `foregroundSelected` still light, `foregroundLight`/`foregroundNeutralLight` still
      dark; R5 programmatic luminance audit vs the REAL canvas; R6 pair inequalities asserted.
- [ ] **A11y**: `tabOrder` = reading order; alt text on non-decorative visuals.
- [ ] **Verification**: JSON/TMDL parses; visual-type keys match the verified list; theme
      card values are ARRAYS; `git diff` reviewed against intent.
