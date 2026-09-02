# Contributing

powerbi-craft is a Claude Code skills marketplace (MIT). Skills live in
`plugins/<plugin>/skills/<skill>/SKILL.md`; each plugin carries a manifest in
`plugins/<plugin>/.claude-plugin/plugin.json`, and `.claude-plugin/marketplace.json`
is the source of truth for the plugin list and versions.

## Proposing a skill or a change

1. Fork the repository and create a branch from `main`.
2. Add or edit the skill under `plugins/<plugin>/skills/<skill>/`. Keep `SKILL.md`
   at roughly 100 lines; depth goes into `reference.md` (progressive disclosure).
   Ukrainian and English trigger phrases are both welcome.
3. Bump the plugin version, add a CHANGELOG entry, run the validator (all below).
4. Open a pull request against `main`. CI (workflow `validate`, Ubuntu + Windows)
   runs `scripts/validate_repo.py` on every PR; the catalog site is rebuilt from
   skill frontmatters automatically after merge.

## What CI rejects

`scripts/validate_repo.py` is the same script CI runs. A PR fails when:

- **Frontmatter.** `SKILL.md` has no YAML frontmatter, the YAML does not parse,
  or `name` / `description` is missing. The classic breakage is an unquoted
  `: ` inside `description` — quote the value. The Claude Code runtime drops a
  broken frontmatter silently, which is why this is a hard error.
- **`name` ≠ folder.** Frontmatter `name` must equal the skill folder name
  (for agents in `plugins/<plugin>/agents/<name>.md`: the file stem).
- **Description length.** `description` must be ≤ 1024 characters — the skill
  router truncates longer ones. The validator enforces this for agent files;
  skill descriptions are held to the same limit in review.
- **Version drift.** `version` in `plugins/<plugin>/.claude-plugin/plugin.json`
  must equal that plugin's `version` in `.claude-plugin/marketplace.json`.
  Bump **both** together.
- **Manifest ↔ disk.** Every folder in `plugins/` is listed in
  `marketplace.json`, and every listed plugin exists on disk.
- **Sanitization.** No local filesystem paths, no local user names, no links to
  private folders, no internal report names or workflow ids anywhere under
  `plugins/**` (`.md`, `.json`, `.yaml`, `.yml`, `.txt`, `.sh`, `.py`).
  Measurements stay, attributed generically ("a production report").
- **Line endings.** `*.sh` must be LF; `.gitattributes` enforces
  `*.sh text eol=lf`. CRLF breaks the hooks on a Windows checkout.

Checked in review rather than by CI:

- Every `description` declares an explicit boundary — `Do NOT trigger for X
  (owner)` — so skills do not compete for the same prompt.
- CHANGELOG headings are `## X.Y.Z — YYYY-MM-DD` with an **em dash** (`—`).
  `scripts/build_catalog.py` reads them with `^##\s+([\d.]+)\s+—\s+(\S+)`; a
  hyphen makes the entry vanish from the site silently. End the entry with a
  `- Версії: <plugin> <version>, …` line naming the plugins you bumped.
- `site/src/catalog.json` is derived — CI regenerates it. Do not hand-edit.

## Run the checks locally

```bash
pip install pyyaml
python3 scripts/validate_repo.py   # prints "OK: … скілів, … плагінів" on success
git grep -i "<term>"               # hunt leftovers case-insensitively, always
```

On Windows use `python` (or the `py` launcher). Editing a `SKILL.md` inside
Claude Code also triggers `.claude/hooks/check_frontmatter.py` (PostToolUse
hook in `.claude/settings.json`), which rejects a broken frontmatter on the
spot. Maintainer rituals are wrapped as slash commands in `.claude/commands/`:
`/add-skill` (register an external skill for the site) and `/release`
(publish updated skills, bump versions, CHANGELOG, validator).

## What never goes into this repository

- **Brand assets.** Company logos live locally only; `pbi-corporate-theme`
  deliberately ships without them.
- **Project specifics.** Names of production reports, internal task codes,
  links to documents that are not part of the package. Keep the measurements,
  anonymize the source.
- **Local paths and user names** — checked by the validator and by the site
  snapshot sanitizer.
- **Skills of private projects** — not published to the site.
- **A CHANGELOG line that quotes what it removed.** Naming a deleted string
  puts it straight back into the site bundle.

## Licence

MIT (see `LICENSE`). By contributing you agree that your contribution is
licensed under the same terms.
