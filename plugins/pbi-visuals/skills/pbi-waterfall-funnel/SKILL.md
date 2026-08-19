---
name: pbi-waterfall-funnel
description: Use when creating, restyling, or reviewing a Power BI waterfall or funnel chart in a PBIP report - plan-vs-actual bridges, variance breakdowns, increase/decrease/total colors, or stage-conversion labels. Do NOT trigger for chart choice (use pbi-visualization-strategy), part-to-whole (use pbi-part-to-whole), or JSON mechanics (use powerbi-visuals). Triggers - 'waterfall chart', 'bridge chart', 'funnel chart', 'воронка', 'каскадна діаграма', 'план факт міст', 'конверсія по етапах'.
---

# Waterfall & Funnel Charts

## Overview

**Waterfall** = a bridge from start to end through ordered +/− contributions (plan-to-actual, variance, headcount) with a running total; **funnel** = an ordered, single-path process where each stage is a subset of the previous, read as conversion/drop-off. Both encode **sequence**, not magnitude — the case overriding "sort by value."

## When to Use

- Waterfall: decomposing a plan-to-fact or period variance into named drivers with a visible running total.
- Funnel: an ordered process, non-increasing counts per stage (leads → MQL → SQL → won); conversion % is the point.
- NOT for: chart choice itself (`pbi-visualization-strategy`); unordered part-to-whole (`pbi-part-to-whole`); a plain variance bar often tells it better (`pbi-bar-column-charts`).

REQUIRED SUB-SKILL: `powerbi-visuals` (JSON, fields); `dax-measures`; `deneb-vegalite` (native gaps); `pbi-design-system` (`pbi-design-system`); `icon-set-manager`.

Pre-flight: detect PBIR format; read a real `waterfallChart`/`funnel` visual as ground truth; confirm fields exist in the TMDL model.

## Quick Reference

| Decision | Rule |
|---|---|
| Visual-type key | `waterfallChart` (not `waterfall`); `funnel` (not `funnelChart`) |
| Waterfall color | Theme `good`/`neutral`/`bad` drive increase/decrease/total; never per-visual hex |
| Breakdown | Splits one bar into sub-drivers; ≤ 8 bars total, tail → "Other" |
| Connectors & labels | On by default; variance text uses `good-text`/`bad-text`, not mark hexes |
| Funnel order | Native process sequence — never sort by value |
| Funnel color | Monochrome `ramp/brand-seq` by depth — never one hue per stage |
| Funnel labels | Value, % of first stage, % of previous stage |
| Funnel critique (F7) | >5–6 stages → weak encoding; prefer sorted bars + conversion-% labels |

Card/property names, native-vs-Deneb decision: [reference.md](reference.md).

## Common Mistakes

| Mistake | Why bad | Correct |
|---|---|---|
| Funnel sorted by value | Breaks process order | Keep native stage order |
| Rainbow color per stage | Implies unrelated categories | Monochrome `ramp/brand-seq` by depth |
| Hardcoded increase/decrease hex | Theme drift | Set `good`/`neutral`/`bad` once in the theme |
| >5–6 stages endorsed uncritically | Area/width is weak (F7) | Sorted bars + conversion-% labels |
| `good`/`bad` hex used as small text | Fails AA | `good-text`/`bad-text` tokens |
| Color as the only signal | Fails colorblind readers | Pair with icons (`icon-set-manager`) or +/− labels |

## Verify before done

JSON parses → visual keys exactly `waterfallChart`/`funnel` → bindings exist in TMDL → theme `good`/`neutral`/`bad` referenced, not hardcoded → `git diff` matches intent. Rendering cannot be verified headless.

