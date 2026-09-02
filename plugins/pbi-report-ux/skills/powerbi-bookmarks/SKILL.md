---
name: powerbi-bookmarks
description: >
  Bookmarks and visual visibility in Power BI reports, both formats — PBIR
  enhanced (definition/bookmarks/*.bookmark.json + bookmarks.json) first,
  PBIR-Legacy report.json as appendix: tab switching inside a page, group
  isolation, show/hide visuals and groups, captured filters that must survive
  a click, bookmark groups for navigators, the options/targetVisualNames scope
  gotcha, bookmarks.json anyOf, schema validation. Trigger on: "закладки",
  "букмарки", "букмарка", "стан сторінки", "перемикання виглядів",
  "сховати групу", "показати/сховати візуали", "вкладки на одній сторінці",
  "bookmark", "bookmarks.json", "tab isolation", "block leaks onto other
  tabs", "bookmark group". Do NOT trigger for: a collapsible slicer panel end
  to end (pbi-filter-panel-bookmark); button and action-link JSON
  (pbi-buttons-actions); tab-bar design, states and navigator visuals
  (pbi-navigation-tabs); choosing a navigation variant
  (pbi-navigation-variants); Legacy visual creation or field binding
  (powerbi-visuals).
---

# Power BI bookmarks & visibility — PBIR first, Legacy appendix

## Overview

A bookmark is a saved page state plus a scope (`options`). Two things break
most reports: an id touched in the state but absent from the scope (silently
ignored), and a `bookmarks.json` item that is neither a leaf nor a group (the
report does not open). This skill owns the bookmark files and the visibility
model; depth per format: PBIR → `references/pbir-bookmarks.md`, Legacy →
`reference.md` (+ byte-faithful harness `pbir.py`).

## When to Use

- Show/hide a visual or group per tab, isolate a block to one tab, keep a
  hidden filter alive across tab clicks, author a bookmark group for a
  navigator, register a new bookmark, fix "block leaks onto other tabs".
- NOT for: the slicer overlay panel as a whole (`pbi-filter-panel-bookmark`),
  wiring buttons (`pbi-buttons-actions`), nav design (`pbi-navigation-tabs`).

## Pre-flight — detect the format

| Evidence | Format | Files you edit |
|---|---|---|
| `definition/bookmarks/` exists, `definition.pbir` version ≥ 4.0 | **PBIR enhanced** | `<id>.bookmark.json`, `bookmarks.json`, `visual.json` |
| single `report.json` with `sections[]` and stringified `config` | PBIR-Legacy | `report.json` via `pbir.py` |

Never mix: the formats are mutually exclusive per report.

## ⚠️ THE #1 GOTCHA — `options.targetVisualNames` (both formats)

```json
"options": { "applyOnlyToTargetVisuals": true, "targetVisualNames": ["<groupId>", "…"], "suppressData": true }
```

With `applyOnlyToTargetVisuals: true` the bookmark applies its captured state
**only** to ids in `targetVisualNames`. An id you set in `explorationState`
but forgot to list is silently ignored — the tab looks empty and nothing
errors. **Rule: any id you touch in the state MUST be in that bookmark's
`targetVisualNames`; the group's own id goes first.** Generate the list from
the files (`references/pbir-bookmarks.md` §3), never by hand.

## PBIR enhanced — the six laws

1. Group visibility lives **only** in `explorationState.sections.<page>.visualContainerGroups.<id>.isHidden`;
   a single visual hides with `visualContainers.<id>.singleVisual.display.mode: "hidden"`
   (enum: `maximize | spotlight | elevation | hidden`).
2. `options` are four switches: `applyOnlyToTargetVisuals`, `suppressData`
   (display-only — tab clicks must not reset the reader's slicers),
   `suppressDisplay` (data-only — "reset filters"), `suppressActiveSection`
   (don't switch page). Both suppress flags together = a bookmark that does nothing.
3. `bookmarks.json` items are **exactly** `{"name"}` (leaf) or
   `{"name","displayName","children"}` (group). A leaf with `displayName`
   breaks the report (incident І-22). The label lives inside the bookmark file.
4. A `.bookmark.json` not listed in `bookmarks.json` does not exist for Desktop.
5. Captured filters are a payload per targeted visual: adding a filter to a
   visual means patching the captured card in every bookmark that targets it.
6. The schema is the gate: `python scripts/pbir_schema_validate.py <X.Report>`
   before Desktop; the plugin hook runs the cheap subset on every edit.

## Legacy (`report.json`) — non-negotiable rules

- Never naïve `json.load`→`dump` (float/CRLF/BOM normalisation = thousands of
  diff lines) — always `pbir.py` → `reference.md` §5.
- Geometry is stored twice — use `pbir.set_position(...)`; acceptance reads
  `cfg['layouts'][0]['position']` → `reference.md` §7.
- Property placement: copy a working instance, never invent → `reference.md` §8.
- Close Power BI Desktop **without saving** before editing, reopen after.

## Symptom → cause

| Symptom | Cause / fix |
|---|---|
| New block never shows on its tab | group id missing from that bookmark's `targetVisualNames` |
| Block leaks onto other tabs | other tabs' bookmarks don't hide it: `isHidden:true` **and** the id in their list |
| One visual leaks while the rest isolate | it lost `parentGroupName` — restore it |
| Report won't open after adding a bookmark | `bookmarks.json` item is a leaf with `displayName`, or a group missing `children` |
| Button click does nothing | bookmark not indexed, or scope excludes the touched ids |
| Tab click resets the reader's slicers | tab bookmarks lack `suppressData: true` |
| Hidden filter dies on first tab click | captured card not patched in bookmarks that target the visual |
| Edit doesn't appear in Desktop | Desktop was open — close without saving, reopen |

## Workflow

1. Detect format; back up the files you will touch.
2. PBIR: write `<id>.bookmark.json` (state + `options`), register it in
   `bookmarks.json` in the right shape, wire the button
   (`pbi-buttons-actions`). Legacy: `pbir.py`, ids unique 20-hex.
3. For **every** bookmark you touch: state **and** `targetVisualNames`.
4. Validate: `pbir_schema_validate.py` (PBIR) / diagnostic snippet (Legacy).
5. Reopen Desktop; verify the switch both ways on every affected tab.

## Reference map

- `references/pbir-bookmarks.md` — §1 files · §2 bookmark file · §3 options ↔ UI
  · §4 `bookmarks.json` anyOf and І-22 · §5 groups · §6 the four panel
  bookmarks · §7 verification · §8 sources.
- `reference.md` (Legacy) — §1 visibility model · §2 captured filters · §3 tab
  isolation · §4 placeholders/z-order · §5 `pbir.py` · §6 diagnostics ·
  §7 geometry twice · §8 property placement.
