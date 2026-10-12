---
name: html-deck
description: Use when building or fixing a self-contained offline HTML presentation - scaffolding it from an approved deck-plan.json (without one, deck-storyline first), a 1280x720 canvas scaled into any viewport, keyboard, touch and overview navigation, slide numbers, TOC and cross-references generated from the DOM, exact one-slide-per-page print to PDF, embedded Cyrillic fonts, aside.notes with a presenter view that works from file://, inline SVG diagrams, copyable code blocks. Symptoms - slide cut off or blank on a laptop or phone, hand-typed numbers out of sync, copy buttons or clipped code in the PDF, layout that shifts on another OS. Do NOT trigger for .pptx files (pptx), a claude.ai Slides artifact, what slides say or look like (deck-storyline, slide-design), judging a finished deck (deck-review), React dashboards (react-ux-mechanics). Triggers - 'HTML-презентація', 'презентація в браузері', 'друк презентації в PDF', 'режим доповідача', 'слайд обрізається', 'html deck', 'presenter view'.
---

# HTML deck: one file, any screen, exact PDF

## Overview

This skill owns the engine of a single-file offline HTML deck: canvas and scaling, generated numbering,
navigation, notes and presenter view, theme, fonts, print, SVG and code mechanics, CSS hygiene, and the
`window.deck` API the lint drives. What the slides say belongs to `deck-storyline`, how they look to
`slide-design`, the verdict to `deck-review`. Every rule cites a `deck-review` references/rubric.md check
(H1-H8 here), which owns every number. Depth: `references/engine.md`.

Evidence is a 33-slide own HTML reading deck. Kept from it: one transform on a fixed canvas, token
theming, the three-tier copy fallback, `#N` deep links, the clickable route, the keyboard map, exact
1280x720 print, reduced motion. Fixed (L63-L69): grid centring that cut or blanked the slide below 1280 px,
hand-typed numbers, platform-only fonts, copy buttons and clipped code in the PDF, no notes or presenter
view, theme restored after first paint, inline styles.

## When to Use

- Building a deck that is shown from a browser and sent as a PDF, with no build step and no network.
- Turning an approved `deck-plan.json` into slides; fixing an HTML deck that cuts off, mis-numbers,
  prints badly, shifts on another OS, or lacks notes and a presenter view.
- If the finished file is then published as a hosted page, the host's artifact rules apply on top.

**NOT for:** .pptx files (`pptx`); a claude.ai Slides artifact (Slides artifact type); arc, titles and
notes content (`deck-storyline`); token values, archetype anatomy, colour pairs (`slide-design`); running
the QA loop and judging findings (`deck-review`); React dashboards (`react-ux-mechanics`); visual direction
of web UI (`frontend-design`).

## Pre-flight

Commands run from the user's working folder, which holds `deck-plan.json`, `deck.html` and `out/`;
`<html-deck>` and `<deck-review>` stand for those skill folders (siblings in this plugin).

1. The storyboard is approved: `approval.status` is `approved` in `deck-plan.json` (`deck-storyline`).
2. Scaffold: `python3 <html-deck>/scripts/scaffold_deck.py deck-plan.json deck.html` prints `n | id |
   archetype | part | title | budget | todo`; read it, then rerun with `--apply`.
3. Paste the `slide-design` token sheet values into the template; keep the role names (`slide-design`
   references/visual-system.md §9). Colours sit in five blocks: light `:root`, dark
   `:root[data-theme="dark"]`, its `prefers-color-scheme` copy, the dark family (title and dividers) and
   the light copy in `@media print`; type scales in `:root` and `[data-mode="reading"]`. `deck_lint.py
   --tokens` rates only the light and dark blocks and does not see a stale copy.
4. Fonts: `python3 <html-deck>/scripts/embed_font.py deck.html --sans <OFL>.woff2:400 --sans
   <OFL>.woff2:600 --mono <OFL mono>.woff2:400 --subset --apply`; `--subset` and .woff2 inputs need
   `pip install fonttools brotli`. Standard library only: pass the TTF or OTF without `--subset` (full
   faces, mind the 1.5 MB warning). Or keep the metric-stable stack and run two-mode QA.
5. Fill every `data-todo` slot (outlined on screen); write notes in `aside.notes`; never type a slide
   number, a range or a total.
6. Images stay inside the file: `python3 <html-deck>/scripts/inline_media.py deck.html --apply` turns each
   relative `img src` into a data URI (base64 PNG and JPEG, percent-encoded SVG with `#` as `%23`); to
   replace an image, point `src` at the new file and rerun. A hand-typed SVG URI with a raw `#` fails.

## Author vs engine

| Author writes | Engine generates |
|---|---|
| `section.slide#id[data-archetype][data-part]`, class `a-<id>` | number, total, part label, progress, `NN / NN · part` readout |
| empty `.pn`; `[data-part-n]` on dividers | slide number (K1); «n / N» of the parts |
| `<a data-ref="slug">` | «слайд N» and the jump link (`ukrainian-ui-copy` plural forms) |
| empty `nav[data-toc]` | route with part titles, questions and generated ranges |
| `[data-list][data-render]` with `deck-data` lists | hub cards, progress strips, recap chips, steps |
| `aside.notes` | presenter panes; hidden on screen and in print |
| plain «3-2-1» or «10-15»; `<span class="nw">` around one in body text | `span.nw` around number groups in titles, deks, route and list names |
| nothing | `window.deck = {version, count, index, slides, go, next, prev, lists, meta, ready}` |

`script#deck-data` (meta, parts, lists, minutes) is written by the scaffold; lists and parts exist once,
there (N13). Contract details and the extra hooks (`data-count`, `data-current`, `data-item-n`):
`references/engine.md` §2.

## Quick Reference

| Rule | Test | Check | Lesson |
|---|---|---|---|
| One translate plus scale transform, bar reserved | slide box inside every H1 viewport, above the bar | H1 | L63 |
| Numbers, TOC ranges, totals and refs generated | no literal slide number in markup | H2 | L64 |
| Embedded OFL subset with Cyrillic, or the metric stack | bottom slack in native and metric font modes | H3 | L65 |
| Print: pages equal slides, chrome, `.copy` and notes hidden, light tokens, no clipped code | `print.pdf` page count and text layer | H4 | L66 |
| SVG viewBox in canvas px, `height:auto`, text inside the viewBox | letterbox and text-outside measures | H5 | L67 |
| Notes on every main talk slide, presenter view over file://, swipe, overview, theme in head | notes count, follow time | H6 | L68 |
| Child selectors, nowrap pills, utilities instead of `style` | inline styles 0, pills on one line | H7 | L69 |
| No scaffold leftovers | `[data-todo]` count 0 | H8 | L73 |

## Canvas

```css
#stage{position:fixed;inset:0 0 var(--bar) 0;overflow:hidden}
#track{position:absolute;left:50%;top:50%;width:1280px;height:720px;
       transform:translate(-50%,-50%) scale(var(--k,1))}
/* fit(): --k = min((stage w - 2g) / 1280, (stage h - 2g) / 720), g = 14 px, on load, resize, fonts */
```

Grid centring with `place-items:center` left the own deck at x=142..1138 at 1024x768 and blank at 390x844.
The template passes 1280x720, 1366x768, 1600x900, 1920x1080, 1024x768 and 390x844 (k from 0.283 to 1.406).
Slide padding 80/48/72 puts the title box at y=80 on every content slide (G1). The body starts at y=160
when there is no dek; a dek starts at y=152 and pushes the body down (y=203-208 in the template).

## Navigation

- Next: → Space PageDown N; previous: ← Shift+Space PageUp P; Home, End; G route; O overview; S presenter;
  T theme; F fullscreen. Letters match the physical key, so a Ukrainian layout works.
- Keys with modifiers or inside inputs pass through; Space and Enter on a focused button activate it;
  movement clamps at the ends; swipe of 50 px or more; tap or click on the left 30% goes back.
- Steps replace the history entry; TOC, `data-ref`, overview, Home, End and G push one, so Back returns
  from a jump. `#N` and `#slide-id` deep links, `hashchange` and `popstate` are followed.

## Presenter view

- S opens the same file with `?presenter`: current slide, next slide, notes, elapsed time against the plan
  minute mark, pause and reset.
- Sync over `file://` by `postMessage` through the `window.open` handle and `window.opener`; over http(s)
  by BroadcastChannel, with `storage` events as the fallback. Measured follow time 9-22 ms on all three
  (H6 allows 200 ms).
- Notes content and timing come from the plan (`deck-storyline` references/demos-and-notes.md §5).

## Print

Excerpt of the template's print block (full block: `references/engine.md` §7):

```css
@page{size:1280px 720px;margin:0}
@media print{
  :root[data-theme],:root:not([data-theme]){ /* light tokens */ }
  html,body{height:auto;overflow:visible;background:none}
  html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
  #stage,#pv,#pv>#stage{position:static;display:block;padding:0}
  #track{position:static;width:1280px;height:auto;transform:none;box-shadow:none}
  .slide{position:relative;display:flex!important;width:1280px;height:720px;contain:size}
  #track>.slide:not(:last-child){break-after:page}
  #bar,#prog,#live,#overview,.toast,#pv-next,#pv-notes,#pv-time,.copy,.slide>.notes{display:none!important}
}
```

Without `height:auto` on html, body and the track, Chromium prints 1 page instead of 13. The template
prints 13 pages at 960x540 pt with no copy label, bar text or notes in the text layer, also when the deck
is stored dark. The PDF to send is `out/print.pdf` from the final lint run (`page.pdf` with
`preferCSSPageSize` and `printBackground`, native fonts); by hand: Ctrl+P, margins none.

## Fonts

Default stacks are metric-stable: `Arial, Arimo, "Liberation Sans"` and `"Courier New", Cousine,
"Liberation Mono"`. Embedding takes OFL faces only (Inter, IBM Plex Sans, Noto Sans; JetBrains Mono, IBM
Plex Mono); `embed_font.py` refuses a face without і ї є ґ ’ « » № NBSP or the minus sign, and one whose
coverage it cannot read (a .woff2 without fontTools) unless `--allow-unverified` is given; it copies the
sanitised licence notice into the CSS. Never Segoe or Cascadia alone: with the Linux fallback the own deck
ran 14/37/43 px past the bottom padding on 3 slides; with Arial-metric fonts it stayed 55/17/13 px above
it: up to 55 px of drift, and two slides would still miss H3. Procedure and sizes: `references/engine.md` §6.

## Common Mistakes

| Mistake | Why bad | Correct |
|---|---|---|
| Grid-centred track scaled around its centre | cut by 114 px at 1024x768, blank on a phone (H1) | translate plus scale, bar reserved |
| Hand-typed numbers, ranges, «33 слайди» | one inserted slide breaks 33 numbers, 23 ranges, 8 refs (H2) | `.pn`, `nav[data-toc]`, `data-ref`, `data-count` |
| Windows-only fonts | layout drifts up to 55 px on another OS (H3) | embedded OFL subset or the metric stack |
| Copy buttons and overflowing commands printed | 234/233/117 px of commands lost in the PDF (H4) | `.copy` hidden in print, `pre-wrap` |
| Dark tokens printed | washed-out headings (H4) | light tokens forced in print |
| SVG letterboxed in a flex board | 182/190/168 screen px bands (about 145-165 design px), labels at 6.6-9.8 px (H5) | viewBox in canvas px, `height:auto` |
| Hex copies of tokens in SVG | colours drift from the theme | classes and CSS variables |
| `.hero .strip div` style selectors | rules leak into nested parts (H7) | child selectors |
| Pills that wrap; 79 `style` attributes | broken chips, tokens bypassed (H7) | `nowrap`, utility classes |
| Theme restored at the end of body | flash of the wrong theme (H6) | head script before CSS |
| `replaceState` for every move | Back leaves the deck (H6) | push for jumps |
| Equal-height cards with `margin-top:auto` | about 200 px dead gap per card (G5) | cards sized to content |
| «3-2-1» left to wrap in body text | Chromium breaks «3-2-» / «1» after a hyphen | `span.nw`; not U+2011 (no Liberation Sans glyph) |
| Image as a relative `src` or a raw `#` in an SVG data URI | the sent file shows no image | `inline_media.py --apply` |

## Verify before done

`scaffold_deck.py` dry run reviewed, then `--apply` → every `data-todo` filled →
`inline_media.py deck.html` reports 0 images to inline →
`node <deck-review>/scripts/html_deck_lint.mjs deck.html out --fonts both` →
`node <deck-review>/scripts/pixels.mjs out/png out` →
`python3 <deck-review>/scripts/deck_lint.py --plan deck-plan.json --metrics out/metrics.json --pixels out/pixels.json --out out`
→ repeat until 0 критично and every бажано is fixed, refuted on the PNGs or accepted by the user in
writing, at most P2 `iterations_max` rounds (`deck-review` stop rule) → open the contact sheet and every
PNG → `out/print.pdf` pages equal slides → `out/metrics.json` `deck.presenter` shows `available` true,
`transport` `postMessage` and `follow_ms` within H6 → `git diff` matches intent. Engine noise follows the
`deck-review` closure rule (fixtures/expected.json `clean_noise`): a finding refuted on the PNGs closes as
«хибне спрацювання» without acceptance; real noise kept on purpose, such as D2 from the 15 pt terminal title
on code-step slides, is put to the user once as a group.

Say what was not verified: the presenter machine's own fonts when none are embedded, the projector's
colours, the real room, and a hands-on S rehearsal on the presenting machine, which the user does.
