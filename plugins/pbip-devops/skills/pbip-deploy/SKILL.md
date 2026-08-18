---
name: pbip-deploy
description: Use when publishing a PBIP project (semantic model and/or report) to a Fabric or Power BI workspace, or when deciding whether a change is ready to publish - covers the approval gate, report-to-model reference integrity, deterministic-output checks, REST deploy mechanics, and post-deploy verification that looks at data rather than job status. Do NOT trigger for local report edits (powerbi-visuals, pbir-format), TMDL authoring (tmdl), or workspace administration. Triggers - 'deploy', 'publish', 'залити', 'опублікувати', 'updateDefinition', 'deploy-fabric', 'викласти звіт', 'публікація моделі'.
---

# Deploying a PBIP project

## Overview

Publishing overwrites a shared object that other reports and people already use. A local edit
shows up in `git diff` and reverts with one command; a publish does not. Treat the two as
different actions with different prices.

**Core principle:** a deploy is only "done" when the *data* proves it, never when the job status does.

## The approval gate — non-negotiable

Without an explicit yes from the user in chat, do **not**:

- run any deploy script in any mode;
- `POST .../items/<id>/updateDefinition`, `POST .../semanticModels`, `POST .../reports`;
- run or schedule notebooks, write to a Lakehouse, `MERGE`/`overwrite` a table;
- change workspace settings, permissions, or capacity.

Reads are free and require no approval: `GET items`, `executeQueries`, `_delta_log`, job status.
**Verifying measures against the live model is a read** — do it early and often.

Approval is per-change and per-session. "Yes" to one deploy is not standing permission.

If a change is ready and approval has not been given, that is **not "done"**. Say explicitly:
what stays unpublished, what symptom the user sees until it ships, and the exact command to ship it.

## Phase 0 — Pre-flight

- [ ] `git status` clean. A dirty tree is the user's uncommitted work — WIP-commit it as-is, never
      `stash`/`reset`/`checkout --`.
- [ ] Branch is not the integration branch.
- [ ] Report format known: single `report.json` (PBIR-Legacy) vs `definition/pages/**` (enhanced).
- [ ] Connection mode known: `byPath` (thick, model deploys with it) vs `byConnection` (thin —
      **the model is remote and your local TMDL edits are invisible until deployed**).

`byConnection` is the single biggest source of "I fixed it and nothing changed". Check it first.

## Phase 1 — Reference integrity: report vs live model

The report is a set of promises about the model. Verify every one against the **live** model
before deploying anything, and again after.

Extract every `Measure.Property` and every `Column` (`Entity` + `Property`) from the report
(`visual.json` in enhanced, `config` blobs in Legacy — parse JSON, do not regex nested braces),
then probe each one:

```
EVALUATE ROW("v", [<measure>])
EVALUATE TOPN(1, VALUES('<table>'[<column>]))
```

A failure means the object does not exist under that exact name. This catches renames that no
validator sees, because a report that points at a missing field is still schema-valid.

**Probe existence AND value.** A measure that resolves but returns BLANK looks identical on the
canvas to one that is missing. `EVALUATE ROW(...)` over all measures at once gives both.

To list what the model actually holds when `INFO.MEASURES()` is unavailable:
`EVALUATE TOPN(1,'<table>')` returns every column name in its result keys.

| Symptom | Do not conclude | Check instead |
|---|---|---|
| Visual empty, axis present | "the measure is missing" | Probe the measure; it usually exists and returns data |
| Whole page empty right after switching | "the page is broken" | Direct Lake over a network renders containers first and streams data after — re-look a few seconds later |
| One slicer shows nothing | "no data for that field" | Probe the column; near-miss names (`OverTime` vs `IsOverTime`) fail silently on every page |

## Phase 2 — Local verification, before the gate

- [ ] Schema validation passes (a CLI validator is **not** a substitute for opening in Desktop).
- [ ] Layout/contrast audit reads the **produced files**, not the generator's call sites. A
      generator that accepts an option and silently drops it produces JSON with nothing wrong in it.
- [ ] **Determinism:** run the generator twice; the output must be byte-identical. Random ids
      (`randomBytes`, `uuid4()`) per run rewrite the whole project and make "only X changed"
      unprovable. Derive ids from stable inputs.
- [ ] For a model change: inventory dependants before touching a shared object (grep every
      `.tmdl` for the name; cross-check every report reference). Dependants outside the task's
      scope → stop and ask.

## Phase 3 — State the blast radius, then wait

Before publishing, tell the user in plain terms:

1. which object is being overwritten (name + id + workspace);
2. what changes in it;
3. who else consumes it;
4. what happens if it is wrong, and how to roll back.

Then wait for a yes. Do not bundle the question with other work.

## Phase 4 — Deploy mechanics

Token, then REST. Interactive CLI logins fail in a non-interactive shell.

```bash
az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv
```

| Call | Body rules |
|---|---|
| Create item | `type` is **required** alongside `displayName` and `definition` |
| Update item | body is **only** `{"definition": {...}}` — no `displayName`, no `type` |
| `updateDefinition?updateMetadata=true` | requires a `.platform` part in the payload; drop the flag when only content changes |

Deploy the **model before the report** when the report depends on new objects, otherwise the
report lands pointing at fields that do not exist yet.

## Phase 5 — Post-deploy verification

`status: Completed` means "the cells did not throw". It does not mean data arrived.

- [ ] Re-run the Phase 1 probe — every reference still resolves.
- [ ] Check values, not just success: row counts, a known aggregate, min/max of the key.
- [ ] For incremental loads, run twice: the first run creates, the second exercises the `MERGE`
      branch that would otherwise fail unobserved the next day. Assert zero duplicates by key.
- [ ] Report-side rendering cannot be verified headlessly. Say so, and name page → tab → visual
      for the user to check.

## Rollback

Keep the previous definition retrievable before overwriting (`GET .../getDefinition` to a file,
or rely on the commit that matches what is live). A rollback is the same `updateDefinition` with
the saved payload. Know this path *before* deploying, not after.

## Common mistakes

| Mistake | Consequence |
|---|---|
| Editing local TMDL for a `byConnection` report and expecting a change | Nothing moves; the model is remote |
| Treating job status as data verification | Silent zero-row loads |
| Deploying report before model | Report references fields that do not exist yet |
| Skipping the reference probe | A renamed column kills a control on every page, silently |
| Random ids in a generator | Every deploy is a full rewrite; regressions become invisible |
| Publishing without stating the blast radius | Overwrites a shared object other reports depend on |
| Calling it done with the deploy unapproved | The user believes a fix shipped that did not |

## Environment traps

- Non-interactive shells: use `curl.exe` with `-D` for headers. Avoid `Invoke-WebRequest` — it can
  fail *after* sending the request, so a retry hits `409 AlreadyExists`.
- `ConvertTo-Json` serialises a one-element array as a scalar; normalise on read.
- A console showing UTF-8 as mojibake is an output artefact, not a corrupt file — verify content
  through a file read, not the terminal.
- Scripts containing non-ASCII must be saved UTF-8 **with BOM** for Windows PowerShell 5.1.

## Related

- Report edits: `powerbi-visuals`, `pbip:pbir-format`. Model edits: `tmdl`, `dax-measures`.
- Pre-merge diff review: `pbip-pr-reviewer`. Design sign-off: `pbi-report-review`.
