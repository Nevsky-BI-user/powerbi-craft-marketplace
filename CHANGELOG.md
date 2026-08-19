# Changelog

## 0.1.8 — 2026-08-19

- Removed all brand assets from the repository: the 26 logo files (13 PNG,
  13 SVG) that shipped with the theme skill are gone. The skill keeps the
  registration mechanics and now expects you to drop your own
  `logo_full_light.png` / `logo_full_dark.png` / `logo_icon_*.png` into
  `assets/logos/`; missing files are skipped instead of crashing the script.
- Renamed two skills to neutral names: `pbi-naftogaz-theme` ->
  `pbi-corporate-theme` (pbi-design-language 0.1.2), `naftogaz-data-entry-app`
  -> `kpi-data-entry-app` (project-bootstrap 0.1.3). Theme files and the
  `name` inside them follow: `corporate-classic.json`, "Corporate Classic".
  The palettes themselves are unchanged.
- Rationale: an MIT-licensed public repository represents that the author may
  license everything in it under those terms (GitHub ToS D.6), and no one can
  grant that over someone else's trademark. Shipping the mechanics without the
  marks removes the representation without losing the skill.

## 0.1.7 — 2026-08-19

- Verified the gate checker on real Linux (Ubuntu 24.04, WSL2, python 3.12), not
  just by reading the code: same output and same exit code as Windows on the same
  PBIP repo.
- Fix found by that run: `pbir.py` (powerbi-bookmarks 0.1.4 / powerbi-visuals
  0.1.2) assumed CRLF line endings, so `verify_roundtrip` reported a false
  mismatch on any LF checkout and the report gate failed with "edits were not made
  through pbir.py". It now reads the convention from the file and preserves it.
  Windows output is byte-identical to before.
- `check_gates.py`: the BPA warning no longer tells non-Windows users to set
  `$env:TE_PATH`.
- Site: the requirements note now states what was actually run where.

## 0.1.6 — 2026-08-19

- `pbip-bootstrap` (pbip-devops → 0.1.2): gate checker ported from PowerShell to
  python (`scripts/check_gates.py`, stdlib only, python 3.9+), so gates run on
  macOS and Linux too. Output was compared line by line with the PowerShell
  version on a live PBIP repo; exit codes match. Only the BPA step stays
  Windows-bound (Tabular Editor) and now degrades to a WARN instead of failing.
  `check-gates.ps1` stays in place for projects that already hook it.
- `react-ux-mechanics` (project-bootstrap → 0.1.2): tooltip value rule, reveal
  granularity, calmer hover, rich tooltips with explicit comparisons.
- `data-storytelling` (report-storytelling → 0.1.2): sharper trigger boundary.
- Site: section band replaces the sticky sidebar, per-plugin descriptions on
  every card, plugin picks highlight their card, new "Що потрібно системі"
  section covering Windows / macOS / Linux.

## 0.1.5 — 2026-08-18

- New skill `react-ux-mechanics` (project-bootstrap → 0.1.1): React SPA UX
  baseline — portal tooltips, sticky table headers, entrance animations with
  reduced-motion guards, error boundaries, lazy routes, optimistic saves,
  URL state, skeletons, count-up numbers; ships assets/patterns.md with nine
  ready recipes.
- New agent `ux-baseline-auditor` (project-bootstrap): read-only audit of an
  existing React app against that baseline; self-sufficient embedded
  checklist.
- Catalog site: full-environment inventory section (all skills of the
  author's machine grouped by source with per-group colors).

## 0.1.4 — 2026-08-18

Trigger coverage completed: all 51 skills now probed live.

- 39 previously untested skills probed with real `claude -p` router runs
  (PBIP repo cwd for report skills, clean Node repo for bootstrap/azure):
  37/39 hit on the first pass; azure-ops and project-bootstrap 6/6.
- The two systematic losers were rewritten and adversarially reviewed:
  `powerbi-visuals` (old prose description had no "Use when", no trigger list
  and no Ukrainian vocabulary — the router never picked it) and `pbi-tables`.
  Both now carry explicit trigger lists and reciprocal Do-NOT boundaries
  (tables ↔ typography/CF/matrix; visuals ↔ every design-skill sibling).
- Coexistence note: with power-bi-agentic-development installed alongside,
  generic report.json / PBIP-table wording may route to its broader
  `pbip`/`pbir-format` skills. In a powerbi-craft-only install,
  `powerbi-visuals` is the sole report.json-mechanics owner.
- `pbi-visuals` → 0.1.1; build script now preserves the marketplace-level
  description field on rebuild.

## 0.1.3 — 2026-08-18

Cross-platform hardening.

- `.gitattributes`: `*.sh` forced to LF — a Windows checkout with
  `autocrlf=true` used to receive CRLF hook scripts that crash bash on every
  report edit.
- `validate-report.sh`: python discovery now also tries the Windows `py -3`
  launcher (plain `python` is often the Microsoft Store stub); opt-out via
  `POWERBI_CRAFT_HOOKS=0`.
- Both agents are now self-sufficient: rulebooks embedded, no reliance on
  reading skill files by relative path (agents run in the user's cwd, not the
  plugin root).
- CI (GitHub Actions, ubuntu + windows): frontmatter YAML of all skills,
  sanitization scan, LF check for shell scripts, plugin/marketplace version
  consistency, and a live pipe-test of the report hook on fixtures.

## 0.1.2 — 2026-08-18

Hooks + agents.

- `pbi-report-ux`: PostToolUse hook validates `report.json` after every edit
  in `*.Report/` — outer/nested JSON parse and sibling-bookmark symmetry.
- `pbi-quality`: `report-design-reviewer` agent (read-only fresh-eyes QA).
- `report-storytelling`: `claim-auditor` agent (mechanical claim-layer checks).
- Contributor hook: SKILL.md frontmatter YAML validation on edit.

## 0.1.1 — 2026-08-18

- 10 oversized skills split into SKILL.md (66–102 lines) + `reference.md`;
  content moved verbatim, preservation verified deterministically.
- Removed `__pycache__` artifacts; affected plugins bumped.

## 0.1.0 — 2026-08-18

Initial release: 9 plugins, 51 skills. Fixed silently-broken YAML frontmatter
in 4 skills (unquoted colon in description).
