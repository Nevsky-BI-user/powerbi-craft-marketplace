---
name: pbi-redesign-approval
description: Use when redesigning a whole Power BI report or page set with user approval gates - the five-gate process (copy, audit, theme, mockup, page-by-page build) with a DECISIONS.md ledger, verdict grammar, and mandatory stops after every screenshot. Orchestrates other skills; owns only process and artifact formats. Do NOT trigger for single-visual tweaks or one-off formatting (use the specific pbi-* skill) or for design audits alone (use pbi-report-review). Triggers - 'редизайн', 'переробити дизайн', 'жахливий дизайн', 'новий дизайн звіту', 'затвердження дизайну', 'затверджую', 'redesign report', 'design approval', 'rework ugly report'.
---

# Redesign with approval gates

Full-report redesign where the user approves every step from real renders.
The agent NEVER advances without a recorded verdict. This skill owns process,
artifacts, and verdict grammar only - design content lives in referenced skills.

## Artifacts (in the report repo, branch `redesign`)

```
docs/redesign/
  audit/report.md          diagnoses with priorities (gate 1)
  mockups/<page>.html      approved offline HTML mockups (gate 3)
  shots/<page>/v0-before.png, v1.png, v2.png...
  DECISIONS.md             the approval ledger - single source of "done"
```

DECISIONS.md row: `| Дата | Сторінка | Версія | Скріншот | Вердикт | Хто | Коментар |`

## Gates

**0. Copy.** Create branch `redesign` (or copy the project folder if no git).
Never touch the original until final merge.

**1. Audit, zero edits.** Screenshot EVERY page via Desktop Bridge into
`shots/<page>/v0-before.png`. Assess per `pbi-report-review` and
`review-report`: layout/grid, typography, color/contrast, visual choice,
overload, navigation, narrative (`data-storytelling`: does each page
state a finding, does every number carry a base?). Write diagnoses with
priorities (критично/бажано/косметика) to `audit/report.md`. Diagnoses
only - no solutions, no code.

**2. Theme first.** Apply the brand theme (`pbi-corporate-theme`,
`modifying-theme-json`). Before/after screenshots. The user decides which
pages theme alone already fixes.

**3. Mockup per page.** Build a SELF-CONTAINED HTML mockup
`mockups/<page>.html`, openable offline in the server browser: inline CSS
only, zero CDN/external resources; canvas at the exact page size (e.g.
1280x720) at 1:1; Segoe UI; brand theme tokens; 8px grid. Draw ONLY what
Power BI can implement - native visuals with their real formatting options
(no CSS effects PBI cannot do); realistic fake data with the page's actual
field names; label every block with its visual type (card, matrix,
clusteredBarChart...). Content per `pbi-design-system`, `pbi-visualization-strategy`,
`pbi-page-layout` and `data-storytelling` (plus the external `pbi-report-design`
canon if installed) - the real headline text goes into the mockup,
never lorem «Заголовок». Iterate until the user approves. No report code
before mockup approval.

**4. Build page-by-page.** Implement ONE approved page (PBIR file mechanics:
Microsoft `powerbi-report-authoring` from skills-for-fabric, or the external
`pbir-cli` / `pbir-format` skills if installed; navigation and bookmarks per
`pbi-navigation-tabs` / `powerbi-bookmarks`), then `pbir desktop reload` + screenshot to
`shots/<page>/vN.png`, commit `redesign(<page>): vN`, then STOP and wait
for the verdict. Never begin the next page without a ЗАТВЕРДЖЕНО row for
the current one.

## Verdict grammar

- `затверджую <page> vN` → append ЗАТВЕРДЖЕНО row to DECISIONS.md, commit,
  tag `approved/<page>-vN`.
- `правки <page> vN: <list>` → append ПРАВКИ row with the comment, implement
  as vN+1, repeat gate 4.
- A page is done ONLY when DECISIONS.md holds ЗАТВЕРДЖЕНО from the report
  owner. "Done" exists nowhere else.
- All pages approved → merge `redesign` into main only on the user's
  explicit command. Never `git push` (AGENTS law 8).

## Hard rules

- Stop after every screenshot - the user judges real renders, not intentions.
- Trust the render, not the schema: verify via bridge screenshot (law 3).
- Run schema validation before any Desktop open (law 1).
- Content questions (which chart, which colors) route to the referenced
  skills; do not duplicate their facts here.
