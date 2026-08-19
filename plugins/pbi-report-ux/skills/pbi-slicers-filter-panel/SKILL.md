---
name: pbi-slicers-filter-panel
description: Use when adding or restyling Power BI slicers or building a filter panel - choosing slicer type (dropdown/list/button-tile/between/text), unifying sizes and styles, a bookmark-toggled panel, clear-all button, or showing applied filters. Do NOT trigger for bookmark mechanics (powerbi-bookmarks), visual JSON edits (powerbi-visuals), or theme generation (pbi-theme-json). Triggers - 'slicer', 'filter panel', 'зріз', 'слайсер', 'панель фільтрів', 'скинути фільтри', 'застосовані фільтри'
---

# Slicers & Filter Panel

## Overview

Filters are chrome, not data: quiet, uniform, predictable, unmistakable selection, clear applied-filter feedback.

Formats: PBIP, PBIR-Legacy or PBIR enhanced; TMDL model. Sub-skills: powerbi-visuals (slicer/button JSON), powerbi-bookmarks (show/hide), icon-set-manager (filter icon), dax-measures.

## When to Use

Adding/unifying slicers, a filter panel/strip, clear-all, applied-filter indication.
NOT for: bookmark/visibility JSON (powerbi-bookmarks), visual JSON (powerbi-visuals), whole-theme authoring (pbi-theme-json), tab navigation (pbi-navigation-tabs).

## Pre-flight (mandatory)

1. Detect format; read an existing slicer of THIS report as ground truth, not memory.
2. Read page `width/height` (legacy 1440-wide → tokens §7); resolve theme palette.
3. Verify slicer fields exist in the TMDL model.

## Quick Reference

| Data / need | Visual (exact key) | Notes |
|---|---|---|
| 2–8 categories, button tiles | `slicer` classic, `data.mode: 'HorizontalList'` | NOT `advancedSlicerVisual` — renders empty tiles hand-authored |
| >8 categories | `slicer` (classic), Dropdown style | enable search when long |
| Medium list in a panel | `listSlicer` (new; classic List for legacy) | vertical |
| Date / numeric range | `slicer` (classic), Between | style `date`/`numericInputStyle` on dark; ≥120px height, not a dropdown's 64px |
| Free-text contains | `textSlicer` | |

Theme all four keys for coverage, but **hand-author slicers as classic `slicer`** (§1/§4) — never `advancedSlicerVisual`. On dark themes, style `items`/`date`/`numericInputStyle` `fontColor`+`background` or slicers render white-on-white. Mode is per-visual: clone a ground-truth slicer.

## Patterns

**Filter panel:** ≤4 slicers → top strip under title; more → 200 px panel (rail via pbi-page-layout, or bookmark-toggled) — reference.md §2; scope via `targetVisualNames` (powerbi-bookmarks).

**Clear-all & applied indication:** `actionButton`, built-in "Clear all slicers" action, ghost style; fallback: default-state bookmark. Closed panel → badge: ISFILTERED-count on toggle (dax-measures). Filter pane `filterCard` (Applied ≠ Available) → reference.md §3.

## Common Mistakes

| Mistake | Why bad | Fix |
|---|---|---|
| Only `slicer` styled in theme | list/button/text slicers unstyled | Cover all four keys (reference.md §1) |
| Selection shown by color alone | fails colorblind (F9) | `color/selection-tint` + bold/check |
| Panel bookmarks w/o `targetVisualNames` | resets unrelated visuals | Scope to panel group (powerbi-bookmarks) |
| Hand-built clear-all from N bookmarks | obsolete (F7) | Built-in "Clear all slicers" action |
| `advancedSlicerVisual` hand-authored | renders empty tiles | Classic `slicer` + `HorizontalList` (reference.md §1) |
| `items`/`date`/`numericInputStyle` unstyled on dark | white-on-white | Set `fontColor`+`background` per mode |
| Between slicer at dropdown height | `responsive` sheds parts silently: 96px drops the TRACK, 64px leaves a funnel icon | Give ≥120px, or disable `responsive` |

## Verify before done

JSON parses → fields exist in model → all four theme keys covered → `targetVisualNames` lists exactly the panel visuals → hit ≥ 24 px, tabOrder, alt text → `git diff` matches intent. Rendering is unverifiable headless — state this.
