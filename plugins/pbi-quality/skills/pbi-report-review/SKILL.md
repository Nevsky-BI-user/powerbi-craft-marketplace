---
name: pbi-report-review
description: Use when auditing a Power BI report page's design before reporting a redesign as done, or verifying a bookmark fix holds page-wide. Symptoms - self-graded acceptance criteria, a narrow diff claimed as a "deep" redesign, a bookmark fix touching only one sibling. Do NOT trigger for diff/code review (pbip-pr-reviewer) or usage/perf audits (reports:review-report). Triggers - 'дизайн рев'ю', 'перевір дизайн', 'аудит сторінки', 'акцептанс', 'симетрія букмарок', 'це дійсно готово?'.
---

# Power BI Report Design Review

## Overview

Independent, evidence-gated design QA — never a self-grade. Incident: an agent restyled 7
cards, self-closed 9 invented criteria (`reference.md` §3). Routes every finding to the checks
below. Covers PBIP (PBIR-Legacy/enhanced) and TMDL.

## When to Use

- Before reporting a design task ("deep"/"глибоко") as done.
- After any bookmark/visibility fix, to confirm the whole page, not just the fixed tab.
- Not for: diffs (pbip-pr-reviewer), usage/perf (reports:review-report), single-element fixes
  (below), a11y checklists (web-design-guidelines).

## Pre-flight (mandatory — nothing is judged before this exists)

1. Detect format; name the **reference** page — if unstated, say so.
2. **Inventory first.** Count every `visualContainer` by type, target AND reference
   (`reference.md` §1) — a skim is not an inventory.
3. Read the real `width`/`height`, theme, `ThemeDataColor` mapping.
4. List every sibling bookmark in the nav group, if any.

## Quick Reference — category → owning skill

|Category|Score against|Route fix to|
|---|---|---|
|Layout/grid|8-px snap, shared row `y`/`height`|`pbi-page-layout`|
|Typography|one size/tier, Segoe UI, one emphasis|`pbi-typography`|
|Color/theme|`ThemeDataColor` not hex; one navy; contrast ≥4.5:1|`pbi-design-system`|
|Chart choice|native visual fits the question|`pbi-visualization-strategy`|
|Narrative/claim|title states a finding not a subject; every number carries a base; one "so what" per page|`data-storytelling`|
|Tables/matrix|`tableEx`/`pivotTable` (not legacy); zebra|`pbi-tables` (tableEx), `pbi-matrix` (pivotTable)|
|Nav/slicers/states|default/hover/selected/disabled distinct, no `press`|`pbi-navigation-tabs` (tabs), `pbi-slicers-filter-panel` (slicers)|
|Tooltips/drillthrough|context header, canvas size|`pbi-tooltips`, `pbi-drillthrough`|
|Bookmarks/visibility|symmetry check below|`powerbi-bookmarks`|
|Bindings|`queryRef` resolves to a real measure|model file|
|A11y|`tabOrder`, alt text, hit ≥24px|`pbi-design-system`|

Score each category with per-visual evidence, not impression — tokens/thresholds are defined
in `pbi-design-system` (e.g. 8-px grid §3, contrast ≥4.5:1 §8 rule 11), never restated with
different values.

## Bookmark symmetry (mandatory whenever bookmarks are touched)

Compare siblings as a SET, not one at a time: `isHidden` fixed alone while a peer lacks
`suppressData` replays that peer's filter on every click (`reference.md` §3, finding B1).

|Metric|Must match across ALL sibling bookmarks|
|---|---|
|`vcg`/`vc` id-sets (touched groups/containers)|same count, same ids|
|`tvn` — `options.targetVisualNames` length|same count|
|`options.suppressData`|identical boolean (mixed = bug)|

Any mismatch is a bug, even outside scope (script: `reference.md` §2).

## Evidence & acceptance discipline

- Criteria come from the task/user/`ACCEPTANCE.md` — never self-authored and self-closed.
- Every "done" line cites the artifact: command + literal output; "looks fine" isn't evidence.
- If "deep"/"глибоко" was asked but the diff is a small fraction of the inventory, say so.
- "JSON parses" is necessary, never sufficient (see Common Mistakes below).

## Common Mistakes

|Mistake|Why bad|Fix|
|---|---|---|
|No counted inventory|Self-graded "deep" on 7 cards|Count every `visualContainer`|
|One bookmark fixed only|Peer replays its filter|Diff all siblings (above)|
|Self-authored, self-closed criteria|Trivially "done"|Criteria external; cite evidence|
|"JSON parses" only check|Invisible/unreadable content passes|Resolve fills vs. real background|
|Only pixels scored, never the claim|Page ships with a dimension-name title and baseless numbers|Score Narrative/claim (`data-storytelling`)|

## Verify before done

Inventory counted → categories scored with evidence → bookmark symmetry computed, zero
mismatches → scale stated for "deep" → `git diff` matches scope.
