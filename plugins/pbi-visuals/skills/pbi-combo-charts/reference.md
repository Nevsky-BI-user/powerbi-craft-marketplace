# Combo Charts — Reference

Companion to `SKILL.md`. All names below are extracted directly from
`reportThemeSchema-2.155.json` (`definitions.visual-lineClusteredColumnComboChart`
/ `visual-lineStackedColumnComboChart`) — never recalled from memory.
Tokens (`color/*`, `type/*`, `ramp/*`) resolve in `pbi-design-system`.

## 1. Visual-type keys and cards

| Key | Format-pane name | Column half |
|---|---|---|
| `lineClusteredColumnComboChart` | Line and clustered column combo | clustered |
| `lineStackedColumnComboChart` | Line and stacked column combo | stacked |

Cards beyond the 16 common cards (`commonCards`), verified from the schema:

- Both variants: `annotationTemplate`, `categoryAxis`, `dataPoint`, `error`, `filters`,
  `general`, `labels`, `layout` (clustered-gap/series-order for the column half),
  `legend`, `lineStyles`, `markers`, `plotArea`, `seriesLabels`, `smallMultiplesLayout`,
  `subheader`, `valueAxis`, `xAxisReferenceLine`, `y1AxisReferenceLine`, `zoom`.
- `lineClusteredColumnComboChart` only: `referenceLine`, `trend` (free-form reference line /
  trend line — the stacked variant has neither, since stacking makes a trend line ambiguous).
- `lineStackedColumnComboChart` only: `totals` (stack total labels).

There is **one `valueAxis` card**, not two separate cards — the secondary (line) axis lives
inside it as `sec*`-prefixed properties (§2). `general.visualType1`/`visualType2` are internal
type tags, not user-facing options — do not treat them as a series-swap control.

## 2. `valueAxis` — the axis-sync properties (verified)

| Property | Type | Meaning |
|---|---|---|
| `show` / `start` / `end` | bool / number / number | Primary (column) axis visibility and manual range |
| `sharedAxis` | bool | **"Shared y-axis"** — forces the line onto the same axis as the columns. Default choice per SKILL.md |
| `secShow` | bool | **"Show secondary"** — enables the independent line axis. Only when `sharedAxis` is unworkable |
| `alignZeros` | bool | **"Align zeros"** — aligns the zero tick of both axes. Mandatory whenever `secShow: true` |
| `secStart` / `secEnd` | number | Secondary axis manual range — never hand-tune to force a crossing (SKILL.md "Avoiding dual-axis manipulation") |
| `secShowAxisTitle` / `secTitleText` | bool / string | Secondary axis title toggle + text — always set both when `secShow: true` |
| `secLabelDisplayUnits` / `secLabelPrecision` | ref / number | Secondary axis number formatting (K/M, decimals) |
| `switchAxisPosition` | bool | Swaps which side (left/right) each axis renders on |
| `gridlineShow` / `gridlineColor` | bool / fill | Value-axis gridlines — one set only, shared by both axes visually |

`categoryAxis` is unchanged from `pbi-bar-column-charts` reference.md (`show`, `labelColor`,
`gridlineShow`, `showAxisTitle`) — the category axis is always shared, never duplicated.

## 3. Column half vs line half styling

| Card | Applies to | Key properties |
|---|---|---|
| `dataPoint` | Columns | `defaultColor` (fill obj, `ThemeDataColor` capable) — same shape as `pbi-bar-column-charts` |
| `lineStyles` | Line | `strokeWidth`, `strokeShow`, `lineChartType`, `showMarker`/`markerShape`/`markerSize`, `interpolationSmooth` |
| `markers` | Line markers | `borderColor`, `borderShow`, `rotation`, `transparency` |
| `labels` | Both (shared card) | `showSeries` (array — pick which series get labels), `labelPosition`, `labelDisplayUnits` |

Per SKILL.md: columns take `color/brand` (or `color/neutral-data` for a context series like
Plan), the line takes `color/accent` — resolved via `ThemeDataColor` against the target
report's theme (`pbi-design-system` §1.7), never a bare hex.

## 4. Native error bars (`error` card) — no-second-axis alternative

Verified properties: `enabled`, `barShow`, `barColor`, `barWidth`, `shadeShow` (tolerance
band), `shadeColor`, `shadeTransparency`, `labelShow`, `tooltipShow`. Use this instead of a
combo when the only need is "how far is Actual from Plan/target," on a single column series —
avoids a second axis entirely. Rule semantics (when to shade vs bar) → `pbi-conditional-formatting`;
mechanics → `powerbi-visuals`.

## 5. Ready-to-adapt theme fragment

Re-resolve `ThemeDataColor` `ColorId`s against the target theme before emitting
(`pbi-design-system` §1.7: in a THEME file `ColorId` 0–7 = `dataColors[0..7]` directly).

```json
"lineClusteredColumnComboChart": {
  "*": {
    "valueAxis": [{
      "show": true, "sharedAxis": false,
      "secShow": true, "alignZeros": true,
      "secShowAxisTitle": true, "secTitleText": "Variance %",
      "gridlineShow": false
    }],
    "categoryAxis": [{ "show": true,
                       "labelColor": { "solid": { "color": "#605E5C" } },
                       "gridlineShow": false, "showAxisTitle": false }],
    "dataPoint": [{ "defaultColor": { "solid": { "color": { "expr": {
                    "ThemeDataColor": { "ColorId": 0, "Percent": 0 } } } } } }],
    "lineStyles": [{ "strokeWidth": 2, "strokeShow": true, "showMarker": false }],
    "legend": [{ "show": true, "position": "BottomCenter" }]
  }
}
```

The same fields apply verbatim to `lineStackedColumnComboChart` if the report uses stacked
columns as the base — just recall it has no `referenceLine`/`trend` card but gains `totals` (§1).

## 6. Worked example, expanded: plan vs actual + variance

**Shape:** N categories × (Plan, Actual, Variance %). **Column series:** Plan
(`color/neutral-data`, context) and Actual (`color/brand`, the answer), clustered.
**Line series:** `Variance % = DIVIDE(Actual - Plan, Plan)` (route the DAX to `dax-measures`;
never invent the formula in this skill). **Axis:** `secShow: true` (percent vs currency
cannot share a scale), `alignZeros: true` so 0% on the line lines up with 0 on the columns,
`secTitleText: "Variance %"`. **Color of the line:** `ramp/diverging` — red below plan,
green above, midpoint fixed at 0% (the meaningful center), not at the series' own mean
(`pbi-design-system` §1.3). **Labels:** Actual gets direct data labels (`labelPosition: OutsideEnd`);
Variance line gets endpoint label only (`seriesLabels`) to avoid clutter over N categories.
**Rejected alternative noted in `pbi-visualization-strategy`:** if Plan and Actual were the
only two series (same unit), this would NOT be a combo — clustered bars alone win; the combo
is justified here specifically because Variance % is a different unit sharing the story.

## 7. Sorting and category order

Combo charts share one category axis between both series — sort by the **column** measure
(usually Actual, descending) unless the axis is ordinal (time). Do not sort by the line
measure independently; that would desynchronize the shared axis from the bar-chart reading
convention (`pbi-bar-column-charts` reference.md §4 applies identically here).
