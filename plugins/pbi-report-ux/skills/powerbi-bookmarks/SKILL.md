---
name: powerbi-bookmarks
description: Safely edit Power BI PBIR-Legacy report.json bookmarks and visual visibility — tab switching, group isolation, show/hide visuals, drill-through pages. Use when adding a visual/group that must appear only on one tab, fixing "block doesn't show on its tab" / "block leaks onto other tabs", wiring tab navigation, or any report.json bookmark/visibility edit. Covers the critical options.targetVisualNames scope gotcha, the visualContainerGroups/visualContainers isHidden model, and byte-faithful editing of report.json.
---

# Power BI bookmarks & visibility (PBIR-Legacy report.json)

## Overview

Editing bookmarks by hand in `report.json` is fragile. This skill encodes the mental model and the **one gotcha that breaks everything**, plus a byte-faithful editing harness. The harness is `pbir.py` in this skill folder; depth — visibility model, filter captures, tab isolation, diagnostics — lives in [reference.md](reference.md).

## When to Use

- Any PBIR-Legacy `report.json` bookmark/visibility edit: tab switching, group isolation, show/hide visuals, hidden filters that must survive tab clicks, placeholders, z-order.
- NOT for: creating/styling visuals or binding fields → `powerbi-visuals`; PBIR **enhanced** filter-panel bookmark pairs → `pbi-filter-panel-bookmark`; tab-bar design and button states → `pbi-navigation-tabs`.

## ⚠️ THE #1 GOTCHA — `options.targetVisualNames`

Every bookmark has:
```json
"options": { "targetVisualNames": ["id1","id2",...], "applyOnlyToTargetVisuals": true, "suppressData": true }
```
When `applyOnlyToTargetVisuals: true`, the bookmark **applies its captured visibility ONLY to visuals/groups whose id is in `targetVisualNames`.** Anything not in that list is left untouched.

**Consequence:** if you add a new visual or group and set its `isHidden` inside `explorationState`, **it is silently ignored** unless you ALSO add its id to `options.targetVisualNames`. The visual then falls back to its own config default (`singleVisualGroup.isHidden` / `display.mode`).

> Symptom: "I set the group visible in the Навч bookmark but the tab is empty." → the group id is missing from `targetVisualNames`.

**Rule: any id you touch in `explorationState` MUST also be in that bookmark's `options.targetVisualNames`.**

## Non-negotiable rules

- **Hidden filters**: after adding/changing a filter on a visual, patch the captured card in EVERY bookmark whose `targetVisualNames` contains that visual — copy the body from the live card, never retype it. A clean live diff proves nothing about surviving a tab click → reference.md §2.
- **Filters and visibility are ONE payload** per targeted visual: you cannot add a visual to `targetVisualNames` just to control its filter — its captured `display` state starts applying too → reference.md §2.
- **Editing**: never naïve `json.load`→`dump` (float/CRLF/BOM normalization = thousands of diff lines). Always use `pbir.py` → reference.md §5.
- **Geometry is stored TWICE**: never assign it by hand — use `pbir.set_position(...)`; any acceptance check MUST read `cfg['layouts'][0]['position']`, never the 2-decimal mirror → reference.md §7.
- **Property placement**: never invent one — Desktop's save-linter silently strips wrong placements. Copy a working instance from report.json, or have the user toggle it in Desktop and read the diff → reference.md §8.
- **Power BI Desktop**: close WITHOUT saving before editing, reopen after — it caches bookmark state and will overwrite your JSON on save.

## Symptom → cause

| Symptom | Cause / fix |
|---|---|
| New block never shows on its tab (tab empty) | group id missing from `options.targetVisualNames` of that bookmark |
| Block leaks onto other tabs | other tab bookmarks don't hide it: add `isHidden:true` **and** the id to their `targetVisualNames` |
| ONE visual (e.g. a title) leaks onto every tab while the rest isolate fine | that visual lost its `parentGroupName` (often when a container was rebuilt) → it's now a top-level orphan, not covered by the group's bookmark cascade. Restore `parentGroupName` to put it back in the group |
| Block covered by "В розробці" / blank box | a higher-`z` placeholder is shown; hide it in that bookmark or raise block `z` |
| Whole `report.json` diff is huge after a 1-line edit | didn't use byte-faithful save (float/CRLF/BOM normalization) |
| Moved/resized a visual, committed, **canvas unchanged** | wrote only the container mirror (`vc['x']…`) and not `cfg['layouts'][0]['position']` — see reference.md §7 |
| Edit doesn't appear in Desktop | Desktop was open during edit — close WITHOUT saving, reopen |
| Hidden filter works on page load, gone after clicking a tab | bookmarks that target the visual replay a captured card with no `filter` body (or no card) — patch every such capture, see "A new filter on a visual dies on the first tab click" (reference.md §2) |

## Workflow checklist

1. Back up `report.json` → `report.json.bak` before first edit.
2. Make the edit with `pbir.py`; keep ids unique (20-hex).
3. For **every** bookmark you touch: set `explorationState` state **and** add the id to `options.targetVisualNames`.
3b. If the change is a **filter** on a visual, patch the captured card in every bookmark that already targets that visual (see the filter gotcha) — a clean live diff does not mean the filter survives a click. → reference.md §2
4. Validate: JSON reloads, diff localized, run the diagnostic snippet (all touched ids `inTarget=True`). Snippet → reference.md §6
5. **Close Power BI Desktop WITHOUT saving**, then reopen `.pbip` (Desktop caches bookmark state and will overwrite your JSON on save).
6. Verify tab switching both ways (block shows on its tab, hidden on others).

## Reference map ([reference.md](reference.md))

§1 where bookmarks live + the visibility model (`explorationState`) · §2 captured filters (bookmark shape ≠ live; ghost scrubbing; the card-patch rule and its corollary) · §3 tab-isolation pattern (adding a new tab, steps 1–4) · §4 placeholders («В розробці») and z-order · §5 byte-faithful editing with `pbir.py` · §6 diagnostic snippet + filter variant · §7 geometry stored twice · §8 visual-property placement (linter strips) · §9 related (project CLAUDE.md, measure-driven SVG visuals).
