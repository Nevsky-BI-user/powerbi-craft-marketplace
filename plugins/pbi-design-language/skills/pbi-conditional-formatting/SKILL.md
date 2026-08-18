---
name: pbi-conditional-formatting
description: "Use when deciding CF for a Power BI visual — table/matrix cells, KPI status, heat maps: rules vs gradient vs field value, semantic colors/icons. Do NOT trigger for CF JSON mechanics (powerbi-visuals), status measures (dax-measures), contrast (pbi-color-accessibility), table layout (pbi-tables). Triggers - 'умовне форматування', 'conditional formatting', 'градієнт', 'теплова карта', 'світлофор', 'RAG', 'field value color'."
---

# Power BI Conditional Formatting

## Overview

CF is the sharpest attention tool in a report — a table that's "all color" has none.
Decide the data question (status, magnitude, deviation, rank), then mechanism, then
palette. Mechanism/color are design decisions here; JSON wiring is `powerbi-visuals`.

## When to Use

- Choosing rules vs. gradient vs. field-value CF for a table/matrix column, KPI card, or
  chart point; picking a RAG/diverging ramp; or skipping color entirely.
- NOT for: CF expr JSON → `powerbi-visuals`; threshold DAX → `dax-measures`; WCAG contrast
  → `pbi-color-accessibility`; column layout → `pbi-tables`; subtotals → `pbi-matrix`; icon
  PNGs → `icon-set-manager`.

## Pre-flight (mandatory)

1. Detect format: PBIR-Legacy (`report.json`) vs enhanced (`definition.pbir` + `visual.json`).
2. Name the data question (states/magnitude/deviation/exception) — it picks the mechanism.
3. Copy the expr shape from a real CF'd visual — never invent it (reference.md §1).
4. Resolve theme `good`/`neutral`/`bad` and `maximum`/`center`/`minimum`/`null` keys —
   never add a second RAG scale.
5. Verify the bound field/measure exists in the model.

## Quick Reference

| Mechanism | Answers | Color source | Notes |
|---|---|---|---|
| Rules (stepped) | Few named states | `ramp/rag` or theme `good`/`neutral`/`bad` | ≤4 thresholds; more → gradient |
| Gradient (2–3 stop) | Magnitude/deviation | `ramp/brand-seq` (magnitude) / `ramp/diverging` (deviation) | Center = target, never data average |
| Field value | Status from compound DAX | Measure returns a named theme color (`good`/`bad`/`maxColor`…, reference.md §1), never raw hex | Logic → `dax-measures`; wiring → `powerbi-visuals` |
| Icon sets | Direction/status at a glance | ▲▼/RAG-dot PNGs via `icon-set-manager` | Pair with color + value, never alone |

Verified JSON fragment, gradient trap, DAX field-value pattern: [reference.md](reference.md).

## Common Mistakes

| Mistake | Why bad | Correct |
|---|---|---|
| CF on every column | Nothing stands out | 1–2 CF columns tied to the page's question |
| Rainbow scale for magnitude | Implies categories, not order | Single-hue `ramp/brand-seq`, dark = more |
| Diverging midpoint = data average | "Good" shifts every refresh | Midpoint = target/zero/plan |
| Red/green alone | Fails ~8% colorblind users | Pair with ▲▼ icon or label |
| Ad-hoc hex per visual | Theme drift | Reference theme sentiment keys |
| Icon with no visible value | Ambiguous, fails a11y | Icon + value + label, alt text |
| `dataBars` with invented sub-keys (`minValue`/`maxValue`) or under `values` | Invalid structure crashes the whole report | Six canonical keys in `columnFormatting` only (reference.md §7) |

## Verify before done

JSON parses → CF binds to a real measure/column → theme keys resolved (not invented) →
CF text contrast ≥ 4.5:1 → red/green paired with icon/label → `git diff` matches intent.
Rendered gradient/rule preview can't be verified headless — say so.

Closes BRIEF F2, F3, F5–F7, F9, F10.
