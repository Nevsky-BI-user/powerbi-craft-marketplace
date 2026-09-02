# Power BI Report Theme (reportThemeSchema) & Visual Types — Authoritative Reference

Research reference for design-level Power BI skills. Covers the theme JSON format
(`reportThemeSchema`), the complete list of internal visual-type names for `visualStyles`,
text classes, structural colors, worked examples, and known pitfalls.

**Sources (verified 2026-07):**
- JSON Schema: [microsoft/powerbi-desktop-samples → Report Theme JSON Schema](https://github.com/microsoft/powerbi-desktop-samples/tree/main/Report%20Theme%20JSON%20Schema).
  Versions available: `reportThemeSchema-2.114.json` … `reportThemeSchema-2.155.json` (one file per Desktop release; 2.155 = latest at time of writing).
  Facts below were extracted programmatically from **2.143** and cross-checked against **2.155** — the visual-type key list is identical in both.
- Microsoft Learn: [Create custom report themes](https://learn.microsoft.com/power-bi/create-reports/report-themes-create-custom),
  [Use report themes](https://learn.microsoft.com/power-bi/create-reports/desktop-report-themes).

---

## 1. Theme file anatomy

A theme is one JSON file. Only `name` is required (`"required": ["name"]` in the schema).
The schema root has `"additionalProperties": false` — an unknown **top-level** key fails import validation.

Four functional blocks:

| Block | Top-level keys | Purpose |
|---|---|---|
| Identity | `name`, `$schema` | Theme name (required); optional pointer to a local schema copy for IDE autocomplete |
| Theme colors | `dataColors`, `good`/`neutral`/`bad`, `maximum`/`center`/`minimum`/`null` | Data palette, sentiment, divergent-gradient colors |
| Structural colors | `firstLevelElements` … `background` … (full list §2) | Chrome: axes, gridlines, labels, backgrounds |
| Text & visuals | `textClasses`, `visualStyles`, `icons` | Fonts, per-visual-type defaults, legacy icon sets |

Complete top-level property list (41 keys, schema 2.143 = 2.155):

```
$schema, name, dataColors, textClasses, visualStyles, icons,
good, neutral, bad, maximum, center, minimum, null,
firstLevelElements, secondLevelElements, thirdLevelElements, fourthLevelElements,
foreground, foregroundLight, foregroundDark,
foregroundNeutralLight, foregroundNeutralDark,
foregroundNeutralSecondary, foregroundNeutralSecondaryAlt, foregroundNeutralSecondaryAlt2,
foregroundNeutralTertiary, foregroundNeutralTertiaryAlt,
foregroundSelected, foregroundButton,
background, secondaryBackground, backgroundLight, backgroundNeutral, backgroundDark,
accent, tableAccent, hyperlink, visitedHyperlink,
shapeStroke, disabledText, mapPushpin
```

All color values at the top level are **plain hex strings** matching
`^#[0-9a-fA-F]{8}$|^#(?:[0-9a-fA-F]{3}){1,2}$` (3-, 6-, or 8-digit hex; 8-digit carries alpha).
`icons` is a legacy map/array of `{ "url": "<svg data-uri>", "description": "..." }` objects
(pre-2019 conditional-formatting icon sets; rarely used today).

---

## 2. Theme & structural colors — exact names

### 2.1 Data and sentiment colors

- `dataColors`: array of hex strings — the series palette. Any length; Power BI generates
  extra hues when exhausted.
- `good`, `neutral`, `bad`: status colors for waterfall and KPI visuals.
- `maximum`, `center`, `minimum`, `null`: divergent gradient stops in conditional formatting.

DAX "Field value" conditional formatting accepts these **named theme colors** (return the name
as a string from a measure). Divergent names differ in DAX:

| Theme JSON name | DAX reference name |
|---|---|
| `maximum` | `maxColor` |
| `center` | `midColor` |
| `minimum` | `minColor` |
| `null` | `nullColor` |
| all others (`good`, `bad`, `background`, `tableAccent`, …) | same as JSON name |

### 2.2 The six structural color classes (preferred names + legacy aliases)

| Preferred name | Legacy alias | Formats (abridged) |
|---|---|---|
| `firstLevelElements` | `foreground` | Primary text: labels outside data points, table/matrix values & totals, card data labels, KPI text, textbox default, trend lines, tooltip text |
| `secondLevelElements` | `foregroundNeutralSecondary` | Secondary "light" text: legend & axis labels, table/matrix headers, slicer items, button text/icon/outline |
| `thirdLevelElements` | `backgroundLight` | Axis gridlines, table/matrix grid, shape fill, gauge arc, applied-filter-card background |
| `fourthLevelElements` | `foregroundNeutralTertiary` | Dimmed legend, card category labels, multi-row card bars, disabled button text |
| `background` | — | Label background inside data points, tooltip background, button fill, donut/treemap stroke |
| `secondaryBackground` | `backgroundNeutral` | Table/matrix grid outline, shape-map default, ribbon fill, tooltip separator |
| `tableAccent` | — | Table/matrix grid outline override (wins when present) |

Both alias sets exist as independent top-level keys in the schema. Use **one** naming
convention per theme file (preferred: `firstLevelElements`…); do not mix.

Dark-theme rule of thumb: when diverging from "black-on-white", always set
`firstLevelElements`, `secondLevelElements`, `background` (and primary text-class colors)
together, or data-label backgrounds and gridlines become unreadable.

---

## 3. textClasses — all names, fields, inheritance

Schema: each class is an object with **exactly** these optional fields:
`fontFace` (string), `fontSize` (number, **points, min 6, max 45**), `fontWeight` (string), `color` (hex string).
`additionalProperties: false` per class.

**14 class keys in the schema** (2.143 & 2.155):

```
callout, title, header, label,
largeTitle, dataTitle,
boldLabel, semiboldLabel, largeLabel, smallLabel,
lightLabel, largeLightLabel, smallLightLabel, smallDataLabel
```

Microsoft Learn documents 12 of them; `dataTitle` and `smallDataLabel` are schema-valid but
undocumented (accepted on import).

**4 primary classes** — set these and the rest inherit:

| Primary | JSON name | Defaults | Applies to |
|---|---|---|---|
| Callout | `callout` | DIN, #252423, 45 pt | Card data labels, KPI indicators |
| Title | `title` | DIN, #252423, 12 pt | Axis titles, multi-row card title, slicer header |
| Header | `header` | Segoe UI Semibold, #252423, 12 pt | Key influencers headers |
| Label | `label` | Segoe UI, #252423, 10 pt | Table/matrix headers, grid, values |

**Secondary classes** derive from a primary and override one aspect:

| Secondary | Inherits from | Delta vs primary | Applies to |
|---|---|---|---|
| `largeTitle` | title | 14 pt | Visual title |
| `boldLabel` | label | Segoe UI Bold | Matrix subtotals/grand totals, table totals |
| `semiboldLabel` | label | Segoe UI Semibold | Key influencers profile text |
| `largeLabel` | label | 12 pt | Multi-row card data labels |
| `smallLabel` | label | 9 pt | Reference-line labels, slicer date-range/numeric input/search box |
| `lightLabel` | label | color #605E5C | Legend, button text, category-axis labels, funnel labels, slicer items |
| `largeLightLabel` | label | #605E5C, 12 pt | Card category labels, gauge labels |
| `smallLightLabel` | label | #605E5C, 9 pt | Data labels, value-axis labels |

The "light" variants derive their color from structural colors — in a dark theme set
`secondLevelElements` accordingly. Secondary classes only need explicit entries when you want
to break inheritance (e.g., non-bold totals).

---

## 4. visualStyles — structure of a style record

```json
"visualStyles": {
    "<visualName>": {
        "<stylePresetName>": {
            "<cardName>": [{
                "<propertyName>": <propertyValue>
            }]
        }
    }
}
```

- **`<visualName>`** — internal visual-type key (full list §5), or `"*"` for *all* visual types.
  The schema declares 52 named keys; `additionalProperties` additionally allows **any** other
  key — that is how `"*"` and custom visuals (e.g. `deneb7E15AEF80B9E4D4F8E12924291ECE89A`)
  are themed, and also why a typo in a visual name is silently ignored (see §7).
- **`<stylePresetName>`** — `"*"` = the default style, applied automatically.
  Any other name (schema pattern `^(?!\*$).+$`) creates a **named style preset** that shows up
  in Format pane → Visual → *Style presets*. Named presets inherit from the `"*"` default of the
  same visual; they apply only when the report author selects them.
  The special card `"stylePreset": [{ "name": "<presetName>" }]` inside `"*"` sets which preset
  is pre-selected after theme import.
- **`<cardName>`** — a formatting card (section). `"*"` targets every card of that visual
  (property-name based, see gotcha §7.6). Card names follow the *theme/PBIR object names*, not
  the Format-pane display labels.
- **Card value is always an ARRAY of objects.** Usually one element `[{...}]`. Multiple
  elements are used with a `"$id"` discriminator for card variants:
  - `filterCard`: `"$id": "Available" | "Applied"`
  - `actionButton` state cards (`fill`, `text`, `icon`, `outline`):
    `"$id": "default" | "hover" | "selected" | "disabled"` (exact enum — there is **no** `"press"`).
    *(Corrected 2026-07-10 against schema 2.155: `shape` was previously listed here too, but its
    `fill`/`outline`/`text` item-schemas declare NO `$id` at all — single-element arrays only —
    and `shape` has no `icon` card; the `icon` card with `$id` belongs to `actionButton`.)*
- **Property values:** booleans, numbers, strings/enums as-is; datetime as
  `"datetime'2022-10-05T14:48:00.000Z'"`; colors inside visualStyles are **fill objects**:

```json
"labelColor": { "solid": { "color": "#605E5C" } }                          // hex (3/6/8-digit)
"labelColor": { "solid": { "color": "foregroundNeutralSecondary" } }       // named theme color
"labelColor": { "solid": { "color": { "expr": { "ThemeDataColor":
                 { "ColorId": 2, "Percent": 0.6 } } } } }                  // dataColors ref + shade
```

  `ThemeDataColor.ColorId` indexes the theme palette (0-based; ids 0–7 map to dataColors),
  `Percent` ∈ [-1, 1] darkens/lightens — this is the THEME-file mapping. Inside report.json/
  visual.json `objects` the verified mapping differs: `0` = background, `1` = foreground,
  `N≥2` = `dataColors[N−2]` (production-report audit; DESIGN-TOKENS §1.7 dual-mapping trap). Gradients
  (`fillRule` with `linearGradient2`/`3`) are also allowed where the property supports them.

**16 common cards** exist on every regular visual type (all 48 non-pseudo entries):

```
*, background, border, divider, dropShadow, general, lockAspect, padding,
spacing, stylePreset, subTitle, title, visualHeader, visualHeaderTooltip,
visualLink, visualTooltip
```

Useful common-card properties (exact names): `background: [color, show, transparency]`,
`border: [color, radius, show, width]`, `title: [alignment, background, bold, fontColor,
fontFamily, fontSize, heading, italic, show, text, titleWrap, underline]`,
`dropShadow: [angle, color, position, preset, shadowBlur, shadowDistance, shadowSpread, show,
transparency]`, `visualHeader: [show, background, border, foreground, show*Button …]`,
`padding: [top, bottom, left, right]`.

---

## 5. Complete list of visual-type keys for visualStyles

Extracted from `properties.visualStyles.properties` — **52 keys**, identical in schema
2.143 and 2.155. Case-sensitive camelCase.

### Cartesian charts

| Key | Format-pane / gallery name |
|---|---|
| `barChart` | **Stacked** bar chart |
| `clusteredBarChart` | Clustered bar chart |
| `hundredPercentStackedBarChart` | 100% stacked bar chart |
| `columnChart` | **Stacked** column chart |
| `clusteredColumnChart` | Clustered column chart |
| `hundredPercentStackedColumnChart` | 100% stacked column chart |
| `lineChart` | Line chart |
| `areaChart` | Area chart (basic) |
| `stackedAreaChart` | Stacked area chart |
| `hundredPercentStackedAreaChart` | 100% stacked area chart |
| `lineClusteredColumnComboChart` | Line and clustered column combo |
| `lineStackedColumnComboChart` | Line and stacked column combo |
| `ribbonChart` | Ribbon chart |
| `waterfallChart` | Waterfall chart |
| `scatterChart` | Scatter / bubble chart |

### Shape & part-to-whole charts

| Key | Name |
|---|---|
| `pieChart` | Pie chart |
| `donutChart` | Donut chart |
| `treemap` | Treemap |
| `funnel` | Funnel (note: not `funnelChart`) |
| `gauge` | Gauge |

### Maps

| Key | Name |
|---|---|
| `map` | Map (bubble, Bing) |
| `filledMap` | Filled map (choropleth) |
| `shapeMap` | Shape map |
| `azureMap` | Azure Maps visual |

### Cards, KPI, tables

| Key | Name |
|---|---|
| `card` | Card (classic, single-number) |
| `cardVisual` | Card (**new**), incl. reference labels & small multiples |
| `multiRowCard` | Multi-row card |
| `kpi` | KPI |
| `tableEx` | Table (note: not `table`) |
| `pivotTable` | **Matrix** (note: not `matrix`) |

### Slicers

| Key | Name |
|---|---|
| `slicer` | Slicer (classic: list/dropdown/date/numeric) |
| `advancedSlicerVisual` | Button slicer (a.k.a. "new slicer") |
| `listSlicer` | List slicer (new) |
| `textSlicer` | Text slicer |

### AI & analytics visuals

| Key | Name |
|---|---|
| `decompositionTreeVisual` | Decomposition tree |
| `keyDriversVisual` | Key influencers |
| `aiNarratives` | Smart narrative / Copilot narrative (note: not `smartNarrative`) |
| `qnaVisual` | Q&A visual |
| `scriptVisual` | R script visual |
| `pythonVisual` | Python visual |

### Elements, navigation, embedded content

| Key | Name |
|---|---|
| `textbox` | Text box |
| `shape` | Shape |
| `image` | Image |
| `actionButton` | Button (all button types) |
| `bookmarkNavigator` | Bookmark navigator |
| `pageNavigator` | Page navigator |
| `rdlVisual` | Paginated report visual |
| `scorecard` | Metrics / scorecard (Goals) |

### Canvas pseudo-entries (not visuals, styled the same way)

| Key | Scope | Cards |
|---|---|---|
| `page` | Every report page | `background`, `displayArea`, `outspace` (wallpaper), `outspacePane` (filter pane), `filterCard`, `pageInformation`, `pageRefresh`, `pageSize`, `personalizeVisual` |
| `report` | Whole report | `outspacePane`, `section` |
| `filter` | Filter pane defaults | `general` |
| `group` | Visual group containers | `background`, `general`, `lockAspect` |

### Names that do NOT exist (frequent mistakes)

- `matrix` → use `pivotTable`; `table` → use `tableEx`
- `smartNarrative` → use `aiNarratives`
- `funnelChart` → use `funnel`
- `donut` → `donutChart`; `pie` → `pieChart`
- `waffleChart` — **not a native visual**; it is a custom (AppSource) visual. Custom visuals are
  themed by their registered visual key — the GUID-suffixed name found in
  `publicCustomVisuals`/`visual.json` of the report, e.g.
  `"deneb7E15AEF80B9E4D4F8E12924291ECE89A"`, `"ChicletSlicer1448559807354"`. The schema accepts
  any such key via `additionalProperties`, but property support depends on the custom visual.
- `slicer` covers ONLY the classic slicer; the new button/list/text slicers are separate keys
  (`advancedSlicerVisual`, `listSlicer`, `textSlicer`) — style all four for full coverage.

---

## 6. Worked examples (exact card/property names from schema 2.155)

### 6.1 Global defaults for ALL visuals — `"*"`

```json
"visualStyles": {
  "*": {
    "*": {
      "*": [{ "fontFamily": "Segoe UI", "wordWrap": true }],
      "background": [{ "show": true, "color": { "solid": { "color": "#FFFFFF" } }, "transparency": 0 }],
      "border":     [{ "show": true, "color": { "solid": { "color": "#E6E6E6" } }, "radius": 8 }],
      "title":      [{ "show": true, "fontColor": { "solid": { "color": "#252423" } },
                       "fontSize": 12, "fontFamily": "Segoe UI Semibold", "bold": false }],
      "dropShadow": [{ "show": false }],
      "visualHeader": [{ "showSmartNarrativeButton": false, "showPinButton": false }],
      "filterCard": [
        { "$id": "Applied",   "foregroundColor": { "solid": { "color": "#252423" } } },
        { "$id": "Available", "border": true }
      ]
    }
  }
}
```

### 6.2 Bar chart (`barChart`) — labels, axis, data points

```json
"barChart": {
  "*": {
    "labels": [{ "show": true, "color": { "solid": { "color": "#605E5C" } },
                 "fontSize": 9, "labelDisplayUnits": 0, "labelPrecision": 1,
                 "labelPosition": "OutsideEnd", "enableBackground": false }],
    "categoryAxis": [{ "show": true, "labelColor": { "solid": { "color": "#605E5C" } },
                       "gridlineShow": false, "showAxisTitle": false }],
    "valueAxis": [{ "show": false, "gridlineShow": true,
                    "gridlineColor": { "solid": { "color": "#F3F2F1" } },
                    "gridlineStyle": "dotted" }],
    "dataPoint": [{ "defaultColor": { "solid": { "color": { "expr": {
                    "ThemeDataColor": { "ColorId": 0, "Percent": 0 } } } } } }]
  }
}
```

Other useful `barChart` cards: `legend`, `plotArea`, `totals`, `zoom`, `ribbonBands`,
`smallMultiplesLayout`, `xAxisReferenceLine`, `y1AxisReferenceLine`, `error`, `annotationTemplate`.

### 6.3 Table (`tableEx`) — headers, grid, values

```json
"tableEx": {
  "*": {
    "columnHeaders": [{ "fontColor": { "solid": { "color": "#FFFFFF" } },
                        "backColor": { "solid": { "color": "#063E61" } },
                        "bold": true, "fontSize": 10, "alignment": "Left", "wordWrap": true }],
    "grid": [{ "gridHorizontal": true,
               "gridHorizontalColor": { "solid": { "color": "#F3F2F1" } },
               "gridVertical": false, "rowPadding": 4, "textSize": 9 }],
    "values": [{ "fontColorPrimary": { "solid": { "color": "#252423" } },
                 "backColorPrimary": { "solid": { "color": "#FFFFFF" } },
                 "backColorSecondary": { "solid": { "color": "#FAFAFA" } } }],
    "total": [{ "fontColor": { "solid": { "color": "#252423" } }, "bold": true }]
  }
}
```

Matrix (`pivotTable`) uses the same header/grid/values cards **plus**
`rowHeaders`, `columnTotal`, `rowTotal`, `subTotals`, `blankRows`, `sparklines`.

### 6.4 Classic slicer (`slicer`) — header and items

```json
"slicer": {
  "*": {
    "header": [{ "show": true, "fontColor": { "solid": { "color": "#252423" } },
                 "textSize": 10, "bold": true, "outlineStyle": "BottomOnly" }],
    "items": [{ "fontColor": { "solid": { "color": "#605E5C" } },
                "background": { "solid": { "color": "#FFFFFF" } }, "textSize": 9 }],
    "general": [{ "outlineColor": { "solid": { "color": "#E6E6E6" } },
                  "outlineWeight": 1, "responsive": true }]
  }
}
```

New button slicer (`advancedSlicerVisual`) has a different card set:
`accentBar`, `actionState`, `icon`, `image`, `label`, `layout`, `outline`, `overFlow`,
`selection`, `shapeCustomRectangle`, `value` …

### 6.5 Button (`actionButton`) — state-dependent cards via `$id`

```json
"actionButton": {
  "*": {
    "fill": [
      { "$id": "default",  "show": true, "fillColor": { "solid": { "color": "#063E61" } }, "transparency": 0 },
      { "$id": "hover",    "fillColor": { "solid": { "color": "#0A5580" } } },
      { "$id": "selected", "fillColor": { "solid": { "color": "#042A42" } } },
      { "$id": "disabled", "fillColor": { "solid": { "color": "#F3F2F1" } } }
    ],
    "text": [
      { "$id": "default", "show": true, "fontColor": { "solid": { "color": "#FFFFFF" } },
        "fontSize": 10, "fontFamily": "Segoe UI Semibold" },
      { "$id": "disabled", "fontColor": { "solid": { "color": "#B3B0AD" } } }
    ],
    "outline": [{ "$id": "default", "show": false }],
    "border": [{ "show": false }]
  }
}
```

`shape` supports the same `$id` states on `fill`/`outline`/`text`. `icon` card adds
`shapeType`, `iconSize`, `lineColor`, `placement`.

### 6.6 New card (`cardVisual`) — callout value, label, layout

```json
"cardVisual": {
  "*": {
    "value": [{ "fontSize": 24, "fontFamily": "DIN",
                "fontColor": { "solid": { "color": "#063E61" } },
                "labelDisplayUnits": 0, "labelPrecision": 1 }],
    "label": [{ "show": true, "fontSize": 9,
                "fontColor": { "solid": { "color": "#605E5C" } }, "position": "Above" }],
    "layout": [{ "orientation": "Horizontal", "rectangleRoundedCurve": 8,
                 "backgroundShow": true,
                 "backgroundFillColor": { "solid": { "color": "#FFFFFF" } } }]
  }
}
```

`cardVisual` is the richest visual in the schema (44 cards) — also `referenceLabel`,
`referenceLabelTitle/Value/Detail/Layout`, `accentBar`, `smallMultiples*` family.

### 6.7 Page canvas (`page`)

```json
"page": {
  "*": {
    "background": [{ "color": { "solid": { "color": "#FFFFFF" } }, "transparency": 0 }],
    "outspace":   [{ "color": { "solid": { "color": "#F5F5F5" } }, "transparency": 0 }]
  }
}
```

`page`/`report`/`filter`/`group` accept only the `"*"` style level (no named presets).

---

## 7. Known pitfalls (граблі)

1. **Case-sensitive names everywhere.** Visual keys, card names, and property names are exact
   camelCase strings: `hundredPercentStackedBarChart`, `lineClusteredColumnComboChart`,
   `tableEx`. A wrong-case key never matches.
2. **A typo in a visual-type key fails silently.** `visualStyles` accepts arbitrary keys (to
   support custom visuals and `"*"`), so `"pieChar"` or `"matrix"` imports fine and does
   nothing. Top-level typos, by contrast, hard-fail import (`additionalProperties: false`).
   Always copy keys from §5.
3. **Card values must be arrays.** `"title": { "show": true }` is invalid;
   it must be `"title": [{ "show": true }]`. This is the most common hand-authoring error.
4. **Stacked vs clustered trap.** `barChart`/`columnChart` are the *stacked* variants.
   Theming `columnChart` does nothing for clustered columns — style `clusteredColumnChart`
   and `hundredPercentStackedColumnChart` too (usually all with identical content).
5. **Specific beats `"*"` — per entry, not per property merge order.**
   Precedence (lowest → highest):
   base theme → custom theme `"*"."*"` → `visualStyles.<type>."*"` → selected named style
   preset → explicit per-visual formatting (`objects` in visual JSON). More specific entries
   override the wildcard for the same property; properties not set anywhere fall back down the
   chain. A theme sets **defaults only**: visuals already explicitly formatted keep their
   formatting until "Reset to default" (which reverts to custom theme, then base theme).
6. **The `"*"` cardName is property-name-based.** It sets a property in *every* card of the
   visual where that name exists. Fine for `fontFamily`; dangerous for generic names like
   `show`, `fontSize`, `transparency` — you may toggle cards you didn't intend.
7. **Two different color syntaxes.** Top level + `textClasses` = plain hex string
   (`"color": "#252423"`); inside `visualStyles` cards = fill object
   (`{"solid": {"color": …}}`) where color can be hex, a **named theme color** string, or a
   `ThemeDataColor` expression (`ColorId` 0-based into palette, `Percent` −1…1 shade).
   Mixing syntaxes fails validation.
8. **`fontFace` vs `fontFamily`.** Text classes use `fontFace`; visualStyles cards use
   `fontFamily`. Weights are baked into family names ("Segoe UI Semibold", "Segoe UI Light");
   `fontSize` is points and schema-limited to 6–45 in textClasses.
9. **`$id` variants have fixed enums.** filterCard: `Available`/`Applied`; button/shape state
   cards: `default`/`hover`/`selected`/`disabled` (there is no `press` state). Array elements
   without `$id` target the default variant.
10. **Named style presets don't auto-apply.** Only `"*"` applies to all visuals of the type;
    a named preset must be chosen in the Format pane (or pre-selected via
    `"stylePreset": [{"name": "..."}]` in `"*"`). Presets inherit from `"*"` of the same visual,
    so put shared settings in `"*"` only.
11. **Conditional-formatting rules cannot be themed.** The theme can set gradient endpoint
    colors (`maximum`/`center`/`minimum`/`null`) and default colors, but not CF rules
    themselves.
12. **Schema is versioned per Desktop release.** New visuals/cards appear in newer schema files
    (e.g. `textSlicer` cards evolved through 2.14x). Pin `$schema` to a downloaded local copy
    for IDE autocomplete; validate against the version matching the user's Desktop.
    Visual-type keys are stable across 2.143–2.155.
13. **Legacy alias collision.** `foreground`≡`firstLevelElements` etc. are separate keys that
    write the same slots; don't specify both variants with different values in one theme.
14. **Classic vs new visual pairs.** `card`≠`cardVisual`, `slicer`≠`advancedSlicerVisual`/
    `listSlicer`/`textSlicer`. A theme meant to restyle "cards" must usually cover both keys.

---

## 8. Where the theme lives in a PBIP report

- **PBIR-Legacy** (single `report.json`): the `config` field (a JSON **string** — parse before
  editing) contains:

  ```json
  "themeCollection": {
    "baseTheme":   { "name": "CY24SU10", "type": 2, "version": { ... } },
    "customTheme": { "name": "Custom013246378101423373.json", "type": 1, "version": { ... } }
  }
  ```

  `type: 1` = RegisteredResources → the theme JSON file sits at
  `<Report>.Report/StaticResources/RegisteredResources/<name>.json`.
  `type: 2` = SharedResources (built-in base themes like `CY24SU10`, managed by Microsoft).
- **PBIR enhanced**: `definition/report.json` has the same `themeCollection` concept with
  string resource types; theme files under `StaticResources/RegisteredResources/`.
- Mechanics of editing report.json safely → see `powerbi-visuals` skill; theme JSON editing
  best practice → keep one theme file, byte-faithful edits, validate JSON before commit.

---

## 9. Quick checklist for generating a theme

1. `name` — required; keep stable across edits.
2. `dataColors` — 8–12 colors, brand-first; check contrast on `background`.
3. Sentiment + divergent: `good`/`neutral`/`bad`, `maximum`/`center`/`minimum`/`null`.
4. Six structural classes (`firstLevelElements` … `secondaryBackground`) + `tableAccent`,
   `hyperlink`, `visitedHyperlink`.
5. `textClasses`: 4 primary classes; secondary only to break inheritance.
6. `visualStyles."*"."*"` — global card defaults (background, border/radius, title, shadow,
   visualHeader).
7. Per-type overrides — remember stacked/clustered/100% triplets and classic/new pairs.
8. Validate: JSON parses; keys match §5; every card value is an array; colors use the right
   syntax for their location.
