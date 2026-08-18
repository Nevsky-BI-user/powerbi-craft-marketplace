---
name: deneb-vegalite
description: >
  Use this skill whenever the user asks to create, edit, debug, or optimize Deneb visuals in Power BI using Vega-Lite or Vega JSON specifications. This includes bar charts, column charts, line charts, area charts, scatter plots, heatmaps, bullet charts, waterfall charts, KPI cards, small multiples, layered visuals, faceted views, conditional formatting, cross-filtering, tooltip configuration, or any Vega-Lite/Vega JSON code for the Deneb custom visual. Also trigger when the user mentions "Deneb", "Vega-Lite", "Vega", "Deneb spec", __selected__, pbiFormat, config tab, params, transforms, encoding channels, mark types, or shows existing Deneb JSON with issues. Trigger even for "зроби Deneb chart", "напиши Vega-Lite spec", "Deneb візуал". Always output FULL JSON — never abbreviate. Output Specification and Config as separate blocks.
---

# Deneb Vega-Lite Skill

This skill produces Vega-Lite (and optionally Vega) JSON specifications for the Deneb
custom visual in Power BI.

## Critical Rule: Full Output

**Every response that contains a Deneb specification MUST output the entire JSON from opening `{` to closing `}`.**
Never truncate. Never use `...`, `// ...`, `/* rest unchanged */`, or any placeholder.
The user will paste this directly into the Deneb Visual Editor.
Partial output is useless — the editor requires valid complete JSON.

If a spec is being edited, output the entire spec with the edit applied.

Always output two separate JSON blocks:
1. **Specification** (the main spec)
2. **Config** (the config tab)

## What Is Deneb

Deneb is a certified custom visual for Power BI that renders Vega or Vega-Lite
specifications. Data flows from Power BI's data model into a dataset named `"dataset"`.
The spec defines how that data is visualized via marks, encodings, transforms, and layers.

Key properties:
- Certified by Microsoft — works in publish-to-web, mobile, Report Server, PDF export.
- No external dependencies — all libraries are bundled.
- Supports Power BI interactivity: tooltips, cross-filtering, context menu, drillthrough.
- Row limit defaults to 10,000 (configurable in settings).
- Cannot load external data — all data must come from Power BI's Values data role.

## Specification Structure (Vega-Lite)

Every Vega-Lite spec in Deneb follows this skeleton:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "data": {"name": "dataset"},
  "params": [],
  "transform": [],
  "layer": [
    {
      "mark": {"type": "bar"},
      "encoding": {}
    }
  ],
  "encoding": {}
}
```

### Top-level properties

| Property | Purpose |
|----------|---------|
| `data` | Always `{"name": "dataset"}` — binds to Power BI data |
| `mark` | Shape type: `bar`, `line`, `point`, `area`, `text`, `rule`, `rect`, `arc`, `tick`, `trail`, `geoshape` |
| `encoding` | Maps data fields to visual channels: `x`, `y`, `color`, `size`, `opacity`, `text`, `tooltip`, `order`, `detail` |
| `transform` | Data transformations: `filter`, `calculate`, `aggregate`, `fold`, `flatten`, `window`, `joinaggregate`, `bin` |
| `params` | Named constants (like DAX variables) or selection parameters |
| `layer` | Array of mark+encoding objects drawn in order (later = on top) |
| `facet` | Split data into small multiples by a field |
| `concat` / `hconcat` / `vconcat` | Combine multiple views |
| `resolve` | Control shared vs independent scales/axes across layers |
| `title` | Chart title (string or object with subtitle, anchor, etc.) |

### Field types

| Type | Deneb keyword | Use for |
|------|---------------|---------|
| Categorical | `"nominal"` | Text categories (names, statuses) |
| Ordered category | `"ordinal"` | Ranked categories, months as text |
| Numeric | `"quantitative"` | Measures, continuous numbers |
| Date/time | `"temporal"` | Date columns |

### Encoding channels

```json
"encoding": {
  "x": {"field": "Category", "type": "nominal"},
  "y": {"field": "Sales", "type": "quantitative"},
  "color": {"field": "Region", "type": "nominal"},
  "size": {"field": "Profit", "type": "quantitative"},
  "opacity": {"value": 0.8},
  "tooltip": [
    {"field": "Category", "type": "nominal"},
    {"field": "Sales", "type": "quantitative", "format": "$#,0", "formatType": "pbiFormat"}
  ]
}
```

## Data Binding

Power BI columns and measures added to the Deneb visual's Values data role become
fields in the `"dataset"`. Reference them by their exact name.

**Special characters:** Deneb replaces `.`, `[`, `]`, `\`, `"` in field names with `_`.
So a measure named `Avg.Sales` becomes `Avg_Sales` in the spec.

**Row context:** The dataset works like a Power BI table visual — each row is the
unique combination of all columns/measures added. Plan granularity before writing the spec.

## Config Tab

The Config tab holds global styling — fonts, colors, axis defaults, mark defaults.
It is separate from the spec, keeping the spec cleaner.

Standard Power BI-friendly config:

```json
{
  "view": {"stroke": "transparent"},
  "font": "Segoe UI",
  "axis": {
    "ticks": false,
    "grid": false,
    "domain": false,
    "labelColor": "#605E5C",
    "labelFontSize": 12,
    "titleFontSize": 14,
    "titleColor": "#252423"
  },
  "axisX": {
    "labelAngle": 0,
    "domain": true
  },
  "axisY": {
    "labelPadding": 10
  },
  "bar": {
    "cornerRadiusTopLeft": 4,
    "cornerRadiusTopRight": 4
  },
  "line": {
    "strokeWidth": 2,
    "interpolate": "monotone"
  },
  "area": {
    "line": true,
    "opacity": 0.6,
    "interpolate": "monotone"
  },
  "text": {
    "font": "Segoe UI",
    "fontSize": 11,
    "fontWeight": "normal"
  }
}
```

Config properties can use `params` for reusable values:

```json
{
  "params": [
    {"name": "globalFont", "value": "Segoe UI"},
    {"name": "primaryColor", "value": "#004385"}
  ],
  "font": {"expr": "globalFont"},
  "bar": {
    "color": {"expr": "primaryColor"}
  }
}
```

## Number Formatting

Deneb supports two formatting systems:

### D3 format (default)
```json
"format": ",.0f"
```
Common D3 specifiers: `,` = thousands separator, `.2f` = 2 decimal places,
`.0%` = percentage, `.2s` = SI prefix (k, M, G).

### pbiFormat (Power BI format strings)
Preferred when working with Power BI currency, percentages, and locale-specific formats:

```json
"axis": {
  "format": "$#,0",
  "formatType": "pbiFormat"
}
```

In expressions (transforms, text marks):
```json
{"calculate": "pbiFormat(datum.Sales, '$#,0')", "as": "formatted_sales"}
```

pbiFormat with options (locale, precision):
```json
{"calculate": "pbiFormat(datum.Sales, '#,0', {value: datum.Sales, precision: 1, cultureSelector: 'en-US'})", "as": "fmt"}
```

For encoding:
```json
"text": {
  "field": "Sales",
  "type": "quantitative",
  "format": "$#,0,.0K",
  "formatType": "pbiFormat"
}
```

### Auto-unit formatting
```json
"format": "",
"formatType": "pbiFormatAutoUnit"
```

## Transforms

### calculate — create new fields (like calculated columns)
```json
"transform": [
  {"calculate": "datum.Actual - datum.Budget", "as": "Variance"},
  {"calculate": "datum.Variance >= 0 ? '#4CAF50' : '#F44336'", "as": "varColor"},
  {"calculate": "datum.Actual >= datum.Budget", "as": "isPositive"}
]
```

### filter — remove rows
```json
"transform": [
  {"filter": "datum.Sales > 0"},
  {"filter": "isValid(datum.Value)"}
]
```

### window — running totals, ranks
```json
"transform": [
  {
    "window": [{"op": "sum", "field": "Sales", "as": "RunningTotal"}],
    "sort": [{"field": "Date", "order": "ascending"}]
  }
]
```

### joinaggregate — add aggregated values to each row
```json
"transform": [
  {
    "joinaggregate": [{"op": "max", "field": "Sales", "as": "MaxSales"}]
  },
  {"calculate": "datum.Sales / datum.MaxSales", "as": "NormalizedSales"}
]
```

### fold — unpivot columns (for multi-measure charts)
```json
"transform": [
  {"fold": ["Actual", "Budget"], "as": ["Measure", "Value"]}
]
```

## Layers

Layer multiple marks in drawing order (later layers render on top):

```json
"layer": [
  {
    "mark": {"type": "bar"},
    "encoding": {"y": {"field": "Actual"}}
  },
  {
    "mark": {"type": "tick", "color": "red", "thickness": 2},
    "encoding": {"y": {"field": "Budget"}}
  },
  {
    "mark": {"type": "text", "dy": -10},
    "encoding": {
      "y": {"field": "Actual"},
      "text": {"field": "Actual", "type": "quantitative", "format": ",.0f"}
    }
  }
]
```

## Cross-Filtering (__selected__)

Deneb generates a `__selected__` field per row: `"on"`, `"off"`, or `"neutral"`.
- `"on"` — row is selected
- `"off"` — another row is selected (this one is not)
- `"neutral"` — nothing is selected

Enable in Deneb settings: "Expose cross-filtering values for dataset rows".

Use in encoding to dim unselected bars:

```json
"opacity": {
  "condition": {
    "test": {"field": "__selected__", "equal": "off"},
    "value": 0.3
  },
  "value": 1
}
```

Cross-filtering only works on un-transformed data points (the original row context).
If you apply transforms that mutate data, cross-filtering may not resolve.

Data point limit: defaults to 50, max 250. Configurable in Deneb settings.

## Tooltips

Default tooltips are enabled in Deneb settings. Add `"tooltip": true` to mark:

```json
"mark": {"type": "bar", "tooltip": true}
```

Custom tooltip fields:
```json
"encoding": {
  "tooltip": [
    {"field": "Category", "type": "nominal", "title": "Category"},
    {"field": "Sales", "type": "quantitative", "format": "$#,0", "formatType": "pbiFormat", "title": "Revenue"}
  ]
}
```

Report page tooltips work if the data point is un-transformed.

## Params (Variables)

```json
"params": [
  {"name": "barColor", "value": "#004385"},
  {"name": "highlightColor", "value": "#FF6B35"}
]
```

Use in marks: `"color": {"expr": "barColor"}`
Use in transforms: `"calculate": "datum.IsActual ? barColor : highlightColor"`
Config tab params are also accessible from the spec.

## Conditional Formatting

### Method 1: In mark property via expr
```json
"mark": {
  "type": "bar",
  "color": {"expr": "datum.Variance >= 0 ? '#4CAF50' : '#F44336'"}
}
```

### Method 2: In encoding via condition
```json
"color": {
  "condition": [
    {"test": "datum.Score >= 90", "value": "#4CAF50"},
    {"test": "datum.Score >= 70", "value": "#FFC107"}
  ],
  "value": "#F44336"
}
```

### Method 3: Via calculate transform + field reference
```json
"transform": [
  {"calculate": "datum.Score >= 90 ? '#4CAF50' : datum.Score >= 70 ? '#FFC107' : '#F44336'", "as": "scoreColor"}
],
"encoding": {
  "color": {"field": "scoreColor", "type": "nominal", "scale": null}
}
```
`"scale": null` tells Vega-Lite to use the field values as literal colors.

## Sorting

```json
"x": {
  "field": "Category",
  "type": "nominal",
  "sort": "-y"
}
```

- `"-y"` — sort descending by y-axis measure
- `"y"` — sort ascending
- `["A", "B", "C"]` — explicit order
- `{"field": "SortOrder", "order": "ascending"}` — sort by another field

## Axis Formatting

```json
"axis": {
  "title": null,
  "labelAngle": -45,
  "labelPadding": 8,
  "format": "%b-%y",
  "tickCount": 5,
  "grid": true,
  "gridDash": [2, 4],
  "gridOpacity": 0.3,
  "domain": true,
  "domainColor": "#999",
  "labelExpr": "datum.value > 1e9 ? datum.value / 1e9 + 'B' : datum.value > 1e6 ? datum.value / 1e6 + 'M' : datum.value"
}
```

Date axis:
```json
"x": {
  "field": "Date",
  "type": "temporal",
  "timeUnit": "yearmonth",
  "axis": {"format": "%b-%y"}
}
```

## Common Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| Empty visual | No fields in Values data role | Add at least one column/measure |
| Field not found | Special chars in name (`.`, `[`, `]`) | Use underscore replacement |
| Measures show wrong values | Wrong granularity | Check what rows the dataset produces (think like a table visual) |
| Cross-filtering doesn't work | Data was transformed | Use un-transformed datum for cross-filter marks |
| Cross-filtering one-way only | Known limitation | Deneb-to-Deneb cross-filtering has limitations |
| Tooltip shows [object Object] | Used pbiFormat in format property without formatType | Add `"formatType": "pbiFormat"` |
| Currency shows wrong symbol | Browser locale mismatch | Use `"options": {"cultureSelector": "en-US"}` |
| Null values break line | Nulls in data | Add `{"filter": "isValid(datum.FieldName)"}` transform |
| Validation error in config | Unsupported property | Check Vega-Lite schema version; remove invalid property |
| Bar chart instead of column | x/y fields swapped | Swap field assignments in encoding |

## Performance Considerations

- Default row limit: 10,000. Increase in Deneb settings if needed but expect slower rendering.
- Complex transforms (window, joinaggregate) on large datasets impact render time.
- Multiple layers with many data points compound rendering cost.
- Use DAX for heavy calculations; use Vega-Lite transforms for light data shaping.

## Output Format

Every spec output must be:
1. **Complete** — full JSON, no abbreviations
2. **Two blocks**: Specification + Config
3. **Valid JSON** — no comments (JSON does not support `//` comments; Deneb's JSONC editor does, but output pure JSON for safety)
4. **Field names matching** — use exact Power BI column/measure names (with special char replacements)
5. **Formatted** — proper indentation for readability

Read `references/recipes.md` for complete copy-paste-ready specifications for common chart types.
