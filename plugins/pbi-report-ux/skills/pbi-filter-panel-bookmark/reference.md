# Filter Panel as a Bookmark-Toggled Overlay — Reference

Ground truth for every JSON block below: the Desktop-emitted PBIR **enhanced** report
`the source report` (schema `visualContainer/2.10.0`, `bookmark/2.1.0`), page `37d8618c987d51132762`,
group `2159afacf1398140e3aa` (`displayName: "Filter Pannel"`). Nothing here is written from memory.
Where a value was not observed in that report it is called out as unknown — do not invent it.

> **Read this before copying anything below.** Ground truth proves only what it contains. Where a
> construct has variants and this report shows one of them, the other variants come from the
> **schema**, never by analogy from the observed one — see §5.2 for the incident that law was paid
> for, and §8.1 for the mechanical check that enforces it.

---

## §1. File map

```
definition/
├─ report.json                                  ← resourcePackages: RegisteredResources (icons)
├─ bookmarks/
│  ├─ bookmarks.json                            ← registry + grouping metadata; unregistered = invisible
│  ├─ <openId>.bookmark.json                    ← group isHidden:false  (see §6 for the flag choice)
│  └─ <closeId>.bookmark.json                   ← group isHidden:true,  suppressData:true
└─ pages/<pageId>/visuals/
   ├─ <groupId>/visual.json                     ← visualGroup, "isHidden": true
   ├─ <backdropId>/visual.json                  ← shape,  parentGroupName: <groupId>
   ├─ <slicerN>/visual.json                     ← slicer / advancedSlicerVisual, parentGroupName
   ├─ <closeBtn>/visual.json                    ← actionButton, parentGroupName, → closeId
   └─ <openerBtn>/visual.json                   ← actionButton, NO parentGroupName, → openId
```

Ground-truth panel size: group `1219.10 × 500.15` at `x 214.35, y 0`, `z 15000`, `tabOrder 10000`;
23 children — 1 `shape` backdrop, 13 `slicer`, 5 `advancedSlicerVisual`, 4 `actionButton`.

---

## §2. The group container

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.10.0/schema.json",
  "name": "2159afacf1398140e3aa",
  "position": { "x": 214.35, "y": 0, "z": 15000, "height": 500.15, "width": 1219.10, "tabOrder": 10000 },
  "visualGroup": { "displayName": "Filter Pannel", "groupMode": "ScaleMode" },
  "isHidden": true
}
```

- `isHidden` sits at the **top level of the group file**, sibling of `visualGroup` — this is the
  default (report-open) state. Panel closed by default ⇒ `true`.
- `groupMode: "ScaleMode"` is what Desktop writes for both groups on the ground-truth page. Other
  modes were not observed — do not guess names.
- **Child positions are relative to the group box.** Verified on two independent groups:
  the panel's children span `x 0 … 1219.10` inside a group placed at canvas `x 214.35`; the
  "Navigation group" at canvas `x 104, width 590.77` has children at `x 0 / 220 / 394`.
  Moving the group moves the contents; you never rewrite child coordinates.

Members carry `"parentGroupName": "2159afacf1398140e3aa"` as a **top-level key of the child file**
(sibling of `name`/`position`/`visual`), not inside `visual`.

### Backdrop shape (member, lowest `z`)

```json
"visual": {
  "visualType": "shape",
  "objects": {
    "shape":   [ { "properties": { "tileShape": {"expr":{"Literal":{"Value":"'rectangleRounded'"}}},
                                   "rectangleRoundedCurve": {"expr":{"Literal":{"Value":"3L"}}} } } ],
    "fill":    [ { "properties": { "fillColor": {"solid":{"color":{"expr":{"ThemeDataColor":{"ColorId":0,"Percent":0}}}}} },
                   "selector": {"id":"default"} } ],
    "outline": [ { "properties": { "show": {"expr":{"Literal":{"Value":"true"}}},
                                   "lineColor": {"solid":{"color":{"expr":{"ThemeDataColor":{"ColorId":0,"Percent":-0.1}}}}} },
                   "selector": {"id":"default"} } ]
  }
}
```

GT geometry: `x 0, y 17.86, w 1206.41, h 482.29, z 0` — i.e. the backdrop is the bottom layer and
covers the whole panel. Without it, an overlay is transparent and the page reads through it.
Shape serialization law (incident І-14) applies unchanged; see §4.

---

## §3. Panel layout — the system

The antipattern being replaced is one narrow column of slicers, each with its own scrollbar.
What replaces it is not a hand-tuned rectangle: **the panel is a pure function of its filters.**
Every number below is produced by `docs/audits/evidence-scripts/filter_panel_layout.py`
(`layout()` returns the boxes, `check()` returns the invariant violations).

Synthesised from four independent designs and their reviews (workflow `wf_6a300216-8f7`).
The four defects the reviewers found in the winning design are fixed here and marked D1-D4.
A second round of corrections, marked **C1-C4**, came from an actual render of the generated
panel rather than review: each is a measured boundary (a clipped caption, a collapsed slicer, an
overflowing column, unequal peer buttons), not a preference — see §3.3.1, §3.4, §3.7 and §3.9.

### §3.1 Why size follows content

Every pixel of panel is a pixel of report the user cannot see while choosing — and the panel is
open precisely when they are watching a number change. So panel area is a **cost**, not a canvas
to fill. Two consequences that decide the whole layout:

- Anchor the RIGHT edge to the page content edge and grow **leftward and downward only**. The
  opener lives at the end of the header scan; the panel must appear to fall out of it.
- `W_panel` and `H_panel` are functions of the filter count alone. A panel wider than its filters
  need is occlusion the user pays for and gets nothing back.

### §3.2 Constants

| Symbol | Value | What it is |
|---|---|---|
| `P` | 24 | panel padding |
| `W_COL` | 280 | column width (360 if any label exceeds `floor(W_COL/8)` chars at 10 pt) |
| `G_COL` | 24 | gap between columns |
| `H_CELL` | 64 | 24 label + 32 control + 8 slack |
| `G_ROW` | 16 | gap between cells; pitch `V = H_CELL + G_ROW = 80` |
| `H_HEAD` | 48 | header band = close-button height |
| `G_HEAD` | 16 | gap below the header band, above the first caption/cell |
| `H_CAP` | 40 | column caption (**D1**: was 24, below the 10 pt floor — it clipped) |
| `G_CAP` | 8 | gap below a column caption, above the first cell |
| `H_ACT` | 48 | action button height |
| `G_ACT` | 24 | gap above the action row |
| `G_LINE` | 24 | gap between the two action lines when `lines = 2` |
| `DEAD` | 120 | dead zone isolating destructive actions from the primary |
| `W_MIN_BTN` | 88 | a captioned button narrower than this renders its caption as nothing |
| `W_PRIM_MIN` | 176 | minimum width of the primary button, the widest on the row |
| `G_PEER` | 24 | gap inside the destructive pair (**C4**: the two peer buttons) |
| `A_CHAR` | 6 | caption-width slope — avg glyph advance, mixed-case Latin, 10 pt (**C1**) |
| `B_CHROME` | 48 | caption-width intercept — button padding + ellipsis reserve (**C1**) |
| `PAGE_W`, `PAGE_H` | 1920, 1080 | page size the panel must fit inside (**C3**: `PAGE_H` drives the column budget) |
| `CONTENT_ORIGIN` | 20 | left/top origin of the report content grid |
| `CONTENT_R` | 1900 | right edge of the content grid (`PAGE_W - CONTENT_ORIGIN`); the panel right-anchors here |
| `M_BOTTOM` | 20 | the panel may not touch the page's bottom edge |
| `U` | 8 | grid unit — every coordinate snaps to it |
| `N_MAX` | 12 | cognitive cap on filter count — fixed, independent of geometry |
| `C_MAX` | 3 | columns beyond which the panel is a page, not an overlay |

### §3.3 The minimum-height table is the single source of truth

`T_RAW(pt)` = 10→40, 12→44, 14→48, 18→52, 24→64 — measured on this project (incident І-12 plus
the `actionButton` chrome finding). The layout uses `T = ceil8(T_RAW)`.

**Why the rounding is a rule and not a fudge:** the calibration floor and the 8-grid are two
independent constraints, and 44 and 52 satisfy only the first. Rounding *up* can only add slack,
so snapping the floor to the grid can never clip a caption — it makes both constraints true at
once. The checker enforces both; without the rounding, `I5` fails on every 12 pt title.

Derived: a textbox needs `T(pt)`; a button needs `T(pt) + 8` (its own chrome); a captioned button
needs `max(W_MIN_BTN, ceil8(A_CHAR*len(caption) + B_CHROME))` of width — the engineering floor and
the text fit are **two separate tests and both must pass**.

### §3.3.1 Caption width — the chrome constant was wrong, not the slope (C1)

The formula above used to be `max(88, ceil8(7*len + 32))`. It predicted the caption `"Default"`
(7 chars, 10 pt) fits an 88 px button. A render of the generated panel showed it clipped to
`"Defa..."` — the floor had hidden a wrong formula for as long as no caption crossed it.

`w = a*len + b` was re-solved against five observed fit/clip boundaries from that render:

| Caption | len | width | result |
|---|---|---|---|
| `Close` | 5 | 88 | fits |
| `Default` | 7 | 88 | **clips** |
| `Clear all slicers` | 17 | 152 | fits |
| `Restore default` | 15 | 160 | fits |
| `Apply and close` | 15 | 280 | fits |

Only `a=6, b=48` satisfies all five simultaneously; the region `a=3..5` is also arithmetically
consistent with the fit points but is physically impossible — a 10 pt glyph cannot advance 3-5 px —
so `A_CHAR=6, B_CHROME=48` is the unique answer, not a fit among several.

**The lesson, stated so it transfers:** the error was in `B_CHROME` (the chrome/padding constant),
not in the slope, and the 88 px floor had been masking it — a floor that hides a wrong formula is
worse than no floor, because it stops failing only by accident, on whichever caption happens to be
short enough. Trust `btn_w()` over the 88 px number; the floor is a backstop, not a validator.

**Caveat:** `A_CHAR=6` is an average for mixed-case Latin at 10 pt. ALL-CAPS or wide-glyph captions
run closer to `1.3×` that advance — the formula does not model case or script, so keep captions
short rather than trusting it near the boundary.

### §3.4 Geometry

```
# C5: SLOTS LIE - cells are PIXELS per what the control DRAWS, calibrated by
# render bisection (64 -> the whole control collapses to a funnel icon; 96 ->
# the between's slider track is SILENTLY dropped; 120 -> everything renders;
# 144 -> visible dead space). H_KIND is a floor, never a suggestion.
H_KIND(kind)  = 120 for between / range / relativeDate
              = 144 for list / hierarchy / chiclet
              =  64 otherwise (H_CELL: 24 label + 32 control + 8 slack)
F             = number of filter visuals = number of DECISIONS (C6 guards use F)
y_panel       = y_opener + h_opener + U

# C3: columns are DERIVED from the page, never a decreed /4. Stay at one column
# until it would overflow the page; only then split. Worst-case chrome (two
# action lines) is priced in up front so the answer never needs revising after
# the action row is actually measured.
col_budget(cap) = PAGE_H - y_panel - M_BOTTOM - chrome(cap)
  where chrome(cap) = gy0(cap) + G_ACT + 2*H_ACT + G_LINE + P
        gy0(cap)    = P + H_HEAD + G_HEAD + cap*(H_CAP + G_CAP)

pack: walk filters in priority order, y-cursor per column; a cell that does not
      fit the column's remaining budget starts the next column (D2: the leftover
      space stays EMPTY - never reorder to fill it). Overflowing C_MAX columns
      rejects the pattern.
C             = columns pack used
cap           = 1 if C == C_MAX else 0         # per-column captions steal a row; re-pack once
W_panel       = 2P + C*W_COL + (C-1)*G_COL     = 24 + 304*C  -> 328 / 632 / 936
stack_h       = max over columns of (last y + last h)
y_act         = gy0 + stack_h + G_ACT

# C4: the destructive pair are PEERS - always identical width. Size from what
# the CAPTIONS need first, then test whether that fits beside the primary;
# testing the full-row split first forces a second action line that was never
# needed.
w_peer        = max(btn_w(caption_clear), btn_w(caption_default))
w_prim        = max(btn_w(caption_primary), W_PRIM_MIN)
lines         = 1 if 2*w_peer + G_PEER + DEAD + w_prim <= W_panel - 2P else 2
w_peer        = floor8((W_panel - 2P - G_PEER) / 2)   # only when lines == 2: the pair owns the row

H_panel       = y_act + lines*H_ACT + (lines-1)*G_LINE + P
x_panel       = CONTENT_R - W_panel            # right-anchored to the content edge (1900 on a 1920 page)
```

`lines` is 1 when `2*w_peer + G_PEER + DEAD + w_prim <= W_panel - 2P`, else 2 (the primary drops to
its own full-width line below the destructive pair, and `w_peer` is re-split to fill that row).

### §3.5 Order is one order

Fill **column-major**, top to bottom then left to right. The funnel of thought is vertical
(broad → narrow); row-major scatters a narrowing sequence across columns and forces horizontal
jumps between dependent choices.

Rank filters by tier, not by taste: `1` time → `2` scope/org/geo → `3` subject hierarchy
coarse-to-fine → `4` status flags → `5` display toggles (field parameters, measure switchers —
always last: they change what is shown, not what is included). Within a tier: most-changed first,
then lowest cardinality.

That single order must be the **visual order, the priority order and the `tabOrder`** at once.
When they diverge, a keyboard user is navigating a layout they cannot see.

**D2 — the hole rule.** A tall cell that does not fit a column's remaining budget starts
the next column, and the leftover space **stays empty**. Never pull a lower-priority filter forward
to fill it: that buys a tidy grid by breaking the order invariant above. A hole is cheaper.

### §3.6 Actions

The action set is fixed and independent of `C` — the available actions must not change because
someone added a filter:

- **primary** (`Apply and close`) bottom-**right**, the widest button (>=176), where the reading
  path ends;
- **destructive pair** (`Clear all slicers`, `Default`) bottom-**left**, ghost-styled, separated
  from the primary by >=`DEAD`. Power BI has no undo — these must never inherit the primary's
  click volume. **They are peers: always identical width** (**C4**) — two ghost buttons of
  different widths read as different weights of action, and a user should not have to guess which
  one is "more" destructive. Size `w_peer` from what the *captions* need first, then test whether
  the pair fits beside the primary on one line; testing the full-row split first forces a second
  action line that was never necessary;
- **Close** top-right: the cheap escape nearest where the cursor lands. Keep *both* exits; each
  serves a different user;
- outside the panel, at most **one** action, and only the constructive one (`Restore default`).
  `Clear all` in the header is a trap that leaves the user with nothing.

`tabOrder` bands: opener 200, outside reset 300, group 1000, close 1100, filters `1200 + 10*i`,
clear/default/primary 2000/2010/2020, page content 3000+. Decorative members get `-1`.

### §3.6.1 Elevation — the style shadow and its margins (C7, user-calibrated GT)

A `shape` visual has **two independent shadows**, and they behave differently:

| Shadow | Object | Where it draws | Geometry it follows |
|---|---|---|---|
| Style shadow | `visual.objects.shadow` | **INSIDE** the container box | the rounded shape |
| Container shadow | `visualContainerObjects.dropShadow` | around the container box | the rectangular box |

For a rounded overlay use the **style shadow** and switch the container shadow **off**.
Serialization follows the standard split: a bare `show` entry plus a `{"id":"default"}` entry
carrying the values (`shadowBlur: 20D` here).

**The style shadow eats canvas.** Because it draws inside the container, the visible rounded
rect shrinks. Compensate in the container, not in the layout: keep computing the VISIBLE panel
rect exactly as in §3.4, then wrap it in the shadow margins

```
container = visible rect + (L 6, R 6, T 0, B 4)      # calibrated at blur 20
members   = visible coordinates + (L, T)              # container-relative on disk
backdrop  = (0, 0, container.w, container.h)          # fills the container, carries the shadow
```

Calibration source: the user manually aligned the rendered panel in Desktop and the engine
reproduces every one of the 11 resulting boxes byte-exactly (roundtrip check in
`filter_panel_layout.py`, invariant **I15**). Numbers, not derivation — the renderer's inset
is not documented anywhere.

**The 8-grid governs the VISIBLE rect, not the container.** After the margins the container
sits off-grid (340 wide at x 1566) while the visible rect stays on it (328 at 1572, right edge
flush with the content edge 1900). The grid is an optical law: it aligns what the eye sees;
a container inflated by optical padding is exempt. I5/I10 therefore check visible coordinates;
I15 checks the container wrap.

### §3.7 Boundaries

- `F <= 3` → **do not build the panel.** It costs a click and buys nothing; put the slicers inline.
- `F > 12` → **do not build a fourth column or a scrollbar.** `F_MAX` is a **fixed cognitive cap
  counting DECISIONS, not pixels** (**C6**: six list slicers are six decisions, however tall),
  independent of the geometry below** — it does not move when the column budget does, and it is checked
  before column count is ever computed. Keep the most-changed filters here and send the rest to
  the native filter pane.
- **C3 — columns are derived, not decreed:** stay at one column until it would overflow the page,
  then split. A right-anchored panel over a wide report is cheaper **tall** than **wide** — growing
  down costs the vertical overlap of one visual, growing left costs the width of the whole report
  body (§3.9 has the measured comparison). If the filters still cannot fit `C_MAX` columns, reject: the
  panel has become a page, not an overlay — use the native filter pane.
- **The footprint rule is about at least one visual, not every visual.** At least one result
  visual — the one the user is actually watching while filtering — must clear the panel footprint
  entirely: `v.x + v.w <= x_panel` or `v.y >= y_panel + H_panel`. Secondary detail visuals may sit
  under the panel and be temporarily occluded. Requiring this of *every* visual would reserve a
  permanent gutter the width of the panel for an overlay that is closed most of the time — a bigger,
  standing cost than the transient occlusion it exists to avoid, and it contradicts §3.1's own
  "panel area is a cost" principle.
- Multi-page reports: fix `C` from the page with the largest `N`, so the left edge does not jump.

### §3.8 Invariants (run them, do not eyeball them)

| # | Invariant |
|---|---|
| I1 | textbox `h >= T(pt)` |
| I2 | button `h >= T(pt) + 8` |
| I3 | button `w >= max(W_MIN_BTN, ceil8(A_CHAR*len(caption) + B_CHROME))` (**C1**: corrected constant) |
| I4 | every member inside the backdrop box |
| I5 | every `x/y/w/h` on the 8-grid |
| I6 | no two members overlap |
| I7 | primary separated from the destructive pair by >=`DEAD` (when `lines = 1`) |
| I8 | `tabOrder` ascends with column-major position |
| I9 | panel top below the opener bottom |
| I10 | panel origin on the content grid (`(coord - 20) mod 8 == 0`) |
| I11 | every member declares edge ownership (`own`/`none`) — the container border and the visual's own outline are independent, and both "on" is the double-border defect |
| I12 | slicer `h >= H_KIND(control)` (**C2/C5**: undersized does not clip - it sheds parts silently: 96 drops the between's track, 64 leaves a funnel icon) |
| I13 | destructive pair: `clear.w == default.w` and `clear.y == default.y` (**C4**: peers are always equal) |
| I14 | `y_panel + H_panel <= PAGE_H - M_BOTTOM` — the panel must fit the page it floats over (**C3**) |

**D3** — bookmark scope counts visuals:
`len(targetVisualNames) = 1 group + 1 backdrop + 1 title + C*cap captions + F filters + 4 buttons`.

### §3.9 Worked examples

Every value below is the actual stdout of `evidence-scripts/filter_panel_layout.py`
(`cd docs/audits/evidence-scripts && python filter_panel_layout.py`) — none of it is hand-computed;
where this document and the script would ever disagree, the script wins (§3, opening paragraph).
Captions `Clear all` / `Default` / `Apply and close` / `Close`; opener 120x48 at `y 84`.

| Case | F | C | stack | lines | panel | at (x,y) | targets | note |
|---|---|---|---|---|---|---|---|---|
| F=2 all dropdown | 2 | — | — | — | — | — | — | REJECTED: `F<=3`, inline the slicers (**D4/C6**: the guard counts decisions) |
| F=4 all dropdown | 4 | 1 | 304 | 2 | 328x560 | 1572,140 | 11 | one column; primary drops to its own line |
| F=7 all dropdown | 7 | 1 | 544 | 2 | 328x800 | 1572,140 | 14 | |
| F=8 all dropdown | 8 | 1 | 624 | 2 | 328x880 | 1572,140 | 15 | last all-dropdown count that fits one column |
| F=12 all dropdown | 12 | 2 | 624 | 1 | 632x808 | 1268,140 | 19 | captions **off** — `C=2 != C_MAX` |
| F=13 all dropdown | 13 | — | — | — | — | — | — | REJECTED: `F>12`, native filter pane |
| demo: date-between + 3 | 4 | 1 | 360 | 2 | 328x616 | 1572,140 | 11 | **C3/C5 evidence** — see below |
| mixed: between+list+2 drop | 4 | 1 | 440 | 2 | 328x696 | 1572,140 | 11 | between 120 + list 144 + 2x64, one column |
| 6 lists | 6 | 2 | 624 | 1 | 632x808 | 1268,140 | 13 | six decisions (allowed); 6x144 splits into two columns |

**Item-level check for the demo row** (`between` + 3 `dropdown`, `C=1`): `between` at
`x24,y88,w280,h120`; dropdowns at `y224/y304/y384`, each `280x64`; peer buttons `128x48` at
`y472`; primary full-width at `y544`. `check()` on this plan returns `[]`.

**C3+C5, the concrete evidence.** The demo (4 filters, one date-between) went `328x560` under
the slot decree (`R_MAX=4` would even have forced `632x408` = 257,856 px2 for a while), then
`328x640` with a slot-doubled 144px date cell — ~54px of visible dead space the user flagged
immediately — and lands at `328x616` with the calibrated 120px cell: everything renders, nothing
is dead. Each step is cheaper by the layout's own §3.1 cost metric, and each was driven by a
measured render, not a preference.

Sanity check on the cost argument: at `N = 4` the system's panel is 328x560 = 183,680 px2,
against 268,800 px2 for the hand-tuned 1200x224 band it replaced — the computed panel occludes
**less** report while showing the same four filters.

---

## §4. The button — full canon (`actionButton`)

Verified opener, GT `7889b2e2454560d165ac`: `36.94 × 40.96` at page `x 1186.21, y 4.82`,
`tabOrder 6000`, `howCreated: "InsertVisualButton"`, **no** `parentGroupName`.

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.10.0/schema.json",
  "name": "7889b2e2454560d165ac",
  "position": { "x": 1186.21, "y": 4.82, "z": 0, "height": 40.96, "width": 36.94, "tabOrder": 6000 },
  "visual": {
    "visualType": "actionButton",
    "objects": {
      "icon": [
        { "properties": {
            "shapeType":   {"expr":{"Literal":{"Value":"'custom'"}}},
            "image": { "image": {
                "name": {"expr":{"Literal":{"Value":"'icon-park-twotone_clear (1).png'"}}},
                "url":  {"expr":{"ResourcePackageItem":{
                           "PackageName":"RegisteredResources","PackageType":1,
                           "ItemName":"icon-park-twotone_clear_(1)8211307375087734.png"}}},
                "scaling": {"expr":{"Literal":{"Value":"'Normal'"}}} } },
            "placement":   {"expr":{"Literal":{"Value":"'custom'"}}},
            "iconSize":    {"expr":{"Literal":{"Value":"29D"}}},
            "horizontalAlignment": {"expr":{"Literal":{"Value":"'center'"}}} },
          "selector": {"id":"default"} },
        { "properties": { "show": {"expr":{"Literal":{"Value":"true"}}} } },
        { "properties": {
            "topMargin": {"expr":{"Literal":{"Value":"0L"}}},
            "bottomMargin": {"expr":{"Literal":{"Value":"0L"}}},
            "rightMargin": {"expr":{"Literal":{"Value":"0L"}}},
            "shapeType": {"expr":{"Literal":{"Value":"'custom'"}}},
            "image": { "image": { "name": {"expr":{"Literal":{"Value":"'icon-park-twotone_clear.png'"}}},
                "url": {"expr":{"ResourcePackageItem":{
                          "PackageName":"RegisteredResources","PackageType":1,
                          "ItemName":"icon-park-twotone_clear5968561032249496.png"}}},
                "scaling": {"expr":{"Literal":{"Value":"'Normal'"}}} } },
            "iconSize": {"expr":{"Literal":{"Value":"32D"}}},
            "horizontalAlignment": {"expr":{"Literal":{"Value":"'center'"}}} },
          "selector": {"id":"hover"} }
      ],
      "text": [
        { "properties": { "show": {"expr":{"Literal":{"Value":"false"}}} } },
        { "properties": {
            "text":      {"expr":{"Literal":{"Value":"'Панель фільтрів'"}}},
            "fontColor": {"solid":{"color":{"expr":{"Literal":{"Value":"'#9E9F9F'"}}}}},
            "fontSize":  {"expr":{"Literal":{"Value":"10D"}}},
            "horizontalAlignment": {"expr":{"Literal":{"Value":"'left'"}}},
            "leftMargin":   {"expr":{"Literal":{"Value":"30L"}}},
            "bottomMargin": {"expr":{"Literal":{"Value":"3L"}}} },
          "selector": {"id":"default"} },
        { "properties": {
            "fontSize": {"expr":{"Literal":{"Value":"10D"}}},
            "bold":     {"expr":{"Literal":{"Value":"true"}}},
            "text":     {"expr":{"Literal":{"Value":"'Панель фільтрів'"}}},
            "fontColor":{"solid":{"color":{"expr":{"ThemeDataColor":{"ColorId":2,"Percent":0}}}}} },
          "selector": {"id":"hover"} }
      ],
      "fill":    [ { "properties": { "show": {"expr":{"Literal":{"Value":"false"}}} } } ],
      "outline": [ { "properties": { "show": {"expr":{"Literal":{"Value":"false"}}} } } ]
    },
    "visualContainerObjects": {
      "visualLink": [ { "properties": {
          "show":     {"expr":{"Literal":{"Value":"true"}}},
          "type":     {"expr":{"Literal":{"Value":"'Bookmark'"}}},
          "bookmark": {"expr":{"Literal":{"Value":"'111bc5e067518804b279'"}}},
          "showDefaultTooltip": {"expr":{"Literal":{"Value":"false"}}} } } ],
      "lockAspect": [ { "properties": { "show": {"expr":{"Literal":{"Value":"true"}}} } } ]
    },
    "drillFilterOtherVisuals": true
  },
  "howCreated": "InsertVisualButton"
}
```

### §4.1 Serialization law (same as shape, incident І-14)

| Entry kind | Selector | Example |
|---|---|---|
| `show` toggle (`icon.show`, `text.show`, `fill.show`, `outline.show`) | **none** — bare entry | `{ "properties": { "show": {...true} } }` |
| Values (image, iconSize, text, fontColor, margins, fillColor, weight) | `"selector": {"id":"default"}` | second entry in the same array |
| Hover state | `"selector": {"id":"hover"}` | third entry in the same array |

A `show` written with a selector, or a value written without one, makes Desktop drop the card and
render the theme default. Every ground-truth `actionButton` on the page follows this two-entry
pattern without exception.

### §4.2 Icon + label in one button

`text.show: true` plus `text.leftMargin: 30L` pushes the caption right, clearing the space the
icon occupies at `horizontalAlignment: 'center'` / `iconSize: 29D`. That is how "icon + caption"
is one control, not two. An icon-only button sets `text.show: false`; GT keeps the caption
properties in the file regardless, so flipping one flag restores the label.

Units seen in GT: `D` on doubles (`29D`, `10D`, `85D`), `L` on integers (`30L`, `3L`, `5L`).
Mixing them up is a structure error, which is the class that breaks the whole report.

### §4.3 PNG registration

`image.name` is the human file name; `image.url.ResourcePackageItem.ItemName` is the **registered**
name and in GT it carries a Desktop-appended numeric suffix
(`icon-park-twotone_clear.png` → `icon-park-twotone_clear5968561032249496.png`). `ItemName` must
match an entry in `report.json` → `resourcePackages[name="RegisteredResources"].items[]`
(`{"name": …, "path": …, "type": "Image"}`) and a real file in
`StaticResources/RegisteredResources/`. Default and hover states may point at two different
registered items. Fetching/registering icons is **pbi-headers-icons-imagery** + `icon-set-manager`.

### §4.4 `visualLink.type`

Values observed in this report: `'Bookmark'` (with a `bookmark` key) and `'ClearAllSlicers'`
(no `bookmark` key — the action is built in). A `'Bookmark'` link may additionally carry
`navigationSection` when the target bookmark lives on another page. **This list is not exhaustive** —
other action types exist in Power BI; read a Desktop-emitted button before using one.

Clear-all therefore needs **no bookmark at all**:

```json
"visualLink": [ { "properties": {
  "show": {"expr":{"Literal":{"Value":"true"}}},
  "type": {"expr":{"Literal":{"Value":"'ClearAllSlicers'"}}},
  "showDefaultTooltip": {"expr":{"Literal":{"Value":"false"}}} } } ]
```

### §4.5 Live count in the caption

`text.properties.text` accepts a measure instead of a literal — the caption then shows the row count
after filters, e.g. "Застосувати вибір (10 134)":

```json
"text": { "expr": { "Measure": {
  "Expression": { "SourceRef": { "Entity": "_Measures" } },
  "Property": "AC.Burnout_risk.Застосувати вибір" } } }
```

Set it on both the `default` and `hover` entries, otherwise the caption changes on hover.

---

## §5. The bookmark file

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmark/2.1.0/schema.json",
  "displayName": "Burnout.Filters_OFF",
  "name": "d22896067aa203f59ba6",
  "options": {
    "applyOnlyToTargetVisuals": true,
    "targetVisualNames": [ "2159afacf1398140e3aa", "e0c18e9225a358a78987", "29646893edb5b48942e1", "…" ],
    "suppressData": true
  },
  "explorationState": {
    "version": "1.3",
    "activeSection": "37d8618c987d51132762",
    "sections": {
      "37d8618c987d51132762": {
        "visualContainers": {
          "d2500a93e3b5b8eace39": { "singleVisual": { "visualType": "shape", "objects": {}, "display": { "mode": "hidden" } } },
          "5aa4c0b11bb110914b64": { "singleVisual": { "visualType": "actionButton", "objects": {} } }
        },
        "visualContainerGroups": { "2159afacf1398140e3aa": { "isHidden": true } }
      }
    },
    "objects": { "merge": { "outspacePane": [ { "properties": {
      "expanded": {"expr":{"Literal":{"Value":"false"}}},
      "visible":  {"expr":{"Literal":{"Value":"false"}}} } } ] } }
  }
}
```

- **Group visibility is ONLY in `visualContainerGroups`.** `visualContainers` carries per-visual
  state, where hiding is `display: { "mode": "hidden" }` — a different key in a different section.
  Putting the group id in `visualContainers` does nothing.
- Nested groups nest the same way (GT):
  `{"2159afacf1398140e3aa":{"isHidden":false},"9552bd717e7291047a2b":{"children":{"1e88e7eaf98deee73df2":{"isHidden":false},"bb41a1638c6a6bdd424f":{"isHidden":true}}}}`
- `explorationState.version` is the string `"1.3"` in this report.
- The `outspacePane` object is how the bookmark also pins the filter pane closed. Optional.

### §5.1 `options` — where panels actually break

| Key | Effect | When |
|---|---|---|
| `applyOnlyToTargetVisuals: true` + `targetVisualNames: [...]` | bookmark touches only those names; everything else keeps its state | always, on every panel bookmark |
| `suppressData: true` | display-only bookmark: flips visibility, does **not** restore slicer selections | the open/close pair |
| `suppressDisplay: true` | data-only bookmark: restores slicer values, does **not** move anything | "Reset to defaults" / "Clear filters" |
| neither | applies both | "open the panel *and* reset it" in one click |

Across 88 bookmarks in the GT report: 53 use `suppressData`, 18 use `suppressDisplay`,
**0 use both** (both together would leave a bookmark that does nothing).

`targetVisualNames` in GT holds 22 names for this panel and the **first entry is the group's own
name**, followed by the backdrop, the slicers and the buttons. Omit the group id and visibility
never changes — the button click is silently filtered out.

The GT list also contains 7 ids that no longer exist on the page (deleted visuals). Stale entries
are harmless but noisy; when you author the list, generate it from the files:

```bash
python - <<'PY'
import json,glob,os
page='definition/pages/<pageId>/visuals'; gid='<groupId>'
names=[gid]+[json.load(open(f,encoding='utf-8'))['name'] for f in glob.glob(page+'/*/visual.json')
              if json.load(open(f,encoding='utf-8')).get('parentGroupName')==gid]
print(json.dumps(names,indent=2))
PY
```

### §5.2 Registration in `bookmarks.json` — the two item shapes

A `.bookmark.json` file that is not listed in `definition/bookmarks/bookmarks.json` does not exist
for Desktop. But *how* you list it is not free-form: schema `bookmarksMetadata/1.0.0` defines
`items[]` as an **anyOf of two variants**, and nothing in between validates.

| Variant | Allowed keys | Required | Notes |
|---|---|---|---|
| `SingleBookmarkMetadata` | **`name` only** | `name` | `additionalProperties: false` — no other key may appear |
| `BookmarkGroupMetadata` | `name`, `displayName`, `children` | **all three** | `children` is the array of member bookmark `name`s |

**A single (ungrouped) bookmark is registered as `{"name": "<id>"}` and nothing else.**

```json
{ "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmarksMetadata/1.0.0/schema.json",
  "items": [
    { "name": "<loneBookmarkId>" },
    { "name": "<anotherLoneBookmarkId>" },
    { "name": "e56e247b6f21deb6be50", "displayName": "AC.Burnout_risk.Slicer_Pannel",
      "children": ["111bc5e067518804b279", "a3e3d5a533cc32f58606", "d22896067aa203f59ba6", "9dbbce1ddc5aeedff7a5"] }
  ] }
```

The third item is verbatim GT: the four panel bookmarks under one named group. The first two show
the leaf form and are **derived from the schema, not observed in GT** — that report contains no
ungrouped bookmark at all (see below).

#### The hybrid that breaks the report (incident І-22)

Writing `{"name": "<id>", "displayName": "Filters ON"}` for a lone bookmark matches **neither**
variant: `displayName` is forbidden on a leaf, and `children` is missing for a group. The report
then does not open at all. Desktop's loader emits three errors per offending item (verbatim, from a
Ukrainian-locale Desktop; the pointer `/items/0` is the index of the bad item):

```
Додаткову властивість "displayName" включено до властивості /items/0 bookmarks/bookmarks.json.
Обов'язкову властивість "children" не включено до властивості /items/0 bookmarks/bookmarks.json.
Як властивість /items/0 bookmarks/bookmarks.json надано неприпустиме значення.
```

Read them as: *additional property `displayName` present* (fails the leaf variant) / *required
property `children` missing* (fails the group variant) / *therefore the value is invalid*. Three
errors for one mistake is the signature of a failed `anyOf`, not of three separate problems.

**Where the human-readable name lives:** in `displayName` **inside `<id>.bookmark.json`** (see the
`"displayName": "Burnout.Filters_OFF"` at the top of §5). `bookmarks.json` is an index and an
ordering/grouping structure, not a label store. A `displayName` in the index names a *group* of
bookmarks and only a group.

#### Why ground truth did not protect against this

The pattern in this file was lifted from a production report, whose `bookmarks.json` holds **26 items and
all 26 are groups** (`{'children','displayName','name'}`). The leaf form does not physically occur
in that report, so it could neither be copied from it nor noticed as missing.

> **Law — the boundary of ground truth.** Ground truth proves only what it contains. When a
> construct has variants and the observed report shows one of them, read the other variants from
> the **schema** (`$schema` URL of the file), not by analogy from the variant you saw. The absence
> of a form in ground truth is evidence about the sample, never evidence about the format.

This is why §8.1 exists: the schema is the authority, and it is cheap to consult mechanically.

---

## §6. The four bookmarks of a real panel (GT roles)

| Bookmark | `options` | Group state | Bound to |
|---|---|---|---|
| `Filters_ON` | `suppressData: true`, 22 targets | `isHidden: false` | opener buttons in the header groups |
| `Filters_OFF` | `suppressData: true`, 22 targets | `isHidden: true` | the panel's ✕ button **and** the "apply" button |
| `Slicers_by_default` | no suppress flag, 22 targets | `isHidden: false` | the standalone filter-icon button; the "За замовчуванням" button inside the panel |
| `Clear_filters` | `suppressDisplay: true`, 22 targets | (present but suppressed) | reset action |

Two observations worth copying:

1. **"Apply" is just "close".** Slicers filter live, so the apply button points at the same
   *Filters_OFF* bookmark as the ✕. It exists as a UX affordance, not as a mechanism.
2. A data-only bookmark still serializes `visualContainerGroups` in its `explorationState`;
   `suppressDisplay: true` is what makes that section inert. Do not delete the section by hand.

---

## §7. Build order

1. Author the panel in Desktop once if you can — then edit the emitted files. Otherwise:
2. Create `visuals/<groupId>/visual.json` with `visualGroup` + `"isHidden": true`.
3. Add the backdrop `shape` and every slicer with `parentGroupName`, coordinates **relative to the
   group**, backdrop at the lowest `z`.
4. Add in-panel buttons: ✕ / apply → close bookmark, clear-all → `'ClearAllSlicers'`.
5. Add the opener `actionButton` **outside** the group (no `parentGroupName`), icon per §4.
6. Register the PNG in `report.json` `resourcePackages` and drop the file into
   `StaticResources/RegisteredResources/`.
7. Write the two bookmark files (§5), generate `targetVisualNames` from the files, add them to
   `bookmarks.json` in the correct item shape — leaf `{"name": …}` or group
   `name`+`displayName`+`children` (§5.2).
8. **Validate every touched file against its `$schema` (§8.1) before opening Desktop**, then walk
   the §8.2 checklist.

---

## §8. Verification

### §8.1 Schema validation — mandatory, before Desktop

**Every file you added or changed must be validated against the schema its own `$schema` key names,
before the report is opened.** Power BI Desktop's loader is a JSON-Schema validator: what it rejects
on open, an offline validator rejects here — same errors, far shorter feedback loop.

A hand-written structural validator (JSON parses, names unique, cross-references resolve) **cannot**
substitute. In incident І-22 the broken `bookmarks.json` was valid JSON with correct cross-references
and passed every structural check; only the schema knew that `items[]` is a two-variant anyOf.

Ready-made script — `docs/audits/evidence-scripts/pbir_schema_validate.py` in this repo:

```bash
pip install jsonschema referencing
python docs/audits/evidence-scripts/pbir_schema_validate.py "<path>/<Name>.Report/definition"
```

It walks `definition/*.json`, `definition/bookmarks/*.json`, `definition/pages/**` and every
`visuals/*/visual.json`; for each file it reads `doc['$schema']`, fetches that schema (disk cache),
and runs `jsonschema.Draft202012Validator(...).iter_errors(doc)` with a `referencing` `Registry` so
remote `$ref`s resolve. It prints the JSON pointer and message for each error and a per-schema
tally at the end.

**Published-schema gaps.** Some versions Desktop writes are not served publicly and 404:

| Declared by Desktop | Public status | Handling |
|---|---|---|
| `visualContainer/2.10.0` | 404 | validate against `visualContainer/2.9.0` |
| `visualContainerMobileState/2.5.0` | 404 | validate against the newest published version |

Substitutions live in the script's `FALLBACK` dict (`{'visualContainer/2.10.0':
'visualContainer/2.9.0'}` today) — add a mapping there when a new 404 shows up, rather than skipping
the file. A skipped file is an unchecked file.

The fallback schema pins `$schema` to its own `const`, so it reports one spurious error at pointer
`/$schema`. That error comes from the substitution, not from your file — filter it out (the script
does). Everything else in the file is still checked.

The run that confirmed the І-22 fix: **312 files, 0 errors.** A clean run is not proof the panel
works — it is proof the report will open. Rendering, hover and click behaviour stay unverifiable
headless (§8.2).

### §8.2 Checklist

```bash
# every touched file parses (cheap pre-check; §8.1 is the real gate)
for f in definition/bookmarks/*.json definition/pages/<pageId>/visuals/*/visual.json; do
  python -c "import json,sys;json.load(open(sys.argv[1],encoding='utf-8'))" "$f" || echo "BAD $f"
done
```

| Check | Pass condition |
|---|---|
| **Schema** | every added/changed file validates against its own `$schema` (§8.1) |
| Default state | group file has `"isHidden": true` |
| Opener isolation | opener's `visual.json` has **no** `parentGroupName` |
| Scope | each bookmark's `targetVisualNames[0]` is the group id; every member present |
| Toggle purity | both toggle bookmarks have `suppressData: true` |
| Section | group id appears under `visualContainerGroups`, never `visualContainers` |
| Serialization | every `show` entry has no selector; every value entry has one |
| Icon | `ItemName` present in `report.json` `resourcePackages` **and** on disk |
| Registration | both bookmark ids appear in `bookmarks.json` **in a valid item shape** (§5.2) |

Rendering, hover states and live click behaviour cannot be verified headless — say so explicitly
instead of claiming the panel works.

---

## §9. Boundaries

| Question | Skill |
|---|---|
| Which slicer type, how to style it | pbi-slicers-filter-panel |
| PBIR-**Legacy** `report.json` bookmarks / visibility | powerbi-bookmarks |
| Switching pages, tab bars, selected state | pbi-navigation-tabs |
| Fetching and registering the PNG icon | pbi-headers-icons-imagery, icon-set-manager |
| Where the panel and its opener sit on the canvas | pbi-page-layout |
| The measure behind the live count | dax-measures |
