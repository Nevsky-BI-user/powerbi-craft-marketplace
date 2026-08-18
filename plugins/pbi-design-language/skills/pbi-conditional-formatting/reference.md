# Power BI Conditional Formatting — Reference

Companion to `SKILL.md`. Names below are verified against `docs/research/theme-visuals.md`
(reportThemeSchema 2.143 = 2.155) or `docs/DESIGN-TOKENS.md` — never recalled from memory.

## 1. What is actually verified vs. what to read from ground truth

**Verified (safe to state as fact):**

- Theme-level sentiment keys `good`/`neutral`/`bad` and divergent gradient stops
  `maximum`/`center`/`minimum`/`null` exist at theme top level and feed CF color pickers
  (theme-visuals §2.1).
- DAX "Field value" CF accepts a **named theme color string** returned by a measure. The
  divergent names differ between the theme JSON and the DAX reference:

  | Theme JSON key | DAX reference name |
  |---|---|
  | `maximum` | `maxColor` |
  | `center` | `midColor` |
  | `minimum` | `minColor` |
  | `null` | `nullColor` |
  | `good`, `bad`, `background`, `tableAccent`, … | same name in DAX |

- Gradient fills support `fillRule` with `linearGradient2`/`linearGradient3` "where the
  property supports them" (theme-visuals §4, verified schema fact).
- **CF rules themselves cannot be themed** — the theme only supplies gradient endpoint
  colors and defaults; per-column/per-visual rule thresholds live in the visual's own
  `objects`, not in `theme.json` (theme-visuals §7, pitfall 11).

**Not verified in this repo's research — do not invent, read from a ground-truth CF'd
visual in the target report or delegate to `powerbi-visuals`:** the exact placement and
key names of stepped "rules" thresholds inside `visual.json`/`report.json` `objects`
(e.g. rule case list, operator enums, per-step color/value pairs), and any per-visual
icon-set property names. BRIEF F2: exact names come only from theme-visuals.md, a real
file, or the schema.

## 2. The one verified JSON fragment (theme-level CF color sources)

Real, schema-backed shape — the sentiment + divergent keys a theme exposes for every CF
dialog in the report (values = DESIGN-TOKENS §1.1/§1.3 canonical tokens):

```json
{
  "good": "#2B9348",
  "neutral": "#FFC107",
  "bad": "#D64550",
  "maximum": "#107C10",
  "center": "#F3F2F1",
  "minimum": "#D13438",
  "null": "#9E9F9F"
}
```

Set these ONCE in the report's theme (`pbi-theme-json` / `modifying-theme-json`); every
CF dialog (gradient, field-value `maxColor`/`midColor`/`minColor`/`nullColor`/`good`/`bad`)
then reads from here instead of re-typing hex per visual (antipattern A1/A9).

## 3. Ramp selection by mechanism

| Ramp | Values | Mechanism it feeds |
|---|---|---|
| `ramp/rag` | `#009051 #02BD3D #C2E330 #FFE521 #FF7E0D #F23711` | Rules (stepped) — 6 discrete thresholds, green→red |
| `ramp/brand-seq` | `#E6ECEF #C1CFD8 #9BB2C0 #6A8BA0 #386581 #063E61` | Gradient, magnitude/heat — single hue, dark = more, never rainbow |
| `ramp/diverging` | `#D13438 ← #F3F2F1 → #107C10` | Gradient, deviation — midpoint = target/zero/100% of plan, never the data mean |

Binary comparisons (e.g. above/below plan as two states, not a scale) prefer
`#063E61` vs `#FFC107`/`#E69F00` — colorblind-safe blue/orange, not red/green.

## 4. DAX field-value pattern (logic only — wiring is `powerbi-visuals`)

The measure returns a color; write the actual measure via `dax-measures`. Shape to hand
off (standard DAX, not a Power BI schema — safe to write directly):

```dax
CF Status Color =
VAR _attainment = [Attainment %]
RETURN
    SWITCH(
        TRUE(),
        _attainment >= 1,    "good",
        _attainment >= 0.85, "neutral",
        "bad"
    )
```

Bind this measure via the Format pane's "Field value" CF (mechanics: `powerbi-visuals`).
Use field value over rules when the threshold logic is compound (multiple conditions,
exceptions, cross-measure comparisons) rather than a single stepped scale.

## 5. Icon sets

- Status/direction glyphs (▲▼, RAG dot, check/x) as PNG assets come from
  `icon-set-manager` (brand `#063E61`, 64 px default, transparent background).
- Legacy theme `icons` array (pre-2019 built-in CF icon sets) still parses but is rarely
  used today (theme-visuals §1) — prefer PNG icon + measure-driven CF color over it for
  visual consistency with the rest of the report.
- Accessibility: icon is never the only signal — pair with the colored value and/or a
  text label; set alt text on the visual (`altText`/`altTextColumns` per visual type).

## 6. Decision order (data question → mechanism)

1. Few named states, simple thresholds (≤4) → **Rules**, colors from `ramp/rag` or theme
   sentiment keys.
2. Continuous magnitude across many rows/cells (heat map) → **Gradient**, `ramp/brand-seq`.
3. Continuous deviation from a target/zero/plan → **Gradient**, `ramp/diverging`, midpoint
   set explicitly to the target — never left at "auto"/data mean.
4. Compound logic, exceptions, or cross-measure conditions → **Field value**, measure via
   `dax-measures` returning a named theme color.
5. Any of the above at a glance in a dense grid → add an **icon set**, never replace the
   color/value with the icon alone.

## 7. Data bars — canonical PBIR structure (crash-class)

Data bars are a per-column CF with a **fixed value structure**. Law: Desktop silently
ignores an unknown property *name*, but an invalid *value structure* on a *known* property
(here `dataBars`) **crashes the entire report** — "Failed to load report", no details.
Hand-authored data bars are a frequent trigger, so treat this as ground-truth-only.

**Verified canonical shape** (PDP report saved by Desktop): `dataBars` lives under the
`columnFormatting` object, keyed to one measure by a `metadata` selector, and has **exactly
six sub-keys** — three colors and three literals:

| Sub-key | Value shape |
|---|---|
| `positiveColor` | `{ "solid": { "color": { "expr": … } } }` |
| `negativeColor` | `{ "solid": { "color": { "expr": … } } }` |
| `axisColor` | `{ "solid": { "color": { "expr": … } } }` |
| `reverseDirection` | `{ "expr": { "Literal": … } }` |
| `hideText` | `{ "expr": { "Literal": … } }` |
| `totalMatchingOption` | `{ "expr": { "Literal": … } }` |

```json
"columnFormatting": [
  {
    "properties": {
      "dataBars": {
        "positiveColor": { "solid": { "color": { "expr": {  } } } },
        "negativeColor": { "solid": { "color": { "expr": {  } } } },
        "axisColor":     { "solid": { "color": { "expr": {  } } } },
        "reverseDirection":    { "expr": { "Literal": { "Value": "false" } } },
        "hideText":            { "expr": { "Literal": { "Value": "false" } } },
        "totalMatchingOption": { "expr": { "Literal": { "Value": "…" } } }
      }
    },
    "selector": { "metadata": "Sales.Total Sales" }
  }
]
```

**Rules:**

- Use **only** those six sub-keys. `minValue`/`maxValue` (or any other invented key) **do
  not exist** in this structure — adding them crashes the whole report.
- `dataBars` belongs **only** under `columnFormatting` with `selector.metadata` =
  `"<Table>.<Measure>"`. It does **not** exist under the `values` object — placing it there
  also crashes the report.
- Verified facts here are the six sub-key names, their color/literal value shapes, the
  `columnFormatting` home, and the `metadata` selector. The color `expr` internals are the
  standard CF color expr (§1 / `powerbi-visuals`); the `Literal` payloads and the
  array/`properties` envelope are not fully documented — **copy them verbatim from a column
  you styled in Desktop and saved**, never hand-invent (BRIEF F2).
