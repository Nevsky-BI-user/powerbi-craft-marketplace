# Navigation variants — reference

Companion to `SKILL.md`: the build script, its config, the coverage report, and the parity
table that maps the navigation patterns of the Rayfin React apps to what PBIR can do.

## §1. `scripts/build_nav.py`

```
python scripts/build_nav.py --report <X.Report> --config cfg.json [--variant V1] [--apply] [--out nav_coverage.md]
```

- **Input** — the same `cfg.json` as `render_nav_previews.py` (`pages[{name,width,height,icon?}]`,
  `hero_page`, `palette`, `selected_style`, `icons`, `groups`) plus:
  `variant` (or `--variant`), `exclude_pages[]` (display names that get no menu item),
  `icon_items {display name → registered ItemName}` (PNGs must already be registered → `pbi-headers-icons-imagery` §9),
  `geometry {"WxH": {x,y,h,item_w,gap,w}}` per-canvas overrides.
- **Reads** `definition/pages/pages.json` (`pageOrder`), every `page.json` (`name`, `displayName`,
  `width`, `height`, `visibility`, `pageBinding.type`), existing `visual.json` positions.
- **Emits per visible page** — V1 top bar, V2 left rail, V3 icon-only rail, V7 grouped bar
  (row 1 = groups, row 2 = pages of the current group): one `visualGroup` "Navigation" +
  one `actionButton` per item, own page in the selected look (`fill` shown + selected colour +
  bold), `visualLink` = `PageNavigation` → page **name**; V6: one `pageNavigator`. Hidden,
  tooltip and drillthrough pages get nothing. V4 (hub) and V5 (☰ overlay) print build
  instructions instead — they are bookmark patterns, not menus.
- **Ids are deterministic** (`sha1(variant, page, item)` → 20 hex) — a re-run overwrites the same
  files, so the second run produces no diff (checked: idempotent on the fixture).
- **Dry run by default**; `--apply` writes. After writing it runs the plugin hook
  (`hooks/check_report.py`) on every generated file and reports the result.
- Geometry defaults: V1/V7 strip at `(24, 8)`, items 96–200 × 32, gap 8; V2 rail 240 px wide,
  items 208 × 32 from `(16, 24)`; V3 rail 56 px, 40 × 40 icons; V6 strip `(24, 8)`, full width.
  Different canvas sizes get different absolute geometry; the same size gets identical geometry.
- Not done by the script: theme-level state styling (`pbi-navigation-tabs`), registering PNGs,
  V4/V5, Legacy `report.json` (exit 1 → `powerbi-visuals`).

## §2. Coverage report (`nav_coverage.md`)

```
# Навігація V1 — покриття
Звіт: `X.Report` · пунктів меню: 6 · видимих сторінок: 6 · прихованих (без меню): 2 · режим: ЗАПИСАНО
| Сторінка | Канвас | Файлів | Selected | Перекриття з наявними візуалами |
| Огляд | 1280×720 | 7 | 1 | — |
…
⚠ Видимі сторінки, яких немає в меню: …
Записано файлів: 42; хук check_report.py: усі чисті
```

Acceptance: every visible page has exactly one `Selected`; no overlaps (or the overlapping visuals
are moved down by the strip height); `pbir_schema_validate.py` clean; Desktop reload shows the
menu on every page and the click lands on the right page.

## §3. Rayfin apps → PBIR parity (what "no worse than the Rayfin apps" can mean)

Source: the two React apps (`Rayfin_Operational_Monitoring` — ROM, sidebar shell; `rayfinn-app`
— RFA, top pill tabs). Mechanism names are the PBIR constructs the marketplace already documents.

| Rayfin pattern | Where it lives | PBIR mechanism | Variant | Limits |
|---|---|---|---|---|
| Top pill tabs with icon + label, active = filled pill | RFA `App.tsx` nav | `pageNavigator` (auto-selected) or `actionButton` row with icons | V6 / V1 | navigator tiles take no custom icons |
| Persistent left sidebar, full height | ROM `Sidebar.tsx` | left rail of buttons in a group on every page | V2 / V3 | no collapse on narrow screens (one canvas) |
| Two-level nav: section row + children | ROM `Sidebar.tsx` | grouped bar: groups row + pages-of-group row | V7 | chevron-as-separate-button = 2 buttons per row |
| Three-state row (active / in section / idle) | ROM `Sidebar.tsx` | two button states + a `shape` overlay for "in section" | V2 / V7 | Power BI buttons carry default/hover/selected only |
| Hamburger → drawer | ROM `TopBar.tsx` | ☰ button + overlay group shown/hidden by a bookmark pair | V5 | → `pbi-filter-panel-bookmark` pattern |
| Hub home with section cards | ROM `DashboardPage.tsx` | cards as buttons (`PageNavigation`) + home button on every page | V4 | manual build |
| Breadcrumb above the title | ROM `AnalyticsOrgPage.tsx` | text box + parent segment as a `PageNavigation` button | any | static text |
| Metric switcher chips | RFA `metrics-page` | **field parameter** slicer | — | best 1:1 in the whole catalogue |
| Hierarchy switcher (org / direct reports) | RFA `org-structure-page` | field parameter or two bookmarks over two visuals | — | |
| Detail drawer / employee profile panel | ROM `MetricDrawer`, RFA profile panel | **drillthrough page** with back button | — | → `pbi-drillthrough` |
| Rich hover tooltip | ROM `HoverTip` | **tooltip page** | — | → `pbi-tooltips` |
| "Reset everything" link | ROM `OrgPage.tsx` | button with `ClearAllSlicers` | — | → `pbi-buttons-actions` |
| Badge counter on a nav item | ROM `Sidebar.tsx` | small card visual over the button | — | conditional visibility via bookmark |
| Status stripe on a card | ROM `DashboardPage.tsx` | 1-px rectangle with conditional fill | — | → `pbi-conditional-formatting` |
| Theme toggle, skeletons, deep links to a row, copy-link, tri-state sort, count-up numbers, responsive breakpoints | ROM/RFA | **no PBIR equivalent** — do not promise | — | |

Icon vocabulary carried over (RFA lucide → icon library): overview = grid, org structure =
network, metrics = bar chart, help = book, search, users, close — the default nav kit in
`icon-set-manager`.

## §4. Selected-state axis and icons — reminder

S1 fill (default V1/V4/V7), S2 indicator bar (V2/V3/V6), S3 weight (never alone), S4 colour
(never alone), S5 fill + weight. The build script implements S1/S5 (fill + bold); S2 needs a
`shape` line per item — add by hand after the build, or extend the script. Icons: `icons:
"labeled"` puts the PNG left of the caption (`text.leftMargin 30L`), `"only"` hides the caption
(V3); V6 ignores icons.
