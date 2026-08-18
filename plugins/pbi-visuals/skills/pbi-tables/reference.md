# Table (tableEx) — Reference

Companion to `SKILL.md`. All names below are verified against
`docs/research/reportThemeSchema-2.155.json` (`definitions.visual-tableEx`) and
`docs/research/theme-visuals.md` §6.3 — never recalled from memory (BRIEF F2). Tokens
(`color/*`, `type/*`, `ramp/*`) resolve in `docs/DESIGN-TOKENS.md`.

## 1. Visual-type key

`tableEx` in `theme.json → visualStyles` and in `report.json`/`visual.json` `visualType`.
**`table` does not exist** — the Format-pane name is "Table" but the schema/JSON key is
always `tableEx` (theme-visuals.md §5, "Names that do NOT exist").

## 2. The 9 verified cards (beyond the common cards every visual has)

| Card | Purpose | Key properties (schema-verified) |
|---|---|---|
| `general` | Misc | `formatString` |
| `columnHeaders` | Top header row | `alignment` (`Auto`\|`Left`\|`Center`\|`Right`), `backColor`, `fontColor`, `bold`, `fontFamily`, `fontSize`, `italic`, `underline`, `wordWrap`, `outlineColor`/`outlineStyle`/`outlineWeight`, `columnAdjustment` (`fitToContent`\|`growToFit`\|`fixedWidth`), `autoSizeColumnWidth`, `customColumnWidth`, `defaultColumnWidth` |
| `columnWidth` | Per-column explicit width (one entry per column, keyed by selector) | `value` (number, px) |
| `values` | Detail cell body | `fontColorPrimary`/`Secondary`, `backColorPrimary`/`Secondary` (zebra), `bandedRowHeaders`-equivalent via the two back colors, `bold`, `italic`, `underline`, `wordWrap`, `icon`, `urlIcon`, `webURL` (hyperlink/image columns), `outlineColor`/`outlineStyle`/`outlineWeight` |
| `columnFormatting` | Per-column CF (bars/color/icons) | `backColor`, `fontColor`, `dataBars`, `labelDisplayUnits`, `labelPrecision`, `alignment`, `styleHeader`/`styleTotal`/`styleValues` (which grains inherit the CF) |
| `grid` | Gridlines & row density | `gridHorizontal`, `gridHorizontalColor`, `gridHorizontalWeight`, `gridVertical`, `gridVerticalColor`, `gridVerticalWeight`, `rowPadding`, `textSize`, `imageHeight`/`imageWidth`, `outlineColor`/`outlineStyle`/`outlineWeight` |
| `total` | Grand total row | `backColor`, `bold`, `underline`, `fontColor`, `fontFamily`, `fontSize`, `italic`, `label` (custom total-row text), `totals` (boolean master toggle), `outlineColor`/`outlineStyle`/`outlineWeight` (border-equivalent — **there is no property literally named `border`, don't invent one**) |
| `sparklines` | In-cell trend (built-in, distinct from `dax-svg` custom measures) | `chartType` (`line`\|`column`), `dataColor`, `markerColor`, `markerShape`, `markerSize`, `markers`, `strokeWidth` |
| `accessibility` | Alt text | `altTextColumns`, `rowWithReferenceText` |

`clustering` exists as a card key but ships with zero properties in the schema — do not use it.
Any property not in this table: read it from `reportThemeSchema-2.1xx.json` or copy from a
ground-truth `tableEx` — do not guess. Card values are always **arrays** of objects.

## 3. Ready-to-adapt theme fragment

`ColorId` mapping used below is the THEME-file mapping (0-based straight into `dataColors`):
`ColorId 0` = `color/brand`. Re-verify against the target theme before emitting
(DESIGN-TOKENS §1.7). One deliberate divergence from the theme-visuals §6.3 / master-theme
example: this fragment sets `alignment: "Auto"` (legal enum: Auto/Left/Center/Right) so the
header follows each column's data alignment, where those examples use `"Left"` — a design
choice of this skill, not a verbatim copy.

```json
"tableEx": {
  "*": {
    "columnHeaders": [{
      "backColor": { "solid": { "color": { "expr": {
                    "ThemeDataColor": { "ColorId": 0, "Percent": 0 } } } } },
      "fontColor": { "solid": { "color": "#FFFFFF" } },
      "bold": true, "fontSize": 10, "alignment": "Auto", "wordWrap": true,
      "columnAdjustment": "fixedWidth"
    }],
    "grid": [{
      "gridHorizontal": true,
      "gridHorizontalColor": { "solid": { "color": "#E6E6E6" } },
      "gridVertical": false, "rowPadding": 4, "textSize": 9
    }],
    "values": [{
      "fontColorPrimary": { "solid": { "color": "#333333" } },
      "backColorPrimary": { "solid": { "color": "#FFFFFF" } },
      "backColorSecondary": { "solid": { "color": "#FAFAFA" } }
    }],
    "total": [{
      "bold": true,
      "fontColor": { "solid": { "color": "#333333" } },
      "totals": true
    }],
    "accessibility": [{ "altTextColumns": "" }]
  }
}
```

Per-column widths and per-column CF (`columnFormatting`) are set per visual in its own
`report.json`/`visual.json` `objects`, not in the theme — wiring mechanics (selectors, `$id`
scope) belong to `powerbi-visuals`; CF rule/threshold semantics to `pbi-conditional-formatting`.

## 4. Sort, totals, and CF color choice

- **Default sort** lives in the visual's own query (`orderBy`), not the theme. Copy the shape
  from a ground-truth sorted `tableEx` rather than hand-writing it.
- **Totals**: toggle the whole row off with `total.totals: false` when the aggregate is
  meaningless (percentages, ratios, unique counts) rather than leaving a misleading sum.
  For a single measure's total, guard the measure itself (`IF(HASONEVALUE(...), ...)`).
  TMDL `summarizeBy: none` disables auto-aggregation of a RAW numeric column only — it has
  no effect on an explicit DAX measure's total row (MS Learn: the total evaluates the
  measure in the total's filter context; default summarization applies to columns).
- **CF color choice** (mechanics belong to `powerbi-visuals`/`pbi-conditional-formatting`):
  magnitude → `ramp/brand-seq` (single hue, light→dark, monotonic); variance vs. a
  target/plan/zero → `ramp/diverging`, midpoint anchored at the actual meaningful center, never
  the data mean. Never pair a CF background with `values` zebra on the same column — pick one
  background system per column.
