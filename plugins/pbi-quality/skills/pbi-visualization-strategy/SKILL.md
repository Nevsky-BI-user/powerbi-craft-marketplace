---
name: pbi-visualization-strategy
description: Use when picking which Power BI visual answers an analytical question - comparison, trend, part-to-whole, distribution, relationship, geo, KPI - or a chart looks misleading, overloaded, or wrong-shaped; also table vs chart, or native vs SVG/Deneb. Do NOT trigger for visual JSON mechanics (powerbi-visuals), SVG rendering (dax-svg), Deneb specs (deneb-vegalite), or the page's claim and title wording (data-storytelling). Triggers - 'який візуал обрати', 'вибір діаграми', 'chart choice', 'pie чи bar', 'яка візуалізація краще', 'дерево вибору візуалу'.
---

# Power BI Visualization Strategy

Chart-selection judgment for PBIP reports (report.json PBIR-Legacy or PBIR enhanced; model TMDL).

## Overview

Choose the visual from the reader's question, not the gallery. Perception ranking (Cleveland–McGill): position > length > slope > angle > area > color — use the highest the data allows; saturate one series (`color/brand`, `pbi-design-system` §6).

## When to Use

- Picking a visual for a new element; challenging a doubtful chart.
- Deciding table vs chart, or native vs `dax-svg`/`deneb-vegalite`.

**NOT for:** visual JSON (`powerbi-visuals`), bookmarks/visibility (`powerbi-bookmarks`), measures (`dax-measures`), per-chart styling (matching `pbi-*` skill, e.g. `pbi-kpi-cards`), the page's claim, title wording and annotation layer (`data-storytelling`).

The reader's question comes from the page claim: underline the comparison word in it (частка / більше ніж / зросло / розподіл / залежить від) and pick the shape from that word — `data-storytelling` reference.md §1.

## Quick Reference — question → visual (exact internal keys)

| Question | First choice | Notes |
|---|---|---|
| Compare categories | `clusteredBarChart`, sorted desc | ≤12 bars (≤20 with scroll), labels on |
| Trend over time | `lineChart` | ≤4–5 series, else gray + one hue |
| Composition over time | `stackedAreaChart` / stacked `columnChart` | share → 100%-stacked |
| Part-to-whole, one moment | `donutChart` ≤5 slices | else bar or `treemap` (≤2 levels) |
| Plan vs fact | bar + variance measure; bridge → `waterfallChart` | bullet → `dax-svg` |
| Correlation | `scatterChart` | bubble = 3rd measure, ≤~1k points |
| Distribution | binned `clusteredColumnChart` | box plot → `deneb-vegalite` |
| Geography | `filledMap` (rates) / `map` (magnitudes) | only for "where"; both Bing — deprecation scheduled, prefer `azureMap`/`shapeMap` for new (`pbi-maps-geo`) |
| Single KPI | `cardVisual` | classic `card` only for legacy |
| Exact-value lookup | `tableEx` / `pivotTable` | in-cell bars → `dax-svg` |
| Why / drivers | `decompositionTreeVisual`, `keyDriversVisual` | needs enough rows |

Full matrix, decision tree, limits, table-vs-chart test, native-gap routing → **reference.md**.

## Worked Example

```
Question: план/факт продажів по 12 категоріях
Choice:   clusteredBarChart, sorted by variance; % labels (dax-measures);
          bullet targets → dax-svg
Rejected: gauge ×12 (no comparison); pieChart (not part-to-whole)
Route:    JSON → powerbi-visuals; tokens → `pbi-design-system` §6
```

## Common Mistakes

| Mistake | Why bad | Instead |
|---|---|---|
| Pie/donut >5 slices | angle = weakest encoding | sorted bar; tail → "Other" |
| Dual axis to imply correlation | fakes a relationship | two charts, shared X; combo only for different units |
| 3D, skeuomorphic gauges | distorts perception | flat 2D; KPI → `cardVisual` |
| `funnel` endorsed uncritically | widths overstate drop-off | stage bars + conversion-% |
| Chart where values must be read | forces guessing | `tableEx` — tables win at lookup |
| Invented keys (`table`, `matrix`, `smartNarrative`) | silently ignored | `tableEx`, `pivotTable`, `aiNarratives` |
