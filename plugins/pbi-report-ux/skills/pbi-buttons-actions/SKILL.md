---
name: pbi-buttons-actions
description: >
  Action buttons in PBIR (enhanced) Power BI reports — the visual.json of an
  actionButton with every action type (page navigation, bookmark, back,
  drillthrough, clear/apply all slicers, web URL), the five button states,
  icon + label anatomy with images from RegisteredResources, and the
  serialization law that makes Desktop drop a card. Trigger on: "кнопка
  переходу", "кнопка на сторінку", "json кнопки назад", "кнопка з іконкою", "дія
  кнопки", "кнопка скинути фільтри", "кнопка застосувати", "стани кнопки",
  "action button", "button action", "page navigation button", "back button
  json", "visualLink". Do NOT trigger for: navigator visuals and tab-bar design
  (pbi-navigation-tabs); bookmark files and scope (powerbi-bookmarks); finding
  or generating the icon PNG (icon-set-manager); registering resources and
  header imagery (pbi-headers-icons-imagery); Legacy report.json buttons
  (powerbi-visuals); the drillthrough page and its back-button design,
  "кнопка назад" (pbi-drillthrough).
---

# Buttons & actions (PBIR `actionButton`)

## Overview

A button is a `visual.json` with `visualType: "actionButton"`, formatting in
`objects` (icon/text/fill/outline/shape) and the action in
`visualContainerObjects.visualLink`. Every fact here is either ground truth
(GT — read from a real file) or schema; the full annotated GT file and the
per-action snippets live in `references/action-button.md`.

## Quick Reference — action ↔ required keys (`visualLink.properties`)

| Desktop action | `type` literal | Companion keys | Status |
|---|---|---|---|
| Page navigation | `'PageNavigation'` | `navigationSection: '<page name>'` | GT |
| Bookmark | `'Bookmark'` | `bookmark: '<bookmark name>'` (+ `navigationSection` if on another page) | GT |
| Drill through | `'Drillthrough'` | `drillthroughSection: '<page name>'` (+ `navigationSection`) | GT |
| Back | `'Back'` | none | GT |
| Clear all slicers | `'ClearAllSlicers'` | none | GT |
| Apply all slicers | `'ApplyAllSlicers'` | none | docs — verify literal in Desktop |
| Web URL | `'WebUrl'` | `url` | docs — verify key in Desktop |
| Q&A | `'QnA'` | none | docs — verify |
| Data function (Fabric user data function) | — | — | docs only, no JSON seen — capture from Desktop before use |

All literals are written as `{"expr":{"Literal":{"Value":"'PageNavigation'"}}}` —
single quotes inside the string. `show` toggles the action (`true`/`false`).
Page navigation is also allowed on `shape` and `image` visuals; the destination
can be measure-driven (Desktop: fx on **Destination**) — JSON not yet verified.

## The serialization law (incident І-14)

| Entry kind | Selector |
|---|---|
| `show` toggle (`icon.show`, `text.show`, `fill.show`, `outline.show`) | **none** — bare entry |
| Values (image, iconSize, text, fontColor, margins, fillColor) | `"selector": {"id": "default"}` |
| Another state | `"selector": {"id": "hover"}` … one entry per state |

A `show` with a selector, or a value without one, makes Desktop drop the whole
card and render the theme default. Units: `D` on doubles (`29D`), `L` on
integers (`30L`) — mixing them is a structure error.

## States

Microsoft lists five: **Default, On hover, On press, Disabled, Loading**.
Observed selector ids in GT: `default`, `hover`; navigators add `selected`.
Ids for press/disabled/loading are not yet observed — toggle the state in
Desktop and read the diff before writing them. Never write `interaction:*` or
`selection:*` ids (they silently kill navigator tiles).

## Icon + label anatomy

- Icon: `objects.icon[]` with `shapeType: 'custom'`, `image.url` as
  `ResourcePackageItem {PackageName:'RegisteredResources', PackageType:1, ItemName}`,
  `iconSize: 29D`, `horizontalAlignment: 'center'`; a second entry with
  `selector.id: 'hover'` may point at a different registered PNG (navy + white pair).
- Label: `text.show: true`, `text.leftMargin: 30L` clears the icon; icon-only =
  `text.show: false` (keep the caption properties — one flag restores it).
- Rounded corners: `objects.shape[].properties.roundEdge: 30L` (GT).
- The PNG must be registered in `report.json → resourcePackages` and exist in
  `StaticResources/RegisteredResources/` → `pbi-headers-icons-imagery` §9;
  which icon goes on which button → `icon-set-manager` policy.
- Live caption from a measure (`text.expr.Measure`) — set on both `default`
  and `hover`, else the caption changes on hover.

## Nav-button kit (sizes from `pbi-navigation-tabs`)

Tab button 96–200 × 32, hit area ≥ 32 × 32; back button top-left ≥ 32 × 32,
first in `tabOrder`; alt text mandatory on icon-only buttons; identical
geometry on every page (`pbi-navigation-variants` builds it).

## Common Mistakes

| Mistake | Why bad | Fix |
|---|---|---|
| `bookmark` key on a `'ClearAllSlicers'` link | Desktop drops the card | no companion key for built-in actions |
| `navigationSection` set to the page **displayName** | link resolves nowhere | use the page `name` (folder id) |
| Value entry without a selector | card dropped, theme default rendered | `"selector":{"id":"default"}` |
| `iconSize: 29L` | wrong unit = structure error | `29D` |
| Different geometry per page for the same button | menu "jumps" between pages | one geometry per canvas size |
| Inventing a state id | tiles vanish | read the id from a Desktop-emitted file |

## Verify before done

JSON parses → `visualLink.type` in the table → companion key present and its
target exists (page folder / `<name>.bookmark.json`) → every value entry has a
selector, every `show` has none → PNG registered → hook `check_report.py` silent
→ Desktop reload shows the click working. Full GT → `references/action-button.md`.
