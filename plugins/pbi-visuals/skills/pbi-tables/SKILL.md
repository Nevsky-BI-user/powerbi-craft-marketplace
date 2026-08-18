---
name: pbi-tables
description: Use when creating, restyling, or formatting Table (tableEx) visuals in Power BI PBIP reports — column widths, alignment, header style, gridlines, zebra rows, number formats, data bars/icons/CF, sort order. Do NOT trigger for matrix (pbi-matrix), CF rule semantics (pbi-conditional-formatting), in-cell SVG bars (dax-svg), or JSON mechanics (powerbi-visuals). Triggers - 'таблиця', 'ширини колонок', 'вирівнювання чисел', 'зебра', 'сортування таблиці'.
---

# Power BI Tables (tableEx)

## Overview

Alignment, consistent number formats, and restrained ink decide scan speed in a table. Every non-data pixel (fill, gridline, CF) must earn its place.

## When to Use

- Detail rows, ranked lists with exact values, many measures per entity.
- NOT for: hierarchies/subtotals → `pbi-matrix`; table-or-chart choice → `pbi-visualization-strategy`; one number → `pbi-kpi-cards`.

REQUIRED SUB-SKILL: `powerbi-visuals` for JSON mechanics (selectors, sort shape). CF semantics → `pbi-conditional-formatting`; in-cell SVG/sparklines → `dax-svg`; missing measures → `dax-measures`. Tokens → DESIGN-TOKENS.md (`pbi-design-system`).

## Pre-flight (mandatory)

1. Detect PBIR-Legacy (`report.json`) vs enhanced (`definition.pbir` + `visual.json`).
2. Read a real `tableEx` as template, never from memory. Key is `tableEx`; `table` is a silent no-op.
3. Verify every `queryRef` exists in the TMDL model; formats live in the model.
4. Resolve theme `ThemeDataColor` mapping; read page `width/height` first.

## Quick Reference

| Decision | Rule |
|---|---|
| Header | `color/brand` fill, `color/text-inverse` text, 10 pt bold, `alignment: "Auto"` |
| Alignment | Text left, numbers right, one fixed date format — never center numbers |
| Column widths | `columnAdjustment: "fixedWidth"`; widths never jump; entity column widest |
| Grid & density | Horizontal-only, 1 px `color/border`; zebra `color/surface-alt`; `rowPadding` 4 |
| Number formats | TMDL format strings: thousands separator, K/M units, 0–1 decimals |
| Conditional formatting | Max 1–2 CF columns: bars = magnitude, icons = status, `ramp/diverging` = vs plan |
| Default sort | Deliberate — primary measure desc, or date desc for logs; copy from ground truth |
| Totals | `total` card bold; `totals: false` when the aggregate is meaningless |

Exact card/property names and a ready theme fragment: [reference.md](reference.md).

## Common Mistakes

| Mistake | Why bad | Correct |
|---|---|---|
| Theming `table` | Key doesn't exist | `tableEx` |
| Centered/left numbers | Can't compare magnitudes by eye | Right-align; header follows via `Auto` |
| Auto-size widths | Layout jumps on refresh/filter | `fixedWidth` + per-column `columnWidth` |
| Zebra + vertical grid + outline | Row/column encoded thrice | Horizontal gridlines + subtle zebra only |
| Red/green CF alone | Fails colorblind users | Pair icons/labels; ramps from tokens |

## Verify before done

JSON parses, key is `tableEx`, card values are ARRAYS → bindings exist in model → `altTextColumns` set, contrast ≥ 4.5:1 → `git diff` matches intent. Rendered widths/wrapping can't be verified headless — say so.

Closes BRIEF F1–F3, F5–F7, F9–F10.
