# html-deck: engine reference

> The specification behind `assets/deck-template.html`, `scripts/scaffold_deck.py`,
> `scripts/embed_font.py` and `scripts/inline_media.py`. Interfaces (DOM contract, `window.deck`, ready signal) are shared with
> `deck-review` scripts/html_deck_lint.mjs and must not drift; every number and severity belongs to
> `deck-review` references/rubric.md (checks H1-H8 here). Evidence: a 33-slide own HTML reading deck
> ("own deck", 1280x720 px canvas) and the acceptance runs of the template in headless Chromium.
> Units are design px on the 1280x720 canvas; 1 pt = 4/3 px. Commands run from the user's working folder;
> `<html-deck>` and `<deck-review>` stand for those skill folders.

## §1. Canvas and scaling (H1, L63)

One fixed canvas, one transform, centred in the stage that sits above the control bar:

```css
#stage{position:fixed;inset:0 0 var(--bar) 0;overflow:hidden}
#track{position:absolute;left:50%;top:50%;width:1280px;height:720px;
       transform:translate(-50%,-50%) scale(var(--k,1))}
```

`fit()` sets `--k = min((stage width - 2g) / 1280, (stage height - 2g) / 720)` with the gutter `g` = 14 px
(0 in the presenter pane) on load, on resize and after fonts load. The stage already excludes the bar,
so the bar is reserved by construction.

- **Why not grid centring.** The own deck used `display:grid; place-items:center` and scaled the track
  around its own centre. Below 1280 CSS px the grid column stays 1280 wide, so the scaled box is centred on
  x=640, not on the viewport: x=142..1138 at 1024x768 (114 px cut), 39 px cut at 1093x615 (a 1366 laptop at
  125%), 226 px at 800x600, and the slide is entirely off-screen at 390x844.
- **Acceptance** (H1 `viewports`, `fit_tol_px`): the slide box stays inside the viewport and above the bar
  on every slide. Template run: k = 0.906 at 1280x720, 1.156 at 1600x900, 0.778 at 1024x768, 0.283 at
  390x844, 0.972 at 1366x768, 1.406 at 1920x1080, zero slides outside at any size.
- **Phone portrait** scales the slide to a 362 px wide thumbnail that fits the viewport (H1); it is not
  readable without zoom (talk body about 8 CSS px at k=0.283), so the phone target is the PDF. The template
  has no rotate hint: presenting from a phone is not a target.
- **The bar never wraps** (`white-space:nowrap`): the hint hides below 980 px, the part label, route and
  presenter buttons below 640 px. The own deck's bar wrapped to 3-4 lines at 390 px.

## §2. DOM contract and generated content (H2, L64)

| Author writes | Engine generates |
|---|---|
| `section.slide#<id>[data-archetype][data-part]` (+ class `a-<id>`, optional `data-mode="reading"`, `data-appendix`) in `#stage > #track`, between `<!-- @slides:start -->` and `<!-- @slides:end -->` | `a-<id>` when missing, `role=group`, `aria-roledescription`, `aria-label` «N з M: заголовок», the readout `NN / NN · part`, the progress bar |
| empty `.pn` (every slide except the title and dividers, K1) | the slide number |
| `[data-part-n]` on a divider | «n / N» of the parts |
| `[data-count]`, `[data-count="main"]`, `[data-count="parts"]` | «13 слайдів», main-flow count, «3 частини» with plural forms |
| empty `nav[data-toc]` | numbered parts with title, question and the generated slide range («3-7»; an en dash only under `dash_policy: en-dash`) |
| `<a data-ref="slug">`, `<a data-ref="a b">` | «слайд 13», «слайди 4 і 7» and `href="#N"`; unresolved: red `.ref-missing` «слайд ?» plus a console error |
| `[data-list="name"][data-render="chips\|steps\|progress\|cards"]` | items from `script#deck-data` `lists` (name `parts` falls back to the parts) |
| `[data-current="item"]` on a progress list, `[data-item-n]` on the eyebrow | the current item marked `.on`; «1 / 3 · мітка» |
| `li[data-item="id"]` children of a cards or steps list | kept as the per-item detail under the rendered name and icon |
| `aside.notes` | presenter panes; hidden on screen and in print |
| a number group («3-2-1», «10-15», «2024-2026») typed plainly in a title or dek | `span.nw` around it in `.slide > .t`, `.slide > .dek`, the route's part names and questions, and rendered list names (§10) |
| `figure.shot > img[data-ui-px][data-native-width]` with a data URI `src` (§13) (+ `svg.ov > rect.hl`, `.callouts`) | nothing: `deck-review` measures S1 and S3 |

Plural forms follow `ukrainian-ui-copy` («Множина після числа»: 1 слайд, 2 слайди, 5 слайдів, 11 слайдів);
every generated number is bound to its noun with NBSP. Icons render only when the page holds an SVG
`<symbol id="i-<name>">` for the list item's `icon`; otherwise the card shows the name alone.

**Single source.** The part label exists once, in `script#deck-data` `parts`; a second hand-typed label
drifts (the own deck's rail and bar disagreed on 6 slides). The own deck typed 33 slide numbers, 23 TOC
ranges, 8 prose references and «33 слайди»; inserting one slide broke all of them.

**`script#deck-data`** (written by the scaffold): `{"meta": {title, lang, mode, minutes, qa_minutes,
dash_policy}, "parts": [{id, title, question}], "lists": {...}, "minutes": {"<slide id>": n}}`.

**`window.deck`** (defined before the ready signal; the lint's only entry point):

```js
window.deck = { version: 1, count, get index(), slides, go(i, {push}), next(), prev(), lists, meta, ready };
```

- `go(i, opts)` clamps, shows slide i synchronously, returns undefined; `opts.push` adds a history entry.
- Ready: `deck.ready` resolves, `<html data-deck-ready="1">` is set and `deck:ready` fires on `window` in
  the same task, after every embedded face is loaded, numbering, TOC, refs and lists are rendered and
  `fit()` has run (3 s cap if `document.fonts` never settles).
- Every navigation dispatches `deck:change` with `detail = {index}`. Lint sequence: `go(i)`, two
  `requestAnimationFrame` ticks, measure, screenshot the slide box.
- Chrome that is never content carries `data-chrome` (`#prog`, `#bar`, `#live`, overview, presenter
  panes, toasts); `<html data-presenter-transport>` names the sync transport (§4).

## §3. Navigation, history, overview (H6, L68)

| Keys | Action | History |
|---|---|---|
| → Space PageDown N | next | replace |
| ← Shift+Space PageUp P | previous | replace |
| Home End | first, last | push |
| G | route slide (first `.a-route` or `nav[data-toc]`) | push |
| O | overview grid; arrows move, Enter opens, Escape or O closes | push on open |
| S | presenter window | |
| T, F | theme, fullscreen | |

- Keys with Ctrl, Alt or Meta pass through (Ctrl+P still prints); keys inside inputs and editable
  elements pass through; Space and Enter on a focused button or link activate it instead of navigating.
- Letters are matched by physical key (`event.code`), so N, P, G, O, S, T, F work with a Ukrainian layout,
  where the N key types «т». The own deck matched `event.key` and ignored them.
- Swipe: one finger, at least 50 px horizontally and 1.5x the vertical travel. Tap or click: left 30% of
  the slide goes back, the rest forward; links, buttons, code, `.term`, `[data-nav-ignore]` and a text
  selection are excluded.
- History: steps use `replaceState`; TOC links, `data-ref` links, overview picks, Home, End and G push,
  so browser Back returns from a jump (the own deck used `replaceState` only, so Back left the deck).
  `#N` and `#slide-id` deep links work on load and through `hashchange` and `popstate`.
- Overview tiles are clones without ids or notes inside an `inert` frame; the grid is removed on close so
  `section.slide` counts stay equal to the deck. Measured: 13 tiles, Enter opens the focused tile.

## §4. Presenter view and sync (H6, L68)

S (or the bar button) opens the same file as `deck.html?presenter#N` in a window named `deckPresenter`.
Panes: the current slide (the real track, scaled into the pane), the next slide (an inert clone), the notes
of the current slide (`white-space: pre-line`), and a timer: elapsed time, «Позначка m:ss» (cumulative plan
minutes through the current slide from `deck-data.minutes`, red when late), «N / M · title», pause and
reset, and the link state. A blocked pop-up shows a toast, never a blocking dialog.

Messages: `{deck: "html-deck:<path>", type, i}` with `type` `go` (either side, after a local move),
`hello` (presenter on load; the audience answers with `go` of its index) and `ping` (presenter every
2 s, so an audience window that reloaded learns its peer again). A received `go` is never echoed.

| Page served from | Transport |
|---|---|
| `file://` | `postMessage` over the `window.open` handle and `window.opener` |
| `http(s)://` | `BroadcastChannel`; `storage` events on `localStorage` when it is missing |

Window handles work whatever origin a browser gives a `file://` page, while BroadcastChannel and storage
events need one shared origin, which `file://` does not guarantee across browsers. In the test Chromium
both also crossed `file://` windows, so this is a portability choice, not a measured Chromium failure.
Measured follow time (H6 `presenter_follow_ms`): 10-22 ms both ways over `file://`, 9-22 ms with
BroadcastChannel over http, 14-18 ms with the storage fallback.

## §5. Theme (H6, L68)

- A one-line script in `<head>`, before the first `<style>`, restores `localStorage['deck-theme']` inside
  `try/catch` (private windows and blocked storage must not break the deck). Measured: `data-theme` is set
  before the first stylesheet is parsed, so there is no flash; the own deck restored it at the end of body.
- Tokens: light roles on `:root`, dark on `:root[data-theme="dark"]`, void and status roles global, type
  roles per mode; values equal `slide-design` assets/tokens.example.json (`slide-design`
  references/visual-system.md §9 is the mapping). Replace the values, never the role names.
- Colour values exist in five blocks, which change together: (1) light `:root`, (2) dark
  `:root[data-theme="dark"]`, (3) its copy under `@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) }`, (4) the dark family `.slide.a-title, .slide.a-divider,
  .slide.a-demo-divider, .slide.a-appendix-divider`, (5) the light copy in `@media print` (§7).
  `deck_lint.py --tokens deck.html` rates only blocks 1 and 2, and H4 `light_tokens` compares the print of
  a dark-stored deck with the light print, so a stale copy 3-5 passes both: the PDF and the title and
  dividers keep the old palette. Compare the five blocks after every token change.
- Families: the title and the three divider archetypes carry the dark family in both themes (token sheet
  `families.dark`); code and diagram boards use the always-dark void tokens.

## §6. Fonts (H3, L65)

- **Default:** the metric-stable stacks `Arial, Arimo, "Liberation Sans"` and `"Courier New", Cousine,
  "Liberation Mono"`: the same advance widths on Windows, macOS and Linux.
- **Embedded:** `python3 <html-deck>/scripts/embed_font.py deck.html --sans Inter.woff2:400 --sans
  Inter.woff2:600 --mono JetBrainsMono.woff2:400 --subset --apply` (needs `pip install fonttools brotli`;
  with the standard library only, pass TTF or OTF faces without `--subset`). OFL faces with Cyrillic:
  Inter, IBM Plex Sans, Noto Sans; JetBrains Mono, IBM Plex Mono. Embed 400 and 600, or the browser fakes
  the bold.
- **Guards:** OFL confirmed by name IDs 13/14 or an OFL.txt next to the font, the notice copied into a CSS
  comment, OS/2 fsType must allow embedding; і ї є ґ ’ « » № NBSP and the minus sign must be in the cmap
  (exit 1 otherwise). Read with the standard library for TTF, OTF and WOFF; WOFF2 and `--subset` need
  fontTools with brotli, and a face whose cmap or fsType cannot be read is refused (exit 2) unless
  `--allow-unverified` is given. Name-table strings are untrusted: the family keeps only letters, digits,
  space, `.`, `_` and `-`, the notice loses `<`, `>` and comment closers, and the licence URL is used
  only when it is a plain http(s) URL. Measured: Liberation Sans 411 KB TTF adds 548 KB as a data URI;
  three full faces add 1.5 MB, which is the warning line, so subset.
- **Never platform-only faces.** Segoe UI and Cascadia exist only on Windows: on Linux the own deck fell
  back to DejaVu and ran 14, 37 and 43 px past the bottom padding on 3 slides and overlapped SVG tspans
  on one; with Arial-metric fonts the same slides stayed 55, 17 and 13 px above it. That is up to 55 px of
  drift (text bottoms moved 54, 38 and 55 px), and two of the slides would still miss H3.
- **Two-mode QA:** `html_deck_lint.mjs --fonts both` measures native and metric fonts; H3 wants
  `bottom_slack_px` in both. The engine loads every embedded face before ready, so a slide shown later
  never measures or prints with a fallback.

## §7. Print and PDF (H4, L66)

The template's block, verbatim except the token values (the light set of `:root`):

```css
@page{size:1280px 720px;margin:0}
@media print{
  :root[data-theme],:root:not([data-theme]){
    /* the light colour roles of :root: surface, surface-2, ink, ink-2, line, accent-fill, on-accent,
       accent-text, link, header-fill, header-ink, dim */
  }
  html,body{height:auto;overflow:visible;background:none}
  html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  #stage,#pv,#pv>#stage{position:static;display:block;padding:0}
  #track{position:static;width:1280px;height:auto;transform:none;box-shadow:none}
  /* contain:size: an element that overflows its slide (even clipped) otherwise makes Chromium shrink every page */
  .slide{position:relative;display:flex!important;width:1280px;height:720px;contain:size}
  #track>.slide:not(:last-child){break-after:page}
  #bar,#prog,#live,#overview,.toast,#pv-next,#pv-notes,#pv-time,.copy,.slide>.notes{display:none!important}
}
```

Code wraps on screen and in print through `.term>pre` and `.hero-code` (`white-space:pre-wrap;
overflow-wrap:anywhere`, §9).

- `height:auto` on html, body and the track is required: without it the static track stays 720 px high
  inside a `height:100%; overflow:hidden` body and Chromium prints 1 page instead of 13 (tested by
  swapping blocks in the template).
- Headless: `page.pdf({preferCSSPageSize: true, printBackground: true})`; by hand: Ctrl+P, no margins.
  The PDF to send is `out/print.pdf` of the final `deck-review` lint run (those options, native fonts).
- Measured on the template: 13 slides give 13 pages with MediaBox 960x540 pt; the text layer holds no
  «Копіювати», no notes and no bar text; a deck stored in the dark theme prints with the light tokens
  (the same text colours as the light print). The own deck printed copy buttons, lost 234/233/117 px of
  commands on 3 slides, and printed washed-out headings from the dark theme.
- Chromium print traps (no blanket `break-inside: avoid`, measure page fill on pixels): `react-ux-mechanics`.
- `contain:size` on the printed slide: without it one element that overflows any slide, even clipped,
  makes Chromium shrink every page to about 0.97 (a 48 px title prints at 34.9 pt instead of 36 pt), while
  page count and page size stay correct (found by the `deck-review` selftest fixture).
- Reading this PDF's text layer: Chromium writes it with a 0.75 transform; `deck-review`
  `pdf_text_runs.py` applies the CTM and reports pt, so the PDF path works on a printed HTML deck. Judge
  HTML decks on the HTML path first: it sees roles, boxes and the engine.

## §8. SVG diagrams (H5, L67)

- Draw the viewBox in canvas px at the board width (`viewBox="0 0 1184 400"` for a full-width board), so
  one user unit is one px and SVG font sizes are real sizes; `width:100%; height:auto` gives the board the
  viewBox aspect, so there is no letterbox. The own deck letterboxed 182/190/168 screen px on 3 slides and
  set diagram text at 6.6-9.8 px.
- Labels centred with `text-anchor="middle"` and about 15% horizontal slack; running sentences go in HTML
  under the SVG, never as absolute-x tspans (they overlapped under DejaVu in the own deck, and its footnotes
  ran past the viewBox).
- `role="img"` with a full-sentence `aria-label`, plus an HTML legend when colours encode something.
- Colours through classes and CSS variables (`.bx .ln .lb .fx .ah` in the template); the own deck repeated
  its tokens as hex in 7 diagrams. Marker ids are unique per slide.
- Animation only through classes switched off by reduced motion and print (`react-ux-mechanics`
  assets/animations.css).

## §9. Code blocks and copy (H4, L66)

- Anatomy: `.term > .term-hd > (.ttl, button.copy)` + `pre`. The copy click takes `pre.textContent`,
  turns NBSP into spaces, then tries the Clipboard API, then a hidden textarea with `execCommand('copy')`,
  then selects the block and says «Виділено, натисніть Ctrl+C»; success shows «Скопійовано» for 2.2 s.
  Measured: the clipboard holds exactly the displayed command.
- No horizontal overflow: `pre-wrap` wraps on screen and in print (`overflow` 0 px for a 125-character
  command). Mono advance is 0.6 em, so a line holds about width / (0.6 x font px): talk code at 24 px about
  37 characters in a half column (576 px) and 79 at full width, reading code at 16 px about 55 and 119.
  Prefer short commands or line continuation (`\`, PowerShell backtick) to wrapped ones.
- Straight quotes and one mono family are `slide-design` rules (V7).

## §10. CSS hygiene (H7, L69)

- Component internals use child selectors: the own deck's `.hero .strip div` also matched nested divs and
  drew stray rules beside its proof numbers.
- Pills, chips and progress items are `white-space:nowrap` (the own deck wrapped two pills).
- Number groups stay on one line. Chromium breaks after a hyphen or an en dash, so under `dash_policy:
  hyphen` (`deck-storyline` references/titles-and-copy.md §9) an eval deck's 72 px divider «Як правило
  3-2-1 повертає файл?» broke as «3-2-» / «1», and «10-15 хвилин» breaks as «10-» / «15». The engine wraps
  every `\d+(-\d+)+` group (en dash too) in `span.nw` (`white-space:nowrap`) in titles, deks, the route's
  part names and questions and rendered list names, before ready; in body text and table cells the author
  wraps a group by hand with `<span class="nw">`. Not U+2011: Liberation Sans, the metric stack's
  face on Linux, has no non-breaking hyphen, so the glyph comes from a fallback face with other metrics.
- No `style` attributes in slide markup: utilities `.g12` with `.c3`-`.c12`, `.stack`, `.mt-auto`,
  `.muted`, `.strong`, `.mono` cover the 79 inline styles of the own deck (15 widths, 10 `flex:none`, 8
  bottom margins, 7 `margin-top:auto`, 7 flex columns, 4 font sizes). Runtime styles the engine sets
  (`--k`, `--s`, progress width) are not markup.
- `.body` sizes to its content (`flex: 0 1 auto`), so measured bottom slack is real; no equal-height cards
  with `margin-top:auto` (about 200 px dead gap per card in the own deck).
- `text-wrap: balance` on titles, `pretty` on deks.
- Engine CSS avoids `slide-design` findings an author cannot fix in markup: the page number has one size
  in both modes (16 px, token `geometry.px.page_number`; the reading `--fs-footer` of 12 px moved it 4 px,
  a K1 drift of 3 pt); the part marker «n / N» and progress items use `--fs-label` (24 px = 18 pt), so
  neither the HTML nor the PDF path reads them as body text below the Y1 body size; text cards trim the
  bottom padding by the last line's half-leading (about 4 px), because G5 compares the top padding with
  the space under the glyphs; the terminal header has no rule under it, which G7 counted as a second
  framed level. Measured on the template: 0 критично, бажано only T1 and T11 (lint noise). Still left: the
  15 pt terminal title sets the D2 minimum of a code-step slide (`deck-review` known noise).

## §11. Motion and accessibility

- `prefers-reduced-motion: reduce` removes every animation and transition (measured: the progress bar
  transition becomes 0 s); slides change without transitions, so print and screenshots never catch a
  half state.
- `lang` from the plan, `:focus-visible` outlines, slide groups with «N з M: заголовок» labels, a polite
  live region that announces each move, buttons with titles that name their key.
- Contrast, type sizes and colour meaning are `slide-design` rules; the engine only carries the tokens.

## §12. Known-defects registry

| Defect | Measured in the own deck | Engine fix | Check |
|---|---|---|---|
| Slide off-centre or blank below 1280 px | 114 px cut at 1024x768, blank at 390x844 | translate plus scale centring, bar reserved | H1 |
| Hand-typed numbers | 33 numbers, 23 TOC ranges, 8 references, rail vs bar on 6 slides | generated from the DOM and deck-data | H2 |
| Platform fonts | 14/37/43 px past the bottom padding with DejaVu, up to 55 px of drift | metric stack or embedded OFL face, two font modes | H3 |
| Copy buttons and clipped code in the PDF | 234/233/117 px lost | `.copy` hidden in print, `pre-wrap` | H4 |
| Dark tokens printed | washed-out headings | light tokens forced in print | H4 |
| SVG letterbox and tiny labels | 182/190/168 screen px bands (about 145-165 design px), 6.6-9.8 px text | viewBox in canvas px, `height:auto` | H5 |
| No notes, presenter view, swipe, overview | none present | `aside.notes`, presenter window, swipe, overview | H6 |
| Theme restored at end of body | possible flash | head script before CSS | H6 |
| Back leaves the deck | `replaceState` only | push for jumps | H6 |
| Selector leak, wrapping pills, inline styles | 1 leak, 2 pills, 79 styles | child selectors, nowrap, utilities | H7 |
| Letter keys dead in a Cyrillic layout | matches `event.key` (read in the code, not measured) | `event.code` matching | H6 |

## §13. Scaffold and media (`scaffold_deck.py`, `inline_media.py`)

`python3 <html-deck>/scripts/scaffold_deck.py deck-plan.json deck.html` prints `n | id | archetype | part
| title | budget | todo` (budget from `deck-review` scripts/thresholds.json `archetypes`, the mirror of
references/rubric.md §13; reading budgets on appendix slides) and the warnings; `--apply` writes,
`--force` overwrites. Output is byte-identical for the same plan.

| Slot | Filled from | When the plan is empty |
|---|---|---|
| `title` | `slides[].title` | (required by the plan) |
| `eyebrow` | `slides[].eyebrow` | removed; a series item gets the generated `[data-item-n]` label |
| `dek` | `slides[].dek`; the title slide falls back to `promise` | removed (title slide of a talk: `data-todo`) |
| `context` | `context` (title slide) | `data-todo` in talk modes, removed in reading |
| `notes` | `slides[].notes` | `data-todo` on main talk slides (H6), removed on appendix and reading slides |
| `list` | `list` (hub, journey), `series{list,item}` (`data-current`), the close recap source | `data-todo` |
| `media` | `media[0]` `file`, `ui_px`, `native_px` (`deck-storyline` references/deck-plan.md §4) become a relative `src` (a warning names the slides), `data-ui-px`, `data-native-width`; alt from `claim` or `title` | `data-todo`; also when the file is missing next to `deck.html` |
| `next`, `url` | `close.next_step`, `close.url` (close and cta) | `data-todo`; the close drops an empty URL pill |
| any other | | `data-todo` with a hint, for the author |

- A hub gets one `li[data-item]` per list item with `data-todo` for its differentiator.
- The close recap renders from `parts` when `close.recap` equals the part titles, or from the list whose
  labels it equals; anything else is a plan error left as `data-todo`.
- Exit 2 for contract errors (schema, mode, `n` sequence, slugs, unknown archetype snippet, unresolved
  part, list or series item, malformed media) with every problem listed; full plan rules are
  `deck_lint.py --plan-only`. A plan whose `approval.status` is not `approved` only warns.

**Media inside the file.** A relative `src` breaks the one-file promise: the deck sent alone shows no
image. `python3 <html-deck>/scripts/inline_media.py deck.html` lists every `img src` between the slide
markers with its slide id and the bytes it adds; `--apply` rewrites them as data URIs, and a second run
changes nothing.

| File | Data URI |
|---|---|
| PNG, JPEG, WebP, GIF | `data:image/png;base64,...` (about 4/3 of the file) |
| SVG | `data:image/svg+xml,` + percent-encoded text: `%` `#` `<` `>` `"` `&` and line breaks escaped |

- `#` must be written `%23`: a raw `#` starts the URL fragment, so `fill='#0B1118'` cuts the SVG short
  and the image does not load (an eval deck's hand-written mock-up did this; the template's demo shows the
  `%23` form). The script encodes it; check by hand only an SVG URI typed into the markup.
- A missing file or an unsupported type stops the run with exit 1 and writes nothing; an http(s) `src`
  is kept with a warning (the script never downloads, and the deck then needs the network).
- To replace an inlined image, point its `src` at the new file and rerun.

## §14. See also

`slide-design` references/archetypes.md (anatomy of every `.a-<id>`) and references/visual-system.md
(tokens), `deck-storyline` references/deck-plan.md (plan fields) and references/demos-and-notes.md §5
(notes content), `deck-review` references/rubric.md (H1-H8 numbers), `react-ux-mechanics` (print traps,
animation guards), `ukrainian-ui-copy` (plural forms, NBSP).
