---
name: pbip-deploy
description: Use when publishing a PBIP project (semantic model and/or report, PBIR enhanced or Legacy) to a Fabric or Power BI workspace, or when deciding whether a change is ready to publish - covers the approval gate, report-to-model reference integrity, deterministic-output checks, REST deploy mechanics incl. report-only PBIR parts and the RegisteredResources caveat, and post-deploy verification that looks at data (and exports every page after a navigation change) rather than job status. Do NOT trigger for local report edits (powerbi-visuals; external powerbi-report-authoring), TMDL authoring (external tmdl skill), Fabric CLI day-to-day operations (fabric-cli-powerbi), or workspace administration. Triggers - 'deploy', 'publish', 'залити', 'опублікувати', 'updateDefinition', 'deploy-fabric', 'викласти звіт', 'публікація моделі', 'опублікуй дашборд'.
---

# Deploying a PBIP project

## Overview

Publishing overwrites a shared object that other reports and people already use. A local edit
shows up in `git diff` and reverts with one command; a publish does not. Treat the two as
different actions with different prices.

**Core principle:** a deploy is only "done" when the *data* proves it, never when the job status does.

## When to Use

- Publishing a PBIP semantic model or report, or deciding whether a change is ready to publish.
- NOT for — related skills instead. Report edits: `powerbi-visuals` (Legacy), the external
  `powerbi-report-authoring` (Microsoft skills-for-fabric, PBIR). Model edits: external `tmdl`
  skill, `dax-measures`. Pre-merge diff review: `pbip-pr-reviewer`. Design sign-off:
  `pbi-report-review`.

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

## Workflow — Quick Reference

| Phase | Core action | Details |
|---|---|---|
| 0 Pre-flight | `git status` clean; not on integration branch; report format Legacy vs enhanced; `byPath` vs `byConnection` — check mode first | reference.md §1 |
| 1 Reference integrity | Probe every report measure/column against the **live** model — existence AND value | reference.md §2 |
| 2 Local verification | Schema check; audit produced files; generator determinism; dependant inventory | reference.md §3 |
| 3 Blast radius | State it plainly, then wait for a yes | below |
| 4 Deploy | Token then REST; model before report; report-only PBIR parts + `byConnection` + RegisteredResources caveat | reference.md §4, §4.2 |
| 5 Post-deploy | Re-probe references; check data, not job status; after a nav/bookmark change export every page (PNG smoke test) | below, reference.md §4.3 |

Rollback path (know it *before* deploying) → reference.md §5.
Environment traps (curl vs `Invoke-WebRequest`, JSON arrays, UTF-8 BOM) → reference.md §6.

## Phase 3 — State the blast radius, then wait

Before publishing, tell the user in plain terms:

1. which object is being overwritten (name + id + workspace);
2. what changes in it;
3. who else consumes it;
4. what happens if it is wrong, and how to roll back.

Then wait for a yes. Do not bundle the question with other work.

## Phase 5 — Post-deploy verification

`status: Completed` means "the cells did not throw". It does not mean data arrived.

- [ ] Re-run the Phase 1 probe — every reference still resolves.
- [ ] Check values, not just success: row counts, a known aggregate, min/max of the key.
- [ ] For incremental loads, run twice: the first run creates, the second exercises the `MERGE`
      branch that would otherwise fail unobserved the next day. Assert zero duplicates by key.
- [ ] Report-side rendering cannot be verified headlessly — but every page can be **exported**:
      after a navigation, bookmark or button change run the PNG smoke test (reference.md §4.3):
      one `ExportTo` per visible page, every file > 0 bytes. Then name page → tab → visual for
      the user to check by eye.
- [ ] After a report-only PBIR deploy: `getDefinition` and diff `resourcePackages` — a new icon
      or theme that vanished must be added through Desktop (preview limitation, §4.2).

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
