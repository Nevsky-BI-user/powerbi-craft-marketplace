---
name: fabric-cli-powerbi
description: Use Fabric CLI (fab) for Power BI operations — semantic models, reports, DAX queries, refresh, gateways, report export/rebind/definition update. Triggers - 'fab', 'Fabric CLI', 'онови модель', 'запусти refresh', 'оновлення датасету впало', 'виконай DAX через fab', 'експортуй звіт у PNG/PDF', 'перепривʼяжи звіт', 'refresh dataset', 'execute DAX', 'export report', 'rebind report'. Do NOT trigger for - the deploy approval gate, blast radius and report-only PBIR deploy rules (pbip-deploy), PR review (pbip-pr-reviewer), Azure cost or RBAC (azure-cost, azure-rbac), generic fab auth/navigation (external fabric-cli-core).
---

# Fabric CLI Power BI Operations

## Overview

Expert guidance for working with Power BI items (semantic models, reports, dashboards) using the `fab` CLI. Item-level work (get/export/import/copy) uses `fab` commands directly; refresh, DAX execution, rebind and gateways go through `fab api -A powerbi`.

## When to Use This Skill

Activate automatically when tasks involve:

- Semantic model (dataset) operations — get, export, refresh, update
- Report management — export, clone, rebind to different model
- Executing DAX queries against semantic models
- Managing refresh schedules and troubleshooting failures
- Gateway and data source configuration
- TMDL (Tabular Model Definition Language) operations

NOT for foundational `fab` CLI usage (auth, navigation, generic commands) — that is the
external `fabric-cli-core` skill (Microsoft skills-for-fabric); it is not part of this
marketplace.

## Prerequisites

- If the external `fabric-cli-core` skill is installed, load it first; otherwise the
  essentials are `fab auth login`, `fab auth status`, `fab ls`, `fab --help`
- User must be authenticated: `fab auth status`
- Appropriate workspace permissions for target items

## Quick Reference — Power BI Item Types

| Entity Suffix | Type | Description |
|---------------|------|-------------|
| `.SemanticModel` | Semantic Model | Power BI dataset (tabular model) |
| `.Report` | Report | Power BI report (visualizations) |
| `.Dashboard` | Dashboard | Power BI dashboard (pinned tiles) |
| `.Dataflow` | Dataflow | Power Query dataflow |
| `.PaginatedReport` | Paginated Report | RDL-based paginated report |

Path examples → reference.md §1.

## Automation Scripts

Ready-to-use Python scripts for Power BI tasks. Run any script with `--help` for full options.

| Script | Purpose | Usage |
|--------|---------|-------|
| `refresh_model.py` | Trigger and monitor semantic model refresh | `python scripts/refresh_model.py <model> [--wait] [--timeout 300]` |
| `list_refresh_history.py` | Show refresh history and failure details | `python scripts/list_refresh_history.py <model> [--last N]` |
| `rebind_report.py` | Rebind report to different semantic model | `python scripts/rebind_report.py <report> --model <new-model>` |

Scripts are located in the `scripts/` folder of this skill.

## Task Routing

| Task | Where |
|---|---|
| Semantic model: get info/ID/TMDL, export, import, copy between workspaces | reference.md §2 |
| Refresh: trigger, enhanced (partition-level), schedule, troubleshoot failures | reference.md §3 |
| DAX queries: simple, aggregation, TOPN, parameterized | reference.md §4 |
| Reports: info, connected model, export, clone, rebind, PDF/PPTX export | reference.md §5 |
| Gateways: list, data sources, update credentials | reference.md §6 |
| Take over ownership (owner left the organization) | reference.md §7 |
| Common patterns: dev→prod deployment, model backup, incremental refresh | reference.md §8 |

## Safety Guidelines

- **Always verify workspace context** before refresh operations
- **Test in dev first** — never refresh production without testing
- **Monitor refresh duration** — set appropriate timeouts
- **Backup before major changes** — export definition before updates
- **Use enhanced refresh** for large models to avoid timeouts

## References

For detailed patterns, see:

- [reference.md](./reference.md) — command patterns moved from this file (§1–§8)
- [references/semantic-models.md](./references/semantic-models.md) — Full TMDL operations
- [references/reports.md](./references/reports.md) — Report management
- [references/refresh.md](./references/refresh.md) — Refresh troubleshooting
- [references/dax-queries.md](./references/dax-queries.md) — Advanced DAX patterns
- [references/gateways.md](./references/gateways.md) — Gateway configuration
