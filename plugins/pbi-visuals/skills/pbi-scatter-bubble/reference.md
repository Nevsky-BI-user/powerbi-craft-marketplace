# Scatter & Bubble Charts — Reference

Companion to `SKILL.md`. All names below are verified against
`docs/research/theme-visuals.md` / `reportThemeSchema-2.155.json`
(`definitions/visual-scatterChart`) — never recalled from memory.
Tokens (`color/*`, `ramp/*`) resolve in `docs/DESIGN-TOKENS.md`.

## 1. Visual-type key

| Key | Format-pane name |
|---|---|
| `scatterChart` | Scatter chart / Bubble chart — same key; "bubble" = a field bound to the Size well |

## 2. Cards and verified properties (theme `visualStyles.scatterChart`)

### Axes — naming trap: Cartesian roles are inherited

| Card | Role | Verified properties |
|---|---|---|
| `categoryAxis` | **X axis** | `show`, `axisType` (`"Scalar"` \| `"Categorical"`), `logAxisScale`, `start`, `end`, `gridlineShow`, `gridlineColor`, `showAxisTitle`, `titleText`, `labelDisplayUnits`, `labelPrecision` |
| `valueAxis` | **Y axis** | near-`categoryAxis` shape plus `switchAxisPosition`, but WITHOUT `axisType` (and without `innerPadding`/`maxMarginFactor`/`preferredCategoryWidth`) — schema-verified |

Scatter's X axis is always continuous data even though the theme calls its card
`categoryAxis` — set `axisType: "Scalar"` explicitly; `"Categorical"` treats X as
ordinal buckets and breaks position encoding.

### Markers and data

| Card | Verified properties |
|---|---|
| `dataPoint` | `defaultColor`/`fill` (fill obj, `ThemeDataColor`-capable), `fillRule` (gradient-by-measure), `showAllDataPoints` |
| `bubbles` | `bubbleSize` (integer **size multiplier**, not a literal px/value), `markerRangeType` (`"magnitude"` \| `"dataRange"` \| `"auto"`), `markerShape` (`circle`\|`square`\|`diamond`\|`triangle`\|`x`\|`shortDash`\|`longDash`\|`plus`), `preventOverflow`, `showSeries` |
| `fillPoint` | `style`: **`"Fill only"`** \| **`"Border only"`** (string enum, not boolean) |
| `markers` | `borderShow`, `borderColor`, `borderColorMatchFill`, `borderWidth`, `transparency`, `rotation` |
| `colorByCategory` | `show` — categorical coloring toggle |
| `colorBorder` | `show` — outlines every marker in its category color |
| `categoryLabels` | `show`, `color`, `fontSize`, `fontFamily`, `bold`, `italic`, `enableBackground`, `backgroundColor` — one on/off switch for the whole visual, no per-point condition in the theme schema |
| `legend` | `show`, `position` (`Top`\|`TopCenter`\|`TopRight`\|`Left`\|`Right`\|`LeftCenter`\|`RightCenter`\|`Bottom`\|`BottomCenter`\|`BottomRight`), `showTitle`, `titleText`, `showGradientLegend` (legend for a continuous `fillRule` color) |
| `general` | `dataVolume` (integer point-count cap), `formatString` |
| `zoom` | `show`, `showOnCategoryAxis`, `showOnValueAxis`, `categoryMin`/`categoryMax`, `valueMin`/`valueMax`, `showLabels`, `showTooltip` |
| `trend` | `show`, `lineColor`, `style` (`solid`\|`dashed`\|`dotted`\|`custom`), `width`, `combineSeries` (`false` = one trend line per legend group instead of one overall) |
| `clustering` | present in schema with no themeable sub-properties (format-pane-only toggle) |

### Quadrant / reference-line geometry

| Card | Verified properties |
|---|---|
| `xAxisReferenceLine` | array; each item: `show`, `value` (X threshold), `lineColor`, `style`, `width`, `position` (`front`\|`back`), `shadeShow`, `shadeRegion` (`before`\|`after`\|`none`), `shadeColor`, `shadeTransparency`, `dataLabelShow`, `dataLabelText`, `dataLabelColor`, `dataLabelHorizontalPosition` (`left`\|`right`), `dataLabelVerticalPosition` (`above`\|`under`), `dataLabelDisplayUnits`, `dataLabelDecimalPoints` |
| `y1AxisReferenceLine` | identical shape, horizontal line at a Y `value` |
| `referenceLine` | same shape again in the schema; in the Format pane, scatter's constant lines are grouped as **X-Axis constant line** / **Y-Axis constant line** — i.e. the two cards above are the ones to emit |
| `plotAreaShading` | `show`, `upperShadingColor`, `lowerShadingColor`, `transparency` — one Y-axis-band split (e.g. RAG background zones), NOT a 4-way quadrant fill |
| `plotArea` | `image`, `transparency` — set `transparency` high/background none to let an overlay `shape` visual show through for the quadrant-fill workaround (§4) |

Any property not in this table: read it from `reportThemeSchema-2.1xx.json` or copy
from a ground-truth visual in the target report — never guess (BRIEF F2).

## 3. Ready-to-adapt theme fragment

Token mapping used below (re-resolve against the *target* theme before emitting):
`ThemeDataColor ColorId 0` = `color/brand`; `#605E5C` = `color/text-secondary`;
`#E6E6E6` = `color/border`.

```json
"scatterChart": {
  "*": {
    "categoryAxis": [{ "show": true, "axisType": "Scalar",
                        "gridlineShow": false, "showAxisTitle": true }],
    "valueAxis":    [{ "show": true, "gridlineShow": true,
                        "gridlineColor": { "solid": { "color": "#E6E6E6" } },
                        "showAxisTitle": true }],
    "bubbles":      [{ "bubbleSize": 40, "markerRangeType": "auto" }],
    "fillPoint":    [{ "style": "Fill only" }],
    "markers":      [{ "borderShow": true,
                        "borderColor": { "solid": { "color": "#FFFFFF" } },
                        "transparency": 20 }],
    "dataPoint":    [{ "defaultColor": { "solid": { "color": { "expr": {
                        "ThemeDataColor": { "ColorId": 0, "Percent": 0 } } } } } }],
    "categoryLabels": [{ "show": false }],
    "legend":       [{ "show": true, "position": "Top" }]
  }
}
```

**ColorId dual mapping (trap, same as every other chart skill).** Inside a THEME
file `ColorId` 0–7 map straight to `dataColors[0..7]`. Inside report.json/visual.json
`objects`, the verified mapping is `0` = background, `1` = foreground, `N≥2` =
`dataColors[N−2]`. Always verify against the target report before emitting
(DESIGN-TOKENS §1.7).

## 4. Quadrant recipe (constant lines + shape overlay)

Native scatter only exposes two lines, so a true 4-color quadrant fill needs an
overlay. Steps:

1. **Two constant lines** define the split. Anchor `value` at 0, a target, or a
   fixed business threshold — never the data mean (shifts every refresh, misleads):
   ```json
   "xAxisReferenceLine": [{ "show": true, "value": 0, "style": "dashed", "width": 1,
                             "lineColor": { "solid": { "color": "#605E5C" } },
                             "position": "back", "dataLabelShow": false }],
   "y1AxisReferenceLine": [{ "show": true, "value": 0, "style": "dashed", "width": 1,
                              "lineColor": { "solid": { "color": "#605E5C" } },
                              "position": "back", "dataLabelShow": false }]
   ```
2. **Color the 4 zones.** `shadeRegion` (`before`/`after`) on one line tints only
   one side of that ONE axis — combining both lines' shading gives at most 2
   overlapping bands, never 4 distinct colors. Instead: set the visual's `plotArea`
   to transparent and add **4 `shape` (rectangle) visuals** behind the scatter
   (lower `z`), each sized to one quadrant of the plot area, filled at low opacity
   (`ramp/rag` extremes for "win"/"lose" quadrants, `color/neutral-data` @ ~10% for
   the other two). Shape JSON + z-order mechanics → `powerbi-visuals`.
3. **Label each corner** with a short textbox ("High growth / High margin", …)
   positioned at the 8-px-snapped corners of the plot area — `type/small`,
   `color/text-secondary`, placed after the chart in `z`/`tabOrder`.
4. A guaranteed single-visual 4-color quadrant fill (no overlay hack, no z-order
   fuss) → `deneb-vegalite` (Vega-Lite `layer` + `rule`/`rect` marks do this
   natively).

## 5. Outlier / selective labels

`categoryLabels.show` is one boolean for the whole visual — there is no built-in
"label only the top-N" or "label only points beyond a threshold" in the theme
schema.

1. Add a DAX flag measure, e.g.
   `IsOutlier = IF(ABS([Residual]) > [Threshold], TRUE(), FALSE())` (`dax-measures`).
2. Check whether **Category labels → Show** exposes conditional formatting (fx) in
   the target report/Desktop version's Format pane. If it does, bind it to the flag
   measure — rule semantics → `pbi-conditional-formatting`, binding mechanics →
   `powerbi-visuals`. This is version/report-specific; verify against the actual file
   before assuming the capability exists (BRIEF F1).
3. If fx is not available on this property, do not fake it with all-labels-on.
   Route to `deneb-vegalite`, which supports a labels layer filtered by exactly
   this condition.

## 6. Data volume & overplotting

- Ceiling from `pbi-visualization-strategy`: **≤ ~1k points** before scatter
  degrades as an encoding.
- Native levers: `general.dataVolume` (point cap), `markers.transparency`
  (20–40% reveals density under overlap), `bubbles.markerRangeType: "dataRange"`
  to stop one outlier compressing every other bubble down to a dot.
- Beyond ~1k points or heavy overplotting: pre-aggregate/bin via `dax-measures`,
  or move to a density/hexbin chart in `deneb-vegalite` — scatter is no longer the
  right visual at that volume (`pbi-visualization-strategy`).
