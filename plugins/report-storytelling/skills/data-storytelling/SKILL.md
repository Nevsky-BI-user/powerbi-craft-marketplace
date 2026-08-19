---
name: data-storytelling
description: Use when deciding or auditing what a report or dashboard page ASSERTS - headline wording (finding vs subject), the comparison base behind every number, annotation, page order, audience, the 'so what'. Power BI and web dashboards. Do NOT trigger for chart choice (pbi-visualization-strategy), fonts/number formats (pbi-typography), colour roles (pbi-color-accessibility), grid math (pbi-page-layout), design QA scoring (pbi-report-review). Triggers - 'сторітелінг', 'наратив звіту', 'висновок сторінки', 'що каже ця сторінка', 'заголовок не про те', 'число без бази', 'so what', 'data storytelling', 'action title'.
---

# Data Storytelling — the claim, not the pixels

## Overview

A page that names its subject has said nothing; a page that names its finding has said one
thing. This skill owns the **claim** — headline wording, the comparison base, annotation, page
order, audience, disclosure — and nothing that has a pixel value. Shape → `pbi-visualization-strategy`;
type/format → `pbi-typography`; colour roles → `pbi-color-accessibility`; grid → `pbi-page-layout`;
card anatomy → `pbi-kpi-cards`; scoring a finished page → `pbi-report-review`.

Wording is a design decision, not a caption: titles take the most fixations and drive recall
(Borkin et al. 2016), and recall follows the title even when it contradicts the chart (Kong,
Liu & Karahalios 2018/2019).

## When to Use

- Writing or auditing a page/visual headline, subtitle, callout, insight line, alt text.
- Deciding what a page asserts, in what order pages argue, what the reader must DO next.
- Symptoms: the title is a dimension name; a number with no base; a page nobody can name a
  decision for; a caveat living in the smallest text on the page.

**NOT for:** which chart (`pbi-visualization-strategy`), fonts/number formats (`pbi-typography`),
palettes/contrast (`pbi-color-accessibility`), layout math (`pbi-page-layout`), card properties
(`pbi-kpi-cards`), machine-written prose (`pbi-ai-visuals`), design QA (`pbi-report-review`).

## Pre-flight (before any wording)

1. Name the **audience tier** and the **decision**: «керівник Групи / чи втручатись у ГРМУ»,
   never "stakeholders". No nameable decision → the page has no reason to exist.
2. Write the **report claim** and one **page claim** per page, as sentences, before touching
   a visual. A page whose message cannot be written is a page that should not be built.
3. Name the **comparison base** the model actually supports (план · попередній місяць · PY ·
   медіана Групи · дедлайн). If only one base exists, that limitation goes on the page.
4. **Recompute** the number you are about to assert. An unrecomputable headline is a guess.

## Quick Reference — layer → obligation → checkable test

| Layer | Obligation | Test an agent can run |
|---|---|---|
| Page claim | entity + verb + magnitude + base + period, one sentence | reverse the data → the sentence must become FALSE |
| Title | states the finding, not the subject | contains a finite verb AND a number or named entity |
| Subtitle | scope: measure, unit, period, base | names all four; carries no evaluation (IBCS splits message from title) |
| Every number | at least one comparison + direction | zero tiles showing a value and nothing else |
| Ranking | sorted by the quantity plotted | sort key ≠ display order, ≠ alphabetical |
| Focus | headline + ONE highlight + annotation — all three or none | exactly one element is emphasised AND the annotation names it (how emphasis is encoded → `pbi-color-accessibility`) |
| Annotation | asserts something, ≤2 per visual | text contains a verb; "how to read" alone does not count |
| Default state | opens on the metric/period the claim is about | default ≠ first row of the catalogue order |
| Disclosure | distortions flagged AT the number | caveat is not the smallest text on the page |
| Page order | one change per step (period OR measure OR entity OR grain) | diff page N→N+1 = exactly one changed thing |
| Close | a named action and an owner, or «дій не потрібно» | the last block on the page is not another chart |
| Number framing | base named in words · ratio variance in п.п. · explicit sign, «н/д» over a negative base · counts carry their denominator · truncated axis stated in words, never a break marker | full IBCS notation ref. §3 |

Frameworks, IBCS notation, annotation catalogue, uncertainty, alt text, Power BI mechanics,
worked critique, and the myth registry → **reference.md**.

## Claim grammar

```
<entity> <verb> <magnitude> <vs base> <period> [→ <consequence or action>]
ok:  Липень: 5 з 8 підприємств у межах плану; ГРМУ −14% до плану, третій місяць поспіль
bad: «Аналітика Групи» (subject) · «Виконання плану» (topic) · «94%» (value with no base)
arc: що → де → чому → що робити; each page is a child of the report claim (ref. §5)
```

Zelazny's gate: underline the comparison word in the claim (частка / більше ніж / зросло /
розподіл / залежить від) and hand *that word* to `pbi-visualization-strategy` — the word picks
the shape, not the gallery. No comparison word → the visual is decoration.

## Common Mistakes

| Mistake | Why bad | Correct |
|---|---|---|
| Title names the dimension | Reader must re-derive the "so what" | Finding in the title, dimension in the subtitle |
| Bare KPI number | A value is not a finding | «94% · −3 п.п. до червня» |
| Rows in catalogue order | A ranking that does not rank | Sort by the plotted quantity |
| Hint explains mechanics only | Teaches reading, not what happened | Mechanics + one finding sentence |
| Caveat in the smallest text | The distortion travels, the disclosure doesn't | Flag at the affected number |
| Highlight with no annotation | Colour without a claim reads as decoration | The focus triad ships whole (ref. §4) |
| Invented composite as the hero | «точність до плану» is not a business quantity | A real quantity, or define it inline |
| Causal verb over correlational evidence | "driven by" asserts a design you don't have | Hedge, or show the decomposition |
| "Tell a story" as acceptance criterion | Unfalsifiable — five incompatible meanings in the literature | Claim + evidence + ordering + how much the reader may re-cut |
| Tooltip/annotation repeats the visible label or value | Duplication asserts nothing — reader hovers and learns nothing («ніякої цінності») | Tooltip only adds what the page does NOT show (comparison, full truncated name, why-good/bad); else no tooltip |
| Same top-N shown twice side by side (chips above the very table) | Two encodings of one claim compete for attention | One encoding per claim per viewport; the second becomes navigation or dies |

## Verify before done

Claim recomputed from a named measure/query → every page title contains a verb → every number
carries a base → default state matches the claim → ranked visuals sorted by the plotted quantity
→ ratio claims re-checked one grain down (Simpson) → one action named → editorial ledger filled
(ref. §6) → `git diff` matches intent.

Whether a claim is TRUE cannot be verified from JSON or TSX. Cite the query and the value that
prove it, or mark it «неперевірено» — never both assert and hedge in the same sentence.
