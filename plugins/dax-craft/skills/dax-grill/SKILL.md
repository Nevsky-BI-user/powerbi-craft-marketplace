---
name: dax-grill
description: >
  Interrogate the requirements of a DAX measure BEFORE writing it — a structured
  interview that pins down grain, filter context, relationships, and expected
  totals, so the measure is right on the first try. Use when the user explicitly
  asks to be grilled or to check the setup: "прожар мене", "прожар постановку",
  "grill me", "перевір вимоги до міри", "перевір постановку", "чому може не
  зійтися total", "задай питання перед мірою", or when they ask for a complex
  measure while grain/totals/model context are visibly unstated and ambiguous.
  Output is a confirmed problem statement handed off to dax-measures — this
  skill writes NO DAX itself. Do NOT trigger for: a clearly specified measure
  request (go straight to dax-measures); slow measures (dax-optimization);
  drawn visuals (dax-svg, deneb-vegalite).
---

# DAX Grill

An interview primitive borrowed from Matt Pocock's "grilling" skills: relentlessly
stress-test the problem statement before any code exists, because a wrong measure
that runs is more expensive than five questions that take a minute.

## When to Use / NOT for

- The user asks to be grilled, or asks for a non-trivial measure (semi-additive,
  mixed grain, "% від того що вибрано", cross-table logic) with the model context
  unstated.
- NOT for: writing the measure itself → `dax-measures`; tuning a slow one →
  `dax-optimization`; visuals → `dax-svg` / `deneb-vegalite`.

## Rules of the grill

1. **Ask, don't assume.** Every answer below either comes from the user, from the
   model files if they are available in the session (TMDL/PBIP), or is written
   down as an explicit assumption the user must confirm.
2. **Short rounds.** Ask at most 3–4 questions at a time, highest-risk first.
   Skip questions the context already answers — a grill that re-asks the known
   reads as a form, not an interview.
3. **Finish with a testable statement**, then hand off to `dax-measures`.

## The seven questions (highest-risk first)

| # | Question | Why it kills measures |
|---|---|---|
| 1 | **Grain**: one row of the fact table = what? At what grain will the visual show the measure? | Mixed grain is the #1 source of double counting |
| 2 | **Totals**: what must the row total / grand total show — sum of rows, recomputation, last value? | Additive assumption breaks semi-additive facts (balances, headcount) |
| 3 | **Filter context**: which slicers/pages/RLS will act on it? Should any be ignored (ALL) or preserved (KEEPFILTERS)? | "% of total" means five different measures depending on the answer |
| 4 | **Relationship path**: which tables connect fact and dimension, any inactive or bidirectional links, USERELATIONSHIP needed? | A measure through the wrong path silently filters nothing |
| 5 | **Blanks and zeros**: is no-data BLANK or 0? Do zero-rows exist in the fact? | `+ 0` vs BLANK changes both visuals and performance |
| 6 | **Time**: calendar marked as date table? Fiscal or calendar year? What is "current period"? | Time intelligence silently misbehaves on unmarked calendars |
| 7 | **Acceptance example**: one concrete slice with the expected number ("за березень по Регіону А має бути 1 234"). | Without a checkable number, "готово" is an opinion |

## Output format

After the rounds, emit a **Problem Statement** block:

```
Міра: <назва>
Грануляція факту: … · Грануляція візуала: …
Totals: … · Фільтри: поважає …, ігнорує …
Шлях зв'язків: … · Blank-поведінка: …
Приклад приймання: <зріз> → <число>
Припущення (підтверджені): …
```

Then: "Передаю в `dax-measures`" — and the measure is written there, against this
statement, with the acceptance example checked mentally before presenting.

## Common Mistakes

| Mistake | Do this instead |
|---|---|
| Grilling a trivial request ("сума продажів") | Answer directly via dax-measures — the grill is for ambiguity, not ceremony |
| Asking all seven at once | 3–4 per round, highest-risk first, skip the already-known |
| Accepting "як зазвичай" as an answer | Pin the assumption in writing and mark it as unconfirmed |
| Writing DAX inside the grill | Hand off; one skill, one job |
