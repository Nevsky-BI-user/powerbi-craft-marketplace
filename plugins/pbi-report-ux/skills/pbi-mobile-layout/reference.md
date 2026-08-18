# pbi-mobile-layout — reference

Detailed math, grounded JSON shapes, and rationale that don't fit in SKILL.md's word budget.

## 1. Worked vertical stack (323 pt wide, portrait, top-to-bottom)

Per Microsoft Learn (§6), the mobile-layout canvas max screen width is **323 pt**, and a default margin is auto-included — set every full-width visual to the full 323 pt, do NOT reserve side margins. There is **no fixed canvas height**: devices vary and the page scrolls vertically, so design the stack by priority, not to a height total.

```
323 pt  hero KPI card     (height ≥ 100 pt — "M" min)
  8 pt  gap
323 pt  supporting chart  (height ≥ 180 pt — "L" min)
  8 pt  gap
323 pt  supporting table  (height ≥ 270 pt — "XL" min for table/matrix)
```

Width is a constant 323 pt (single column, no exceptions). Keep ≥ 6–8 pt between visuals (one arrow-key press). Use Microsoft's minimum recommended sizes as height FLOORS — XL 323×270, L 323×180, M 323×100, S 158×100 (pt) — going smaller truncates content and forces an in-visual scrollbar. If only 1 supporting visual is needed, give it more height rather than splitting into two cramped ones. Drop, don't shrink.

## 2. Ground-truth JSON shape (verified against a real production `report.json`)

Every `visualContainer.config` (a JSON string) carries a `layouts` array. The desktop position is always the entry with `id: 0` — confirmed pattern across every visual scanned in a production PBIP report:

```json
"layouts": [
  {
    "id": 0,
    "position": { "x": 0, "y": 0, "z": 1000, "width": 695, "height": 706, "tabOrder": 1000 }
  }
]
```

**What is NOT verified in this repo's research:** the `id` value Desktop assigns to a phone-layout position when a Mobile layout is authored for that visual. No scanned report (including the production reference report) has an authored Mobile layout, so no second `layouts[]` entry has ever been observed here. Do not invent this number (BRIEF F2). Resolution order:

1. Grep the target report for a visual whose `config` contains `"layouts":[{"id":0,...},{"id":<N>,...}]` (two entries) — reuse the observed `<N>` and the same JSON shape for other visuals on that page.
2. If no page in the target report has one, open the report in Power BI Desktop, use **View → Mobile layout** to drag the curated visuals onto the phone canvas, save, then read back the generated `id` — now it is ground truth for this repo.
3. Only as a last resort, delegate to `powerbi-visuals` and flag this exact caveat so it doesn't silently guess either.

A visual intentionally excluded from mobile simply keeps its single `id: 0` entry — no explicit "hide" flag is needed or has been observed.

## 3. Touch-target standard, sourced

DESIGN-TOKENS §3.2 sets the Power BI desktop hit-target floor at 24 px (WCAG 2.2 minimum) with a 32 px standard — sized for mouse/trackpad precision. Phone canvases need more: **Apple Human Interface Guidelines** recommend a 44×44 pt minimum tap target; **Material Design** recommends 48×48 dp. This skill's 44 px floor sits at the intersection of both and comfortably clears WCAG's AAA 44×44 target-size guidance. Apply it to every interactive control placed on the mobile canvas (buttons, in-canvas slicer chips) — cards and charts that are view-only don't need it.

## 4. Filters on the phone canvas

The Power BI mobile app (iOS/Android) has its own native **Filters** icon in the app chrome, independent of any in-canvas slicer — it surfaces report/page/visual-level filters without consuming canvas space. Default recommendation: rely on it and skip an in-canvas slicer entirely. Only add one in-canvas slicer when a single control is central to the page's task (e.g., a date-range picker the user is expected to touch immediately) — keep it to exactly one, full 323 pt width, header collapsed if the label is obvious from context.

## 5. Orientation and device fallback

Mobile layout is authored **portrait-only** in Desktop; there is no separate landscape phone canvas to design. On a tablet, or a phone rotated to landscape, the Power BI mobile app falls back to rendering the desktop-designed layout responsively — this skill's guidance does not apply there; use `pbi-page-layout` for that experience instead.

## 6. Source — phone-canvas dimensions (authoritative)

Canvas width, margin behavior, spacing floor, and minimum visual sizes above are from Microsoft Learn, **"Best practices for creating mobile-optimized reports"**:
<https://learn.microsoft.com/power-bi/create-reports/power-bi-create-mobile-optimized-report-best-practices>

- "**323 pt is the maximum screen width on the mobile layout canvas**" (stated twice).
- Full-width visuals extend to 323 pt; "a default margin is automatically included … so there's no need to reserve extra space."
- Minimum recommended visual sizes (pt): XL 323×270, L 323×180, M 323×100, S 158×100.
- Space visuals "at least six to eight points" apart; portrait, top-to-bottom flow; heights vary by device (page scrolls) — no fixed canvas height.

The phone canvas is a **distinct coordinate space** (pt, max 323 wide), NOT the 1280×720 px desktop grid in `DESIGN-TOKENS.md` / `theme-visuals.md` (neither documents a phone dimension). Do not reuse desktop px canvas figures here. This §6 corrects a prior unsourced `360×640 / 328 px` figure.

## 7. Mobile layout is a SECOND view state, not a resized page

The Power BI mobile layout is a **second state of the same report page** — one report, one model, one set of filters, two rendered views. Desktop switches between them with the **View → Mobile layout** toggle (a phone/PC switch), and the mobile app shows the phone view on phones, the desktop view on tablets. Resizing the desktop page to `360×720` (or any small size) is **NOT** a mobile layout — it is just a small desktop page, and the mobile app still renders it as the desktop view. This was a real production error: an agent shrank the page and called it "mobile"; the user corrected that mobile layout means the toggle/second state, not a smaller page.

**The phone state IS hand-authorable in enhanced PBIR** — it lives in a per-visual **sibling file**, not inside `page.json` or `visual.json`. Every visual that appears on the phone gets its own `mobile.json` next to its `visual.json`:

```
pages/<pageId>/visuals/<VisualName>/visual.json    ← desktop position (unchanged)
pages/<pageId>/visuals/<VisualName>/mobile.json    ← phone position (this file)
```

```json
// pages/<pageId>/visuals/<VisualName>/mobile.json — ground truth generated by Desktop
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainerMobileState/2.5.0/schema.json",
  "position": { "x": 0, "y": 137, "z": 2000, "height": 100, "width": 158, "tabOrder": 0 }
}
```

Rules verified empirically (Power BI Desktop 2.155, **View → Mobile layout → Auto-create** run on a KPI-cards page):

- Schema is `visualContainerMobileState/2.5.0`; the only payload is one `position` object (`x`, `y`, `z`, `height`, `width`, `tabOrder`) — the same coordinate keys as a Legacy `layouts[]` entry.
- The phone canvas is **~320 pt** wide (within the 323 pt max in §6), portrait, and scrolls vertically — `y` edges were observed out past ~670.
- `page.json` carries **no** mobile key. The phone layout simply IS the set of `mobile.json` files present on that page.
- A visual with **no** `mobile.json` sibling is **hidden** on the phone. Excluding a visual from mobile = not writing its `mobile.json` (there is no separate hide flag).
- The earlier "no mobile properties at all" claim came from inspecting the wrong schemas: `page/2.1.0` and `visualContainer/2.9.0` genuinely have none, but the phone state lives in its own `visualContainerMobileState` file beside the visual.

Even though it is hand-authorable, **prefer to generate it in Desktop** (View → Mobile layout → Auto-create), save, and read the files back (BRIEF F2): Desktop assigns `x`/`y`/`z`/`tabOrder` sensibly, so reading back gives ground-truth coordinates instead of invented ones. In **PBIR-Legacy** the phone position is instead a second `layouts[]` entry (`id` ≠ 0) per §2 — the same "generate and read back" rule applies.
