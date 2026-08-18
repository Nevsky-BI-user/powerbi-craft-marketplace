---
name: pbi-headers-icons-imagery
description: Use when composing or fixing a Power BI page header - title, logo, last-refreshed stamp, filter-status cue, divider, or background/watermark imagery. Do NOT trigger for icon fetch (icon-set-manager), nav tabs (pbi-navigation-tabs), filter badge (pbi-slicers-filter-panel), drill-through header (pbi-drillthrough), or JSON mechanics (powerbi-visuals). Triggers - 'header', 'page header', 'logo', 'last refreshed', 'watermark', 'заголовок сторінки', 'хедер', 'лого', 'дата оновлення', 'розділювач'.
---

# Page Headers, Icons & Imagery

## Overview

The header is the one row every page shares — title, whose data, how current, what's filtered — without competing with the hero KPI below. Owns composition: zones, sizing, placement, refresh-stamp source, divider restraint, image contrast. Writes no JSON, fetches no PNGs. Title **text** (subject vs finding) → `data-storytelling`. Required: `icon-set-manager` (icon/logo, `#063E61`, 64/128 px); JSON → `powerbi-visuals`.

Formats: PBIP (PBIR-Legacy or enhanced); TMDL. Closes BRIEF F1–F3, F6–F10.

## When to Use

Title+logo row, "data as of" stamp, filter-status cue, divider/band, or background/watermark imagery; header byte-identical across pages.

## Pre-flight (mandatory)

1. Detect format; read an existing `textbox`/`shape`/`image` as ground truth — never from memory.
2. Read actual page `width/height` (PDP 1440-wide → tokens §7); resolve theme palette.
3. Inventory header elements across pages — one shared recipe, not per-page drift.

## Quick Reference

| Zone | Content | Spec |
|---|---|---|
| Row | Full width × **40 px**, y = 24 | Identical `x/y/width/height` |
| Left | Logo (32×32, optional) + title | `type/hero` 18 pt Semibold `color/text-title` |
| Right | Refresh stamp + filter-status | `type/small` 9 pt `color/text-secondary`, low priority |
| Below | 16–24 px gap (default) or divider | Whitespace over a line |

## Patterns

**Logo/title**: `image` via `icon-set-manager`, **64 px** default (never 128 px hero — downscale only); `textbox` clones the ground-truth title.

**Refresh stamp**: theme's `pageInformation`/`pageRefresh` cards if already shown; else a `dax-measures` timestamp on a textbox — never hardcoded.

**Filter-status**: short measure on a `type/small` textbox next to a filter icon; badge/clear-all → `pbi-slicers-filter-panel`.

**Divider/band**: hairline `shape`, 1 px `color/border`, sparingly; full-bleed brand band only on cover pages. A `shape` is **two-entry**: show-toggles (`fill.show`, `outline.show`) bare, NO selector; value props (`fillColor`, `lineColor`, `weight`) in a separate entry with `selector {id:"default"}` — else default purple. `tileShape` only `rectangle`/`rectangleRounded`/`line`/`tabRoundTopCorners`, not `rectangleRoundedByPixel`.

**Background/watermark**: full-page `image` allowed; text needs a scrim or flat-zone placement, ≥4.5:1 contrast.

Card/property names, worked JSON, icon categories, DAX: [reference.md](reference.md).

## Common Mistakes

| Mistake | Why bad | Fix |
|---|---|---|
| Coordinates differ per page | Title/logo jump on navigation | One byte-identical recipe |
| Hardcoded "Updated: 12.03" | Silently stale | DAX measure or native `pageRefresh` |
| 128 px logo in a 32 px row | Oversized | Request 64 px, or downscale |
| Text over a busy photo | Fails contrast | Scrim or flat-zone placement |
| External/CDN `imageUrl` on `image` | Blank placeholder (no fetch) | Register PNG (RegisteredResources + `ResourcePackageItem`) — [reference.md](reference.md) |
| Dark PNG on dark page | Near-invisible | Repaint to a light token first |

## Verify before done

JSON parses → coordinates identical across pages → refresh/filter text bound to a measure → alt text set (or decorative) → image contrast ≥4.5:1 → `git diff` matches intent. Logo/photo rendering unverifiable headless.
