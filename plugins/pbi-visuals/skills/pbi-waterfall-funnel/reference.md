# Waterfall & Funnel — Reference

Companion to `SKILL.md`. Names below are verified against `docs/research/theme-visuals.md`
(reportThemeSchema 2.143 = 2.155) or must be read from a real report file before use — never
recalled from memory (BRIEF F2). Tokens (`color/*`, `ramp/*`, `type/*`) resolve in
`docs/DESIGN-TOKENS.md`.

## 1. Visual-type keys (verified, theme-visuals.md §5)

| Key | Format-pane name | Trap |
|---|---|---|
| `waterfallChart` | Waterfall chart | not `waterfall` |
| `funnel` | Funnel | not `funnelChart` — the schema key dropped "Chart" |

Both keys go under `visualStyles` like any other chart (theme-visuals.md §4); style once at
`"*"` scope unless a variant genuinely differs.

## 2. Sentiment colors — the verified mechanism

`docs/research/theme-visuals.md` §2.1 confirms: **`good`, `neutral`, `bad` are top-level
theme keys documented as "status colors for waterfall and KPI visuals."** This is the
primary, verified lever for waterfall increase/decrease/total coloring — set once in the
theme, not per visual:

```json
{
  "name": "report-theme",
  "dataColors": ["#063E61", "#3781F0", "#FFC107", "#2B9348",
                 "#D64550", "#3C648A", "#79B0FF", "#916400"],
  "good":    "#2B9348",
  "neutral": "#FFC107",
  "bad":     "#D64550"
}
```

Mapping to the bridge: `good` → increase bars, `bad` → decrease bars, `neutral` → total/
start/end bars. DESIGN-TOKENS §1.5 fixes the theme sentiment values at `good = #2B9348`,
`neutral = #FFC107`, `bad = #D64550` — the same `neutral` key also serves warning/watchlist
states elsewhere in the theme, so accept `#FFC107` as the report-wide total/start/end color
by default; do not invent a second "neutral" hex just for the bridge (anti-drift, one theme
= one meaning per key). A DAX "field value" conditional-formatting measure can reference
these same names directly as strings (`"good"`, `"bad"`) per DESIGN-TOKENS §1.7 — useful
when a Breakdown sub-driver needs an exception color; write the measure via `dax-measures`,
wire the CF via `powerbi-visuals`.

**Not verified in this corpus — read from the schema or a ground-truth visual before
emitting:** the specific per-visual override cards (Format pane "Sentiment colors" section,
"Increase"/"Decrease"/"Total" sub-properties; the "Breakdown" and "Detail labels" cards).
Only the visual-type keys and the top-level `good`/`neutral`/`bad` mechanism above are
confirmed against research; everything else is native, documented Power BI UI vocabulary,
not a verified JSON shape — do not hand-write it from recall. If a ground-truth report
already styles such a card, copy its exact shape. Per-visual `objects` overrides reference
sentiment colors via `ThemeDataColor` expr where the ground truth does (DESIGN-TOKENS §1.7,
"objects" row); the named-token fill form `{"solid": {"color": "good"}}` is verified only
for theme-level `visualStyles` cards — never re-hardcode either as raw hex.

## 3. Waterfall specifics

- **Field wells** (UI concept, binding mechanics → `powerbi-visuals`): Category, **Breakdown**
  (splits one bar into named sub-contributors), Y-axis (value), Tooltips. Breakdown is what
  turns "Revenue changed +12%" into "+8% price, +5% volume, −1% mix."
- **Cap the bar count.** ≤ 8 bars including start/end; a Breakdown that explodes past that
  needs a "other drivers" bucket (helper measure → `dax-measures`), same discipline as any
  categorical chart (DESIGN-TOKENS §1.5 "max 6–8 categories before grouping").
- **Connectors** default on; they are the thin lines tracing the running total between bars —
  the reason a waterfall reads as a bridge instead of a disconnected bar chart. Turn off only
  in dense multi-page bridges where they become visual noise.
- **Running total as a number**, not just a shape: if the audience needs to read the exact
  end value, add a labeled total bar or a reference line rather than relying on eyeballing
  cumulative bar tops.
- **Orientation:** the native visual renders vertically only. A horizontal bridge (long
  category names, many drivers) is not a native option — route to `deneb-vegalite`.

## 4. Funnel specifics

- **Order is data, not decoration.** The stage sequence must match the actual process order
  in the model (e.g. a `sortByColumn` on an explicit stage-rank field via the semantic
  model) — never let the visual auto-sort by value, which is the default behavior for most
  other charts and the wrong one here.
- **Color encodes depth, not category.** Each stage is the *same* metric measured further
  down one process, not a different thing — use `ramp/brand-seq` monochrome (lighter →
  darker with depth) or a single `color/brand` fill. A distinct hue per stage implies
  unrelated categories and misleads (Common Mistakes table).
- **Conversion labels.** The native Detail-labels setting supports value, "percent of first
  stage," and "percent of previous stage." Percent-of-first tells the audience the overall
  yield; percent-of-previous tells them where the leak is. Pick (or show both) based on the
  question the page is answering — don't default to raw counts alone.
- **Critical review (BRIEF F7).** Funnel width/area is a weak perceptual encoding
  (Cleveland–McGill: area ranks below position/length). Beyond ~5–6 stages, or whenever the
  reader must compare two similar-sized stages precisely, replace the funnel with sorted
  stage bars (natural process order, not value-sorted) plus conversion-% data labels —
  `pbi-bar-column-charts` covers the bar mechanics. State this trade-off explicitly rather
  than defaulting to funnel because the process "sounds like a funnel."

## 5. Native vs. custom (`deneb-vegalite`) decision

Reach for `deneb-vegalite` only when the native visual has a real gap, not by default
(skills-inventory.md #19: "custom waterfall, if native doesn't hold up"):

| Need | Native holds up? | Route |
|---|---|---|
| Standard vertical bridge, ≤ 8 bars, Breakdown | Yes | `waterfallChart` |
| Horizontal bridge | No (vertical-only) | `deneb-vegalite` |
| Custom per-segment coloring beyond good/neutral/bad/Breakdown CF | Partial | Try CF via `dax-measures`/`powerbi-visuals` first; Deneb if insufficient |
| Standard single-path funnel with conversion % | Yes | `funnel` |
| Funnel with branching paths / multiple parallel funnels compared | No (single path only) | `deneb-vegalite` or side-by-side `funnel` visuals with a shared axis |

## 6. Sizing

Standard "Chart row height" sizing applies (240/280/320 px, DESIGN-TOKENS §3.2). Waterfalls
with many Breakdown bars need the wider end of that range or a half/third-width block (§3.2)
rather than shrinking bar labels below `type/small` (9 pt).
