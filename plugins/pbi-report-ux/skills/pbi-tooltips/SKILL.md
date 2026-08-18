---
name: pbi-tooltips
description: Use when designing, creating, or reviewing Power BI tooltips - default vs custom tooltip page, canvas sizing, hover content, or fixing slow, oversized, or unreadable tooltips. Do NOT trigger for right-click detail pages (use pbi-drillthrough), tooltip JSON wiring (use powerbi-visuals), or tooltip measures (use dax-measures). Triggers - 'tooltip', 'tooltip page', 'report page tooltip', 'hover detail', 'тултіп', 'спливаюча підказка', 'підказка при наведенні', 'сторінка-підказка'
---

# Tooltip Page Design

## Overview

A tooltip answers ONE micro-question about the hovered data point: **context** (what is this) + **detail** (how it moved / what it is made of). This skill owns default-vs-custom, canvas size, content hierarchy, and performance budget; JSON wiring is delegated (REQUIRED SUB-SKILL: `powerbi-visuals`).

## When to Use

- Adding hover detail to a visual, or decluttering a chart by moving labels into tooltips.
- Creating or reviewing a tooltip page; unifying tooltip styling report-wide.

NOT for: right-click detail (`pbi-drillthrough`), wiring JSON (`powerbi-visuals`), measures (`dax-measures`), the on-page annotation/callout layer (`data-storytelling` — a conclusion that lives only in a tooltip is unreachable by keyboard and screen readers).

## Pre-flight (mandatory)

Detect format: Legacy `report.json` uses integer flags (`"visibility": 1`, `displayOption: 3`); PBIR enhanced `page.json` uses STRING flags (`visibility: "HiddenInViewMode"`, `displayOption: "ActualSize"`, `type: "Tooltip"`). Clone exact values from a ground-truth tooltip page; read actual canvas `width/height`; verify bound fields exist in TMDL (missing → `dax-measures`).

## Quick Reference

| Element | Spec (tokens: DESIGN-TOKENS.md) |
|---|---|
| Default vs custom vs off | ≤3 confirm fields → **default tooltip** via theme `visualTooltip` card; context+detail (trend, composition, plan vs fact) → **custom page**; decorative → **off** |
| Canvas | `grid/canvas-tooltip` 320×240, up to 550×500; ActualSize mandatory (syntax per format: Pre-flight) |
| Visuals | ≤3: context header, value + delta, one detail visual; `visualHeader.show: false` |
| Type | Header `type/title`; hero value `type/header`; body `type/label`; captions `type/small`; floor 8 pt |
| Interactivity | None — read-only |

Full rationale: `reference.md`.

## Layout — the one pattern

320×240, top to bottom: 8 px margin → 24 px context header (category · period, `type/title`) → 32 px value + Δ vs PY (`type/header`; good/bad + ▲▼, never color alone) → 148 px detail (12-pt trend, direct end label, axes/legend/labels off) → 8+8 px gap/margin (full pixel table: `reference.md`).

Context header = DAX measure with `SELECTEDVALUE` fallback — same pattern as `pbi-drillthrough`. Sparkline detail → `dax-svg`; richer specs → `deneb-vegalite`.

## Performance budget

Every hover fires every query on the page. Keep ≤3 visuals, measures cheap (`power-bi-dax-optimization`), no maps/AI visuals/high-cardinality tables. Reuse ONE generic tooltip page instead of per-chart clones.

## Common Mistakes

| Mistake | Fix |
|---|---|
| FitToPage left on | ActualSize (Legacy int / enhanced string) |
| Full 1280×720 page as tooltip | 320×240…550×500 |
| Critical info only in tooltip | Duplicate on page / `pbi-drillthrough` |
| Multi-field `cardVisual`, or value crammed into h=44 | Single-field cards, 148×64 (8-pt label + 16-pt value need h=64) |
| Narrow trend, 24-month categorical axis → scrollbar | TopN-12 filter: `In`+`Subquery` `Top:12`, `OrderBy` Max on sort col |

More mistakes: `reference.md`.

## Verify before done

File parses → canvas size, ActualSize, hidden + tooltip flag present → bound fields exist in model → `git diff` matches intent. Report-page tooltip binding + re-save crash: `reference.md`. Hover rendering isn't verifiable headless — say so explicitly.
