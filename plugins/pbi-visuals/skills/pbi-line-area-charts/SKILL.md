---
name: pbi-line-area-charts
description: Use when creating or restyling Power BI line/area trend charts — series count, markers, interpolation, end-of-line labels, trendlines, forecast bands, area transparency, date-axis format. Do NOT trigger for ranking (pbi-bar-column-charts), dual-axis combo (pbi-combo-charts), chart choice (pbi-visualization-strategy), or JSON mechanics (powerbi-visuals). Triggers - 'line chart', 'area chart', 'trend line', 'forecast', 'лінійна діаграма', 'діаграма з областями', 'тренд', 'прогноз', 'часовий ряд'.
---

# Line & Area Charts

## Overview

Line encodes trend as position along a continuous axis (usually time); area adds
filled magnitude below it — use the fill only when volume is the message, not to
make a line "look bolder." One chart, one trend, **≤4–5 series**.

## When to Use

- Trend over a continuous/ordinal axis: single series or ≤4–5 comparison set.
- Area/stacked area only when the filled volume is the message.
- NOT for: ranking → `pbi-bar-column-charts`; mixed units → `pbi-combo-charts`;
  chart-choice → `pbi-visualization-strategy`; single-point share → `pbi-part-to-whole`.

Before writing JSON: detect PBIR-Legacy vs enhanced format, read a ground-truth
visual as template, confirm a true date/continuous axis, and verify every
`queryRef` exists in the TMDL model.

REQUIRED SUB-SKILL: `powerbi-visuals` (JSON mechanics). Measures → `dax-measures`.
Tokens → DESIGN-TOKENS.md (`pbi-design-system`).

## Quick Reference

| Decision | Rule |
|---|---|
| Visual-type keys | `lineChart` (only key with `forecast`/`anomalyDetection`), `areaChart`, `stackedAreaChart`, `hundredPercentStackedAreaChart` — diffs: reference.md §1; mixed units → `pbi-combo-charts` |
| Series count | ≤4–5 lines; beyond, small multiples or rank + "Other" |
| Markers & interpolation | Markers ON sparse/monthly, OFF dense daily/hourly (`lineStyles.showMarker`); `lineChartType` linear default, smooth for continuous only, step for state changes |
| Line weight | One emphasis line (`color/brand`, thicker stroke); rest thinner, `color/neutral-data` |
| Labels vs legend | ≤5 series: `seriesLabels` at line end; 6+: legend `type/small` |
| Data labels | Last point only — units K/M, 0–1 decimals |
| Trend/forecast | `trend`: dashed, `color/text-secondary`; `forecast` (`lineChart` only): continuation + confidence band — both labelled |
| Area transparency | `dataPoint.transparency`; Y axis must start at 0 |

Exact card/property names, enums, theme fragment: [reference.md](reference.md).

## Common Mistakes

| Mistake | Why bad | Correct |
|---|---|---|
| 6+ thin same-weight lines | Spaghetti | ≤4–5 series; small multiples or "Other" |
| Smoothed/marker-heavy style on dense, volatile data | Hides real swings; visual noise | Linear + markers off; reserve for sparse series |
| Basic `areaChart` with 3+ series | Fills occlude each other | `stackedAreaChart` or drop the fill |
| Truncated Y axis under a fill | Distorts magnitude | Always start at 0 |
| Trendline/forecast styled like actual data | Can't tell fact from projection | Dashed, secondary color, labelled |
| Legend AND end-of-line labels both on | Double-encodes identity | Pick one |

## Verify before done

JSON parses, keys/card names match reference.md, values are ARRAYS, bindings exist
in model, `git diff` matches intent. Rendering clarity can't be verified headless.

Closes BRIEF F1, F2, F3, F5, F6, F7, F10.
