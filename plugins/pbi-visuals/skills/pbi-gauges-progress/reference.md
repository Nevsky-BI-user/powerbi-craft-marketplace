# Gauges & Progress Indicators — Reference

Companion to `SKILL.md`. Visual-type keys and card names below are verified against
`docs/research/theme-visuals.md` (reportThemeSchema 2.143 = 2.155) — never recalled from
memory (BRIEF F2). Tokens (`color/*`, `ramp/*`) resolve in `docs/DESIGN-TOKENS.md`.

## 1. Verified visual-type keys in this space

| Key | Format-pane name | Verified? |
|---|---|---|
| `gauge` | Gauge | Yes — key confirmed (theme-visuals §5, "Shape & part-to-whole charts"); no per-visual card names verified in our research |
| `kpi` | KPI | Yes — key confirmed (theme-visuals §5, "Cards, KPI, tables"); no per-visual card names verified |
| `cardVisual` | Card (new) | Yes — 44 cards; `value`, `label`, `layout` fully verified (theme-visuals §6.6); also has `referenceLabel`, `referenceLabelTitle`, `referenceLabelValue`, `referenceLabelDetail`, `referenceLabelLayout`, `accentBar` (named, sub-properties NOT enumerated in our research) |

**No native `progressBar` / `progressRing` visual key exists** — confirmed absent from the
complete visual-type list (theme-visuals §5). Do not theme or reference one; a progress
bar/ring is either a `dax-svg` DAX-measure image, or a `cardVisual` with a `referenceLabel`.

For `gauge` and `kpi`: their card names (`indicator`, axis min/max/target properties, trend
line settings, etc.) are **not** in our verified schema notes. Before styling either, read a
real instance from the target report, or the matching `reportThemeSchema-2.1xx.json`, via
`powerbi-visuals`. Never guess property names from memory.

## 2. Decision matrix

| Need | Visual | Why |
|---|---|---|
| One KPI, no trend, exec expects a dial | `gauge` (single instance) | Only case where angle encoding is acceptable — familiarity outweighs the perceptual cost, but only once per page |
| One KPI vs target, no trend | `cardVisual` + `referenceLabel` | Value + target + delta in the richest native card visual; no custom SVG needed |
| One KPI vs target, WITH trend | `kpi` | Native visual bundles value + sparkline + goal line; theme `good`/`neutral`/`bad` drives status |
| Several KPIs vs targets, comparable | Bullet chart (`dax-svg`, one per row/small-multiple) | Position/length encoding; qualitative zones + target tick + actual bar, all comparable on one shared scale |
| "X% complete", no zones | Linear progress bar (`dax-svg` single filled rect, or `cardVisual` `referenceLabel` showing `%`) | Simplest legible option — nothing beats a filled rectangle for "how much of 100%" |
| In-cell progress inside a table/matrix column | In-cell linear bar (`dax-svg`) | Horizontal, compact, scans down a column; a ring/radial per row does not |

## 3. Bullet graph — design anatomy (Few's bullet graph, adapted)

A bullet graph is a horizontal bar with three layered elements, drawn by a `dax-svg`
DAX measure. This skill owns the *design spec*; `dax-svg` owns turning it into a SVG
image measure.

1. **Qualitative background range** (drawn first, behind everything): 2–3 bands along the
   full scale, light→dark neutral fills — do NOT use `ramp/rag` here (that ramp is for
   status/CF, not backdrop bands); use tints of `color/border` / `color/surface-alt`.
2. **Performance bar**: a thinner bar (≈1/3 the band height), centered, filled
   `color/brand` (on-track) or `ramp/rag` status color if the KPI has a pass/fail state.
3. **Target tick**: a single vertical line (contrasting, e.g. `color/text-body` or
   `color/bad` if missed), drawn at the target value's position on the same scale.

**Draw the target tick inside the SVG measure — never via `barChart` error bars.** The safe
ways to show a target are: the SVG `<line>` above, a `gauge` target property, or a combo-chart
reference line. Do NOT hand-author `error` / `errorRange` on the underlying `barChart`: the
property *name* is valid (theme-visuals.md §6.2 lists the `error` card), but its value
*structure* is undocumented, and Power BI Desktop reacts to a valid property carrying a
malformed value structure by **refusing to open the entire report** — "Failed to load report",
no error detail. This is the cross-cutting Desktop law: an *unknown* property name is silently
ignored, but a *known* name with an invalid value structure crashes the whole report. If error
bars are truly needed, configure them in Desktop UI and copy the JSON Desktop saves verbatim —
never invent the shape. Diagnosing such a crash means bisection: remove half the hand-added
JSON, reopen, repeat until the offending object is isolated (this cost 9 reopen rounds once).

```
0                                    target        max
├──────band 1──────┼──────band 2──────┼───band 3───┤
      ███████████████████████████               |          ← performance bar + target tick
```

Example SVG sketch (design reference only — the real measure lives in `dax-svg`, bound
via an image-URL DAX measure, dimensions/scale computed from the measure's own min/max):

```svg
<svg viewBox="0 0 200 24" xmlns="http://www.w3.org/2000/svg">
  <rect x="0"  y="0" width="120" height="24" fill="#FAFAFA"/>  <!-- band 1: color/surface-alt -->
  <rect x="120" y="0" width="80"  height="24" fill="#E6E6E6"/> <!-- band 2: color/border (neutral tints per SKILL rule — never brand/RAG on the backdrop) -->
  <rect x="0" y="8" width="140" height="8" fill="#063E61"/>    <!-- performance bar: color/brand -->
  <line x1="150" y1="0" x2="150" y2="24" stroke="#333333" stroke-width="2"/> <!-- target tick -->
</svg>
```

Scale, exact coordinates, and the DAX formula that computes them (percent-of-max →
pixel math, target position, conditional fill color) are `dax-svg` responsibilities —
this sketch only fixes the *design* (band tints, bar height ratio, tick style).

## 4. Zones and status color

- Qualitative background bands: neutral tints (`ramp/brand-seq` steps 100–300, or plain
  `color/border`/`color/surface-alt`), never `ramp/rag` — bands are context, not judgment.
- Performance-bar / needle-arc status color (on-track vs at-risk vs off-track): `ramp/rag`
  (DESIGN-TOKENS §1.3), referenced from the theme, never re-hardcoded per visual.
- Binary on/off-target: prefer `good`/`bad` theme sentiment keys over a 6-step ramp.

## 5. When a gauge is the deliberate choice

Checklist before emitting a `gauge` (all must hold):

- [ ] Exactly one instance on the page (never a grid — reject per Common Mistakes).
- [ ] Minimum, maximum, AND target are all defined and bound to real measures/values
      (verify against the TMDL model — missing → `dax-measures`).
- [ ] No trend requirement — if the user also wants "how did we get here", route to `kpi`
      or a line chart with a reference line instead.
- [ ] Styled flat (no 3D/skeuomorphic preset), theme-consistent border/background per
      DESIGN-TOKENS §4, arc color from `ramp/rag` or `good`/`bad`.

## 6. Verified `cardVisual` fragment to extend for reference-label progress

Base card (theme-visuals §6.6, verified) — extend with `referenceLabel` for a target/goal
line once its exact sub-properties are confirmed from a ground-truth visual or schema:

```json
"cardVisual": {
  "*": {
    "value": [{ "fontSize": 24, "fontFamily": "DIN",
                "fontColor": { "solid": { "color": "#063E61" } },
                "labelDisplayUnits": 0, "labelPrecision": 1 }],
    "label": [{ "show": true, "fontSize": 9,
                "fontColor": { "solid": { "color": "#605E5C" } }, "position": "Above" }],
    "layout": [{ "orientation": "Horizontal", "rectangleRoundedCurve": 8,
                 "backgroundShow": true,
                 "backgroundFillColor": { "solid": { "color": "#FFFFFF" } } }]
  }
}
```

`referenceLabel*` cards exist on `cardVisual` (confirmed by name in theme-visuals §6.6) for
showing the target/goal alongside the value — read their exact sub-properties from a
ground-truth `cardVisual` with a reference label already configured, or from the schema
file, before emitting JSON (BRIEF F1/F2). JSON mechanics (adding/binding the card) →
`powerbi-visuals`.

**Caveat on the base-card fragment above:** it is copied verbatim from an observed
production report (theme-visuals §6.6) to prove the JSON *shape* — its `fontFamily: "DIN"`
and `value.fontSize: 24` are that report's drift, not canonical tokens (DESIGN-TOKENS §2:
Segoe UI only, never an external font stack; the pt ramp is 28/18/14/12/10/9, so 24 isn't
on it). In new work, swap `fontFamily` to `"Segoe UI"`/`"Segoe UI Semibold"` and
`value.fontSize` to `type/value` (12 pt) or, for a hero gauge-replacement card,
`type/callout-hero` (28 pt) — never keep `"DIN"`/`24` as if they were tokens.
