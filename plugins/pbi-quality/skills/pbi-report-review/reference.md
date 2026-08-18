# pbi-report-review — Scripts & Worked Case

Companion to `SKILL.md`. Property names (`visualContainerGroups`, `visualContainers`,
`options.targetVisualNames`, `suppressData`) are owned by `powerbi-bookmarks` — verify
against a real `report.json` before trusting these snippets on a different schema version.

## 1. Full visual inventory (mandatory Pre-flight step 2)

Works for **PBIR-Legacy** (`config` is a JSON *string* inside `report.json`) and adapts to
**PBIR enhanced** (`definition/pages/<page>/visuals/<id>/visual.json`, one file per visual —
just glob and read `visual.visualType` per file instead of walking `sections`).

```python
import json
from collections import Counter

d = json.load(open(REPORT_JSON, encoding='utf-8'))
section = next(s for s in d['sections'] if s['name'] == TARGET_SECTION_ID)

def walk(containers, counts, rows, parent=None):
    for vc in containers:
        sv = vc.get('singleVisual') or vc.get('singleVisualGroup')
        vtype = (vc.get('singleVisual', {}) or {}).get('visualType') \
                or ('group' if 'singleVisualGroup' in vc else 'unknown')
        counts[vtype] += 1
        rows.append((vc['name'], vtype, parent, vc.get('singleVisual', {}).get('display')))
        if 'children' in vc:
            walk(vc['children'], counts, rows, parent=vc['name'])

counts, rows = Counter(), []
walk(section.get('visualContainers', []), counts, rows)
for vtype, n in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"{n:3d}  {vtype}")
print("TOTAL:", sum(counts.values()))
```

Run this for the target page AND the declared reference page. Paste both tables as evidence
— "I looked at the page" is not an inventory; this printed, counted list is.

## 2. Bookmark symmetry checker (mandatory whenever bookmarks are touched)

Compares every sibling bookmark in a nav group on one section: counts + id-sets of touched
`visualContainerGroups` (vcg) and `visualContainers` (vc), length of
`options.targetVisualNames` (tvn), and `options.suppressData`.

```python
import json

d = json.load(open(REPORT_JSON, encoding='utf-8'))
cfg = json.loads(d['config'])
SEC = TARGET_SECTION_ID

def collect(bookmarks, out):
    for b in bookmarks:
        es = (b.get('explorationState') or {}).get('sections', {}).get(SEC)
        if es is not None:
            vcg = set(es.get('visualContainerGroups', {}).keys())
            vc  = set(es.get('visualContainers', {}).keys())
            opt = b.get('options') or {}
            tvn = set(opt.get('targetVisualNames', []))
            out.append({
                'name': b.get('displayName'),
                'vcg': len(vcg), 'vc': len(vc), 'tvn': len(tvn),
                'suppressData': opt.get('suppressData'),
                'ids': vcg | vc,
            })
        if b.get('children'):
            collect(b['children'], out)

rows = []
collect(cfg['bookmarks'], rows)
base = rows[0]
for r in rows:
    mismatch = (r['vcg'], r['vc'], r['tvn']) != (base['vcg'], base['vc'], base['tvn']) \
               or r['suppressData'] != base['suppressData'] \
               or r['ids'] != base['ids']
    flag = '  <-- MISMATCH' if mismatch else ''
    print(f"{r['name']:30s} vcg={r['vcg']:3d} vc={r['vc']:3d} tvn={r['tvn']:3d} "
          f"suppressData={r['suppressData']}{flag}")
```

Any `MISMATCH` line is an open bug — report it even when it's outside the task's original
scope, and even when `isHidden` visibility itself looks correct (that was exactly the case
in the incident below: display was fixed, `suppressData` wasn't).

## 3. Worked case — task #5 (`docs/audits/task5-audit.md`)

Task: (1) fix a bookmark so one subtab doesn't leak onto others; (2) "very deeply rework
the design, listing every possible improvement." Agent reported success 9/9, self-defined.
Actual diff: 8 lines — one bookmark option changed, seven KPI-card style tweaks.

Independent re-audit found, in the SAME diff's blast radius:

| Finding | What the self-grade missed |
|---|---|
| B1 (critical) | The bookmark fix set `isHidden` correctly but was the only sibling of 5 missing `options.suppressData:true` — it silently replayed a sibling bookmark's captured slicer/filter state on every click. The symmetry check in §2 catches this in one run; a display-only check does not. |
| B2 (major) | A toggle button's state was captured in only 1 of 5 sibling bookmarks — it gets stuck hidden after first use. Same class of bug as B1: caught by comparing bookmarks as a set, not one at a time. |
| D1–D2 (critical) | A histogram series rendered white-on-white (invisible); a drill-table's text was `#EDEDED` on white (unreadable). Both pass "JSON parses." Neither survives resolving each fill color against its actual background — not part of the self-graded 9. |
| D3–D14 | Section background, table headers, slicer style, title weight, and grid alignment on the "reworked" subtab still didn't match the four sibling subtabs it was supposed to match — because no reference-page inventory/comparison was ever run. |

Lesson encoded in `SKILL.md`: inventory + count first, diff every sibling bookmark as a set
(never one at a time), and resolve colors against their real background instead of trusting
"JSON parses" as a stand-in for "renders correctly."
