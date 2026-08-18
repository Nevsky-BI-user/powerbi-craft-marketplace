# pbip-deploy — reference

Depth for [SKILL.md](SKILL.md). The approval gate, blast-radius statement, post-deploy
verification and common mistakes stay there; this file holds the phase mechanics.

## §1. Phase 0 — Pre-flight

- [ ] `git status` clean. A dirty tree is the user's uncommitted work — WIP-commit it as-is, never
      `stash`/`reset`/`checkout --`.
- [ ] Branch is not the integration branch.
- [ ] Report format known: single `report.json` (PBIR-Legacy) vs `definition/pages/**` (enhanced).
- [ ] Connection mode known: `byPath` (thick, model deploys with it) vs `byConnection` (thin —
      **the model is remote and your local TMDL edits are invisible until deployed**).

`byConnection` is the single biggest source of "I fixed it and nothing changed". Check it first.

## §2. Phase 1 — Reference integrity: report vs live model

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

## §3. Phase 2 — Local verification, before the gate

- [ ] Schema validation passes (a CLI validator is **not** a substitute for opening in Desktop).
- [ ] Layout/contrast audit reads the **produced files**, not the generator's call sites. A
      generator that accepts an option and silently drops it produces JSON with nothing wrong in it.
- [ ] **Determinism:** run the generator twice; the output must be byte-identical. Random ids
      (`randomBytes`, `uuid4()`) per run rewrite the whole project and make "only X changed"
      unprovable. Derive ids from stable inputs.
- [ ] For a model change: inventory dependants before touching a shared object (grep every
      `.tmdl` for the name; cross-check every report reference). Dependants outside the task's
      scope → stop and ask.

## §4. Phase 4 — Deploy mechanics

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

## §5. Rollback

Keep the previous definition retrievable before overwriting (`GET .../getDefinition` to a file,
or rely on the commit that matches what is live). A rollback is the same `updateDefinition` with
the saved payload. Know this path *before* deploying, not after.

## §6. Environment traps

- Non-interactive shells: use `curl.exe` with `-D` for headers. Avoid `Invoke-WebRequest` — it can
  fail *after* sending the request, so a retry hits `409 AlreadyExists`.
- `ConvertTo-Json` serialises a one-element array as a scalar; normalise on read.
- A console showing UTF-8 as mojibake is an output artefact, not a corrupt file — verify content
  through a file read, not the terminal.
- Scripts containing non-ASCII must be saved UTF-8 **with BOM** for Windows PowerShell 5.1.
