# powerbi-craft — Claude Code skills marketplace

Craft skills for building Power BI / Fabric reports with Claude Code: per-visual
recipes, report UX, design language, quality gates, DAX, PBIP git lifecycle,
data storytelling — grown and battle-tested on real enterprise reporting projects.

**Catalog site**: https://nevsky-bi-user.github.io/powerbi-craft-marketplace/ —
browse every skill with copy-ready install commands, install-everything blocks
(terminal or agent prompt), and setup instructions incl. auto-update. Rebuilt
automatically from skill frontmatters on every push (see `site/`,
`scripts/build_catalog.py`, `docs/site-design.md`).

## Install

```bash
claude plugin marketplace add Nevsky-BI-user/powerbi-craft-marketplace
claude plugin install pbi-visuals@powerbi-craft
```

## Plugins

| Plugin | Skills | What it owns |
|---|---|---|
| `pbi-visuals` | 13 | one skill per visual type + shared report.json mechanics |
| `pbi-report-ux` | 11 | layout, navigation + navigators, buttons & actions, slicers/panels, drillthrough, tooltips, mobile, bookmarks (PBIR + Legacy) |
| `pbi-design-language` | 7 | design tokens, typography, colour accessibility, CF, theme.json, icons, corporate themes |
| `pbi-quality` | 4 | chart-choice strategy, evidence-gated review, approval-gated redesign, manual test cases |
| `report-storytelling` | 3 | what a page asserts: message titles, comparison bases; Ukrainian UI-string grammar; dashboard-copy — business Ukrainian labels + EN→UA glossary |
| `dax-craft` | 6 | DAX measures, performance tuning, pre-measure grilling, SVG measures, Deneb/Vega-Lite, DAX regression tests |
| `pbip-devops` | 5 | PBIP scaffold, deploy, PR review, release notes, Fabric CLI |
| `azure-ops` | 7 | cost, diagnostics, RBAC, Azure DevOps rituals (work items, PRs, hygiene) |
| `project-bootstrap` | 4 | CLAUDE.md bootstrap, Rayfin platform bootstrap, data-entry app blueprint, React SPA UX baseline |
| `agent-craft` | 2 | Model orchestration + plain-language reporting (UA); exec-haiku/sonnet/opus + verify-skeptic agents |

## Це один організм / One organism

Скіли густо посилаються один на одного через межі плагінів (понад 270
перехресних посилань): `pbi-kpi-cards` маршрутизує формулювання в `data-storytelling`,
міри — у `dax-measures`, токени — у `pbi-design-system`. **Рекомендовано
ставити всі 10 плагінів.** Часткова інсталяція працює — посилання на
невстановлений скіл просто не завантажиться, деградація мʼяка — але повну
силу дає повний набір.

Skills cross-reference each other across plugin boundaries (270+ references).
**Installing all ten plugins is recommended.** Partial installs degrade
gracefully — a reference to an absent skill simply does not load.

## Requirements

Skills and agents: none — any Claude Code install. The report-validation hook
additionally expects **bash** (on Windows: Git Bash, which Claude Code uses
anyway) and **python 3** (`python`, `python3` or the `py` launcher — if none is
found the hook silently does nothing). Disable hooks any time with
`POWERBI_CRAFT_HOOKS=0`.

## Agents and hooks

Beyond skills, five plugins ship extras — disclosed here because hooks run
automatically on your machine after installation:

- `pbi-report-ux` ships a **PostToolUse hook**: after any Edit or Write inside
  `*.Report/`, it checks the touched file — Legacy `report.json` (outer JSON +
  nested config strings, sibling-bookmark symmetry) and PBIR enhanced files
  (`*.bookmark.json` scope vs `targetVisualNames`, `bookmarks.json` leaf/group
  shapes, `visual.json` action links resolving to real pages and bookmarks,
  the serialization law). Read-only, silent when clean, feeds findings back to
  Claude when broken. Skips silently if `python` is not on PATH.
  Source: `plugins/pbi-report-ux/hooks/` — three small readable files.
- `pbi-quality` ships the **`report-design-reviewer` agent**,
  `report-storytelling` ships the **`claim-auditor` agent**, and
  `project-bootstrap` ships the **`ux-baseline-auditor` agent** — independent
  read-only reviewers (sonnet) for fresh-eyes QA that cannot edit your files.
- `agent-craft` ships four agents: `exec-haiku` / `exec-sonnet` / `exec-opus` —
  brief-driven executors that CAN edit files within the brief's boundaries
  (tools: Read, Glob, Grep, Edit, Write, Bash) — and `verify-skeptic`, a
  read-only adversarial verifier (`model: inherit`). All four write their
  reports under the plain-language rules of the `plain-report` skill.

## External skills referenced, not shipped

Some skills hand work to skills that live elsewhere. A clean install of this
marketplace alone will not find them — install the source or read the fact
inline where the skill quotes it.

| Reference | Source | What it owns |
|---|---|---|
| `powerbi-report-authoring`, `powerbi-report-design`, `powerbi-report-planning` | Microsoft `skills-for-fabric` (MIT) | raw PBIR file mechanics, validation (`powerbi-report-author validate <.Report>`), Desktop reload |
| `fabric-cli-core` | Microsoft `skills-for-fabric` | generic `fab` auth and navigation |
| `pbir-format`, `pbir-cli`, `pbip`, `tmdl` | external Power BI agentic skill sets (e.g. data-goblin) | PBIR schema walkthroughs, PBIP renames, TMDL authoring |
| `pbi-report-design`, `humanizer`, `web-design-guidelines` | author's local library / community skills | report design canon, de-AI-ing prose, a11y checklists |

Our PBIR skills are the layer **above** `powerbi-report-authoring`: it owns the
files, we own bookmarks, buttons, navigators, icons and design decisions.

## Conventions

- SKILL.md ≤ ~100 lines, depth in `reference.md` (progressive disclosure).
- Every description declares explicit `Do NOT trigger for X (owner)` boundaries.
- Empirical claims carry their study and effect size; debunked folklore is
  registered (see `report-storytelling/skills/data-storytelling/reference.md` §12)
  so it cannot creep back in.
- Ukrainian + English triggers throughout.

## License

MIT (see LICENSE).
