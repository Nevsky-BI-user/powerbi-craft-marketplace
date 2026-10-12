---
name: deck-review
description: Use when checking a presentation before it is shown or sent, or tearing down someone else's deck into lessons - a measurable rubric, every slide rendered to PNG, one lint over HTML decks and PDFs exported from pptx or Slides (words, minimum font, title drift, safe margins, contrast, luminance flips, duplicate bullets, page numbers, off-canvas and raster text, print page count), a render-look-fix loop until zero critical findings, an evidenced report ranked критично/бажано/косметика with a could-not-verify list. Do NOT trigger for writing a deck (deck-storyline, slide-design, html-deck), .pptx XML validation (pptx), Power BI page review (pbi-report-review), claim audits of report pages (claim-auditor). Triggers - 'перевір презентацію', 'рев'ю слайдів', 'чи готова презентація', 'лінт слайдів', 'проаналізуй презентацію', 'розбери чужу презентацію', 'review deck', 'deck teardown'.
---

# Deck review: measure, look, fix, repeat

## Overview

A deck is judged against external criteria, never self-graded. The criteria are `references/rubric.md`
(77 checks, each with an ID, thresholds per mode, severity, lesson and fix owner; the numbers are mirrored in
`scripts/thresholds.json`) and the deck's `deck-plan.json`. Scripts render every slide, measure it and judge
it; the reviewer then looks at every PNG, confirms or refutes each automatic finding on the pixels and
answers the visual-only questions of rubric §V. Fixes go to the skill named in each finding:
`deck-storyline` (N, T), `slide-design` (G, Y, C, V, D, S, K), `html-deck` (H), this skill (T11, P).
The discipline (inventory first, external criteria, evidence per finding, severity, an explicit
could-not-verify list) is the one of `pbi-report-review`, applied to slides. Evidence: on a 52-slide vendor
platform deck most failures were machine-detectable (L73), and the text layer misreported raster and
gradient text (L74).

## When to Use

- Before a talk, before the PDF is sent, after a restyle, an import or a build by another agent.
- When asked to analyse someone else's deck and turn it into lessons (teardown mode).
- Symptoms: "looks fine" with no numbers; only the changed slide re-checked; text-layer statistics taken
  at face value; a PDF that nobody opened page by page; a reading deck about to be shown in a hall.

**NOT for:** writing or restyling slides (`deck-storyline`, `slide-design`, `html-deck` own the fixes);
.pptx XML validation and soffice mechanics (`pptx`); Power BI page review (`pbi-report-review`,
`report-design-reviewer`); the truth of report claims (`claim-auditor`, `data-storytelling`); adversarial
number checks (`verify-skeptic`); generic PDF extraction (`pdf`).

## Two modes

| Mode | Input | Output | Done when |
|---|---|---|---|
| Audit (own deck, pre-show) | HTML deck or PDF, plus `deck-plan.json` | `findings.json` and `.md`, report, loop log | judge exits 0 and every бажано is fixed, refuted or accepted (P2) |
| Teardown (someone else's deck) | PDF (a .pptx converted first) | lessons ledger, inventory, inferred plan, copy and avoid list | ledger spot-checked on pixels (`references/teardown.md`) |

## Pre-flight (nothing is judged before this exists)

1. **Render source per engine.** HTML: as is. A .pptx: convert to PDF with the `pptx` skill's soffice
   wrapper. A claude.ai Slides artifact: its PDF export. A PDF: as given.
2. **Plan.** `deck-plan.json` from `deck-storyline`. None: write an inferred plan (`inferred: true`,
   `deck-storyline` references/deck-plan.md §10) before judging; without archetypes N2, N5 and D2 are
   skipped and dividers are not exempted. No declared mode: the deck is judged as talk and N1 says so.
   A reading deck that will be presented is judged twice into separate folders: `--mode reading --out
   out/reading`, then `--mode talk --out out/talk`; the report carries both.
3. **Inventory.** Count slides, archetype per slide, main flow vs appendix, dividers, demos. A skim is
   not an inventory.
4. **Tools.** Node 18+ with Playwright and a full Chromium (`CHROME_PATH`; the headless shell has no PDF
   viewer), Python 3 (stdlib only), LibreOffice only for PDF text runs (`XPDFIMPORT`). A missing tool turns
   its checks into «Не вдалося перевірити» and the report says so; it never silently passes them.
5. **Privacy and disk.** Work in a scratch folder outside any repo. Outputs carry no names. xpdfimport
   streams about 200 MB of stdout for a 52-page deck; PNGs need tens of MB.

## The loop

Script paths below are relative to this skill's folder; run them from a scratch folder outside any
repository, which holds the deck, the plan and `out/`. Every script runs headless
(no window opens), prints usage and exits 2 on bad arguments, and writes only into its output folder.

**Step 1. Render and measure every slide.**

```bash
# HTML deck (html-deck engine exposes window.deck)
node scripts/html_deck_lint.mjs deck.html out --fonts both
# HTML deck without window.deck: name the slides, the active class and the next key
node scripts/html_deck_lint.mjs deck.html out --slide-selector 'section.slide' --active-class on --next-key ArrowRight
# PDF (exported from pptx, Slides or a browser)
node scripts/pdf_pages.mjs deck.pdf out/png
python3 scripts/pdf_text_runs.py deck.pdf out/runs
```

**Step 2. Pixels.** Contact sheets every 30 slides, luminance class per slide, near-duplicates, and for
PDFs the background colour under every text run:

```bash
node scripts/pixels.mjs out/png out                              # HTML
node scripts/pixels.mjs out/png out --runs out/runs/pages.json   # PDF
```

**Step 3. Judge.**

```bash
python3 scripts/deck_lint.py --plan deck-plan.json --metrics out/metrics.json --pixels out/pixels.json --out out
python3 scripts/deck_lint.py --plan deck-plan.json --runs out/runs/pages.json --pixels out/pixels.json --out out
```

Exit 0: no finding at or above `--fail-on critical|should|cosmetic` (критично, бажано, косметика; default
`critical` for the judge, `should` for `--plan-only` and `--tokens`); 1: at least one; 2: bad input, plan
schema violation or missing thresholds. `findings.md` is the human table; `findings.json`
(`deck-findings/1`) carries per finding the check, slide, measured value, threshold, lesson, owner,
`font_mode` (native, metric or both) and `confirm: true` for A+V checks.

**Step 4. Look.** Open the contact sheet first (families, luminance flips, near-duplicates, the map
highlight at thumbnail size), then every PNG at full size, in batches of at most 12. Answer the rubric §V
question of every check in `visual_todo`, starting with the pointers in `visual_hints` (T11 look-alike
pairs, T1 suspects); mark each `confirm: true` finding confirmed or false positive with what is seen (L74).

**Step 5. Fresh eyes.** Dispatch in parallel the `deck-reviewer` agent (this plugin: visual V checks,
read-only) with the PNG folder, contact sheets, `findings.json` and the plan, and `claim-auditor`
(`report-storytelling` plugin) with the slide titles read alone. Their reports go into the review report.
Without an agent tool (a subagent run) do both passes yourself and record each under «Не вдалося
перевірити»: the deck-reviewer procedure (contact sheet, every PNG, §V questions, confirmations) as
«deck-reviewer недоступний, §V перевірено вручну, свіжого погляду немає»; the claim-auditor Title test on
the titles read alone (a finite verb and a number or named entity; `groups.title_exempt` skipped) as
«claim-auditor недоступний, T1 перевірено вручну».

**Step 6. Fix in the owning skill** with the smallest change. Never fix D1 by shrinking type below the
Y1 floor; move content to the appendix or split the slide instead.

**Step 7. Re-render all slides**, not only the fixed one, rerun steps 1-3 and append one line to the loop
log: iteration, критично, бажано, what changed.

**Stop rule.** Stop when the judge exits 0 and every бажано is fixed, refuted or accepted (P2); after P2
`iterations_max` iterations report what remains, each item with its owner. One closure rule: a finding
refuted on the PNGs in step 4 closes as «хибне спрацювання» with what was seen, no user acceptance; only
a finding that is real and kept on purpose needs the user's acceptance in writing. The html-deck engine's
known noise (`scripts/fixtures/expected.json` `clean_noise`) follows it: G5 glyph-box padding, G7 terminal
header border and K2 family split on the PDF path are refuted on the PNGs; Y1 on the n/N and progress
labels and D2 terminal title are real and accepted once as a group. Never fix them against `html-deck`.

## Severity

From rubric §1, never re-decided per finding:

- **критично**: the audience cannot read it, it is wrong, it leaks or it breaks in the PDF (below a floor,
  failing contrast, overflow or clipping, off-canvas or hidden title, raster-only words, unscrubbed
  identity, untitled slide, visible duplicate, viewport or print failure, a leftover `data-todo`);
  **бажано**: structure and consistency; **косметика**: polish.

A severity cell in the rubric may name the condition that changes it (for example D1 is критично only
above `words_hard` on a talk slide); `deck_lint.py` applies those conditions.

## Scripts

| Script | Input | Output | Needs | Feeds |
|---|---|---|---|---|
| `html_deck_lint.mjs` | HTML deck | `metrics.json`, `png/`, `png-metric/`, `print.pdf` | Node, Playwright, Chromium | every html check |
| `pdf_pages.mjs` | PDF | `png/slide-NN.png`, `manifest.json` | full Chromium (PDF viewer) | P1, pixels |
| `pdf_text_runs.py` | PDF | `pages.json` (`deck-runs/1`), `pages.txt`, `stats.txt` | LibreOffice xpdfimport | every pdf check |
| `pixels.mjs` | PNG folder (+ runs) | `pixels.json`, `contact-N.png` | Node, Playwright, Chromium | C1 on PDF, C4, G5, K2, T11 |
| `deck_lint.py` | metrics or runs, pixels, plan | `findings.json`, `findings.md` | Python 3 | the verdict |
| `deck_lint.py --plan-only`, `--tokens` | `deck-plan.json`; `tokens.json` or `deck.html` | summary (`plan-findings.*`, `token-findings.*` with `--out`) | Python 3 | `deck-storyline`, `slide-design` gates |
| `thresholds.json` | | | | every number, mirrored from rubric.md |
| `selftest.py` | `fixtures/`: seeded and clean twin decks, plans, `expected.json` | pass or fail per section | as the scripts above | trust in the kit |

After any change to rubric.md, thresholds.json, a script or the `html-deck` template, run
`python3 scripts/selftest.py` until it exits 0: rubric and enum sync, the plan and token gates, 100% recall
of the planted defects on both paths and 0 критично on the clean twin (`--sync-only` needs no browser).

Environment: `CHROME_PATH` (full Chromium or Chrome; unset uses Playwright's channel `chromium`),
`PLAYWRIGHT_MODULE` (Playwright package path when normal resolution fails), `PDF_WAIT_MS`,
`XPDFIMPORT`. No script holds a machine path. `python3` here means Python 3: `python` or `py -3` on
Windows. Units (design px, pt, the baseline-from-bottom y of PDF runs): rubric §1.

## Report

Fill `references/report-template.md`: inventory, render facts, lint summary, findings with slide, check,
measured vs threshold, lesson and owner, the ranked list, «Не вдалося перевірити», the loop log and a
one-sentence verdict. Unverified items are marked «неперевірено» and never mixed with assertions.

## Teardown in brief

Fixed order (L79): contact sheets, then per-slide runs and PNGs, then word-weighted statistics, then
computed contrast for the top colour pairs, then pixel spot checks of the most surprising claims. Read
word counts as distributions (silent and dense slides), never as averages. Privacy: no presenter, event,
customer or person names in any output, at most 6 words quoted verbatim, a sensitivity-labelled source
never leaves scratch. Pipeline, blind spots and the ledger format: `references/teardown.md`.

## Proofreading (L20)

Read every slot, including table cells, footnotes and cloned siblings. T11 automates part of it: two items
sharing their first 5 words on one slide (критично) or across neighbours (бажано; a zoom and a declared
pair are exempt), a repeated title (бажано), double spaces, footnote markers without a note, slides alike
on the dHash and in their text (look-alikes with different text go to `visual_hints`). Spelling, clone
leftovers and a row whose content does not match its label stay visual: read siblings on the contact sheet.

## Common Mistakes

| Mistake | Why bad | Fix |
|---|---|---|
| Reviewing the text layer only | 16-29 pt reported where the visible content is 7-9 pt raster (L74) | render every slide; confirm on PNGs |
| Averages instead of distributions | median 39 words hid 11 silent and 7 dense slides (L79) | read silent and dense lists in the judge info |
| Re-checking only the fixed slide | fixes move titles, numbering and overflow elsewhere | re-render all slides every iteration |
| "Looks fine" without a measurement | unevidenced verdicts miss what the lint finds (L75) | every line cites slide, check and number |
| Self-authored criteria | trivially "done" | rubric.md and the plan only |
| #000000 counts at face value | gradient text arrives as #000000 (L78) | treat as "black or gradient"; C3 could-not-verify |
| Runs counted as words, raw xpdfimport coordinates | splits cut words (L78); drawChar is in user space | `pdf_text_runs.py`; teardown §5-6 |
| Fixing density by shrinking text | trades D1 for Y1 | split, cut or move to the appendix |
| Skipping the print check | copy buttons, clipped code and dark tokens ship in the PDF (H4) | keep `print.pdf` in every HTML run |

## Verify before done

The last loop iteration shows 0 критично -> every PNG is listed as viewed -> the `deck-reviewer` and
`claim-auditor` reports are attached, or their step 5 fallback lines are recorded -> «Не вдалося
перевірити» is present and non-empty when a tool, an agent or a font was missing -> every fix is routed
to its owner skill -> in a repo, `git diff` matches the scope.
