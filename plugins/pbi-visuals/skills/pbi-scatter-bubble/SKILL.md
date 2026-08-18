---
name: pbi-scatter-bubble
description: Use when creating or restyling a Power BI PBIP scatter/bubble chart for correlation analysis - bubble-size encoding, quadrants via constant lines, or labeling only outlier points. Do NOT trigger for chart-type choice (pbi-visualization-strategy), Deneb scatter/quadrant/density (deneb-vegalite), or JSON mechanics (powerbi-visuals). Triggers - 'scatter chart', 'bubble chart', 'quadrant chart', 'діаграма розсіювання', 'бульбашкова діаграма', 'квадранти', 'кореляція'.
---

# Scatter & Bubble Charts

## Overview

Scatter encodes two continuous measures as position — the strongest encoding; bubble AREA adds a weaker third (Cleveland–McGill). Power BI exposes only two constant lines (X+Y); 4-color quadrant fills and per-point outlier labels are gaps routed below. Formats: PBIP, PBIR-Legacy/enhanced, TMDL model.

## When to Use

- Correlation between two measures, optionally size (3rd) and color (4th); ≤ ~1k points raw.
- Quadrant analysis via two constant lines (e.g., growth vs. margin).

**NOT for:** chart-type choice (`pbi-visualization-strategy`); 4-quadrant fill, selective labels, >1k-pt density (`deneb-vegalite`); JSON mechanics (`powerbi-visuals`); flag/rollup measures (`dax-measures`).

REQUIRED SUB-SKILL: `powerbi-visuals` (JSON mechanics). Tokens → DESIGN-TOKENS.md (`pbi-design-system`).

## Pre-flight (mandatory)

1. Detect format; read a real `scatterChart` from the target report as template — never from memory.
2. Verify X/Y/size/color `queryRef`s exist in the model (missing → `dax-measures`); read actual page `width`/`height` first.

## Quick Reference

| Decision | Rule |
|---|---|
| Visual-type key | `scatterChart` — one key for scatter and bubble (bubble = a field bound to Size) |
| Axis naming trap | `categoryAxis` = **X**, `valueAxis` = **Y**; set `axisType: "Scalar"` for continuous X |
| Bubble size | 3rd measure → `bubbles.bubbleSize`; encodes AREA — never pre-square/cube it |
| Quadrants | `xAxisReferenceLine` + `y1AxisReferenceLine`; anchor `value` at 0/target, never the data mean |
| Quadrant fill | `shadeRegion` caps at 2 zones; 4-zone fill = 4 `shape` visuals + corner labels, or `deneb-vegalite` |
| Outlier labels | `categoryLabels.show` is all-or-nothing; drive from a DAX flag (`dax-measures`), rule semantics `pbi-conditional-formatting` if exposed, else `deneb-vegalite` |
| Color | Nominal → `colorByCategory`; 4th measure → `dataPoint.fillRule` with `ramp/brand-seq`/`ramp/diverging`, never rainbow |
| Overplotting | >~1k points: pre-aggregate (`dax-measures`), lower `markers.transparency`, cap `general.dataVolume` |
| Trend line | `trend` card, one line unless `combineSeries: false` |

Exact card/property names, quadrant recipe JSON, outlier-label technique: [reference.md](reference.md).

## Common Mistakes

| Mistake | Why bad | Correct |
|---|---|---|
| Bubble measure pre-squared | Area double-encoded | Feed the raw measure; native sizing already scales area |
| 2 shaded halves called "4 quadrants" | Only 2 of 4 zones tinted | 4 corner textboxes + shape overlay, or `deneb-vegalite` |
| All category labels on for 30+ points | Text soup | Outlier-only flag measure, or legend + hover |
| Reference-line `value` = data mean | Shifts every refresh | Anchor at 0, a target, or fixed threshold |

## Verify before done

File written → JSON parses → visual key/card names match reference.md → bindings exist in the model → constant-line values justified → `git diff` matches intent. Rendering/overplotting can't be judged headless — say so.

Closes BRIEF F1, F2, F3, F5, F6, F7, F10.
