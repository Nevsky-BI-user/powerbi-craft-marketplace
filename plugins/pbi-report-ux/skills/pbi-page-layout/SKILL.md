---
name: pbi-page-layout
description: Use when placing or rearranging visuals on a Power BI report page - canvas size, x/y/width/height math, 8px grid snapping, header/KPI/chart/filter zones, gaps, overlaps, z-order, tab order. Do NOT trigger for visual JSON mechanics (powerbi-visuals), bookmark/tab visibility (powerbi-bookmarks), phone canvas (pbi-mobile-layout). Triggers - 'розкладка сторінки', 'сітка 8px', 'вирівняй візуали', 'канвас', 'макет сторінки', 'зони дашборду'
---

# Power BI Page Layout

## Overview

Layout is arithmetic, not eyeballing: `x/y/width/height` comes from the 8px grid and a
deliberate F-pattern zone (DESIGN-TOKENS §3; BRIEF F1, F4, F6, F9, F12). Formats:
PBIR-Legacy/enhanced. JSON writing → REQUIRED SUB-SKILL `powerbi-visuals`.

## When to Use

Planning a new page, adding a visual/row, fixing misalignment, overlap, jitter, z-order, tab
order.
**NOT for:** visual JSON edits (`powerbi-visuals`), bookmark/tab visibility
(`powerbi-bookmarks`), phone canvas (`pbi-mobile-layout`), theme colors (`pbi-theme-json`).

## Pre-flight (mandatory)

1. Detect format: Legacy `report.json` → `sections[].visualContainers[]`; enhanced →
   `definition.pbir` + per-visual `visual.json`.
2. Read the ACTUAL page `width/height/displayOption` — never assume 1280×720 (1440-wide →
   PDP profile, ref. §4).
3. Inventory existing visuals' positions (count by type) first.

## Quick Reference (1280×720; tokens §3)

| Token | Value |
|---|---|
| Canvas / usable | 1280×720, margin 24 → 1232×672 |
| Columns | 12 × 88 + 16 gutters; col start x = 24 + 104·(n−1) |
| Gaps | gutter 16 (8 inside a group); sections 24–32 |
| KPI cards | 6-up 192×104; 4-up 296×136 |
| Blocks | half 608, third 400; chart row h 240/280/320 |
| Header / filters | nav strip full×40; left rail 200×full |
| Tooltip page | 320×240, ActualSize |

## Zones, grid and order rules

**F-pattern:** title + hero number top-left → KPI strip → trends → detail table. Filters: strip
under title OR 200px left rail. One focal point per page — chosen by the page's claim
(`data-storytelling`), not by visual size.

**Grid:** snap all coordinates to multiples of 8. Rows share `y`+`height`; columns share
`x`+`width`. Verify sums: n·w + (n−1)·16 = 1232. Grouped visuals: children are relative to the
group origin.

**Z-order & tab order:** z bands — decorative < 1000, data 1000+, nav/slicers on top. `tabOrder`
= reading order, step 100 (a11y DoD). Legacy: top-level `x/y/z/width/height` mirrors
`config.layouts[0].position` (holds `tabOrder`) — sync via `powerbi-visuals`, never Tabular
Editor (semantic model only, a different PBIP artifact).

Worked stack: `24+40 header+16+104 KPI+16+280 charts+16+200 table+24=720`. Coordinate maps,
JSON snippets, left-rail variant, PDP profile → **reference.md**.

## Common Mistakes

| Mistake | Why bad | Fix |
|---|---|---|
| Assume 1280×720 canvas | Real canvas differs (PDP 1440) | Read `width/height` |
| Eyeballed coords (242.2…) | Reads as sloppy jitter | Snap to column starts, multiples of 8 |
| Filling every pixel | No whitespace = no hierarchy | 16px gutters, 24–32 section gaps |
| Divider shapes for grouping | Ink instead of space | Widen gap 8px; group visuals |
| z/tabOrder left default | Wrong paint / reader order | z bands + tabOrder by reading order |
| Only top-level x/y updated (Legacy) | Desktop reads `layouts[0].position` | Sync via `powerbi-visuals`, not Tabular Editor |
| Divider/rectangle keyed `basicShape` | Deprecated 2021 → silent no-op (F2: `visualStyles` accepts arbitrary keys — theme-visuals §7 п.2) | Use `shape`; verify against `theme-visuals.md` §5 |
