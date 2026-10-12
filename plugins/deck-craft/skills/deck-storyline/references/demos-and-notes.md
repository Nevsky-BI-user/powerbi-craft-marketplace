# deck-storyline: demos, speaker notes and rehearsal reference

> Demo choreography (entrance, proof, exit, fallback), the speaker-notes specification, the reading
> and handout variant, and rehearsal. Lesson L06 with evidence from a 52-slide vendor platform deck
> ("ref"): four demo posters back to back (19-22) with no recap; an entrance with no exit (31-33), after
> which 34 changes topic and template; raw stills (47, 49, 51) running into the close; demo stills and
> posters make up about 21% of its slides (11 of 52). Capture rules for the stills (S1-S6) belong to
> `slide-design`; numbers belong to `deck-review` references/rubric.md.

## §1. The demo triple (N6)

| Role | Archetype | Plan fields | What the slide shows | Checks |
|---|---|---|---|---|
| entrance | `demo-divider` | `demo {id, role: entrance, minutes}`, `proof_of` | an outcome title that says what to watch for (L06), the deck's demo pill, the concept's icon or colour carried over; the «дивіться на ...» cue goes in the notes | N6, T1 `demo_divider_words_max`, N5 |
| proof | `demo-still` | `demo {id, role: proof}`, `media[]`, `proof_of` | the result moment with a «що помітити» caption and the demo marker | N6, S1-S6 |
| exit | `demo-recap` | `demo {id, role: exit}` | three numbered steps or one outcome sentence | N6, N8, §13 `steps_max` |

- One entrance, at least one proof, one exit, in that order; `demo.minutes` on the entrance is the time
  box and N12 subtracts it from the slot.
- The concept the demo proves comes directly before the entrance; the entrance and the stills carry its
  id in `proof_of` (N11).
- Never two demos without an exit between them. The exit is what the audience remembers and the bridge
  back to talk density (N8 `bridge_words`).
- `media[]` (`file`, `native_px`, `ui_px`, `placed_pt`) lets the PDF path compute the effective UI
  text size (S1) without the HTML attributes. The still's anatomy is the `demo-still` entry of
  `slide-design` references/archetypes.md.

From `assets/deck-plan.example.json`, slides 7-10:

| n | Archetype | Role | Title |
|---|---|---|---|
| 7 | `concept` | | «Сейф шифрує паролі ще на ноутбуці» |
| 8 | `demo-divider` | entrance, 3 min | «Відновлюємо доступ за 2 хвилини» |
| 9 | `demo-still` | proof | «Користувач сам повертає собі доступ» |
| 10 | `demo-recap` | exit | «Три кроки повертають доступ без заявки» |

## §2. Before the talk: demo checklist

| Item | Why | Source |
|---|---|---|
| A demo account with synthetic data | nothing on screen needs scrubbing live or in the stills | S4, L56 |
| App zoom at 150-200% for the live part and every capture | UI text readable from the room and in the PDF | S1, L53 |
| Notifications, chat pop-ups and trial banners off | they are on the scrub list and steal the result moment | S4, L56 |
| The proof still captured in advance at the result moment | it is the PDF record and the first fallback | S2, L54, L06 |
| A recorded clip as the second fallback, its poster the result frame | a failed live demo still proves the claim | S2, L54 |
| The time box and a hard-stop cue in the entrance notes | the demo cannot eat the next part | N6, N12 |
| A fail line in the notes | the speaker knows what to say before it is needed | L06 |

A reset path back to the starting state makes the rehearsal and the live run reach the same result; it
is a house practice, not a measured rule. Login, network and the presenting machine can be checked only
on site: list them as unverified until a rehearsal on that machine.

## §3. Live versus PDF

- In a deck that will be sent as a PDF (`talk+appendix`, `reading`), the still or the video poster is
  the only record of the demo, so it shows the result moment, a caption and the demo marker (S2, S6).
- An empty-state or setup-state poster teaches the PDF reader nothing: the ref's posters 19-22 show
  setup or empty states, and two of them are near-identical.
- Step-by-step frames that do not fit the main flow go to the appendix as recap frames for the PDF
  reader (`references/arc-and-pacing.md` §2).

## §4. Demo timing

- The entrance slide's `minutes` equals `demo.minutes`; the proof and exit slides carry their own short
  minutes.
- If a demo overruns in rehearsal, cut from the next part (move its weakest slide to the appendix), not
  the exit: the recap is the part the audience keeps (L06).

## §5. Speaker notes

Every main slide of a talk carries notes (H6 counts them in an HTML build; `html-deck` puts them in
`aside.notes` and the presenter view, `pptx` in `slide.addNotes()`). Print hides them (H4), so nothing a
PDF reader needs may live only in the notes. Appendix slides carry notes only as backup answers for
questions.

| Field | Content | Source |
|---|---|---|
| Cue | what is on screen, what to click or show | H6 |
| Points | the points to make, as short phrases, not prose to read aloud | `plain-report` for wording |
| Numbers aloud | rounded and said with their base: «три таблиці на один відділ», not «три таблиці» | L18, `data-storytelling` reference.md §3 |
| Transition | one sentence that leads into the next slide's claim | `references/arc-and-pacing.md` §3 |
| Minute mark | cumulative, from the plan minutes: «Позначка 6:00» | N12 |
| Backup | one answer to the likeliest question; for a demo entrance, the fail line | L06 |

Worked example for slide 7 of the example plan:

```text
Слайд 7 · Сейф шифрує паролі ще на ноутбуці
Підказка: на екрані одна схема з трьох блоків (ноутбук, шифр, сервер). Клік не потрібен.
Тези:
- пароль шифрується до того, як покине ноутбук;
- сервер зберігає лише шифр;
- ключ знає тільки користувач.
Перехід: «Як це виглядає для користувача, покаже демо».
Позначка 6:00.
Запасна відповідь на «А якщо користувач забуде головний пароль?»: відновлення покажемо в демо.
```

Bad notes: a paragraph copied from the slide; a number without its base; no minute mark; the only copy
of a link or a caveat the PDF reader needs.

## §6. Reading and handout variant

Set `mode: reading` (or put the pages behind the `appendix-divider` of a `talk+appendix` deck):

- The spoken script becomes visible text within the reading budget (D1 reading `words_max`); split a
  page above it.
- Titles stay assertions within the same T3 budget; a dek is allowed.
- Use the reading archetypes of `slide-design` references/archetypes.md: `kpi-wall` with a measurement
  note, `trap-card`, `setup-step`, `glossary`, `matrix`, `error-log`, `risks`, `summary-card`.
- No demo triple (N6 does not apply in reading mode): a demo becomes a run of `setup-step` pages or
  annotated stills of the result.
- The close becomes a one-sentence `summary-card` plus a links table.

The own 33-slide HTML deck is a model for the structure of a handout: assertion titles, a route with an
audience hint, proof numbers with a measurement note, a summary card and a links table. Its density and
type size fail even reading mode: a 226-word median against N1 reading `median_words_max`, 10 slides
above 250 words against D1 reading `words_max`, and 97% of words at or below 13.6 px, under the Y1
reading floor.

## §7. Rehearsal

1. Run the talk once against a timer and note the actual minute at each part divider next to the plan's
   minute marks.
2. Over time: move the weakest content slide of the longest part to the appendix (`appendix: true`),
   rerun `--plan-only`, rehearse again.
3. Never cut by shrinking text below the mode floor (Y1) or by speaking faster.
4. Report the rehearsal honestly: no script verifies delivery or timing; the lint checks only the
   minutes the plan claims.

## §8. See also

`references/arc-and-pacing.md` · `references/titles-and-copy.md` · `references/deck-plan.md` §4 (demo
and media fields) · `slide-design` references/archetypes.md (`demo-divider`, `demo-still`,
`demo-recap`, reading archetypes) · `html-deck` (aside.notes, presenter view) · `pptx` (addNotes) ·
`plain-report` (notes prose).
