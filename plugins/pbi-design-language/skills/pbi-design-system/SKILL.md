---
name: pbi-design-system
description: Use when choosing any design value for a Power BI report element in a PBIP project - colors, typography, spacing, grid, radius, interactive states, WCAG contrast - or when auditing a page/report for design-system compliance. Do NOT trigger for visual JSON mechanics (powerbi-visuals) or theme.json generation (pbi-theme-json). Triggers - 'design system', 'design tokens', 'дизайн-система', 'токени дизайну', 'кольори звіту', 'сітка', 'відступи', 'типографіка', 'єдиний стиль', 'чек-лист дизайну'.
---

# Power BI Design System

## Overview

Root pbi-* skill: every property maps to a `reference.md` token (`docs/DESIGN-TOKENS.md`);
siblings apply per element.

## When to Use

Picking any design value in PBIR-Legacy/enhanced report JSON or model TMDL — or auditing
a page.

Not for: JSON mechanics (`powerbi-visuals`), bookmarks (`powerbi-bookmarks`), theme.json
(`pbi-theme-json`), chart choice (`pbi-visualization-strategy`), icons (`icon-set-manager`),
narrative/claim wording (`data-storytelling`), web design (`frontend-design`).

## Quick Reference

| Decision | Tokens | Non-negotiable rule |
|---|---|---|
| Color | §1 | Roles, not hues: brand `#063E61`; AA text variants; 5 neutrals |
| Ramps / CF | §1.2–1.3 | Brand-tint sequential; diverging anchored at center; `ramp/rag` |
| Typography | §2 | Segoe UI only; pt ramp 28/18/14/12/10/9, floor 8; emphasis = Semibold |
| Layout | §3 | 8-px grid; 24 margin, 16 gutter; spacing scale 4/8/16/24/32 |
| Shape | §4 | One radius (8); never two edges; shadow = elevation, never default; style shadow draws INSIDE (grow container by its margins), container shadow outside |
| States | §5 | default/hover/selected/disabled; selected = brand fill + white text |
| Components | §6 | `cardVisual`/`tableEx`/`pivotTable`/`advancedSlicerVisual` — modern only |
| PDP edits | §7 | Keep its 1440 grid; navy via `ThemeDataColor ColorId 2` |
| Theme inversion | §1.9 | Neutrals mirror; accents DEEPEN (−400→−600/700, never mirror); audit luminance after sweep |

## Workflow

1. **Pre-flight**: detect format, verify `ThemeDataColor` mapping, read the real page size
   and a visual; map each property to a token (ask if none fits).
2. Emit colors per §1.7; reference the theme in JSON, never duplicate hex:

   ```json
   {"expr": {"ThemeDataColor": {"ColorId": 2, "Percent": 0}}}
   ```

3. Snap `x/y/width/height` to integer 8-px multiples; re-derive §3.3 on non-standard pages.
4. Theme conversion dark↔light → §1.9 **R1–R6**, all six.
5. Run the §9 checklist; cite evidence per item.

## Common Mistakes

| Mistake | Why bad | Correct |
|---|---|---|
| Hardcoding theme hex per visual | Drift (PDP: 173×) | `ThemeDataColor` / named color |
| Second navy in new work | Two brands, one page | One navy; `#063E61` for new |
| Eyeballed coordinates | Ragged grid, jitter | Integers, multiples of 8 |
| Mixed title sizes 10–13 pt | Broken hierarchy | `type/title` = 12 pt everywhere |
| Red/green as the only signal | Colorblind users lose meaning | Pair with icon/label; contrast ≥ 4.5:1 |
| "Every visual needs a border" | Wrong invariant — labels/icons/dividers borderless by design | Tiles get one edge; labels none — never two |
| Shadow everywhere / `Center` preset | Halo mimics a second border | Overlays only; directional |
| Restyling N visuals identically | That's the theme's job | Theme `visualStyles` defaults → `pbi-theme-json` |
| Chained find-replace | `A→B` then `B→C` turns A into C | One map-driven pass; `#hex`+`%23hex` together |
