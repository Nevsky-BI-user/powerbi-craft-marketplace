# pbi-color-accessibility — Reference

> All ratios below were **computed** with the WCAG 2.x relative-luminance formula (§1), not
> copied from memory or from `pbi-design-system` prose. Where a computed value differs from a
> rounded annotation elsewhere, the number here wins — cite it as evidence.
> Token hex values are `pbi-design-system` / `pbi-design-system`; this file only adds contrast
> math, colorblind checks, and gradient text-safety zones on top of them.

---

## 1. WCAG contrast formula (compute, don't guess)

```
srgb_to_lin(c) = c/12.92                          if c ≤ 0.03928
               = ((c+0.055)/1.055) ^ 2.4           otherwise      (c = channel/255)

rel_luminance(hex) = 0.2126·R_lin + 0.7152·G_lin + 0.0722·B_lin

contrast(hexA, hexB) = (L_lighter + 0.05) / (L_darker + 0.05)
```

Thresholds: normal text ≥ **4.5:1**; large text (≥18 pt, or ≥14 pt bold — e.g.
`type/callout-hero`, `type/hero`) ≥ **3:1**; non-text graphical objects (bars, lines, icons,
focus outlines) ≥ **3:1** against the adjacent color. Reference implementation (Python,
adapt inline for any pair not in the tables below — never eyeball a new hex):

```python
def srgb_to_lin(c):
    c = c / 255.0
    return c/12.92 if c <= 0.03928 else ((c+0.055)/1.055) ** 2.4

def rel_lum(hex_):
    hex_ = hex_.lstrip('#')
    r, g, b = (int(hex_[i:i+2], 16) for i in (0, 2, 4))
    r, g, b = srgb_to_lin(r), srgb_to_lin(g), srgb_to_lin(b)
    return 0.2126*r + 0.7152*g + 0.0722*b

def contrast(c1, c2):
    l1, l2 = rel_lum(c1), rel_lum(c2)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)
```

Sanity checks: `contrast('#000000', '#FFFFFF')` = 21.00 (max possible); `contrast('#767676',
'#FFFFFF')` = 4.54 (the classic "AA gray" reference value) — use these to confirm any
reimplementation before trusting its output.

---

## 2. Verified pairs — semantic tokens (`pbi-design-system` §1)

| Pair | Ratio | Verdict |
|---|---|---|
| `color/text-title` `#063E61` on white | 11.23:1 | Normal text |
| `color/text-body` `#333333` on white | 12.63:1 | Normal text |
| `color/text-secondary` `#605E5C` on white | **6.46:1** | Normal text (higher than the 4.6:1 noted in `pbi-design-system` §1.4 — that figure looks based on the generic `#767676` AA-gray benchmark, not this exact hex; both pass, cite 6.46:1) |
| `color/text-disabled` `#9E9F9F` on white | 2.65:1 | Fails AA — disabled/inactive only, never body text |
| White on `color/brand` `#063E61` | 11.23:1 | Normal text |
| White on `color/good` `#2B9348` | 3.91:1 | Large text / marks only |
| `color/good-text` `#107C10` on white | 5.37:1 | Normal text |
| White on `color/bad` `#D64550` | 4.35:1 | Large text / marks only |
| `color/bad-text` `#D13438` on white | 4.93:1 | Normal text |
| `#333333` on `color/warning` `#FFC107` | 7.75:1 | Normal text — always use dark text on warning fill |
| White on `color/warning` `#FFC107` | 1.63:1 | Fails — never white text on warning |
| `color/warning-text` `#916400` on white | 5.22:1 | Normal text |
| White on `color/neutral-data` `#3C648A` | 6.21:1 | Normal text |
| `color/accent` `#3781F0` on white (either direction) | 3.78:1 | Large text / marks only — not for small body text |
| `color/selection-tint` `#C9DDFB` on white | 1.38:1 | Non-text chip fill; pair with a border or bold, don't rely on the tint alone for a boundary |
| `color/border` `#E6E6E6` on white | 1.25:1 | Below 3:1 non-text — a divider, not a component boundary that must itself carry meaning |

---

## 3. Sequential ramp (`ramp/brand-seq`) — text-on-fill safety zones

Verified per step, dark text = `#333333`, light text = `#FFFFFF`:

| Step | Hex | Dark text | White text | Safe for normal-size on-fill text? |
|---|---|---|---|---|
| seq-100 | `#E6ECEF` | 10.59:1 | 1.19:1 | Dark text only |
| seq-200 | `#C1CFD8` | 7.93:1 | 1.59:1 | Dark text only |
| seq-300 | `#9BB2C0` | 5.73:1 | 2.21:1 | Dark text only |
| seq-400 | `#6A8BA0` | 3.50:1 | 3.61:1 | **Dead zone** — neither color reaches 4.5:1 |
| seq-500 | `#386581` | 2.01:1 | 6.27:1 | White text only |
| seq-600 (brand) | `#063E61` | 1.12:1 | 11.23:1 | White text only |

**Rule:** light half (100–300) → dark text; dark half (500–600) → white text; **seq-400 is
unsafe for either** at normal text size (9–12 pt). If a heatmap/choropleth CF gradient spans
the full ramp and a value label must sit directly on the fill: either (a) bump that label to
large/bold (≥14 pt bold clears the 3:1 floor at 3.50–3.61), or (b) don't render the value on
the fill at all — use a separate data-bar/icon column, or keep the number in a fixed-color
cell next to a small color chip instead (pattern C in SKILL.md).

## 4. Diverging ramp (`ramp/diverging`) — named stops

| Stop | Hex | Text | Ratio |
|---|---|---|---|
| minimum | `#D13438` | White | 4.93:1 (normal) |
| center | `#F3F2F1` | `#333333` | 11.30:1 (normal) |
| maximum | `#107C10` | White | 5.37:1 (normal) |

The three *named* stops are all safe with the pairing shown. A rendered 3-stop gradient
interpolates continuously between them; the dead zones below are **computed** by per-channel
linear interpolation of the hex stops (WCAG formula §1) — actual PBI rendering may differ
slightly, so sample the real fill for borderline values:

| Half-ramp | Dark `#333333` safe | White safe | **Dead zone** (neither ≥4.5:1) |
|---|---|---|---|
| `minimum→center` (#D13438→#F3F2F1) | from ≈`#DF8082` (t≥0.4) toward center | only at the `#D13438` stop itself (4.93:1) | ≈`#D4474A`…`#DB6D70` (t 0.1–0.3) |
| `center→maximum` (#F3F2F1→#107C10) | until ≈`#6BAB6A` (t≤0.6) from center | only from ≈`#278826` (t≥0.9, 4.53:1 borderline) | ≈`#549F54`…`#3D943D` (t 0.7–0.8) |

Practical guidance: pattern (B) flip-font-color-at-the-rule, or pattern (C) keep text off the
fill; values whose fill lands in a dead-zone band have NO compliant on-fill text color for
normal size — route those labels off-fill (C). Pattern B skeleton (DAX via `dax-measures`,
CF wiring via `powerbi-visuals`):

```dax
On-Fill Label Color =
-- _pos: value's normalized position on the ramp domain (-1 = minimum stop, +1 = maximum)
VAR _pos = DIVIDE ( [Deviation vs Plan], [Ramp Domain Half-Width] )
RETURN SWITCH ( TRUE(),
    _pos <= -0.99, "White",   -- white-safe only at the extreme red stop (4.93:1)
    _pos >=  0.90, "White",   -- white-safe from ≈#278826 (4.53:1, borderline)
    "#333333" )               -- dark text elsewhere; dead-zone bands → pattern (C)
```

## 5. RAG 6-step ramp (`ramp/rag`) — text-on-fill safety

| Step | Hex | Dark `#333333` | White | Best choice |
|---|---|---|---|---|
| rag-1 | `#009051` | 3.07:1 | 4.11:1 | Neither reaches 4.5:1 — large/bold text only (white slightly better) |
| rag-2 | `#02BD3D` | 5.02:1 | 2.52:1 | Dark text |
| rag-3 | `#C2E330` | 8.62:1 | 1.47:1 | Dark text |
| rag-4 | `#FFE521` | 9.92:1 | 1.27:1 | Dark text |
| rag-5 | `#FF7E0D` | 4.96:1 | 2.55:1 | Dark text |
| rag-6 | `#F23711` | 3.21:1 | 3.94:1 | Neither reaches 4.5:1 — large/bold text only (white slightly better) |

**Rule:** dark `#333333` text is safe for steps 2–5; steps 1 and 6 (the most saturated green
and red) are large/bold-text-only zones for on-fill labels — for normal-size text on those
two steps, move the value off the fill.

## 6. Colorblind-safe categorical palette (Okabe–Ito) — contrast-checked

Okabe–Ito is differentiable under deuteranopia/protanopia/tritanopia, but that does **not**
imply WCAG-safe against a white Power BI canvas — check every hue before using it as a thin
line or small marker:

| Hue | Hex | On white | Non-text ≥3:1? |
|---|---|---|---|
| Blue | `#0072B2` | 5.19:1 | Pass |
| Orange | `#E69F00` | 2.25:1 | **Fail** |
| Bluish green | `#009E73` | 3.42:1 | Pass |
| Pink | `#CC79A7` | 3.06:1 | Pass (marginal) |
| Sky | `#56B4E9` | 2.31:1 | **Fail** |
| Vermillion | `#D55E00` | 3.87:1 | Pass |
| Yellow | `#F0E442` | 1.32:1 | **Fail** |
| Black | `#000000` | 21.00:1 | Pass |

Orange, sky, and yellow fail the 3:1 non-text minimum on a white canvas as thin lines/points
(no border). For those three: either darken ~15–20% (consistent with the project's own
`ThemeDataColor { Percent: -0.2 }` shading mechanic) before use as a line/marker series, or
give the mark a ≥1 px darker outline/stroke so the boundary itself carries the contrast, or
reserve them for filled areas ≥3 px wide with an adjacent border. Never use them for text.

**Do not conflate `color/warning` `#FFC107` with Okabe–Ito orange `#E69F00`.** They are
different hexes: on white, `#FFC107` is **1.63:1** (§2) — worse than `#E69F00`'s 2.25:1 —
failing both the 4.5:1 text and 3:1 non-text minimums, so the same darken/stroke mitigations
above are mandatory for it as a thin mark, and it is never a text color on white.

## 7. Redundant coding checklist (color never alone)

| Encode meaning with | Mechanics |
|---|---|
| ▲▼ trend icon next to the value | PNG from `icon-set-manager` (brand `#063E61`, transparent, 64 px) |
| Direct label / data label | `powerbi-visuals` (labelPosition, format) |
| Position or sort order | Sorted bars/ranked table rows — meaning survives grayscale by construction |
| Weight or line style | Bold/Semibold for "selected", dashed for "target/forecast" vs solid "actual" |

## 8. CF color plumbing (theme ↔ DAX) — verified names only

- Theme JSON sentiment/gradient keys (verified, theme-visuals.md §2.1): `good`, `neutral`,
  `bad` (status colors, e.g. waterfall/KPI); `maximum`, `center`, `minimum`, `null`
  (divergent gradient stops).
- DAX "Field value" conditional formatting accepts these **named theme color strings**
  returned from a measure (verified, theme-visuals.md §2.1):

  | Theme JSON key | DAX string |
  |---|---|
  | `maximum` | `"maxColor"` |
  | `center` | `"midColor"` |
  | `minimum` | `"minColor"` |
  | `null` | `"nullColor"` |
  | `good` / `bad` / others | same name, e.g. `"good"`, `"bad"` |

- Gradients inside `visualStyles` fill objects use `fillRule` with `linearGradient2`/`3`
  (verified, theme-visuals.md §4) where the property supports it.
- Writing the actual CF rule object / `fillRule` JSON, and deciding rule *thresholds*
  (when to color, how many buckets) is `powerbi-visuals` / `pbi-conditional-formatting` —
  this skill only supplies which colors are safe to plug into those rules and why.

## 9. Shipping checklist

1. Every NEW color pair (not already in §2–5) has a computed ratio, using §1's formula.
2. Any CF gradient/heatmap/choropleth checked across its full range, not just its named
   stops — cite the dead zone if one exists (§3–5 pattern).
3. Categorical palette ≤ 6–8 hues, brand-first; if Okabe–Ito substitutes are used, each hue
   checked against §6 before being used as a thin mark.
4. No sentiment hue (`good`/`bad`/`warning`) reused as a plain categorical color elsewhere on
   the same page.
5. Every red/green (or RAG-ramp) encoding paired with an icon, label, or position — never
   color alone.
6. Any fill carrying transparency: rated on the BLENDED color (§11), **and** its
   `dataPoint.borderShow` state recorded — a solid same-color border can supply the ≥3:1
   boundary the pale fill cannot (§11a).

## 10. Auditing a whole report — systematic, not by eye

The per-pair checks above are for colors you are *adding*. To audit a *finished* report — the
failure mode that ships light-on-light bands and dark-on-dark pills because contrast was
judged "by eye" — enumerate every color; do not spot-check.

**Method.**
1. Extract every hex: from `theme.json` `visualStyles`, from each visual's `objects` /
   `visualContainerObjects`, and from every hex literal inside SVG-measure / DAX strings and
   `dataBars` colors. (Top-level theme colors may be 8-digit — the last 2 digits are alpha,
   theme-visuals.md §1.)
2. Compute `rel_lum` (§1) for each; for every foreground/background pair that actually
   overlaps, compute `contrast`.
3. Flag pairs below the floor: **< 4.5:1** for value/label text, **< 3:1** for large text
   (≥18 pt, or ≥14 pt bold) and for non-text marks (bars, lines, chip fills). Report the
   computed ratio for each flagged pair — never "looks fine".

**In-cell graphics count as text.** A number inside an SVG chip/badge, a data-bar label, or a
KPI pill is text: its background is the **fill directly under the glyphs**, not the page or
the cell. Measure the value against the chip fill, not the report canvas.

**A swatch or caption that demonstrates a color.** A legend chip painted in the very token it
documents, and a caption painted in "the text color that would sit ON the fill", are both
measured against the surface they **actually** sit on — usually the card, not the fill. In a
verified case the legend line `min: white text 6.18:1` was painted `#f1f5f9` and vanished on
a white card. Fix: for any sample whose contrast to its own surface is < 3:1, use an outline
glyph (`◻` / `○`) in a readable neutral plus the hex in the caption; paint a text-color demo
caption in a neutral, never in the color it demonstrates.

**Semi-transparent fills — blend first.** A pill drawn at `opacity=0.18` (or an 8-digit-hex
fill carrying alpha) is *not* its nominal color. Alpha-composite it over the real background,
then run §1 against the effective color:

```python
def blend(fill, bg, alpha):   # alpha 0..1, '#RRGGBB' strings
    f = [int(fill.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
    b = [int(bg.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]
    e = [round(alpha*fc + (1-alpha)*bc) for fc, bc in zip(f, b)]
    return '#%02X%02X%02X' % tuple(e)
```

A faint chip over a dark `#0f172a` page collapses to nearly the page color, so colored text
on it is near-invisible even though the nominal fill hex looked saturated.

A blended fill below 3:1 is **not automatically a defect** for a chart data point: check
`dataPoint.borderShow`/`borderColorMatchFill` before flagging it — the border may already be
carrying the boundary (§11a).

**Dark-canvas caveat.** On a dark page, medium-gray fills/accents — `#475569`, `#64748b` and
darker — carry almost no contrast against the background and read as black/dead. For accents
or marks that must be seen, use bright tokens only (e.g. `#34d399`, `#fcd34d`, `#f87171`,
`#22d3ee`); this is the §6 rule (a mark must itself clear ≥3:1 against its adjacent color)
applied to a dark canvas.

## 11. Transparency tuned for one canvas fails on the other

`fillTransparency` (and any `transparency` property) is a **percentage of transparency**, not
alpha: `alpha = 1 − t/100`. A theme-level `visualStyles["*"]["*"].dataPoint.fillTransparency`
chosen on a dark canvas — where a bright accent read through 50% looks fine — washes that
same accent out once the canvas turns light:

```
blended = fg × (1 − t/100) + bg × (t/100)

fg #4f46e5 over a white card:
  t=50 → #a7a2f2   2.31:1   fails the 3:1 non-text minimum
  t=30 → #847eed   3.39:1   passes
  t=20 → #726bea   4.19:1   passes — the value actually shipped
```

Run §1 on the **blended** color, never on the source hex, and compare against **3:1**
(non-text graphics), not 4.5:1.

### 11a. A translucent fill can borrow its boundary from the data-point BORDER

**Rule: a fill that fails 3:1 has TWO legal fixes, not one — lower the transparency, OR turn
on a solid data-point border in the fill's own color. Never report "the fill fails 3:1"
without first checking whether `dataPoint.borderShow` is on.**

`dataPoint` carries its own border keys, separate from the fill keys. Verified in the shipped
`sqlbi-light` theme at `visualStyles["*"]["*"].dataPoint`, sitting right next to the
`fillTransparency: 20` from І-17:

| Key | What it does | Shipped value |
|---|---|---|
| `borderShow` | draws the data-point outline | `true` |
| `borderSize` | outline width, px | `2` |
| `borderColorMatchFill` | outline takes the shape's own (series/fill) color | `true` |
| `borderOutlineOnly` | hide inner borders — outer edge only | `true` |
| `borderTransparency` | the border's OWN transparency; `fillTransparency` never dilutes it | unset (opaque) |

The border is painted in the **undiluted** hex, so it keeps exactly the contrast the blended
fill threw away (§1 formula, same accent `#4f46e5`):

| What is measured | vs a white card | vs canvas `#f1f5f9` |
|---|---|---|
| Fill at `fillTransparency: 50` → `#a7a2f2` | 2.31:1 **fail** | 2.22:1 **fail** |
| Fill at `fillTransparency: 20` → `#726bea` | 4.19:1 pass | 3.93:1 pass |
| Solid 2 px border `#4f46e5` (`borderColorMatchFill`) | **6.29:1** pass | **5.74:1** pass |

**This is why "ghost" bars/columns still read.** What must clear 3:1 for a non-text mark is
the shape's boundary against the adjacent color; a 2 px same-color outline supplies that
boundary on its own, so a deliberately washed-out fill (density, overlap, target/ghost
series) stays compliant without being darkened.

Apply it:

- **State both halves in an audit.** "`#a7a2f2` = 2.31:1, fails" is half an answer if
  `borderShow: true` is in the theme — report the blended fill ratio AND the border ratio.
- **Keep the pale fill when the design needs it**: set `borderShow: true` + `borderSize` ≥ 2 +
  `borderColorMatchFill: true` instead of re-darkening every series.
- **`borderColorMatchFill: false` voids the guarantee** — a hand-picked border hex must be
  contrast-checked against the canvas like any other mark; matching the fill is what makes the
  border inherit the series' contrast automatically.
- Same mechanic as §6's "give the mark a darker outline": the outline, not the fill, is what
  carries the ≥3:1 boundary for thin or pale marks.

**Shadows are the same class.** A `dropShadow` built for a dark theme (`#000d1a`,
transparency 20, distance 5) reads as a dirty smudge on a light surface; the verified fix was
transparency 88 / blur 12 / distance 2.
