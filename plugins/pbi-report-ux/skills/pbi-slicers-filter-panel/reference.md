# Slicers & Filter Panel — Reference

## §1. Four slicer theme keys — coverage

| Theme key | Visual | Known formatting cards |
|---|---|---|
| `slicer` | Classic (list/dropdown/date/numeric) | `header`, `items`, `general` (see §3 for exact properties) |
| `advancedSlicerVisual` | Button slicer ("new slicer") | `accentBar`, `actionState`, `icon`, `image`, `label`, `layout`, `outline`, `overFlow`, `selection`, `shapeCustomRectangle`, `value` |
| `listSlicer` | List slicer (new) | Not enumerated in our research corpus — read the `reportThemeSchema` or a ground-truth `visual.json`/theme file before writing properties. Never guess. |
| `textSlicer` | Text slicer | Same caveat as `listSlicer` — verify against schema/ground truth. |

A theme meant to "restyle slicers" must cover all four keys, or three of four visuals silently keep the default style. `slicer` and `advancedSlicerVisual` are the two most common in practice; when the report uses `listSlicer`/`textSlicer`, clone the property list from an existing styled instance of that exact visual rather than inventing card names.

### §1a. Hand-authoring a button/tile slicer — use classic `slicer`, NOT `advancedSlicerVisual`

Verified empirically (Desktop 2.155): a hand-authored `advancedSlicerVisual` renders **empty tiles** — `fillCustom`/`value`/`layout` set correctly per capabilities, yet the field values never display. This is a rendering failure of the new visual under hand-authored PBIR, independent of theming. The reliable canon (ground truth: an audited production report ships `slicer` with `data.mode`) is the **classic `slicer`** in `HorizontalList` mode, which gives the same chip/button look and renders on the first load.

- **Visual JSON** (clone a ground-truth classic slicer of that mode): set `data.mode: 'HorizontalList'` for buttons; `'Dropdown'` for a compact picker; `'Between'` for date/numeric. Single-select buttons: `selection.singleSelect: true`.
- **Dark theme is mandatory per mode** — an unstyled classic slicer is dark-text-on-white, i.e. white-on-white on a dark canvas. Style each mode's card:
  - List/HorizontalList/Dropdown → `items`: `fontColor` + `background`.
  - Date/numeric (Between) → `date` and `numericInputStyle`: `fontColor` + `background`.
  - `header`: `show` + `fontColor` (hide it, or color it, but never leave default white).

```json
"slicer": { "*": {
  "header":            [{ "show": true, "fontColor": { "solid": { "color": "#cbd5e1" } } }],
  "items":             [{ "fontColor": { "solid": { "color": "#e2e8f0" } },
                          "background": { "solid": { "color": "#1e293b" } } }],
  "date":              [{ "fontColor": { "solid": { "color": "#e2e8f0" } },
                          "background": { "solid": { "color": "#1e293b" } } }],
  "numericInputStyle": [{ "fontColor": { "solid": { "color": "#e2e8f0" } },
                          "background": { "solid": { "color": "#1e293b" } } }],
  "selection":         [{ "singleSelect": true }]
} }
```

## §2. Filter panel — worked layout (200 px rail)

Coordinates assume a 1280×720 canvas rail anchored top-right or left (adjust `x` to canvas width for right-anchored):

```
y=0,   height=full page
w=200
├─ 0–16      margin
├─ 16–48     "Filters" header row (type/header) + 32×32 close button, right-aligned
├─ 48–64     16 px gap
├─ 64…       slicers stacked, 168 px wide, 16 px vertical gaps between
└─ …–bottom  clear-all button (actionButton, ghost style), 16 px above bottom margin
```

Chrome: `color/surface` fill, 1 px `color/border` inner edge, **no radius** (it is a full-bleed rail, not a floating card), `z` above data visuals so it doesn't get occluded when toggled on. Toggle control: a filter-icon button (`icon-set-manager`) top-right of the canvas, ≥32×32, with alt text and — when closed — the applied-filter badge (§ below) on or beside it.

**Mechanics** (author via `powerbi-bookmarks`, not here): one visual **group** containing the rail's slicers + header + close button; two bookmarks — "Filters open" and "Filters closed" — each toggling that group's visibility; data capture **OFF** on both (bookmarks must not also snapshot filter state); the bookmark pair's `options.targetVisualNames` scoped to exactly the toggle button + the group, never left at report-wide default (that resets/reapplies every other visual's state on toggle).

## §3. Theme JSON — classic slicer + filter-pane cards

Verified against the theme-schema introspection notes §6.4 and the `filterCard` example (schema 2.155). Hexes shown resolve to `color/brand` / `color/text-body` / `color/border` — use the report's own theme file, not literal hex, when editing an existing theme (tokens §1.7).

```json
"visualStyles": {
  "slicer": { "*": {
    "header":  [{ "show": true, "fontColor": { "solid": { "color": "#063E61" } },
                  "textSize": 10, "bold": true, "outlineStyle": "BottomOnly" }],
    "items":   [{ "fontColor": { "solid": { "color": "#333333" } },
                  "background": { "solid": { "color": "#FFFFFF" } }, "textSize": 10 }],
    "general": [{ "outlineColor": { "solid": { "color": "#E6E6E6" } },
                  "outlineWeight": 1, "responsive": true }]
  } },
  "*": { "*": {
    "filterCard": [
      { "$id": "Applied",   "foregroundColor": { "solid": { "color": "#063E61" } } },
      { "$id": "Available", "border": true }
    ]
  } }
}
```

`filterCard` is a **page-level** card (nested under `"*": {"*": {...}}}`, i.e. every visual type / every page — it drives the built-in Filters pane, not a specific visual). `$id` is a fixed two-value enum: `Applied` | `Available` — no others exist.

## §4. Sizes & tokens (`pbi-design-system` §3.2/§5)

Dropdown slicer 192×48 w/ header, 192×32 headerless; grid gutter 16; filter left rail 200 px wide; slicer width inside rail = 200 − 2×16 margin = 168; hit target ≥ 24 px (standard 32). Header text 10 pt bold `color/brand` (as shipped in master-theme `slicer.header`); item text `type/small` 9 pt / `color/text-secondary` (master-theme `slicer.items`: textSize 9, #605E5C). Selected state = `color/selection-tint` fill **plus** bold or a check mark — never color alone (colorblind-safe). Hover = `color/hover-tint`. One radius (`shape/radius` 8 px) across all slicers on a page; no shadow.

**Between/relative-date/numeric-range height:** a `Between`-mode slicer draws two input boxes plus a slider track, not one control. Calibrated by render bisection on this project: at 280×64 it collapsed to the label plus a bare funnel glyph (no inputs, no track); at 280×96 the inputs rendered but the slider track was **silently dropped**; at 280×120 everything rendered; at 280×144 there was visible dead space below the track. Budget **120 px** — roughly a dropdown's 64 (24 header + 32 control + 8 slack) plus a track row. The failure ladder is the important part, and it is silent at every rung: master-theme `slicer.general.responsive` is `true` (§3), and a responsive slicer that does not fit its container does not clip or scroll — it sheds its parts, largest first. On screen that reads as broken/unbound and invites a data-binding investigation that won't find anything. Read it correctly instead: **a funnel glyph (or a missing track) where a control should be means the container is too small, not that the slicer is broken.** Give it height, or set `responsive: false` on that instance for an honest clip.