# `actionButton` — ground truth and per-action snippets (PBIR enhanced)

GT sources: a production PBIR report (filter-panel opener, verified opener id
`7889b2e2454560d165ac`), microsoft/fabric-toolbox FUAM report (Drillthrough,
Back), public PBIR repos (PageNavigation with icon, roundEdge). Schema:
`visualContainer/2.9.0`–`2.10.0` → `visualConfiguration/2.3.0`.

## §1. Full GT — icon + label button bound to a bookmark

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

Read the shape, not the values: bare `show` entries, value entries with a
selector, one selector id per state, `D`/`L` units, `ItemName` with the
Desktop-appended numeric suffix.

## §2. `visualLink` per action

```jsonc
// Page navigation (GT, public repo) — target is the page NAME (folder id), not displayName
"visualLink": [ { "properties": {
  "show": {"expr":{"Literal":{"Value":"true"}}},
  "type": {"expr":{"Literal":{"Value":"'PageNavigation'"}}},
  "navigationSection": {"expr":{"Literal":{"Value":"'66907e008ef2285fa43b'"}}} } } ]

// Bookmark (GT) — plus navigationSection when the bookmark lives on another page
"visualLink": [ { "properties": {
  "show": {"expr":{"Literal":{"Value":"true"}}},
  "type": {"expr":{"Literal":{"Value":"'Bookmark'"}}},
  "bookmark": {"expr":{"Literal":{"Value":"'111bc5e067518804b279'"}}} } } ]

// Drillthrough (GT, FUAM) — drillthroughSection + navigationSection
"visualLink": [ { "properties": {
  "show": {"expr":{"Literal":{"Value":"true"}}},
  "type": {"expr":{"Literal":{"Value":"'Drillthrough'"}}},
  "drillthroughSection": {"expr":{"Literal":{"Value":"'<pageName>'"}}},
  "navigationSection":   {"expr":{"Literal":{"Value":"'<pageName>'"}}} } } ]

// Back (GT, FUAM) — no companion key
"visualLink": [ { "properties": {
  "show": {"expr":{"Literal":{"Value":"true"}}},
  "type": {"expr":{"Literal":{"Value":"'Back'"}}} } } ]

// Clear all slicers (GT) — no bookmark at all
"visualLink": [ { "properties": {
  "show": {"expr":{"Literal":{"Value":"true"}}},
  "type": {"expr":{"Literal":{"Value":"'ClearAllSlicers'"}}},
  "showDefaultTooltip": {"expr":{"Literal":{"Value":"false"}}} } } ]
```

Not yet observed in a file (Microsoft docs list the actions): `ApplyAllSlicers`,
`WebUrl` (with a `url` property), `QnA`, and the `Data function` preview. Add a
button with that action in Desktop, save the project, and copy the emitted
`visualLink` — do not guess the literal.

## §3. Page-navigation button with an icon and rounded corners (GT, public repo)

```jsonc
"objects": {
  "icon": [ { "properties": {
      "shapeType": {"expr":{"Literal":{"Value":"'custom'"}}},
      "image": { "image": {
        "name": {"expr":{"Literal":{"Value":"'1.png'"}}},
        "url":  {"expr":{"ResourcePackageItem":{"PackageName":"RegisteredResources","PackageType":1,"ItemName":"18576312066115739.png"}}},
        "scaling": {"expr":{"Literal":{"Value":"'Normal'"}}} } },
      "horizontalAlignment": {"expr":{"Literal":{"Value":"'center'"}}} },
    "selector": {"id":"default"} } ],
  "fill": [ { "properties": { "show": {"expr":{"Literal":{"Value":"true"}}} } },
            { "properties": { "fillColor": {"solid":{"color":{"expr":{"ThemeDataColor":{"ColorId":4,"Percent":0.6}}}}} },
              "selector": {"id":"default"} } ],
  "shape": [ { "properties": { "roundEdge": {"expr":{"Literal":{"Value":"30L"}}} }, "selector": {"id":"default"} } ]
},
"visualContainerObjects": { "visualLink": [ { "properties": {
  "show": {"expr":{"Literal":{"Value":"false"}}},
  "type": {"expr":{"Literal":{"Value":"'PageNavigation'"}}},
  "navigationSection": {"expr":{"Literal":{"Value":"'66907e008ef2285fa43b'"}}} } } ] }
```

Note `show: false` on the link — Desktop keeps the action definition and just
disables it; flip to `true` to activate.

## §4. States — what is documented vs observed

| Microsoft docs (Desktop UI) | Selector id observed in files |
|---|---|
| Default | `default` |
| On hover | `hover` |
| On press | not observed — read from a Desktop diff before using |
| Disabled | not observed on buttons; theme `$id: "disabled"` exists |
| Loading | not observed |
| (navigators) Selected | `selected` |

Docs: https://learn.microsoft.com/power-bi/create-reports/desktop-buttons#button-states
Fill images per state, Shape/Style/Icon cards per state, Rotation for all states.

## §5. Resolution rules the hook checks

- `navigationSection` / `drillthroughSection` value = an existing
  `definition/pages/<x>/page.json` `name` (or folder name).
- `bookmark` value = an existing `definition/bookmarks/<name>.bookmark.json`
  that is indexed in `bookmarks.json`.
- Image `ItemName` = an item in `report.json → resourcePackages[].items[]` with
  a file under `StaticResources/RegisteredResources/`.
- Every `objects.*[]` entry: `show`-only → no selector; otherwise a selector.

## §6. Sources

- Buttons and actions: https://learn.microsoft.com/power-bi/create-reports/desktop-buttons
- Conditional destination: https://learn.microsoft.com/power-bi/create-reports/button-navigators#set-the-page-navigation-destination-conditionally
- Container schema: https://raw.githubusercontent.com/microsoft/json-schemas/main/fabric/item/report/definition/visualContainer/2.9.0/schema.json
- GT repos: https://github.com/microsoft/fabric-toolbox (FUAM report) · https://github.com/sonbaoharryson/Data_Engineer_JobPulse_Project
