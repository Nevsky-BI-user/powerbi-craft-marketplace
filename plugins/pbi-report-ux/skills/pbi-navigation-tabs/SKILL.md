---
name: pbi-navigation-tabs
description: "Use when designing or building in-report navigation for Power BI reports: tab bars, page vs bookmark navigation choice, button states (default/hover/selected), breadcrumbs. Do NOT trigger for bookmark/visibility JSON mechanics (powerbi-bookmarks) or drill-through back button (pbi-drillthrough). Triggers - 'navigation', 'tab bar', 'tabs', 'page navigator', 'bookmark navigator', 'breadcrumb', 'навігація', 'таби', 'вкладки', 'меню звіту', 'перемикання сторінок', 'хлібні крихти'."
---

# Navigation & Tab Bar Design

## Overview

Navigation answers "where am I, where can I go": one persistent tab strip, an unmistakable selected state. Decides pattern, placement, states; JSON wiring delegated (powerbi-bookmarks, powerbi-visuals). Formats: PBIP — PBIR-Legacy (`report.json`) or PBIR enhanced (`definition.pbir` + pages).

## When to Use

- Adding/redesigning a tab bar, nav menu, breadcrumb; choosing page vs bookmark navigation.
- Fixing inconsistent or invisible active-tab states.

NOT for: bookmark JSON (powerbi-bookmarks), drill-through back button (pbi-drillthrough), filter toggle (pbi-slicers-filter-panel), icons (icon-set-manager).

## Pre-flight (mandatory)

Detect format; read the nav group or an `actionButton` as ground truth, never from memory. Read page `width/height`; resolve `ThemeDataColor`; list every nav target.

## Quick Reference (tokens from `pbi-design-system`)

| Element | Spec |
|---|---|
| Nav strip | Full width × 40 px, top of page; identical x/y/size every page |
| Tab button | 96–200 × 32; hit ≥ 32×32; label `type/label`, sentence case |
| States | default transparent + `color/text-secondary`; hover `color/hover-tint`; selected `color/brand` fill + `color/text-inverse` + Semibold; disabled `color/text-disabled` |
| a11y | Nav first in `tabOrder`; alt text; contrast ≥ 4.5:1 |

Icon sizing, left-rail variant, breadcrumb spec, legacy grid → [reference.md](reference.md).

## Choosing the Pattern (F7)

| Tabs switch… | Use | Why |
|---|---|---|
| Report pages | `pageNavigator` | Auto-selected state |
| Views in one page | `bookmarkNavigator` + group | Scope gotcha → powerbi-bookmarks |
| No navigator fits | `actionButton` row (last resort) | → powerbi-bookmarks |
| Hierarchy location | Breadcrumb (below) | Orientation, not switching |

Theme keys: `actionButton`, `pageNavigator`, `bookmarkNavigator` (theme-visuals §5).

**pageNavigator (PBIR visual.json):** `layout.orientation` carries NO selector; schema `2.10.0`, `howCreated: "InsertVisualButton"`, `drillFilterOtherVisuals: true`. Author in Desktop, read as ground truth.

## Theme Block — Style Once (A7)

`$id` enum: `default | hover | selected | disabled` — no `press` (per-visual only). Values are ARRAYS; copy names from a real file, never memory (F2).

```json
"actionButton": {
  "*": {
    "fill": [
      { "$id": "default", "show": false },
      { "$id": "selected", "show": true, "fillColor": { "solid": { "color": "#063E61" } } }
    ]
  }
}
```

Same pattern styles `text`/`border`. Full 4-state block → reference.md §1.

## Common Mistakes

| Mistake | Why bad | Fix |
|---|---|---|
| Hand-made page-switch buttons | Reinvents selected-state logic | `pageNavigator`/`bookmarkNavigator` |
| Selected shown by color alone | Fails grayscale/colorblind | Brand fill + Semibold/underline |
| `"$id": "press"` in theme | Not in enum, ignored | Four states only |
| Breadcrumb as tabs in a textbox | Antipattern A10 | Separate buttons, plain text |
| Invented bookmark/button options | Fails silently | Ground truth + powerbi-bookmarks |
| pageNavigator state id `interaction:*`/`selection:*` | Silently kills ALL tiles | Id EXACTLY `default`/`selected` |
| `visualContainerObjects.title` on pageNavigator | Removes every tile | Title in separate textbox |

## Verify before done

JSON parses → every nav target exists → coordinates identical across pages → tabOrder/alt text set → contrast checked. Rendering can't be verified headless — flag it.
