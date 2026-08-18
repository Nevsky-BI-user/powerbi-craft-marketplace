# Page Headers, Icons & Imagery — Reference

Companion to `SKILL.md`. Names verified against `docs/research/theme-visuals.md`
(reportThemeSchema 2.143 = 2.155) or a real report file — never recalled from memory.
Tokens (`color/*`, `type/*`) resolve in `docs/DESIGN-TOKENS.md`.

## 1. Visual-type keys involved

| Key | Element | Notes |
|---|---|---|
| `textbox` | Title, context line, filter-status text | Beyond the 16 common cards (§2), schema adds `text` (`color`/`fontFamily`/`fontSize`) and `values` cards |
| `shape` | Divider line, header band | Cards `fill`/`outline`/`text` are single-element arrays — **no `$id` states** (schema 2.155); the `$id`-stated `icon` card belongs to `actionButton`, not `shape` (§3) |
| `image` | Logo/brand mark, background/watermark | Theme-settable too: `image` card (`sourceType`/`sourceUrl`/`fit`) and `imageScaling` card (`imageScalingType`: Normal→"Fit"/Fit→"Stretch"/Fill) exist in `visualStyles.image`; per-visual `objects` override per instance — verify the exact property against ground truth before writing (BRIEF F2) |

Pseudo-entries (page-level, not visuals): `page` scope carries `pageInformation`,
`pageRefresh`, `filterCard`, `outspace` (wallpaper), `displayArea`. Property names inside
`pageInformation`/`pageRefresh` are not verified in this repo's research corpus — read them
from the schema file or Format pane → Page background/Page information before emitting.

## 2. Common 16 cards (every regular visual, incl. `textbox`/`shape`/`image`)

```
*, background, border, divider, dropShadow, general, lockAspect, padding,
spacing, stylePreset, subTitle, title, visualHeader, visualHeaderTooltip,
visualLink, visualTooltip
```

Verified property names:

| Card | Properties |
|---|---|
| `background` | `color` (fill obj), `show`, `transparency` |
| `border` | `color` (fill obj), `radius`, `show`, `width` |
| `divider` | draws a rule at an edge of the visual — use for a title textbox's bottom rule instead of stacking a separate `shape`; exact property names (side/color/width) — read from schema/ground truth before use |
| `title` | `alignment`, `background`, `bold`, `fontColor`, `fontFamily`, `fontSize`, `heading`, `italic`, `show`, `text`, `titleWrap`, `underline` |
| `dropShadow` | `angle`, `color`, `position`, `preset`, `shadowBlur`, `shadowDistance`, `shadowSpread`, `show`, `transparency` — keep `show: false` (flat design, DESIGN-TOKENS §4) |
| `visualHeader` | `show`, `background`, `border`, `foreground`, `show*Button…` — hide on title/logo/stamp elements (`visualHeader.show: false`) |
| `padding` | `top`, `bottom`, `left`, `right` |

## 3. `shape` styling and icon-in-button

`shape` cards take NO `$id` (schema 2.155 — single-element arrays); the `$id`-stated `icon`
card is `actionButton`'s:

```json
"shape": {
  "*": {
    "fill":    [{ "show": true, "fillColor": { "solid": { "color": "#E6E6E6" } } }],
    "outline": [{ "show": false }]
  }
},
"actionButton": {
  "*": {
    "icon": [{ "$id": "default", "shapeType": "circle", "iconSize": 16,
               "lineColor": { "solid": { "color": "#063E61" } },
               "placement": "center" }]
  }
}
```

`icon` card properties (`shapeType`, `iconSize`, `lineColor`, `placement`) are schema-verified
names **on `actionButton`**; exact enum values for `shapeType`/`placement` — confirm against a
ground-truth visual or the schema file before emitting a value outside the obvious set.

## 4. `filterCard` — Applied vs Available (for a filter-status cue tied to the built-in pane)

```json
"*": { "*": {
  "filterCard": [
    { "$id": "Applied",   "foregroundColor": { "solid": { "color": "#063E61" } } },
    { "$id": "Available", "border": true }
  ]
} }
```

This styles Power BI's own filter-pane chips; it is a styling hook, not a text badge — the
"3 filters applied" text cue in the header itself is a DAX measure (§6), and its clear-all /
show-hide mechanics belong to `pbi-slicers-filter-panel`.

## 5. Worked header group (theme defaults for the three elements)

```json
"visualStyles": {
  "textbox": { "*": {
    "*":       [{ "fontFamily": "Segoe UI" }],
    "divider": [{ "show": false }]
  } },
  "shape": { "*": {
    "dropShadow": [{ "show": false }],
    "fill": [{ "$id": "default", "fillColor": { "solid": { "color": "#E6E6E6" } } }]
  } },
  "image": { "*": {
    "border":     [{ "show": false }],
    "dropShadow": [{ "show": false }]
  } }
}
```

Per-instance placement (not theme — report.json/visual.json layout, mechanics via
`powerbi-visuals`): header row `x:24, y:24, width:1232, height:40`; logo `x:24, y:28,
width:32, height:32`; title textbox `x:64, y:24, width:700, height:40`; refresh/filter-status
textbox `x:936, y:24, width:320, height:40` (right-aligned text — end aligns with header row's
right edge at x=1256, symmetric to logo's flush-left at x=24).

## 6. DAX snippets (author via `dax-measures`; shown here only to size the header slot)

```dax
Last Refreshed =
"Дані станом на " & FORMAT ( MAX ( RefreshLog[RefreshDateTime] ), "DD.MM.YYYY HH:MM" )

Filter Status =
VAR _n = COUNTROWS ( FILTERS ( DimDate[Year] ) ) -- repeat/UNION per slicer field in scope
RETURN
    IF ( _n = 0, "Без фільтрів", _n & " фільтр(ів) застосовано" )
```

Bind either measure to a `textbox`/`cardVisual` with `visualHeader.show: false` in the
right-hand header zone. Full badge/clear-all pattern (multi-slicer count, toggle button) →
`pbi-slicers-filter-panel`.

## 7. Icon categories relevant to headers (via `icon-set-manager`)

`navigation` (home, back, forward, menu, search, filter, breadcrumb, sidebar),
`actions` (refresh), `status` (ok, warning, error, info, pending). Default 64 px, brand
`#063E61`; request 128 px only for a cover/start-page hero lockup, never for the 32–40 px
row logo (downscale a larger PNG instead of upscaling a smaller one).

## 8. Text-over-image contrast

Any text/logo placed on a photo or gradient background must still clear the ratios in
`pbi-color-accessibility` (≥4.5:1 body, ≥3:1 large/18pt). Two safe patterns: (a) a solid or
gradient scrim `shape` between the image and the text (e.g. `#000000` @ 40–60%
transparency), or (b) place text only over a photographically flat region of the image and
verify the sampled color, not an assumption.

## 9. Image rendering: register the PNG, never an external URL

Power BI Desktop does **not** fetch a remote URL in an `image` visual — an
`imageUrl` pointing at `https://cdn…/logo.png` (or any CDN/raw GitHub link) renders a **blank
placeholder**. The logo/icon PNG must be *registered inside the report*. The mechanics below
are executed by `powerbi-visuals` (report JSON) and `icon-set-manager` (PNG fetch/recolor);
this skill's job is to hand them the correct target, not an external link.

Canonical chain (ground truth: PDP report saved by Desktop):

1. **File** — PNG at `<Report>.Report/StaticResources/RegisteredResources/<name>.png`.
2. **Package entry** — an item of type `Image` in `report.json` `resourcePackages`
   (name matches the `ItemName` used below).
3. **Per-visual reference** — the `image` visual's `imageUrl` is a `ResourcePackageItem`
   expression, not a string URL:

```json
"imageUrl": { "expr": { "ResourcePackageItem": {
  "PackageName": "RegisteredResources",
  "PackageType": 1,
  "ItemName": "logo.png"
} } }
```

**Recolor for theme.** A dark brand PNG (e.g. `#063E61`) on a dark page is near-invisible —
repaint it to a light token (e.g. `#cbd5e1`) before registering, then verify contrast (§8):

```
magick in.png -channel RGB +level-colors "#cbd5e1","#cbd5e1" +channel out.png
```

**Shape `objects` are two-entry (per-instance).** In a header divider/band `shape`'s
visual.json `objects`, the rule is two-sided: show-toggles (`fill.show`, `outline.show`,
`text.show`) are a **bare** entry with NO selector, while value props (`fillColor`,
`lineColor`, `weight`, `transparency`, `fontColor`) go in a **separate** entry carrying
`"selector": { "id": "default" }`. Put a selector on a toggle, or omit it on a value, and
Desktop ignores the whole config (visual reverts to the default purple). This is the
report-JSON per-instance layer (distinct from theme `$id` states in §3). Valid
hand-authored `tileShape` values from ground truth: `rectangle`, `rectangleRounded` (with an
integer `rectangleRoundedCurve`), `line`, `tabRoundTopCorners` — `rectangleRoundedByPixel`
(and `roundEdge`) are not Desktop-emitted and are ignored.
