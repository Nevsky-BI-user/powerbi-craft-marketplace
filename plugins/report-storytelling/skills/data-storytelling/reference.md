# Data Storytelling — Reference

Deep companion to `SKILL.md`. Practitioner frameworks (Knaflic, Duarte, Minto, Zelazny, IBCS)
are **conventions**; empirical claims below carry their study and effect size so a later editor
can tell the two apart. Folklore that was deliberately excluded is listed in **§12** — do not
reintroduce it.

---

## §1. From decision to claim — the pre-build sequence

Four artefacts, in order. Each is checkable; none requires a tool.

1. **Audience + decision**, one sentence: «керівник Групи вирішує, чи втручатись у ГРМУ цього
   місяця». If nobody can name the decision, the page is a statistic, not a report.
2. **SCQA** (Minto): *Situation* the reader already accepts → *Complication* that changed →
   *Question* it raises → *Answer*. Ship only the **Answer** as the page message; keep S and C
   to one line each; the Q must never appear as text — the page structure answers it.
3. **The claim** (Duarte's DataPOV): a point of view plus what is at stake. It must contain the
   quantified outcome and, where one exists, the action.
4. **Paper storyboard**: one post-it per page, its text = that page's future title. Approved
   before any visual is built. A post-it with no verb and no stake = a page with no reason.

Failure tests for a claim: it is a noun phrase; it names a metric instead of a judgement; it
stays true when the numbers are reversed; it cannot be recomputed from a named measure.

**Zelazny's gate** (Say It With Charts): underline the comparison word — частка / більше ніж /
зросло-впало / розподіл / залежить від — and map it to the five comparison types (component,
item, time series, frequency distribution, correlation). That word picks the shape; hand it to
`pbi-visualization-strategy`. No comparison word → the visual is decoration.

**MECE test on the supporting visuals** (Minto): no two visuals answer the same sub-question,
and no obvious sub-question of the page claim is unanswered. A page whose visuals answer
different questions is two pages.

---

## §2. Message vs title vs subtitle

IBCS splits them and so should you:

- **Message** — evaluative, a complete sentence, at the top of the page, same position on every
  page. IBCS SA 3.1: a message is a *detection* (checkable true/false), an *explanation* (why),
  or a *suggestion* (what to do).
- **Title** — identifies content, carries **no** evaluation. IBCS UN 2.2 three-line form:
  (1) reporting unit; (2) measure + unit; (3) period + scenario + variance. On a screen this
  usually collapses into one subtitle line; keep the four facts.
- **Subtitle** — only what differs between objects. Anything common lives in the page title.

**Why wording is a design decision, not a caption.** Borkin et al., *Beyond Memorability*
(TVCG 2016 / InfoVis 2015): titles attract the most fixations and are the most-recalled element;
message-bearing titles raise message recall. The risk side is symmetrical — Kong, Liu &
Karahalios (CHI 2018, CHI 2019): recall follows the **title** even when the title contradicts
the chart; ~72% of readers still rated a slanted title as neutral, and ~42% could not recall the
title afterwards. *(Attribution note: this is Kong/Liu/Karahalios — not Kong/Heer/Agrawala.)*

**Review ritual** (30 seconds, catches most defects): read the title alone → write the sentence
it implies. Cover the title, read the chart → write the sentence it implies. Any divergence is a
defect: either the title over-claims or the chart under-shows.

**Action-title conventions** (≤15 words, ≤2 lines, active voice, a number where one exists) are
consulting-house practice, not a standard — labelled here as convention. What *is* enforceable:
a finite verb, a number or named entity, and falsifiability.

---

## §3. Comparison base and variance notation (IBCS UNIFY, house subset)

**Scenario by fill, never by hue** (IBCS UN 3.2) — hue is reserved for good/bad:

| Scenario | Encoding |
|---|---|
| AC — факт | solid dark fill |
| PY — минулий рік / earlier measured period | solid light fill |
| PL/BU — план | outline only, no fill |
| FC — прогноз | outline + hatch in the AC colour |

When stacking or multi-line rendering makes fills unusable, move the notation to the category
axis. Scenario abbreviations are substitutable if documented; the **fills are not**.

**Variance grammar** (IBCS UN 4.1):

- `Δ` prefixes the subtrahend: `ΔPL` = AC−PL, `ΔPY` = AC−PY; `%` suffix for relative. Write it
  out (`AC-PL`, `(AC-PL)%`) whenever AC-vs-FC is ambiguous.
- Positive variances carry an explicit `+`. One negative format (`-123` **or** `(123)`) per report.
- Absolute-variance bars share **width and scale** with the base bars; relative variances are
  thin **pins**, not full-width bars.
- Variance of a percentage measure is in **percentage points**: 50% − 40% = **+10 в. п.**, never «+10%».
- Relative variance is «н/д» when the reference is negative (AC 30 vs PL −30 → −200% is meaningless).
- Data labels sit **outside** the element, on the side of the increase direction.
- Colour by good/bad business impact, not by driver identity; no colour available → red becomes
  dark grey, green light grey; for CVD readers green becomes blue-green.

**Scenario mapping (UA)**: факт=AC · план=PL · прогноз=FC · минулий рік=PY. When **plan is the only
base the model supports** — a common case in operational reporting — say so on the page and add a second
reference that costs nothing: rank within the Group, or the prior month. Adding a *new metric*
is the expensive answer; adding a *base* is the cheap one.

**Bridges** (IBCS EX 1.1): name which of the four it is — horizontal growth (stock over time),
horizontal variance (flow across periods/scenarios), vertical calculation (P&L scheme with
subtotals), vertical variance (structural drivers). Driver segments must sum **exactly** to the
endpoint variance (assert numerically); state the decomposition convention in a footnote, because
price/volume/mix results are order-dependent.

**Zero baseline and axis range.** Bars start at zero (IBCS CH 1.1). For any truncation, state the
range **in words** in the subtitle — a rectangular axis-break marker and a gradient bar bottom do
**not** reduce the exaggeration (Correll, Bertini & Franconeri, CHI 2020: F(2,60)=3.1, p=.05;
wavy/jagged glyphs were deliberately excluded from the stimuli, so zig-zags remain untested). The
bias survives when readers are also made to estimate values — perceived severity still tracked
truncation (F(1,20)=11, p=.003) while trend-estimation error did not differ (F(1,20)=0.002,
p=.96), and individual-value error was in fact *worse* at a 25% axis start (F(1,20)=8.3, p=.009).
There is **no** bar-vs-line difference (F(1,38)=0.5, p=.50) — the folk exemption for lines is
wrong. Pick the range from a pre-declared reference (contract target, tolerance band, prior-year
range) and lock it in the theme so a later editor cannot re-author the story by re-tuning it.

**Two y-axes** carry a measured cost, so never add one to imply a correlation the claim does not
assert. The same-unit/different-unit gate and `alignZeros` belong to `pbi-combo-charts`; when the
second axis exists only to fit two series in one frame, the claim-side answers are small multiples
or indexing both to 100 at a stated base. (Isenberg et al., TVCG 2011 is often miscited here: it
studied *dual-scale* charts — one measure at two resolutions — and concluded cut-out designs are
best and superimposed should be avoided. A blanket dual-axis ban is house convention, not a study.)

---

## §4. The focus triad and the annotation catalogue

**The evidence.** Ajani, Lee, Xiong, Knaflic, Kemper & Franconeri (TVCG 2022, N=24): focused
designs produced story-relevant conclusions **2.96×** more often than cluttered and **2.49×**
more than merely decluttered. Decluttering **alone** showed no significant recall gain (redraw
p=0.81, free-response p=0.67). Open coding of the free responses produced many distinct
conclusion categories per topic (Fig. 4), most irrelevant to the author's intended story.

So: **decluttering is hygiene, focus is the message.** The triad — headline + one highlight +
annotation — ships whole or not at all. A highlight with no annotation reads as decoration; an
annotation with no highlight makes the reader hunt.

| Pattern | Claim it makes | Power BI | Web/React |
|---|---|---|---|
| Reference / target line | "this is the bar" | Analytics pane constant/average/percentile line, data label on | SVG line + label |
| Band / period shading | "something changed here" | shape behind the plot | `<rect>` under the series |
| Callout + leader | "this point, because X" | chrome-off textbox + thin shape | absolutely-positioned label |
| Highlight-and-grey | "look here, not there" | one saturated series, rest neutral | same |
| Dynamic headline | the claim, filter-aware | expression-based title (fx), **string-returning model measure** | template literal from the same selector as the chart |

Rules: annotation contains a verb and a number; ≤2 per visual (house budget, not evidence);
annotations go **on** the chart — about half of the 45 professionally produced data stories in
Stolper et al. 2016 put textual annotation directly on the chart, and the paper calls it a common
technique; annotation parked in a side box forces a lookup. Link prose to marks by colour so no
legend round-trip is needed. Cross-visual brushing is an exploratory idiom (4 of 45 stories) and
does not belong on a narrative page.

Every comparative claim in a title needs its baseline **drawn**: "above average" needs the
average line; "below plan" needs the plan line.

---

## §5. Page arc, sequencing, audience tiers

**One change per step**, with the effect size. Hullman et al. (InfoVis 2013): cost-1 transitions
were strongly preferred over cost-2 (p<0.01), and cost-2 was no better than cost-3 — a cliff, not
a slope. With cost held constant the preference order was **Temporal > (Dimension | Measure) >
Granularity**, all p<0.01. Consequence: **drill-in goes last**, which inverts the folk reading of
"overview first, zoom and filter" as a *narrative* rule. Parallel internal structure across
sections improved memory for order (F(3,69)=5.59, p=0.002) but **not** comprehension — claim only
the memory benefit.

| Tier | Question the page owes | What changes | Rayfin example |
|---|---|---|---|
| Керівництво Групи | «чи ми в плані, і де ні» | one claim, one ranking, one action; no filters above the fold | сторінка Групи |
| Керівник підприємства | «чому, і який драйвер» | breakdown + drivers + the recorded reason | сторінка підприємства |
| Відповідальний за внесення | «що я маю зробити до 10-го» | deadline as the benchmark, per-metric worklist | Dashboard / збір |

Each tier must answer its own question **without** the tier below it (Eckerson).

**Story or dashboard?** Segel & Heer (2010): if consumption order matters, commit to one
structure — *martini glass* (locked author-driven opening, then free exploration), *interactive
slideshow* (author steps, exploration inside each), or *drill-down* (hub with reader-chosen
threads). A "next" affordance bolted onto an order-free dashboard is the smell. The martini glass
is the most *common* corpus structure, never a tested winner. If there is no ordered sequence and
no defined path, it is not a story — judge it on task time and accuracy instead (Kosara &
Mackinlay 2013).

**Entry model.** Do not force a group overview on a reader who arrived to see one entity (van Ham
& Perer, TVCG 2009 — "search, show context, expand on demand"). Test: can a named user reach
their own numbers in **0 clicks** after landing?

**Causality test**: if you cannot write "X explains Y" in one sentence and defend it, label the
page a reference page and drop the causal verb.

---

## §6. Honesty ledger (fill in before publish)

Five lines, covering the four editorial layers of Hullman & Diakopoulos, TVCG 2011 — data, visual
representation, annotation, interactivity — plus a provenance line of our own:

1. What rows/metrics were **omitted or aggregated**?
2. What **source, method, vintage and uncertainty** are disclosed?
3. What does the **scale choice** do to the impression?
4. What does the **title assert** beyond what the marks show?
5. What does the **default filter state** hide? (It is a rhetorical choice — disclose it.)

If a line is uncomfortable to write, that is the thing to fix, not the thing to omit.

Mechanical checks:

- **Mirage re-render** (McNutt, Kindlmann & Correll, CHI 2020): recompute the headline under at
  least two defensible alternatives — different grain, different window, with/without an outlier
  rule. If the headline flips, it is a mirage: soften it or show both.
- **Simpson check** (Bickel et al. 1975): any ratio KPI is recomputed one grain down before it is
  published as a finding. If the gap flips in most segments, the aggregate may not ship without
  the breakdown. Berkeley: 44% men vs 35% women admitted university-wide, yet women were admitted
  at higher rates in 4 of the 6 largest departments (A, B, D, F).
- **Denominator rule** (Gelman & Price 1999): never rank or colour units by a rate without n
  visible. Extreme rates cluster in small-n units by construction. Declare the minimum-n
  suppression threshold **once at report level** — choosing it per chart is a cherry-picking vector.
- **Polarity trap**: metrics where менше = краще must be excluded from — or flagged inside — any
  symmetric "accuracy" average, and the flag lives **at the number**, not in a footnote.
- **Invented composites**: an app-invented index may not be the largest number on a page without
  an inline definition and a trend.
- **Adversarial check**: ask a second person to argue the opposite claim from the same data. If
  they can without changing the data, the claim is under-supported.

---

## §7. Uncertainty and forecast wording

- **Label every interval** with what it is (95% CI / ±1 SE / P10–P90 / min–max). Even published
  researchers conflate CI and SE bars (Belia et al. 2005); SE bars are about half the length and
  look roughly twice as precise.
- **Never let overlap imply significance.** The eye-rules for independent means (≈half-arm
  overlap ≈ p≈.05) require independent groups and similar n — they are invalid for paired
  measures and for one entity over time (Cumming & Finch 2005).
- **Prefer countable frequency framing**: «20 зі 100 сценаріїв нижче X» rather than a shaded band
  or a bare ±. Quantile dotplots cut estimate variance ~1.15× versus density (Kay et al. 2016).
  For comparative questions, individual draws (HOPs) beat error bars and violin plots (Hullman,
  Resnick & Adar 2015).
- **A widening band is read as the quantity growing**, not as knowledge shrinking (Ruginski et al.
  2016). Prefer discrete scenario lines; if a band is used, print what it is **not**:
  «смуга — діапазон прогнозу, а не обсяг показника».
- **When intervals cannot be computed**, the cheap honest signals are mandatory: as-of timestamp,
  completeness («дані по 7 з 9 підприємств»), preliminary/restatable status. Hiding uncertainty
  does not remove it — the reader substitutes a worse private guess (Hullman 2020).

---

## §8. Text accessibility of the claim

This section owns only **what the words say**; contrast, palettes and colour-not-alone belong to
`pbi-color-accessibility`, reading/tab order to `pbi-page-layout`.

- **Alt-text formula** (Cesal): `{chart type} of {type of data} where {reason for including the
  chart}. {link to source}`. It must **not** restate the title — the screen reader already
  announced it.
- **Content level** (Lundgard & Satyanarayan, TVCG 2022): write L2 (statistics, relations: max,
  min, rank, difference) + L3 (perceptual trends: rises, plateaus, clusters, outliers). Keep L1
  (axis mechanics) minimal. Put L4 (why it happened) in a **separate, attributed** sentence —
  «Причина за поясненням підрозділу: …». 63% of blind participants rejected interpretation blended
  into description, while 41% of sighted readers preferred story-shaped text: separate, don't blend.
- **Two tiers** for complex charts (W3C): short alt that points to a long description; the long
  description carries scales, ranked values and the trend.
- **Never** put a load-bearing conclusion only in a tooltip or only behind an interaction —
  screen readers cannot read Power BI report tooltips, and hover is unreachable by keyboard.
- Provide a human-readable data table (Chartability marks its absence critical) and keep text at
  reading grade ≤9.
- **Headline in a textbox, not baked into the visual's image.** Text living inside a chart
  image (rendered title, source line) fails WCAG 1.4.5 and cannot be read or resized — the UK
  Government Analysis Function makes this a hard rule for published charts
  (https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-charts/).

---

## §9. Ukrainian wording and number conventions

- **Glossary discipline**: внесення · показник · **підприємство** (не «підрозділ») · вікно
  внесення · тотал/складові. Term drift between pages reads as *different metrics* to a business
  audience.
- **Граматика склеєних рядків — `ukrainian-ui-copy`.** Claim-рядок «−1,1 в. п. до червня»
  вимагає родового відмінка, «5 підприємств» — правильної форми множини; ні те, ні інше не
  ловиться компілятором. Цей скіл вирішує, ЩО стверджує рядок; той — чи він граматичний.
- **в. п. vs %** — every time (see §3).
- **One unit vocabulary per page.** «12,4 млн» in the title and «12.4M» on the axis read as two
  different numbers to a business audience. The format strings, decimal/date conventions and the
  **Default format string locale** pin are `pbi-typography`'s (`reference.md` §3) — this skill only
  requires that whatever is chosen there is used consistently across the page and in the claim.
- A translated metric **label** without a translated **definition** is the commonest source of
  silent metric disagreement in bilingual reporting.

### §9.1 Ukrainian lexicon of comparison bases (fixed words — do not paraphrase)

| Base / framing | Write | Not |
|---|---|---|
| plan vs actual | **план-факт**; «до плану», «відхилення від плану» | «план vs факт» |
| variance of two ratios | «−3 в. п. до плану» | «−3%» |
| year-to-date | **з початку року** | «YTD» (only where width forces it) |
| month-/quarter-to-date | з початку місяця / кварталу | |
| cumulative / running total | **наростаючим підсумком** | «кумулятивно» |
| year-over-year | до торішнього (р/р); name the base in words once per page | «YoY» alone |
| month-over-month | до попереднього місяця | «MoM» |
| growth rate vs increment | **темп зростання** = ratio to base (110%); **темп приросту** = ratio − 100% (+10%) | mixing the two — the claim silently doubles or halves |
| share | **частка** | «доля» |
| median of the group | медіана Групи (explain once: half below, half above) | |
| forecast | прогноз; «прогноз на кінець року» | «форкаст» |
| run-rate | у перерахунку на рік | «ран-рейт» |

Sources: НБУ Інфляційний звіт (в. п.), ABM Cloud «план-факт», «Показники рядів
динаміки» (buklib.net), НП(С)БО 1 line names; full EN→UA glossary —
`dashboard-copy/references/glossary-en-ua.md`; number/date formats —
`dashboard-copy/references/uk-formats.md`.

---

## §10. Power BI implementation map

- **Expression-based titles/subtitles**: Format → General → Title → fx. The measure must return a
  **STRING**; unsupported on R, Python and Key Influencers; lost when the visual is pinned to a
  dashboard; on a live semantic-model connection only **model** measures appear in the picker.
  Split the work: title = what happened, subtitle = so-what / as-of.
- **Text boxes with bound values** write real sentences (Format → General → Values → fx). Check:
  after every slicer change the sentence still reads as correct grammar *and* magnitude.
- **Analytics pane = the annotation layer.** Constant/average/percentile lines, error bars,
  forecast, anomalies. Forecast and anomaly detection are **line-chart only**; percentile line
  needs Import or a live connection to AS 2016+.
- **Tooltips**: a tooltip page is non-interactive (no slicers, no scrolling) and never
  load-bearing; canvas sizing is `pbi-tooltips`'. Turn on *Sentence format only* + *Sentence
  template* so the hover layer reads as a sentence. Help tooltips explain the visual, not the
  data point.
- **Bookmarks as chapters** (mechanics → `powerbi-bookmarks`; sibling symmetry → `pbi-report-review`):
  a chapter change must not reset the reader's filters, and hidden slicers keep filtering — that is
  how one page tells several chapters. Narrative constraint only: every chapter must still satisfy
  the page claim; if two chapters answer different questions, they are two pages.
- **Navigation**: name pages as chapters (the page navigator is the table of contents); one
  bookmark **group** per navigator — two navigators over overlapping settings show a misleading
  selected state; selected state is not preserved in exports.
- **Drill-through** as narrative depth: keep the Back button, hide the page, and ensure no visual
  goes BLANK under the drill-through filter.
- **Decomposition tree / Key influencers are hypothesis generators, not conclusions.** The tree's
  AI split is a greedy max/min search that recomputes on any cross-filter; Key Influencers is a
  Wald test at p=0.05 over a 10,000-row sample of observational data, needs ≥100 observations in
  the analysed state and ≥10 per comparison state, and reports continuous drivers **per standard
  deviation** — quote the sd or the number is meaningless.
- **Smart narrative** is a draft generator: convert to Custom mode and never let it make a causal
  or forward-looking claim (boundary shared with `pbi-ai-visuals`).
- **Narrative density is paid for in queueing**, not in DAX: 33 single cards = 35 queries / 2.7 s
  versus 3 consolidated visuals = 5 queries / 0.3 s (SQLBI); decorative chrome as 260 shapes took
  time-to-interactive from 3.7 s to 24.3 s versus 4.5 s as one background image (Chris Webb).
  The third layer of detail belongs in a tooltip or drill-through page, not a fourth chart.

---

## §11. Worked critique — Rayfin operational monitoring (verified 2026-08-13)

| # | Now | Claim-form rewrite |
|---|---|---|
| 1 | `AnalyticsOverviewPage.tsx:107` — h1 «Аналітика Групи» | «Липень: 5 з 8 підприємств у межах плану; ГРМУ −14% — найбільший розрив» (topic moves to the subtitle) |
| 2 | `:161` StatTile «Точність по Групі» = `94%` | «94% · −3 в. п. до червня» — a value is not a finding |
| 3 | `:166` StatTile «Показників із відхиленням >10%» = `37` | «37 із 214 (17%) · місяць тому 22» — count + denominator + direction |
| 4 | `:175` Section «Точність до плану по підприємствах», bars in catalogue order | sort by accuracy desc; title names the takeaway; worst rows separated |
| 5 | `:189` «Карта року» hint explains how to read a cell | mechanics **plus** the finding: «червона смуга лютий–березень — усі три ГРМУ одночасно» |
| 6 | `ExecSummarySection.tsx:34` — polarity caveat in 12 px faint text | marker at the affected numbers; exclude inverted-polarity metrics from the mean (`lib/analytics.ts:147-151` computes `100 − abs(факт/план − 100)`, symmetric by construction) |
| 7 | `DeviationsSection.tsx:20` — top-10 by `abs(pct)` | split under/over; surface `MetricValues.comment` in the row, explicit «причину не вказано» when empty |
| 8 | `TrendSection.tsx:47` — default metric = first in catalogue order | default = the metric the page claim is about; auto-caption «факт нижче плану 5 місяців поспіль» |

The single highest-leverage fix is #1: the page currently names its subject, so the reader does
all the interpretation. The second is #6 — an honest caveat that nobody reads is not a disclosure.

---

## §12. Contested — do NOT reintroduce

| Excluded claim | Why | What this skill says instead |
|---|---|---|
| "Stories are 22× more memorable than facts" | Untraceable to any published study | Cite mechanisms (annotation, highlight, grouping), never a ratio |
| "63% recall stories vs 5% statistics" | Traces to an informal classroom exercise, not a controlled study | Same — mechanism only |
| "Decluttering improves comprehension" | Ajani et al. 2022 measured **recall**, not comprehension, and found no significant declutter-only gain there (redraw p=0.81, free response p=0.67); decluttering did raise professionalism ratings | Decluttering is hygiene and a credibility signal; the 2.5–3× recall effect belongs to **focus** |
| Data-ink ratio as a numeric target; "chartjunk always harms" | Never validated as an objective; Bateman et al. 2010 and Haroz et al. 2015 undercut the blanket form | Every mark needs a job; ornament allowed only when it **encodes data** |
| "Bars must start at zero but lines may float" | No bar-vs-line difference in the bias (Correll et al. 2020, p=.50) | Zero baseline for bars; for any truncation, state the range in words |
| "A break marker makes truncation honest" | Empirically ineffective (F(2,60)=3.1, p=.05) | Name the range and the pre-declared reference |
| "7±2 KPIs/colours/visuals per page" | Miller measured absolute-judgment span; Cowan (2001) puts chunks at ~4; the transfer was never justified | No count rule — limit what the reader must **carry across** the page (~4 values) |
| "Dashboards must be readable in 3/5 seconds" | No primary source; folk extrapolation from a ~200 ms preattentive detection threshold | Write the real acceptance criterion: "8 of 10 target users state the status correctly in one 10 s exposure" |
| F-pattern / Z-pattern as *eye-tracking evidence* for a layout | NN/g's own 2017 correction: F-scanning is a symptom of unformatted text, not a template; Z-pattern has no primary study | Never argue a placement from a scan path. `pbi-page-layout` uses «F-pattern» as the NAME of its zone stack (title+hero → KPI strip → trends → detail) — that stack is hierarchy + reading direction and stays valid; only the scan-path justification is dropped |
| "78% of first fixations land on text" (Poynter) | Not verifiable in EyeTrack07 | Cite Borkin 2016 for titles |
| "People remember 80% of what they see" | Dale's Cone, debunked | Omitted |
| "Never use pie charts" | Cleveland & McGill rank angle 3rd, not last; IBCS itself carves out pies on maps | Category limits stay with `pbi-part-to-whole`; the hard error is parts that don't sum |
| "Progressive disclosure cuts load by 55% (NN/g)" | NN/g publishes no such number | Two disclosure levels max, each labelled with information scent |
| "IBCS has 98 rules" / "the whole IBCS is an ISO standard" | 98 is the rule count on Hichert's 2008 SUCCESS poster, not the standard's rule set; IBCS **notation** was ratified as ISO 24896:2026 (published 11 June 2026 alongside IBCS Standards 2.0) — the Composition part is **not** in the ISO standard | Cite chapters actually read; say "the notation is ISO 24896, the storyline is not" |
| "IBCS notation is research-backed" | IBCS's own work group: the semantic rules "depend on conventions rather than scientific research" | Argue it on cross-report recognisability; put it in the theme |
| "Green = good, red = bad is universal" | Inverted in CN/JP/KR/TW; ~1 in 12 male readers has CVD | Hue must never be the only carrier of the verdict — the wording states direction («−14% до плану»). Which hues encode good/bad is `pbi-color-accessibility`'s call (its default for binary states is blue/orange, not red/green) |
| "Overview first, zoom and filter" as a law | A 1996 heuristic; van Ham & Perer argue the opposite for known-entity needs; Hullman 2013 ranks granularity transitions **last** | Entry model chosen per audience; drill-in goes last |
| "Narrative intros drive exploration" | Boy, Détienne & Fekete (CHI 2015): three field experiments, no increase | The narrative layer is justified as delivery to the majority who never explore |
| "Scrollytelling beats stepping" / "add a progress bar" | McKenna et al. 2017: in the N=240 study, level of control (stepper vs scroller) showed no effect on engagement — though visuals and animated navigation feedback did; in the 10-person interview study only 2 preferred the stepper, and the progress-bar preference is 3 readers in a separate 8-person pilot | Spend the effort on the claim and on the transitions, not on the stepper-vs-scroller debate |
| "Parallel structure improves understanding" | Hullman 2013 confirmed memory-for-order only | Claim the memory benefit only |
| Borkin 2013 memorability as licence for decoration | Measured recognition of having *seen* a chart, not comprehension | Use Borkin 2016 (titles, redundancy) instead |
| "Decomposition tree = root cause" / "Key influencers explains why" | Greedy search; Wald test on observational data | Hypothesis generators; recompute the claim from a named measure |
| "Alt text must be under 125 characters" | Legacy tool artefact, not a W3C requirement | Two-tier: short alt + long description; length follows content |
| "Action titles: ≤15 words, ≤2 lines" | Consulting-training convention, no study | Kept, explicitly labelled a **house convention** (§2) |
| "≤2 annotations per visual" | A house budget with no evidence base | Labelled as such; the evidenced rule is the focus triad (§4) |
| "Tell a story" as acceptance criterion | At least five incompatible definitions in the literature | Specify claim + evidence + ordering + how much the reader may re-cut |
| "Data speaks for itself" | Contradicted by the rhetoric literature | Demand disclosure (§6), not neutrality |

---

## §13. See also

Shape → `pbi-visualization-strategy` · type and number formats → `pbi-typography` · colour roles
and contrast → `pbi-color-accessibility` · grid and reading order → `pbi-page-layout` · card
anatomy → `pbi-kpi-cards` · tooltips (incl. canvas sizing) → `pbi-tooltips` · drill-through →
`pbi-drillthrough` · bookmark/visibility mechanics → `powerbi-bookmarks` · navigators and tab bars
→ `pbi-navigation-tabs` · dual-axis / combo justification → `pbi-combo-charts` · machine prose →
`pbi-ai-visuals` · scoring a finished page → `pbi-report-review` · approval gates →
`pbi-redesign-approval` · non-BI charts in code/artifacts → the bundled `dataviz` skill.
