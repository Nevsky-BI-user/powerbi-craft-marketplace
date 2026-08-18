---
name: pbi-ai-visuals
description: Use when adding, theming, or scoping Power BI AI visuals - Decomposition tree, Key influencers, Smart narrative, Q&A visual, anomaly detection. Flags correlation-vs-causation, Copilot licensing. Do NOT trigger for chart choice (pbi-visualization-strategy), visual JSON (powerbi-visuals), driver measures (dax-measures). Triggers - 'decomposition tree', 'key influencers', 'smart narrative', 'Q&A visual', 'anomaly detection', 'дерево декомпозиції', 'ключові фактори впливу', 'розумна розповідь'.
---

# AI Visuals

## Overview

Four visual types plus one analytics feature bring built-in ML/NLP: `decompositionTreeVisual`,
`keyDriversVisual`, `aiNarratives` (Smart narrative — **not** `smartNarrative`), `qnaVisual`, and
anomaly detection (a `lineChart` card, **not** standalone). JSON/binding → `powerbi-visuals`;
driver/target measures → `dax-measures`; chart choice → `pbi-visualization-strategy`. Covers
PBIR-Legacy/enhanced; schema-verified against `reportThemeSchema-2.155.json`.

## When to Use

- Root-cause / "why did X change" across dimensions → Decomposition tree.
- "What drives/predicts target Y" or segment discovery → Key influencers.
- Auto-generated narrative that updates with filters → Smart narrative.
- Ad-hoc natural-language exploration for end users → Q&A visual.
- Outlier flagging on one time series → `lineChart`'s `anomalyDetection` card.

**NOT for:** a known fixed drill path (→ `pbi-drillthrough`); proving causation; replacing a
KPI/title with prose (authored claims → `data-storytelling`); production Q&A with zero synonym
curation; anomaly flags on bar/column (lineChart only).

Before writing JSON: detect PBIR-Legacy vs enhanced format, read a ground-truth instance of the
target visual if one exists in the report, and confirm bound fields exist in the TMDL model
(missing → `dax-measures`) — never invent card values from memory.

## Quick Reference

| Feature | Key | Use when |
|---|---|---|
| Decomposition tree | `decompositionTreeVisual` | Breakdown by dimension; optional AI split |
| Key influencers | `keyDriversVisual` | "What drives Y" / segment finder |
| Smart narrative | `aiNarratives` | Auto-summarize visuals in text |
| Q&A visual | `qnaVisual` | Free-form NL question box |
| Anomaly detection | `lineChart` → `anomalyDetection` card | Outliers on a regular-interval series |

Full tables and design notes → **reference.md**.

## Styling under theme

All five inherit the global `"*"` defaults (DESIGN-TOKENS §6) plus their own cards; reference
colors via `ThemeDataColor`/named theme colors (§1.7), never hex literals.

```json
"visualStyles": {
  "keyDriversVisual": { "*": { "keyInfluencersVisual": [{
    "primaryColor": { "solid": { "color": { "expr": { "ThemeDataColor": { "ColorId": 2, "Percent": 0 } } } } },
    "secondaryColor": { "solid": { "color": "#E6E6E6" } }
  }]}}
}
```

## Common Mistakes

| Mistake | Why bad | Instead |
|---|---|---|
| Key influencers as proof of cause | Correlation only | Say "influencers / correlated with" |
| Decomposition tree for a known fixed path | ML overhead, no new answer | `pbi-drillthrough` |
| Q&A shipped with zero synonym setup | Poor NL matching | Curate synonyms/hidden fields; flag unverified |
| Anomaly markers red-only | Fails colorblind users | Pair `markerShape` + color (tokens §1.3) |
| Hardcoded hex in these cards | Theme drift | `ThemeDataColor` / named theme colors |

Wrong keys (`smartNarrative`, top-level `anomalyDetection`) → **reference.md** "Known-wrong keys".

## Verify before done

File parses as JSON; theme validates against `reportThemeSchema-2.1xx`; keys/cards match above;
bound fields exist in the TMDL model. Narrative text, Q&A phrasing, and AI-split/anomaly
results depend on live data — flag these as unverifiable headless.

Closes BRIEF F1, F2, F3, F5, F6, F7, F9, F10.
