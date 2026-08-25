---
name: dax-regression-tests
description: Use when the user wants automated regression tests for DAX measures of a semantic model - a suite that proves key measures still compute correctly after model changes, runnable against Power BI Desktop's local instance or a Fabric/Power BI workspace. Covers test taxonomy (invariants over golden values), frozen-slice golden discipline, diff-driven test selection, and honest generated-vs-executed reporting. Do NOT trigger for authoring measures (use dax-measures), human-language QA checklists (use manual-test-cases), one-off post-deploy verification (use pbip-deploy), or DAX performance tuning (use dax-optimization). Defaults - tests/dax/*.dax + baseline/golden_values.json committed, results git-ignored. Triggers - 'DAX regression tests', 'measure regression', 'golden values', 'регресійні тести мір', 'регресія DAX', 'тести для мір', 'перевірити що міри не поламались', 'автотести моделі'.
---

# DAX measure regression tests

## Overview

A regression suite is only useful if a failure means "the model broke", not "the data
refreshed". The single biggest design mistake is golden values captured on totals that
drift with every scheduled refresh — the suite then cries wolf weekly and the team learns
to re-baseline blindly, which is the exact failure the suite exists to prevent.

**Core principle:** invariants first, golden values last — and golden values only on
frozen slices that data refreshes cannot move.

## When to Use

- "Зроби регресійні тести для мір", after-change verification gates, CI for a semantic model.
- NOT for: measure authoring (`dax-measures`), manual QA (`manual-test-cases`),
  deploy-time checks (`pbip-deploy`), performance (`dax-optimization`).

## Pre-flight (mandatory)

1. **Pick measures from artifacts, not intuition:** the model's own KPI lists (dispatcher
   tables like `t_Indicators`, calculation groups, report-page bindings), built-in
   reconciliation measures («Автотести»), and — first of all — **measures inside the
   current change radius**: `git diff` on `*_Measures.tmdl` plus everything that references
   the changed objects (grep by name). A suite that ignores what just changed tests the
   wrong thing.
2. **Detect execution paths available NOW** (and say which are absent):
   - Desktop local AS — `connect-pbid` (needs Desktop open with the project);
   - Fabric/Power BI workspace — `fab api "datasets/<id>/executeQueries"` per
     `fabric-cli-powerbi` §4 (needs `fab` auth);
   - always available: offline structural checks from TMDL (measure exists, references
     resolve, DAX text hash).
3. **No secrets in committed artifacts:** server/database names and connection strings
   stay out of test files — including prose mentions in README/manifests, not just
   structured connection fields; results directory is git-ignored.

## Test taxonomy — in priority order

| Tier | What | Golden needed | Survives refresh |
|---|---|---|---|
| 1. Structural | measure exists, references resolve, DAX hash changed knowingly | no | yes |
| 2. Invariants | sum of parts = total; dispatcher (SWITCH) = direct measure; twin measures agree in same context; built-in reconciliation counters = 0 | no | yes |
| 3. Guard behavior | impossible filter → BLANK (never-blank rule §11); no errors on empty context | no | yes |
| 4. Golden values | exact numbers on **frozen slices only** | yes | yes — by design |

Most of the suite must live in tiers 1–3. If more than ~5 tests need golden values,
the selection is wrong.

## Golden-value discipline

- **Frozen slice only:** pin the filter context to data that can no longer change —
  a closed year/season, an archived period: `CALCULATE([EBITDA], 'dim_Date'[Year] = 2024)`.
  Grand totals and current-period values are FORBIDDEN as golden anchors — every refresh
  moves them and every run turns red for a non-reason.
- **Fact table has no calendar relationship at all?** That does not license a grand total.
  Find the model's nearest "closed unit" analog — an archived/finalized dimension member
  (a final planning model, a flag like `isActualArchive`) — document why it is immutable,
  and confirm the concrete member with the model owner instead of guessing.
- Capture (`-CaptureBaseline`) only against a model whose numbers a human has already
  verified by eye. The capture date and who approved it go into the JSON.
- Tolerance explicit per test (floats: relative 1e-6 or a business tolerance); BLANK is a
  value, not a missing result — `expected: null` must mean "expect BLANK", never "not set"
  (use a separate `status: NOT_CAPTURED`).
- **Re-baseline protocol:** only after an intentional, separately verified change — and
  never as the immediate response to a red run. A red golden test is a finding first.

## Repo placement

```
tests/dax/*.dax              committed — readable in DAX Query View / DAX Studio / TE
baseline/golden_values.json  committed — expectations separate from queries
results/                     git-ignored — run artifacts
scripts/                     runner (ADOMD.NET / executeQueries wrapper)
README.md                    committed — how to run, re-baseline protocol, and the
                             generated/executed/blocked summary of the latest run
```

## Honest reporting

Every delivery states three numbers separately: tests **generated**, tests **executed**
(against which endpoint), tests **impossible to execute now and why** (Desktop closed,
no `fab` auth, VPN). "Suite created" with zero executed runs is a draft, not a done —
say so explicitly and give the exact command that runs it once a connection exists.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Golden values on grand totals / current period | Frozen slices only (closed year); refresh must not move them |
| Re-baselining right after a red run | Red golden = finding; re-capture only after verified intentional change |
| Suite ignores the current diff | Change-radius measures get tests first (`git diff` + reference grep) |
| Handpicked "important" measures | KPI lists from the model's own artifacts (dispatcher tables, calc groups) |
| Everything needs golden values | Tiers 1–3 (structure, invariants, guards) carry the suite |
| "Tests created" without a single execution | Report generated / executed / blocked separately, with the unblock command |
| `expected: null` means both BLANK and not-captured | BLANK is a value; `NOT_CAPTURED` is a status field |
| Server names in committed test files | Endpoints resolved at run time; results git-ignored |

## Verify before done

- [ ] Change-radius measures covered; selection sources named (which artifact gave the KPI list).
- [ ] Golden tests ≤ ~5, every one on a frozen slice, with tolerance and capture metadata.
- [ ] Invariant and guard tiers present and runnable without golden values.
- [ ] At least the structural tier actually executed in this session, with PASS/FAIL counts.
- [ ] Generated / executed / blocked reported as three separate numbers.
- [ ] No secrets in committed files; `results/` git-ignored.
