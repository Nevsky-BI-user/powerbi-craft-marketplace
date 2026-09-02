# Navigation & Tab Bar — Reference

Companion to `SKILL.md`. Card/property names verified against the report theme schema
(`reportThemeSchema` — the `$schema` of a theme file) and an audit of a real `report.json` nav group;
navigator JSON (§6) verified in public PBIR repositories.
Tokens (`color/*`, `type/*`) resolve in `pbi-design-system`.

## 1. Full theme block — all four states

`actionButton` cards are `fill`, `text`, `outline`, `border` (theme schema). `shape`
supports the same `$id` states on `fill`/`outline`/`text`. `icon` card (on `shape`/button-icon
visuals) adds `shapeType`, `iconSize`, `lineColor`, `placement` — verify `$id` support on that
card against a real file or the theme schema before relying on it (don't assume from memory, F2).

```json
"actionButton": {
  "*": {
    "fill": [
      { "$id": "default",  "show": false },
      { "$id": "hover",    "show": true, "fillColor": { "solid": { "color": "#E6ECEF" } }, "transparency": 0 },
      { "$id": "selected", "show": true, "fillColor": { "solid": { "color": "#063E61" } }, "transparency": 0 },
      { "$id": "disabled", "show": false }
    ],
    "text": [
      { "$id": "default",  "show": true, "fontColor": { "solid": { "color": "#605E5C" } }, "fontSize": 10, "fontFamily": "Segoe UI" },
      { "$id": "hover",    "fontColor": { "solid": { "color": "#333333" } } },
      { "$id": "selected", "fontColor": { "solid": { "color": "#FFFFFF" } }, "fontFamily": "Segoe UI Semibold" },
      { "$id": "disabled", "fontColor": { "solid": { "color": "#9E9F9F" } } }
    ],
    "border": [{ "show": false }]
  }
}
```

Card values are ARRAYS. Row-by-row mapping to tokens (`pbi-design-system` §5): default = transparent
fill + `color/text-secondary` text; hover = `color/hover-tint` fill + `color/text-body` text;
selected = `color/brand` fill + `color/text-inverse` text + Semibold; disabled = transparent fill
+ `color/text-disabled` text. Microsoft lists **five** button states (Default, On hover, On press,
Disabled, Loading — https://learn.microsoft.com/power-bi/create-reports/desktop-buttons#button-states);
the theme `$id` enum carries four, and "On press" (`color/pressed-tint` `#CDD8DF`) is set only on the
individual button instance — its selector id is not yet observed in a file, read it from a Desktop diff.

## 2. Icons

- `icon-set-manager` PNGs (brand navy) for nav icons. PNGs do **not** recolor per state — provide
  navy + white variants, or use a native icon shape via the `icon` card.
- Icon-only button: 32 × 32 px minimum; alt text is mandatory (no visible label to fall back on).

## 3. Left-rail variant

When tabs exceed roughly six, switch from a horizontal strip to a left rail: 200 px wide,
full page height, one button per row (same states as the horizontal strip).

## 4. Breadcrumb

- Typography: `type/small`, `color/text-secondary`.
- Parents render as clickable page/bookmark-nav buttons; separate each with a "›" separator glyph.
- Current level: plain text in `color/text-body`, NOT clickable (it's "you are here", not a link).
- Do not fake a breadcrumb as one textbox with tab-character spacing — that's antipattern A10
  (seen in an audited report); it isn't clickable and drifts under font-size changes.
  Use separate button/text visuals per crumb.

## 5. Legacy report compatibility (existing 1440-wide report only)

Keep the report's established nav footprint instead of inventing new coordinates
(audited report, navigation bar):

| Parameter | Value |
|---|---|
| Nav group | ≈ 590 × 38 px at x≈104, y≈3–4 — identical on every page (top strip) |
| Nav buttons | ≈ 197–223 × 31–38 px, 10 pt label |
| Canvas | 1440 × 675 (dashboards) / 1440 × 720 (drill-through) — `pbi-design-system` §7 |
| Brand navy | theme `ColorId 2` (`#003A5D`) via `ThemeDataColor` — this report's own navy, not the icon-library `#063E61` |

Everything else (typography, states, a11y) follows the canonical tokens in `pbi-design-system`.

## 6. Navigator visuals in PBIR — `pageNavigator` and `bookmarkNavigator` (GT)

Both are inserted from Desktop (Insert → Buttons → Navigator) and **sync themselves**: the page
navigator takes labels from page display names, order from page order, the selected tile from the
current page, and follows renames/additions; the bookmark navigator does the same for a bookmark
group. Docs: https://learn.microsoft.com/power-bi/create-reports/button-navigators

```jsonc
// pageNavigator — public PBIR repo; layout.orientation carries NO selector
{ "$schema": ".../visualContainer/2.10.0/schema.json",
  "name": "nav_lateral",
  "position": { "x": 30, "y": 132, "z": 9000, "height": 330, "width": 145, "tabOrder": 7000 },
  "visual": {
    "visualType": "pageNavigator",
    "objects": { "layout": [ { "properties": { "orientation": {"expr":{"Literal":{"Value":"1D"}}} } } ] },
    "drillFilterOtherVisuals": true },
  "howCreated": "InsertVisualButton" }
// orientation 1D = vertical rail; omit for the default horizontal strip. An `objects.pages` card
// (show hidden pages / tooltip pages) is observed in a second repo — copy it from Desktop output.
```

```jsonc
// bookmarkNavigator — public PBIR repo; bound to a bookmark GROUP, selected state via selector "selected"
"visual": { "visualType": "bookmarkNavigator",
  "objects": {
    "bookmarks": [ { "properties": {
        "bookmarkGroup":    {"expr":{"Literal":{"Value":"'Bookmark8c06930e6985477eb587'"}}},
        "selectedBookmark": {"expr":{"Literal":{"Value":"'Bookmarka41b7586573ce49ab49d'"}}} } } ],
    "fill":    [ { "properties": { "show": {"expr":{"Literal":{"Value":"false"}}} } } ],
    "outline": [ { "properties": { "show": {"expr":{"Literal":{"Value":"false"}}} } } ],
    "text":    [ { "properties": {
        "fontColor": {"solid":{"color":{"expr":{"ThemeDataColor":{"ColorId":1,"Percent":0}}}}} },
      "selector": {"id":"selected"} } ] },
  "drillFilterOtherVisuals": true }
```

Format cards beyond ordinary buttons: **Grid layout** (horizontal / vertical / grid + padding),
**Selected state**, **Pages** (show hidden / tooltip pages) for the page navigator, **Bookmarks**
(all or one group, *Allow deselection*, *Launch on deselection* → target bookmark, *Hide deselection
bookmark*) for the bookmark navigator. Theme keys are the same strings: `visualStyles.pageNavigator`,
`visualStyles.bookmarkNavigator` (validate against the theme schema).

Limitations (docs): only **one active bookmark per report** — two navigators over groups that control
overlapping settings show a misleading active tile; the bookmark navigator's selected state **is not
reflected in exports** (PDF/PPTX); custom PNG icons cannot be placed on navigator tiles (use an
`actionButton` row → `pbi-buttons-actions` when icons are required). Selector ids on navigators are
exactly `default` / `hover` / `selected` — `interaction:*` or `selection:*` silently kills all tiles.

Repos: https://github.com/dalvadev/hakuwinay · https://github.com/Rede-DSBR/DocPBI2 ·
https://github.com/tomatminceddata/PBIR_XRAY
