---
name: pbi-combo-charts
description: Use when deciding if a line+column combo chart is justified, styling lineClusteredColumnComboChart/lineStackedColumnComboChart, syncing primary/secondary value axes, or building a plan-vs-actual+variance visual. Do NOT trigger for single-series bars (pbi-bar-column-charts), pure trend lines (pbi-line-area-charts), or chart-choice triage (pbi-visualization-strategy). Triggers - 'комбо діаграма', 'лінія і стовпці', 'подвійна вісь', 'план факт відхилення', 'dual axis'.
---

# Combo Charts (Line + Column)

## Overview

A combo chart overlays a line on clustered/stacked columns to read two measures of
**different unit or scale** on one shared category axis. Per Cleveland–McGill, columns
(position) outrank the line (slope): column = magnitude, line = rate, never inverted
(`pbi-design-system` §3.4). Verified visual-type keys:
`lineClusteredColumnComboChart`, `lineStackedColumnComboChart`. Column → `pbi-bar-column-charts`;
line → `pbi-line-area-charts`; combo-or-not → `pbi-visualization-strategy`; JSON →
`powerbi-visuals`; variance DAX → `dax-measures`; tokens → `pbi-design-system` (`pbi-design-system`).

## When to Use

- Two measures with **different units or magnitudes** read together against the same
  categories (actual $ + variance %, revenue + margin %).
- NOT for: same-unit measures (one axis); single-series charts
  (`pbi-bar-column-charts`/`pbi-line-area-charts`); the chart-choice decision
  (`pbi-visualization-strategy`).

Before writing JSON: detect PBIR-Legacy vs enhanced, read a ground-truth visual, verify
`queryRef`s exist in the model (missing measure → `dax-measures`).

## Quick Reference

| Decision | Rule |
|---|---|
| Justify the combo | Only different units/scale, both matter at once. Same unit → one axis |
| Axis strategy | Try `sharedAxis: true` first; `secShow: true` only if incompatible |
| Axis sync (2 axes) | `alignZeros: true` — else relative movement lies |
| Series roles | Column = magnitude; Line = rate/trend/target — never invert |
| Color | Column `color/brand`; line `color/accent`; never both |
| Legend | Always ON (2+ series); `type/small`, bottom or top-right |
| Labels | One style per axis; don't double-encode with gridlines too |

Property tables and a JSON fragment: [reference.md](reference.md).

## Avoiding Dual-Axis Manipulation

Add a secondary axis only when one scale would flatten a series at zero — then
`alignZeros: true`. Never hand-tune `secStart`/`secEnd` for a crossing; auto-scale,
and always set `secTitleText`.

## Worked Example: Plan vs Actual + Variance

`clusteredColumnChart` (Plan/Actual, `color/brand`/`color/neutral-data`) + line = `Variance %`,
secondary axis, `color/accent`, `alignZeros: true`, `secTitleText: "Variance %"`. Line uses
`ramp/diverging`, midpoint at 0% (meaningful center, not the mean). No second axis wanted?
Native `error` band, or a bullet-style target via `dax-svg` ([reference.md](reference.md)).

## Common Mistakes

| Mistake | Why bad | Correct |
|---|---|---|
| Combo for same-unit measures | No scale problem to solve | One axis, or two charts |
| Zeros not aligned across axes | Line falsely diverges | `alignZeros: true` |
| Hand-tuned `secStart`/`secEnd` | Manipulates the crossing | Auto-scale or matching bounds |
| Secondary axis, no title | Reader can't tell units differ | `secShowAxisTitle` + `secTitleText` |
| Both series `color/brand` | No visual separation | Column brand, line accent |

## Verify before done

JSON parses → keys/cards match reference.md → bindings exist in the model →
`alignZeros`/`sharedAxis` deliberate → `git diff` matches intent. Rendering cannot be verified
headless — say so.

