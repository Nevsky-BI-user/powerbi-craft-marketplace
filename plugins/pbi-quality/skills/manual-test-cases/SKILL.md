---
name: manual-test-cases
description: Use when the user wants test cases in human language for a project, report, or feature - a document a human tester can execute without reading code, describing what can be tested, how, and what result counts as pass. Cases derive from the real artifact (files, model, report), never from imagination. Do NOT trigger for design/visual QA of a Power BI page (use pbi-report-review), post-deploy data verification (use pbip-deploy), or automated unit tests (use test-driven-development). Defaults - user's chat language, P1 smoke set <= 10 cases, in PBIP repos the doc goes to .claude/TEST_CASES.md (git-ignored, no PII). Triggers - 'test cases', 'what can be tested', 'UAT checklist', 'manual QA', 'acceptance tests', 'тест-кейси', 'тесткейси', 'що можна тестувати', 'чеклист тестування', 'кейси для тестувальника', 'мануальне тестування', 'приймальні тести'.
---

# Writing human-language test cases

## Overview

A test case earns its place only if a human can execute it without you and can *disagree*
with the result. A vague case ("filter works correctly") always passes and catches nothing.

**Core principle:** every case has a falsifiable expected result anchored **outside** the
thing under test — a source query, a reconciliation page, a second visual, a hand-computed
number. If the only way to know the expected result is to look at the visual being tested,
it is not a test case.

## When to Use

- "Напиши тест-кейси", "що можна тестувати", UAT/acceptance checklist for a report,
  app or feature; before a release; after a large change.
- NOT for: design QA of a page (`pbi-report-review`), post-deploy data verification
  (`pbip-deploy`), automated tests (`test-driven-development`).

## Pre-flight (mandatory)

1. **Inventory the artifact from files** — pages/features, interactive elements (slicers,
   bookmarks, drill-through, buttons, parameters), refresh settings, hidden pages.
2. **Find built-in QA first.** Reports often carry their own reconciliation pages
   (hidden "Автотести"/"Reconciliation" pages, difference counters). These become the
   backbone of the smoke set — never re-invent what the report already checks.
3. **Read what you write about.** A case asserting measure math requires reading that
   measure's expression. Not read → the case is marked `[assumption — formula not read]`
   or dropped. Never state "sum of components = total" from the measure *name*.
4. **PII and secrets scan.** Real names, salaries, contract numbers, server/DB names never
   go into a committable doc. In PBIP repos the doc lives at `.claude/TEST_CASES.md`
   (git-ignored); people are referenced by role, not name.

## Case format

| ID | Pri | Prerequisites | Steps | Expected result (with anchor) | Source | Status |
|---|---|---|---|---|---|---|

- **Expected result** names its anchor: "total = result of `SELECT SUM(...)` on the source
  view", "counter on the reconciliation page shows 0", "equals the value on page X for the
  same filter". Restating the step ("data is filtered by region") is a tautology, not a result.
- **Prerequisites** name the concrete data pick that hits the boundary: the culture with zero
  rows, the forage culture that the formula treats specially, the period straddling a season —
  not "select any value".
- **Source** — the file/fact the case derives from, so a stale case is traceable.
- Written for a human without code access: display names, page names, click paths — no
  internal identifiers in Steps.

## Document structure

1. **P1 smoke set** — ≤10 cases run after every refresh/deploy (built-in reconciliation
   counters first).
2. **Per-area sections** mapped to the actual pages/features found in pre-flight.
3. **Coverage map** — every visible page/feature has ≥1 case **or** an explicit
   "not covered: <reason>" row. Silent gaps read as "covered".
4. **When to run** — change-type triggers: model change → which sections, report-only
   change → which, deploy → smoke.
5. **Needs live access** — what files cannot prove (performance, RLS in Service,
   mobile rendering): short, derived from real signals in the project (e.g. 597 slicers,
   `PT1M` page refresh), never padded with generic browser-matrix advice.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Tautological expected result ("works correctly") | Anchor to a source-of-truth number or second view |
| No priorities — tester doesn't know where to start | P1 smoke ≤10 + when-to-run triggers |
| Real names / servers in a committable doc | Roles instead of names; `.claude/TEST_CASES.md` git-ignored |
| Math cases about unread formulas | Read the expression or mark `[assumption]` |
| Generic filler sections (browsers, perf boilerplate) | Derive from real project signals or omit |
| No coverage map — gaps look like coverage | Page-by-page matrix with explicit "not covered" rows |
| Re-inventing checks the report already has | Built-in reconciliation pages become the smoke set |

## Verify before done

- [ ] Every expected result is falsifiable and names its anchor.
- [ ] Coverage map lists every visible page/feature — covered or explicitly not.
- [ ] Smoke set ≤10, ordered by risk; when-to-run triggers present.
- [ ] PII grep done (names, salaries, servers); doc location honors repo rules.
- [ ] `[assumption]` marks present wherever the underlying code was not read.
- [ ] Every quoted measure/column/table name is confirmed by a separate exact-match search
      (grep) — "I read that line range" is not enough; adjacent names get confused.
- [ ] Document language = user's language.
