---
name: pbi-part-to-whole
description: "Use when choosing or designing a part-to-whole visual in Power BI PBIP: pie, donut, treemap, stacked/100% stacked, or waffle. Covers category limits and the \"Other\" bucket. Do NOT trigger for chart selection (pbi-visualization-strategy), bar/column craft (pbi-bar-column-charts), JSON mechanics (powerbi-visuals), or Deneb builds (deneb-vegalite). Triggers - 'pie chart', 'donut chart', 'кругова діаграма', 'донат діаграма', 'treemap', 'waffle chart', '100% stacked', 'частка від цілого'."
---

# Part-to-Whole Composition

## Overview

Part-to-whole shows how a total splits into parts. Angle/area are the weakest perceptual encodings (Cleveland–McGill) — pie/donut suit one moment, few parts; beyond that a sorted bar reads faster. This skill picks the shape and enforces category-limit / "Other"-bucket discipline.

## When to Use

- Deciding among pie/donut, treemap, stacked/100%-stacked, or waffle for a "how does X break down" question, or fixing a doubtful pie/donut.
- NOT for: chart-type selection (`pbi-visualization-strategy`), stacked bar/column craft (`pbi-bar-column-charts`), JSON authoring (`powerbi-visuals`), Vega-Lite builds (`deneb-vegalite`).

Before writing JSON: detect PBIR format, read a ground-truth pie/donut/treemap visual (cards unverified — see reference.md §1), count categories, verify fields against the TMDL model.

REQUIRED SUB-SKILL: `powerbi-visuals`. "Other" measures → `dax-measures`. Custom waffle → `deneb-vegalite`. Tokens → `pbi-design-system`.

## Quick Reference

| Decision | Shape / rule |
|---|---|
| ≤5, one moment, whole matters | `donutChart` (preferred) or `pieChart` — never mix both in one report |
| ≤5, ranking beats the whole | sorted `clusteredBarChart`/`clusteredColumnChart` → craft in `pbi-bar-column-charts` |
| >5, per-item precision needed | sorted bar + "Other" bucket — position beats angle |
| 2-level hierarchy, area ≈ proportional | `treemap` (≤2 levels); deeper → `decompositionTreeVisual` (`pbi-ai-visuals`) |
| Repeats across time/categories | `stackedAreaChart` / stacked `columnChart`; segment craft → `pbi-bar-column-charts` §5 |
| Share only, total not needed | `hundredPercentStackedBarChart`/`ColumnChart`/`AreaChart` — needs a legend |
| Exact % of a fixed count, a11y priority | waffle-style unit chart — not native → `deneb-vegalite` |
| "Other" bucket recipe | rank by measure, keep top N, fold rest into "Other" (last, never value-sorted) — `dax-measures` |

Exact visual keys, treemap/waffle detail, worked example: [reference.md](reference.md).

## Common Mistakes

| Mistake | Instead |
|---|---|
| Pie/donut with >5 slices | Sorted bar; tail grouped into "Other" |
| Mixing pie AND donut on one report | Pick one idiom, use it everywhere |
| "Other" sorted by value into the middle | Always last, regardless of its value |
| Treemap with 3+ hierarchy levels | Cap at 2; deeper → decomposition tree |
| Untracked custom waffle visual from AppSource | Prefer `deneb-vegalite` unit-chart spec |
| Inventing `dataPoint`/`legend` card names for donut/treemap | Confirm against ground truth or schema first (BRIEF F2) |

## Verify before done

File written → JSON parses → category count within the shape's limit → "Other" present, sorted last, when exceeded → bindings exist in model → `git diff` matches intent. Rendering (slice angles, treemap areas) can't be verified headless — say so.

Closes BRIEF F1, F2, F5, F6, F7, F10.
