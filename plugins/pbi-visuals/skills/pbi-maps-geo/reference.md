# Maps & Geo — Reference

Companion to `SKILL.md`. Card and property names verified against
`reportThemeSchema-2.155.json` (`visual-map`, `visual-filledMap`,
`visual-shapeMap`, `visual-azureMap` definitions) — never recalled from memory.
Tokens (`color/*`, `ramp/*`) resolve in `pbi-design-system`.

## 1. Visual-type keys & cards (theme `visualStyles`)

| Key | Cards (verified) |
|---|---|
| `map` | `general`, `dataPoint`, `bubbles`, `categoryLabels`, `legend`, `mapControls`, `mapStyles`, `heatMap` |
| `filledMap` | `general`, `dataPoint`, `stroke`, `categoryLabels`, `legend`, `mapControls`, `mapStyles`, `labels` |
| `shapeMap` | `general`, `shape`, `defaultColors`, `dataPoint`, `legend`, `zoom` |
| `azureMap` | `general`, `commonDataOptions`, `dataPoint`, `bubbleLayer`, `heatMapLayer`, `barChart`, `pathLayer`, `referenceLayer`, `tileLayer`, `traffic`, `filledMap`, `categoryLabels`, `labels`, `legend`, `mapControls` |

**Currency note (MS Learn, verified 2026-07-10).** `map` and `filledMap` are the **Bing Maps
visuals, scheduled for deprecation** (timeline TBD; existing reports keep working; Bing Maps
platform itself retires June 2028). Microsoft's guidance: upgrade NEW work to `azureMap` unless
users are in China/Korea/government clouds (Azure Maps unsupported there); a one-click
conversion exists in Desktop. `shapeMap` (TopoJSON) does not depend on Bing geocoding and is
unaffected, but remains officially "(preview)". Sources:
`learn.microsoft.com/power-bi/visuals/power-bi-visualization-filled-maps-choropleths`,
`learn.microsoft.com/azure/azure-maps/power-bi-visual-conversion`.

## 2. Card properties (schema-verified)

### `map`
- `bubbles`: `bubbleSize` (integer), `markerRangeType` (`magnitude` \| `dataRange` \| `auto`)
- `dataPoint`: `defaultColor`/`fill` (fill object), `fillRule` (gradient, §3), `showAllDataPoints` (bool), `transparency` (number)
- `mapStyles`: `mapTheme` (`aerial` \| `canvasDark` \| `canvasLight` \| `grayscale` \| `road`), `showLabels` (bool)

### `filledMap`
- `dataPoint`: same shape as `map` — `fillRule` drives the choropleth scale
- `stroke`: `show` (bool), `strokeColor` (fill object), `strokeWidth` (number)
- `categoryLabels`: `show` (bool)
- `mapStyles`: same as `map`

### `shapeMap`
- `shape`: `datasourceType` (`url` \| `file_upload`), `mapUrl` (string), `projectionEnum` (`albersUsa` \| `equirectangular` \| `mercator` \| `orthographic`)
- `defaultColors`: `borderColor`, `borderThickness`, `defaultColor` (fill for shapes with no data), `defaultShow` (bool — show shapes even without data)
- `dataPoint`: same `fillRule` shape as above (no `transparency` field)

### `azureMap`
- Requires an **Azure Maps account key** — an external Azure resource, not a report/model setting. Confirm the user has one before building; if not, prefer `filledMap`/`shapeMap`.
- Layers are separate cards (`bubbleLayer`, `heatMapLayer`, `pathLayer`, `referenceLayer`, `tileLayer`) — style each independently; unset layers fall back to `dataPoint`/`general` defaults.

Any property not listed here: read it from `reportThemeSchema-2.1xx.json` or copy from a ground-truth visual in the target report — do not guess. Card values are always **arrays** of objects.

## 3. `fillRule` — the choropleth/bubble color-scale shape

Schema `oneOf`: `linearGradient2` (2-stop) or `linearGradient3` (3-stop). Each stop is
`{ "color": <colorOrThemeColor>, "value": <number> }`.

```json
"fillRule": [{
  "linearGradient2": {
    "min": { "color": "#E6ECEF", "value": 0 },
    "max": { "color": "#063E61", "value": 100000 }
  }
}]
```

- **Sequential** (magnitude — e.g. revenue by region): `linearGradient2`, min/max only.
  Endpoints from `ramp/brand-seq` (`pbi-design-system` §1.2); dark = more, never rainbow.
- **Diverging** (deviation around a meaningful zero/target — e.g. YoY %, plan vs actual):
  `linearGradient3` (`min`/`mid`/`max`). `mid.value` is pinned at the meaningful center
  (0, or 100% of plan) — **never the data mean** (`pbi-design-system` §1.3). Endpoints from
  `ramp/diverging`.
- `nullColoringStrategy` (either variant): `{ "strategy": <string>, "color": <colorOrThemeColor> }`
  controls how blank values render. Always set an explicit `color` (e.g. `color/border`)
  — default gray-on-gray reads as "zero", not "no data".

## 4. Ukraine / oblast decision path

1. **Lat/Long first.** Add two numeric columns to the TMDL model (data category
   `Latitude`/`Longitude` — property lives in TMDL, see `tmdl`/`semantic-model` skills).
   Bypasses geocoding entirely; most reliable path for `map`.
2. **Named-region maps (`filledMap`) with Bing geocoding.** Known failure modes for
   Ukraine: stale admin-2 boundary data, oblast names colliding with city names,
   occupied-territory naming drift. Errors are **silent** — a mis-plotted or missing
   shape, no thrown error. Mitigate: disambiguate the text value as
   `"<Oblast name>, Ukraine"`, set data category `State or Province`, and spot-check a
   handful of oblasts actually render in the right place before shipping.
3. **`shapeMap` — recommended default for Ukraine oblast dashboards.** Fully bypasses
   Bing: supply your own TopoJSON (`shape.datasourceType: "url"`, `shape.mapUrl`) with the
   24 oblasts + Kyiv city + Crimea as separate features, keyed by a stable code (e.g.
   ISO 3166-2:UA, `UA-05`…`UA-77`) matching a column in the model. Source the TopoJSON
   from a maintained public dataset — **verify the feature-key property name against a
   raw fetch** before wiring `dataPoint.fillRule`; never assume the key name.
4. **`azureMap`** only when the task genuinely needs routing/traffic/live layers over
   Ukraine geography — otherwise it adds an external Azure dependency for no benefit over
   `shapeMap`.

## 5. Table-vs-map decision test

Ask: does the reader need to find **WHERE**, or compare **HOW MUCH**? A map wins only for
the first question.

- Regions ≥ 15 AND ranking matters → sorted bar chart or `tableEx`
  (`pbi-bar-column-charts`/`pbi-tables`) wins; area+hue is the weakest accurate encoding
  for magnitude (Cleveland–McGill: position > length > slope > angle > area > color).
- Regions vary a lot in physical size but not in value (e.g. small Zakarpattia oblast with
  2× the value of large Odesa oblast) → choropleth visually understates the smaller
  region; pair with a ranked table, or use `map` bubbles (size ≠ shape area) instead.
- Spatial adjacency, clustering, logistics routes, or "near the front line" IS the
  question → map is justified; still add a compact ranked table alongside for exact
  lookups (F9 — never color-only).

## 6. Worked example

```
Question: revenue by oblast, this year vs last year (deviation)
Shape:    24 categories (oblast) x 1 measure (YoY % delta)
Choice:   shapeMap (Bing named-region geocoding unreliable for oblasts);
          own Ukraine-oblast TopoJSON, keyed by ISO 3166-2:UA;
          dataPoint.fillRule = linearGradient3, mid pinned at 0% (not the data mean);
          defaultColors for oblasts with no data this period (borderColor = color/border);
          legend on; each oblast's exact % also shown in a tooltip page (pbi-tooltips)
Rejected: filledMap (Bing oblast geocoding drift -- silent mis-plots);
          bar chart alone (adjacency across regions matters for this report)
Route:    JSON -> powerbi-visuals; TopoJSON hosting -> user provides/verifies;
          tokens -> `pbi-design-system` §1.2/1.3
```
