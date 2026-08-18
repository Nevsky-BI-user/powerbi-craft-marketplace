---
name: pbi-maps-geo
description: "Use when creating, choosing, or restyling map/filledMap/shapeMap/Azure Maps visuals in Power BI reports: choropleth vs bubble choice, color-scale design, Ukraine oblast geocoding pitfalls, or whether a map is the right visual. Do NOT trigger for non-geo chart choice (pbi-visualization-strategy), topojson-in-Deneb (deneb-vegalite), or visual JSON mechanics (powerbi-visuals). Triggers - 'мапа', 'карта України', 'область', 'choropleth', 'filled map', 'shape map', 'Azure Maps', 'геовізуалізація'."
---

# Power BI Maps & Geo Visuals

## Overview

A map is justified only when spatial adjacency or location IS the insight — otherwise a sorted bar chart/table ranks values more accurately (position/length beat area/hue — Cleveland–McGill). Visual choice depends on data shape (points vs named regions vs custom boundaries) — see Quick Reference.

## When to Use

- Adding/restyling a geo visual; choosing map type; designing a choropleth/bubble color scale; troubleshooting Ukraine oblast geocoding.
- **NOT for:** chart choice (`pbi-visualization-strategy`), topojson-in-Deneb (`deneb-vegalite`), visual JSON mechanics (`powerbi-visuals`), color tokens (`pbi-design-system`).

REQUIRED SUB-SKILL: `powerbi-visuals`; missing measures → `dax-measures`.

## Pre-flight (mandatory)

1. Detect format (PBIR-Legacy `report.json` vs enhanced `visual.json`); read a real geo visual as template — never invent JSON.
2. Ask first: location, or only ranking/magnitude? Latter → `pbi-bar-column-charts`/`pbi-tables`, not a map.
3. Verify the geography field's data category and bound measure exist in the model.
4. Ukraine oblasts: Bing geocoding fails **silently** (stale boundaries, name collisions, drift). Prefer Lat/Long columns, or `shapeMap` + own TopoJSON (ISO 3166-2:UA). Decision path → [reference.md](reference.md) §4.

## Quick Reference

| Data shape | Visual key | Color card | Notes |
|---|---|---|---|
| Points, size = magnitude | `map` | `dataPoint.fillRule` | `bubbleSize`; `markerRangeType: magnitude` (stable) vs `dataRange` (one snapshot) |
| Rate/share, named region | `filledMap` | `dataPoint.fillRule` | Sequential → `ramp/brand-seq`; deviation → `ramp/diverging`; `stroke` 1 px |
| Ukraine oblasts, custom boundaries | `shapeMap` | `dataPoint.fillRule` + `defaultColors` | Own TopoJSON (`shape.mapUrl`) — bypasses Bing |
| Routes, traffic, reference/heat layers | `azureMap` | per layer (`bubbleLayer`, `heatMapLayer`, …) | Needs Azure Maps key — flag before building |

Color: `linearGradient2` (min/max, `ramp/brand-seq`, dark = more, never rainbow) for magnitude; `linearGradient3` (min/mid/max, `ramp/diverging`) for deviation, `mid` pinned at the meaningful zero/target — never the data mean. `map`/`filledMap` = Bing, deprecation scheduled — prefer `azureMap`/`shapeMap` for new work (currency note → reference.md §1). Card/property JSON → [reference.md](reference.md).

## Common Mistakes

| Mistake | Why bad | Instead |
|---|---|---|
| Choropleth for exact-value lookup | Weakest accurate encoding | `tableEx` or sorted bar |
| Rainbow color scale | No implied order, fails colorblind users | Lead with `ramp/brand-seq`/`ramp/diverging` (canon) FIRST; a client-insisted alt palette only as tokens + documented deviation + labeled polarity |
| `dataRange` sizing across a time filter | Bubbles not comparable slice to slice | `markerRangeType: magnitude` |
| Trusting Bing geocoding unverified | Silent mis-plot, wrong region highlighted | Lat/long columns or `shapeMap` + TopoJSON |
| Choropleth with no legend/tooltip value | Color alone isn't precise | Legend on + exact value in tooltip |

## Verify before done

File written → JSON parses → visual/card names match reference.md → bindings exist in model → `git diff` matches intent. Rendering/geocoding can't be verified headless — say so.

Closes BRIEF F1, F2, F3, F5, F6, F7, F9, F10.
