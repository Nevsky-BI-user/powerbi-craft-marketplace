---
name: pbi-color-accessibility
description: Use when assigning or auditing colors in a Power BI report - semantic roles (good/bad/warning), WCAG contrast for text/data pairs, colorblind-safe palettes, sequential/diverging heatmap or choropleth scales, PBIR-Legacy/enhanced. Do NOT trigger for CF thresholds (pbi-conditional-formatting), theme.json (pbi-theme-json), visual JSON mechanics (powerbi-visuals). Triggers - 'color contrast', 'WCAG', 'colorblind', 'heatmap colors', 'доступність кольору', 'контраст', 'дальтонізм', 'кольорова шкала'.
---

# Power BI Color & Accessibility

## Overview

A color is a semantic role first, a hex second — it must clear a computed WCAG ratio
before shipping (BRIEF F3/F6/F9/F10). Detect the format (`report.json` PBIR-Legacy vs
`visual.json` enhanced), resolve theme colors (`dataColors` via `ColorId`; named keys
`good`/`neutral`/`bad`/`maximum`/`center`/`minimum`/`null` by name, not `ColorId`),
then classify each pair STATIC (once) or DYNAMIC (full range, not endpoints).

## When to Use

- Assigning/reviewing series, KPI sentiment, legend, or CF heatmap/choropleth colors.
- Checking a new pair for AA before it ships.
- Building a sequential/diverging scale (`filledMap`/`shapeMap`, CF gradient).

Also NOT for: icons (`icon-set-manager`); a11y (`web-design-guidelines`); non-PBI palettes
(`theme-factory`); hex values (`pbi-design-system`/DESIGN-TOKENS.md).

## Quick Reference

| Decision | Rule |
|---|---|
| Semantic roles | One hue = one meaning; never reuse sentiment hues as categorical |
| Contrast minimums | Normal text ≥4.5:1; large text (≥18 pt/≥14 pt bold) ≥3:1; non-text marks ≥3:1 |
| Categorical palette | Brand-first `dataColors`, max 6–8 hues; Okabe–Ito need a contrast check (§6) |
| Binary states | Blue vs orange (`color/brand`/`color/warning`), never red vs green |
| Sequential/diverging ramp | `ramp/brand-seq`/`ramp/diverging`; midpoint = meaningful center, never mean; seq-400 = dead zone (§3) |
| CF plumbing | Theme sentiment/gradient keys ↔ DAX color strings (§8) |
| Redundant coding | Color never alone: pair with ▲▼ (`icon-set-manager`), label, or sort order |
| In-cell / dark-theme contrast | Chip/SVG/data-bar text: contrast vs its fill, not the page; on dark, `#475569`-class grays read black — bright tokens only (§10) |
| Transparency after a theme flip | Rate the BLENDED fill: `#4f46e5` @50% on white = 2.31:1 (<3:1); 20 → 4.19:1 (§11) |
| Fill still under 3:1 | Two fixes, not one: less transparency OR `dataPoint` `borderShow`/`borderSize` 2/`borderColorMatchFill` (§11a) |

Full formulas/tables: [reference.md](reference.md).

## Patterns (on-fill text safety)

- **A — Restrict range**: clip fill to one text color's safe sub-range.
- **B — Flip at breakpoint**: switch text color at the dead-zone boundary.
- **C — Off-fill**: put the value beside the fill.

## Common Mistakes

| Mistake | Why bad | Correct |
|---|---|---|
| Contrast judged by eye | Fails AA silently | Extract all hex (theme+visuals), compute and cite every ratio (§10) |
| Fixed text on full-range gradient | Midtones/dark end unreadable | Pattern A/B/C above |
| Red/green RAG, no icon/label | Invisible to ~8% of men | Pair with ▲▼ + label, or blue/orange |
| Pale fill judged without its border | Half an audit | Check `borderShow` too (§11a) |
| Okabe–Ito assumed WCAG-safe | Orange/sky/yellow fail ≥3:1 | Darken or outline thin marks |

## Verify before done

JSON parses → every NEW pair has a computed/cited ratio → roles consistent → colorblind
checked → `git diff` matches intent (headless render unverifiable — say so).
