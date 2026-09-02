# -*- coding: utf-8 -*-
"""Filter-panel layout engine + invariant checker.

layout(filters, captions) -> boxes for every panel member, and invariants that
make a clipped caption, a collapsed slicer or a double edge impossible by
construction.

Synthesised from four independent designs; the four
defects the judges found are fixed (D1-D4). Round 2 corrections come from a
render of the generated panel - each is a measured boundary, not a preference:

  C1 caption width: 7*len+32 predicted "Default" fits 88px; it rendered "Defa...".
     Solving a*len+b against five observed fit/clip boundaries leaves a=6,b=48
     (slopes 3-5 are ruled out: a 10pt glyph cannot advance 3px). The CHROME
     term was wrong, not the slope, and the 88px floor was masking it.
  C2 a Between / relative-date slicer needs a DOUBLE cell. With responsive=true
     an undersized slicer does not clip - it collapses to a bare funnel icon,
     which reads as a broken visual. weight() now keys off what the control
     DRAWS, not off whether it is a list.
  C3 R_MAX=4 was a decree. A right-anchored panel over a wide report is cheaper
     tall than wide, so a column may run until it would overflow the PAGE. R_MAX
     is now derived; a second column opens only when the first cannot fit.
  C4 peer buttons (the destructive pair) share the row EQUALLY. Two ghost
     buttons of different widths read as different weights of action.

Round 3 (render of round 2 - "забагато пустого місця"):

  C5 SLOTS LIE. "Double cell = 144" gave the between slicer 144px when its
     content (label + two inputs + track) measures ~90px - 54px of dead space
     the user saw immediately. Cells are now sized in PIXELS per control kind
     (H_KIND), packed by y-cursor; the slot/weight fiction is gone.
  C6 the <=3 / >12 guards are COGNITIVE, so they count F (decisions), not
     weighted geometry. Six list slicers are six decisions, not twelve.

Round 4 (user's manual Desktop edit - adopted as ground truth):

  C7 a shape has TWO shadows. objects.shadow (the shape STYLE shadow) draws
     INSIDE the container and follows the rounded geometry - but it EATS canvas,
     so the visible rect shrinks. visualContainerObjects.dropShadow draws around
     the rectangular container box. For a rounded overlay: STYLE shadow on,
     container shadow off, and the container grows by the shadow margins so the
     VISIBLE rect keeps its size. The 8-grid governs the VISIBLE rect (what the
     eye aligns), not the container box - the container may sit off-grid.
     Margins calibrated by the user's manual alignment at blur 20: L6 R6 T0 B4.

Usage:
    from filter_panel_layout import layout, check
    plan = layout([{'name':'SlicerDate','kind':'between'}, ...], CAPTIONS)
    problems = check(plan)
"""
import math

# --- T(pt): the single source of truth for vertical minimums --------------------
# Measured on this project (incident I-12 + the actionButton chrome finding).
# T_RAW is the measured floor; the layout uses ceil8(T_RAW) so that the legibility
# floor and the 8-grid never contradict each other. Rounding UP can only add slack,
# so no caption can be clipped by the snap.
T_RAW = {8: 32, 9: 36, 10: 40, 12: 44, 14: 48, 18: 52, 24: 64}
T = {pt: int(math.ceil(v / 8.0) * 8) for pt, v in T_RAW.items()}

# --- caption width: w = ceil8(A*len + B), floored at W_MIN_BTN -------------------
# A is the average glyph advance at 10pt mixed-case Latin; B is button chrome
# (padding + the ellipsis reserve). Solved from observed fit/clip boundaries:
#   "Close"(5)@88 fits | "Default"(7)@88 CLIPS | "Clear all slicers"(17)@152 fits
#   "Apply and close"(15)@280 fits | "Restore default"(15)@160 fits
# An ALL-CAPS or wide-glyph caption needs ~1.3x; keep captions short instead.
A_CHAR = 6
B_CHROME = 48

U = 8            # grid unit
P = 24           # panel padding
W_COL = 280      # column width (360 when any label exceeds the char budget)
G_COL = 24       # gap between columns
H_CELL = 64      # 24 label + 32 control + 8 slack
G_ROW = 16
V = H_CELL + G_ROW          # vertical pitch = 80; a w=2 cell is exactly 2V - G_ROW
H_HEAD = 48      # header band = close-button height
G_HEAD = 16
H_CAP = 40       # D1: a 10pt caption textbox may not go below T[10]
G_CAP = 8
H_ACT = 48       # action button height = T[10] + chrome
G_ACT = 24
G_LINE = 24
G_PEER = 24      # gap inside the destructive pair
DEAD = 120       # dead zone isolating destructive actions from the primary
W_MIN_BTN = 88   # a labelled button below ~60px renders its caption as nothing
W_PRIM_MIN = 176
PAGE_W = 1920
PAGE_H = 1080
CONTENT_ORIGIN = 20
CONTENT_R = PAGE_W - CONTENT_ORIGIN
M_BOTTOM = 20    # the panel may not touch the page edge

C_MAX = 3
F_MAX = 12       # cognitive cap: DECISIONS, independent of geometry (C6)

# C7: style-shadow margins. The backdrop's objects.shadow (blur SH_BLUR) draws
# INSIDE the container; the container = visible rect + these margins. Calibrated
# by the user's manual Desktop alignment - ground truth, not derivation.
SH_BLUR = 20
SH_L, SH_R, SH_T, SH_B = 6, 6, 0, 4

# C5: cell height in PIXELS per what the control DRAWS. Measured on renders:
# a dropdown is label 24 + control 32 + slack 8 = 64. A between draws label +
# two inputs + a slider track; calibrated by render bisection: at 64 the whole
# control collapses to a funnel icon, at 96 the TRACK is silently dropped, at
# 120 everything renders, at 144 there is visible dead space -> 120. An open
# list needs visible rows -> 144. H_KIND is a floor, never a suggestion: a
# responsive slicer sheds parts silently instead of clipping.
H_KIND = {'between': 120, 'range': 120, 'relativeDate': 120,
          'list': 144, 'hierarchy': 144, 'chiclet': 144}


def ceil8(v):
    return int(math.ceil(v / 8.0) * 8)


def floor8(v):
    return int(math.floor(v / 8.0) * 8)


def btn_w(caption, minimum=W_MIN_BTN):
    """Engineering floor AND text fit - two separate tests, both must pass."""
    return max(minimum, ceil8(A_CHAR * len(caption) + B_CHROME))


def cell_h(kind):
    """C2+C5: keyed off what the control DRAWS, in pixels."""
    return H_KIND.get(kind, H_CELL)


def col_budget(y_panel, cap):
    """C3: pixels a column may spend before the panel overflows the page.
    Worst-case chrome (two action lines) so the answer never has to be revised
    after the action row is measured."""
    gy0 = P + H_HEAD + G_HEAD + cap * (H_CAP + G_CAP)
    chrome = gy0 + G_ACT + 2 * H_ACT + G_LINE + P
    return PAGE_H - y_panel - M_BOTTOM - chrome


def pack(filters, budget):
    """Column-major, strict priority order (D2): a cell that does not fit the
    column's remaining budget starts the next column; the leftover space stays
    empty. Returns [(col, y_offset, h)] per filter, or None on overflow."""
    out, j, y = [], 0, 0
    for f in filters:
        h = cell_h(f['kind'])
        if y and y + h > budget:
            j, y = j + 1, 0
        if h > budget or j >= C_MAX:
            return None
        out.append((j, y, h))
        y += h + G_ROW
    return out


def layout(filters, captions, y_opener=84, h_opener=48, w_opener=120):
    """filters: list of {name, kind}, in priority order. captions: button texts."""
    F = len(filters)

    if F <= 3:                                    # C6: decisions, not geometry
        return {'rejected': 'F<=3: the panel costs a click and buys nothing - '
                            'put the slicers inline in the header band'}
    if F > F_MAX:
        return {'rejected': 'F>%d: keep the most-changed filters here and send the '
                            'rest to the native filter pane' % F_MAX}

    y_panel = y_opener + h_opener + U
    placed = pack(filters, col_budget(y_panel, 0))
    if placed is None:
        return {'rejected': 'packing overflow: filters do not fit %d columns - '
                            'use the native filter pane' % C_MAX}
    C = max(j for j, _, _ in placed) + 1
    cap = 1 if C == C_MAX else 0
    if cap:                                       # captions steal a row of height
        placed = pack(filters, col_budget(y_panel, cap))
        if placed is None:
            return {'rejected': 'packing overflow with captions: use the native '
                                'filter pane'}
        C = max(j for j, _, _ in placed) + 1

    W_panel = 2 * P + C * W_COL + (C - 1) * G_COL
    INNER = W_panel - 2 * P

    # C4: the destructive pair are PEERS - always identical width. Ask what the
    # captions need first, then decide whether that fits beside the primary;
    # deciding the other way round forces a second line that was never needed.
    w_peer = max(btn_w(captions['clear']), btn_w(captions['default']))
    w_prim = max(btn_w(captions['primary']), W_PRIM_MIN)
    one_line = (2 * w_peer + G_PEER + DEAD + w_prim) <= INNER
    lines = 1 if one_line else 2
    if lines == 2:                                # the pair owns the row: split it
        w_peer = floor8((INNER - G_PEER) / 2.0)
    w_clear = w_def = w_peer

    gy0 = P + H_HEAD + G_HEAD + cap * (H_CAP + G_CAP)
    stack_h = max(y + h for _, y, h in placed)    # tallest column, in pixels
    y_act = gy0 + stack_h + G_ACT
    H_panel = y_act + lines * H_ACT + (lines - 1) * G_LINE + P

    x_panel = CONTENT_R - W_panel

    items = [
        {'name': 'backdrop', 'x': 0, 'y': 0, 'w': W_panel, 'h': H_panel,
         'z': 0, 'tabOrder': -1, 'kind': 'shape', 'edge': 'own'},
        {'name': 'title', 'x': P, 'y': P,
         'w': W_panel - 2 * P - W_MIN_BTN - G_ROW, 'h': T[12],
         'z': 1, 'tabOrder': -1, 'kind': 'textbox', 'pt': 12, 'edge': 'none'},
        {'name': 'close', 'x': W_panel - P - W_MIN_BTN, 'y': P,
         'w': W_MIN_BTN, 'h': H_ACT, 'z': 4, 'tabOrder': 1100,
         'kind': 'button', 'pt': 10, 'caption': captions['close'], 'edge': 'own'},
    ]

    # D2 held: pack() already placed column-major in strict priority order,
    # leaving holes rather than reordering (reordering breaks tabOrder == visual).
    for i, (f, (j, y, h)) in enumerate(zip(filters, placed)):
        items.append({
            'name': f['name'], 'kind': 'slicer', 'control': f['kind'],
            'x': P + j * (W_COL + G_COL),
            'y': gy0 + y,
            'w': W_COL,
            'h': h,
            'z': 2, 'tabOrder': 1200 + 10 * i, 'edge': 'none',
        })

    if cap:
        for jj in range(C):
            items.append({'name': 'caption%d' % jj, 'x': P + jj * (W_COL + G_COL),
                          'y': P + H_HEAD + G_HEAD, 'w': W_COL, 'h': H_CAP,
                          'z': 1, 'tabOrder': -1, 'kind': 'textbox', 'pt': 10,
                          'edge': 'none'})

    if lines == 1:
        acts = [('clear', P, y_act, w_clear, 2000),
                ('default', P + w_clear + G_PEER, y_act, w_def, 2010),
                ('primary', W_panel - P - w_prim, y_act, w_prim, 2020)]
    else:
        acts = [('clear', P, y_act, w_clear, 2000),
                ('default', P + w_clear + G_PEER, y_act, w_def, 2010),
                ('primary', P, y_act + H_ACT + G_LINE, INNER, 2020)]
    for name, x, y, w, tab in acts:
        items.append({'name': name, 'x': x, 'y': y, 'w': w, 'h': H_ACT,
                      'z': 3, 'tabOrder': tab, 'kind': 'button', 'pt': 10,
                      'caption': captions[name], 'edge': 'own'})

    # C7: the group/container box wraps the visible rect in the shadow margins;
    # members are container-relative, so they shift by (SH_L, SH_T); the backdrop
    # fills the whole container and carries the style shadow.
    group_box = {'x': x_panel - SH_L, 'y': y_panel - SH_T,
                 'w': W_panel + SH_L + SH_R, 'h': H_panel + SH_T + SH_B}
    emit = []
    for it in items:
        e = dict(it)
        if it['name'] == 'backdrop':
            e['x'], e['y'] = 0, 0
            e['w'], e['h'] = group_box['w'], group_box['h']
        else:
            e['x'] += SH_L
            e['y'] += SH_T
        emit.append(e)

    return {
        'F': F, 'C': C, 'cap': cap, 'lines': lines, 'stack_h': stack_h,
        'W_panel': W_panel, 'H_panel': H_panel,          # VISIBLE rect (grid law)
        'x_panel': x_panel, 'y_panel': y_panel,
        'group_box': group_box,                           # container (may be off-grid)
        'opener': {'x': CONTENT_R - w_opener, 'y': y_opener,
                   'w': w_opener, 'h': h_opener, 'tabOrder': 200},
        'items': items,                                   # visible coordinates
        'emit': emit,                                     # container-relative, on disk
        # D3: bookmark scope counts VISUALS
        'targetCount': 1 + 1 + 1 + C * cap + F + 4,
    }


def check(plan):
    """Any failure here is a defect that would ship as a clipped caption, a
    collapsed slicer, a double edge, an overlap or a broken keyboard path."""
    if 'rejected' in plan:
        return []
    p, out = plan, []
    W, H = p['W_panel'], p['H_panel']

    for it in p['items']:
        if it['kind'] == 'textbox' and it['h'] < T[it['pt']]:
            out.append('I1 %s: h=%d < T[%dpt]=%d'
                       % (it['name'], it['h'], it['pt'], T[it['pt']]))
        if it['kind'] == 'button' and it['h'] < T[it['pt']] + 8:
            out.append('I2 %s: button h=%d < %d'
                       % (it['name'], it['h'], T[it['pt']] + 8))
        if it['kind'] == 'button':
            need = btn_w(it.get('caption', ''))
            if it['w'] < need:
                out.append('I3 %s: w=%d < %d needed for "%s"'
                           % (it['name'], it['w'], need, it.get('caption')))
        if it['name'] != 'backdrop' and (it['x'] + it['w'] > W or it['y'] + it['h'] > H):
            out.append('I4 %s: %d..%d x %d..%d outside %dx%d'
                       % (it['name'], it['x'], it['x'] + it['w'],
                          it['y'], it['y'] + it['h'], W, H))
        if it['x'] % 8 or it['y'] % 8 or it['w'] % 8 or it['h'] % 8:
            out.append('I5 %s: not on the 8 grid (%d,%d,%d,%d)'
                       % (it['name'], it['x'], it['y'], it['w'], it['h']))
        # I11 exactly one edge per visual: the container border and the visual's
        # own outline are independent, and both on is the double border.
        if it.get('edge') not in ('own', 'none'):
            out.append('I11 %s: edge ownership undeclared' % it['name'])
        # I12 a slicer below its control's pixel floor does not clip -
        # responsive mode silently collapses it to a funnel icon.
        if it['kind'] == 'slicer':
            need_h = cell_h(it['control'])
            if it['h'] < need_h:
                out.append('I12 %s: %s control needs h>=%d, got %d (it will '
                           'collapse to a funnel icon, not clip)'
                           % (it['name'], it['control'], need_h, it['h']))

    body = [i for i in p['items'] if i['name'] != 'backdrop']
    for a in range(len(body)):
        for b in range(a + 1, len(body)):
            u, v = body[a], body[b]
            if (u['x'] < v['x'] + v['w'] and v['x'] < u['x'] + u['w']
                    and u['y'] < v['y'] + v['h'] and v['y'] < u['y'] + u['h']):
                out.append('I6 overlap: %s vs %s' % (u['name'], v['name']))

    by = {i['name']: i for i in body}
    if p['lines'] == 1 and all(k in by for k in ('default', 'primary')):
        gap = by['primary']['x'] - (by['default']['x'] + by['default']['w'])
        if gap < DEAD:
            out.append('I7 dead zone %d < %d' % (gap, DEAD))
    # I13 the destructive pair are peers: same width, same row, same styling.
    if all(k in by for k in ('clear', 'default')):
        if by['clear']['w'] != by['default']['w'] or by['clear']['y'] != by['default']['y']:
            out.append('I13 peer buttons differ: clear %dx%d@%d, default %dx%d@%d'
                       % (by['clear']['w'], by['clear']['h'], by['clear']['y'],
                          by['default']['w'], by['default']['h'], by['default']['y']))

    fl = [i for i in body if i['kind'] == 'slicer']
    order = sorted(fl, key=lambda i: (i['x'], i['y']))
    if [i['tabOrder'] for i in order] != sorted(i['tabOrder'] for i in order):
        out.append('I8 tab order diverges from column-major visual order')

    if p['y_panel'] <= p['opener']['y'] + p['opener']['h']:
        out.append('I9 panel top %d overlaps the opener' % p['y_panel'])
    if (p['x_panel'] - CONTENT_ORIGIN) % 8 or (p['y_panel'] - CONTENT_ORIGIN) % 8:
        out.append('I10 panel origin off the content grid')
    # I14 the panel must fit the page it floats over (container included).
    gb = p['group_box']
    if gb['y'] + gb['h'] > PAGE_H - M_BOTTOM:
        out.append('I14 container bottom %d exceeds the page (%d)'
                   % (gb['y'] + gb['h'], PAGE_H - M_BOTTOM))
    # I15 C7: container == visible + shadow margins, and emitted members shifted
    # by exactly (SH_L, SH_T) - the grid law is checked on VISIBLE coordinates,
    # the container is allowed off-grid.
    if (gb['x'] != p['x_panel'] - SH_L or gb['y'] != p['y_panel'] - SH_T or
            gb['w'] != p['W_panel'] + SH_L + SH_R or
            gb['h'] != p['H_panel'] + SH_T + SH_B):
        out.append('I15 container box does not wrap the visible rect in the '
                   'shadow margins')
    for it, e in zip(p['items'], p['emit']):
        if it['name'] == 'backdrop':
            if (e['w'], e['h']) != (gb['w'], gb['h']) or (e['x'], e['y']) != (0, 0):
                out.append('I15 backdrop does not fill the container')
        elif (e['x'] - it['x'], e['y'] - it['y']) != (SH_L, SH_T):
            out.append('I15 %s not shifted by the shadow margin' % it['name'])
    return out


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    CAPS = {'clear': 'Clear all', 'default': 'Default',
            'primary': 'Apply and close', 'close': 'Close'}

    def run(tag, filters):
        pl = layout(filters, CAPS)
        if 'rejected' in pl:
            print('%-26s REJECTED: %s' % (tag, pl['rejected']))
            return
        bad = check(pl)
        print('%-26s F=%-2d C=%d stack=%d lines=%d  %dx%d @(%d,%d) targets=%d  %s'
              % (tag, pl['F'], pl['C'], pl['stack_h'], pl['lines'],
                 pl['W_panel'], pl['H_panel'], pl['x_panel'], pl['y_panel'],
                 pl['targetCount'], 'OK' if not bad else 'FAIL: ' + '; '.join(bad)))

    for n in (2, 4, 7, 8, 12, 13):
        run('F=%d all dropdown' % n,
            [{'name': 'f%d' % i, 'kind': 'dropdown'} for i in range(n)])
    run('demo: date-between + 3',
        [{'name': 'SlicerDate', 'kind': 'between'},
         {'name': 'SlicerReg', 'kind': 'dropdown'},
         {'name': 'SlicerCat', 'kind': 'dropdown'},
         {'name': 'SlicerProd', 'kind': 'dropdown'}])
    run('mixed: between+list+2 drop',
        [{'name': 'a', 'kind': 'between'}, {'name': 'b', 'kind': 'list'},
         {'name': 'c', 'kind': 'dropdown'}, {'name': 'd', 'kind': 'dropdown'}])
    run('6 lists', [{'name': 'f%d' % i, 'kind': 'list'} for i in range(6)])
