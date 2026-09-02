---
name: pbi-navigation-variants
description: Use when the user wants to see several navigation options for a Power BI report and pick one before anything is built - the skill inventories the report's pages, renders PNG previews of 7 canonical navigation variants on the report's own canvas sizes and theme, lets the user choose exactly one, then builds the chosen menu on every visible page. Do NOT trigger for styling an already-chosen navigation or navigator JSON (use pbi-navigation-tabs), bookmark files and scope (use powerbi-bookmarks), button/action JSON (use pbi-buttons-actions), or Legacy visual JSON (use powerbi-visuals). Defaults - 7 variants V1-V7, previews via scripts/render_nav_previews.py, choice via AskUserQuestion, build via scripts/build_nav.py only after one explicit choice. Triggers - 'варіанти навігації', 'кілька варіантів меню', 'дай обрати навігацію', 'навігаційне меню на всіх сторінках', 'меню на кожній сторінці', 'navigation variants', 'nav menu options', 'зроби варіанти і я оберу', 'обрати навігацію з варіантів'.
---

# Navigation in variants — render, choose, build everywhere

## Overview

Users cannot pick navigation from prose — they pick what they can see. And a menu that
exists on one page is not navigation, it is a poster.

**Core principle:** previews are rendered PNGs of *this* report's pages in *its* theme;
the user picks exactly one of 7; the chosen menu then lands on **every** visible page.

## When to Use

- "Зроби варіанти навігації і дай обрати", new report needs a navigation concept,
  existing navigation reaches only part of the pages.
- NOT for: polishing an already-chosen nav (`pbi-navigation-tabs`), bookmark mechanics
  (`powerbi-bookmarks`), visual JSON mechanics (`powerbi-visuals`).

## Pre-flight (mandatory)

1. **Inventory from files:** visible vs hidden pages (tooltip / drillthrough / dev pages
   excluded from menus); canvas size **per page** — sizes often differ, and a cross-page
   menu must adapt per size, one absolute geometry is impossible; current navigation and
   the pages unreachable from it (that gap is the problem statement); theme palette and
   fonts — **exact hex codes read from the registered theme file**
   (`StaticResources/RegisteredResources/*.json` → `dataColors`), never a neighbouring
   shade from memory.
2. **Traps:** a logo-looking button is not necessarily "home" — read its action type
   (it may be ClearAllSlicers); page display names ≠ section names — group pages before
   drawing menus.
3. Pillow present (`python -c "import PIL"`); PNG icons → `icon-set-manager`.

## The 7 canonical variants

Adapt each to the real report (its groups, names, palette) — do not invent an eighth ad hoc.

| V | Layout | Wins when |
|---|---|---|
| V1 | Top tab bar (pill tabs, active state) | ≤ ~8 sections, wide canvases |
| V2 | Left rail, icon + label (~240px) | many sections, wide canvases, scanning by name |
| V3 | Left icon-only rail (~56px) + tooltips | canvas width is precious, icons are meaningful |
| V4 | Hub home with section cards + «home» button on every page | exploratory reports, few cross-jumps |
| V5 | Hamburger ☰ → bookmark overlay panel | canvas must stay clean; powerbi-bookmarks mechanics |
| V6 | Native `pageNavigator` strip | pages change often — it syncs itself; limited styling |
| V7 | Grouped top bar: sections + sub-tab row | two-level hierarchy (group → page) |

## Two more design axes (decided per report, not hardcoded)

**Selected-state style** — how the current section is marked. The palette of signals:

| S | Signal | Notes |
|---|---|---|
| S1 | Fill (pill/card filled, inverted text) | strongest; default for V1/V4/V7 |
| S2 | Indicator bar (3–4px underline / left edge bar) | quiet; default for V2/V3/V6 |
| S3 | Font weight (Semibold/Bold vs Regular) | never alone — pair with S1/S2/S4 |
| S4 | Text/icon color accent | **color alone is not a signal** (accessibility) — always pair with another cue |
| S5 | Fill + weight combo | for dense menus where the fill is subtle |

Guardrails: the selected cue must survive greyscale (route `pbi-color-accessibility`);
selected text vs its background ≥ 4.5:1; every page's menu differs from its neighbours
in exactly one item's state — never one frozen "selected" replicated everywhere.

**Section icons** — each menu item may or may not carry a PNG icon:

- Sourcing/generation by name → `icon-set-manager` (find-or-fetch, brand color, 64px,
  transparent PNG); never hotlink random images.
- Modes: no icons / icon + label / icon-only (V3 requires icons; V6 cannot have them —
  native pageNavigator does not render custom icons).
- Selected item's icon may swap to the accent-colored variant — as a *paired* cue (S4 rule).

## Phase 1 — render PNG previews

`scripts/render_nav_previews.py --config <cfg.json>` — config carries the **recon
values**, never defaults: real page names, per-page canvas sizes, theme palette, font
with Cyrillic glyphs, hero page, `selected_style` (S1–S5) and `icons` mode (with icon
file paths when available). Each variant is rendered with its *recommended* selected
style and icon mode from the tables above — opinionated defaults, not all 84 combinations.
One PNG per variant into `previews/`. Send all 7 to the user (SendUserFile, render) —
the PNGs themselves, not links — together with a short written recon note (visible /
hidden counts, unreachable pages, action-type traps found): decisions must leave an
audit trail beyond the render config.

## Phase 2 — the choice (two decisions, not one)

1. **Layout:** `AskUserQuestion`, 7 variants in two rounds (4 + 3); labels
   `V1 — top tab bar`, descriptions = wins-when + effort.
2. **Refinement round** for the chosen layout: selected-state style (S1–S5, with the
   recommended one first) and icons (none / icon + label / icon-only where applicable).
3. Render **one final PNG** of the chosen combination and confirm it before Phase 3 —
   the user approves what will actually be built, not a memory of it.

"Reply with a letter somewhere" is not a selection mechanism. Headless / user away →
deliver PNGs + table and **stop**: implementing without an explicit choice is forbidden.

## Phase 3 — the menu on every page

1. Build the chosen menu **once**, on a reference page; verify in Desktop
   (bridge reload, passive) before replicating.
2. Replicate to **all visible pages**: geometry adapted per canvas size; the item for the
   current page carries the *selected* state on that page (each page's menu differs in
   exactly that one state); consistent z-order and tabOrder.
3. Hidden pages get no menu; drillthrough pages keep their back-button pattern instead.
4. Build with `scripts/build_nav.py --report <X.Report> --config cfg.json --apply` (same
   config as the previews; V1/V2/V3/V6/V7 emitted, V4/V5 documented as manual) — it writes
   one navigation group per visible page, adapts geometry per canvas size, marks the own
   page as selected and prints a coverage report; see reference.md.
5. Mechanics by name: button/action JSON → `pbi-buttons-actions`; navigator JSON and
   state styling → `pbi-navigation-tabs`; overlay show/hide + bookmark scope →
   `powerbi-bookmarks` (panel pattern → `pbi-filter-panel-bookmark`); icons →
   `icon-set-manager` policy; tokens → `pbi-design-system`; Legacy → `powerbi-visuals`.

## Common Mistakes

| Mistake | Fix |
|---|---|
| 3–4 prose variants instead of 7 rendered | 7 canonical, one PNG each, real names and colors |
| HTML mockup / artifact link when PNGs were asked | `render_nav_previews.py`; send the PNG files |
| "Answer with a letter in chat" | `AskUserQuestion`, single explicit choice |
| Recon delivered as the result | Phase 3 is the deliverable once a choice exists |
| Menu on some pages / identical selected state everywhere | replicate per page, per-size geometry, own-page highlight; count check |
| Logo assumed to be a home button | read the button's action type first |
| One geometry pasted onto different canvas sizes | per-size adaptation planned in pre-flight |
| Selected section marked by color alone | pair color with fill/underline/weight (greyscale test) |
| Icons hotlinked or invented ad hoc | `icon-set-manager` find-or-fetch, brand color, PNG |
| Built from the variant PNG, skipping the refinement round | selected-style + icons confirmed on a final combined PNG first |

## Verify before done

- [ ] `previews/` holds exactly 7 PNGs — one per variant, never more, never fewer;
      real page names and theme colors visible in each.
- [ ] The user's single explicit choice is recorded (or the headless stop is documented).
- [ ] The final combined PNG (layout + selected style + icons) was rendered and confirmed
      before any file was touched.
- [ ] Menu present on **every** visible page — grep/count equals the visible-page count.
- [ ] On each page the selected state points to that page, not to one frozen page.
- [ ] No geometry overlap with existing visuals (checked from files, not by eye).
- [ ] Where-to-look line delivered: which pages changed and what to press.
