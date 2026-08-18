# pbi-drillthrough — reference

Ground-truth details and extended patterns that don't fit SKILL.md's word budget.

## 1. Ground-truth markers (verify against a real file — never assume)

These are structural `report.json`/`page.json` facts, not theme properties, so they are not
in `theme-visuals.md`. Confirm them against an existing drill-through page of the target
report before writing anything (BRIEF F1/F2) — Power BI's exact encoding has shifted across
versions, so treat the numbers below as a starting hypothesis, not a literal to copy blind.

- **PBIR-Legacy** (`report.json`): a hidden page is a `section` object carrying a
  `"visibility"` flag (visible pages omit it or use `0`); a filter delivered by a
  drill-through action carries a distinguishing `"howCreated"` value different from a
  manually-built Basic/Advanced filter. Read the target report's own hidden section and its
  own drill filter object first — the exact integers are this report's ground truth, not a
  cross-report constant.
- **PBIR enhanced** (`definition/pages/<page>/page.json`): the same two concepts are a
  string-valued `visibility` (e.g. hidden vs. visible) and a `filterConfig` on the page. Read
  one real `page.json` from the target report before writing property names from memory.
- Either format: the drill page's `filters` must reference fields that exist in the TMDL
  model — verify with the model before wiring (`dax-measures` for anything missing).

## 2. Source-page linkage, in depth

Two ways to make an invisible right-click drill-through discoverable on the source page:

1. **Passive hint** — a small `type/small` / `color/text-secondary` caption near the visual
   ("Right-click → Drill through for detail"), or a nudge on an existing tooltip
   (mechanics: `pbi-tooltips`).
2. **Explicit `actionButton`** with its action set to Drillthrough, bound to the target page
   and drill field. Power BI disables this button automatically unless exactly ONE value of
   the bound field is currently in filter context — this is Desktop-side behavior; don't try
   to force it enabled in JSON.

When users should reach the drill target WITHOUT first selecting a single value (e.g.
"browse the whole customer list" rather than one customer's detail), don't leave a
drillthrough button permanently disabled. Instead add a `pageNavigator` visual (verified
native visual key, theme-visuals.md §5 "Elements, navigation, embedded content") pointing at
the same page — one auto-generated, auto-selected-state button per page, no bookmark logic
required. Pattern and states: `pbi-navigation-tabs`. Visual JSON mechanics for either
approach: `powerbi-visuals`.
