---
name: pbi-gauges-progress
description: Use when a gauge, speedometer, dial, or progress bar/ring is requested for a Power BI PBIP report - native gauge vs bullet chart vs linear progress vs cardVisual reference label vs kpi choice. Do NOT trigger for chart choice (pbi-visualization-strategy), SVG rendering (dax-svg), or JSON mechanics (powerbi-visuals). Triggers - 'gauge', 'speedometer', 'progress bar', '% of goal', 'спідометр', 'індикатор прогресу', 'прогрес-бар', 'ціль виконання'.
---

# Gauges & Progress Indicators

## Overview

Native `gauge` encodes value as needle angle — the weakest perceptual channel
(Cleveland–McGill) — and wastes half its card as empty arc. Prefer a bullet graph
or linear progress bar; reserve `gauge` for one justified case.

## When to Use

- A gauge/speedometer/dial, "% of goal", or progress bar/ring is requested — decide
  whether `gauge` is justified, else route to a bullet chart, linear progress, `cardVisual`
  reference label, or `kpi`. Not for KPI card layout (`pbi-kpi-cards`) or CF semantics
  (`pbi-conditional-formatting`).

Before writing JSON: detect PBIR-Legacy vs enhanced, confirm the measure AND target exist
(missing → `dax-measures`), and read a ground-truth gauge/card/SVG visual if one exists.

REQUIRED SUB-SKILL: `dax-svg` (bullet/progress SVG measures); also `deneb-vegalite` (custom),
`powerbi-visuals` (JSON), `pbi-design-system` (tokens).

## Quick Reference

| Decision | Rule |
|---|---|
| Default choice | Bullet graph (`dax-svg`) — actual + target tick + zones + stacks |
| `gauge` acceptable | One hero KPI, ONE per page, dial expected, min/target/max set |
| Reject `gauge` | >1 per page; no min/max/target; trend matters → `kpi`; comparing categories |
| Linear progress ("X% done") | `dax-svg` filled rect, or `cardVisual` `referenceLabel` |
| Zone bands (backdrop) | Neutral tints, 2–3 bands — never `ramp/rag` (status color; reference.md §3–4) |
| Performance-bar / needle status | `ramp/rag` (DESIGN-TOKENS §1.3) or `good`/`bad` |

No native `progressBar`/`progressRing` key exists (theme-visuals.md §5) — build progress via
`dax-svg` or `cardVisual`. Bullet anatomy + the `cardVisual.referenceLabel` fragment:
[reference.md](reference.md).

## Common Mistakes

| Mistake | Why bad | Instead |
|---|---|---|
| Grid of 4–6 native gauges | Angle isn't comparable; wastes space | Stacked bullet charts (`dax-svg`), shared scale |
| Gauge with no min/max/target | Needle floats, no reference | Bullet graph with a target tick |
| 3D/skeuomorphic dial styling | Zero data-ink gain | Flat 2D, theme-consistent |
| Speedometer for a KPI needing history | Gauge shows only "now" | Native `kpi`, or line + reference line |
| Backdrop bands colored/hardcoded | Pre-judges the reading | Neutral tints (`color/border`/`surface-alt`), 2–3 bands only |
| Status/target-zone color as arbitrary hex | Theme drift | `ramp/rag` or `good`/`bad` from DESIGN-TOKENS |
| Inventing a `progressBar` key | Doesn't exist; silent no-op | `dax-svg` measure or `cardVisual`, real keys |
| Hand-authoring `error`/`errorRange` for a target tick | Valid property, invented value *structure* → Desktop refuses to open the whole report | SVG tick (reference.md §3), `gauge` target, or combo reference line — never error bars |

## Verify before done

File written → JSON parses → visual key is real (`gauge`/`kpi`/`cardVisual`) → measure AND
target bindings exist → SVG measures return valid markup → `git
diff` matches intent. Needle angle / SVG rendering can't be verified headless — say so.

Closes BRIEF F1, F2, F3, F5, F6, F7, F9, F10.
