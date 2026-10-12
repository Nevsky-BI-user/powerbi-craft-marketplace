# deck-review: teardown of someone else's deck

> How a reference deck becomes a lessons ledger without leaking it. This is the pipeline that produced
> lessons L01-L79 from a 52-slide vendor platform deck (960x540 pt PDF carrying a sensitivity label) and
> a 33-slide own HTML deck. Check IDs point to `references/rubric.md`; lessons to the ledger format in §9.

## §1. When

- «проаналізуй цю презентацію», «розбери чужу презентацію», «що взяти з цього деку»: someone else's deck
  is the input, lessons are the output.
- The output feeds skill updates (rubric rows, archetypes, tokens) or a new deck's token sheet and plan.
- Not a review of the user's own deck before a show: that is the audit loop in SKILL.md.

## §2. Privacy (applies to every output, including scratch notes that may be pasted later)

1. **The source stays in scratch.** Copy the PDF into a scratch folder outside every repository; never
   commit it, its PNGs, `pages.txt` or contact sheets. A deck carrying a sensitivity or classification
   label stays in scratch: the PDF, its PNGs, `pages.txt`, `pages.json` and contact sheets never leave it;
   only measurements (sizes, counts, ratios, hex values, slide numbers) may, as in the rubric calibration
   rows.
2. **No identities.** No presenter, event, customer, partner or person names, no tenant or workspace
   names, no e-mails or URLs with IDs. Refer to the source as "a 52-slide vendor platform deck" or
   similar. Product names are replaced by their role ("a data catalog", "the notebook editor") whenever
   the lesson is general.
3. **At most 6 words verbatim.** Paraphrase titles and bullets; quote at most 6 consecutive words, and
   only when the wording is the lesson. `deck_lint.py` truncates its evidence to 6 words for the same
   reason.
4. **Numbers are fine, content is not.** Sizes, counts, contrast ratios, positions and slide numbers are
   the evidence; what the slides say about the product is not.
5. **Screenshots in the source are someone's data.** Describe what a capture shows ("a personal name in
   the greeting"); never copy the name (S4 is the rule for your own captures).
6. Before anything leaves scratch: `git grep -i` for every name you saw, and a grep for temporary-folder,
   home-folder and drive-letter paths.

## §3. The fixed order (L79)

Cheap global signals first, expensive local checks last. Commands as run on the reference, from the
scratch folder (`ref/` inside it), with the scripts called by their path in this skill (`<skill>/scripts/`);
never run them with the skill folder or any repository as the working directory. Measured cost on a
52-page, 12 MB PDF:

| Step | Command | Cost | Gives |
|---|---|---|---|
| 1. Pages | `node <skill>/scripts/pdf_pages.mjs deck.pdf ref/png` | 2 min 43 s, 20 MB of PNG | 52 page-exact PNGs at 1.69 px/pt |
| 2. Runs | `python3 <skill>/scripts/pdf_text_runs.py deck.pdf ref/runs` | 15 s | `pages.json`, `pages.txt`, `stats.txt` |
| 3. Pixels | `node <skill>/scripts/pixels.mjs ref/png ref --runs ref/runs/pages.json` | 8 s | 2 contact sheets, luminance, dHash, run backgrounds |
| 4. Judge | `python3 <skill>/scripts/deck_lint.py --runs ref/runs/pages.json --pixels ref/pixels.json --out ref` | under 1 s | findings with slide numbers |
| 5. Look | contact sheets, then every PNG | most of the time | families, archetypes, visual checks |
| 6. Spot checks | §8 | 10-12 slides | confirmed or refined claims |

Order of reading: contact sheets (families, luminance flips, near-duplicates, how many templates) ->
per-slide runs next to the PNG (archetype, title type, smallest font, words, layout) -> deck statistics
weighted by words (fonts, sizes, colours) -> computed contrast for the top colour pairs -> pixel spot
checks of the most surprising claims.

Run the judge twice when the plan is unknown: once bare (archetype-free checks), then again with an
inferred plan (`inferred: true`, archetypes guessed from the contact sheet) so N2, N5, D2 and the divider
exemptions apply.

## §4. Rendering without poppler (L76)

poppler, PyMuPDF and pdfplumber were all missing; full Chromium was present. `pdf_pages.mjs` encodes what
worked:

- Full Chromium in new headless mode. The headless *shell* has no PDF viewer: the script refuses a
  `CHROME_PATH` that points to it and exits 1 when the browser downloads the PDF instead of showing it.
- `file:///.../deck.pdf#page=N&toolbar=0&navpanes=0&view=Fit`, with `about:blank` between pages (a
  fragment change alone does not reload the viewer).
- Wait for the asynchronous paint: about 5 s for the first page, 2.5 s after (`PDF_WAIT_MS`), then
  capture until two screenshots agree; one retry on a blank capture.
- Viewport 1640x940 gives about 1.7 px/pt. The page rectangle is found on the pixels (the viewer draws a
  neutral dark grey with a soft shadow) and the PNG is cropped to it in memory. Do not clip with the
  screenshot API on the viewer: the clip came back offset by the page margin.
- Page count from `/Type /Pages /Count`; a compressed page tree needs `[from] [to]` on the command line.
- When poppler's `pdftoppm` exists it is a faster alternative; keep the PNG names `slide-NN.png` so
  `pixels.mjs` and the judge pair them with the runs.

## §5. Text runs with xpdfimport (L77)

LibreOffice ships `xpdfimport`, the PDF import filter of Draw. It is the only positioned-text extractor
that came with the machine. `pdf_text_runs.py` encodes the practice:

- Pass an options argument `-o ''` and a newline on stdin as the password; otherwise it aborts with
  "basic_string: construction from null".
- stdout mixes text commands with binary image and font payloads that are **not adjacent** to the
  commands announcing them. Never skip payload bytes by length; read line by line and ignore every line
  that is not a command. On the reference stdout was 208,580,919 bytes with 16,781 `drawChar` and 52
  `startPage` lines; stderr carried 68 MB of image data and goes to a temporary file.
- Run under `stdbuf -o0` on Linux when available. The buffered and unbuffered runs were byte-identical,
  so it is a safeguard against losing the tail on a crash, not a fix.
- `startPage 96000 54000` is 960x540 pt: page sizes arrive in hundredths of a point.
- `updateFont` carries the font name after its 7th field; `updateFillColor r g b a` sets the fill.
- `drawChar x0 y0 x1 y1 a b c d size char` is in **user space** with the Tf size. The transformation
  arrives separately as `updateCtm` (absolute, hundredths of a point, y measured down from the page top),
  and `saveState` / `restoreState` restore CTM, colour and font **without re-emitting them**. The parser
  keeps its own state stack and maps every character to page points. A PowerPoint export draws text in
  page space, so a parser without the CTM looks right there; a browser-printed HTML deck draws in CSS px
  and lands 720 px lower per page.
- Output convention: x from the left, y = baseline from the **bottom**, size in pt; sort by -y for
  reading order.
- Runs: consecutive characters with the same font, colour and size whose gap is under 0.6 of the size
  join one run; a gap above 0.18 of the size inserts a space. This re-joins most kerning splits; the
  judge also joins runs that touch on one baseline into lines (colour splits inside a bullet).

## §6. Blind spots, each re-verified on pixels (L78)

| Blind spot | What the text layer says | What to do |
|---|---|---|
| Gradient text | `#000000`, even on a black page | count it as "black or gradient"; C3 could-not-verify on dark backgrounds |
| Kerning and colour splits | one word or bullet in two runs | count tokens of grouped runs and lines, never runs |
| Hidden titles | runs with y above the page height (553.1 and 576.0 on a 540 pt page) | V4 off-canvas; look at the PNG |
| Text under images | present and counted | V4 and S6 need the PNG |
| Raster text | absent: 0-5 live words on a slide full of words | V4 raster suspect; read the PNG |
| Scaled imports | sizes such as 34.7, 32.1, 17.1 pt | Y2 non-integer sizes; signals a pasted, scaled slide |

## §7. Statistics as distributions

- Words per slide as a list, then silent (at most `silent_words_max`) and dense (above D1 `words_hard`)
  slides. On the reference mean 47.1 and median 39 looked healthy while 11 slides were silent and 7 dense,
  often neighbours (0, 48, 165, 255 words on four consecutive slides).
- Sizes weighted by words (the `stats.txt` SHARE line gives the share below the `--small` cut and the talk
  Y1 `floor_pt` and `body_pt`, 12, 14 and 18 pt by default), non-integer sizes, font names and folded
  families, text colours by words.
- Title x, y and size per slide (G1), page numbers (K1), template families and luminance per slide (K2,
  C4) from the contact sheets.
- Contrast: compute the top colour pairs with the `pbi-color-accessibility` reference.md §1 formula and
  label every ratio **computed** (exact hex) or **approx.** (sampled pixels). The background under a run
  comes from `pixels.json` `run_bg`; an `unknown: true` ring is not a measurement.
- `stats.txt` counts whitespace tokens (it reproduces the analysts' numbers); `deck_lint.py` counts live
  words, tokens with a letter or digit, so a few bullets and pipes drop out of its totals.

## §8. Spot-check protocol

1. Pick the 10-12 most surprising claims from the analysts or the judge (a contrast below 2.5:1, a hidden
   title, identical bullets, connectors off the card centres).
2. Open each slide PNG at full size and its runs side by side; for pixel claims sample the colours or
   measure positions on the PNG.
3. Record each claim as confirmed, refuted or refined with the evidence. On the reference 11 slides were
   checked; every high-confidence claim held and 6 refinements were recorded (for example: one display face's word
   count was mostly the event footer band; the #000000 count included gradient text; page numbers existed
   on 15 slides, not "about 17").

## §9. Ledger format

`evidence.md` (in scratch): measured deck facts, the spot-check log, the arc, the design system observed,
the archetype catalog, then the ledger. One entry per lesson:

```
**L49** [density | do | high]
Rule: one sentence, imperative, with the number when there is one.
Why: the cost of breaking it, in one sentence.
Evidence: slide numbers and measurements, no names, at most 6 words quoted.
```

Confidence: **high** = measured and spot-checked on pixels; **medium** = measured, or seen on at least
2 slides; **low** = a single observation, not codified into a rule.

## §10. From ledger to skills

- Each high or medium lesson lands in exactly one owner skill; others cite it by id.
- Numbers go to `references/rubric.md` and `scripts/thresholds.json` in one commit; prose never restates
  them.
- Every new automatic check gets a measurement field in a script and a seeded fixture slide (rubric §15).
- The reference PDF and its renders stay local and the regression against it runs locally (rubric §14);
  only the measured numbers in the calibration rows enter the repository.
