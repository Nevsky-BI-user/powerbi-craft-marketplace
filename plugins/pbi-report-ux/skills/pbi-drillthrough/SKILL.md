---
name: pbi-drillthrough
description: Use when designing or reviewing a Power BI drill-through detail page — back button, context header with the drilled value, keep-all-filters decision, linking source visuals. Do NOT trigger for tooltip pages (use pbi-tooltips), tab navigation (use pbi-navigation-tabs), JSON mechanics (use powerbi-visuals). Triggers - 'drill through', 'drillthrough', 'detail page', 'back button', 'деталізація', 'сторінка деталізації', 'кнопка назад', 'дрілтру'
---

# Drill-through Page Design

## Overview

A drill-through page is a hidden detail view from one data point: **what entity, what filters, how back**. This skill owns the design; JSON mechanics → powerbi-visuals (BRIEF §4). Formats: PBIP; **PBIR-Legacy** (`report.json`) or **PBIR enhanced** (`definition/pages/**`); TMDL model.

## When to Use

Creating/redesigning a Drill-through page (entity 360°, transaction detail), or fixing its back button, context header, or drill fields.

**NOT for:** hover detail (`pbi-tooltips`), persistent navigation (`pbi-navigation-tabs`), hierarchy drill-down, JSON writing (`powerbi-visuals`).

## Pre-flight (mandatory)

1. Detect format; read an existing drill-through page as ground truth, never from memory (markers: reference.md §1).
2. Read the actual `width/height` (PDP: 1440×720, DESIGN-TOKENS §7); resolve `ThemeDataColor`.
3. Verify every drill field exists in the model; missing measures → `dax-measures`.

## Quick Reference (tokens from DESIGN-TOKENS.md)

| Element | Spec |
|---|---|
| Page | Hidden; source's canvas + theme |
| Back button | Top-left `actionButton` (`Back`), ≥ 32×32, states §5, tabOrder first |
| Header | `type/hero` / `color/text-title`, DAX-bound |
| Context line | `type/small` / `color/text-secondary`, filter summary |
| Keep all filters | ON by default, else own context |
| Drill fields | One grain/page; every source-visual field |
| Body | KPI → trend → table (F-pattern, §3 grid, 8-px snap) |

## Context header — the one pattern

```dax
Drill Header =
"Customer — "
    & SELECTEDVALUE ( Customer[Customer Name], "no selection — open via right-click → Drill through" )
```

Bind to the title (mechanics: powerbi-visuals; conventions: dax-measures); the fallback doubles as the empty state.

## Source linkage

Right-click drill-through is invisible — hint at it: a caption, or a drillthrough `actionButton` (disabled until one value is in context; `pageNavigator` for "the whole list" — `pbi-navigation-tabs`, reference.md §2).

## Common Mistakes

| Mistake | Why bad | Fix |
|---|---|---|
| Static title ("Details") | Context unknown | SELECTEDVALUE measure |
| No / buried back button | Dead-end page | Top-left, ≥ 32 px, tabOrder first |
| Page visible in nav | Lands unfiltered | Hide + fallback header |
| Keep-all-filters OFF silently | Numbers ≠ source | Keep ON, or show context |
| Drill button for lists | Disabled w/o a value | `pageNavigator` instead |
| Invented filter JSON | Fails silently | Clone truth; powerbi-visuals |
| New hex, ad-hoc sizes | Theme drift | Tokens; `ThemeDataColor` |

## Verify before done

File parses → drill fields exist in model → back button present, tabOrder-first, alt-texted → header DAX-bound → `git diff` matches intent; note what can't be verified headless.
