# Power BI Visualization Strategy — Reference

Deep-dive companion to SKILL.md. Visual-type keys verified against
`docs/research/theme-visuals.md` §5 — 48 native visual-type keys (52 total `visualStyles`
schema keys once the `page`/`report`/`filter`/`group` pseudo-entries are counted too, schema
2.143–2.155); this skill only routes chart-choice for the 48 real visual types, matching the
count `pbi-theme-json` covers.

## Decision tree

1. **What is the reader asking?** Map to one bucket: comparison, trend, part-to-whole,
   deviation, distribution, relationship, geography, single-value/status, exact lookup,
   flow/hierarchy, or "why".
2. **How many categories/series/points?** Check Limits below — if over the ceiling, bin,
   sort-and-truncate to "Other", or switch to a table.
3. **Does a native visual (theme-visuals.md §5) cover it?** If not, route to the Native-gap
   table — do not force a native visual into a shape it can't encode.
4. **Read vs compare?** If the reader must verify exact figures, prefer a table even when a
   chart would also "work" — see Table-vs-chart test.

## Full matrix (extends SKILL.md Quick Reference)

| Question | First choice | Notes |
|---|---|---|
| Ranking / top N | `clusteredBarChart` sorted desc | callout for #1 via `cardVisual` |
| Deviation from target | `clusteredColumnChart` + reference line, or `waterfallChart` for bridges | native error bars available on some cartesian charts |
| Composition ranked over time | `ribbonChart` | shows rank swaps; ≤6 series |
| Multi-measure trend, different units | `lineClusteredColumnComboChart` / `lineStackedColumnComboChart` | never combo same-unit series just to fit two axes |
| Hierarchy drill | `pivotTable` + drillthrough, or `decompositionTreeVisual` | mechanics → `powerbi-bookmarks`/`powerbi-visuals` |
| Flow between stages (linear) | `funnel` | ≤7 stages; label conversion %, not just width |
| Flow between stages (branching) | none native | `deneb-vegalite` (Sankey) |
| Rank-over-time / bump chart | none native | `deneb-vegalite` |
| Correlation matrix / heatmap | `pivotTable` + conditional formatting (coarse) | full control → `deneb-vegalite` |
| Distribution across groups | binned `clusteredColumnChart` (histogram) | box plot → `deneb-vegalite` |

## Limits & thresholds (practical ceilings before readability breaks)

| Visual | Ceiling | Beyond it |
|---|---|---|
| `clusteredBarChart`/`clusteredColumnChart` | ≤12 categories ideal, ≤20 with scroll | group tail into "Other" or switch to `tableEx` |
| `pieChart`/`donutChart` | ≤5 slices | sorted bar |
| `lineChart` | ≤4–6 series before color collision | gray out all but the focus series + one hue |
| `scatterChart` | ≤~1,000 points before overplotting | transparency, sampling, or binning |
| `treemap` | ≤2 hierarchy levels practical | deeper → `decompositionTreeVisual` |
| `waterfallChart` | ≤15 categories | aggregate smaller buckets into "Other" |
| `funnel` | ≤7 stages | merge adjacent stages |

## Table vs chart test

Ask: does the reader need to (a) compare shapes/trends at a glance, or (b) verify/read exact
values? (a) → chart. (b) → `tableEx`/`pivotTable`. Both → chart above a table, or in-cell bars
inside `tableEx` via `dax-svg` (conditional-formatting data bars for coarse cases).

## Native-gap routing (no native visual covers this — route to code)

| Need | Native gap | Route |
|---|---|---|
| Bullet chart | none | `dax-svg` |
| Box plot | none | `deneb-vegalite` |
| Sankey / branching flow | none | `deneb-vegalite` |
| Full-control heatmap | `pivotTable` CF is coarse | `deneb-vegalite` |
| Bump / rank-over-time chart | none | `deneb-vegalite` |
| Radar / spider chart | none (legacy custom visual only) | `deneb-vegalite` |
| Gantt chart | none native | AppSource custom visual or `deneb-vegalite` |
| Custom in-cell shapes beyond native sparklines | `pivotTable` has native `sparklines` card only | `dax-svg` |

## See also

Per-visual-type styling (color, spacing, states) lives in the matching library skill:
`pbi-bar-column-charts`, `pbi-line-area-charts`, `pbi-part-to-whole`, `pbi-waterfall-funnel`,
`pbi-scatter-bubble`, `pbi-maps-geo`, `pbi-kpi-cards`, `pbi-tables`, `pbi-matrix`,
`pbi-gauges-progress`, `pbi-combo-charts`, `pbi-ai-visuals`. This skill only decides *which*
shape to use; those decide how it looks; `data-storytelling` decides what it claims.
