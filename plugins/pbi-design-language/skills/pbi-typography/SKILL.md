---
name: pbi-typography
description: Use when choosing or fixing fonts, sizes, title/label styling, callouts, or number display formats (K/M/%, Ukrainian тис./млн) in Power BI PBIP reports (PBIR-Legacy or enhanced). Do NOT trigger for theme.json generation (pbi-theme-json), visual JSON mechanics (powerbi-visuals), DAX measures (dax-measures), or what a title/callout should SAY (data-storytelling). Defaults - Segoe UI, ramp 28/18/14/12/10/9 pt, floor 8 pt. Triggers - 'font', 'text size', 'number format', 'типографіка', 'шрифт', 'розмір тексту', 'формат чисел', 'тис/млн'.
---

# Power BI Typography

## Overview

One family, one ramp, few weights. Every text property resolves to a `type/*` token (`pbi-design-system` §2): Segoe UI only, floor 8 pt; emphasis = family switch to `Segoe UI Semibold`, never combined with `bold`. The ramp lives once in theme `textClasses` — per-visual overrides are exceptions.

## When to Use

Setting or reviewing fonts, sizes, text hierarchy, or number formats in a PBIP report (Legacy or enhanced; model TMDL).

NOT for: theme.json generation (`pbi-theme-json`), visual/report JSON mechanics (`powerbi-visuals`), display-measure DAX (`dax-measures`), hierarchy theory (`frontend-design`), title/label **wording** (`data-storytelling`). Tokens → `pbi-design-system` (`pbi-design-system`).

Before writing: detect Legacy vs enhanced; read the theme's `textClasses` and a same-type visual first — never from memory; check the measure's `formatString` in TMDL.

## Quick Reference

| Decision | Rule |
|---|---|
| Ramp | callout-hero 28 / hero 18 / header 14 / title 12 / value 12 / label 10 / small 9; floor 8 pt |
| Emphasis | Family switch to Semibold; `bold: true` only if no family property; never both |
| Key names | `fontFace` (textClasses) vs `fontFamily` (visualStyles); tableEx/slicer use `textSize` |
| Number display | Model `formatString` first; `labelDisplayUnits` 1000=K/10⁶=M; тис./млн/млрд need scaling-comma formats — reference.md |
| Cards | Label 9 pt secondary color (`type/small`) above value; delta smaller, good/bad |
| Tables | Header 10 pt bold on `color/brand`; body `grid.textSize` 9; totals bold |
| Textbox 1-line min h | 10pt→40, 12→44, 14→48, 18(+bold)→52, 24→64 px; shorter clips + grows a scrollbar. Mass-resize needs a collision guard — reference.md |

Full 14-class textClasses map, per-visual-type font property names, Ukrainian format-string cookbook: [reference.md](reference.md).

## Pattern: pin largeTitle

`largeTitle` doesn't inherit `title`'s size (schema default 14 pt) — pin it explicitly:

```json
{
  "textClasses": {
    "title":      { "fontFace": "Segoe UI Semibold", "fontSize": 12, "color": "#063E61" },
    "largeTitle": { "fontFace": "Segoe UI Semibold", "fontSize": 12, "color": "#063E61" }
  }
}
```

## Common Mistakes

| Mistake | Why bad | Correct |
|---|---|---|
| Resize titles via `title` class | Titles use `largeTitle` | Pin `largeTitle` (see Pattern) |
| `fontFamily`/`fontFace` swapped | Ignored or invalid | textClasses=`fontFace`, visualStyles=`fontFamily` |
| Semibold family + `bold: true` | Faux-bold, double emphasis | One mechanism only |
| DAX `FORMAT()` or raw numbers for тис./млн | Kills sorting; digit clutter | `formatString` + display units |
| Per-visual font overrides ×N | Drift, mixed sizes | Set `textClasses` once |
| Textbox too short (18pt in 48px, 10pt in 32px) | Clips last line; scrollbar shows as a stray light strip per page | Calibrated floor 40/44/48/52/64 for 10/12/14/18/24pt |

## Verify before done

File written → JSON parses (`fontSize` 6–45 pt), sizes ≥ 8 pt, contrast via tokens (≥ 4.5:1; ≥ 3:1 for ≥ 18 pt), no textbox shows an overflow scrollbar → `git diff` matches intent. Font fallback can't be verified headless — say so.

