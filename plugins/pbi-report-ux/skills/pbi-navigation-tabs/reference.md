# Navigation & Tab Bar — Reference

Companion to `SKILL.md`. Card/property names verified against `docs/research/theme-visuals.md`
(schema §5–6) and `docs/research/pdp-design-audit.md` (real PDP `report.json` nav group).
Tokens (`color/*`, `type/*`) resolve in `docs/DESIGN-TOKENS.md`.

## 1. Full theme block — all four states

`actionButton` cards are `fill`, `text`, `outline`, `border` (theme-visuals §6.5). `shape`
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

Card values are ARRAYS. Row-by-row mapping to tokens (DESIGN-TOKENS.md §5): default = transparent
fill + `color/text-secondary` text; hover = `color/hover-tint` fill + `color/text-body` text;
selected = `color/brand` fill + `color/text-inverse` text + Semibold; disabled = transparent fill
+ `color/text-disabled` text. A per-visual `pressed` state exists (`color/pressed-tint`
`#CDD8DF`) but has no theme-level `$id` — it can only be set on the individual button instance.

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
  (`docs/research/pdp-design-audit.md`); it isn't clickable and drifts under font-size changes.
  Use separate button/text visuals per crumb.

## 5. PDP report compatibility (existing 1440-wide report only)

Keep the report's established nav footprint instead of inventing new coordinates
(`docs/research/pdp-design-audit.md` §"Navigation bar"):

| Parameter | Value |
|---|---|
| Nav group | ≈ 590 × 38 px at x≈104, y≈3–4 — identical on every page (top strip) |
| Nav buttons | ≈ 197–223 × 31–38 px, 10 pt label |
| Canvas | 1440 × 675 (dashboards) / 1440 × 720 (drill-through) — DESIGN-TOKENS.md §7 |
| Brand navy | theme `ColorId 2` (`#003A5D`) via `ThemeDataColor` — this report's own navy, not the icon-library `#063E61` |

Everything else (typography, states, a11y) follows the canonical tokens in `DESIGN-TOKENS.md`.
