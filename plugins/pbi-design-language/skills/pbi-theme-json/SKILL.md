---
name: pbi-theme-json
description: Use when creating, generating, or rebranding a Power BI report theme.json, or auditing whether a theme covers every visual type used in a PBIP project (PBIR-Legacy or PBIR enhanced). Do NOT trigger for one-visual formatting (powerbi-visuals), token values (pbi-design-system), pbir-CLI audit (reports:modifying-theme-json), non-PBI themes (theme-factory). Triggers - 'theme.json', 'тема звіту', 'кольори теми', 'дизайн-тема', 'згенеруй тему', 'visualStyles'.
---

# Power BI Theme JSON

## Overview

A theme sets **defaults only** — one file styles every visual (DESIGN-TOKENS.md §8). Ships [`assets/master-theme.json`](assets/master-theme.json): a full `reportThemeSchema` theme — `dataColors`, structural+text classes, all 48 visual-type keys (`theme-visuals.md` §5), plus `"*"`/`page`/pseudo-entries. Every hex/pt is a DESIGN-TOKENS.md token.

## When to Use

New report theme, rebrand, or audit theme coverage of every visual type used.

NOT for the description's four cases; font ramp → `pbi-typography`, icons → `icon-set-manager`.

## Quick Reference

| Task | Do this |
|---|---|
| New report, on-brand | Copy `master-theme.json`; find-replace token hexes (→ reference.md); keep keys |
| Rebrand | Read current theme first; replace only `dataColors`/structural/`textClasses` colors, not card names |
| Missing visual type | Copy that key's block from `master-theme.json`, never memory |
| Wire in (Legacy/enhanced) | Parse `config`/`definition/report.json`, set `themeCollection`, drop file in `RegisteredResources/` — recipe → reference.md §4 |
| Validate | JSON parses; every card value an array; keys match §5 verbatim |

Token-hex map, per-type coverage, pseudo-entries → [reference.md](reference.md).

## Common Mistakes

| Mistake | Why bad | Correct |
|---|---|---|
| Only `visualStyles."*"` block | Per-type cards unthemed | Explicit entry per type (48) |
| `matrix`/`table`/`smartNarrative` keys | Silently ignored (typo, no error) | `pivotTable`, `tableEx`, `aiNarratives` |
| `"title": {"show": true}` (object) | Commonest error | `"title": [{"show": true}]` — always an array |
| Styling only `columnChart` | Clustered/100%-stacked variants untouched | Theme all three |
| Mixing `firstLevelElements` + `foreground` | Both write the same slot | One convention only |
| Display name where schema wants an enum/int (`"Above"`, `"Horizontal"`, …) | PBI **rejects the whole theme** | Use the schema enum/int, not the label — reference.md §6 |
| Switching a card off at theme type level | Only INHERITING visuals change — 45/50 audited cards had it as their ONLY edge | Count inherit vs override first; per-visual > type > `*` |
| Expecting `visualStyles.group` to work | Runtime IGNORES it — a group inherits `*/*`; white background past a rounded backdrop reads as a "second frame" | `visualGroup.objects.background=[{properties:{show:false}}]` in the group's JSON |
| Light↔dark: recoloring only `dataColors`/`background` | Banding/headers/`total`/`subTotals`/grid stay light; base64 `page` wallpaper + `outspace transparency:100` have no hex to sweep | Recolor matched back+font pairs, grid→dark; regenerate/drop image; transparency→0; audit luminance. §7–8 |
| Inline base64 `background` with a stray `U+FEFF` BOM | Whole report won't open (invalid-value crash) | `base64.b64decode(payload, validate=True)` must pass; BOM can hide past byte 0 |

## Verify before done

File written → `json.load` parses → **schema-validate** (`jsonschema` vs `reportThemeSchema-2.155.json`, 0 errors) → every `visualStyles.<type>` key matches §5 → every card value an array → colors follow §1.7 → if wired, config parses + file exists in `RegisteredResources`. Rendering can't be verified headless.

Closes BRIEF F1, F2, F3, F4, F6, F7, F10.
