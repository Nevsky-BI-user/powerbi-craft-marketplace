---
name: pbi-mobile-layout
description: Use when designing a Power BI report's Mobile layout (phone canvas) - which visuals to include, touch-target sizing, vertical flow, hiding desktop-only visuals. Do NOT trigger for desktop layout (pbi-page-layout) or visual JSON mechanics (powerbi-visuals). Triggers - 'mobile layout', 'phone view', 'мобільна версія', 'мобільний вигляд', 'адаптація під телефон', 'мобільна розкладка'
---

# Power BI Mobile Layout

## Overview

Desktop's **View → Mobile layout** toggle curates a phone-portrait canvas from the SAME
desktop visuals — a SECOND view state of one report (shared model/filters), resized or
omitted, never a separate small page. Design decision only; `layouts[]` JSON → SUB-SKILL
`powerbi-visuals`. Formats PBIR-Legacy/enhanced, TMDL. Sibling `pbi-page-layout`.

## When to Use

Phone-canvas visual selection, order/size, touch targets, filters.
**NOT for:** desktop grid math (`pbi-page-layout`), `layouts[]` JSON mechanics
(`powerbi-visuals`), tab/panel visibility (`powerbi-bookmarks`), chart-type choice
(`pbi-visualization-strategy`).

## Pre-flight (mandatory)

1. Read the desktop page's visual inventory — mobile is a curated SUBSET.
2. A second `layouts[]` entry (`id` ≠ 0) = a phone layout exists — read as ground truth.
3. Reuse the desktop theme palette; no mobile-only colors.

## Quick Reference

| Token | Value |
|---|---|
| Canvas | 323 pt max width, portrait; full-width = 323 pt (margin auto-included); height scrolls, no fixed cap (MS Learn) |
| Content budget | 1 hero KPI + 1–2 supporting |
| Layout | Single column, full width, portrait only — no side-by-side/landscape |
| Gaps | ≥ 6–8 pt between visuals (MS floor) |
| Touch target | ≥ 44×44 px (HIG/Material floor) |
| Typography | `pbi-design-system` §2; hero → `type/callout-hero` 28 pt |
| Filters | Native app Filter pane; ≤ 1 full-width slicer |

## Content, flow and the `layouts[]` id

Rank by hero-KPI hierarchy (`pbi-design-system` §3.4): the most decision-relevant number is hero,
plus 1–2 supporting visuals. Dense tables, decorative shapes, wide multi-series charts — leave
off, don't shrink illegibly. Order = priority (hero first); `tabOrder` mirrors the stack.
Enhanced PBIR stores the phone state as a per-visual `mobile.json` sibling (schema
`visualContainerMobileState/2.5.0`); Legacy keeps a 2nd `layouts[]` entry. Either way generate
it in Desktop and read back — never invent coords/`id`. Shapes → reference.md.

## Common Mistakes

| Mistake | Why bad | Fix |
|---|---|---|
| Shrank/cloned desktop page as "mobile" | Small desktop page, not the phone state | View → Mobile layout toggle; curate to hero KPI + 1–2 visuals |
| Side-by-side visuals | Cramped at arm's length | Single column, stack vertically |
| Reused 32 px hit target | Fat-finger mis-taps | ≥ 44×44 px on mobile controls |
| Full filter rail on 323 pt | Eats the screen | Native Filter pane; one slim slicer max |
| Landscape mobile design | Not an authored surface | Portrait only; desktop layout applies |

## Verify before done

Desktop inventory read first → mobile = curated subset, not a resized page → single column,
width 323 pt, heights ≥ MS minimums → touch targets ≥ 44×44 px → phone `id` from a real
example, never invented → `git diff` matches intent. Phone-canvas rendering can't be verified
headless — say so.
