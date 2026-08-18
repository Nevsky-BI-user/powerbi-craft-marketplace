# pbi-typography — Reference

Detail moved out of SKILL.md to keep it scannable. Sources: `docs/research/theme-visuals.md`
(schema 2.143–2.155, verified) and `docs/DESIGN-TOKENS.md` §2.

## 1. Full `textClasses` map (14 keys)

`additionalProperties: false` per class; only `fontFace` (string), `fontSize` (number, 6–45 pt),
`fontWeight` (string), `color` (hex) are legal fields.

**4 primary** — set these, everything else inherits:

| Class | Default | Applies to |
|---|---|---|
| `callout` | DIN, 45 pt | Card data labels, KPI indicators |
| `title` | DIN, 12 pt | Axis titles, multi-row card title, slicer header |
| `header` | Segoe UI Semibold, 12 pt | Key influencers headers |
| `label` | Segoe UI, 10 pt | Table/matrix headers, grid, values |

**10 secondary** — inherit from a primary, override one aspect; write them only to break inheritance:

| Class | Inherits | Delta | Applies to |
|---|---|---|---|
| `largeTitle` | title | 14 pt | Visual title (does NOT scale with `title` — pin explicitly) |
| `dataTitle` | title | schema-valid, undocumented | — |
| `boldLabel` | label | Segoe UI Bold | Matrix subtotals/grand totals, table totals |
| `semiboldLabel` | label | Segoe UI Semibold | Key influencers profile text |
| `largeLabel` | label | 12 pt | Multi-row card data labels |
| `smallLabel` | label | 9 pt | Reference-line labels, slicer date/numeric/search input |
| `lightLabel` | label | color `#605E5C` | Legend, button text, category-axis labels, funnel labels, slicer items |
| `largeLightLabel` | label | `#605E5C`, 12 pt | Card category labels, gauge labels |
| `smallLightLabel` | label | `#605E5C`, 9 pt | Data labels, value-axis labels |
| `smallDataLabel` | — | schema-valid, undocumented | — |

Project convention: use the DESIGN-TOKENS.md §2.1 canonical block (4 primary + `largeTitle` pinned +
`smallLabel`/`lightLabel` where a report needs them) rather than writing all 14.

## 2. Per-visual-type font property names (verified, schema 2.155)

| Visual / location | Card → property | Notes |
|---|---|---|
| Global default | `visualStyles."*"."*"."*"`: `fontFamily` | Sets family on every card that has the property |
| Any visual title | `visualStyles.<type>."*".title`: `fontColor`, `fontSize`, `fontFamily`, `bold` | Common card, all 48 regular visual types |
| `cardVisual` (new card) | `value`: `fontSize`, `fontFamily`, `fontColor`, `labelDisplayUnits`, `labelPrecision`; `label`: `fontSize`, `fontColor`, `position` | Richest visual (44 cards); label defaults 9 pt secondary color |
| `tableEx` | `columnHeaders`: `fontColor`, `backColor`, `bold`, `fontSize`; `grid`: `textSize`; `values`: `fontColorPrimary`; `total`: `fontColor`, `bold` | Grid uses `textSize`, not `fontSize` |
| `pivotTable` (matrix) | Same as `tableEx` + `rowHeaders`, `columnTotal`, `rowTotal`, `subTotals`, `blankRows`, `sparklines` | |
| `slicer` (classic) | `header`: `fontColor`, `textSize`, `bold`; `items`: `fontColor`, `textSize` | Uses `textSize`, not `fontSize` |
| `advancedSlicerVisual`/`listSlicer` | `label`, `value` cards (different card set entirely) | Style separately — not covered by `slicer` |
| `actionButton` / `shape` | `text`: `fontColor`, `fontSize`, `fontFamily` per `$id` (`default`/`hover`/`selected`/`disabled`) | No `press` state exists |
| `barChart`/`columnChart`/etc. | `labels`: `fontSize`, `color`, `labelDisplayUnits`, `labelPrecision`; `categoryAxis`/`valueAxis`: `labelColor` | Style stacked + clustered + 100% variants separately |

Rule: text classes use `fontFace`; every `visualStyles` card uses `fontFamily`. Mixing the two fails
validation or is silently ignored.

## 3. Ukrainian number-format cookbook

Set in the model's `formatString` (TMDL) so every visual inherits — never in a text-producing DAX
`FORMAT()`. Power BI custom format codes scale the displayed number by 1000 per trailing comma
placed right after the last digit placeholder (before any literal text):

| Unit | Format string | 12 400 000 renders as |
|---|---|---|
| Тисячі (K) | `#,##0.0,"тис."` | `12400.0тис.` |
| Мільйони (M) | `#,##0.0,,"млн."` | `12.4млн.` |
| Мільярди (B) | `#,##0.0,,,"млрд."` | `0.0млрд.` |
| Відсотки | `0.0%` | value already 0–1 ratio → `%` |

Add a leading space inside the quotes (`" тис."`) if a gap before the suffix is wanted. Keep 0–1
decimal places (`labelPrecision` on visuals with no model format, or `.0`/`.00` in the string) —
never more. This only works on numeric measures/columns; a DAX measure that returns formatted
*text* (via `FORMAT()`) loses sorting, axis binding, and totals — use it only as a last resort,
and prefer `dax-measures` for the underlying calculation.

## 4. Worked example — hardcoded fill → theme reference (report.json/visual.json `objects`)

The verified fill shape (DESIGN-TOKENS §1.7) has NO `solidColor` key — a frequent invention.
Confirm the enclosing card/property names against a ground-truth visual of the same type in
the target report; only the fill shape below is schema-verified:

```json
// BEFORE — hardcoded hex (theme drift, A1):
{ "solid": { "color": "#1F2937" } }

// AFTER — theme-referenced (ColorId per the objects mapping: 0=background, 1=foreground, N≥2=dataColors[N−2]):
{ "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 2, "Percent": 0 } } } } }
```

## 5. Textbox height minimums (overflow → scrollbar)

A textbox shorter than its text clips the last line **and** grows a thin vertical scrollbar. On a
rendered report that scrollbar reads as a stray light vertical strip on every page — the "mysterious
light element" users flag. Diagnose any such strip beside a text block as an overflowing textbox, not
a stray shape.

The `h ≈ lines × pt × 1.6 + 16 px` formula **underfloors** — it yields 32 px at 10 pt and ~45 px at
18 pt, both of which still clip. Use the calibrated single-line minimums instead, taken from a
6-size × 10-height calibration page screenshotted in Desktop 2.155 (measure, don't assume):

| Font pt | 10 | 12 | 14 | 18 (and bold) | 24 |
|---|---|---|---|---|---|
| 1-line min h, px | 40 | 44 | 48 | 52 | 64 |

18 pt **bold** needs the same 52 px as 18 pt regular. Multiply the min h by line count for wrapped
text. Fix an overflowing box either direction: raise/widen the frame, or drop the pt.

**Mass resize needs a collision guard:** grow a box downward only if nothing overlaps it in the new
zone (no X-range intersection with a neighbour) and it stays on canvas; otherwise drop the pt instead
of growing. Verify by rendering — no textbox should show a scrollbar.

Incident: single-line textboxes across the report clipped/scrolled because the old heuristic
underfloored (10 pt cut at h=32, 18 pt at h=48); the calibrated 40/44/48/52/64 floors cleared every
strip.
