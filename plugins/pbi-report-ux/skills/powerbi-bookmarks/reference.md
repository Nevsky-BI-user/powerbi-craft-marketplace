# powerbi-bookmarks — reference

Depth for [SKILL.md](SKILL.md). Numbered sections resolve the "reference.md §N" pointers.

## §1. Where bookmarks live & the visibility model

- Report-level `report.json` → `config` is a **JSON string** (~8 MB). Parse it; bookmarks are at `config.bookmarks` — a recursive tree (`name`, `displayName`, `children`, `explorationState`, `options`).
- A "bookmark group" (folder) is a bookmark with `children` and usually no `explorationState`. A bookmarkNavigator visual bound to that group's id renders one tab per child and applies the child bookmark on click.

The visibility model (`explorationState`):

```
explorationState
  activeSection: "<sectionId>"
  sections.<sectionId>
    visualContainerGroups.<groupId>  -> { "isHidden": true|false, "children": { <subGroupId>: {...} } }
    visualContainers.<visualId>      -> { "singleVisual": { "visualType":"...", "objects":{}, "display": {"mode":"hidden"} } }
```
- **Group** hidden/shown: `visualContainerGroups[groupId].isHidden`. Hiding a group hides all its children visually.
- **Single visual** hidden form: add `"display": {"mode": "hidden"}` inside its `singleVisual`. Visible form: same entry WITHOUT the `display` key.
- A group's own default lives in its container config: `singleVisualGroup.isHidden` (usually `true`). The active bookmark overrides it — but only if the group is a target (see gotcha). The gotcha itself is in SKILL.md.

## §2. Captured filters inside bookmarks (shape differs from live!)

A LIVE `visualContainer.filters` is a compact JSON **string** holding a `[cards]` array.
Inside a bookmark's `explorationState`, the captured `visualContainers.<id>.filters` is a
**native dict**: `{"byExpr": [cards...], "byName": {"<cardName>": {card+state}}}`. A scrubber
that only handles the list form silently skips every bookmark (verified on a production report, 2026-07-28).

Renamed/deleted-measure "ghosts" in captured states (filters.byExpr entries, orderBy,
projections) are inert when the bookmark has `suppressData:true` OR the container id is not
in `targetVisualNames` — safe to scrub. Deleting a captured `orderBy`/`projections` key is
schema-normal (most captured singleVisuals lack them: 12805/15853 no orderBy, 15845/15853
no projections in the audited report).

### ⚠️ A new filter on a visual dies on the first tab click unless you also patch the captures

Setting a filter on a LIVE `visualContainer.filters` card is only half the job. Every bookmark
that lists that visual in `targetVisualNames` **replays its captured filter state onto it**:

| Captured card | Effect of clicking that bookmark |
|---|---|
| card present, has `filter` body | visual gets that value |
| card present, **no** `filter` body | value is **cleared** (card exists, no selection) |
| card **absent** (capture older than the card) | nothing guarantees your value survives — patch it too |

Real incident (production report, 2026-07-30): `STATUS_KEY IN {'1'}` was set on the
"Працюючі" table to exclude mobilized employees. The card `3b7d2f1a…` already existed as an
empty placeholder, so both tab bookmarks had captured it **empty** — the fix worked on load
and evaporated the moment the user clicked a tab. Verifying the live visual only ("filter is
there, diff is clean") proves nothing about runtime.

Rule: after adding/changing a hidden filter, enumerate every bookmark whose
`targetVisualNames` contains that visual id and make its captured card match the live one
(reduced capture form: `name, type, filter, expression, howCreated` — no `objects` /
`isHiddenInViewMode` / `isLockedInViewMode`). Copy the body from the live card, never retype it.

Corollary — filters and visibility are **one** payload per targeted visual: you cannot add a
visual to `targetVisualNames` just to control its filter. The same snapshot's `display` state
(`{"mode":"hidden"}` present = hidden, key absent = **shown**) starts applying too. If a
switcher must not move a visual's visibility, leave it out of that bookmark's targets and
constrain the data another way (a static filter that is correct in every tab state, or a
measure-side guard).

## §3. Tab-isolation pattern (one group per tab)

A tab = a top-level `singleVisualGroup` (parentGroupName absent). Each tab bookmark:
- sets **its** group `isHidden:false` and **every other** tab group `isHidden:true`,
- lists all those groups in `targetVisualNames`.

To add a NEW tab's content as an isolated group `G` on section `S`:
1. Add the group container + child visuals to `sections[S].visualContainers` (group: `singleVisualGroup.isHidden:true` default; children with `parentGroupName: G`).
2. In the tab's bookmark: `explorationState.sections[S].visualContainerGroups[G] = {isHidden:false}` **and** append `G` to `options.targetVisualNames`.
3. In **every other** bookmark that controls section `S`: `...[G] = {isHidden:true}` **and** append `G` to `options.targetVisualNames`. (Without this, `G` leaks onto whatever tab you switch to next, because that bookmark never hides it.)
4. Group-level toggling cascades to children — you usually do NOT need to target children individually.

## §4. Placeholders ("В розробці") and z-order

- Shared placeholder shapes (e.g. an "under construction" rectangle) are often a single top-level visual shown via each tab's bookmark `visualContainers` entry (no `display:hidden`) and hidden on finished tabs (`display:{mode:hidden}`). When you finish a tab, set that placeholder to the hidden form in that tab's bookmark (and confirm the placeholder id is in `targetVisualNames`).
- Each visualContainer has its own canvas `z`. A placeholder at a higher `z` covers your content. Either hide the placeholder, or raise your visuals' `z` above it (update BOTH the top-level `z` and `config.layouts[0].position.z`).

## §5. Byte-faithful editing — use `pbir.py` (in this skill folder)

`report.json` is `json.dumps(indent=2, ensure_ascii=False)` with **CRLF, no BOM, no trailing newline**. Naïve `json.load`→`dump` rewrites floats (`980.00`→`980.0`) = thousands of diff lines. `pbir.py` preserves bytes via Decimal+sentinel.

```python
import pbir                                   # adjust path / pbir.PATH
d = pbir.load('…/report.json')                # whole report (sections + config string)
cfg = pbir.load_config(d['config'])           # parse the embedded bookmarks/config string
# ...edit cfg['bookmarks'] / d['sections'][i]['visualContainers'] ...
d['config'] = pbir.dump_config(cfg)           # compact re-serialize (separators=(',',':'))
pbir.save(d, '…/report.json')                 # CRLF, no BOM
```
Inner `visualContainer.config` and section-level `filters` are ALSO compact JSON **strings** — `json.loads`/`pbir.dump_config` them too.

Always confirm the change is localized:
```python
# a line-based diff vs a .bak should show ONLY: config line (bookmarks) + your inserted/edited containers.
```
A bookmark edit always rewrites the one giant `config` line — that's expected/unavoidable.

## §6. Diagnostic snippet (drop-in)

```python
import json
d=json.load(open(REPORT,encoding='utf-8')); cfg=json.loads(d['config'])
SEC, VID = '<sectionId>', '<visualOrGroupId>'
def walk(bms):
    for b in bms:
        es=b.get('explorationState') or {}; sec=(es.get('sections') or {}).get(SEC)
        if sec:
            vcg=sec.get('visualContainerGroups',{}); vc=sec.get('visualContainers',{})
            state = vcg.get(VID) or vc.get(VID)
            tvn=(b.get('options') or {}).get('targetVisualNames') or []
            if state is not None or VID in tvn:
                print(repr(b.get('displayName')), '| state=',state, '| inTarget=', VID in tvn)
        if b.get('children'): walk(b['children'])
walk(cfg['bookmarks'])
```
If `inTarget=False` anywhere you set a state → that's your bug.

Filter variant — run this after touching any hidden filter card, `CARD` = its `name`:

```python
for path, b in walk_leaves(cfg['bookmarks']):            # your recursive walker
    cap = ((b.get('explorationState') or {}).get('sections',{}).get(SEC,{})
             .get('visualContainers',{}) or {}).get(VID)
    if cap is None: continue
    card = (cap.get('filters',{}).get('byName') or {}).get(CARD)
    tgt  = VID in ((b.get('options') or {}).get('targetVisualNames') or [])
    print('%-46s target=%-5s card=%s' % (path[:46], tgt,
          'body' if (card or {}).get('filter') else ('EMPTY' if card else 'absent')))
```
Any row with `target=True` and `card` not `body` will wipe your filter on click.

## §7. ⚠️ Geometry is stored TWICE — write both, verify the right one

Every `visualContainer` carries its position in two places:

| Where | Precision | Who reads it |
|---|---|---|
| `config.layouts[0].position` (`x/y/z/width/height`) | full float | **Power BI Desktop renders from this** |
| `vc['x'] / vc['y'] / vc['z'] / vc['width'] / vc['height']` | 2 decimals | mirror copy |

Writing only the mirror is a **silent no-op on the canvas**: the file diff looks
right, a checker that reads `vc['x']` reports success, and nothing moves. (Real
incident: a task swapped 8 containers' mirror `x` only, passed its own 8/8
acceptance check, and changed nothing visible for days.)

Rules:
- Never assign geometry by hand. Use `pbir.set_position(vc, cfg, x=…, width=…)`
  — it writes `layouts[0].position` **and** the 2-decimal mirror, then
  re-serializes `vc['config']`.
- Any acceptance check on layout MUST read `cfg['layouts'][0]['position']`,
  never the mirror.
- After editing, run `python pbir.py <report.json>` — it prints the byte-faithful
  roundtrip result and `geometry_mismatches()` (mirror vs config, tolerance
  0.011 for the 2-decimal rounding). Expect `0`.

## §8. Visual properties: where they REALLY live (linter strips wrong placements)

Power BI Desktop's save-time linter silently DELETES properties placed at the wrong
level of the container config. The diff looks fine, a reload even renders it — until
the next Desktop save wipes it. Verified placements (production report, 2026-07-28):

| Property | Correct location | Wrong location (stripped on save) |
|---|---|---|
| Hide hover header icons (`visualHeader.show=false`) | `singleVisual.vcObjects.visualHeader` | top-level `config.vcObjects` — 1242 entries wiped by ONE save |
| Shape shadow («Тінь» card in «Стиль фігури») | `singleVisual.objects.shadow` = `[{"properties":{"show":{"expr":{"Literal":{"Value":"true"}}}}}]` | `vcObjects.dropShadow` (both levels) — ignored for shapes AND stripped |
| Per-column alignment (matrix/table) | `singleVisual.objects.values` + `selector:{metadata:"<queryRef>"}` | — |

Rules:
1. **Never invent a placement.** Grep report.json for an existing WORKING instance of the
   same property first and copy its structure exactly. If none exists, have the user toggle
   it once in Desktop, save, and read the diff — that is authoritative schema.
2. **After every Desktop save, `git diff`** and verify your injected properties survived;
   re-inject anything the linter stripped (same rule as columnHeaders/totals in CLAUDE.md).
3. A property that renders after bridge-reload but has its format-pane toggle OFF is a
   symptom of wrong placement — the pane reads the canonical location only.

## §9. Related

- Byte-faithful report.json pipeline and TMDL gotchas live in the project's `CLAUDE.md`.
- For measure-driven SVG visuals: a measure returning raw `<div><svg>…</svg></div>` binds to the `htmlContent…` custom visual; a measure returning `data:image/svg+xml;utf8,…` with `dataCategory: ImageUrl` binds to a `cardVisual`.
