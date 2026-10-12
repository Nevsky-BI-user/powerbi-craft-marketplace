# slide-design: screenshots, devices and components

> Everything that is not running text: screenshots and demo stills (effective size, capture, scrub,
> annotation, crop), devices and diagrams (meaning map, relationship grammar, architecture maps, live text),
> components (code line, status pill, demo marker, stat tile, URL pill) and stage tables. Numbers belong to
> `deck-review` references/rubric.md (check IDs in brackets). Evidence: a 52-slide vendor platform deck
> ("ref N") and a 33-slide own HTML reading deck ("own N"); ratios computed with the
> `pbi-color-accessibility` reference.md §1 formula.

## §1. Effective size (S1; L53, L74)

A screenshot is read at its **effective size**, not at the size its text layer reports:

```
effective pt = UI px x placed width pt / native width px        (PDF, pptx: plan.slides[].media)
effective px = ui_px x box.w / native_width;  pt = px x 0.75    (HTML: img[data-ui-px][data-native-width])
```

`UI px` is the size of the smallest text the claim needs, in capture pixels. A HiDPI capture doubles both UI
px and native width, so it changes nothing; only app zoom and cropping move the result. Minimum 9 pt
(`eff_min_pt`); below it add a crop, a zoom inset or a callout of at least 14 pt.

| Capture | UI px | Native px | Placed | Effective | S1 |
|---|---|---|---|---|---|
| full window, slide width | 12 | 1920 | 960 pt | 6.0 pt | fails |
| same at 200% app zoom | 24 | 1920 | 960 pt | 12.0 pt | passes |
| full window framed at 60% | 12 | 1920 | 576 pt | 3.6 pt | fails |
| full window in the 7-column media zone | 12 | 1920 | 508 pt | 3.2 pt | fails |
| same at 200% app zoom | 24 | 1920 | 508 pt | 6.35 pt | fails |
| panel crop at 150% zoom | 18 | 960 | 508 pt | 9.5 pt | passes |
| example plan `demo-still` | 28 | 1600 | 720 pt | 12.6 pt | passes |

In the 7-column zone of a `feature-shot` a 1920 px capture needs 34 px UI text, a 960 px panel crop 17 px:
zoom and crop, never one alone. **Fix order:** app zoom 150-200%, crop to the panel that proves the claim, a
zoom inset, a callout of at least 14 pt (S1), built at 18 pt so the S3 callout minimum holds too.

Evidence: ref full windows render UI at about 7-9 pt (11, 19, 20), framed shots at 60% width at 4-5 pt (46,
48, 50), ref 33 at about 4 pt; the crop on 42 and the zoomed capture on 49 reach 9-10 pt. Ref 19-24 report
16-29 pt in the text layer while the visible content is 7-9 pt raster, so compute, never read the layer.

## §2. Capture checklist (L53, L54, L56, L57)

Answer each with yes or no before the capture is placed:

- Demo account with synthetic data the audience would recognise as plausible?
- App zoom at 150-200%, window sized to the panel that proves the claim?
- The result moment on screen (output, answer, chart), not a setup, landing or empty state?
- App theme matching the slide family (or framed and dimmed per C4)?
- Notifications off, cursor hidden, no terminal or browser chrome that the claim does not need?
- Native width and UI px written down for `data-native-width` / `data-ui-px` or `plan.slides[].media`?

## §3. Scrub checklist (S4; L56)

Every item yes or no on every capture; one "no" is a критично finding:

- personal names, avatars, greetings («Доброго ранку, ...»);
- owner, author or assignee columns;
- tenant, workspace, organisation or project names;
- sensitivity or classification labels;
- trial or licence banners;
- notification counts;
- timestamps and dates that are not part of the claim;
- cursors and hover states;
- incidental terminal notices (for example, about auto-approved permissions);
- URLs carrying IDs, tokens or tenant names;
- e-mail addresses and phone numbers.

Re-capture with synthetic data rather than blur: blur on short strings can be reversible, and a blurred block
still tells the reader something was hidden. Evidence: ref shows personal names or greetings on 5 slides,
owner columns on 3, classification labels on 4, trial banners on 3, cursors on 5, and a terminal notice about
auto-approved permissions on 1.

## §4. Annotation (S3, V3; L55, L45)

- **One highlight** per screenshot: a stroke of at least 3 pt in the `hl` colour (used nowhere else in the
  deck; #CC4410 holds 4.77 on white and 3.88 on the void board), covering 10-25% of the image. HTML: `.hl`
  inside `figure.shot`.
- **At most 3 callouts** at 18 pt or more, each within 12 pt of its anchor or on a leader line (V3). HTML:
  `.callout`.
- **Number badges** map the slide's bullets to image regions; the badge numbers reappear in a `demo-recap`.
  Badge digits are text: `hl-ink` on `hl`, white 4.77 (`visual-system.md` §6).
- Evidence: ref 39 boxes about 25% of the image (good); ref 27 uses one outline and 3 arrows (good); ref 37 a
  20x25 pt box on a 540 pt image (invisible); ref 11, 33, 43 none.

## §5. Crop and placement (S5, G6; L57, L28)

- One screenshot per slide, cropped at UI boundaries (never mid-word), filling its zone in at least one
  dimension within 2 pt, in the slide's theme.
- No collage, no letterbox, no device frame that eats width (a frame at 60% width is the 3.6 pt row in §1).
- In a text plus image split, the image top and bottom align with the text zone within 2 pt (G6).
- Evidence: ref 38 overlaps two shots, ref 39 leaves about 87 pt of letterbox, ref 33 a letterbox strip, ref
  27 cuts a word at the edge, ref 41 puts dark UI on a cream slide.

## §6. Demo stills (S2, S6, V4; L54, L58)

- Show the **result moment** of the claim; a video bound for a PDF gets the result frame as its poster,
  because the PDF shows only the poster.
- Every still has a visible title or a caption of at most 10 words plus the deck demo marker; a title is
  never hidden behind the image.
- The still is the proof step of the demo triple (entrance `demo-divider`, proof `demo-still`, exit
  `demo-recap`, sequence owned by `deck-storyline`).
- Evidence: ref 19 and 21 show setup cells with 35-40% blank and are near-identical; ref 22 an empty editor;
  ref 40 a landing page; ref 44 an empty canvas; good: ref 39 (boxed output), ref 41 (prompt plus the
  resulting chart). No title on ref 11, 31, 33, 43, 47; titles behind images on 49 and 51; the demo divider
  of ref 32 is never reused for later demos.

## §7. Device meaning map (V1; L43)

- Each device keeps **one meaning** per deck. Icons come from the token sheet `icons` map, and plan lists
  name them (`lists[].icon`), so a concept carries one icon everywhere.
- **Literal reading test:** read each icon as a word next to its claim. The token sheet maps `vault` to a
  closed `lock`; ref 10 illustrates a security claim with an open padlock, ref 9 network isolation with a
  chart glyph.
- **Numbers, steppers and rails only for ordered sequences.** Ref numbered rings mean steps (3), problems (4)
  and features (9); dot rails mark unordered benefits on 44, 48, 50; one concept gets 4 icons on 4 slides and
  a magnifier stands for 3 concepts. The own deck keeps one meaning per marker (good).

## §8. Relationship grammar and labels (V2, V3; L44, L45)

| Relation | Draw it as | Evidence |
|---|---|---|
| composition | "+" between equal shapes | ref 52 (good) |
| hierarchy | a bracket | ref 52 (good) |
| flow | an arrow in reading direction, connectors at card centres (G4) | ref 34 misses centres by about 88 pt |
| result | a band traced visibly to every input | ref 12 links its result to neither input |

Label every grouping device and every edge that encodes a relation; a group label may break its border in
fieldset style (ref 29, good). Ref 3 has an unlabelled dashed box, ref 16 undirected edges; own 9 lets labels
collide with box edges and a connector cross a label.

## §9. Architecture maps (V6, N5; L48, L05)

- At most 12 boxes or logos, flow in reading direction, outcomes as the largest text, exactly one highlighted
  zone.
- The highlight must be found within 1 s on a 25% thumbnail: run that test on the `deck-review` contact sheet.
  A 2 px outline is too subtle (ref 29); fill the zone with `accent-fill` or dim the rest to about 2:1 (C6).
- A zoom repeats the map layout with 0 pt drift and carries the highlighted element to the demo divider (N5).
- HTML: `.a-map` with `[data-box]` or `.box`, the highlight as `.hl`.
- Evidence: ref 6 carries 22 logos and 96 words, mostly at 7-8 pt, with outcomes smallest; ref 7 carries 25
  images; own 8-9 set labels at 7.8-8.8 px.

## §10. Live text only (V4, Y1; L46, L47, L67)

- Every word is live text inside the canvas: diagrams in HTML/SVG or native pptx shapes, never a picture of
  words, never a title parked off-canvas or under an image.
- A slide outside the `raster_exempt` group with 5 or fewer live words plus an image is a raster suspect.
- SVG text is judged at its effective size (font-size x SVG scale) against the Y1 floor; match the viewBox to
  the board aspect and keep long captions in HTML under the SVG (`html-deck` H5).
- Restyle imported diagrams to the host family (V5); a third-party logo is flattened to one colour.
- Evidence: ref 16 bakes about 170 words into an image and parks its title at y=553.1 on a 540 pt page; ref
  28 parks a title at y=576; ref 23 has 0 live words. Own deck diagrams are live SVG, but letterboxing shrinks
  their text to 6.6-9.8 px.

## §11. Components (V7, V8, S6, T7, N10, K1, K3; L19, L21, L18, L59, L61)

**Code line** (V7). One mono family deck-wide; 18 pt (24 px) in talk, 24 pt for a hero line, 11 pt in
reading; straight quotes only (curly quotes are критично because copy-paste breaks); colour only on the
tokens that matter (ref 17 colours only namespace and method). Capacity at a 0.6 em mono advance, inside a
code block with 15 pt (20 px) padding per side as in the `html-deck` template: at 18 pt about 79 characters
across the 888 pt content box, 44 in the 7-column zone, 30 in the 5-column zone. A longer
command wraps or moves to the appendix; nothing overflows horizontally (`html-deck` H4; own 13, 14, 18 clip
commands by 234, 233 and 117 px).

**Status pill** (V8). One component: one size (14 pt / 20 px in the token sheet), sentence case, never
wrapping, one position on every feature slide; a distinct fill per state; label at least 4.5:1; roadmap
claims carry an as-of date. Plan field `slides[].status {state, as_of}`.

| State | Label | Fill / ink | Ratio |
|---|---|---|---|
| `ga` | «Доступно» | #1F7A50 / #FFFFFF | 5.31 |
| `preview` | «Тестування» | #D7EAF6 / #0B4F70 | 7.18 |
| `planned` | «Заплановано» + «станом на жовтень 2026» | #E3E8EC / #41586A | 6.02 |

Evidence: ref encodes status as an inline bullet, a 16 pt pill and a 12 pt pill; its GA and preview pills
share #6BE9BD; ref 26 names a future month with no as-of date; own pills at 10 px wrap on slide 10.

**Demo marker** (S6). `.demo-pill` labelled «Демо» in `accent-fill` with `on-accent` text (10.96), on the demo
divider and on every demo still.

**Stat tile** (T7). `.stat > .v .l .m`: the value at the hero size (at least 2x body), a label of at most 6
words, a method line saying the base and how it was measured (own 4 is the model).

**URL pill** (N10). At most 25 characters in a filled pill of at least 18 pt on the close or cta slide; full
links go on the close or in the appendix (the notes may repeat them, never as the only copy: print hides
notes, H4), and body text never underlines links.

**Page number** (K1) and **series frame** (K3): `visual-system.md` §8.

## §12. Stage tables and shape as hero (D3, D4, C2; L51, L52, L37)

- A projected comparison table holds at most 6 rows by 3 columns with cells at 14 pt or more; repeated cell
  prefixes become column subheads; the title states the answer the table supports. A `ref-table` follows its
  own budget (at most 8 rows on stage). One header fill at 4.5:1 or more (C2).
- Evidence: ref 14 shows 9 rows of 9 pt cells and repeats its two scope prefixes about 13 times; the own deck's
  7 x 3 error log is fine in reading mode.
- **Shape as hero:** when the point is a shape (a tangle, a sprawl, a fan-out), the shape is the hero and at
  most 4 takeaways of 20 pt or more sit beside it, linked by numbered callouts. Labels inside the shape are
  exempt from the Y1 floor; declare it (`shape: true` in the plan, `[data-shape]` in HTML). Ref 4 shows the
  shape with 4 pains at 20 pt (good) but never links them.
