# Matrix (pivotTable) — Reference

Companion to `SKILL.md`. All names below are verified against
`docs/research/reportThemeSchema-2.155.json` (`definitions.visual-pivotTable`) and
`docs/research/theme-visuals.md` §6.3 — never recalled from memory (BRIEF F2). PDP audit:
83 real `pivotTable` instances. Tokens (`color/*`, `type/*`, `ramp/*`) resolve in
`docs/DESIGN-TOKENS.md`.

## 1. Visual-type key

`pivotTable` in `theme.json → visualStyles` and in `report.json`/`visual.json` `visualType`.
**`matrix` does not exist** — the Format-pane name is "Matrix" but the schema/JSON key is
always `pivotTable` (theme-visuals.md §5, "Names that do NOT exist").

## 2. The 14 verified cards (beyond the 16 common cards every visual has)

| Card | Purpose | Key properties (schema-verified) |
|---|---|---|
| `general` | Layout mode | `layout`: `"Compact"` \| `"Outline"` \| `"Tabular"` |
| `rowHeaders` | Left hierarchy labels | `stepped`, `showExpandCollapseButtons`, `expandCollapseButtonsColor`, `expandCollapseButtonsSize`, `expandCompositeHierarchy`, `repeatRowHeaders`, `alignment`, `backColor`, `fontColor`, `bold`, `fontFamily`, `fontSize` |
| `columnHeaders` | Top field headers | `alignment`, `backColor`, `fontColor`, `bold`, `fontSize`, `columnAdjustment` (`fitToContent`\|`growToFit`\|`fixedWidth`), `customColumnWidth`, `defaultColumnWidth`, `autoSizeColumnWidth` |
| `columnWidth` | Per-column explicit width | `value` (number, px) |
| `values` | Detail cell body | `fontColorPrimary/Secondary`, `backColorPrimary/Secondary` (zebra), `bandedRowHeaders`, `icon`, `bold` |
| `columnFormatting` | Per-field CF (bars/color/icons) | `backColor`, `fontColor`, `dataBars`, `labelDisplayUnits`, `labelPrecision`, `styleHeader`/`styleSubtotals`/`styleTotal`/`styleValues` (which grains inherit the CF) |
| `grid` | Gridlines & row density | `gridHorizontal`, `gridHorizontalColor`, `gridHorizontalWeight`, `gridVertical`, `gridVerticalColor`, `rowPadding`, `imageHeight`/`imageWidth` |
| `subTotals` | Subtotal rows/columns | `$id`: `"Row"` \| `"Column"` (axis-scoped override, NOT an interaction state); `rowSubtotals`, `columnSubtotals`, `rowSubtotalsLabel`, `columnSubtotalsLabel`, `rowSubtotalsPosition` (`Top`\|`Bottom`), `perRowLevel`, `perColumnLevel`, `levelSubtotalEnabled`, `levelSubtotalLabel`, `bold`, `backColor`, `underline` — **no `border` property** |
| `total` | Grand total (both axes) | `backColor`, `bold`, `underline`, `fontColor`, `applyToHeaders` — **no `border` property** |
| `rowTotal` / `columnTotal` | Grand total per axis | same shape as `total`, scoped to one axis |
| `sparklines` | In-cell trend | `chartType` (`line`\|`column`), `dataColor`, `markerColor`, `markerShape`, `markerSize`, `markers`, `strokeWidth` |
| `blankRows` | Empty-row handling | `showBlankRows`, `blankRowColor`, `blankRowTransparency`, `showBorder`, `borderPosition` (`Top`\|`Bottom`\|`TopAndBottom`), `borderColor`, `borderWidth` — this is the ONE card in the whole visual that legitimately has a border |
| `accessibility` | Alt text | `altTextColumns` |

Any property not in this table: read it from `reportThemeSchema-2.1xx.json` or copy from a
ground-truth `pivotTable` — do not guess. Card values are always **arrays** of objects.

## 3. Drill/expand header icons (`visualHeader` — common card, schema-verified)

Field-level expand/collapse (`rowHeaders.showExpandCollapseButtons`) is a different mechanism
from the visual's own header icons. The header-icon properties, verified in
`definitions.commonCards.properties.visualHeader`:

| Property | Format-pane label |
|---|---|
| `showDrillDownExpandButton` | Expand to next level icon |
| `showDrillDownLevelButton` | Show next level icon |
| `showDrillUpButton` | Drill up icon |
| `showDrillToggleButton` | Drill down icon |
| `showDrillRoleSelector` | Drill on dropdown |
| `foreground` | Icon color (fill object) |
| `show` | Master visibility for the whole header icon row |

DESIGN-TOKENS §6 says new visuals are born with `visualHeader.show: false` — **matrices with
row/column hierarchies are the deliberate exception**: these five icons are the only drill
affordance a reader has, so keep `show: true` and set `foreground` to `color/text-secondary`
(quiet, not competing with `color/brand` data).

If the client insists on hiding them anyway: pre-expand the hierarchy to leaf level in Desktop
first, then disable only the `showDrill*` buttons — never `visualHeader.show: false`, which
removes the whole header row.

## 4. Ready-to-adapt theme fragment

`ColorId` mapping used below is the THEME-file mapping (0-based straight into `dataColors`):
`ColorId 0` = `color/brand`. Re-verify against the target theme before emitting
(DESIGN-TOKENS §1.7).

```json
"pivotTable": {
  "*": {
    "general": [{ "layout": "Compact" }],
    "rowHeaders": [{
      "stepped": true,
      "showExpandCollapseButtons": true,
      "expandCollapseButtonsColor": { "solid": { "color": "#605E5C" } },
      "repeatRowHeaders": true,
      "bold": false,
      "fontColor": { "solid": { "color": "#333333" } },
      "fontSize": 10
    }],
    "columnHeaders": [{
      "backColor": { "solid": { "color": { "expr": {
                    "ThemeDataColor": { "ColorId": 0, "Percent": 0 } } } } },
      "fontColor": { "solid": { "color": "#FFFFFF" } },
      "bold": true, "fontSize": 10,
      "columnAdjustment": "fixedWidth"
    }],
    "grid": [{
      "gridHorizontal": true,
      "gridHorizontalColor": { "solid": { "color": "#E6E6E6" } },
      "gridVertical": false, "rowPadding": 4
    }],
    "values": [{
      "fontColorPrimary": { "solid": { "color": "#333333" } },
      "backColorPrimary": { "solid": { "color": "#FFFFFF" } }
    }],
    "subTotals": [
      { "$id": "Row", "bold": true,
        "backColor": { "solid": { "color": "#FAFAFA" } },
        "rowSubtotalsPosition": "Bottom" },
      { "$id": "Column", "bold": true,
        "backColor": { "solid": { "color": "#FAFAFA" } } }
    ],
    "total": [{
      "bold": true, "underline": true,
      "backColor": { "solid": { "color": { "expr": {
                    "ThemeDataColor": { "ColorId": 0, "Percent": 0.85 } } } } }
    }],
    "sparklines": [{
      "chartType": "line",
      "dataColor": { "solid": { "color": { "expr": {
                    "ThemeDataColor": { "ColorId": 1, "Percent": 0 } } } } },
      "strokeWidth": 1.5
    }],
    "visualHeader": [{
      "show": true,
      "foreground": { "solid": { "color": "#605E5C" } },
      "showDrillDownExpandButton": true,
      "showDrillDownLevelButton": true,
      "showDrillUpButton": true,
      "showDrillToggleButton": true
    }]
  }
}
```

## 5. Heatmap pattern — what lives where

The theme fragment above sets **static defaults only**. The heatmap itself is a per-visual
conditional-formatting rule (an `fx` expression on `columnFormatting.backColor` or
`values.backColor` in the visual's own `report.json`/`visual.json` `objects`, not the theme) —
wiring mechanics belong to `powerbi-visuals`; rule semantics/thresholds to
`pbi-conditional-formatting`. This skill's job is the color choice only:

- Magnitude (bigger = more attention): `ramp/brand-seq` — single hue, light→dark, monotonic.
- Variance vs. target/plan/zero: `ramp/diverging` — anchor the midpoint at the actual
  meaningful center (0, 100 % of plan), never the data mean.
- Never apply a heatmap to a column that also has `values.bandedRowHeaders` zebra striping —
  pick one background system per matrix.

## 6. Layout mode → when to pick it

| Mode | Row-header rendering | Pick when |
|---|---|---|
| `Compact` | One stepped, indented column; deepest level nests visually | Default; most reports, narrow-to-medium width |
| `Outline` | Each subtotal on its own row above its children (Excel Outline feel) | Groups are large and the subtotal needs a full-width row of its own |
| `Tabular` | Every hierarchy level gets its own full column | Downstream copy/export to Excel as a flat pivot; column-aligned comparison across levels matters more than compactness |

## 7. Header font/back pair — both sides in ONE place

A visual can override `objects.columnHeaders[0].fontColor` in its own `visual.json` and leave
`backColor` unset; the background then comes from `visualStyles.pivotTable.*.columnHeaders` in
the theme. **A pair split across two files desyncs on every theme change.**

Incident (SKILLZ demo report, dark → light conversion): `MatrixMain`/`MatrixYearly` carried
`fontColor` in `visual.json` and no `backColor` at all. After the theme was inverted the header
background became white while the font color — repainted by the hex sweep — stayed light, and
the header disappeared. The same pair was already broken in the ORIGINAL dark theme:
`#0f172a` on `#1e293b` = **1.3:1**, i.e. the header was unreadable before the conversion even
started (this was one of the early "nothing is visible" user reports).

**Law.** If a visual overrides ONE side of a pair (font) and leaves the other (background) to
the theme, the pair desyncs on any theme change. Either both sides live in the theme, or both
live in the visual — never one each. Same law for the other split pairs of this visual:
`rowHeaders.fontColor`/`backColor`, `values.fontColorPrimary`/`backColorPrimary`,
`total.fontColor`/`backColor`.

After any theme change, verify the pairs **programmatically** (resolve each side, compute the
contrast) rather than by eyeballing the canvas.
