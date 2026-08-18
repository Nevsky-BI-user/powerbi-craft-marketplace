# powerbi-craft — Claude Code skills marketplace

Craft skills for building Power BI / Fabric reports with Claude Code: per-visual
recipes, report UX, design language, quality gates, DAX, PBIP git lifecycle,
data storytelling — grown and battle-tested on real Naftogaz reporting projects.

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
| `pbi-design-language` | 7 | design tokens, typography, colour accessibility, CF, theme.json, icons, Naftogaz theme |
| `pbi-quality` | 4 | chart-choice strategy, evidence-gated review, approval-gated redesign, manual test cases |
| `report-storytelling` | 2 | what a page asserts: message titles, comparison bases; Ukrainian UI-string grammar |
| `dax-craft` | 4 | DAX measures, SVG measures, Deneb/Vega-Lite, DAX regression tests |
| `pbip-devops` | 5 | PBIP scaffold, deploy, PR review, release notes, Fabric CLI |
| `azure-ops` | 3 | cost, diagnostics, RBAC |
| `project-bootstrap` | 3 | CLAUDE.md bootstrap, Rayfin platform bootstrap, data-entry app blueprint |

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

## Conventions

- SKILL.md ≤ ~100 lines, depth in `reference.md` (progressive disclosure).
- Every description declares explicit `Do NOT trigger for X (owner)` boundaries.
- Empirical claims carry their study and effect size; debunked folklore is
  registered (see `report-storytelling/skills/data-storytelling/reference.md` §12)
  so it cannot creep back in.
- Ukrainian + English triggers throughout.

## License

MIT (see LICENSE).
