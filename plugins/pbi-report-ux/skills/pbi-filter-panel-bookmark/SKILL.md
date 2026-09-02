---
name: pbi-filter-panel-bookmark
description: Use when a page's slicers should collapse into one bookmark-toggled overlay group instead of a permanent slicer column - panel layout sizing, the filter button with a PNG icon, the show/hide bookmark pair, group visibility and bookmark scoping in PBIR enhanced. Do NOT trigger for slicer type choice or styling (pbi-slicers-filter-panel), PBIR-Legacy report.json bookmarks (powerbi-bookmarks), page switching (pbi-navigation-tabs), or registering the PNG as a resource (pbi-headers-icons-imagery). Triggers - 'collapsible filter panel', 'overlay filter panel', 'toggle filter panel', 'bookmark panel', 'toggle slicers', 'hide slicers', 'filter button', 'згорнута панель фільтрів', 'панель фільтрів, що ховається', 'кнопка фільтрів', 'сховати слайсери', 'показати/сховати фільтри', 'слайсери в букмарку'.
---

# Filter Panel as a Bookmark-Toggled Overlay

One hidden group holds every page slicer; a PNG-icon button toggles it via bookmarks.
PBIR **enhanced** only; Legacy → powerbi-bookmarks.

Pre-flight: read a Desktop-emitted group, `actionButton`, bookmark **of this report**.
**GT proves only what it contains**; the schema shows the *expressible*, a render the *honored*.

## Anatomy

| Part | Load-bearing fact |
|---|---|
| Group, own `visual.json` | `visualGroup` + top-level `"isHidden": true` = closed |
| Members via `parentGroupName` | **relative to the group box** |
| Backdrop `shape`, lowest `z` | else the page shows through |
| Opener `actionButton` **outside** | inside, it hides itself |
| `visualContainerObjects.visualLink` | `'Bookmark'` + id; `'ClearAllSlicers'` — none |
| `<id>.bookmark.json` **+** `bookmarks.json` item | unregistered = invisible |

A lone `bookmarks.json` item is `{"name": "<id>"}`, **nothing else** — `displayName` there
stops the report opening. Open/close `suppressData`, reset `suppressDisplay`;
`targetVisualNames` = group name plus members.

## Layout — compute it, never eyeball it

Panel pixels hide the report: size from content; right-anchor; grow left/down.

Cells are **pixels per control, not slots**: dropdown 64 (24+32+8), between/range/relative-date
120, list/hierarchy/chiclet 144. Pack by y-cursor; `C=1` until page overflow, then split;
`W = 24 + 304·C`. Fill **column-major** by priority — time → scope/geo →
subject coarse-to-fine → status → display — tab order = reading path = priority; never
reorder to close a gap. Guards count decisions: `F ≤ 3` → inline; `F > 12` → filter pane.

**Minimums.** `T(pt)`: 10→40, 12→44, 14→48, 18→52, 24→64, rounded **up to 8**; a textbox needs `T`,
a button `T + 8`. Caption width `w >= max(88, ceil8(6*len + 48))` — floor masked a wrong constant.
An undersized slicer sheds parts SILENTLY (96 drops between's track; 64 → funnel icon).
A style shadow draws INSIDE: container = visible + L6/R6/T0/B4 (blur 20); the 8-grid governs
the VISIBLE rect, container may sit off-grid.

Formulas, invariants, examples → [reference.md](reference.md); engine → `filter_panel_layout.py`.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Group name absent from `targetVisualNames` | group id first, then members |
| Group `isHidden` put in `visualContainers` | `visualContainerGroups` |
| `show` toggle carrying a selector | bare `show`; values in `{"id":"default"}` |
| Cell sized to the tallest control | per-kind px 64/120/144 |
| A group inherits `*/*` container chrome | `visualGroup.objects.background` off |
| Peer buttons unequal width | always equal — same weight |
| `text.bottomMargin` on a plain caption | only with `leftMargin`, icon+label |
| Container `dropShadow` for elevation | style `objects.shadow`; container OFF |

## Verify before done

**Validate every changed file against its `$schema` before Desktop** — the loader *is* a
JSON-Schema validator (`pbir_schema_validate.py`; unpublished versions 404 → newest published).
Then the layout checker; `isHidden: true`; opener outside; icon registered. Headless can't
verify rendering — say so.
