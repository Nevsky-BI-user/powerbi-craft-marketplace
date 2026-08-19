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
| `pbi-report-ux` | 10 | layout, navigation, slicers/panels, drillthrough, tooltips, mobile, bookmarks |
| `pbi-design-language` | 7 | design tokens, typography, colour accessibility, CF, theme.json, icons, corporate themes |
| `pbi-quality` | 4 | chart-choice strategy, evidence-gated review, approval-gated redesign, manual test cases |
| `report-storytelling` | 2 | what a page asserts: message titles, comparison bases; Ukrainian UI-string grammar |
| `dax-craft` | 4 | DAX measures, SVG measures, Deneb/Vega-Lite, DAX regression tests |
| `pbip-devops` | 5 | PBIP scaffold, deploy, PR review, release notes, Fabric CLI |
| `azure-ops` | 3 | cost, diagnostics, RBAC |
| `project-bootstrap` | 4 | CLAUDE.md bootstrap, Rayfin platform bootstrap, data-entry app blueprint, React SPA UX baseline |

## Це один організм / One organism

Скіли густо посилаються один на одного через межі плагінів (123 перехресні
посилання): `pbi-kpi-cards` маршрутизує формулювання в `data-storytelling`,
міри — у `dax-measures`, токени — у `pbi-design-system`. **Рекомендовано
ставити всі 9 плагінів.** Часткова інсталяція працює — посилання на
невстановлений скіл просто не завантажиться, деградація мʼяка — але повну
силу дає повний набір.

Skills cross-reference each other across plugin boundaries (123 references).
**Installing all nine plugins is recommended.** Partial installs degrade
gracefully — a reference to an absent skill simply does not load.

## Requirements

Skills and agents: none — any Claude Code install. The report-validation hook
additionally expects **bash** (on Windows: Git Bash, which Claude Code uses
anyway) and **python 3** (`python`, `python3` or the `py` launcher — if none is
found the hook silently does nothing). Disable hooks any time with
`POWERBI_CRAFT_HOOKS=0`.

## Agents and hooks

Beyond skills, two plugins ship extras — disclosed here because hooks run
automatically on your machine after installation:

- `pbi-report-ux` ships a **PostToolUse hook**: after any edit inside
  `*.Report/`, it re-parses `report.json` (outer JSON + nested config strings)
  and checks sibling-bookmark symmetry (`targetVisualNames` counts,
  `suppressData`). Read-only, silent when clean, feeds findings back to Claude
  when broken. Skips silently if `python` is not on PATH.
  Source: `plugins/pbi-report-ux/hooks/` — three small readable files.
- `pbi-quality` ships the **`report-design-reviewer` agent**,
  `report-storytelling` ships the **`claim-auditor` agent**, and
  `project-bootstrap` ships the **`ux-baseline-auditor` agent** — independent
  read-only reviewers (sonnet) for fresh-eyes QA that cannot edit your files.

## Conventions

- SKILL.md ≤ ~100 lines, depth in `reference.md` (progressive disclosure).
- Every description declares explicit `Do NOT trigger for X (owner)` boundaries.
- Empirical claims carry their study and effect size; debunked folklore is
  registered (see `report-storytelling/skills/data-storytelling/reference.md` §12)
  so it cannot creep back in.
- Ukrainian + English triggers throughout.

## License

MIT (see LICENSE).
