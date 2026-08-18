---
name: claude-md-bootstrap
description: Use when a new or existing repository of any stack needs a CLAUDE.md so Claude Code works there by the project's rules - right after git init, when scaffolding a project, or when the current CLAUDE.md is a stale codebase summary that answers no "how do we work here" questions. Recon-first - detects stack, commands and conventions from files, asks only what files cannot answer, writes a durable rules-file with verified commands, never overwrites silently. Do NOT trigger for Power BI PBIP repositories (use pbip-bootstrap - it ships the full PBIP CLAUDE.md with gates), for editing code, or for one-off codebase Q&A. Defaults - rules-first file <= ~60 lines, docs in the user's chat language. Triggers - 'create CLAUDE.md', 'init claude md', 'set up rules for Claude Code', 'bootstrap agent rules', 'створи CLAUDE.md', 'клод мд', 'файл клод мд', 'розгорни правила для Claude', 'налаштуй проєкт під Claude Code', 'новий проєкт - додай CLAUDE.md'.
---

# Bootstrapping CLAUDE.md for a new project

## Overview

CLAUDE.md is loaded into every session of every agent that works in the repo. Its job is to
hold what an agent cannot re-derive from files: team decisions, working rules, and verified
commands. Code structure the agent re-reads for free each session; a wrong rule or a stale
fact it will obey forever.

**Core principle:** durable rules + verified commands, not a codebase snapshot.

## When to Use

- Right after `git init` / scaffolding a project of any stack.
- Repo exists but has no CLAUDE.md, or its CLAUDE.md only narrates code structure.
- NOT for PBIP repos — `pbip-bootstrap` ships a PBIP-specific CLAUDE.md with gates G0–G4.

## Pre-flight (mandatory)

Recon before any questions — never ask what files already show:

```bash
ls -a && git branch --show-current && git remote -v && git log --oneline -5
```

- Stack and commands: `package.json` scripts, `pyproject.toml`, `Makefile`, `*.csproj`,
  `go.mod`, `Cargo.toml`, `pom.xml`, CI configs under `.github/workflows/`.
- Existing agent files: `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `copilot-instructions.md`.
  If present — diff and merge with the user's consent, never overwrite silently.
- `*.pbip` found → stop, route to `pbip-bootstrap`.

## Ask only what files cannot answer

One `AskUserQuestion` round (≤4 questions), skipping anything recon already answered:

1. **Integration branch + policy** — commit straight to it, or branch-per-task with PR?
2. **Tracker and commit format** — Jira `ABC-123` / Azure Boards `TASK NNNNN:` /
   GitHub `#123` / conventional commits / none.
3. **Language** — for docs, commits and chat. Never decide this silently.
4. **Boundaries and gates** — what must the agent never touch, and what counts as
   "verified" before reporting done (tests? build? review?).

Missing answer → honest `[fill in]`, never a plausible guess.

## Write the file

Order: what it is (1 line) → commands → conventions → boundaries → definition of done.

**Every command is run before it is written.** A command that was not run is marked
`# not verified`. The baseline failure this skill exists to stop: shipping setup/test
commands that were never executed, plus a "current state" section ("no README yet, single
init commit") that rots after the first push.

**The month test:** every line must still be true in a month. Transient facts (branch has
one commit, venv not created, file X is still empty) fail it — they belong in the chat
reply, not in CLAUDE.md. The compact form of the same defect is equally forbidden: a
transient fact tucked into a parenthesis or a trailing clause of a durable line
(`Integration branch: main (currently a single commit, no remote)`). If a fact fails the
month test, it is not written in any form — not even as an aside.

Example skeleton (adapt, do not paste):

```markdown
# CLAUDE.md
ETL CLI on Python 3.11 (typer + pandas + SQLAlchemy). Domain: <one line>.

## Commands
- setup: python -m venv .venv && .venv\Scripts\pip install -e ".[dev]"
- test: pytest          # single: pytest tests/test_x.py::test_y
- lint: ruff check . && mypy src

## Conventions
- Integration branch: main; work in task/<id>-<slug>, PR before merge.
- Commits: "TASK NNNNN:" prefix, Ukrainian, body states what was verified.
- Docs and chat: Ukrainian; code identifiers English.

## Boundaries
- Never touch: deploy/ configs, .env*.
- Secrets never in the repo; connections via env vars.

## Definition of done
- pytest and ruff pass locally; no direct commits to main.
```

## Quick Reference

| Goes in | Stays out |
|---|---|
| Verified build/test/run commands | Commands never executed (or mark `# not verified`) |
| Branch, commit, language conventions | Code-structure narration (agent reads code itself) |
| Never-touch zones, secrets policy | Transient state (fails the month test) |
| Definition of done / gates | Generic advice ("write clean code") |
| Non-obvious facts: ports, locale, domain terms | Aspirational sections for code that does not exist |

## Common Mistakes

| Mistake | Fix |
|---|---|
| Codebase snapshot instead of rules | Rules first; delete any paragraph the agent can re-derive from files |
| "Current state" facts inside CLAUDE.md | Month test; report status in chat instead |
| Untested commands | Run each one; mark exceptions `# not verified` |
| Deciding language/conventions silently | The question round covers them; unanswered → `[fill in]` |
| Overwriting existing CLAUDE.md / AGENTS.md | Show diff, offer replace / merge / keep |
| Asking what files already show | Recon first; skip answered questions |
| Transient fact hidden in a parenthesis / aside | Same month test — drop the aside, keep only the durable part |

## Verify before done

- [ ] Every command in the file was executed in this session, or carries `# not verified`.
- [ ] `grep -c "\[fill in\]" CLAUDE.md` — count reported to the user, with what is missing and why.
- [ ] `grep -niE "наразі|на момент|станом на|currently|as of|not yet" CLAUDE.md` — zero
      matches, or each match moved to the chat reply.
- [ ] Month test passes for every line.
- [ ] No silent overwrite; merge decisions were the user's.
- [ ] File ≤ ~60 lines; if longer — move detail to `docs/` and link it.
