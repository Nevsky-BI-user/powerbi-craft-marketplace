# Line & Area Charts — Reference

Companion to `SKILL.md`. All card/property names below are extracted directly from
`docs/research/reportThemeSchema-2.155.json` (`definitions.visual-lineChart` /
`visual-areaChart` / `visual-stackedAreaChart` / …) — never recalled from memory.
Tokens (`color/*`, `type/*`) resolve in `docs/DESIGN-TOKENS.md`.

## 1. Visual-type keys (case-sensitive, theme `visualStyles`)

| Key | Format-pane name | Notes |
|---|---|---|
| `lineChart` | Line chart | Only key with `forecast` and `anomalyDetection` cards |
| `areaChart` | Area chart (basic) | Unstacked filled series — overlap beyond ~2 series |
| `stackedAreaChart` | Stacked area chart | Adds a `totals` card |
| `hundredPercentStackedAreaChart` | 100% stacked area chart | Shares, not absolutes; adds `totals` |
| `lineClusteredColumnComboChart` / `lineStackedColumnComboChart` | Combo | Mechanics → `pbi-combo-charts` |

Card set per key differs slightly (verified from schema `allOf` siblings of `"*"`):

- `lineChart`: `annotationTemplate, anomalyDetection, categoryAxis, dataPoint, error, filters, forecast, general, labels, layout, legend, lineStyles, markers, plotArea, referenceLine, scalarKey, seriesLabels, smallMultiplesLayout, subheader, trend, valueAxis, xAxisReferenceLine, y1AxisReferenceLine, y2Axis, zoom`
- `areaChart`: same minus `anomalyDetection`, `error`, `forecast`.
- `stackedAreaChart` / `hundredPercentStackedAreaChart`: same as `areaChart` plus `totals`,
  minus `referenceLine` (schema-verified: the stacked variants drop that card).

**Trap:** `forecast` and `anomalyDetection` exist ONLY on `lineChart` — do not attempt
them on an area or combo visual key; the property will silently do nothing.

## 2. Verified cards and properties

| Card | Key properties (from schema) |
|---|---|
| `lineStyles` (per-series line/marker/area style) | `lineChartType` (`linear`\|`smooth`\|`step`), `interpolationSmooth` (`monotoneX`\|`cardinal`), `interpolationSmoothParam`, `interpolationStep` (`before`\|`center`\|`after`), `lineStyle` (`solid`\|`dashed`\|`dotted`\|`custom`), `strokeWidth`, `strokeColor`, `strokeShow`, `strokeDashArray`, `showMarker`, `markerShape` (`circle`\|`square`\|`diamond`\|`triangle`\|`x`\|`shortDash`\|`longDash`\|`plus`), `markerColor`, `markerSize`, `areaShow` (bool, "Shade area"), `areaColor`, `areaMatchStrokeColor`, `segmentAlignment` (`left`\|`center`\|`right`), `showSeries` |
| `markers` | `borderColor`, `borderShow`, `borderWidth`, `borderColorMatchFill`, `borderTransparency`, `rotation`, `transparency` — marker BORDER only; fill/shape live in `lineStyles` |
| `dataPoint` | `defaultColor`, `fill`, `showAllDataPoints`, **`transparency`** — titled "Area transparency" in the schema (drives the area fill's opacity on `areaChart`/`stackedAreaChart`) |
| `seriesLabels` (end-of-line labels) | `show`, `showAll`, `showByDefault`, `seriesPosition` (`Left`\|`Right`), `seriesColor`, `seriesMatchColor`, `seriesFontFamily`, `textSize`, `bold`, `leaderLines`, `leaderLineColor` |
| `labels` (data labels) | `show`, `showAll`, `labelPosition` (`Auto`\|`InsideEnd`\|`OutsideEnd`\|`InsideCenter`\|`InsideBase`\|`Above`\|`Under`), `labelDisplayUnits`, `labelPrecision`, `color`, `fontSize`, `labelDensity`, `enableBackground` |
| `trend` | `show`, `lineColor`, `style` (`solid`\|`dashed`\|`dotted`\|`custom`), `width`, `dashArray`, `combineSeries`, `useHighlightValues`, `displayName` |
| `forecast` (`lineChart` only) | `show`, `lineColor`, `style`, `width`, `interpolation`, `bandLineShow`, `bandLineColor`, `bandAreaShow`, `bandAreaColor`, `bandAreaTransparency`, `displayName` |
| `anomalyDetection` (`lineChart` only) | `show`, `markerShow`, `markerColor`, `markerShape`, `confidenceBandShow`, `confidenceBandColor`, `confidenceBandStyle` (`fill`\|`line`\|`none`) |
| `categoryAxis` / `valueAxis` | Shared with bar/column — see `pbi-bar-column-charts/reference.md` §2. `axisType`: `Scalar` (continuous, date gaps preserved) vs `Categorical` (evenly spaced labels) — pick `Scalar` for true date trends |
| `y2Axis` (secondary axis) | `show`, `secLabelColor`, `secTitleText`, `secStart`/`secEnd` — same dual-axis honesty rules as `pbi-combo-charts` (`alignZeros`, no hand-tuned crossing) |
| `referenceLine` | `show`, `value`, `lineColor`, `style`, `position` (`back`\|`front`), `shadeShow`/`shadeColor` (tolerance band), `dataLabelShow`/`dataLabelText` |

Any property not in this table: read it from `reportThemeSchema-2.155.json` or copy from
a ground-truth visual — do not guess (BRIEF F2). Card values are always **arrays** of
objects, matching the bar/column convention.

## 3. Ready-to-adapt theme fragment (the one example)

Single emphasis series over a monthly (sparse) date axis, end-of-line label, dashed
trendline. Re-resolve `ThemeDataColor` `ColorId` against the *target* theme first.

```json
"lineChart": {
  "*": {
    "lineStyles": [{
      "lineChartType": "linear",
      "strokeWidth": 2.5,
      "strokeColor": { "solid": { "color": { "expr": {
        "ThemeDataColor": { "ColorId": 0, "Percent": 0 } } } } },
      "showMarker": true,
      "markerShape": "circle",
      "markerSize": 5,
      "markerColor": { "solid": { "color": { "expr": {
        "ThemeDataColor": { "ColorId": 0, "Percent": 0 } } } } }
    }],
    "seriesLabels": [{ "show": true, "seriesPosition": "Right",
                        "seriesMatchColor": true, "textSize": 9 }],
    "legend": [{ "show": false }],
    "categoryAxis": [{ "show": true, "axisType": "Scalar", "gridlineShow": false }],
    "valueAxis": [{ "show": false, "gridlineShow": false }],
    "trend": [{ "show": true, "style": "dashed",
                "lineColor": { "solid": { "color": "#605E5C" } }, "width": 1 }]
  }
}
```

For area: add `"lineStyles":[{ "areaShow": true, "areaMatchStrokeColor": true }]` and
`"dataPoint":[{ "transparency": 70 }]` (≈70% — fill reads as a tint, not a solid block;
never 0% transparency on a fill sitting under a legible line/marker).

**ColorId dual mapping (trap, same as bar/column):** inside a THEME file `ColorId` 0–7
map straight to `dataColors[0..7]`; inside report.json/visual.json `objects`, `0` =
background, `1` = foreground, `N≥2` = `dataColors[N−2]`. Always verify against the target
report before emitting (DESIGN-TOKENS §1.7).

## 4. Series-count and emphasis guidance

- ≤4–5 series is the hard ceiling for a single line/area chart before line-crossing and
  color-matching make it unreadable (Cleveland–McGill: position along a shared axis is
  precise, but only when few enough lines exist to trace one at a time).
- Beyond that: small multiples (one line per panel, shared Y scale — same pattern as
  `pbi-bar-column-charts` §6), or collapse the tail into "Other," or pivot the question
  to "which categories rank highest now" (a bar chart of the latest period).
- Emphasis recipe: one line `color/brand` at full `strokeWidth` (e.g. 2.5), the rest
  `color/neutral-data` at a lighter weight (e.g. 1.5) — weight AND color both drop for
  context series so the answer is unambiguous even in grayscale.
- Binary comparison (actual vs prior period): blue vs orange
  (`color/brand` vs `color/warning`/`#E69F00`) — colorblind-safe per DESIGN-TOKENS §1.3.

## 5. Trendlines vs forecast vs reference line — when each applies

| Need | Card | Notes |
|---|---|---|
| Statistical fit line through historical data (linear/moving average) | `trend` | Descriptive only — dashed, secondary color, never the same weight as the data line |
| Projected future values beyond the last known point | `forecast` (`lineChart` only) | Requires a continuous date axis; band = confidence interval; label the cutover clearly |
| Fixed target/threshold (budget, SLA, prior-year same period) | `xAxisReferenceLine` / `y1AxisReferenceLine` | A static value, not derived from the series — label it (`dataLabelText`) instead of adding a second flat series |
| Point-level outliers vs expected range | `anomalyDetection` (`lineChart` only) | Native anomaly detection markers + confidence band; distinct from `forecast` |

Any of these that need a computed value (e.g. a custom trend measure, YoY comparison
series) → helper DAX via `dax-measures`; period-over-period patterns specifically are
that skill's documented use case.

## 6. Date-axis formatting

- `categoryAxis.axisType: "Scalar"` for a true continuous date trend (gaps in data stay
  visually proportional); `"Categorical"` only when periods must be evenly spaced
  regardless of calendar gaps (e.g. comparing non-contiguous fiscal periods).
- Display units and precision on data labels come from `labels.labelDisplayUnits` /
  `labelPrecision` — K/M with 0–1 decimals, never raw thousands (DESIGN-TOKENS anti-drift
  rule, same as bar/column).
- Date formatting itself (e.g. `"MMM yyyy"`) is a column/measure format-string concern in
  the TMDL model, not a theme property — route format-string changes through the model,
  not per-visual overrides.
