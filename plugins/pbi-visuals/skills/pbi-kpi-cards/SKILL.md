---
name: pbi-kpi-cards
description: Use when creating or restyling KPI/scorecard cards in Power BI PBIP reports (Legacy or enhanced) - card vs cardVisual vs multiRowCard vs kpi choice, title/value/delta anatomy, good/bad delta color, showBlankAs, card grids. Do NOT trigger for chart choice (pbi-visualization-strategy), delta DAX/SVG (dax-measures/dax-svg), visual JSON mechanics (powerbi-visuals), or what the card should SAY - naming its comparison base so a bare number becomes a finding (data-storytelling). Triggers - 'KPI картка', 'скорборд', 'delta колір', 'сітка карток', 'multi-row card'.
---

# Power BI KPI Cards

## Overview

A KPI card is one number absorbed in under a second — but only if every card shares identical title/value/delta styling, property by property. Partial restyles silently diverge.

## When to Use

- Single-metric callouts, KPI rows, scorecards, delta/trend indicators, per-entity metric grids.
- NOT for: multi-series trends → `pbi-bar-column-charts`/`pbi-line-area-charts`; gauges/progress → `pbi-gauges-progress`; many metrics × entities → `pbi-tables`/`pbi-matrix`; chart choice → `pbi-visualization-strategy`.

Before writing JSON: detect PBIR-Legacy vs enhanced, read a real same-type card from the target report as parity template, verify every `queryRef` against the TMDL model.

REQUIRED SUB-SKILL: `powerbi-visuals` (cloning, GUID, object wrapping). Delta measures → `dax-measures`; sparkline → `dax-svg`; icons → `icon-set-manager`; tokens → `pbi-design-system`; label wording and naming the comparison base in words («−3 п.п. до червня», not «−3%») → `data-storytelling`.

## Quick Reference

| Decision | Rule |
|---|---|
| Visual type | Value+title → `cardVisual` (default); goal/trend indicator → `kpi` (`status` good/bad/neutral); several metrics, one entity → `multiRowCard`; legacy → `card` (existing only) |
| Title | `type/title` 12pt Semibold, `color/text-title`; one size per tier (A4) |
| Value | `type/value` 12pt; hero `type/callout-hero` 28pt, one per page max |
| Delta | Mark (accentBar/icon): `color/good`/`bad`. Small-delta text (fontColor): `color/good-text`/`bad-text`. Always + ▲▼ icon; never color alone (F9) |
| Blank value | `showBlankAs` on `value`/`referenceLabelValue`; unset renders nothing |
| Card shell | `shape/radius` 8, `shape/border`, `color/surface`; border OR shadow, never both |
| Grid | 6-up 192×104, 4-up 296×136, hero 296×176; 16px gutter, 8px snap |

Exact property names, the `e27a80` recipe, and the parity-diff method: [reference.md](reference.md).

## Common Mistakes

| Mistake | Why bad | Correct |
|---|---|---|
| Restyle cards by eye, no diff | Properties silently diverge or land in wrong dictionary | Diff every card vs etalon (reference.md §7) first |
| `card` for new work | Legacy (7 of 514 in PDP); fewer features | `cardVisual` |
| Delta by color only | Fails colorblind/grayscale readers | Pair with ▲▼ icon or label |
| `showBlankAs` unset | Renders empty on a filtered-to-empty slice | Set on `value`/`referenceLabelValue` |
| Mixed title sizes in one row | Broken hierarchy (A4) | One `type/title` per tier |
| Container title + built-in `label` both on | Measure name twice — title strip + label above value | One label source; if built-in `label`, set `visualContainerObjects.title.show=false` |
| Hardcoded hex per card | Theme drift (A1) | `ThemeDataColor` / theme's `good`/`bad` names |
| `good`/`bad` on small delta text | Fails AA (F9), reference.md §4 | use `color/good-text`/`bad-text` |

## Verify before done

JSON parses, card values are ARRAYS → bindings exist in model → **full parity table** vs the reference card (reference.md §7) → delta never color-alone, contrast ≥ 4.5:1 → `git diff` matches intent. Layout can't be verified headless — say so.

Closes BRIEF F1, F2, F3, F4, F5, F6, F7, F9, F10, F11.
