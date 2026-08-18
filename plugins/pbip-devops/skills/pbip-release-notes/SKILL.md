---
name: pbip-release-notes
description: Use when the user wants release notes or a changelog for a Power BI report aimed at its business users - a human-language summary of what changed, built from the PBIP repo's git history and real diffs, never from commit messages alone. Do NOT trigger for code-level diff review (use pbip-pr-reviewer), deploy mechanics (use pbip-deploy), or test cases (use manual-test-cases). Defaults - user's chat language, business audience, net-diff between two anchored states, coverage statement up front. Triggers - 'release notes', 'changelog', 'що змінилось у звіті', 'реліз ноутс', 'список змін для користувачів', 'опиши зміни звіту', 'нотатки релізу', 'що нового у звіті'.
---

# Release notes for report users

## Overview

Release notes are read by people who never open TMDL. Every line must answer: what will
I *see* differently, and where. A changelog of commits is not release notes.

**Core principle:** one **net-diff between two anchored states** is the source of truth —
never the sum of per-commit diffs, and never commit messages alone.

## When to Use

- "Напиши release notes / що змінилось у звіті" for business users; before/after a publish.
- NOT for: PR review (`pbip-pr-reviewer`), the deploy itself (`pbip-deploy`),
  test cases (`manual-test-cases`).

## Pre-flight (mandatory)

1. **Anchor both ends.** Baseline = last delivered state: previous release notes' SHA, a
   tag, the last deploy — and before falling back to a calendar date, check for a
   `prod`/`main`/`release`-like branch (`git branch -a`): its tip is a far better proxy
   for "what users last received" than any date on a dev branch. Ambiguous → ask the
   user. **Both anchors resolve to concrete SHAs** — a date without a SHA is not an
   anchor. Name both SHAs and dates in the document header.
2. **Staleness check:** `git status -sb` / `git fetch --dry-run` evidence — if the local
   clone is behind origin, the notes MUST open with a coverage statement ("covers X..Y;
   the portal may already have newer changes"). Never present a stale window as complete.
3. **Merge-artifact trap:** with parallel branches, per-commit diffs show the same change
   as "added" several times. The document is built from `git diff <baseline>..<head>` —
   net state-to-state — with `git show` of single commits only as drill-down evidence.

## What goes in — and how it is proven

- Item = **user-visible effect**: a new filter, a renamed page, a changed number's
  meaning, a redesigned navigation. Each item names **where to look**: page → element.
- Every item traceable to a concrete diff hunk (report.json / *.tmdl / theme). A change
  whose visible effect cannot be confirmed from the diff is either dropped or explicitly
  marked "заявлено в коміті, у файлах не підтверджено" — never narrated on faith.
- **Renames get a table** (old name → new name) — users search by the name they remember.
- Group by business theme, not chronology; bugfixes in one compact block.
- Language: the report users' language; zero DAX/TMDL/JSON vocabulary **in the main
  text**. The exclusions footer is an audit trail and may name technical objects.

## What stays out (list the exclusions at the end, one line each)

Internal renames with no visible effect; data-source/parameter plumbing; refresh
artifacts (`PBI_ResultType` noise); pure Power Query refactors; commits whose content
could not be confirmed. An honest "виключено: …" footer beats silent omission.

## Document skeleton

```
# <Report name> — що нового (<date>)
Період: <d1>–<d2> · стан: <baseline SHA> → <head SHA> [· увага: локальна копія
відстає від порталу]

## <Business theme 1>   ← what changed + where to look
## <Business theme 2>
## Виправлення
## Перейменування (таблиця: було → стало)
## Виключено з нотаток (чому)
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Summing per-commit diffs across merged branches | One net-diff baseline..head; commits only as drill-down |
| Trusting commit messages | Every item confirmed in the diff or marked unconfirmed |
| Developer vocabulary (measure, TMDL, relationship) | User-visible effect + page name |
| No coverage statement on a stale clone | Header names the window and the staleness |
| Chronological commit list | Business-theme grouping; renames table |
| Silent exclusions | "Виключено" footer with one-line reasons |
| Scope chosen silently | Anchors named in the header; ambiguous baseline → ask |

## Verify before done

- [ ] Header names both anchors (SHA + date) and the staleness status.
- [ ] Every item has a where-to-look and a confirming diff behind it.
- [ ] Renames table present when any rename happened.
- [ ] Exclusions footer present; nothing dropped silently.
- [ ] Zero developer vocabulary — read it as the report's least technical user.
