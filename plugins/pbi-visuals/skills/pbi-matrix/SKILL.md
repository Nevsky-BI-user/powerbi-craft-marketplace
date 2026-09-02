---
name: pbi-matrix
description: Use when creating or restyling Matrix (pivotTable) visuals in Power BI PBIP reports (PBIR-Legacy or enhanced) - hierarchies, stepped/outline/tabular layout, drill-expand icons, subtotal vs grand-total styling, heatmap CF, sparklines. Do NOT trigger for flat tables (pbi-tables), CF semantics incl. a heat map's colour rules — 'теплова карта' (pbi-conditional-formatting), drill-through pages (pbi-drillthrough), JSON mechanics (powerbi-visuals). Triggers - 'матриця', 'зведена таблиця', 'ієрархія', 'проміжні підсумки', 'matrix visual', 'pivot table'.
---

# Power BI Matrix (pivotTable)

## Overview

A matrix packs several grains — detail, subtotal, grand total — into one grid. The design job:
stepped indentation, a clear strength order values → subtotal → grand total, a heatmap layer
that adds signal, not noise.

## When to Use

- Row/column hierarchies (Category > Product, Region > Store), pivoted cross-tabs, per-level
  subtotals.
- NOT for: flat ranked lists → `pbi-tables`; CF semantics → `pbi-conditional-formatting`;
  drill-through pages → `pbi-drillthrough`.

REQUIRED SUB-SKILL: `powerbi-visuals` (JSON mechanics, `$id` selectors, CF wiring). Missing
measures → `dax-measures`; tokens → `pbi-design-system`.

## Quick Reference

| Decision | Rule |
|---|---|
| Layout | `Compact` (default, stepped) · `Outline` (subtotal own row) · `Tabular` (every level own column, export only) |
| Stepped rows | `rowHeaders.stepped`+`showExpandCollapseButtons`; icon `color/text-secondary`; `repeatRowHeaders` on tall matrices |
| Header fill | Brand fill on `columnHeaders` only; `rowHeaders` = `color/surface` — separate levels by weight/indent, not extra color (`pbi-design-system` §3.4) |
| Subtotals & totals | `subTotals` (`$id: "Row"`/`"Column"`, axis-scoped) bold + `color/surface-alt`; `total`/`rowTotal`/`columnTotal` bold+underline, firmer tint; **neither has `border`** |
| Drill icons | Keep `visualHeader.show: true`, tint `foreground` |
| Heatmap | CF `backColor` rule, `ramp/brand-seq` (magnitude) or `ramp/diverging` (vs. target); never with `values.bandedRowHeaders` |
| Sparklines | `sparklines` card, `chartType: "line"`, `color/accent`, `strokeWidth` 1–2 |
| Grid | `gridHorizontal` 1 px `color/border`; `gridVertical` off unless deep column hierarchy |

Full cards (14 verified), drill icons, theme fragment, header pair law:
[reference.md](reference.md).

## Workflow

Detect format (PBIR-Legacy vs enhanced) → read a real `pivotTable` as template (`matrix`
doesn't exist) → verify every hierarchy field/measure exists in TMDL → resolve `ThemeDataColor`
mapping and page `width`/`height`.

## Common Mistakes

| Mistake | Why bad | Correct |
|---|---|---|
| Theming `matrix` | Key doesn't exist — silent no-op | `pivotTable` |
| `columnHeaders.fontColor` in visual.json, `backColor` from theme | Pair desyncs on any theme change — header vanishes | Both sides in ONE place; theme default: `visualStyles.pivotTable.*.columnHeaders` |
| `Tabular` layout by default | Repeats every value per row, kills the stepped scan | `Compact` + `rowHeaders.stepped` |
| Inventing `border` on `subTotals`/`total` | Property doesn't exist (F2) | `backColor` tint + `bold`/`underline` |
| Heatmap + zebra together | Two competing background systems | Pick one background pattern |
| `visualHeader.show: false` on hierarchy matrix | Removes the only drill controls | Keep visible, style via `foreground`; exception → reference.md §3 |
| Invented subtotal measure names | Breaks refresh silently | Verify against TMDL; missing → `dax-measures` |

## Verify before done

JSON parses → key is `pivotTable`, card values are ARRAYS → hierarchy fields/measures exist
in model → `altTextColumns` set, contrast ≥ 4.5:1 → `git diff` clean. Stepped indentation,
expand state, heatmap gradient aren't verifiable headless — say so.
