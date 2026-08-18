# Changelog

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
