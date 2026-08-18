---
name: powerbi-visuals
description: "Owns the report.json MECHANICS of Power BI PBIR-Legacy visuals — add/clone a visual container from code, rebind columns/measures (projections, queryRef), set colors/axes/labels in config JSON, wire drill-through plumbing, embed a measure-driven SVG. This skill is HOW the JSON is edited; WHAT a visual should look like belongs to its design skill. Do NOT trigger for bookmark/visibility mechanics (powerbi-bookmarks); design/styling of a visual type — tables (pbi-tables), matrix (pbi-matrix), KPI cards (pbi-kpi-cards), slicers (pbi-slicers-filter-panel), charts (pbi-bar-column-charts etc.); arrangement on canvas (pbi-page-layout); authoring SVG measures (dax-svg); PBIP folder structure/renames (pbip skill). Triggers - 'додай візуал у report.json', 'клонуй візуал', 'привʼяжи міру до візуала', 'зміни кольори графіка в json', 'add visual to report.json', 'clone visual', 'visualType', 'projections', 'queryRef', 'byte-faithful report.json edit'."
---

# Power BI visuals (PBIR-Legacy report.json)

Build visuals by editing `report.json` directly. **Golden rule: clone an existing visual of the target type, then swap fields/measures/ids/positions/colors.** Hand-writing a config from scratch risks subtle schema errors that make Desktop refuse the file. Use `pbir.py` (in this skill folder) for byte-faithful edits.

## Contrast & consistency (ALWAYS check — non-negotiable)
Before finishing ANY visual, verify each foreground element against **the background it actually sits on**:
- **Light text on dark fills; dark text on light fills.** Never dark-on-dark or light-on-light. E.g. white (`#FFFFFF`) data labels inside colored bar segments; dark (`#003a5d` navy / `#3a3a3a`) text on white cards. If a segment/cell color is dark → label white; if light → label dark.
- Check **every** text element against **its own** background, not the page: data labels (vs the bar/segment fill), axis & legend labels (vs card/page), card numbers (vs card backdrop), button text (vs button fill), matrix/table values, and SVG text (vs the SVG cell fill it overlaps).
- A measure-SVG placed on a white card backdrop should have a **transparent or matching** background so it blends — don't paint a differently-colored rect behind it.
- **Keep ONE style across the block/report**: same font family, title/accent color, card backdrop (rounded white + subtle border), corner radius, and color palette. **Reuse colors already used by sibling visuals / the theme** rather than inventing new ones.
- If the report has a dark theme (or may switch), sanity-check contrast in both; avoid colors that only read on one background. Prefer `ThemeDataColor` where the value should follow the theme.

## File shape
`report.json` = pretty JSON (indent 2, **CRLF, no BOM**). `sections[i]` = a page; `sections[i].visualContainers[j]` = a visual. The report-level `config` and each `visualContainer.config` and `section.filters` are **compact JSON strings** — parse/dump them separately. Edit via `pbir.py`:
```python
import pbir
d   = pbir.load(REPORT)
gp  = next(s for s in d['sections'] if s['name']==SECTION)
cfg = json.loads(vc['config']); ... ; vc['config'] = pbir.dump_config(cfg)
pbir.save(d, REPORT)
```

## visualContainer anatomy
```json
{ "config": "<compact JSON string>", "filters": "[]",
  "x": 0.0, "y": 0.0, "z": 1000.0, "width": 300.0, "height": 200.0 }
```
`filters` is optional (a JSON string, default `"[]"` = no visual-level filter). The top-level `x/y/z/width/height` mirror `config.layouts[0].position` (often rounded).

`config` (the string) parses to:
```json
{ "name": "<20-hex unique id>",
  "layouts": [{"id":0,"position":{"x":0,"y":0,"z":1000,"width":300,"height":200,"tabOrder":0}}],
  "singleVisual": { ... },          // OR "singleVisualGroup": {"displayName","groupMode":0,"isHidden":true}
  "parentGroupName": "<group id>" } // omit for top-level
```
- **Positions are RELATIVE to `parentGroupName`.** A child at x=10,y=6 sits 10/6 px inside its group. Top-level tab groups all stack at the same canvas region.
- **⚠️ Preserve `parentGroupName` when rebuilding a container.** Dropping it turns the visual into a top-level orphan that **leaks onto every tab** (it's no longer hidden by the group's bookmark cascade). This is a classic self-inflicted bug.
- `z` is per-visual canvas stacking order. Higher = front. To overlay (e.g. a transparent click layer over a chart) give the overlay a higher `z`.

## singleVisual
```json
{ "visualType": "clusteredBarChart",
  "drillFilterOtherVisuals": true,
  "projections": { "<role>": [ {"queryRef":"...","active":true} ] },
  "prototypeQuery": { "Version":2, "From":[...], "Select":[...], "OrderBy":[...] },
  "objects": { ... },      // data-role formatting
  "vcObjects": { ... },    // container formatting (title, background, border, padding, visualLink)
  "columnProperties": { "<queryRef>": {"displayName":"..."} } }  // optional column renames
```

### Binding fields — projections + prototypeQuery (keep them in sync)
- **Column**: `queryRef = "Entity.Column"`; Select: `{"Column":{"Expression":{"SourceRef":{"Source":"f"}},"Property":"Col"},"Name":"Entity.Col","NativeReferenceName":"Ukr label"}`.
- **Measure**: `queryRef = "_Measures.Measure Name"`; Select: `{"Measure":{"Expression":{"SourceRef":{"Source":"_"}},"Property":"Measure Name"},"Name":"_Measures.Measure Name","NativeReferenceName":"label"}`.
- **Aggregated numeric column** (table value): `queryRef = "Sum(Entity.Col)"`, Name matches.
- `From`: `[{"Name":"f","Entity":"Entity","Type":0},{"Name":"_","Entity":"_Measures","Type":0}]`. The `Source` in Select refers to the `From` alias.
- `OrderBy`: `[{"Direction":2,"Expression":{...}}]` — **1 = ascending, 2 = descending**.
- `"Name"` in Select == the `queryRef`. `NativeReferenceName` is the field caption (set Ukrainian here, but table HEADERS use `columnProperties[queryRef].displayName`).

### Projection roles by visual type
| visualType | roles |
|---|---|
| `textbox` | (none — text in objects.general.paragraphs) |
| `shape` | (none — pure styling) |
| `cardVisual` | `Data` (one measure) |
| `htmlContent443BE3AD55E043BF878BED274D3A6855` | `content` (one measure returning HTML/SVG) |
| `clusteredBarChart` / `clusteredColumnChart` | `Category`, `Y`, optional `Series` |
| `hundredPercentStackedBarChart` | `Category`, `Series`, `Y` |
| `donutChart` / `pieChart` | `Category`, `Y` |
| `pivotTable` (matrix) | `Rows`, `Columns`, `Values` |
| `tableEx` | `Values` (columns) |
| `actionButton` | (none — action in vcObjects.visualLink) |
| `slicer` / `advancedSlicerVisual` | `Values` |

## Formatting: objects vs vcObjects
Property wrapper everywhere: `{"properties": {"<prop>": {"expr": {"Literal": {"Value": "<v>"}}}}}`. Value encodings: `"'text'"` (quoted string), `"true"`/`"false"`, `"8L"` (int/long), `"0D"` (double), `"10pt"`/`"9D"` (font size), color → `{"solid":{"color":{"expr":{"Literal":{"Value":"'#1B3A5C'"}}}}}` or `{"...ThemeDataColor":{"ColorId":0,"Percent":0}}` (ColorId 0 ≈ first theme color).

- **objects** (data formatting): `labels` (data labels: show/labelColor/labelDisplayUnits), `categoryAxis`/`valueAxis` (show/showAxisTitle/labelColor), `legend` (show/position 'TopCenter'/showTitle), `dataPoint` (fill — see below), `grid`/`columnHeaders`/`rowHeaders`/`values`/`total`/`subTotals` (table/matrix), `general` (textbox paragraphs, image url), `shape`/`fill`/`outline` (shape).
- **vcObjects** (container): `title` (show false to hide), `background` (show/color/transparency), `border` (show/width/radius/color), `padding` (top/bottom/left/right), `visualHeader` (show false hides the ⋯ menu), `visualLink` (button action), `divider`.

### dataPoint conditional colors
Per-series/category color via a selector:
```json
"dataPoint": [
  {"properties":{"fill":{"solid":{"color":{"expr":{"Literal":{"Value":"'#1B3A5C'"}}}}}},
   "selector":{"data":[{"dataViewWildcard":{"matchingOption":1}}]}},          // default for all
  {"properties":{"fill":{"solid":{"color":{"expr":{"Literal":{"Value":"'#C1272D'"}}}}}},
   "selector":{"data":[{"scopeId":{"Comparison":{"ComparisonKind":0,           // 0=equals
     "Left":{"Column":{"Expression":{"SourceRef":{"Entity":"fact_X"}},"Property":"Cat"}},
     "Right":{"Literal":{"Value":"'Без рішень'"}}}}}]}} ]
```

## Visual cookbook (minimal skeletons)
- **textbox**: `objects.general.paragraphs=[{"textRuns":[{"value":"Title","textStyle":{"fontWeight":"bold","fontSize":"16pt","color":"#003a5d"}}]}]`.
  - **⚠️ ANTI-SCROLLBAR (mandatory, both required):** a hand-built textbox shows a vertical scrollbar unless you set **BOTH** `vcObjects.background.show:false` **AND** `vcObjects.padding` = `[{"properties":{"top":{...0D},"bottom":{...0D},"left":{...0D},"right":{...0D}}}]` (all four sides `0D`). Setting only `background.show:false` is the classic half-fix that still scrolls — PBI's default ~8px padding eats the height so an N-pt line no longer fits an N-pt-tall box. Also give height headroom (box height ≥ ~2.2× font pt: 10pt → ≥22px, safer ≥26px). Clone an existing report title textbox and confirm it carries the full padding block — some older textboxes omit it and only survive because they're tall.
- **rounded card backdrop (shape)**: `objects.shape={tileShape:'rectangleRounded',rectangleRoundedCurve:'8L'}`, `objects.fill={show:true,fillColor:#FFFFFF}`, `vcObjects.border={show:true,radius:'11D',width:'1D',color:#E6E6E6}`, `visualHeader.show:false`. Low z (backdrop).
- **cardVisual** (single number): `projections.Data=[measure]`; `objects.labels.fontSize` for big value; `categoryLabels.show:false` to hide caption.
- **measure-SVG** (2 modes):
  - **htmlContent** custom visual: measure returns raw `"<div style='...overflow:hidden;...'>"&svg&"</div>"`; bind to `content`. The custom-visual id must be in report `publicCustomVisuals`.
  - **cardVisual + ImageUrl**: measure has `dataCategory: ImageUrl` and returns `"data:image/svg+xml;utf8,"&svg`; bind to a card's `Data`.
- **bar/column chart**: Category+Y(+Series); `labels.show:true`, `valueAxis.show:false`, `legend.show:false`, `dataPoint` colors, `vcObjects.title.show:false`.
- **single 100% segmented bar**: `hundredPercentStackedBarChart` with **Category = a constant column** (add a calc column `Const="X"` so there's exactly one bar), `Series = the splitting column`, `Y = count`; one `dataPoint` per series value; `labels.show:true` for %.
- **pivotTable (matrix)**: Rows+Columns+Values. Hide chrome: `objects.columnHeaders.show:false`, `rowHeaders.show:false`, `grid.gridVertical/gridHorizontal:false`, `total.totals:false`, `subTotals.rowSubtotals/columnSubtotals:false`, `vcObjects.background.show:false`, `visualHeader.show:false`.
  - **Transparent click/drill overlay**: do the above + use a **text measure returning `""`** as Values (cells exist → clickable, but show nothing) and put the matrix at a higher z over the visible chart. Cells align best when both the chart-SVG (`preserveAspectRatio='none'`, grid fills its box) and the matrix occupy the **same rect**. Alignment usually needs a Desktop-screenshot tuning pass.
- **tableEx**: `projections.Values=[columns]`; numeric → `"Sum(Entity.Col)"`; rename headers with `columnProperties[queryRef].displayName`.
- **actionButton**: `objects.icon=[{properties:{shapeType:'blank'},selector:{id:'default'}},{properties:{show:false}}]`, `objects.text=[{properties:{show:true}},{properties:{text:'Деталізація',fontColor:#fff,fontSize:'10D',horizontalAlignment:'center'},selector:{id:'default'}}]`, `objects.fill` for background. Action in `vcObjects.visualLink`: `type` ∈ `'PageNavigation'` (`navigationSection`), `'Drillthrough'` (`drillthroughSection`+`navigationSection`), `'Back'`, `'Bookmark'` (`bookmark`+`navigationSection`). A **drill-through** button is disabled unless the destination's drill field is single-valued in context → for "open the whole list" use **PageNavigation**.

## Drill-through pages
A detail page is a section with `config` `{"objects":{"background":[...],"displayArea":[...]},"visibility":1,"type":2}` and one or more **drill-through filter fields** in `section.filters` with `"howCreated":5`. Any visual elsewhere that USES such a field gets right-click → *Drill through* → this page, carrying that field's value (plus the source page's filter context = team/RLS). Add multiple drill fields (e.g. `Matrix_Row`+`Matrix_Col`) so different source visuals can target the same page.

## DAX-for-SVG gotchas
- **Locale decimals**: concatenating a fractional number can emit `,` and break SVG. Use **integer coordinates** or `FORMAT(x,"0")`. Force display commas in TEXT via `SUBSTITUTE(FORMAT(x,"0.0%"),".",",")`.
- Use **single quotes** for SVG attributes (the DAX string delimiter is `"`), so no escaping.
- `preserveAspectRatio='none'` makes an SVG fill its container exactly (predictable for overlays); `'xMidYMid meet'` letterboxes.
- Inside a ` ``` `-fenced DAX measure, `//` and `/* */` are fine (it's DAX, not TMDL).

## Desktop linter (re-inject defaults)
On save, PBI Desktop **strips `objects` properties it deems default** — notably `columnHeaders.show=false`, `total.totals=false`, `grandTotal.show=false`, `subTotals.rowSubtotals=false` on matrices. After a Desktop save, `git diff` and **re-inject** anything that vanished; don't assume your edit was wrong.

## Workflow checklist
1. Back up `report.json` → `.bak`.
2. Find a working visual of the target type; dump its parsed `config` to learn the schema; clone + swap.
3. Mint unique 20-hex `name` ids; set `parentGroupName` (preserve it on rebuilds!).
4. Edit with `pbir.py`; keep `projections` and `prototypeQuery.Select` in sync.
5. Validate: JSON reloads; line-diff localized (only your containers + maybe the bookmarks `config` line).
6. **Any hand-built textbox** → set `padding` 0 (all four sides) **and** `background.show:false`, height ≥ ~2.2× font pt (see textbox cookbook). Skipping padding = scrollbar. Diff every new textbox's `vcObjects` against a known-good one before declaring done.
7. **Close Power BI Desktop WITHOUT saving**, reopen `.pbip` (model recalcs; Desktop overwrites JSON on save).
8. Screenshot-tune styling/alignment; re-inject linter-stripped props.

## Related
- **powerbi-bookmarks** skill — visibility, tab isolation, and the critical `options.targetVisualNames` scope rule. Any new visual/group that must show on one tab only is wired there.
