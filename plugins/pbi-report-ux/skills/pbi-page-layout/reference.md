# pbi-page-layout — reference

Detailed coordinate maps and JSON shapes that don't fit in SKILL.md's word budget.

## 1. Full page coordinate map (1280×720, sums exactly — verify before writing)

| Visual | x | y | width | height |
|---|---|---|---|---|
| Header / title strip | 24 | 24 | 1232 | 40 |
| KPI card 1 | 24 | 80 | 192 | 104 |
| KPI card 2 | 232 | 80 | 192 | 104 |
| KPI card 3 | 440 | 80 | 192 | 104 |
| KPI card 4 | 648 | 80 | 192 | 104 |
| KPI card 5 | 856 | 80 | 192 | 104 |
| KPI card 6 | 1064 | 80 | 192 | 104 |
| Chart A (half) | 24 | 200 | 608 | 280 |
| Chart B (half) | 648 | 200 | 608 | 280 |
| Detail table (full) | 24 | 496 | 1232 | 200 |

Row math: 24 margin + 40 header + 16 gutter = 80 (KPI row y). 80 + 104 + 16 = 200 (chart row y).
200 + 280 + 16 = 496 (table y). 496 + 200 + 24 margin = 720. KPI x-steps: 24 + 208·(n−1)
(192 width + 16 gutter, 2-column span each). Column-start formula for any n-th single grid
column: `x = 24 + 104·(n−1)` (88 col + 16 gutter).

## 2. JSON position snippets (write via `powerbi-visuals`, never hand-roll)

**Legacy** (`report.json`) — top-level fields AND `config.layouts[0].position` must carry
identical values; `tabOrder` lives only in the `layouts[0].position` copy:

```json
{
  "x": 232, "y": 80, "z": 1000, "width": 192, "height": 104,
  "config": "{\"layouts\":[{\"id\":0,\"position\":{\"x\":232,\"y\":80,\"z\":1000,\"width\":192,\"height\":104,\"tabOrder\":200}}]}"
}
```

**PBIR enhanced** (`visual.json`) — single `position` object, no duplication:

```json
{
  "position": { "x": 232, "y": 80, "z": 1000, "width": 192, "height": 104, "tabOrder": 200 }
}
```

## 3. Left-rail variant (200 px filter rail instead of a top filter strip)

Rail: `x:24, y:24, width:200, height:672` (full usable height). Content area shifts right:
effective left margin becomes `24 + 200 + 16 = 240`; usable content width
`1280 − 240 − 24 = 1016`. Recompute column starts and KPI/chart widths against 1016, not 1232
— do not reuse the top-strip numbers from §1 unchanged.

## 4. PDP 1440 compatibility profile (existing production report ONLY — DESIGN-TOKENS §7)

| Parameter | Value |
|---|---|
| Canvas | 1440×675 (dashboards, FitToWidth) / 1440×720 (drill-through) / 1440×3400–3800 (scroll) |
| Page margin | 70 px; content width 1300 |
| Columns | 5 × 248 px + 4 × 15 px gutters (= 1300) |
| Card heights | 106 / 140 / 178 (observed standard) |
| Half-blocks | 642 px + 16 px center gutter |
| Brand navy | theme's `ColorId 2` (`#003A5D`) via `ThemeDataColor` |

Use this profile only when editing that report; new pages use §1's 1280×720 grid.
