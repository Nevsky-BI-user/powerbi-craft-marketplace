# Part-to-Whole Composition — Reference

Companion to `SKILL.md`. Visual keys below are verified against `docs/research/theme-visuals.md`
(reportThemeSchema 2.143 = 2.155). Where a card/property name is **not** in that file, this
document says so explicitly instead of inventing one (BRIEF F2) — confirm such names against
the schema or a real ground-truth visual before writing JSON. Tokens (`color/*`, `ramp/*`)
resolve in `docs/DESIGN-TOKENS.md`.

## 1. Visual-type keys (case-sensitive, theme `visualStyles`)

| Key | Format-pane name | Verified in |
|---|---|---|
| `pieChart` | Pie chart | theme-visuals §5 |
| `donutChart` | Donut chart | theme-visuals §5 |
| `treemap` | Treemap | theme-visuals §5 |
| `barChart` / `columnChart` | **Stacked** bar / column (default variant) | theme-visuals §5 |
| `hundredPercentStackedBarChart` / `hundredPercentStackedColumnChart` | 100% stacked bar / column | theme-visuals §5 |
| `stackedAreaChart` / `hundredPercentStackedAreaChart` | Stacked / 100% stacked area | theme-visuals §5 |

**Naming traps** (theme-visuals §5): `donut` → `donutChart`; `pie` → `pieChart`. Never `matrix`
or `table` for anything here — irrelevant to this skill but a common nearby slip.

**`$id` selector trap (per-category color override).** The `$id` discriminator inside a
`visualStyles` card is verified ONLY for `filterCard` (Available/Applied) and for
`actionButton` state cards (default/hover/selected/disabled) — see `theme-visuals.md` §4/§7.9
(`shape` cards take no `$id` in schema 2.155).
It is **NOT** a per-category override mechanism for `dataPoint` (no `$id` field exists on any
`visual-donutChart.dataPoint`/`pieChart.dataPoint`/`treemap.dataPoint` in
`reportThemeSchema-2.155.json`). To fix a specific category's color (e.g. neutral grey for
"Other"), do it in the visual's `report.json`/`visual.json` `objects.dataPoint` via
`selector.metadata` mechanics (`powerbi-visuals`), NOT via a fabricated `$id` in the theme.

**Cards for `pieChart`/`donutChart`/`treemap` — partially schema-verified (2026-07-10).**
`dataPoint` (Data colors: `fill`/`defaultColor`/`borderColor`) and `legend` are confirmed in
`reportThemeSchema-2.155.json` for all three keys (identical definitions), and
`master-theme.json` ships a `legend` entry for each. Other format-pane concepts (detail labels
showing category/value/percent, per-slice options) remain **unconfirmed** here — read their
exact card/property names from a ground-truth visual or the schema before emitting any
`objects`/`visualStyles` JSON (BRIEF F2). The global `"*"` defaults (background, border, title,
dropShadow — theme-visuals §6.1) apply to these three keys like any other visual.

## 2. Category limit and the "Other" bucket

- **Pie/donut: ≤5 categories.** Beyond that, angle differences become indistinguishable and
  legends grow past a glance. Route to a sorted bar instead (`pbi-bar-column-charts`).
- **Treemap: ≤2 hierarchy levels.** A third level shrinks rectangles past legibility; deeper
  breakdowns belong to `decompositionTreeVisual` (`pbi-ai-visuals`) or a drill-through page
  (`pbi-drillthrough`).
- **Theme `dataColors`: max 6–8 before grouping** (DESIGN-TOKENS §1.5) — this is the hard
  ceiling even for shapes without their own slice limit (stacked charts, treemap leaves).
- **"Other" is always last**, regardless of its summed value — it is a residual category, not
  a ranked one. Never alphabetize or value-sort it into the middle of the sequence.
- **Recipe:** rank categories by the driving measure, keep the top N (N = the shape's limit
  above), fold the remainder into "Other". This is a model-level grouping (a calculated column
  or a grouping measure), not a report-JSON concern — hand the DAX to `dax-measures`. Shape
  only, as the one illustrative fragment:

  ```dax
  Category Group =
  VAR _rank =
      RANKX ( ALL ( Category[Category] ), CALCULATE ( [Sales Amount] ), , DESC )
  RETURN
      IF ( _rank <= 5, Category[Category], "Other" )
  ```

  Bind the visual's category axis to this grouping column/measure instead of the raw column;
  wiring the binding into visual.json → `powerbi-visuals`.

## 3. Treemap specifics

- Two levels max (category → subcategory). Color the top level categorically
  (`dataColors` order, DESIGN-TOKENS §1.5); shade subcategories with `ramp/brand-seq`
  (DESIGN-TOKENS §1.2) so the eye reads "family of X" rather than unrelated hues.
- Area is a weaker encoding than length — never use a treemap where a sorted bar would answer
  the same question with one shape only (single flat category list). Treemap earns its keep
  only when the *nesting* itself is the message (this category rolls up into that one).
- Label overflow (small leaves show no text) is expected — do not fight it with tiny fonts
  below `type/small` (9 pt, DESIGN-TOKENS §2); rely on tooltips (`pbi-tooltips`) and color
  instead of forcing every leaf to carry a visible label.

## 4. Stacked and 100% stacked — disambiguation

Full stacked-chart craft (segment count, sort order, baseline choice, `totals` card,
small multiples) already lives in `pbi-bar-column-charts` reference.md §5 — do not duplicate
it here. This skill's job is only the *upstream* decision:

- Choose stacked/100%-stacked over pie/donut/treemap when composition **repeats** across a
  dimension (time, region, product line) — a series of small pies is unreadable, a stacked
  or 100%-stacked chart handles the repetition natively.
- Plain stacked = total matters and is the primary message, composition secondary.
  100%-stacked = only shares matter, the absolute total is dropped from the visual entirely.
- 100%-stacked needs a legend (segments rarely fit inline labels); when readers must compare
  one segment's exact share across many bars, a `tableEx` column with in-cell bars (`dax-svg`)
  often communicates faster than reading stacked-bar heights.
- `stackedAreaChart`/`hundredPercentStackedAreaChart` apply the same logic when the x-axis is
  continuous (time) rather than categorical.

## 5. Waffle-style alternative

- **Not a native Power BI visual** (theme-visuals §5, "Names that do NOT exist"): `waffleChart`
  is a custom/AppSource visual, themed only by its registered GUID-suffixed key
  (e.g. `"deneb7E15AEF80B9E4D4F8E12924291ECE89A"`) if built in Deneb, or its own vendor key if
  an AppSource visual — never assume `waffleChart` as a literal theme key.
- **Preferred route: `deneb-vegalite`.** A waffle/unit chart (10×10 grid, N of 100 squares
  colored to represent a percentage) is a standard Vega-Lite pattern and keeps the report on
  a maintained, certification-free spec instead of an AppSource dependency.
- **When to reach for it:** the audience needs to read an exact share as a count-out-of-100
  (e.g. "73 of 100 customers"), which pie/donut's angle encoding communicates only
  approximately. Flag the AppSource-vs-Deneb tradeoff explicitly if the user insists on a
  packaged custom visual instead (BRIEF F7 — name the gap, don't endorse silently).
- Do not reach for waffle as a default part-to-whole shape — it earns its keep only for that
  specific "precise share, small N" reading; for everything else in §Quick Reference it adds
  complexity without a perceptual win.

## 6. Worked example

```
Question: розподіл виручки по 8 продуктових лініях, один період
Shape:    8 categories, one moment → whole matters, but 8 > 5-slice limit
Choice:   Top-4 product lines + "Other" → donutChart (5 slices total);
          category grouping via a DAX rank measure → dax-measures
Rejected: pieChart with 8 raw slices (unreadable angles);
          treemap (no hierarchy — flat category list, bar/donut already answers it);
          waffleChart as a literal key (not native; would need deneb-vegalite)
Route:    JSON → powerbi-visuals; grouping DAX → dax-measures; tokens → DESIGN-TOKENS.md §6
```

## 7. Verification ladder

File written → JSON parses → category count within the chosen shape's limit (§2) → "Other"
present and sorted last when the limit was exceeded → treemap ≤2 levels if used → bindings
(`queryRef`/grouping column) exist in the TMDL model → `git diff` reviewed against intent.
Slice-angle and treemap-area rendering cannot be verified headless — state that explicitly
rather than assuming the layout is correct.
