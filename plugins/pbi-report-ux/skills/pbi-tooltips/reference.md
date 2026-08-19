# pbi-tooltips — reference

Companion to `SKILL.md`. Load this when you need the full pixel breakdown, format-detection
detail, or the rest of the mistake list — not on every invocation.

## Format detection detail

- **PBIR-Legacy**: single `report.json`, pages as `sections[]`. A tooltip section carries
  **integer** flags: `"visibility": 1` (hidden from nav) and `displayOption: 3` (ActualSize —
  do not confuse with `1` = FitToPage, used by normal pages). Confirmed against this project's
  own audited reports.
- **PBIR enhanced**: `definition.pbir` + `definition/pages/<page>/page.json`. The same two
  concepts are **STRING** properties instead — `visibility: "HiddenInViewMode"`,
  `displayOption: "ActualSize"` — plus a dedicated `type: "Tooltip"` page property that Legacy
  has no direct equivalent for. Writing an integer into an enhanced `page.json` breaks the file
  (schema requires a string); never port a Legacy literal into an enhanced file or vice versa.
  Per-visual opt-in (`visualContainerObjects.visualTooltip`) — verified canon and the Desktop
  re-save crash are below under **Report-page tooltip binding**; general wiring mechanics stay
  in `powerbi-visuals`.
- Either format: resolve the theme's `ThemeDataColor` mapping before choosing colors (see
  `pbi-design-system` §1.7) — never hardcode a hex the theme already exposes.

## Report-page tooltip binding (per-visual)

Wiring a finished tooltip page to a source visual is verified and compact — Desktop's UI
serializes exactly this, so it can be hand-authored:

1. **Source visual** (`visual.json`) — add to `visualContainerObjects` (no `selector`):
   ```json
   "visualTooltip": [
     { "properties": { "show": true, "type": "ReportPage", "section": "<internal page name>" } }
   ]
   ```
   `section` is the tooltip page's internal (definition) name.
2. **Tooltip `page.json`** — top-level `"type": "Tooltip"` is sufficient. `pageBinding` is
   needed ONLY for auto-bind via Tooltip fields; for this per-visual binding a Desktop re-save
   left `page.json` byte-for-byte unchanged.
3. **Desktop re-save crash — delete `showChartSpecificTooltips`.** On save Desktop ADDS a
   `showChartSpecificTooltips` key into `visualTooltip`, and its own loader then REJECTS the
   report on the next open ("additional property showChartSpecificTooltips … enabled"). After
   binding through Desktop, remove that key from the file by hand.
4. **Canvas ≠ live hover.** A tooltip page that renders perfectly on the canvas (ActualSize)
   can still show the default modern tooltip on an actual hover — the format-panel binding
   being present is not proof it renders. Verify live hover only with a real user or in the
   Service; a canvas screenshot is not sufficient evidence.

## Full layout — 320×240, Σ = 240

```
8    margin
24   context header — hovered category · period    type/title, color/text-title
4    gap
32   value + Δ vs PY                                type/header size; Δ good/bad + ▲▼
8    gap
148  detail: 12-point trend — direct end label,
     axes/legend/labels off (single-field cards 148×64)
8+8  gap + bottom margin
```

Grid: 8-px snapped; 8 px edge margin; internal gaps 4/8 only (`pbi-design-system` §3.1 spacing
scale). Delta color: `good`/`bad` theme sentiment colors + a ▲▼ icon — never color alone
(WCAG non-text contrast).

### Legacy compatibility profile

One audited production report uses a wider tooltip-canvas range than the 320×240 default:
observed sizes 320×200, 400×150, and 400/450/550 × 200–500, always with `displayOption: 3`
(ActualSize). When editing such a report's tooltip page, keep its existing canvas size rather than
resizing to 320×240 — match the report's established profile (`pbi-design-system` §7 for the
rest of that report's grid).

## Default vs custom vs off — full rationale

| Hover need | Choice | Why |
|---|---|---|
| Confirm the value + up to ~3 extra fields | **Default tooltip** | No custom page to maintain; style ONCE via the theme's `visualTooltip` common card — never per-visual (avoids theme drift, `pbi-design-system` antipatterns A1/A7) |
| Context + detail: mini-trend, composition, plan vs fact; labels moved off the chart to declutter | **Custom tooltip page** | Needs its own visuals/measures; budget against the performance rule below |
| Decorative shapes, images, spacer rectangles | Tooltip **off** | Nothing meaningful to show; an empty/default tooltip on a decorative shape is noise |

Tooltips are hover-only: invisible on touch devices and to keyboard-only users. Never make a
tooltip the sole carrier of a decision-critical number — duplicate that number on
the page itself, or expose it via a drill-through (`pbi-drillthrough`).

## Common Mistakes — full list

| Mistake | Why bad | Fix |
|---|---|---|
| FitToPage left on | Tooltip rescales to fit the hover popup, text blurs | ActualSize (Legacy int `3` / enhanced string `"ActualSize"`) |
| Full 1280×720 page reused as a tooltip | Covers the source chart entirely | 320×240 … 550×500 (or the report's established profile) |
| Critical info only in tooltip | Touch/keyboard users never see it | Duplicate on page, or `pbi-drillthrough` |
| 4+ visuals, heavy measures on the tooltip page | Every hover fires all queries — laggy report | ≤3 visuals; `power-bi-dax-optimization` |
| Slicers/buttons on tooltip page | A tooltip cannot be interacted with | Remove — read-only content only |
| Tooltip page visible in nav | Users land on a broken mini page | Hide (Legacy `"visibility": 1` / enhanced `"HiddenInViewMode"`) |
| Text under 8 pt to cram in content | Unreadable at hover size | Cut content — one question per tooltip |
| Per-tooltip ad-hoc styling (colors/fonts set per visual) | Theme drift across the report (`pbi-design-system` antipatterns A1/A7) | Tokens + theme's `visualTooltip` defaults, set once |
| Multi-field `cardVisual` (2 fields) | Renders as two narrow stubs | One single-field card per number, 148×64 |
| 8-pt label + 16-pt value crammed into h=44 | Text clips — doesn't fit | h=64 (heights from I-12 table) |
| Trend with 24-month categorical axis in a narrow chart | Horizontal scrollbar ("white rectangle") | TopN-12 filter on the month field: `filterConfig` `In` + `Subquery` `Top:12`, `OrderBy` Aggregation Max on the sort column |

## Related skills

- `powerbi-visuals` — general wiring mechanics, `visualHeader`/`displayOption` JSON; per-visual report-page tooltip canon — see the binding section above.
- `pbi-drillthrough` — right-click detail pages; shares the `SELECTEDVALUE` context-header pattern.
- `dax-measures` — tooltip measure conventions; `power-bi-dax-optimization` — keeping them cheap.
- `dax-svg` / `deneb-vegalite` — sparkline-grade vs richer detail visuals inside a tooltip.
- `pbi-theme-json` — generating/editing the theme's `visualTooltip` common card.
