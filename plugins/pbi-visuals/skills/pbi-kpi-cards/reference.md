# KPI Cards — Reference

Companion to `SKILL.md`. Card/property names verified against `reportThemeSchema-2.155.json`
(schema introspection) and an audit of a real report.json (card
`e27a80bd6af9b1c61380`, Group Profile). Tokens (`color/*`, `type/*`, `shape/*`) resolve in
`pbi-design-system`.

## 1. Visual-type keys and their cards (schema-verified)

| Visual key | Cards beyond common (`title`, `subTitle`, `background`, `border`, `padding`, `visualHeader`, `dropShadow`, `general`) |
|---|---|
| `cardVisual` | `value`, `label`, `layout`, `fillCustom`, `shapeCustomRectangle`, `accentBar`, `referenceLabel`, `referenceLabelTitle`, `referenceLabelValue`, `referenceLabelDetail`, `referenceLabelLayout`, `cardCalloutArea`, `cardImage`, `image`, `divider`, `glowCustom`, `grid`, `outline`, `overFlow`, `rotation`, `shadowCustom`, `spacing`, `smallMultiples*` (8 cards: AccentBar/Border/CellBackGround/Grid/Header/Layout/OuterShape/OverFlow) |
| `kpi` | `indicator`, `status`, `goals`, `trendline`, `lastDate` |
| `multiRowCard` | `card`, `cardTitle`, `categoryLabels`, `dataLabels` |
| `card` (classic) | `categoryLabels`, `labels`, `wordWrap` |

`card` ≠ `cardVisual` — entirely different property sets, not just an old/new naming split
(kills antipattern A11). `card` has no `value`/`fillCustom`/`layout` cards at all.

## 2. Key property names, per card

| Card | Verified properties |
|---|---|
| `cardVisual.value` | `$id`, `bold`, `customFormatString`, `fontColor`, `fontFamily`, `fontSize`, `horizontalAlignment`, `italic`, `labelDisplayUnits`, `labelPrecision`, `show`, `showBlankAs`, `textWrap`, `transparency`, `underline` |
| `cardVisual.label` | `$id`, `alignBaselines`, `bold`, `fontColor`, `fontFamily`, `fontSize`, `heading`, `horizontalAlignment`, `italic`, `matchValueAlignment`, `position`, `show`, `text`, `textWrap`, `transparency`, `underline` |
| `cardVisual.accentBar` | `$id`, `color`, `position`, `show`, `transparency`, `width` |
| `cardVisual.referenceLabelValue` | `$id`, `customFormatString`, `show`, `showBlankAs`, `textWrap`, `valueBold`, `valueDisplayUnits`, `valueFontColor`, `valueFontFamily`, `valueFontSize`, `valueItalic`, `valuePrecision`, `valueTransparency`, `valueUnderline` |
| `kpi.status` | `badColor`, `direction`, `goodColor`, `neutralColor` |
| `kpi.indicator` | `bold`, `fontColor`, `fontFamily`, `fontSize`, `horizontalAlignment`, `iconSize`, `indicatorDisplayUnits`, `indicatorPrecision`, `italic`, `showIcon`, `underline`, `verticalAlignment` |
| `kpi.goals` | `direction`, `goalText`, `showGoal`, `showDistance`, `distanceLabel`, `goalFontColor`, `distanceFontColor`, `titleFontSize`, `labelPrecision` (+ bold/italic/underline variants) |
| `multiRowCard.card` | `barColor`, `barShow`, `barWeight`, `cardBackground`, `cardPadding`, `outlineColor`, `outlineStyle`, `outlineWeight` |
| common `title`/`border`/`background`/`padding` (`card`/`multiRowCard`/`kpi`) | `title`: `show`, `text`, `fontSize`, `fontColor`, `bold`, `alignment`, `titleWrap`; `border`: `show`, `color`, `radius`, `width`; `background`: `show`, `color`, `transparency`; `padding`: `top`/`left`/`right`/`bottom`. **`cardVisual` OVERRIDES these**: its `border` = `color`/`show`/`style`/`transparency`/`width` (NO `radius` — radius via `layout.rectangleRoundedCurve`), its `padding` = `$id`/`*Margin`/`paddingIndividual`/`paddingSelection`/`paddingUniform` |

Any property not in this table: read the schema file or a ground-truth visual — never guess.

## 3. Reference recipe — the etalon card

Empirically confirmed pattern across all 514 `cardVisual` in the production report
(from that audit) — use as the structural AND parity template for new/restyled cards.
Shown as annotated pseudo-JSON (card → array of style objects, per the real
`config.singleVisual.vcObjects`/`.objects` shape); exact value-expression wrapping
(`{"expr":{"Literal": {...}}}`) and the GUID `name`/container fields are mechanics →
`powerbi-visuals` — do not hand-invent that wrapper.

```
config.singleVisual.vcObjects:                    # container-level (common cards)
  title:      [{ show:true, text:'<label>', titleWrap:true, fontSize:12, bold:true,
                  fontColor: ThemeDataColor{ColorId:2, Percent:0} }]   # brand navy
  subTitle:   [{ text:'<qualifier>' }]                                 # e.g. "(остання)"
  border:     [{ show:true, width:1, radius:8, color: ThemeDataColor{ColorId:0} }]
  background: [{ show:true, transparency:0 }]                          # fill via objects.fillCustom
  padding:    [{ top:5, left:13 }]
  visualHeader: [{ show:false }]

config.singleVisual.objects:                      # visual-type-specific cards
  outline:    [{ show:false }]
  fillCustom: [{ show:true, fillColor: ThemeDataColor{ColorId:0} }]     # white card
  label:      [{ show:false }]                                          # category label hidden
  value:      [{ fontSize:12, bold:false,
                  fontColor: ThemeDataColor{ColorId:1, Percent:0.2},    # #333333
                  transparency:5, showBlankAs:'0' }]
  layout:     [{ alignment:'bottom', orientation:1, maxTiles:1, cellPadding:0 }]
  shapeCustomRectangle: [{ tileShape:'rectangleRoundedByPixel', rectangleRoundedCurve:8 }]
```

**One label source (never both).** A `cardVisual` can print the measure name in *two* places
at once: the container title (`vcObjects.title.text`, strip at top-left) and the built-in card
`label` (`objects.label`, sits above the value). Showing both renders the name twice — the exact
"навіщо дублювання назв" defect (45 cards in the SKILLZ incident). Pick one and silence the other:
- Container title as the label (the etalon above): `vcObjects.title.show:true` **and**
  `objects.label` → `[{ show:false }]`.
- Built-in `label` as the label: `objects.label.show:true` **and**
  `vcObjects.title` → `[{ show:false }]`.
The etalon already encodes option 1 (`title` shown, `label` hidden) — keep that pairing when
cloning it; if you instead turn the built-in `label` on, you MUST also set the container title off.

Token mapping (report.json `objects` scope): `ColorId 2` = `dataColors[0]` = `color/brand`;
`ColorId 0` = background/white; `ColorId 1 @ Percent 0.2` = `color/text-body` `#333333`. This
mapping is the *report.json* one (`0`=background, `1`=foreground, `N≥2`=`dataColors[N−2]`) —
different from the *theme file* mapping where `ColorId` indexes `dataColors` directly
(`pbi-design-system` §1.7). Verify against the target report before emitting.

## 4. Delta / good-bad coloring

- `kpi` visual: native — set once in the `status` card (`goodColor`/`badColor`/`neutralColor`,
  `direction: "Positive"|"Negative"` — schema enum, NOT up/down), ideally in the theme so it
  applies to every KPI visual at once. No per-card CF needed.
- `cardVisual`: no native sentiment card. Either (a) `accentBar` colored via a CF measure
  returning a named theme color (`good`/`bad` — a mark, so the 3.9–4.3:1 contrast of those
  raw theme colors is fine, `pbi-design-system` §1.1), or (b) CF on `value.fontColor` /
  `referenceLabelValue.valueFontColor` bound to a sign-of-delta measure. CF wiring →
  `powerbi-visuals`; measure → `dax-measures`.
- **Text vs mark color, don't conflate them.** `good`/`bad` are calibrated for marks/large
  text only (`pbi-design-system` §1.1). Option (b) colors small TEXT (`value`/`referenceLabelValue`
  default to `type/value` 12pt regular — below the 18pt/14pt-bold "large text" floor), so it
  must use the AA-safe `color/good-text` (`#107C10`) / `color/bad-text` (`#D13438`) instead of
  the raw named `good`/`bad` strings, or fails 4.5:1. Neither has a named theme-color string
  (theme only defines `good`/`bad`/`neutral`) — this is one of the "colors genuinely absent
  from the theme" cases `pbi-design-system` §1.7 allows as literal hex.
- Icon pairing (never color alone, F9): ▲▼ via `icon-set-manager`, or the native
  `kpi.indicator.showIcon: true`.

## 5. `showBlankAs`

Verified on `cardVisual.value` and `cardVisual.referenceLabelValue`. Left unset, the card
renders nothing on a filtered-to-empty slice — reads as broken, not "no data". Always set
explicitly (e.g. `'0'` or a dash literal), matching the model's own blank-handling convention.

## 6. Grid (`pbi-design-system` §3.2; Σ = 1232 on the 1280 canvas, 1300 on a 1440 canvas)

| Layout | Card size | Math |
|---|---|---|
| 6-up row | 192×104 | 6·192+5·16 = 1232 |
| 4-up row | 296×136 | 4·296+3·16 = 1232 |
| Hero (max 1 per page) | 296×176 | span 3, tall |
| 5-col on 1440 (existing report only) | ≈248×106/140/178 | 5·248+4·15 = 1300 (§7 profile) |

## 7. Parity-diff method (closes the task5-audit D4/D5 incident)

The incident: an agent "unified" 7 KPI cards by eye and reported success; an independent audit
diffed each card's `vcObjects`/`objects` against the etalon (`e27a80`) and found missing
`fillCustom`/`padding`/`layout` settings, and a color literally written to the wrong object
dictionary (never rendered). Full record: `docs/audits/task5-audit.md` D4/D5; evidence script:
`docs/audits/evidence-scripts/da08_cards_diff.py`.

**Do this instead, for every card you touch, before reporting done:**

1. Load the etalon card's `config.singleVisual` and every candidate card's.
2. Flatten each `objects`/`vcObjects` bag to
   `"objects.<card>[<selector>].<property>" → value` (`da08_cards_diff.py` has the exact,
   reusable flattening function — copy it, don't re-derive it).
3. Diff candidate vs etalon: any key present in the etalon but `<MISSING>` or different in the
   candidate is an open defect — including keys that carry no visible color (`padding`,
   `layout`, `shapeCustomRectangle`) since those fail silently and are easy to skip by eye.
4. Only report the restyle done when the diff is empty for every card.
