# PBIR (enhanced) bookmarks — the canon

Verified against the Microsoft JSON schemas and ground-truth (GT) reports; every
claim marked GT was read from a real file, every claim marked *schema* from the
`$schema` URL of that file. Legacy `report.json` bookmarks → `reference.md`.

## §1. Where bookmarks live

```
<Name>.Report/
├─ definition.pbir                       version 4.0+; datasetReference byPath | byConnection
├─ StaticResources/RegisteredResources/  images, themes
└─ definition/
   ├─ bookmarks/
   │  ├─ <name>.bookmark.json            one file per bookmark (state + options)
   │  └─ bookmarks.json                  index: order and groups — NOT a label store
   ├─ pages/<pageName>/page.json
   ├─ pages/<pageName>/visuals/<visualName>/visual.json
   └─ report.json                        resourcePackages, themeCollection
```

- `name` is a 20-character id by default (`d22896067aa203f59ba6`); the file is
  `<name>.bookmark.json`. Renaming files is allowed (word characters and hyphens)
  but needs a Desktop restart and can break references — keep the default.
- A bookmark may **persist data values** (slicer selections, filter values) into
  its JSON — read before committing anything that came from production data.
- Copying a `.bookmark.json` into another report intentionally strips visuals
  that don't exist there.
- Source: https://learn.microsoft.com/power-bi/developer/projects/projects-report#pbir-format

## §2. The bookmark file (`bookmark/2.1.0`) — GT

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmark/2.1.0/schema.json",
  "displayName": "Burnout.Filters_OFF",
  "name": "d22896067aa203f59ba6",
  "options": {
    "applyOnlyToTargetVisuals": true,
    "targetVisualNames": [ "2159afacf1398140e3aa", "e0c18e9225a358a78987", "…" ],
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

Laws:

- **Group visibility lives ONLY in `visualContainerGroups`** (`isHidden`).
  `visualContainers` carries per-visual state, where hiding is
  `display.mode: "hidden"`. A group id inside `visualContainers` does nothing.
- `display.mode` enum (*schema*): `maximize` | `spotlight` | `elevation` | `hidden`.
- Nested groups nest the same way (GT):
  `{"<g1>":{"isHidden":false},"<g2>":{"children":{"<g2a>":{"isHidden":false},"<g2b>":{"isHidden":true}}}}`
- `explorationState.version` is the string `"1.3"` in current Desktop output;
  older reports carry `bookmark/1.4.0` files with the same shape.
- `objects.merge.outspacePane` pins the Filters pane open/closed. Optional.
- `sections.<id>.filters` holds captured page/visual filters — the same
  "captured card must be patched in every bookmark that targets the visual" rule
  as Legacy (`reference.md` §2) applies here.

## §3. `options` — the four switches and what the UI calls them

| Key | Desktop UI | Effect |
|---|---|---|
| `applyOnlyToTargetVisuals: true` + `targetVisualNames[]` | **Selected visuals** | the bookmark touches only those names; everything else keeps its live state |
| `suppressData: true` | **Data** unchecked | display-only: flips visibility, does **not** restore slicers/filters |
| `suppressDisplay: true` | **Display** unchecked | data-only: restores slicer values, does **not** show/hide anything |
| `suppressActiveSection: true` | **Current page** unchecked | applies without switching to the captured page |
| none of the suppress keys | all three checked | applies everything |

Across 88 GT bookmarks: 53 `suppressData`, 18 `suppressDisplay`, **0 both** —
a bookmark with both suppressed does nothing.

**The #1 gotcha is the same as in Legacy:** with `applyOnlyToTargetVisuals`,
any id you set in `explorationState` that is missing from `targetVisualNames` is
silently ignored — the button click does nothing and no error appears. The GT
list holds the **group's own name first**, then the backdrop, slicers and
buttons. Generate the list from the files:

```bash
python - <<'PY'
import json,glob
page='definition/pages/<pageId>/visuals'; gid='<groupId>'
names=[gid]+[json.load(open(f,encoding='utf-8'))['name'] for f in glob.glob(page+'/*/visual.json')
              if json.load(open(f,encoding='utf-8')).get('parentGroupName')==gid]
print(json.dumps(names,indent=2))
PY
```

Stale ids (deleted visuals) in the list are harmless; missing ids are fatal.
Source: https://learn.microsoft.com/power-bi/create-reports/desktop-bookmarks

## §4. `bookmarks.json` (`bookmarksMetadata/1.0.0`) — two shapes, nothing in between

`items[]` is an **anyOf** of exactly two variants (*schema*, `additionalProperties:false`):

| Variant | Allowed keys | Required |
|---|---|---|
| `SingleBookmarkMetadata` | **`name` only** | `name` |
| `BookmarkGroupMetadata` | `name`, `displayName`, `children` | **all three** |

```json
{ "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/bookmarksMetadata/1.0.0/schema.json",
  "items": [
    { "name": "<loneBookmarkId>" },
    { "name": "e56e247b6f21deb6be50", "displayName": "AC.Burnout_risk.Slicer_Pannel",
      "children": ["111bc5e067518804b279", "a3e3d5a533cc32f58606", "d22896067aa203f59ba6", "9dbbce1ddc5aeedff7a5"] }
  ] }
```

**Incident І-22:** `{"name": "<id>", "displayName": "Filters ON"}` for a lone
bookmark matches neither variant and the report **does not open**. Desktop emits
three errors per item (additional property `displayName` / required `children`
missing / invalid value) — the signature of a failed `anyOf`, one mistake.
The human-readable name lives in `displayName` **inside** `<id>.bookmark.json`;
in the index, `displayName` names a *group* only.

> **Law — the boundary of ground truth.** GT proves only what it contains.
> When a construct has variants and the observed report shows one, read the
> other variants from the schema, never by analogy.

## §5. Bookmark groups — authoring

- A group is an index item with `name` + `displayName` + `children[]`; a child
  is listed by `name` only, and its file must exist.
- `children` order = navigator order = Bookmarks pane order.
- A `bookmarkNavigator` visual binds `objects.bookmarks[].properties.bookmarkGroup`
  to the group `name` and `selectedBookmark` to a child `name` → JSON in
  `pbi-navigation-tabs/reference.md` §6.
- Ungrouping in Desktop deletes the group item, never the bookmarks.
- Limitation: only **one** active bookmark per report — two navigators over
  groups that control overlapping settings show a misleading active state.

## §6. The four bookmarks of a real panel (GT roles)

| Bookmark | `options` | Group state | Bound to |
|---|---|---|---|
| `Filters_ON` | `suppressData` | `isHidden: false` | opener buttons |
| `Filters_OFF` | `suppressData` | `isHidden: true` | ✕ button **and** "apply" |
| `Slicers_by_default` | no suppress | `isHidden: false` | the standalone filter-icon button |
| `Clear_filters` | `suppressDisplay` | (suppressed) | reset action |

Same skeleton serves tabs-in-one-page: one bookmark per tab, each hides every
other tab's group and shows its own, all with `suppressData` so a tab click
never resets the reader's slicers. Wiring the buttons → `pbi-buttons-actions`.

## §7. Verification — the schema is the gate

1. `python scripts/pbir_schema_validate.py <.Report>` — validates every
   `*.bookmark.json` and `bookmarks.json` against its own `$schema` (downloads
   the schema; `pip install jsonschema` once), then runs the referential checks:
   every `children[]`/index name has a file, every file is indexed, every
   `targetVisualNames` id exists on the captured page, every touched id is targeted.
2. The plugin hook (`hooks/check_report.py`) runs the cheap subset on every
   Edit/Write automatically.
3. Desktop: close **without saving** before editing, reopen after — it caches
   bookmark state and will overwrite your JSON on save.

## §8. Sources

- PBIR project folder: https://learn.microsoft.com/power-bi/developer/projects/projects-report
- Bookmarks in Desktop (options ↔ UI): https://learn.microsoft.com/power-bi/create-reports/desktop-bookmarks
- Navigators and their limitations: https://learn.microsoft.com/power-bi/create-reports/button-navigators
- Schemas: https://github.com/microsoft/json-schemas/tree/main/fabric/item/report/definition
  (`bookmark/2.1.0`, `bookmarksMetadata/1.0.0`, `visualContainer/2.9.0`)
