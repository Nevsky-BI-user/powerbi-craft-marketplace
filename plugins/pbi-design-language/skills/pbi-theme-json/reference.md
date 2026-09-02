# pbi-theme-json — Reference

> Companion to [`SKILL.md`](SKILL.md) and the shipped artifact [`assets/master-theme.json`](assets/master-theme.json).
> Every value below is either a verbatim `pbi-design-system` token or a shape demonstrated in
> the theme-schema introspection notes. Where a value is *derived* (no direct token) or the schema is
> *undocumented*, it is flagged explicitly — never presented as verified fact.

## 1. What's in `master-theme.json`

| Block | Content |
|---|---|
| `name` | `"pbi-design-system-063E61"` — rename per report/brand |
| `dataColors` | 8 colors, brand-first (`pbi-design-system` §1.5, verbatim) |
| `good`/`neutral`/`bad` | `#2B9348`/`#FFC107`/`#D64550` (§1.5, verbatim) |
| `maximum`/`center`/`minimum` | `#107C10`/`#F3F2F1`/`#D13438` (§1.5 divergent stops, verbatim) |
| `null` | `#9E9F9F` (`color/null`, §1.3 — same value as `color/text-disabled`) |
| `firstLevelElements`…`tableAccent` | The 6 structural classes + `tableAccent` (§1.6, verbatim). Preferred names only — legacy aliases (`foreground`, `backgroundLight`, …) deliberately omitted (theme-visuals.md §2.2: "do not mix") |
| `accent` | `#3781F0` (`color/accent`) — direct schema/token match |
| `hyperlink` | `#3781F0` (`color/hyperlink`, §1.8 — reuses `color/accent`) |
| `visitedHyperlink` | `#3C648A` (`color/hyperlink-visited`, §1.8 — reuses `color/neutral-data`) |
| `disabledText` | `#9E9F9F` (`color/text-disabled`) — direct match |
| `shapeStroke` | `#E6E6E6` (`color/border`) — **derived**, reuses the border token as the default shape stroke |
| `textClasses` | All 14 schema keys — see §2 |
| `visualStyles` | `"*"` global + `page` + all 48 visual-type keys + `report`/`filter`/`group` pseudo-entries — see §3 |

**Deliberately omitted:** `foregroundSelected`, `foregroundButton`, `foregroundDark`, `foregroundNeutralLight/Dark`, `foregroundNeutralSecondaryAlt(2)`, `foregroundNeutralTertiaryAlt`, `backgroundDark`, `mapPushpin` — none has a corresponding `pbi-design-system` entry; adding hex values for them would be invention. Add manually, sourced from an actual brand need, if a dark-theme variant requires them.

## 2. `textClasses` — all 14 keys, verbatim vs. derived

| Class | fontFace | pt | color | Source |
|---|---|---|---|---|
| `callout` | Segoe UI | 28 | `#333333` | `pbi-design-system` §2.1, verbatim |
| `title` | Segoe UI Semibold | 12 | `#063E61` | verbatim |
| `header` | Segoe UI Semibold | 14 | `#063E61` | verbatim |
| `label` | Segoe UI | 10 | `#333333` | verbatim |
| `largeTitle` | Segoe UI Semibold | 12 | `#063E61` | verbatim — **pinned**, does not inherit the schema's 14 pt default (theme-visuals.md §3 note) |
| `smallLabel` | Segoe UI | 9 | `#605E5C` | verbatim |
| `lightLabel` | Segoe UI | 10 | `#605E5C` | verbatim |
| `boldLabel` | Segoe UI Bold | 10 | `#333333` | derived: `label` + "Segoe UI Bold" delta (§3 table) |
| `semiboldLabel` | Segoe UI Semibold | 10 | `#333333` | derived: `label` + Semibold family |
| `largeLabel` | Segoe UI | 12 | `#333333` | derived: `label` + 12 pt delta (matches `type/value`) |
| `largeLightLabel` | Segoe UI | 12 | `#605E5C` | derived: `label` + 12 pt + secondary color |
| `smallLightLabel` | Segoe UI | 9 | `#605E5C` | derived: `label` + 9 pt + secondary color (= `type/small`) |
| `dataTitle` | Segoe UI Semibold | 12 | `#063E61` | **undocumented in schema docs** (theme-visuals.md §3: "schema-valid but undocumented") — defaulted to mirror `title` |
| `smallDataLabel` | Segoe UI | 9 | `#605E5C` | **undocumented** — defaulted to mirror `smallLightLabel` |

`dataTitle`/`smallDataLabel` have no published inheritance rule or usage list; if a Desktop version turns out to render them differently from their sibling, override explicitly per-report.

## 3. `visualStyles` — per-type card coverage

All 48 keys get the **4 universal cards** (verified on every regular visual type, theme-visuals.md §4): `background`, `border`, `title`, `dropShadow`. Groups below list what's added **on top**.

| Group | Visual-type keys | Extra cards added | Card source |
|---|---|---|---|
| Cartesian (15) | `barChart`, `clusteredBarChart`, `hundredPercentStackedBarChart`, `columnChart`, `clusteredColumnChart`, `hundredPercentStackedColumnChart`, `lineChart`, `areaChart`, `stackedAreaChart`, `hundredPercentStackedAreaChart`, `lineClusteredColumnComboChart`, `lineStackedColumnComboChart`, `ribbonChart`, `waterfallChart`, `scatterChart` | `labels`, `categoryAxis`, `valueAxis`, `legend` | Worked example §6.2 (`barChart`) + "other useful cards" list |
| Part-to-whole w/ legend (3) | `pieChart`, `donutChart`, `treemap` | `legend` | Same `legend` shape as above |
| Part-to-whole w/o legend (2) | `funnel`, `gauge` | — (mandatory only) | No verified extra card names for these two |
| Maps (4) | `map`, `filledMap`, `shapeMap`, `azureMap` | — (mandatory only) | No verified extra card names |
| Tables (2) | `tableEx`, `pivotTable` | `columnHeaders`, `grid`, `values`, `total`; `pivotTable` also gets `rowHeaders`, `subTotals` | Worked example §6.3. `values` ships the full banding quartet `backColorPrimary`/`fontColorPrimary` + `backColorSecondary`/`fontColorSecondary`; `total`/`subTotals` ship `backColor`+`fontColor`+`bold` (all needed for the §7 dark conversion). `rowHeaders`/`subTotals` card **names** are verified; their **properties** mirror `columnHeaders`/`total` by symmetry (Format pane exposes identical options) — confirm in Desktop before relying on them in production |
| Classic cards/KPI (3) | `card`, `multiRowCard`, `kpi` | — (mandatory only) | Legacy visuals; prefer `cardVisual` for new work (`pbi-design-system` §6) |
| New card (1) | `cardVisual` | `value`, `label`, `layout` | Worked example §6.6, verbatim. `value.fontSize` set to `type/value` (12 pt, dense-grid default) — override to `type/callout-hero` (28 pt) per-instance for the one hero KPI on a page |
| Classic slicer (1) | `slicer` | `header`, `items`, `general` | Worked example §6.4, verbatim |
| Modern slicers (3) | `advancedSlicerVisual`, `listSlicer`, `textSlicer` | — (mandatory only) | Card *names* exist (`accentBar`, `actionState`, `icon`, `image`, `label`, `layout`, `outline`, `overFlow`, `selection`, `shapeCustomRectangle`, `value` for `advancedSlicerVisual`) but no property shapes are demonstrated in theme-visuals.md — adding them here would be invention. Confirm exact fields in the Format pane before authoring |
| AI/analytics (6) | `decompositionTreeVisual`, `keyDriversVisual`, `aiNarratives`, `qnaVisual`, `scriptVisual`, `pythonVisual` | — (mandatory only) | No verified extra cards; these are routed to `pbi-ai-visuals`/`dax-measures` for content, not theme, decisions |
| Buttons/shapes (2) | `actionButton`, `shape` | `fill`, `text`, `outline` with `$id` states (`default`/`hover`/`selected`/`disabled`); `border` forced off | Worked example §6.5, verbatim shape. Colors mapped to `pbi-design-system` §5 interactive-states table (**neutral default**, not the brand-filled "primary button" look of the raw schema example) so every button/tab instance — including nav tabs — starts from the quiet default state |
| Nav visuals (2) | `bookmarkNavigator`, `pageNavigator` | — (mandatory only) | Built-in selected-state styling per `pbi-design-system` §5; no extra card properties verified |
| Elements (4) | `textbox`, `image`, `rdlVisual`, `scorecard` | — (mandatory only) | No verified extra cards |

**Pseudo-entries** (theme-visuals.md §5 explicitly labels these "not visuals, styled the same way"):

- `page` — **included**, `background` + `outspace` (worked example §6.7, verbatim); `outspace` = `color/page-bg` (kills the legacy page-background drift, `pbi-design-system` §1.4/§8).
- `report`, `filter`, `group` — **included** in `master-theme.json` with minimal, non-token defaults (no `pbi-design-system` entry drives them, since none has a corresponding token): `report.outspacePane` (`expanded: false`, `visible: true`) + `report.section` (`verticalAlignment: Top`); `filter.general` (`isInvertedSelectionMode: false`, `requireSingleSelect: false`); `group.background` (hidden, `#FFFFFF`) + `group.lockAspect` (off). Card *names* match theme-visuals.md (`outspacePane`/`section`; `general`; `background`/`general`/`lockAspect`). Override any of these per-report if a canvas-level filter-pane or group-container need arises — these defaults are conservative placeholders, not tokenized values.

### 3.1 Precedence: per-visual beats type beats `*`

`visualStyles.<type>.*` overrides `visualStyles.*.*` (the type block wins whenever both set
the same card/property), and an explicit per-visual `visualContainerObjects` setting in the
visual's own JSON overrides both. The practical consequence, easy to get wrong: **switching a
card off at type level in the theme only affects visuals that INHERIT it** — a visual carrying
its own `visualContainerObjects` entry for that card is unaffected either way.

**Grounding incident.** Turning the container border off for `cardVisual` at theme level
looked safe — until an audit found that 45 of 50 cards on the target report INHERITED that
border, and it was their ONLY edge (their own tile outline had already been switched off
per-visual, per §4.1 of `pbi-design-system`). The theme-level change would have left 45 cards
edgeless. **Before making a type-level change, count how many visuals actually inherit versus
override** — grep every visual's `visualContainerObjects` for the card in question and diff
against the total instance count for that type.

### 3.2 A visual GROUP: inherits `*/*`, ignores its own type key — override inside `visualGroup`

Render-bisected on a live overlay panel (group + rounded backdrop shape), three Desktop
cycles, one variable at a time:

1. The panel showed a "second frame": a white band with square corners poking out past the
   rounded backdrop. Backdrop `dropShadow` OFF → band **unchanged**. Not the shadow.
2. The theme carried `visualStyles.group["*"].background.show = false` the whole time —
   and the band was still painted. **The runtime ignores the `group` type entry** (the key
   exists in `reportThemeSchema`, so schema presence proves nothing about runtime honor).
   The group was inheriting the `*/*` container background (white, square-cornered) and
   painting it edge-to-edge behind the rounded backdrop.
3. `visualGroup.objects.background = [{"properties": {"show": false}}]` in the group's own
   visual.json → band **gone**, single frame.

So the working rules are:

- A group **inherits `*/*` container defaults but does not consult `visualStyles.group`.**
  Theme-side, the only way to spare groups is to not paint chrome in `*/*` at all.
- The per-group override lives INSIDE `visualGroup.objects` — the PBIR schema
  (`VisualGroupConfig`) allows exactly `background`, `lockAspect`, `general` there, and the
  container's `additionalProperties: false` forbids a `visualContainerObjects` node beside
  `visualGroup`. `border`/`dropShadow` have no group-level knob at all — but with the
  background off there is nothing for them to outline, which is why killing the background
  suffices for the "second frame" symptom.

Diagnostic signature worth memorising: **a straight-edged halo offset outward from a
rounded overlay = a container background showing past the shape's corner radius.** JSON
will show only one border; the "second frame" is a background, not a border.

General lesson, twice paid for: the schema tells you what is *expressible*, only a render
tells you what is *honored*. Read the schema for structure; bisect a render for behavior.

## 4. Wiring into a PBIP report

### PBIR-Legacy (single `report.json`)

`report.json.config` is a **JSON string**, not a nested object — parse it first.

```jsonc
// after JSON.parse(config):
"themeCollection": {
  "baseTheme":   { "name": "CY24SU10", "type": 2, "version": { "major": 1, "minor": 0 } },
  "customTheme": { "name": "Custom<digits>.json", "type": 1, "version": { "major": 1, "minor": 0 } }
}
```

`type: 1` = RegisteredResources → place the file at
`<Report>.Report/StaticResources/RegisteredResources/<customTheme.name>`. Re-stringify `config`
back into `report.json` byte-faithfully (mechanics/pitfalls of editing the `config` string →
`powerbi-visuals`).

### PBIR enhanced

Same `themeCollection` concept lives in `definition/report.json`; the theme file sits under
`definition/StaticResources/RegisteredResources/`. The exact `resourcePackages`/registration
array shape is enhanced-schema-specific — confirm the precise field names against the
PBIR schema (`https://github.com/microsoft/json-schemas/tree/main/fabric/item/report/definition`)
or the external `pbir-format` / `pbip` skills (Microsoft skills-for-fabric, data-goblin) before
hand-editing.

## 5. Rebranding: token replace-map

Every hex in `master-theme.json` is one of these tokens — replace by exact string match, not by
guessing which card uses which color:

| Hex in file | Token | Hex in file | Token |
|---|---|---|---|
| `#063E61` | `color/brand` | `#605E5C` | `color/text-secondary` |
| `#3781F0` | `color/accent` | `#9E9F9F` | `color/text-disabled` |
| `#FFC107` | `color/warning` | `#FFFFFF` | `color/surface` / `color/text-inverse` |
| `#2B9348` | `color/good` | `#FAFAFA` | `color/surface-alt` |
| `#D64550` | `color/bad` | `#F5F4F2` | `color/page-bg` |
| `#3C648A` | `color/neutral-data` | `#E6E6E6` | `color/border` |
| `#D13438` | `ramp/diverging` min | `#E6ECEF` | `color/hover-tint` |
| `#107C10` | `ramp/diverging` max | `#F3F2F1` | `ramp/diverging` center |
| `#333333` | `color/text-body` | | |

Do not rename or restructure any `visualStyles` key, card name, or `$id` value while rebranding —
only the leaf hex/pt values change.

## 6. Testing (headless)

1. `python -c "import json; json.load(open('master-theme.json', encoding='utf-8'))"` — must not raise.
2. Every `visualStyles` key (except `"*"` and `page`) must appear verbatim in `theme-visuals.md`
   §5's 48-key list (case-sensitive) — a scripted `set()` diff catches typos like `pieChar` or
   `matrix` that Power BI would silently ignore on import.
3. Every card value must be a JSON array (`isinstance(v, list)`), never a bare object.
4. If wired into a report: the report's `config`/`definition/report.json` must still parse after
   re-stringifying, and the referenced `RegisteredResources` file must exist on disk.
5. **Cannot be verified headless:** actual rendering (font fallback if Segoe UI is unavailable,
   which style preset shows as "selected" in the Format pane, dark-mode legibility). State this
   limitation explicitly rather than asserting the theme "looks right" — Tabular Editor's BPA
   does not apply to theme JSON (that's semantic-model tooling); there is no equivalent headless
   theme linter beyond the JSON/key checks above.

**Enum/int value map** (a Format-pane display name in these slots makes PBI reject the whole theme
on load — use the schema value, confirm against `reportThemeSchema-2.155.json`):

| Property | Wrong (label) | Right |
|---|---|---|
| `position` | `"Above"` | `"aboveValue"` / `"belowValue"` |
| `orientation` | `"Horizontal"` | int — `2`=Horizontal, `1`=Vertical, `0`=Grid |
| `outlineStyle` | `"BottomOnly"` | int — `0`=None, `1`=BottomOnly … `7`=Frame |

## 7. Converting a light theme to dark (RED-verified checklist)

Flipping an imported light theme (e.g. a vendor/SQLBI export) to a dark background by recoloring
only `dataColors` + page `background` **leaves light values stranded** — they hide as
same-colour-on-same-colour (light stripe under a light font). Verified failure on a real dark
report (Desktop 2.155): every other table/matrix row rendered as a white band with white text,
headers blurred. Recolor **all** of §7.1–§7.4 in one pass.

### 7.1 Banding pairs — the exact I-1 trap

The `tableEx`/`pivotTable` `values` card has **two** independent row states, each with its own
background **and** its own font. They are **two matched pairs — never a "trio"**:

| Row state | Background key | Font key (its only partner) |
|---|---|---|
| Odd / primary rows | `backColorPrimary` | `fontColorPrimary` |
| Even / banded (alternating) rows | `backColorSecondary` | **`fontColorSecondary`** |

**The bug the incident reproduced:** binding `backColorSecondary` to `fontColorPrimary` (or leaving
`fontColorSecondary` unset). The banded background is *always* read with the **secondary** font, so
a light `backColorSecondary` (`#FAFAFA`/`#F9F9F9`) under any light font (e.g. `#e2e8f0`) = invisible
text on every second row. Rules:

- Recolor `backColorPrimary`↔`fontColorPrimary` **and** `backColorSecondary`↔`fontColorSecondary`,
  each pair moving to dark together.
- **Never** pair the secondary background with the primary font.
- If a source theme omits `fontColorSecondary` (older SQLBI-style exports do — the card then shows
  only `fontColorPrimary`/`backColorPrimary`/`backColorSecondary`, which is what tricks you into a
  "trio"), **add `fontColorSecondary` explicitly**; otherwise banded rows fall back to an unmanaged
  colour. `master-theme.json` now ships all four keys so the pairing is self-evident.

### 7.2 Headers, total, subTotals — each has its own `backColor` **and** `fontColor`

`columnHeaders`, `rowHeaders`, `total`, and (on `pivotTable`/matrix) `subTotals` are all real cards
that each expose **both** `backColor` and `fontColor` (`total`/`subTotals` additionally `bold`). It
is **wrong** to say `total` has "only `fontColor`, no `backColor`" — it has its own `backColor`, and
a stranded light `total.backColor` (`#EBEBEB`) or `subTotals` fill is exactly the I-1 residue. On
dark conversion set `backColor` **and** its matching `fontColor` **together** on all four. Light
header `backColor` `#F5F5F5` + light `fontColor` `#94a3b8` = blurred, unreadable headers.
`master-theme.json` now sets `backColor`+`fontColor` on `columnHeaders`, `rowHeaders`, `total`, and
`pivotTable.subTotals` so every band/total/subtotal field is present to recolor.

### 7.3 Grid

The `grid` card gridline/outline colour (`gridHorizontalColor`/`gridVerticalColor`,
`#E8E8E8`/`#E0E0E0` in light themes) → a dark hairline; light gridlines glow on a dark canvas.

### 7.4 Luminance gate — a mechanical sweep over EVERY hex, not a spot-check

Do **not** eyeball, and do **not** check only a few named pairs. The rule is a general test applied
to the whole theme:

1. Extract **every** hex in the theme — all of `dataColors`, the structural classes, `textClasses`,
   and every `visualStyles` card value.
2. Pair **each** background with **every** foreground drawn over it: page bg vs body text,
   `backColorPrimary` vs `fontColorPrimary`, `backColorSecondary` vs `fontColorSecondary`, each
   header/`total`/`subTotals` `backColor` vs its `fontColor`, grid vs canvas.
3. Compute relative luminance for both members of each pair. **Fail condition (both directions):
   a light background with a light foreground, OR a dark background with a dark foreground** — either
   strands the text. Pass/fail is mechanical per pair, over the full hex set — not a judgement call.

Medium-grey fills read as near-black on dark — reserve them for muted separators, never for text.

### Embedded base64 backgrounds (report-crash class)

If a page uses `visualStyles.page.*.background[0].image.url` with an inline
`data:image/…;base64,…` payload, a stray `U+FEFF` BOM — picked up when the base64 was pasted from
a text file — **anywhere** in the string makes the **whole report fail to open**
("Couldn't load the report", no detail). This is the invalid-value-of-a-known-property crash
class: Desktop silently ignores unknown property *names*, but a malformed *value* of a known
property brings down the whole report. Before shipping: `base64.b64decode(payload, validate=True)`
must succeed, and scan the entire payload for `U+FEFF`, not just its first byte.

## 8. Dark → light: two theme keys a hex sweep can never reach (RED-verified)

A complete find-replace of every hex (verified across 195 files of a real 30-page report) can
finish and still leave **every page dark**. Two `page` keys hold no hex to replace:

### 8.1 The wallpaper is a base64 data-URI *inside* theme.json

`visualStyles.page["*"].background.image`:

```json
{ "name": "ModernGradient", "scaling": "Fit", "url": "data:image/png;base64,iVBORw0…" }
```

One such key bloats theme.json to **~1.8 MB**, and recoloring hex does not touch it in principle —
the colours are pixels inside the PNG. The image must be **regenerated or removed**, not
recolored. Note where to look: the wallpaper lives in the **theme**, not in `page.json`.

### 8.2 `transparency: 100` means the colour is OFF, not "tinted"

`page["*"].outspace`:

```json
[{ "color": { "solid": { "color": "#e2e8f0" } }, "transparency": 100 }]
```

The theme *names* a light colour but never paints it, so Desktop's own (dark) canvas background
shows through around the page. The symptom users report is "the page sits in a black frame".
Fixing the hex changes nothing — the transparency has to come down (0 = fully painted). Read
`transparency: 100` anywhere in a theme as "this colour is disabled", never as "transparent over
the light surface underneath".
