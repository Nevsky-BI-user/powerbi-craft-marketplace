---
name: pbi-bar-column-charts
description: Use when creating, restyling, sorting, or decluttering bar/column charts in Power BI PBIP reports (PBIR-Legacy or enhanced) — ranking, top-N, data labels vs axis, gridlines, category colors, small multiples. Do NOT trigger for chart-type selection (use pbi-visualization-strategy), trends (pbi-line-area-charts), or raw JSON mechanics (powerbi-visuals). Triggers - 'bar chart', 'column chart', 'sort bars', 'стовпчикова діаграма', 'лінійчаста діаграма', 'рейтинг', 'сортування стовпців'.
---

# Bar & Column Charts

## Overview

Bars encode value as position/length — the most accurately read encoding (Cleveland–McGill). A good bar chart is sorted by value, labeled directly, stripped of non-data ink, and saturates exactly one answer.

## When to Use

- Ranking/comparison across categories, top-N. Horizontal **bar** for long labels or >8 categories; vertical **column** for ≤8 or a short ordinal axis.
- NOT for: trends → `pbi-line-area-charts`; part-to-whole → `pbi-part-to-whole`; bar+line → `pbi-combo-charts`; chart choice → `pbi-visualization-strategy`.

Before writing JSON: detect PBIR-Legacy vs enhanced format, read a ground-truth visual as template, and verify every `queryRef` exists in the TMDL model (missing → `dax-measures`).

REQUIRED SUB-SKILL: `powerbi-visuals` (report.json/visual.json mechanics). Tokens → DESIGN-TOKENS.md (`pbi-design-system`).

## Quick Reference

| Decision | Rule |
|---|---|
| Visual-type keys | `barChart`/`columnChart` = STACKED; clustered = `clusteredBarChart`/`clusteredColumnChart`; plus `hundredPercentStacked*`. Theme all six identically |
| Sorting | Descending by value; ordinal axis (time, stages, Likert) keeps natural order |
| Labels vs axis | Pick ONE: labels (`type/small`, K/M units, 0–1 decimals) OR value axis. Axis only for dense/small-multiple charts |
| Category axis | Always on; `type/small` `color/text-secondary`; title off if the visual title covers it |
| Gridlines | Perpendicular to bars only, 1 px `color/border`; off when labels on; never both directions |
| Color | Single series `color/brand`, legend off; emphasis = one saturated point + `color/neutral-data` rest; categories → theme `dataColors`, max 6–8 + "Other" |
| Small multiples | Prefer over clustered when >3 series or a repeated question; 2×2/3×3, shared Y scale |

Exact property names, sorting locations, and a theme fragment: [reference.md](reference.md).

## Common Mistakes

| Mistake | Why bad | Correct |
|---|---|---|
| Alphabetical category order | Hides the ranking | Sort by measure desc; natural order for ordinal axes |
| Labels, axis, and gridlines together | Same number encoded three times | Labels on, axis + gridlines off |
| Uniform brand-color bars, or per-point hardcoded hex | No focal point; theme drift (antipattern A1/A3) | Gray + one hue; `ThemeDataColor` refs, fixed via the theme |
| Theming `columnChart` for a clustered visual | Stacked-variant key — silent no-op | Style the whole key triplet |
| Clustered chart with 4+ series | Middle bars incomparable | Small multiples, or top-N + "Other" |

## Verify before done

File written → JSON parses → visual keys match reference.md, card values are ARRAYS → bindings exist in model → `git diff` matches intent. Rendering cannot be verified headless.

Closes BRIEF F1, F2, F3, F5, F6, F7, F10.
