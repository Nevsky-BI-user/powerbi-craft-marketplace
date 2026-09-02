# Bar & Column Charts — Reference

Companion to `SKILL.md`. All names below are verified against the theme-schema introspection notes
(reportThemeSchema 2.143 = 2.155) or a real report file — never recalled from memory.
Tokens (`color/*`, `type/*`) resolve in `pbi-design-system`.

## 1. Visual-type keys (case-sensitive, theme `visualStyles`)

| Key | Format-pane name | Orientation |
|---|---|---|
| `barChart` | **Stacked** bar chart | horizontal |
| `clusteredBarChart` | Clustered bar chart | horizontal |
| `hundredPercentStackedBarChart` | 100% stacked bar chart | horizontal |
| `columnChart` | **Stacked** column chart | vertical |
| `clusteredColumnChart` | Clustered column chart | vertical |
| `hundredPercentStackedColumnChart` | 100% stacked column chart | vertical |

**Trap:** `barChart`/`columnChart` are the *stacked* variants. A theme entry for
`columnChart` does nothing for a clustered column visual. Emit all six keys with
identical content unless a variant genuinely differs.

**Axis semantics flip with orientation:** for bar (horizontal) the category axis is Y and
the value axis is X; for column (vertical) the category axis is X and the value axis is Y.
"Gridlines perpendicular to bars" = value-axis gridlines in both cases.

## 2. Cards and verified property names

Chart-specific cards for `barChart` (from schema; beyond the 16 common cards):
`labels`, `categoryAxis`, `valueAxis`, `dataPoint`, `legend`, `plotArea`, `totals`,
`zoom`, `ribbonBands`, `smallMultiplesLayout`, `xAxisReferenceLine`,
`y1AxisReferenceLine`, `error`, `annotationTemplate`.

**Card sets differ per key** — the list above is `barChart`'s only (pbi-theme-json/references/theme-visuals.md scopes it
so). Schema-verified for the clustered variants: `clusteredBarChart`/`clusteredColumnChart`
have `referenceLine`, `layout`, `subheader`, `trend` but NO `totals` and NO `ribbonBands`.
Verify the exact card against the schema for the specific key before theming it.

Properties verified in pbi-theme-json/references/theme-visuals.md §6.2:

| Card | Verified properties |
|---|---|
| `labels` | `show`, `color` (fill obj), `fontSize`, `labelDisplayUnits`, `labelPrecision`, `labelPosition` (e.g. `"OutsideEnd"`), `enableBackground` |
| `categoryAxis` | `show`, `labelColor` (fill obj), `gridlineShow`, `showAxisTitle` |
| `valueAxis` | `show`, `gridlineShow`, `gridlineColor` (fill obj), `gridlineStyle` (e.g. `"dotted"`) |
| `dataPoint` | `defaultColor` (fill obj, supports `ThemeDataColor`) |

Any property not in this table: read it from the schema file
(`reportThemeSchema-2.1xx.json`) or copy from a ground-truth visual — do not guess. Card values are always **arrays** of objects.

## 3. Ready-to-adapt theme fragment (the one example)

Token mapping used below — re-resolve against the *target* theme before emitting:
`ThemeDataColor ColorId 0` (in a THEME file, ColorId is 0-based into `dataColors`, so
`0` = `color/brand`), `#605E5C` = `color/text-secondary`, `#E6E6E6` = `color/border`.

```json
"clusteredBarChart": {
  "*": {
    "labels": [{ "show": true,
                 "color": { "solid": { "color": "#605E5C" } },
                 "fontSize": 9, "labelDisplayUnits": 0, "labelPrecision": 1,
                 "labelPosition": "OutsideEnd", "enableBackground": false }],
    "categoryAxis": [{ "show": true,
                       "labelColor": { "solid": { "color": "#605E5C" } },
                       "gridlineShow": false, "showAxisTitle": false }],
    "valueAxis": [{ "show": false, "gridlineShow": false }],
    "dataPoint": [{ "defaultColor": { "solid": { "color": { "expr": {
                    "ThemeDataColor": { "ColorId": 0, "Percent": 0 } } } } } }]
  }
}
```

Repeat the same block for the other five keys (§1). If a chart must show an axis instead
of labels (dense charts, small multiples): `labels.show: false`, `valueAxis.show: true`,
`valueAxis.gridlineShow: true` with `gridlineColor` = `color/border`, `gridlineStyle`
`"dotted"` or 1 px solid.

**ColorId dual mapping (trap).** Inside a THEME file `ColorId` 0–7 map straight to
`dataColors[0..7]`. Inside report.json/visual.json `objects`, the verified mapping is
`0` = background, `1` = foreground, `N≥2` = `dataColors[N−2]`. Always verify against the
target report before emitting (`pbi-design-system` §1.7).

**Pre-emission check (apply it, don't just cite it).** Before writing any per-visual
`objects.dataPoint` block: write down which mapping applies to THIS file, then assign brand
series starting at `ColorId: 2`. A series assigned `ColorId: 0` or `1` in `objects` renders
**white/black**, not brand — the exact silent failure observed in a 2026-07-09 GREEN run,
where the answer quoted this very trap and still emitted `ColorId: 0` for the first series.

## 4. Sorting

- Rule: descending by the plotted measure. Natural order only when the axis is ordinal
  (dates, process stages, age bands, Likert).
- Where it lives: sort order is part of the visual's query definition
  (PBIR-Legacy: inside the visualContainer's `config` query; PBIR enhanced: the
  `visual.json` query/sort section). **Copy the exact shape from a ground-truth sorted
  visual in the same report** via `powerbi-visuals`; the structures differ per format and
  must not be hand-crafted from memory.
- Custom non-value order (e.g. "Low/Medium/High"): `sortByColumn` on the column in the
  TMDL model — a model change, not a report change. Rank-based orders (top-N + "Other")
  → helper measures via `dax-measures`.

## 5. Stacked and 100% stacked guidance

- Stacked: only when the TOTAL is the primary message and composition is secondary.
  Readers cannot compare middle segments (no shared baseline) — max 4–5 segments,
  most important segment on the baseline, order segments by size or meaning (not
  alphabetically), total label via the `totals` card.
- 100% stacked: shares, not absolutes. Requires a legend (labels rarely fit); consider a
  `tableEx` column with in-cell bars (`dax-svg`) when precision matters.
- Segment colors: theme `dataColors` order; never re-declare per visual.

## 6. Small multiples

- Use instead of clustered/stacked when >3 series, or when one question repeats across a
  dimension ("same chart per region").
- Grid 2×2 or 3×3 (more panes → the pattern, not values, is the message); shared Y scale
  (default — do not un-share unless magnitudes differ by orders); order panes by value,
  not alphabetically.
- Small-multiple panes: turn data labels OFF, keep a shared value axis instead
  (labels overwhelm at pane size); category axis labels may drop to every pane's
  shared edge.
- Theme card: `smallMultiplesLayout` (property names not verified in our research —
  read them from the schema or a ground-truth visual before use).
- The field goes into the visual's "Small multiples" well — binding mechanics →
  `powerbi-visuals`.

## 7. Emphasis recipes

- One-bar accent ("gray + one hue"): conditional formatting on Columns/Data colors with a
  DAX measure returning a named theme color (`"good"`, `"bad"`) or a `ThemeDataColor`-safe
  value; all other points `color/neutral-data`. Measure → `dax-measures`, CF mechanics →
  `powerbi-visuals`, rule semantics → `pbi-conditional-formatting`.
- Plan/fact deviation coloring: `ramp/diverging` semantics from `pbi-design-system` §1.3 —
  midpoint at the meaningful center (0 or 100% of plan), never the data mean.
- Reference targets: `xAxisReferenceLine` / `y1AxisReferenceLine` cards (line + label),
  instead of a second bar series for a static target.
