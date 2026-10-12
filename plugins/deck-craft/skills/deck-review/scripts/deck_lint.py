#!/usr/bin/env python3
"""deck_lint.py: the single judge of deck-review.

Judges HTML metrics (html_deck_lint.mjs) or PDF text runs (pdf_text_runs.py, plus pixels.mjs) against
thresholds.json and an optional deck-plan.json; validates a plan on its own; rates a token sheet.
Every rule threshold and measurement parameter comes from thresholds.json (mirror of references/rubric.md);
this file holds only the geometry heuristics that read text boxes (glyph box, line joining, centring).

Usage:
  python3 deck_lint.py [--plan deck-plan.json] (--metrics out/metrics.json | --runs out/runs/pages.json)
                       [--pixels out/pixels.json] [--thresholds path] [--mode talk|reading|talk+appendix]
                       [--only N,T,D1] [--skip H6] [--fail-on critical|should|cosmetic] --out out
  python3 deck_lint.py --plan-only deck-plan.json [--out dir] [--fail-on ...]
  python3 deck_lint.py --tokens tokens.json|deck.html [--mode talk|reading] [--out dir] [--fail-on ...]

Writes findings.json (deck-findings/1) and findings.md into --out (plan-findings.* and token-findings.*
for the two standalone modes, only when --out is given).
Exit: 0 no finding at or above --fail-on; 1 at least one; 2 usage error, unsupported or invalid input
(plan schema violations are listed), missing thresholds, failed contrast sanity asserts.
Stdlib only; writes only into --out; starts no processes.
"""
import argparse
import json
import os
import re
import statistics
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SEV = ['критично', 'бажано', 'косметика']
FAIL_ON = {'critical': 0, 'should': 1, 'cosmetic': 2}
FAMILY_ORDER = 'NTGYCVDSKHP'
PX2PT = 0.75


def die(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


# ------------------------------------------------------------------ contrast (pbi-color-accessibility §1)
def _lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def rel_lum(h):
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(ch * 2 for ch in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a, b):
    la, lb = rel_lum(a), rel_lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


HEX = re.compile(r'^#[0-9A-Fa-f]{6}$')


def is_hex(v):
    return isinstance(v, str) and bool(HEX.match(v))


# ------------------------------------------------------------------ text helpers
LIVE = re.compile(r'[^\W_]')
CYR = re.compile(r'[Ѐ-ӿ]')
UK_VERB = re.compile(r'\b\w+(?:ає|яє|ує|ює|еє|іє|ить|іть|ать|ять|уть|ють|ться|ється|ємо|имо|емо|[аиіяоу]в|[аиія]ла|[аиія]ли|[аиія]ло|[аиіяоу]вся|[аиіяу]л[аио]с[яь])\b', re.I)
# present-tense and reflexive endings; the past-tense endings left in UK_VERB (-ав, -ів, -ов, -ла, -ли, -ло) also end
# nouns (фільтрів, скіли, число), so a title that matches only those is a T1 suspect, not a pass
UK_VERB_STRONG = re.compile(r'\b\w+(?:ає|яє|ує|ює|еє|іє|ить|іть|ать|ять|уть|ють|ться|ється|ємо|имо|емо|[аиіяоу]вся|[аиіяу]л[аио]с[яь])\b', re.I)
EN_VERB = re.compile(r'\b(?:is|are|was|were|has|have|had|can|will|does|do|did|cuts|makes|\w+ed|\w+s)\b', re.I)
UNIT = re.compile(r'\d (?:%|грн|млн|млрд|тис|хв|хвилин\w*|секунд\w*|год\w*|годин\w*|дн\w*|тижн\w*|місяц\w*|рок\w*|років|ГБ|МБ|ТБ|px|pt|мс)\b')
DASHES = re.compile('[\u2013\u2014]')
HYPHEN_RANGE = re.compile(r'\d\s?-\s?\d')
DASH_RANGE = re.compile('\\d\\s?[\u2013\u2014]\\s?\\d')
CURLY = re.compile('[‘’“”]')
URL = re.compile(r'(?:https?://)?(?:[\w-]+\.)+[a-z]{2,}(?:/\S*)?', re.I)
MONO = re.compile(r'mono|code|courier|consolas|cascadia|menlo', re.I)
BOLD = re.compile(r'bold|black|heavy', re.I)
STYLE_WORDS = {'bold', 'semibold', 'demibold', 'extrabold', 'ultrabold', 'black', 'heavy', 'medium', 'light', 'semilight',
               'extralight', 'ultralight', 'thin', 'regular', 'normal', 'book', 'roman', 'italic', 'oblique', 'display',
               'text', 'small', 'variable', 'mt', 'ps', 'psmt'}


def tokens(text):
    return [t for t in str(text or '').split() if LIVE.search(t)]


def quote(text, n=6):
    """Evidence never quotes more than 6 words of slide text."""
    w = str(text or '').split()
    return ' '.join(w[:n]) + (' …' if len(w) > n else '')


def family_key(name):
    """Fold weight, style and optical-size words; key for counting families."""
    name = re.sub(r'^[A-Z]{6}\+', '', str(name or '?'))
    out = []
    for tok in re.split(r'[\s,\-_]+', name):
        if not tok:
            continue
        if len(tok) > 4:
            tok = re.sub(r'(PSMT|MT|PS)$', '', tok)
        parts = re.findall(r'[A-Z]+(?![a-z])|[A-Z]?[a-z]+|\d+', tok) or [tok]
        while parts and parts[-1].lower() in STYLE_WORDS:
            parts.pop()
        tok = ''.join(parts)
        if tok and tok.lower() not in STYLE_WORDS:
            out.append(tok)
    return (''.join(out) or name).lower()


def stems(text):
    return {w.lower()[:5] for w in re.findall(r'[^\W\d_]{4,}', str(text or ''))}


def median(vals):
    return statistics.median(vals) if vals else 0


def modal(vals):
    return Counter(vals).most_common(1)[0][0] if vals else None


def r1(v):
    return None if v is None else round(v, 1)


# ------------------------------------------------------------------ judge context
class Judge:
    def __init__(self, thr, path, only=None, skip=None):
        self.thr = thr
        self.C = thr['checks']
        self.A = thr['archetypes']
        self.G = {k: set(v) for k, v in thr['groups'].items()}
        self.M = thr['measure']
        self.path = path
        self.only, self.skip = only or set(), skip or set()
        self.findings, self.cnv, self.info, self.skipped = [], [], [], []
        self.hints = defaultdict(dict)  # check -> note -> slides: pointers for the visual pass (rubric §V)
        self.ran = set()
        self.font_mode = None

    def selected(self, cid):
        fam = re.match(r'[A-Z]+', cid).group(0)
        if self.only and cid not in self.only and fam not in self.only:
            return False
        return not (cid in self.skip or fam in self.skip)

    def on(self, cid, path=None):
        if not self.selected(cid) or (path or self.path) not in self.C[cid]['auto']:
            return False
        self.ran.add(cid)
        return True

    def par(self, cid, mode):
        return self.C[cid].get(mode)

    def add(self, cid, slide, message, measured=None, threshold=None, unit=None, op=None, evidence=None,
            severity=None, mode=None, slide_id=None, theme=None, key=None):
        c = self.C[cid]
        self.findings.append({
            'id': None, 'check': cid, 'severity': severity or c['severity'], 'slide': slide, 'slide_id': slide_id,
            'mode': mode, 'font_mode': self.font_mode, 'theme': theme, 'measured': measured, 'threshold': threshold,
            'unit': unit, 'op': op, 'message': message, 'evidence': evidence, 'lesson': list(c['lessons']),
            'owner': c['owner'], 'measured_by': c['measured'], 'confirm': c['measured'] == 'A+V',
            '_key': key if key is not None else (evidence or message),
        })

    def cannot(self, cid, slide, reason, evidence=None):
        if self.selected(cid):
            self.cnv.append({'check': cid, 'slide': slide, 'reason': reason, 'evidence': evidence})

    def hint(self, cid, note, slides=()):
        if self.selected(cid):
            self.hints[cid].setdefault(note, set()).update(x for x in slides if x is not None)

    def skip_check(self, cid, reason):
        if self.selected(cid) and not any(s['check'] == cid for s in self.skipped):
            self.skipped.append({'check': cid, 'reason': reason})


# ------------------------------------------------------------------ plan: schema (deck-plan.md §7)
SLUG = re.compile(r'^[a-z0-9][a-z0-9-]*$')
DEMO_ROLE = {'entrance': 'demo-divider', 'proof': 'demo-still', 'exit': 'demo-recap'}
TALK_MODES = ('talk', 'talk+appendix')
TITLE_VERIFIED = ('claim-auditor', 'manual')


def validate_plan(p, enum):
    errs = []
    E = errs.append
    if not isinstance(p, dict):
        return ['план має бути об’єктом JSON']
    if p.get('schema') != 'deck-plan/1':
        E(f"schema: очікується deck-plan/1, є {p.get('schema')!r}")
    for k in ('title', 'lang', 'mode', 'canvas', 'engine', 'dash_policy', 'audience', 'decision', 'parts', 'slides', 'approval'):
        if k not in p:
            E(f'немає обов’язкового поля {k}')
    enums = {'lang': ('uk', 'en'), 'mode': ('talk', 'reading', 'talk+appendix'), 'canvas': ('1280x720px', '960x540pt'),
             'engine': ('html', 'pptx', 'slides-artifact'), 'dash_policy': ('hyphen', 'en-dash')}
    for k, allowed in enums.items():
        if k in p and p[k] not in allowed:
            E(f'{k}={p[k]!r} поза переліком {"|".join(allowed)}')
    talk = p.get('mode') in TALK_MODES
    if talk:
        for k in ('minutes', 'promise', 'context', 'close'):
            if k not in p:
                E(f'немає поля {k}, обов’язкового для режиму {p.get("mode")}')
    ap = p.get('approval')
    if 'approval' in p and (not isinstance(ap, dict) or set(ap) != {'version', 'status', 'verdict', 'date'}
                            or ap.get('status') not in ('draft', 'changes', 'approved')):
        E('approval має бути {version, status: draft|changes|approved, verdict, date}')
    parts = p.get('parts') if isinstance(p.get('parts'), list) else []
    part_ids = []
    for i, pt in enumerate(parts, 1):
        if not isinstance(pt, dict) or not all(k in pt for k in ('id', 'title', 'question')):
            E(f'parts[{i}] має містити id, title, question')
            continue
        if not SLUG.match(str(pt['id'])):
            E(f"parts[{i}].id {pt['id']!r} не slug")
        part_ids.append(pt['id'])
    if len(part_ids) != len(set(part_ids)):
        E('parts: повторений id')
    lists = p.get('lists', {})
    if not isinstance(lists, dict):
        E('lists має бути об’єктом')
        lists = {}
    for name, items in lists.items():
        if not isinstance(items, list) or not all(isinstance(x, dict) and 'id' in x and 'label' in x for x in items):
            E(f'lists.{name}: кожен пункт має містити id і label')
    slides = p.get('slides') if isinstance(p.get('slides'), list) else []
    if 'slides' in p and not slides:
        E('slides порожній')
    ids = [s.get('id') for s in slides if isinstance(s, dict)]
    for d in sorted({x for x in ids if ids.count(x) > 1}, key=str):
        E(f'повторений id слайда {d!r}')
    byid = {s.get('id'): s for s in slides if isinstance(s, dict)}
    pair_count = Counter()
    for i, s in enumerate(slides, 1):
        if not isinstance(s, dict):
            E(f'slides[{i}] не об’єкт')
            continue
        for k in ('n', 'id', 'archetype', 'title'):
            if k not in s:
                E(f'слайд {i}: немає поля {k}')
        if s.get('n') != i:
            E(f'слайд {i}: n={s.get("n")} не за порядком')
        if 'id' in s and not SLUG.match(str(s['id'])):
            E(f"слайд {i}: id {s['id']!r} не slug")
        if 'archetype' in s and s['archetype'] not in enum:
            E(f"слайд {i}: архетип {s['archetype']!r} поза переліком")
        if s.get('part') is not None and s['part'] not in part_ids:
            E(f"слайд {i}: part {s['part']!r} не знайдено в parts")
        if s.get('list') is not None and s['list'] not in lists:
            E(f"слайд {i}: list {s['list']!r} не знайдено в lists")
        se = s.get('series')
        if se:
            if not isinstance(se, dict) or se.get('list') not in lists or se.get('item') not in [x.get('id') for x in lists.get(se.get('list'), [])]:
                E(f'слайд {i}: series не розв’язується')
        if s.get('proof_of') is not None and s['proof_of'] not in byid:
            E(f"слайд {i}: proof_of {s['proof_of']!r} не знайдено")
        pr = s.get('pair')
        if pr:
            if not isinstance(pr, dict) or pr.get('role') not in ('before', 'bridge', 'after'):
                E(f'слайд {i}: pair.role має бути before, bridge або after')
            else:
                pair_count[pr.get('id')] += 1
        d = s.get('demo')
        if d:
            if not isinstance(d, dict) or DEMO_ROLE.get(d.get('role')) != s.get('archetype'):
                E(f'слайд {i}: demo.role не відповідає архетипу (entrance=demo-divider, proof=demo-still, exit=demo-recap)')
        if talk and not s.get('appendix') and 'minutes' not in s:
            E(f'слайд {i}: немає minutes (режим {p.get("mode")})')
        if s.get('title_verified') is not None and s['title_verified'] not in TITLE_VERIFIED:
            E(f'слайд {i}: title_verified має бути claim-auditor або manual')
        st = s.get('status')
        if st:
            if not isinstance(st, dict) or st.get('state') not in ('ga', 'preview', 'planned') or not re.match(r'^\d{4}-\d{2}$', str(st.get('as_of', ''))):
                E(f'слайд {i}: status має бути {{state: ga|preview|planned, as_of: YYYY-MM}}')
        for m in s.get('media') or []:
            if not isinstance(m, dict) or set(m) - {'file', 'native_px', 'ui_px', 'placed_pt'}:
                E(f'слайд {i}: media має поля file, native_px, ui_px, placed_pt')
    for pid, c in pair_count.items():
        if c < 2:
            E(f'pair.id {pid!r} має лише один слайд')
    return errs


# ------------------------------------------------------------------ plan: rules (deck-plan.md §8)
def plan_rules(J, p, mode=None):
    """mode: the effective mode (--mode overrides plan.mode, deck-plan.md §10)."""
    C, G = J.C, J.G
    slides = p['slides']
    talk = (mode or p['mode']) in TALK_MODES
    mk = 'talk' if talk else 'reading'
    main = [s for s in slides if not s.get('appendix')]
    lists = p.get('lists', {})
    byid = {s['id']: s for s in slides}
    on = lambda cid: J.on(cid, 'plan')
    if on('N1'):
        app = [s['n'] for s in slides if s.get('appendix')]
        ad = [s['n'] for s in slides if s['archetype'] == 'appendix-divider']
        if app and (not ad or min(app) < ad[0]):
            J.add('N1', min(app), 'слайд додатка стоїть перед appendix-divider', evidence='plan.slides[].appendix')
        if ad and any(s['n'] > ad[0] for s in main):
            J.add('N1', ad[0], 'основний слайд після appendix-divider', evidence='plan.slides[].appendix')
    if on('N2'):
        P = C['N2'][mk]
        route = [s['n'] for s in main if s['archetype'] == 'route']
        if not route or route[0] > P['route_pos_max']:
            J.add('N2', route[0] if route else None, 'слайд route відсутній або пізно', measured=route[0] if route else None,
                  threshold=P['route_pos_max'], unit='slide', op='<=', evidence='plan route')
        if talk:
            lo, hi = P['parts']
            if p.get('minutes', 99) < P['short_minutes']:
                lo = P['parts_short_min']
            if not lo <= len(p['parts']) <= hi:
                J.add('N2', None, f'{len(p["parts"])} частин, а має бути {lo}-{hi}', measured=len(p['parts']),
                      threshold=f'{lo}..{hi}', unit='parts', op='in', evidence='plan.parts')
        for part in p['parts']:
            first = next((s for s in main if s.get('part') == part['id']), None)
            if not first or first['archetype'] != 'divider':
                J.add('N2', first['n'] if first else None, f"частина {part['id']} не відкривається divider", evidence=f"part {part['id']}")
    if on('N3'):
        if slides[0]['archetype'] != 'title' or (talk and (not p.get('promise') or not p.get('context'))):
            J.add('N3', 1, 'слайд 1 не title або немає promise чи context', evidence='plan.promise, plan.context', key=('plan', 'n3'))
    pairs = defaultdict(list)
    for s in slides:
        if s.get('pair'):
            pairs[s['pair']['id']].append(s)
    if on('N4'):
        for pid, ss in pairs.items():
            b = [s for s in ss if s['pair']['role'] == 'before']
            a = [s for s in ss if s['pair']['role'] == 'after']
            if len(b) != 1 or len(a) != 1:
                J.add('N4', ss[0]['n'], f'пара {pid}: потрібен один before і один after', evidence=f'pair {pid}')
                continue
            b, a = b[0], a[0]
            if b['archetype'] != a['archetype']:
                J.add('N4', a['n'], f'пара {pid}: різні архетипи', evidence=f'pair {pid}')
            between = [s for s in slides if b['n'] < s['n'] < a['n']]
            gap = C['N4'][mk]['gap_max']
            if len(between) > gap or any((s.get('pair') or {}).get('role') != 'bridge' for s in between):
                J.add('N4', a['n'], f'пара {pid}: між кінцями {len(between)} слайдів не-bridge', measured=len(between),
                      threshold=gap, unit='slides', op='<=', evidence=f'pair {pid}')
    if on('N5'):
        for i, s in enumerate(slides):
            if s['archetype'] == 'zoom' and (i == 0 or slides[i - 1]['archetype'] not in ('map', 'zoom')):
                J.add('N5', s['n'], 'zoom не йде одразу після map', evidence=s['id'])
    if on('N6') and C['N6'].get(mk) is not None:
        demos = defaultdict(list)
        for s in slides:
            if s.get('demo'):
                demos[s['demo']['id']].append(s)
        for did, ss in demos.items():
            roles = [s['demo']['role'] for s in ss]
            if roles.count('entrance') != 1 or roles.count('exit') != 1 or 'proof' not in roles:
                J.add('N6', ss[0]['n'], f'демо {did}: потрібні вхід, доказ і вихід', evidence=f'demo {did}')
                continue
            if roles != sorted(roles, key=['entrance', 'proof', 'exit'].index):
                J.add('N6', ss[0]['n'], f'демо {did}: порядок не вхід, доказ, вихід', evidence=f'demo {did}')
            if not [s for s in ss if s['demo']['role'] == 'entrance'][0]['demo'].get('minutes'):
                J.add('N6', ss[0]['n'], f'демо {did}: на вході немає minutes', evidence=f'demo {did}')
    for name, items in lists.items():
        hub = [s for s in main if s.get('list') == name and s['archetype'] == 'hub']
        spokes = [s for s in main if (s.get('series') or {}).get('list') == name]
        if on('N7'):
            if spokes and (not hub or hub[0]['n'] > spokes[0]['n']):
                J.add('N7', spokes[0]['n'], f'хаб списку {name} іде після спиць або відсутній', evidence=f'list {name}')
            order = [[x['id'] for x in items].index(s['series']['item']) for s in spokes]
            if order != sorted(order):
                J.add('N7', spokes[0]['n'] if spokes else None, f'спиці списку {name} не в порядку хаба', evidence=f'list {name}')
        if on('N9') and talk and len(spokes) > C['N9']['talk']['items_main_max']:
            J.add('N9', spokes[0]['n'], f'{len(spokes)} спиць списку {name} в основному потоці', measured=len(spokes),
                  threshold=C['N9']['talk']['items_main_max'], unit='slides', op='<=', evidence=f'list {name}')
        if on('N13'):
            labels = {x['id']: x['label'] for x in items}
            for s in slides:
                if (s.get('series') or {}).get('list') == name and s.get('eyebrow') and labels[s['series']['item']] not in s['eyebrow']:
                    J.add('N13', s['n'], 'eyebrow спиці не містить мітки пункту', evidence=s['id'])
    if on('N13'):
        for part in p['parts']:
            first = next((s for s in main if s.get('part') == part['id']), None)
            if first and first['archetype'] == 'divider' and first['title'] != part['question']:
                J.add('N13', first['n'], 'заголовок divider не дорівнює parts[].question', evidence=first['id'])
    if on('N10') and talk and not isinstance(p.get('close'), dict):
        J.cannot('N10', None, 'план без close (режим доповіді задано через --mode): закриття за планом не перевірено')
    elif on('N10') and talk:
        c = p['close']
        last = main[-1]
        allowed = {x['title'] for x in p['parts']} | {x['label'] for v in lists.values() for x in v}
        if last['archetype'] not in ('close', 'cta'):
            J.add('N10', last['n'], 'останній основний слайд не close чи cta', evidence=last['id'])
        if len(re.findall(r'[.!?](\s|$)', str(c.get('takeaway', '')).strip())) > 1:
            J.add('N10', last['n'], 'takeaway довший за одне речення', evidence='close.takeaway')
        if not c.get('recap') or any(r not in allowed for r in c['recap']):
            J.add('N10', last['n'], 'recap не повторює назви частин або списків дослівно', evidence='close.recap')
        if not c.get('next_step'):
            J.add('N10', last['n'], 'немає next_step', evidence='close.next_step')
        lim = C['N10']['talk']['url_chars_max']
        if c.get('url') and len(c['url']) > lim:
            J.add('N10', last['n'], f"URL {len(c['url'])} символів", measured=len(c['url']), threshold=lim, unit='chars', op='<=', evidence='close.url')
    if on('N11'):
        for s in slides:
            po = s.get('proof_of')
            if not po:
                continue
            if byid[po]['n'] >= s['n']:
                J.add('N11', s['n'], 'proof_of вказує вперед', evidence=s['id'])
                continue
            for t in slides[byid[po]['n']:s['n'] - 1]:
                if t.get('proof_of') != po:
                    J.add('N11', t['n'], f'між концептом і доказом стоїть слайд з іншим proof_of', evidence=t['id'])
    if on('N12') and talk and not isinstance(p.get('minutes'), (int, float)):
        J.cannot('N12', None, 'план без minutes (режим доповіді задано через --mode): хронометраж не перевірено')
    elif on('N12') and talk:
        dm = sum(s['demo'].get('minutes', 0) for s in main if s.get('demo') and s['demo']['role'] == 'entrance')
        avail = p['minutes'] - p.get('qa_minutes', 0) - dm
        content = [s for s in main if s['archetype'] not in G['structural']]
        lo, hi = C['N12']['talk']['min_per_slide']
        rng = f'{avail / hi:.1f}..{avail / lo:.1f}'
        if len(content) > avail / lo:
            J.add('N12', None, f'{len(content)} змістових слайдів на {avail:g} хв', measured=len(content), threshold=rng, unit='slides', op='in', evidence='plan.minutes')
        elif len(content) < avail / hi:
            J.add('N12', None, f'{len(content)} змістових слайдів на {avail:g} хв (менше нижньої межі)', measured=len(content),
                  threshold=rng, unit='slides', op='in', severity='косметика', evidence='plan.minutes')
        total = sum(s.get('minutes', 0) for s in main) + p.get('qa_minutes', 0)
        if total > p['minutes'] + 1e-9:
            J.add('N12', None, f'хвилини слайдів і Q&A {total:g} > {p["minutes"]}', measured=total, threshold=p['minutes'], unit='min', op='<=', evidence='plan.slides[].minutes')
    t1, t3 = C['T1'][mk], C['T3'][mk]
    uk = p.get('lang', 'uk') == 'uk'
    for s in slides:
        t = s['title']
        if on('T1'):
            if s['archetype'] in ('divider', 'appendix-divider') and len(t.split()) > t1['divider_words_max']:
                J.add('T1', s['n'], f'заголовок divider {len(t.split())} слів', measured=len(t.split()), threshold=t1['divider_words_max'], unit='words', op='<=', evidence=quote(t), key=('plan', 'words'))
            if s['archetype'] == 'demo-divider' and len(t.split()) > t1['demo_divider_words_max']:
                J.add('T1', s['n'], f'заголовок demo-divider {len(t.split())} слів', measured=len(t.split()), threshold=t1['demo_divider_words_max'], unit='words', op='<=', evidence=quote(t), key=('plan', 'words'))
            if s['archetype'] not in G['title_exempt'] and not s.get('title_verified'):
                v = t1_verdict(t, uk)
                if v is None:
                    J.add('T1', s['n'], 'заголовок без дієслова чи числа (кандидат для claim-auditor)', evidence=quote(t), key=('plan', 'verb'))
                elif v == 'suspect':
                    J.hint('T1', T1_SUSPECT, [s['n']])
        if on('T3') and s['archetype'] not in G['dividers']:
            budget = t3['chars_cyr'] if CYR.search(t) else t3['chars_latin']
            if len(t) > budget:
                J.add('T3', s['n'], f'заголовок {len(t)} символів', measured=len(t), threshold=budget, unit='chars', op='<=', evidence=quote(t), key=('plan', 'chars'))
    strings = []
    for s in slides:
        for k in ('title', 'eyebrow', 'dek', 'claim'):
            if s.get(k):
                strings.append((s['n'], s[k]))
    for k in ('title', 'promise', 'context'):
        if p.get(k):
            strings.append((None, p[k]))
    strings += [(None, x) for pt in p['parts'] for x in (pt['title'], pt['question'])]
    strings += [(None, x['label']) for v in lists.values() for x in v]
    if p.get('close'):
        strings += [(None, p['close'].get(k) or '') for k in ('takeaway', 'next_step')] + [(None, r) for r in p['close'].get('recap', [])]
    for n, v in strings:
        if on('T9') and UNIT.search(v):
            J.add('T9', n, 'звичайний пробіл між числом і одиницею (потрібен NBSP)', evidence=quote(UNIT.search(v).group(0)), key=v)
        if on('T10'):
            if p['dash_policy'] == 'hyphen' and DASHES.search(v):
                J.add('T10', n, 'довге або коротке тире при dash_policy hyphen', evidence=quote(v), key=v)
            if p['dash_policy'] == 'en-dash' and HYPHEN_RANGE.search(v):
                J.add('T10', n, 'діапазон через дефіс при dash_policy en-dash', evidence=quote(v), key=v)
    if on('T11'):
        seen = {}
        for s in slides:
            if s['title'] in seen and s['archetype'] != 'zoom':
                J.add('T11', s['n'], f"заголовок повторює слайд {seen[s['title']]}", evidence=quote(s['title']), severity='бажано', key='title-dup')
            seen.setdefault(s['title'], s['n'])


# ------------------------------------------------------------------ tokens (--tokens)
def rate_tokens(J, src, mode):
    T = J.thr['tokens']
    classes = T['classes']

    def minimum(cls):
        ref = classes[cls].split()[0]
        cid, key = ref.split('.')
        block = J.C[cid].get(mode) or J.C[cid]['talk']
        return block[key], cid

    themes, stored, sheet = {}, [], None
    if src.lower().endswith('.json'):
        try:
            sheet = json.load(open(src, encoding='utf-8'))
            glob = dict(sheet.get('void', {}).get('colors', {}))
            glob.update(sheet.get('status', {}).get('colors', {}))
            for name, th in sheet['themes'].items():
                c = dict(glob)
                c.update(th['colors'])
                themes[name] = c
                stored += [(name, x) for x in th.get('pairs', [])]
            stored += [('void', x) for x in sheet.get('void', {}).get('pairs', [])]
            stored += [('status', x) for x in sheet.get('status', {}).get('pairs', [])]
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
            die(f'token sheet unreadable ({e}): {src}')
    else:
        try:
            css = open(src, encoding='utf-8').read()
        except OSError as e:
            die(f'cannot read {src}: {e}')
        css = ' '.join(re.findall(r'<style[^>]*>(.*?)</style>', css, re.S | re.I)) or css

        def block(pattern):
            out = {}
            for m in re.finditer(pattern + r'\s*\{([^}]*)\}', css):
                out.update({k: v for k, v in re.findall(r'--([a-z0-9-]+)\s*:\s*(#[0-9A-Fa-f]{6})\b', m.group(1))})
            return out
        light = block(r'(?<![\w\]-]):root(?![\w\[-])')
        dark = dict(light)
        dark.update(block(r'(?::root|html)?\[data-theme=["\']?dark["\']?\]'))
        themes = {'light': light}
        if dark != light:
            themes['dark'] = dark
    seen, rated = set(), 0
    for theme, c in themes.items():
        for fg, bg, cls in T['default_pairs']:
            if fg not in c or bg not in c:
                continue
            glob = fg.startswith(('void', 'ga-', 'preview-', 'planned-'))
            label = ('void' if fg.startswith('void') else 'status') if glob else theme
            if (label, fg, bg, cls) in seen:
                continue
            seen.add((label, fg, bg, cls))
            judge_pair(J, label, fg, bg, cls, c[fg], c[bg], minimum)
            rated += 1
    for label, x in stored:
        try:
            colours = themes.get(label) or themes.get('light', {})
            if label in ('void', 'status'):
                colours = dict(themes.get('light', {}))
            a, b = colours[x['fg']], colours[x['bg']]
        except KeyError:
            J.cannot('C1', None, f"пара {x.get('fg')} на {x.get('bg')}: роль не визначена ({label})")
            continue
        r = round(contrast(a, b), 2)
        if (label, x['fg'], x['bg'], x['class']) not in seen:
            seen.add((label, x['fg'], x['bg'], x['class']))
            judge_pair(J, label, x['fg'], x['bg'], x['class'], a, b, minimum)
            rated += 1
        if x.get('ratio') is not None and abs(r - x['ratio']) > 0.01:
            cid = minimum(x['class'])[1]
            J.add(cid, None, f"записане співвідношення {x['ratio']} не збігається з обчисленим {r}", measured=r,
                  threshold=x['ratio'], unit='ratio', op='==', evidence=f"{x['fg']} на {x['bg']}", severity='бажано', theme=label)
    if not rated:
        J.cannot('C1', None, 'жодної пари ролей thresholds.json tokens.default_pairs не знайдено у джерелі')
    J.info.append({'check': 'tokens', 'note': f'оцінено пар: {rated}; теми: {", ".join(sorted(themes))}'})


def judge_pair(J, theme, fg, bg, cls, a, b, minimum):
    r = round(contrast(a, b), 2)
    mn, cid = minimum(cls)
    if not J.on(cid, 'tokens'):
        return
    if cls == 'dim':
        J.info.append({'check': cid, 'theme': theme, 'measured': r, 'note': f'dim {fg} на {bg} (ціль близько {mn}:1)'})
        return
    if r < mn:
        J.add(cid, None, f'{fg} {a} на {bg} {b}: {r}:1, клас {cls}', measured=r, threshold=mn, unit='ratio', op='>=',
              evidence=f'{fg} на {bg}', theme=theme, key=(theme, fg, bg, cls))


# ------------------------------------------------------------------ normalisation to one slide model (pt, top-left)
def norm_html(metrics):
    passes = metrics.get('passes') or []
    if not passes:
        die('metrics.json has no passes')
    out = []
    for ps in passes:
        slides = []
        for s in ps['slides']:
            W, H = [v * PX2PT for v in (s.get('canvas_px') or metrics.get('canvas_px') or [1280, 720])]
            B = (lambda b: [v * PX2PT for v in b] if b else None)
            texts = []
            for t in s.get('texts', []):
                texts.append({'role': t['role'], 'text': t.get('text', ''), 'words': t.get('words', 0), 'box': B(t['box']),
                              'size': t['size_px'] * PX2PT, 'bold': (t.get('weight') or 400) >= 600, 'color': t.get('color'),
                              'bg': t.get('bg'), 'bg_kind': t.get('bg_kind'), 'lines': t.get('lines') or 1,
                              'cpl': t.get('chars_per_line'), 'align': t.get('align'), 'transform': t.get('transform'),
                              'family': t.get('family'), 'mono': t.get('mono'), 'gradient': t.get('gradient'),
                              'in_shape': t.get('in_shape'), 'excluded': t.get('excluded', False), 'sel': t.get('sel'),
                              'underline': t.get('underline')})
            ti = s.get('title')
            title = None
            if ti:
                title = dict(ti)
                title['box'] = B(ti['box'])
                title['size'] = ti['size_px'] * PX2PT
                title['bold'] = (ti.get('weight') or 400) >= 600
                title['centred'] = ti.get('align') == 'center'
            pn = s.get('page_number')
            if pn:
                pn = {'value': pn.get('value'), 'box': B(pn.get('box')), 'size': (pn.get('size_px') or 0) * PX2PT, 'text': pn.get('text')}
            slides.append({'n': s['n'], 'id': s.get('id'), 'archetype': s.get('archetype'), 'mode_attr': s.get('mode'),
                           'appendix': bool(s.get('appendix')), 'words': s.get('words', 0), 'texts': texts, 'title': title,
                           'pn': pn, 'W': W, 'H': H, 'images': len(s.get('images') or []), 'src': 'html', 'raw': s,
                           'bg_lum': (s.get('bg') or {}).get('lum')})
        out.append((ps.get('font_mode', 'native'), slides))
    return out


def norm_pdf(doc, pixels, M):
    pages = doc.get('pages') if isinstance(doc, dict) else doc
    if not isinstance(pages, list) or not pages:
        die('runs file has no pages')
    default = (doc.get('page_pt') if isinstance(doc, dict) else None) or [960, 540]
    ring = {}
    for b in (pixels or {}).get('run_bg', []) or []:
        ring[(b['n'], b['i'])] = (b.get('bg'), b.get('unknown', True))
    slides = []
    for idx, pg in enumerate(pages, 1):
        n = pg.get('n') or pg.get('page') or idx
        W, H = pg.get('size_pt') or default
        texts = []
        for i, r in enumerate(pg.get('runs', [])):
            fam = r.get('family') or r.get('font', '?')
            mono = r.get('mono') if 'mono' in r else bool(MONO.search(fam))
            bold = r.get('bold') if 'bold' in r else bool(BOLD.search(r.get('font', '')))
            size = float(r['size'])
            yb = H - float(r['y'])
            off = r['y'] > H or r['y'] < 0 or r['x'] >= W or r['x1'] <= 0
            bg, unk = ring.get((n, i), (None, True))
            texts.append({'role': 'code' if mono else 'body', 'text': r['text'], 'words': len(tokens(r['text'])),
                          'box': [r['x'], yb - 0.8 * size, max(0.0, r['x1'] - r['x']), size], 'size': size, 'bold': bold,
                          'color': r.get('color'), 'bg': bg if not unk else None, 'bg_kind': 'solid' if bg and not unk else 'unknown',
                          'lines': 1, 'cpl': None, 'align': None, 'transform': 'none', 'family': fam, 'mono': mono,
                          'gradient': None, 'in_shape': False, 'excluded': False, 'sel': f'run {i}', 'i': i, 'baseline': yb,
                          'offcanvas': off, 'font': r.get('font')})
        pn = None
        for t in texts:
            m = re.fullmatch(r'0*(\d{1,3})(?:\s*/\s*\d{1,3})?', t['text'].strip())
            if m and t['size'] <= M['pn_max_pt'] and int(m.group(1)) == n and not t['offcanvas']:
                pn = {'value': int(m.group(1)), 'box': t['box'], 'size': t['size'], 'text': t['text']}
                t['role'], t['excluded'] = 'footer', True
                break
        for t in texts:
            if t['role'] == 'body' and t['baseline'] >= 0.9 * H and t['size'] <= M['pn_max_pt']:
                t['role'] = 'footer'
        title = pdf_title(texts, n, W, H, M)
        slides.append({'n': n, 'id': None, 'archetype': None, 'mode_attr': None, 'appendix': False,
                       'words': sum(t['words'] for t in texts if not t['excluded']), 'texts': texts, 'title': title, 'pn': pn,
                       'W': W, 'H': H, 'images': pg.get('images') if isinstance(pg.get('images'), int) else len(pg.get('images') or []),
                       'src': 'pdf', 'raw': pg, 'bg_lum': None})
    return slides


def pdf_title(texts, n, W, H, M, anywhere=False, mark=True):
    live = [t for t in texts if not t['offcanvas'] and not t['excluded'] and t['words']]
    zone = [t for t in live if t['baseline'] <= M['title_zone_top'] * H] if not anywhere else live
    if not zone:
        return None
    big = max(t['size'] for t in zone)
    cand = sorted([t for t in zone if abs(t['size'] - big) <= 0.5], key=lambda t: (t['baseline'], t['box'][0]))
    first = cand[0]
    group, last = [first], first['baseline']
    for t in cand[1:]:
        if t['font'] != first['font'] and abs(t['baseline'] - last) > 0.5 * big:
            continue
        if t['baseline'] - last <= 1.6 * big:
            group.append(t)
            last = max(last, t['baseline'])
    lines = []
    for t in sorted(group, key=lambda t: (t['baseline'], t['box'][0])):
        if lines and abs(lines[-1][0] - t['baseline']) < 0.5 * big:
            lines[-1][1].append(t)
        else:
            lines.append([t['baseline'], [t]])
    text = ' '.join(' '.join(x['text'] for x in sorted(ln[1], key=lambda x: x['box'][0])) for ln in lines)
    x0 = min(t['box'][0] for t in group)
    x1 = max(t['box'][0] + t['box'][2] for t in group)
    centres = [(min(x['box'][0] for x in ln[1]) + max(x['box'][0] + x['box'][2] for x in ln[1])) / 2 for ln in lines]
    centred = all(abs(c - W / 2) <= 0.03 * W for c in centres) and x0 > 0.1 * W
    for t in group if mark else ():
        t['role'] = 'title'
    return {'text': text, 'chars': len(text), 'lines': len(lines), 'last_line_words': len(tokens(' '.join(x['text'] for x in lines[-1][1]))),
            'box': [x0, first['baseline'] - 0.8 * big, x1 - x0, lines[-1][0] - first['baseline'] + big], 'size': big,
            'bold': first['bold'], 'color': first['color'], 'bg': first['bg'], 'visible': True, 'covered': None,
            'centred': centred, 'baseline': first['baseline'], 'runs': [t['i'] for t in group]}


TITLE_ANYWHERE = ('title', 'divider', 'demo-divider', 'appendix-divider', 'close', 'cta')


def retitle(s, M):
    """Title, dividers, close and cta may set their title anywhere on the page (centred, under a pill or an
    eyebrow): the largest live on-canvas run wins even when the top zone holds smaller text."""
    new = pdf_title(s['texts'], s['n'], s['W'], s['H'], M, anywhere=True, mark=False)
    if not new or (s['title'] and new['size'] <= s['title']['size'] + M['tol_pt']):
        return
    for t in s['texts']:
        if t['role'] == 'title':
            t['role'] = 'code' if t['mono'] else 'body'
        if t['i'] in new['runs']:
            t['role'] = 'title'
    s['title'] = new


# ------------------------------------------------------------------ deck context
class Deck:
    def __init__(self, J, slides, plan, mode_arg, meta_mode, lang):
        self.J, self.plan = J, plan
        self.mode = mode_arg or (plan or {}).get('mode') or meta_mode
        self.declared = bool(self.mode)
        self.mode = self.mode or 'talk'
        self.lang = (plan or {}).get('lang') or lang
        ps = (plan or {}).get('slides') or []
        for s in slides:
            pl = ps[s['n'] - 1] if 0 < s['n'] <= len(ps) else None
            s['plan'] = pl
            if pl:
                s['archetype'] = pl.get('archetype') or s['archetype']
                s['appendix'] = bool(pl.get('appendix')) or s['appendix']
                s['id'] = s['id'] or pl.get('id')
            s['arch_inferred'] = False
            if not s['archetype'] and s['n'] == 1:
                s['archetype'], s['arch_inferred'] = 'title', True
            if s['archetype'] and s['archetype'] not in J.A:
                J.cannot('D2', s['n'], f"архетип {s['archetype']!r} поза переліком")
        self.slides = slides
        self.known = any(s['archetype'] and not s['arch_inferred'] for s in slides)

    def smode(self, s):
        if s.get('mode_attr') in ('talk', 'reading'):
            return s['mode_attr']
        if self.mode == 'reading':
            return 'reading'
        if self.mode == 'talk+appendix':
            return 'reading' if s['appendix'] else 'talk'
        return 'talk'

    def ing(self, s, group):
        return s['archetype'] in self.J.G[group]

    def lang_of(self, text):
        if self.lang in ('uk', 'en'):
            return self.lang
        return 'uk' if CYR.search(text or '') else 'en'


T1_SUSPECT = 'дієслово знайдено лише за закінченням минулого часу (-ав, -ів, -ла, -ли, -ло мають і іменники): Title test або claim-auditor'


def t1_verdict(text, uk):
    """T1: a digit or a verb passes ('number', 'verb'), None fails. A Cyrillic title whose only verb-regex hits are
    past-tense endings shared with nouns is a 'suspect': routed to claim-auditor (visual_hints), neither passed
    silently nor reported."""
    if re.search(r'\d', text or ''):
        return 'number'
    if (UK_VERB if uk else EN_VERB).search(text or ''):
        return 'suspect' if CYR.search(text) and not UK_VERB_STRONG.search(text) else 'verb'
    return None


def title_verified(pl, text):
    # deck-plan.md §4: the plan records a T1 verb suspect that claim-auditor or the manual Title test passed;
    # it holds only while the rendered title still equals the plan title
    return bool(pl and pl.get('title_verified') and ' '.join(str(pl.get('title', '')).split()) == ' '.join((text or '').split()))


def live_texts(s, roles=None):
    return [t for t in s['texts'] if not t['excluded'] and t['words'] and (roles is None or t['role'] in roles)]


def body_target(J, s, mode):
    y1 = J.par('Y1', mode)
    a = J.A.get(s['archetype'] or '', {})
    mn = a.get('min_pt') if a.get('mode') in (mode, 'any') else None
    return mn if mn is not None and mn < y1['body_pt'] else y1['body_pt']


# ------------------------------------------------------------------ per-slide checks (both engines)
def slide_checks(J, D, slides, pixels):
    M = J.M
    for s in slides:
        n, mode, sid = s['n'], D.smode(s), s['id']
        texts = live_texts(s)
        title = s['title']
        add = lambda cid, msg, **k: J.add(cid, n, msg, mode=mode, slide_id=sid, **k)

        # ---- T1 rendered titles
        if J.on('T1') and J.par('T1', mode) is not None and title:
            P = J.par('T1', mode)
            tw = len(tokens(title['text']))
            if s['archetype'] in ('divider', 'appendix-divider') and tw > P['divider_words_max']:
                add('T1', f'заголовок divider {tw} слів', measured=tw, threshold=P['divider_words_max'], unit='words', op='<=', evidence=quote(title['text']))
            elif s['archetype'] == 'demo-divider' and tw > P['demo_divider_words_max']:
                add('T1', f'заголовок demo-divider {tw} слів', measured=tw, threshold=P['demo_divider_words_max'], unit='words', op='<=', evidence=quote(title['text']))
            elif not D.ing(s, 'title_exempt') and not title_verified(s.get('plan'), title['text']):
                v = t1_verdict(title['text'], D.lang_of(title['text']) == 'uk')
                if v is None:
                    add('T1', 'заголовок без дієслова чи числа (кандидат для claim-auditor)', evidence=quote(title['text']), key='verb')
                elif v == 'suspect':
                    J.hint('T1', T1_SUSPECT, [n])

        # ---- T3 one-line titles
        if J.on('T3') and title and not D.ing(s, 'dividers'):
            P = J.par('T3', mode)
            base = P['chars_cyr'] if CYR.search(title['text']) else P['chars_latin']
            budget = base * P['at_pt'] / title['size'] if title['size'] else base
            if s['src'] == 'html' and any(d.get('kind') == 'brand' for d in s['raw'].get('deco') or []):
                budget -= P['logo_minus']
            if title['lines'] > P['lines_max']:
                add('T3', f"заголовок у {title['lines']} рядки", measured=title['lines'], threshold=P['lines_max'], unit='lines', op='<=', evidence=quote(title['text']), key='lines')
            if title['chars'] > budget:
                add('T3', f"{title['chars']} символів при {r1(title['size'])} pt", measured=title['chars'], threshold=round(budget), unit='chars', op='<=', evidence=quote(title['text']), key='chars')
            if title['lines'] > 1 and title['last_line_words'] < P['orphan_words_min']:
                add('T3', f"останній рядок заголовка: {title['last_line_words']} слово", measured=title['last_line_words'], threshold=P['orphan_words_min'], unit='words', op='>=', evidence=quote(title['text']), key='orphan')
        dek = s['raw'].get('dek') if s['src'] == 'html' else None
        if J.on('T3') and dek and dek.get('lines', 0) > 1 and dek.get('last_line_words', 2) < J.par('T3', mode)['orphan_words_min']:
            add('T3', f"останній рядок підзаголовка (dek): {dek['last_line_words']} слово", measured=dek['last_line_words'], threshold=J.par('T3', mode)['orphan_words_min'],
                unit='words', op='>=', evidence=dek.get('sel'), severity='косметика', key='dek-orphan')

        # ---- T4 claim is the largest text
        if J.on('T4') and title:
            others = [t for t in texts if t['role'] not in ('title', 'hero') and not t.get('offcanvas') and not re.fullmatch(r'[\d\s.,%+×x/:-]+', t['text'])]
            big = max(others, key=lambda t: t['size'], default=None)
            if big and big['size'] > title['size'] + M['tol_pt']:
                add('T4', f"текст {r1(big['size'])} pt більший за заголовок {r1(title['size'])} pt", measured=r1(big['size']), threshold=r1(title['size']), unit='pt', op='<=', evidence=big['sel'], key='largest')
            eb = s['raw'].get('eyebrow') if s['src'] == 'html' else None
            if eb and eb.get('size_px'):
                lo, hi = J.par('T4', mode)['eyebrow_pt']
                ept = eb['size_px'] * PX2PT
                if not lo - 0.01 <= ept <= hi + 0.01:
                    add('T4', f'eyebrow {r1(ept)} pt', measured=r1(ept), threshold=f'{lo}..{hi}', unit='pt', op='in', evidence='.eyebrow', key='eyebrow')

        # ---- T6 restatement
        if J.on('T6') and title and not D.ing(s, 'title_exempt'):
            below = sorted([t for t in texts if t['role'] == 'body' and t['box'] and t['box'][1] >= title['box'][1] + title['box'][3] - 1 and t['words'] >= 3],
                           key=lambda t: (round(t['box'][1]), t['box'][0]))
            ts = stems(title['text'])
            if below and len(ts) >= 2:
                ov = len(ts & stems(below[0]['text'])) / len(ts)
                if ov >= J.par('T6', mode)['overlap_max'] - 1e-9:  # the cut itself is a restatement (ref 10 at 0.50)
                    add('T6', f'перший рядок повторює заголовок на {round(ov * 100)}%', measured=round(ov, 2), threshold=J.par('T6', mode)['overlap_max'], unit='ratio', op='<', evidence=quote(below[0]['text']))

        # ---- T9 NBSP, T10 dashes
        if J.on('T9'):
            hits = [t for t in texts if UNIT.search(t['text'])]
            if hits:
                add('T9', f'{len(hits)} місць без NBSP між числом і одиницею', measured=len(hits), threshold=0, unit='hits', op='<=', evidence=quote(UNIT.search(hits[0]['text']).group(0)))
        if J.on('T10') and D.plan:
            pol = D.plan.get('dash_policy')
            hits = [t for t in texts if (DASHES.search(t['text']) if pol == 'hyphen' else HYPHEN_RANGE.search(t['text']))]
            if hits:
                add('T10', f'{len(hits)} рядків з формою діапазону, що суперечить dash_policy {pol}', measured=len(hits), threshold=0, unit='hits', op='<=', evidence=hits[0].get('sel'))

        # ---- G2 safe margin
        if J.on('G2'):
            P = J.par('G2', mode)
            worst, cnt = None, 0
            items = [(t['box'], t['role'], t['sel']) for t in texts if t['box'] and not t.get('offcanvas')]
            if s['pn'] and s['pn']['box']:
                items.append((s['pn']['box'], 'footer', 'page number'))
            if s['src'] == 'html':
                for im in s['raw'].get('images') or []:
                    b = [v * PX2PT for v in im['box']]
                    if b[2] >= 0.9 * s['W'] or b[3] >= 0.9 * s['H']:
                        continue
                    items.append((b, 'media', im['sel']))
            for b, role, sel in items:
                d = min(b[0], b[1], s['W'] - b[0] - b[2], s['H'] - b[1] - b[3])
                lim = P['footer_edge_pt'] if role == 'footer' else P['margin_pt']
                if d < lim - M['tol_pt'] and d > -1:
                    cnt += 1
                    if worst is None or d - lim < worst[0] - worst[1]:
                        worst = (d, lim, sel)
            if worst:
                add('G2', f'{cnt} елементів ближче до краю, ніж {worst[1]} pt', measured=r1(worst[0]), threshold=worst[1], unit='pt', op='>=', evidence=worst[2])

        # ---- G5 empty space with small text
        if J.on('G5'):
            P = J.par('G5', mode)
            body = [t['size'] for t in texts if t['role'] in ('body', 'label')]
            target = body_target(J, s, mode)
            empty = None
            if s['src'] == 'html':
                empty = s['raw'].get('empty_ratio')
            elif pixels:
                px = pixels.get(n)
                empty = px.get('bottom_free') if px else None
            if empty is not None and body and empty > P['empty_ratio'] and min(body) < target and not D.ing(s, 'dividers'):
                add('G5', f'{round(empty * 100)}% висоти порожньо, текст від {r1(min(body))} pt', measured=round(empty, 3), threshold=P['empty_ratio'], unit='ratio', op='<=', evidence='bottom', key='empty')
            if s['src'] == 'html':
                # content cards only: chips, bars and headers below 64 design px have no bottom padding to balance
                bad = [c for c in s['raw'].get('cards') or [] if c.get('gap_bottom_px') is not None and c.get('pad_top_px') and c['box'][3] >= 64
                       and c['gap_bottom_px'] > c['pad_top_px'] * (1 + P['card_pad_tol']) + 1]
                if bad:
                    w = max(bad, key=lambda c: c['gap_bottom_px'] - c['pad_top_px'])
                    add('G5', f"{len(bad)} карток з порожнім низом до {r1(w['gap_bottom_px'] * PX2PT)} pt при верхньому відступі {r1(w['pad_top_px'] * PX2PT)} pt",
                        measured=r1(w['gap_bottom_px'] * PX2PT), threshold=r1(w['pad_top_px'] * PX2PT * (1 + P['card_pad_tol'])), unit='pt', op='<=', evidence=w['sel'], key='cards')
                # dead space inside a card (a note pinned by margin-top:auto in equal-height cards) while its text is small
                dead = []
                for c in s['raw'].get('cards') or []:
                    if not c.get('max_inner_gap_px') or c['box'][3] < 64 or c['max_inner_gap_px'] <= P['empty_ratio'] * c['box'][3]:
                        continue
                    cb = [v * PX2PT for v in c['box']]
                    inner = [t['size'] for t in texts if t['role'] in ('body', 'label') and t['box'] and t['box'][0] >= cb[0] - 1 and t['box'][1] >= cb[1] - 1
                             and t['box'][0] + t['box'][2] <= cb[0] + cb[2] + 1 and t['box'][1] + t['box'][3] <= cb[1] + cb[3] + 1]
                    if inner and min(inner) < target:
                        dead.append(c)
                if dead:
                    w = max(dead, key=lambda c: c['max_inner_gap_px'] / c['box'][3])
                    ratio = w['max_inner_gap_px'] / w['box'][3]
                    add('G5', f"{len(dead)} карток з порожнім проміжком усередині до {round(ratio * 100)}% висоти картки ({r1(w['max_inner_gap_px'] * PX2PT)} pt), текст менший за {target} pt",
                        measured=round(ratio, 3), threshold=P['empty_ratio'], unit='ratio', op='<=', evidence=w['sel'], key='inner')
            elif s['src'] == 'pdf' and not pixels:
                J.cannot('G5', n, 'немає pixels.json: порожнє місце внизу не виміряно')

        # ---- Y1 type scale and floors
        if J.on('Y1'):
            P = J.par('Y1', mode)
            below, soft = [], []
            target = body_target(J, s, mode)
            for t in texts:
                if t['in_shape'] or t['role'] == 'title':
                    continue
                floor = P['footer_pt'] if t['role'] == 'footer' else P['eyebrow_min_pt'] if t['role'] == 'eyebrow' else P['floor_pt']
                if t['size'] < floor - 0.05:
                    below.append((t, floor))
                elif t['role'] in ('body', 'label') and t['size'] < target - 0.05:
                    soft.append(t)
            if below:
                t, floor = min(below, key=lambda x: x[0]['size'] - x[1])
                w = sum(x[0]['words'] for x in below)
                add('Y1', f"{w} слів нижче порогу (мін. {r1(t['size'])} pt, роль {t['role']})", measured=r1(t['size']), threshold=floor, unit='pt', op='>=', evidence=t['sel'], key='floor')
            if soft:
                t = min(soft, key=lambda x: x['size'])
                w = sum(x['words'] for x in soft)
                add('Y1', f"{w} слів основного тексту нижче {target} pt", measured=r1(t['size']), threshold=target, unit='pt', op='>=', evidence=t['sel'], severity='бажано', key='body')
            if title and mode == 'talk' and P.get('title_pt'):
                if D.ing(s, 'dividers') and s['archetype'] != 'title' and P.get('divider_pt'):
                    lo, hi = P['divider_pt']
                elif not D.ing(s, 'dividers'):
                    lo, hi = P['title_pt']
                else:
                    lo = hi = None
                if lo is not None and not lo - 0.05 <= title['size'] <= hi + 0.05:
                    add('Y1', f"заголовок {r1(title['size'])} pt поза діапазоном", measured=r1(title['size']), threshold=f'{lo}..{hi}', unit='pt', op='in', evidence='title', severity='бажано', key='title')
            if title and not D.ing(s, 'dividers'):
                body = [t['size'] for t in texts if t['role'] in ('body', 'label')]
                if body and title['size'] < P['levels_ratio'] * max(body) - 0.05:
                    add('Y1', f"заголовок {r1(title['size'])} pt лише в {round(title['size'] / max(body), 2)} раза більший за текст", measured=round(title['size'] / max(body), 2), threshold=P['levels_ratio'], unit='ratio', op='>=', evidence='title', severity='бажано', key='levels')

        # ---- Y3 centred text
        if J.on('Y3'):
            lim = J.par('Y3', mode)['centred_lines_max']
            if s['src'] == 'html':
                hits = [t for t in texts if t['align'] == 'center' and t['role'] in ('body', 'label') and t['lines'] > lim]
                if hits:
                    t = max(hits, key=lambda t: t['lines'])
                    add('Y3', f"центрований блок у {t['lines']} рядків", measured=t['lines'], threshold=lim, unit='lines', op='<=', evidence=t['sel'])
            else:
                blk = pdf_centred_blocks(s, lim)
                if blk:
                    add('Y3', f'центрований блок у {blk[0]} рядків ({len(blk[1])} блоків)', measured=blk[0], threshold=lim, unit='lines', op='<=', evidence=f'runs від y {r1(blk[2])}')

        # ---- Y6 uppercase Cyrillic with digits in mono
        if J.on('Y6'):
            hits = [t for t in texts if t['mono'] and CYR.search(t['text']) and re.search(r'\d', t['text']) and re.search('[зЗоОбБ]', t['text'])
                    and (t['transform'] == 'uppercase' or (s['src'] == 'pdf' and t['text'] == t['text'].upper()))]
            if hits:
                add('Y6', f'{len(hits)} рядків капсом кирилиці з цифрами в моноширинному', measured=len(hits), threshold=J.par('Y6', mode)['hits_max'], unit='hits', op='<=', evidence=f"{hits[0]['sel']}: {quote(hits[0]['text'], 4)}")

        # ---- C1 text contrast, C3 gradient text
        if J.on('C1'):
            P = J.par('C1', mode)
            fails, unknown = {}, 0
            for t in texts:
                large = t['size'] >= P['large_pt'] - 0.05 or (t['bold'] and t['size'] >= P['large_bold_pt'] - 0.05)
                need = P['large'] if large else P['body']
                cols = t['gradient'] if t['gradient'] else [t['color']]
                if s['src'] == 'pdf' and t['color'] == '#000000' and t['bg'] and rel_lum(t['bg']) < M['dark_bg_max']:
                    J.cannot('C3', n, 'текст #000000 на темному тлі: чорний або градієнтний (L78)', t['sel'])
                    continue
                if not t['bg'] or not all(is_hex(c) for c in cols if c) or not any(cols):
                    unknown += t['words']
                    continue
                r = min(contrast(c, t['bg']) for c in cols if c)
                if r < need - 0.005:
                    k = (cols[0], t['bg'], need)
                    f = fails.setdefault(k, {'r': r, 'w': 0, 'sel': t['sel'], 'need': need})
                    f['w'] += t['words']
                    f['r'] = min(f['r'], r)
            for (c, bg, need), f in sorted(fails.items(), key=lambda kv: kv[1]['r']):
                add('C1', f"{c} на {bg}: {f['r']:.2f}:1, {f['w']} слів", measured=round(f['r'], 2), threshold=need, unit='ratio', op='>=', evidence=f['sel'], key=(c, bg))
            if unknown:
                J.cannot('C1', n, f'{unknown} слів на градієнті, зображенні чи невідомому тлі')
        if J.on('C3'):
            P = J.par('C3', mode)
            for t in texts:
                if t['gradient'] and (t['size'] < P['min_pt'] or t['words'] > P['words_max']):
                    add('C3', f"градієнтний текст {r1(t['size'])} pt, {t['words']} слів", measured=r1(t['size']), threshold=P['min_pt'], unit='pt', op='>=', evidence=t['sel'], key=t['sel'])

        # ---- V4 live text on canvas
        if J.on('V4'):
            P = J.par('V4', mode)
            off = [t for t in s['texts'] if t['words'] and (t.get('offcanvas') or (t['box'] and (t['box'][0] < -1 or t['box'][1] < -1 or t['box'][0] + t['box'][2] > s['W'] + 1 or t['box'][1] + t['box'][3] > s['H'] + 1)))]
            if off:
                t = off[0]
                where = f"y={r1(s['raw']['runs'][t['i']]['y'])}" if s['src'] == 'pdf' else t['sel']
                add('V4', f"{sum(t['words'] for t in off)} слів поза полотном", measured=len(off), threshold=0, unit='elements', op='<=', evidence=where, key='offcanvas')
            if title and s['src'] == 'html' and (not title.get('visible', True) or title.get('covered')):
                add('V4', 'заголовок схований або перекритий', evidence='title', key='title')
            if s['words'] <= P['raster_words_max'] and s['images'] and not D.ing(s, 'raster_exempt'):
                add('V4', f"{s['words']} живих слів і {s['images']} зображень: підозра на текст у растрі", measured=s['words'], threshold=P['raster_words_max'], unit='words', op='>', evidence='images', key='raster')

        # ---- V7 code line
        if J.on('V7'):
            P = J.par('V7', mode)
            if s['src'] == 'html':
                code = [{'size': c['size_px'] * PX2PT, 'sel': c['sel']} for c in s['raw'].get('code') or [] if c.get('size_px')]
                curly = sum(c.get('curly', 0) for c in s['raw'].get('code') or [])
            else:
                code = [t for t in texts if t['mono']]
                curly = sum(len(CURLY.findall(t['text'])) for t in code)
            if curly > P['curly_quotes_max']:
                add('V7', f'{curly} кручених лапок у коді', measured=curly, threshold=P['curly_quotes_max'], unit='chars', op='<=', evidence='code', severity='критично', key='curly')
            small = [t for t in code if t['size'] < P['code_pt'] - 0.05]
            if small:
                t = min(small, key=lambda t: t['size'])
                add('V7', f"код {r1(t['size'])} pt", measured=r1(t['size']), threshold=P['code_pt'], unit='pt', op='>=', evidence=t['sel'], key='size')

        # ---- D1 words and zones
        if J.on('D1'):
            P = J.par('D1', mode)
            w = s['words']
            if mode == 'talk' and w > P['words_hard']:
                add('D1', f'{w} слів на слайді доповіді', measured=w, threshold=P['words_hard'], unit='words', op='<=', evidence='slide', severity='критично', key='words')
            elif w > P['words_max']:
                add('D1', f'{w} слів', measured=w, threshold=P['words_max'], unit='words', op='<=', evidence='slide', severity='бажано', key='words')
            if mode == 'talk' and s['src'] == 'html' and s['raw'].get('zones', 0) > P['zones_max']:
                add('D1', f"{s['raw']['zones']} зон", measured=s['raw']['zones'], threshold=P['zones_max'], unit='zones', op='<=', evidence='.body', severity='бажано', key='zones')

        # ---- D2 archetype budgets
        if J.on('D2') and not s.get('arch_inferred'):
            a = J.A.get(s['archetype'] or '')
            if not a:
                if D.known and not s['archetype']:
                    add('D2', 'слайд без архетипу', evidence='data-archetype', key='none')
            else:
                amode = mode if a['mode'] == 'any' else a['mode']
                if a['mode'] == 'reading' and mode == 'talk' and not s['appendix']:
                    add('D2', f"архетип читання {s['archetype']} в основному потоці доповіді", evidence=s['archetype'], key='mode')
                eff_mode = mode
                wmax = a['words_max'] if eff_mode == amode and a['words_max'] is not None else J.par('D1', eff_mode)['words_max']
                if s['words'] > wmax:
                    add('D2', f"{s['words']} слів для {s['archetype']}", measured=s['words'], threshold=wmax, unit='words', op='<=', evidence=s['archetype'], key='words')
                mn = a['min_pt'] if eff_mode == amode and a['min_pt'] is not None else J.par('Y1', eff_mode)['floor_pt']
                sizes = [t['size'] for t in texts if t['role'] not in ('footer', 'eyebrow') and not t['in_shape']]
                if sizes and min(sizes) < mn - 0.05:
                    add('D2', f"найменший текст {r1(min(sizes))} pt для {s['archetype']}", measured=r1(min(sizes)), threshold=mn, unit='pt', op='>=', evidence=s['archetype'], key='size')

        # ---- S6 visible title or caption
        if J.on('S6'):
            P = J.par('S6', mode)
            ok = title and title.get('visible', True) and not title.get('covered')
            if not ok:
                caps = [t for t in texts if t['role'] == 'label' and 0 < t['words'] <= P['caption_words_max']]
                if not (s['archetype'] == 'photo' and caps):
                    add('S6', 'немає видимого заголовка чи підпису', evidence='title', key='title')
            if s['archetype'] == 'demo-still' and s['src'] == 'html' and not s['raw'].get('demo_marker'):
                add('S6', 'demo-still без позначки демо', evidence='.demo-pill', key='marker')

        # ---- S1 on the PDF path from plan media
        if J.on('S1') and s['src'] == 'pdf':
            P = J.par('S1', mode)
            media = (s.get('plan') or {}).get('media') or []
            for m in media:
                try:
                    eff = m['ui_px'] * m['placed_pt'] / m['native_px']
                except (KeyError, TypeError, ZeroDivisionError):
                    continue
                if eff < P['eff_min_pt'] - 0.05:
                    add('S1', f"текст інтерфейсу {eff:.1f} pt на скріншоті", measured=round(eff, 1), threshold=P['eff_min_pt'], unit='pt', op='>=', evidence=quote(m.get('file', 'media'), 3), key=m.get('file'))
            if not media and s['images']:
                J.cannot('S1', n, f"{s['images']} зображень без plan.slides[].media: ефективний розмір тексту невідомий")


def pdf_lines(s, roles=('body', 'code', 'label')):
    """Runs on one baseline that touch each other form a line (colour or kerning splits re-joined)."""
    runs = sorted([t for t in live_texts(s, roles)], key=lambda t: (round(t['baseline'], 1), t['box'][0]))
    lines = []
    for t in runs:
        ln = lines[-1] if lines else None
        if ln and abs(ln['y'] - t['baseline']) < 0.3 * t['size'] and -1 <= t['box'][0] - ln['x1'] < 1.5 * t['size']:
            ln['text'] += ' ' + t['text']
            ln['x1'] = max(ln['x1'], t['box'][0] + t['box'][2])
            ln['size'] = max(ln['size'], t['size'])
            ln['runs'].append(t)
        else:
            lines.append({'y': t['baseline'], 'x0': t['box'][0], 'x1': t['box'][0] + t['box'][2], 'size': t['size'], 'text': t['text'], 'runs': [t],
                          'box': t['box']})
    for ln in lines:
        ln['box'] = [ln['x0'], ln['y'] - 0.8 * ln['size'], ln['x1'] - ln['x0'], ln['size']]
        ln['sel'] = ln['runs'][0]['sel']
    return lines


def pdf_centred_blocks(s, lim):
    blocks = []
    for ln in sorted(pdf_lines(s), key=lambda l: l['y']):
        c = (ln['x0'] + ln['x1']) / 2
        for b in blocks:
            last = b[-1]
            if abs(c - last['c']) <= 2 and abs(ln['size'] - last['size']) < 0.6 and 0 < ln['y'] - last['y'] <= 1.7 * ln['size']:
                b.append({**ln, 'c': c})
                break
        else:
            blocks.append([{**ln, 'c': c}])
    blocks = [b for b in blocks if len(b) > lim and max(l['x0'] for l in b) - min(l['x0'] for l in b) > 4]
    if not blocks:
        return None
    big = max(blocks, key=len)
    return (len(big), blocks, big[0]['y'])


# ------------------------------------------------------------------ deck-level checks (both engines)
def deck_checks(J, D, slides, pixels, pixels_doc):
    M = J.M
    main = [s for s in slides if not s['appendix']]
    modes = {D.smode(s) for s in slides}
    # N1
    if J.on('N1'):
        if not D.declared:
            J.add('N1', None, 'режим не оголошено (plan.mode або --mode): судимо як talk', evidence='plan.mode', key='mode')
        for m in sorted({D.smode(s) for s in main}):
            ws = [s['words'] for s in main if D.smode(s) == m]
            med = median(ws)
            lim = J.par('N1', m)['median_words_max']
            if med > lim:
                J.add('N1', None, f'медіана {med:g} слів на слайд ({m})', measured=med, threshold=lim, unit='words', op='<=', mode=m, evidence='main flow', key=m)
    # N2 rendered: dividers show n/N
    if J.on('N2'):
        if not D.known:
            J.skip_check('N2', 'архетипи невідомі (немає плану чи data-archetype)')
        for s in slides:
            if s['archetype'] == 'divider' and not any(re.search(r'\b\d+\s*/\s*\d+\b', t['text']) for t in s['texts']):
                J.add('N2', s['n'], 'divider без n/N', evidence='divider', mode=D.smode(s), key='nN')
    # N3 title slide
    if J.on('N3') and slides:
        s = slides[0]
        P = J.par('N3', D.smode(s))
        t = s['title']
        rest = [x for x in live_texts(s) if x['role'] not in ('title', 'footer')]
        if t and rest:
            sub = max(rest, key=lambda x: x['size'])
            if t['size'] < P['title_ratio_min'] * sub['size'] - 0.05:
                J.add('N3', 1, f"заголовок {r1(t['size'])} pt лише в {round(t['size'] / sub['size'], 2)} раза більший за підзаголовок", measured=round(t['size'] / sub['size'], 2), threshold=P['title_ratio_min'], unit='ratio', op='>=', evidence=sub['sel'], key='ratio')
            lo, hi = P['context_pt']
            # a context line is words (date, event, version): hero values and digit-dominant runs (proof numbers) are not
            ctx = [x for x in rest if x['role'] != 'hero' and sum(c.isdigit() for c in x['text']) < sum(c.isalpha() for c in x['text'])]
            if not any(lo - 0.05 <= x['size'] <= hi + 0.05 for x in ctx):
                J.add('N3', 1, f'немає рядка контексту {lo}-{hi} pt', threshold=f'{lo}..{hi}', unit='pt', op='in', evidence='slide 1', key='context')
    # N5 zoom drift
    if J.on('N5'):
        for a, b in zip(slides, slides[1:]):
            if b['archetype'] == 'zoom' and a['archetype'] in ('map', 'zoom') and a['title'] and b['title']:
                d = max(abs(a['title']['box'][0] - b['title']['box'][0]), abs(a['title']['box'][1] - b['title']['box'][1]), abs(a['title']['size'] - b['title']['size']))
                lim = max(J.par('N5', D.smode(b))['drift_pt'], M['tol_pt'])
                if d > lim:
                    J.add('N5', b['n'], f'рамка заголовка зсунулась на {r1(d)} pt відносно карти', measured=r1(d), threshold=J.par('N5', D.smode(b))['drift_pt'], unit='pt', op='<=', evidence='title', mode=D.smode(b))
    # N7, N13 rendered lists
    plan = D.plan or {}
    lists = plan.get('lists') or {}
    if J.on('N7') and plan:
        for s in slides:
            se = (s.get('plan') or {}).get('series')
            if not se:
                continue
            if s['src'] == 'html':
                if not any(l.get('name') == se['list'] for l in s['raw'].get('lists') or []):
                    J.add('N7', s['n'], f"спиця без смуги прогресу списку {se['list']}", evidence='[data-list]', mode=D.smode(s))
            else:
                label = next((x['label'] for x in lists.get(se['list'], []) if x['id'] == se['item']), None)
                if label and not any(label in t['text'] for t in s['texts']):
                    J.add('N7', s['n'], 'на спиці немає мітки пункту хаба', evidence=quote(label, 4), mode=D.smode(s))
    if J.on('N13'):
        for s in slides:
            if s['src'] == 'html':
                for l in s['raw'].get('lists') or []:
                    want = [x['label'] for x in lists.get(l.get('name'), [])]
                    if want and l.get('labels') and l['labels'] != want[:len(l['labels'])] and set(l['labels']) - set(want):
                        J.add('N13', s['n'], f"список {l['name']} не збігається з plan.lists", evidence=f"[data-list={l['name']}]", mode=D.smode(s), key=l['name'])
            if s['archetype'] == 'divider' and plan and s['title']:
                pl = s.get('plan') or {}
                part = next((p for p in plan.get('parts', []) if p['id'] == pl.get('part')), None)
                if part and s['title']['text'].strip() != part['question'].strip():
                    J.add('N13', s['n'], 'заголовок divider не дорівнює питанню частини', evidence=quote(s['title']['text']), mode=D.smode(s), key='divider')
    # N8 neighbour density
    if J.on('N8'):
        seq = [s for s in main if D.smode(s) == 'talk' and not D.ing(s, 'dividers')]
        for a, b in zip(seq, seq[1:]):
            if b['n'] - a['n'] > 1 and any(x['n'] for x in slides if a['n'] < x['n'] < b['n'] and D.ing(x, 'dividers')):
                continue
            P = J.par('N8', 'talk')
            big, small = max(a['words'], b['words']), min(a['words'], b['words'])
            if big > P['bridge_words'] and (small == 0 or big / small > P['ratio_max']):
                ratio = 'нескінченність' if small == 0 else round(big / small, 1)
                J.add('N8', b['n'], f"сусіди {a['n']} і {b['n']}: {a['words']} і {b['words']} слів", measured=ratio if small else None, threshold=P['ratio_max'], unit='ratio', op='<=', evidence=f"{a['n']}-{b['n']}", mode='talk')
    # N10 rendered close
    if J.on('N10'):
        for s in slides:
            mode = D.smode(s)
            P = J.par('N10', mode)
            if not P:
                continue
            if s['src'] == 'html' and s['archetype'] not in ('close', 'cta') and s['raw'].get('links_underlined'):
                J.add('N10', s['n'], f"{s['raw']['links_underlined']} підкреслених посилань поза закриттям", measured=s['raw']['links_underlined'], threshold=0, unit='links', op='<=', evidence='a', mode=mode, key='links')
            if s['archetype'] in ('close', 'cta') and 'url_chars_max' in P:
                for t in live_texts(s):
                    for m in URL.finditer(t['text']):
                        u = m.group(0)
                        if len(u) > P['url_chars_max']:
                            J.add('N10', s['n'], f'URL {len(u)} символів', measured=len(u), threshold=P['url_chars_max'], unit='chars', op='<=', evidence=t['sel'], mode=mode, key='url')
                        elif t['size'] < P['pill_min_pt'] - 0.05:
                            J.add('N10', s['n'], f"URL {r1(t['size'])} pt", measured=r1(t['size']), threshold=P['pill_min_pt'], unit='pt', op='>=', evidence=t['sel'], mode=mode, key='urlsize')
    # T10 without plan: one dash form deck-wide
    if J.on('T10') and not D.plan:
        dash = [s['n'] for s in slides if any(DASH_RANGE.search(t['text']) for t in live_texts(s))]
        hyph = [s['n'] for s in slides if any(HYPHEN_RANGE.search(t['text']) for t in live_texts(s))]
        if dash and hyph:
            J.add('T10', None, f'дві форми діапазонів: тире на {len(dash)} слайдах, дефіс на {len(hyph)}', measured=2, threshold=1, unit='forms', op='<=', evidence=f'слайди {fmt_list(dash[:8])}', key='mixed')
        elif dash:
            J.info.append({'check': 'T10', 'note': f'діапазони через тире на слайдах {fmt_list(dash)}; без плану dash_policy невідома'})
    # T4 series label used as a title (L15)
    if J.on('T4'):
        t4_series(J, D, slides)
    # T11 duplicates
    if J.on('T11'):
        t11(J, D, slides, pixels_doc)
    # G1 title box token
    if J.on('G1'):
        g1(J, D, slides)
    # Y2 families and scale
    if J.on('Y2'):
        y2(J, D, slides)
    # C4 luminance flips
    if J.on('C4'):
        cls = {n: v.get('class') for n, v in (pixels or {}).items()}
        for s in slides:  # HTML: the slide background decides the family; a dark board on a light slide is not a flip
            if s.get('bg_lum') is not None:
                l = s['bg_lum']
                cls[s['n']] = 'dark' if l <= M['lum_dark_max'] else 'light' if l >= M['lum_light_min'] else 'mid'
        if not cls:
            J.cannot('C4', None, 'немає pixels.json: яскравість слайдів не виміряна')
        flips = 0
        for a, b in zip(slides, slides[1:]):
            ca, cb = cls.get(a['n']), cls.get(b['n'])
            if ca in ('dark', 'light') and cb in ('dark', 'light') and ca != cb:
                if D.ing(a, 'dividers') or D.ing(b, 'dividers'):
                    continue
                flips += 1
                J.add('C4', b['n'], f"перемикання яскравості {a['n']} ({ca}) на {b['n']} ({cb}) без роздільника", measured=1, threshold=J.par('C4', D.smode(b))['flips_max'], unit='flips', op='<=', evidence=f"{a['n']}-{b['n']}", mode=D.smode(b))
        if cls and not D.known:
            J.info.append({'check': 'C4', 'note': 'архетипи невідомі: роздільники не виключено з перемикань'})
    # K1 page numbers
    if J.on('K1'):
        k1(J, D, slides)
    # K2 template families: proxy = background treatment (slide background colour in HTML, modal page colour
    # from pixels.json on a PDF); the reviewer confirms the families on the contact sheet
    if J.on('K2'):
        sig = Counter()
        for s in slides:
            if s['src'] == 'html' and s['raw'].get('bg'):
                b = s['raw']['bg']
                sig[(b.get('kind'), b.get('color'))] += 1
            elif pixels and s['n'] in pixels:
                sig[(pixels[s['n']].get('class'), pixels[s['n']].get('bg'))] += 1
        lim = J.par('K2', D.mode if D.mode in ('talk', 'reading') else 'talk')['families_max']
        if not sig:
            J.cannot('K2', None, 'тло слайдів не виміряно (немає pixels.json)')
        elif len(sig) > lim:
            top = ', '.join(f'{k[1] or k[0]} ({v})' for k, v in sig.most_common(6))
            J.add('K2', None, f'{len(sig)} варіантів тла слайдів: {top}; підтвердити родини на контактному аркуші', measured=len(sig), threshold=lim, unit='families', op='<=', evidence='contact sheet')
    # K3 series frame lock
    if J.on('K3'):
        k3(J, D, slides)
    # V7 one mono family (PDF; the HTML path checks it per font pass)
    if J.on('V7') and slides and slides[0]['src'] == 'pdf':
        fams = sorted({family_key(t['family']) for s in slides for t in live_texts(s) if t['mono']})
        if len(fams) > 1:
            J.add('V7', None, f"{len(fams)} моноширинні родини в коді: {', '.join(fams)}", measured=len(fams), threshold=1, unit='families', op='<=', evidence='mono runs', key='mono')
    silent = [s['n'] for s in slides if s['words'] <= M['silent_words_max']]
    dense = [s['n'] for s in slides if D.smode(s) == 'talk' and s['words'] > J.par('D1', 'talk')['words_hard']]
    ws = [s['words'] for s in slides]
    J.info.append({'check': 'D1', 'note': f"слів: медіана {median(ws):g}, середнє {round(sum(ws) / max(len(ws), 1), 1)}; тихі (<= {M['silent_words_max']}) {len(silent)}: {fmt_list(silent)}; щільні talk (> {J.par('D1', 'talk')['words_hard']}) {len(dense)}: {fmt_list(dense)}"})
    # V4 summary for P2 is computed by the caller


def fmt_list(ns):
    ns = sorted(set(ns))
    out, i = [], 0
    while i < len(ns):
        j = i
        while j + 1 < len(ns) and ns[j + 1] == ns[j] + 1:
            j += 1
        out.append(str(ns[i]) if i == j else f'{ns[i]}-{ns[j]}')
        i = j + 1
    return ', '.join(out)


MARK_TAIL = re.compile(r'(?<=[^\W_])([*†‡¹²³⁴⁵⁶⁷⁸⁹⁰]+)(?=[\s.,;:)]|$)')
MARK_HEAD = re.compile(r'^\s*([*†‡¹²³⁴⁵⁶⁷⁸⁹⁰]+|\d{1,2}(?=[\s.)]))')


SERIES = re.compile(r'^(.{4,}?)\s*[|:]\s')


def t4_series(J, D, slides):
    """T4 (L15): a leading segment before '|' or ':' that repeats on two or more titles anywhere in the deck is a
    series label spent as a title; it belongs in an eyebrow, the title carries the per-slide claim."""
    seg = defaultdict(list)
    for s in slides:
        m = SERIES.match((s['title'] or {}).get('text') or '')
        if m:
            seg[' '.join(m.group(1).lower().split())].append(s)
    for label, ss in seg.items():
        if len(ss) < 2:
            continue
        ns = [x['n'] for x in ss]
        for s in ss:
            J.add('T4', s['n'], f"заголовок починається з мітки серії «{quote(label, 4)}» (слайди {fmt_list(ns)}): мітку в eyebrow, заголовок на твердження",
                  measured=len(ss), threshold=1, unit='slides', op='<=', evidence=quote(s['title']['text']), mode=D.smode(s), key=('series', label))


def clusters_of(pairs):
    """Connected groups of slide pairs (union-find), each with its slides and the pairs inside it."""
    up = {}

    def find(x):
        while up.setdefault(x, x) != x:
            up[x] = up[up[x]]
            x = up[x]
        return x
    for p in pairs:
        up[find(p['a'])] = find(p['b'])
    out = defaultdict(list)
    for p in pairs:
        out[find(p['a'])].append(p)
    return [(sorted({x for p in ps for x in (p['a'], p['b'])}), ps) for ps in out.values()]


def t11(J, D, slides, pixels_doc):
    P = J.par('T11', 'talk')
    k = P['prefix_words']

    def items(s):
        src = pdf_lines(s) if s['src'] == 'pdf' else live_texts(s, ('body', 'label', 'code'))
        out = []
        for t in src:
            w = [x.lower().strip('.,;:!?«»"()') for x in tokens(t['text'])]
            if w and re.fullmatch(r'\d{1,2}', w[0]):  # a list number (a PDF draws a CSS counter as its own run) is not item text
                w = w[1:]
            if len(w) >= k:
                out.append((' '.join(w[:k]), t))
        return out
    per = {s['n']: items(s) for s in slides}
    freq = Counter()
    for n, its in per.items():
        for key in {p for p, _ in its}:
            freq[key] += 1
    chrome = {key for key, c in freq.items() if c >= 3}
    for s in slides:
        n, seen, dups = s['n'], {}, []
        for key, t in per[n]:
            if key in chrome:
                continue
            if key in seen and abs(seen[key]['box'][1] - t['box'][1]) > 1:
                dups.append(t)
            seen.setdefault(key, t)
        if dups:
            J.add('T11', n, f'{len(dups)} рядків повторюють перші 5 слів іншого пункту на цьому слайді', measured=len(dups), threshold=0, unit='items', op='<=', evidence=quote(dups[0]['text'], 5), mode=D.smode(s), key='in')
    build = set()  # a zoom repeats its map and a declared pair shares its pattern (N4, N5, C6)
    for a, b in zip(slides, slides[1:]):
        if b['archetype'] == 'zoom' or ((a.get('plan') or {}).get('pair') and (b.get('plan') or {}).get('pair')):
            build.add((a['n'], b['n']))
    for a, b in zip(slides, slides[1:]):
        if (a['n'], b['n']) in build:
            continue
        common = {p for p, _ in per[a['n']]} & {p for p, _ in per[b['n']]} - chrome
        if common:
            J.add('T11', b['n'], f"{len(common)} пунктів повторюють слайд {a['n']}", measured=len(common), threshold=0, unit='items', op='<=', evidence=quote(sorted(common)[0], 5), severity='бажано', mode=D.smode(b), key=('sib', a['n']))
    for s in slides:
        if s['src'] == 'pdf':
            dbl = [t for t in live_texts(s) if '  ' in t['text']]
            if dbl:
                J.add('T11', s['n'], f'{len(dbl)} подвійних пробілів', measured=len(dbl), threshold=0, unit='hits', op='<=', evidence=quote(dbl[0]['text'], 4), severity='косметика', mode=D.smode(s), key='dbl')
        texts = [t for t in s['texts'] if t['words'] or t['text'].strip()]
        body = [t['size'] for t in live_texts(s, ('body', 'label'))]
        med = median(body) if body else 0
        notes = {m.group(1) for t in texts if (m := MARK_HEAD.match(t['text'])) and len(t['text'].strip()) > len(m.group(1)) + 1}
        marks = set()
        for t in texts:
            if t['role'] in ('footer', 'code') or t['mono'] or (MARK_HEAD.match(t['text']) and len(t['text'].strip()) > 3):
                continue
            for m in MARK_TAIL.finditer(t['text']):
                marks.add(m.group(1))
            bare = t['text'].strip()
            if re.fullmatch(r'[*†‡¹²³⁴⁵⁶⁷⁸⁹⁰]{1,3}|\d{1,2}', bare) and med and t['size'] <= 0.75 * med:
                marks.add(bare)
        orphan = sorted(m for m in marks if m not in notes)
        if orphan:
            J.add('T11', s['n'], f"позначка виноски {', '.join(orphan)} без самої виноски", measured=len(orphan), threshold=0, unit='marks', op='<=', evidence=', '.join(orphan), severity='бажано', mode=D.smode(s), key='mark')
    # near-identical slides: a pixel match (dHash at or below dup_hamming_max) is a finding only when the text
    # backs it (titles share their first prefix_words words, or the content words of the prose overlap, shared
    # over all, at the T6 cut);
    # a pixel-only match (one layout, different text) goes to visual_hints for the contact sheet (L73).
    # Code, eyebrows and footers repeat by design across a series, so only titles, body and labels count.
    byn = {s['n']: s for s in slides}

    def content_stems(s):
        return stems(' '.join(t['text'] for t in live_texts(s) if t['role'] not in ('eyebrow', 'footer', 'code')))

    def head(s):
        return [x.lower().strip('.,;:!?«»"()') for x in tokens((s['title'] or {}).get('text', ''))]

    def backed(a, b):
        ha, hb = head(a), head(b)
        if ha and (ha == hb or (len(ha) >= k and ha[:k] == hb[:k])):
            return True
        sa, sb = content_stems(a), content_stems(b)
        return bool(sa and sb) and len(sa & sb) / len(sa | sb) >= J.par('T6', D.smode(b))['overlap_max'] - 1e-9
    text_dup, pixel_dup = [], []
    for p in (pixels_doc or {}).get('dup_pairs') or []:
        a, b = byn.get(p['a']), byn.get(p['b'])
        if not a or not b or (p['a'], p['b']) in build or (D.ing(a, 'dividers') and D.ing(b, 'dividers')):
            continue  # builds repeat by design; dividers share one style (N2)
        (text_dup if backed(a, b) else pixel_dup).append(p)
    for ns, ps in clusters_of(text_dup):
        hs = [p['hamming'] for p in ps]
        J.add('T11', ns[1], f"слайди {fmt_list(ns)} майже однакові (dHash {min(hs)}-{max(hs)}) і повторюють текст", measured=min(hs),
              threshold=J.M['dup_hamming_max'], unit='bits', op='>', evidence=', '.join(map(str, ns)), severity='бажано', mode=D.smode(byn[ns[1]]), key=('dup', ns[0]))
    for ns, ps in clusters_of(pixel_dup):
        hs = [p['hamming'] for p in ps]
        J.hint('T11', f"схожі мініатюри з різним текстом (dHash {min(hs)}-{max(hs)}): {fmt_list(ns)}", ns)
    near = (pixels_doc or {}).get('near_pairs') or []
    if near:
        J.hint('T11', 'найближчі пари вище dup_hamming_max: ' + ', '.join(
            f"{p['a']}/{p['b']} ({p['hamming']}{', збірка' if (p['a'], p['b']) in build else ''})" for p in near), [x for p in near for x in (p['a'], p['b'])])


def g1(J, D, slides):
    for mode in ('talk', 'reading'):  # the appendix of a talk+appendix deck has its own title token
        g1_mode(J, D, [s for s in slides if D.smode(s) == mode], mode)


def g1_mode(J, D, slides, mode):
    M = J.M
    rows = [s for s in slides if s['title'] and not D.ing(s, 'title_box_exempt')]
    if not rows:
        return
    P = J.par('G1', mode)
    left = [s for s in rows if not s['title'].get('centred')]
    xs = [round(s['title']['box'][0], 1) for s in left]
    ys = [round(s['title'].get('baseline', s['title']['box'][1]), 1) for s in rows]
    zs = [round(s['title']['size'], 1) for s in rows]
    # the token is one real title box: the most frequent joint (x, y, size) among left-aligned titles that keep
    # the G2 safe margin (a title in the edge band is itself a G2 finding, never the token); centred titles
    # carry no x. Without such a title the token has no x and only y and size are compared.
    ybase = lambda s: round(s['title'].get('baseline', s['title']['box'][1]))
    safe = [s for s in left if s['title']['box'][0] >= J.par('G2', mode)['margin_pt'] - M['tol_pt']]
    tok = Counter((round(s['title']['box'][0]), ybase(s), round(s['title']['size'], 1)) for s in safe)
    if tok:
        (mx, my, mz), _ = tok.most_common(1)[0]
        src = [s['n'] for s in safe if (round(s['title']['box'][0]), ybase(s), round(s['title']['size'], 1)) == (mx, my, mz)]
    else:
        (my, mz), _ = Counter((ybase(s), round(s['title']['size'], 1)) for s in rows).most_common(1)[0]
        mx = None
        src = [s['n'] for s in rows if (ybase(s), round(s['title']['size'], 1)) == (my, mz)]
    token = f"{'x ' + str(mx) if mx is not None else 'без x'}, y {my}, {mz} pt"

    def clusters(vals, tol):
        out = []
        for v in sorted(vals):
            if not out or v - out[-1][-1] > tol:
                out.append([v])
            else:
                out[-1].append(v)
        return out
    nx = len(clusters(xs, M['tol_pt'])) + (1 if len(left) < len(rows) else 0)
    sizes = clusters(zs, M['nonint_tol_pt'])
    if len(sizes) > P['title_sizes_max']:
        J.add('G1', None, f"{len(sizes)} розмірів заголовка ({', '.join(f'{c[0]:g}' for c in sizes)} pt), {nx} значень x; токен ({token}) зі слайдів {fmt_list(src)[:60]}",
              measured=len(sizes), threshold=P['title_sizes_max'], unit='sizes', op='<=', evidence='titles', mode=mode, key=('sizes', mode))
    for s in rows:
        t = s['title']
        d = []
        if not t.get('centred') and mx is not None and abs(t['box'][0] - mx) > P['drift_pt']:
            d.append(f"x {r1(t['box'][0])}")
        yv = t.get('baseline', t['box'][1])
        if abs(yv - my) > P['drift_pt']:
            d.append(f'y {r1(yv)}')
        if abs(t['size'] - mz) > P['drift_pt']:
            d.append(f"{r1(t['size'])} pt")
        if d:
            dev = max(abs(t['box'][0] - mx) if not t.get('centred') and mx is not None else 0, abs(yv - my), abs(t['size'] - mz))
            J.add('G1', s['n'], f"рамка заголовка відходить від токена ({token}): {', '.join(d)}", measured=r1(dev), threshold=P['drift_pt'], unit='pt', op='<=', evidence='title', mode=D.smode(s), key='drift')
        if not t.get('centred'):
            padl = (s['raw'].get('padding_px') or [0, 0, 0, 0])[3] * PX2PT if s['src'] == 'html' else 0
            below = [x for x in live_texts(s, ('body', 'label', 'code')) if x['box'] and x['box'][1] > t['box'][1] + t['box'][3] - 1 and x['box'][0] >= padl - 1]
            if below:
                cl = min(x['box'][0] for x in below)
                if t['box'][0] - cl > P['drift_pt']:
                    J.add('G1', s['n'], f"заголовок на {r1(t['box'][0] - cl)} pt правіше за лівий край вмісту", measured=r1(t['box'][0] - cl), threshold=P['drift_pt'], unit='pt', op='<=', evidence='title', mode=D.smode(s), key='left')


def y2(J, D, slides):
    M = J.M
    P = J.par('Y2', 'talk')
    fams, names = Counter(), Counter()
    for s in slides:
        for t in s['texts']:
            names[t.get('font') or t['family']] += 1
        for t in live_texts(s):
            fams[(family_key(t['family']), bool(t['mono']))] += t['words']
    if len(fams) > P['families_max']:
        top = ', '.join(f'{k[0]}{" (mono)" if k[1] else ""}' for k, _ in fams.most_common(6))
        J.add('Y2', None, f'{len(fams)} родин шрифтів ({len(names)} назв): {top}', measured=len(fams), threshold=P['families_max'], unit='families', op='<=', evidence='fonts', key='families')
    scale = None
    if slides and slides[0]['src'] == 'html':
        ts = (D.metrics_deck or {}).get('type_scale_px') if hasattr(D, 'metrics_deck') else None
        if ts:
            scale = sorted({v * PX2PT for k in ('talk', 'reading') for v in (ts.get(k) or [])})
    off, total, where = 0, 0, Counter()
    for s in slides:
        for t in live_texts(s):
            total += t['words']
            if scale:
                bad = not any(abs(t['size'] - v) <= M['scale_tol_pt'] for v in scale)
            else:
                bad = abs(t['size'] - round(t['size'])) > M['nonint_tol_pt']
            if bad:
                off += t['words']
                where[s['n']] += t['words']
    if off > P['offscale_words_max']:
        rule = 'поза оголошеною шкалою' if scale else 'на дробових розмірах pt'
        J.add('Y2', None, f'{off} слів ({round(100 * off / max(total, 1), 1)}%) {rule}; слайди {fmt_list(list(where))[:120]}', measured=off, threshold=P['offscale_words_max'], unit='words', op='<=', evidence='sizes', key='scale')


def k1(J, D, slides):
    P = J.par('K1', 'talk')
    rows = [s for s in slides if not D.ing(s, 'dividers')]
    have = [s for s in rows if s['pn']]
    J.info.append({'check': 'K1', 'note': f"номери сторінок на {sum(1 for s in slides if s['pn'])} з {len(slides)} слайдів"})
    boxes = [s['pn']['box'] for s in have if s['pn'].get('box')]
    left = modal([round(b[0]) for b in boxes])
    right = modal([round(b[0] + b[2]) for b in boxes])
    top = modal([round(b[1]) for b in boxes])
    pos = (left, right, top) if boxes else None
    for s in rows:
        pn = s['pn']
        if not pn:
            J.add('K1', s['n'], 'немає номера сторінки', evidence='page number', mode=D.smode(s), key='missing')
            continue
        if pn.get('value') is not None and pn['value'] != s['n']:
            J.add('K1', s['n'], f"номер {pn['value']} не дорівнює позиції {s['n']}", measured=pn['value'], threshold=s['n'], unit='n', op='==', evidence='page number', mode=D.smode(s), key='value')
        if pn.get('size') and pn['size'] < P['pn_min_pt'] - 0.05:
            J.add('K1', s['n'], f"номер {r1(pn['size'])} pt", measured=r1(pn['size']), threshold=P['pn_min_pt'], unit='pt', op='>=', evidence='page number', mode=D.smode(s), key='size')
        if pos and pn.get('box'):
            b = pn['box']
            d = max(min(abs(b[0] - pos[0]), abs(b[0] + b[2] - pos[1])), abs(b[1] - pos[2]))
            if d > P['pn_drift_pt']:
                J.add('K1', s['n'], f'номер зсунутий на {r1(d)} pt від спільної позиції', measured=r1(d), threshold=P['pn_drift_pt'], unit='pt', op='<=', evidence='page number', mode=D.smode(s), key='pos')


def k3(J, D, slides):
    P = J.par('K3', 'talk')
    groups = defaultdict(list)
    for s in slides:
        pl = s.get('plan') or {}
        if pl.get('series'):
            groups[('series', pl['series']['list'])].append(s)
        elif pl.get('pair'):
            groups[('pair', pl['pair']['id'])].append(s)
    if not D.plan:
        cur, key = [], None
        for s in slides:
            t = (s['title'] or {}).get('text', '')
            m = re.match(r'^(.{4,}?)\s*[|:]\s', t)
            k = m.group(1).lower() if m else ' '.join(t.lower().split()[:3]) if len(t.split()) >= 4 else None
            if k and k == key:
                cur.append(s)
            else:
                if len(cur) >= 2:
                    groups[('title', key)] = cur
                cur, key = [s], k
        if len(cur) >= 2:
            groups[('title', key)] = cur
    for (kind, name), ss in groups.items():
        if len(ss) < 2:
            continue
        ref = ss[0]
        rb = modal([round(t['size'], 1) for t in live_texts(ref, ('body', 'label'))])
        for s in ss[1:]:
            d = []
            if ref['title'] and s['title']:
                dt = max(abs(ref['title']['box'][0] - s['title']['box'][0]), abs(ref['title']['box'][1] - s['title']['box'][1]), abs(ref['title']['size'] - s['title']['size']))
                if dt > P['frame_drift_pt']:
                    d.append(f'заголовок зсунуто на {r1(dt)} pt')
            sb = modal([round(t['size'], 1) for t in live_texts(s, ('body', 'label'))])
            if rb and sb and abs(rb - sb) > J.M['tol_pt']:
                d.append(f'основний текст {sb:g} pt проти {rb:g} pt')
            if s['src'] == 'html':
                ia, ib = ref['raw'].get('images') or [], s['raw'].get('images') or []
                if ia and ib:
                    db = max(abs(a - b) for a, b in zip(ia[0]['box'], ib[0]['box'])) * PX2PT
                    if db > P['frame_drift_pt']:
                        d.append(f'зображення зсунуто на {r1(db)} pt')
            if d:
                J.add('K3', s['n'], f"серія {name} від слайда {ref['n']}: {'; '.join(d)}", evidence=f"{ref['n']}-{s['n']}", mode=D.smode(s), key=(kind, name))


# ------------------------------------------------------------------ HTML-only checks
def html_slide_checks(J, D, slides):
    for s in slides:
        n, mode, sid, raw = s['n'], D.smode(s), s['id'], s['raw']
        add = lambda cid, msg, **k: J.add(cid, n, msg, mode=mode, slide_id=sid, **k)
        texts = live_texts(s)
        if J.on('T7'):
            P = J.par('T7', mode)
            for st in raw.get('stats') or []:
                if st.get('value_px') and st.get('body_px') and st['value_px'] < P['hero_ratio_min'] * st['body_px']:
                    add('T7', f"число {r1(st['value_px'] * PX2PT)} pt лише в {round(st['value_px'] / st['body_px'], 2)} раза більше за текст", measured=round(st['value_px'] / st['body_px'], 2), threshold=P['hero_ratio_min'], unit='ratio', op='>=', evidence='.stat .v', key='ratio')
                    break
            labels = [st['label_words'] for st in raw.get('stats') or [] if st.get('label_words') is not None]
            if labels and max(labels) > P['label_words_max']:
                add('T7', f'підпис числа {max(labels)} слів', measured=max(labels), threshold=P['label_words_max'], unit='words', op='<=', evidence='.stat .l', key='label')
            if raw.get('stats') and not any(st.get('has_method') or st.get('slide_method') for st in raw['stats']):
                add('T7', 'числа без бази й методу', evidence='.stat', key='method')
        if J.on('T8') and raw.get('fromto'):
            ft = raw['fromto']
            if ft['from_rows'] != ft['to_rows']:
                add('T8', f"рядків «з» {ft['from_rows']}, «до» {ft['to_rows']}", measured=ft['to_rows'], threshold=ft['from_rows'], unit='rows', op='==', evidence='.from, .to')
        if J.on('G3'):
            P = J.par('G3', mode)
            for d in raw.get('deco') or []:
                b = [v * PX2PT for v in d['box']]
                for t in texts:
                    tb = t['box']
                    gap = max(tb[0] - (b[0] + b[2]), b[0] - (tb[0] + tb[2]), tb[1] - (b[1] + b[3]), b[1] - (tb[1] + tb[3]))
                    if gap < P['decoration_clear_pt']:
                        add('G3', f"декор ближче за {P['decoration_clear_pt']} pt до тексту ({r1(gap)} pt)", measured=r1(gap), threshold=P['decoration_clear_pt'], unit='pt', op='>=', evidence=d['sel'], key=d['sel'])
                        break
        if J.on('G6') and s['archetype'] in (None, 'feature-shot'):
            P = J.par('G6', mode)
            shots = [im for im in raw.get('images') or [] if im.get('shot')]
            if len(shots) == 1 and texts:
                im = shots[0]
                b = [v * PX2PT for v in im['box']]
                pad = [v * PX2PT for v in raw.get('padding_px') or [0, 0, 0, 0]]
                cw = s['W'] - pad[1] - pad[3]
                if cw > 0 and b[2] < 0.8 * cw:
                    share = 1 - b[2] / cw
                    side = [t for t in texts if t['role'] in ('body', 'label') and (t['box'][0] + t['box'][2] <= b[0] + 1 or t['box'][0] >= b[0] + b[2] - 1) and t['box'][1] >= b[1] - 40]
                    lo, hi = P['text_share']
                    if not lo <= share <= hi:
                        add('G6', f'текст займає {round(share * 100)}% ширини', measured=round(share, 2), threshold=f'{lo}..{hi}', unit='ratio', op='in', evidence=im['sel'], key='share')
                    if side:
                        top, bot = min(t['box'][1] for t in side), max(t['box'][1] + t['box'][3] for t in side)
                        dev = max(abs(top - b[1]), abs(bot - (b[1] + b[3])))
                        if dev > P['align_pt']:
                            add('G6', f'зображення не вирівняне з текстом ({r1(dev)} pt)', measured=r1(dev), threshold=P['align_pt'], unit='pt', op='<=', evidence=im['sel'], key='align')
        if J.on('G7'):
            P = J.par('G7', mode)
            if raw.get('framed_depth_max', 0) > P['nesting_max']:
                add('G7', f"{raw['framed_depth_max']} рівні вкладених рамок", measured=raw['framed_depth_max'], threshold=P['nesting_max'], unit='levels', op='<=', evidence='cards', key='depth')
            bad = []
            for st in raw.get('strokes') or []:
                if not (is_hex(st.get('bg')) and is_hex(st.get('color'))) or rel_lum(st['bg']) >= J.M['dark_bg_max']:
                    continue
                w = st['width_px'] * PX2PT
                r = contrast(st['color'], st['bg'])
                if w < P['stroke_min_pt'] - 0.05 or r < P['stroke_contrast']:
                    bad.append((r, w, st))
            if bad:
                r, w, st = min(bad, key=lambda x: x[0])
                add('G7', f"{len(bad)} ліній на темному тлі тонші за {P['stroke_min_pt']} pt або нижче {P['stroke_contrast']}:1 (гірша {r:.2f}:1, {r1(w)} pt)", measured=round(r, 2), threshold=P['stroke_contrast'], unit='ratio', op='>=', evidence=st['sel'], key='strokes')
        if J.on('Y4'):
            P = J.par('Y4', mode)
            lo, hi = P['line_chars']
            bad = [t for t in texts if t['role'] == 'body' and t['lines'] >= 3 and t['cpl'] and not lo <= t['cpl'] <= hi]
            if bad:
                t = max(bad, key=lambda t: abs(t['cpl'] - (lo + hi) / 2))
                add('Y4', f"{len(bad)} абзаців з рядком {t['cpl']} символів", measured=t['cpl'], threshold=f'{lo}..{hi}', unit='chars', op='in', evidence=t['sel'], key='measure')
            narrow = [t for t in texts if t['role'] == 'body' and t['lines'] >= 3 and t['box'][2] < P['column_min_pt'] - 0.5]
            if narrow:
                t = min(narrow, key=lambda t: t['box'][2])
                add('Y4', f"колонка {r1(t['box'][2])} pt", measured=r1(t['box'][2]), threshold=P['column_min_pt'], unit='pt', op='>=', evidence=t['sel'], key='column')
        if J.on('Y5'):
            P = J.par('Y5', mode)
            if raw.get('emphasis_styles', 0) > P['emphasis_styles_max']:
                add('Y5', f"{raw['emphasis_styles']} способи виділення", measured=raw['emphasis_styles'], threshold=P['emphasis_styles_max'], unit='styles', op='<=', evidence='b, strong, em, mark')
        if J.on('C2'):
            P = J.par('C2', mode)
            for tb in raw.get('tables') or []:
                if is_hex(tb.get('header_bg')) and is_hex(tb.get('header_color')):
                    r = contrast(tb['header_color'], tb['header_bg'])
                    if r < P['header'] - 0.005:
                        add('C2', f"шапка таблиці {tb['header_color']} на {tb['header_bg']}: {r:.2f}:1", measured=round(r, 2), threshold=P['header'], unit='ratio', op='>=', evidence=tb['sel'], key=(tb['sel'], 'r'))
                elif tb.get('header_fills'):
                    J.cannot('C2', n, 'тло шапки таблиці невідоме', tb['sel'])
                if tb.get('header_fills', 0) > P['header_fills_max']:
                    add('C2', f"{tb['header_fills']} заливки шапки", measured=tb['header_fills'], threshold=P['header_fills_max'], unit='fills', op='<=', evidence=tb['sel'], severity='бажано', key=(tb['sel'], 'f'))
        if J.on('C6') and raw.get('zoom'):
            P = J.par('C6', mode)
            z = raw['zoom']
            if z.get('active_min_ratio') is not None and z['active_min_ratio'] < P['active_min']:
                add('C6', f"активний текст {z['active_min_ratio']}:1", measured=z['active_min_ratio'], threshold=P['active_min'], unit='ratio', op='>=', evidence='.zoom', key='active')
            if z.get('reveal_px') and z.get('context_px') and z['reveal_px'] / z['context_px'] < P['reveal_ratio_min']:
                add('C6', 'нове менше за повторений контекст', measured=round(z['reveal_px'] / z['context_px'], 2), threshold=P['reveal_ratio_min'], unit='ratio', op='>=', evidence='.reveal', key='reveal')
            for dd in z.get('dim') or []:
                if dd.get('ratio') is not None:
                    J.info.append({'check': 'C6', 'slide': n, 'measured': dd['ratio'], 'note': f"приглушений контекст (ціль близько {P['dim_target']}:1)"})
        if J.on('C7'):
            P = J.par('C7', mode)
            bad = []
            for c in raw.get('cards') or []:
                if not (is_hex(c.get('bg')) and is_hex(c.get('parent_bg'))):
                    continue
                step = contrast(c['bg'], c['parent_bg'])
                if step < P['card_step'] and c.get('border_px', 0) * PX2PT < P['border_pt'] - 0.05 and c['box'][0] > (raw.get('padding_px') or [0, 0, 0, 0])[3] - 1:
                    bad.append((step, c))
            if bad:
                step, c = min(bad, key=lambda x: x[0])
                add('C7', f"{len(bad)} карток відділено лише {'тінню' if c.get('shadow') else 'заливкою'} {step:.2f}:1", measured=round(step, 2), threshold=P['card_step'], unit='ratio', op='>=', evidence=c['sel'])
        if J.on('V6') and raw.get('map'):
            P = J.par('V6', mode)
            mp = raw['map']
            if mp['boxes'] > P['boxes_max']:
                add('V6', f"{mp['boxes']} блоків на карті", measured=mp['boxes'], threshold=P['boxes_max'], unit='boxes', op='<=', evidence='[data-box]', key='boxes')
            if mp['highlights'] != P['highlights']:
                add('V6', f"{mp['highlights']} підсвічених зон", measured=mp['highlights'], threshold=P['highlights'], unit='zones', op='==', evidence='.hl', key='hl')
        if J.on('V7'):
            P = J.par('V7', mode)
            if mode == 'talk' and P.get('code_hero_pt'):
                for c in raw.get('code') or []:
                    if c.get('hero') and c.get('size_px') and c['size_px'] * PX2PT < P['code_hero_pt'] - 0.05:
                        add('V7', f"головний рядок коду {r1(c['size_px'] * PX2PT)} pt", measured=r1(c['size_px'] * PX2PT), threshold=P['code_hero_pt'], unit='pt', op='>=', evidence=c['sel'], key='hero')
        if J.on('V8'):
            P = J.par('V8', mode)
            for p in raw.get('pills') or []:
                if re.search(r'\b(ga|preview|planned|status)\b', p.get('cls', '')) and is_hex(p.get('color')) and is_hex(p.get('bg')):
                    r = contrast(p['color'], p['bg'])
                    if r < P['label_contrast'] - 0.005:
                        add('V8', f"статус {p['color']} на {p['bg']}: {r:.2f}:1", measured=round(r, 2), threshold=P['label_contrast'], unit='ratio', op='>=', evidence=p['sel'], key=p['sel'])
        if J.on('D3') and J.par('D3', mode):
            P = J.par('D3', mode)
            for tb in raw.get('tables') or []:
                a = J.A.get(s['archetype'] or '', {})
                rows_max = a.get('rows_max', P['rows_max'])
                cols_max = a.get('cols_max', P['cols_max']) if s['archetype'] != 'ref-table' else None
                why = []
                if tb['rows'] > rows_max:
                    why.append(f"{tb['rows']} рядків")
                if cols_max and tb['cols'] > cols_max:
                    why.append(f"{tb['cols']} колонок")
                if tb.get('min_size_px') and tb['min_size_px'] * PX2PT < P['cell_min_pt'] - 0.05:
                    why.append(f"клітинки {r1(tb['min_size_px'] * PX2PT)} pt")
                if why:
                    add('D3', 'таблиця на сцені: ' + ', '.join(why), measured=tb['rows'], threshold=rows_max, unit='rows', op='<=', evidence=tb['sel'], key=tb['sel'])
        imgs = raw.get('images') or []
        if J.on('P1'):
            broken = [im for im in imgs if im.get('broken')]
            if broken:
                add('P1', f"{len(broken)} зображень не завантажились (naturalWidth 0): на слайді замість них alt-текст або порожнє місце", measured=len(broken),
                    threshold=J.par('P1', mode)['missing_max'], unit='images', op='<=', evidence=broken[0]['sel'], key=('broken', broken[0]['sel']))
            for im in imgs:
                if im.get('broken') is None:
                    J.cannot('P1', n, 'зображення ще вантажилось під час виміру', im['sel'])
        if J.on('S1'):
            P = J.par('S1', mode)
            for im in imgs:
                if im.get('eff_px') is None:
                    if im.get('shot'):
                        J.cannot('S1', n, 'скріншот без data-ui-px', im['sel'])
                    continue
                eff = im['eff_px'] * PX2PT
                if eff < P['eff_min_pt'] - 0.05 and not any(c['size_px'] * PX2PT >= P['callout_min_pt'] for c in im.get('callouts') or []):
                    add('S1', f'текст інтерфейсу {eff:.1f} pt без виноски', measured=round(eff, 1), threshold=P['eff_min_pt'], unit='pt', op='>=', evidence=im['sel'], key=im['sel'])
        if J.on('S3'):
            P = J.par('S3', mode)
            for im in [i for i in imgs if i.get('shot')]:
                why = []
                hl, co = im.get('highlights') or [], im.get('callouts') or []
                if len(hl) > 1:
                    why.append(f'{len(hl)} підсвічень')
                for h in hl:
                    if h['stroke_px'] * PX2PT < P['stroke_pt'] - 0.05:
                        why.append(f"обведення {r1(h['stroke_px'] * PX2PT)} pt")
                    lo, hi = P['area']
                    if h.get('area_ratio') is not None and not lo <= h['area_ratio'] <= hi:
                        why.append(f"підсвічено {round(h['area_ratio'] * 100)}% кадру")
                if len(co) > P['callouts_max']:
                    why.append(f'{len(co)} виносок')
                small = [c for c in co if c['size_px'] * PX2PT < P['callout_min_pt'] - 0.05]
                if small:
                    why.append(f"виноска {r1(min(c['size_px'] for c in small) * PX2PT)} pt")
                if why:
                    add('S3', 'анотація: ' + ', '.join(why), evidence=im['sel'], key=im['sel'])
        if J.on('S5'):
            P = J.par('S5', mode)
            shots = [i for i in imgs if i.get('shot')]
            if len(shots) > P['shots_max']:
                add('S5', f'{len(shots)} скріншоти на слайді', measured=len(shots), threshold=P['shots_max'], unit='shots', op='<=', evidence='img', key='count')
            for im in shots:
                if im.get('letterbox_px', 0) * PX2PT > P['fill_tol_pt']:
                    add('S5', f"порожні смуги {r1(im['letterbox_px'] * PX2PT)} pt навколо скріншота", measured=r1(im['letterbox_px'] * PX2PT), threshold=P['fill_tol_pt'], unit='pt', op='<=', evidence=im['sel'], key=(im['sel'], 'lb'))
                elif im.get('fills_zone') is False:
                    add('S5', 'скріншот не заповнює свою зону', evidence=im['sel'], key=(im['sel'], 'fill'))


def html_deck_checks(J, D, passes, metrics, mdir):
    deck = metrics.get('deck') or {}
    slides = passes[0][1]
    n = len(slides)
    modes = {D.smode(s) for s in slides}
    mk = 'talk' if 'talk' in modes else 'reading'
    if J.on('H1'):
        P = J.par('H1', mk)
        got = {(v['w'], v['h']) for v in deck.get('viewports') or []}
        for w, h in P['viewports']:
            if (w, h) not in got:
                J.cannot('H1', None, f'в’юпорт {w}x{h} не виміряно')
        for v in deck.get('viewports') or []:
            if not v.get('visible', True):
                J.add('H1', None, f"{v['w']}x{v['h']}: слайд повністю поза в’юпортом, сторінка порожня (рамка слайда {', '.join(f'{x:g}' for x in v.get('slide_box') or [])})",
                      measured=v.get('cut_px'), threshold=P['fit_tol_px'], unit='px', op='<=', evidence=f"{v['w']}x{v['h']}", key=(v['w'], v['h']))
            elif v.get('cut_px', 0) > P['fit_tol_px'] or v.get('bar_overlap_px', 0) > P['fit_tol_px']:
                J.add('H1', None, f"{v['w']}x{v['h']}: обрізано {v.get('cut_px')} px, перекриття панелі {v.get('bar_overlap_px', 0)} px", measured=max(v.get('cut_px', 0), v.get('bar_overlap_px', 0)), threshold=P['fit_tol_px'], unit='px', op='<=', evidence=f"{v['w']}x{v['h']}", key=(v['w'], v['h']))
    if J.on('H2'):
        P = J.par('H2', mk)
        ln = deck.get('literal_numbers') or {}
        tot = sum(v for v in ln.values() if isinstance(v, int))
        if tot > P['literal_numbers_max']:
            J.add('H2', None, f"вписані вручну: номери сторінок {ln.get('pn', 0)}, діапазони змісту {ln.get('toc_ranges', 0)}, посилання в тексті {ln.get('prose_refs', 0)}, загальна кількість {ln.get('count_text', 0)}, мітки частин {ln.get('part_labels', 0)}", measured=tot, threshold=P['literal_numbers_max'], unit='numbers', op='<=', evidence='source markup')
    if J.on('N13'):
        for m in deck.get('part_label_mismatch') or []:
            s = next((x for x in slides if x['n'] == m['n']), None)
            J.add('N13', m['n'], f"мітка частини «{quote(m['label'], 4)}» не збігається з розділом слайда «{quote(m['section'], 4)}»", evidence='.rail .vert, [data-role=part], .eyebrow',
                  mode=D.smode(s) if s else None, key=('part', m['n']))
    if J.on('H3'):
        P = J.par('H3', mk)
        if len(passes) < P['font_modes']:
            J.add('H3', None, f'виміряно {len(passes)} режим шрифтів', measured=len(passes), threshold=P['font_modes'], unit='modes', op='>=', evidence='--fonts both', severity='бажано', key='modes')
    if J.on('H4'):
        P = J.par('H4', mk)
        pr = deck.get('print')
        if not pr:
            J.cannot('H4', None, 'друк не виміряно (--no-print)')
        else:
            if pr.get('pages') != n:
                J.add('H4', None, f"друк дає {pr.get('pages')} сторінок на {n} слайдів", measured=pr.get('pages'), threshold=n, unit='pages', op='==', evidence='print.pdf', key='pages')
            if pr.get('page_pt') and [round(v) for v in pr['page_pt']] != list(P['page_pt']):
                J.add('H4', None, f"сторінка {pr['page_pt'][0]}x{pr['page_pt'][1]} pt", measured='x'.join(str(v) for v in pr['page_pt']), threshold='x'.join(str(v) for v in P['page_pt']), unit='pt', op='==', evidence='print.pdf', key='size')
            if pr.get('visible_chrome'):
                J.add('H4', None, f"у друці видно: {', '.join(pr['visible_chrome'])}", measured=len(pr['visible_chrome']), threshold=0, unit='elements', op='<=', evidence='@media print', key='chrome')
            if pr.get('pdf_text_leaks'):
                J.add('H4', None, f"у PDF потрапляє текст: {', '.join(pr['pdf_text_leaks'])}", measured=len(pr['pdf_text_leaks']), threshold=0, unit='kinds', op='<=', evidence='@media print', key='leaks')
            if pr.get('light_tokens') is False:
                diff = pr.get('theme_differs') or []
                J.add('H4', None, f"друк із темної теми відрізняється від світлої на {len(diff)} слайдах ({fmt_list([d['n'] for d in diff])[:60]})", measured=len(diff), threshold=0, unit='slides', op='<=', evidence='@media print', key='light')
            for c in pr.get('code_overflow') or []:
                if c['px'] > P['code_overflow_px']:
                    J.add('H4', c['n'], f"код обрізано на {c['px']} px у друці", measured=c['px'], threshold=P['code_overflow_px'], unit='px', op='<=', evidence='pre', key=('print', c['n']))
    if J.on('H6') and 'talk' in modes:
        P = J.par('H6', 'talk')
        miss = [s['n'] for s in slides if D.smode(s) == 'talk' and not s['appendix'] and not (s['raw'].get('notes') or {}).get('present')]
        if len(miss) > P['notes_missing_max']:
            J.add('H6', None, f'немає нотаток на {len(miss)} слайдах: {fmt_list(miss)}', measured=len(miss), threshold=P['notes_missing_max'], unit='slides', op='<=', evidence='aside.notes', key='notes')
        pres = deck.get('presenter') or {}
        if not pres.get('available'):
            J.add('H6', None, 'режим доповідача не відкрився (клавіша S)', evidence='presenter', key='presenter')
        elif pres.get('follow_ms') is None or pres['follow_ms'] > P['presenter_follow_ms']:
            J.add('H6', None, f"режим доповідача відстає: {pres.get('follow_ms')} мс", measured=pres.get('follow_ms'), threshold=P['presenter_follow_ms'], unit='ms', op='<=', evidence='presenter', key='follow')
        feats = deck.get('features') or {}
        missing = [k for k, lab in (('swipe', 'свайп'), ('overview', 'огляд')) if not feats.get(k)]
        if missing:
            J.add('H6', None, 'немає: ' + ', '.join(missing), evidence='features', key='features')
        if not deck.get('theme_in_head', False):
            J.add('H6', None, 'тема відновлюється не в head до першого малювання', evidence='head script', key='theme')
    if J.on('H7'):
        P = J.par('H7', mk)
        if deck.get('inline_styles', 0) > P['inline_styles_max']:
            per = [s['n'] for s in slides if s['raw'].get('inline_styles')]
            J.add('H7', None, f"{deck['inline_styles']} атрибутів style у розмітці слайдів ({fmt_list(per)[:80]})", measured=deck['inline_styles'], threshold=P['inline_styles_max'], unit='attributes', op='<=', evidence='[style]', key='inline')
        per_slide = defaultdict(list)
        for lk in deck.get('css_descendant_leaks') or []:
            for sn in lk.get('slides') or []:
                per_slide[sn].append(lk)
        for sn, lks in sorted(per_slide.items()):
            s = next((x for x in slides if x['n'] == sn), None)
            J.add('H7', sn, f"правило-нащадок «{lks[0]['selector'][:60]}» з рамкою чи відступом чіпляє вкладені елементи" + (f' (ще правил: {len(lks) - 1})' if len(lks) > 1 else ''),
                  measured=len(lks), threshold=P['descendant_leaks_max'], unit='rules', op='<=', evidence=lks[0]['selector'][:80], mode=D.smode(s) if s else None, key=('descendant', sn))
    if J.on('P1'):
        P = J.par('P1', mk)
        for fm, ss in passes:
            miss = [s['n'] for s in ss if not s['raw'].get('png') or not os.path.isfile(os.path.join(mdir, s['raw']['png']))]
            if len(miss) > P['missing_max']:
                J.add('P1', None, f'немає PNG ({fm}) для слайдів {fmt_list(miss)}', measured=len(miss), threshold=P['missing_max'], unit='slides', op='<=', evidence=fm, key=fm)
        if D.plan and len(D.plan['slides']) != n:
            J.add('P1', None, f"у плані {len(D.plan['slides'])} слайдів, відрендерено {n}", measured=n, threshold=len(D.plan['slides']), unit='slides', op='==', evidence='plan.slides', key='plan')


def html_pass_checks(J, D, slides):
    """Checks whose result depends on the font pass (H3, H4 screen code, H5, H7 pills, H8)."""
    for s in slides:
        n, mode, raw = s['n'], D.smode(s), s['raw']
        add = lambda cid, msg, **k: J.add(cid, n, msg, mode=mode, slide_id=s['id'], **k)
        if J.on('H3'):
            P = J.par('H3', mode)
            slack = raw.get('bottom_slack_px')
            free = raw.get('flex_free_px') or 0  # auto margins or flex-grow above the lowest content absorb reflow first
            body_over = [o for o in raw.get('overflow') or [] if o['kind'] == 'body' and o.get('oy_px', 0) > 1]
            if slack is not None and slack < 0:
                add('H3', f'вміст виходить за нижнє поле на {r1(-slack)} px', measured=slack, threshold=P['bottom_slack_px'], unit='px', op='>=', evidence='bottom padding', key='slack')
            elif slack is not None and slack + free < P['bottom_slack_px']:
                add('H3', f'запас знизу {r1(slack + free)} px' + (f' (з них {r1(free)} px вільного місця у flex-колонці)' if free else ''), measured=r1(slack + free),
                    threshold=P['bottom_slack_px'], unit='px', op='>=', evidence='bottom padding', severity='бажано', key='slack')
            if body_over:
                add('H3', f"{body_over[0]['sel']} переповнено на {body_over[0]['oy_px']} px", measured=body_over[0]['oy_px'], threshold=0, unit='px', op='<=', evidence=body_over[0]['sel'], key='overflow')
        if J.on('H4'):
            P = J.par('H4', mode)
            for o in raw.get('overflow') or []:
                if o['kind'] == 'pre' and o.get('ox_px', 0) > P['code_overflow_px'] and not o.get('ellipsis'):
                    add('H4', f"код обрізано на {o['ox_px']} px на екрані", measured=o['ox_px'], threshold=P['code_overflow_px'], unit='px', op='<=', evidence=o['sel'], key=('screen', o['sel']))
        if J.on('H5'):
            P = J.par('H5', mode)
            for v in raw.get('svgs') or []:
                if v.get('text_outside', 0) > P['text_outside_max']:
                    add('H5', f"{v['text_outside']} написів за межами viewBox", measured=v['text_outside'], threshold=P['text_outside_max'], unit='texts', op='<=', evidence=v['sel'], severity='критично', key=(v['sel'], 'out'))
                if v.get('text_overlap', 0) > P['text_overlap_max']:
                    add('H5', f"{v['text_overlap']} перетинів напису з іншим написом або краєм блока", measured=v['text_overlap'], threshold=P['text_overlap_max'], unit='overlaps', op='<=', evidence=v['sel'], severity='критично', key=(v['sel'], 'overlap'))
                if v.get('letterbox_ratio', 0) > P['letterbox_max']:
                    add('H5', f"порожні смуги {v['letterbox_px']} px ({round(v['letterbox_ratio'] * 100)}%) навколо схеми", measured=v['letterbox_ratio'], threshold=P['letterbox_max'], unit='ratio', op='<=', evidence=v['sel'], key=(v['sel'], 'lb'))
        if J.on('H7'):
            P = J.par('H7', mode)
            wrap = [p for p in raw.get('pills') or [] if p.get('lines', 1) > P['pill_lines_max']]
            if wrap:
                add('H7', f'{len(wrap)} пігулок переносяться', measured=max(p['lines'] for p in wrap), threshold=P['pill_lines_max'], unit='lines', op='<=', evidence=wrap[0]['sel'], key='pills')
        if J.on('H8'):
            P = J.par('H8', mode)
            if raw.get('todo', 0) > P['todo_max']:
                add('H8', f"{raw['todo']} незаповнених слотів data-todo", measured=raw['todo'], threshold=P['todo_max'], unit='slots', op='<=', evidence='[data-todo]')
    # V7 one mono family, V8 one pill style (deck-wide, per pass)
    if J.on('V7'):
        fams = {family_key(c.get('family')) for s in slides for c in s['raw'].get('code') or []}
        if len(fams) > 1:
            J.add('V7', None, f"{len(fams)} моноширинні родини в коді: {', '.join(sorted(fams))}", measured=len(fams), threshold=1, unit='families', op='<=', evidence='pre, code', key='mono')
    if J.on('V8'):
        P = J.par('V8', 'talk')
        styles = {(p.get('size_px'), p.get('transform'), round((p.get('box') or [0, 0, 0, 0])[3])) for s in slides for p in s['raw'].get('pills') or []
                  if re.search(r'\b(ga|preview|planned|status)\b', p.get('cls', ''))}
        if len(styles) > P['pill_styles_max']:
            J.add('V8', None, f'{len(styles)} варіанти пігулки статусу', measured=len(styles), threshold=P['pill_styles_max'], unit='styles', op='<=', evidence='.pill', key='styles')


# ------------------------------------------------------------------ outputs
FIX = {
    'N1': 'оголосити режим у плані; щільні слайди винести в додаток', 'N2': 'route після титулу, divider n/N на кожну частину',
    'N3': 'обіцянка в підзаголовку, рядок контексту 14-18 pt', 'N4': 'одна сітка й шаблон заголовка для пари',
    'N5': 'zoom повторює карту без зсуву рамки', 'N6': 'вхід, кадр результату й підсумок для кожного демо',
    'N7': 'хаб перед спицями, ті самі мітки й порядок', 'N8': 'вирівняти щільність сусідів або вставити місток до 25 слів',
    'N9': 'на сцені хаб і до 2 пунктів, решта в додаток', 'N10': 'одне речення висновку, recap дослівно, один наступний крок',
    'N11': 'доказ одразу після концепту', 'N12': 'узгодити кількість слайдів з хвилинами', 'N13': 'рендерити списки з plan.lists',
    'T1': 'заголовок як твердження з дієсловом чи числом', 'T2': 'найсильніше речення в заголовок', 'T3': 'скоротити до одного рядка без висячого слова',
    'T4': 'заголовок найбільший; повторювану мітку в eyebrow', 'T5': 'одна граматика для сусідніх назв', 'T6': 'перший рядок додає число чи результат',
    'T7': 'число вдвічі більше за текст, база й метод', 'T8': 'рівні стовпці, «до» як спостережуваний результат', 'T9': 'NBSP між числом і одиницею',
    'T10': 'одна форма діапазону за dash_policy', 'T11': 'прибрати дублікат, виправити клон, додати виноску',
    'G1': 'один токен рамки заголовка', 'G2': 'відсунути від краю до безпечного поля', 'G3': 'відсунути декор від вмісту', 'G4': 'з’єднувачі в центри карток',
    'G5': 'збільшити текст або перекомпонувати', 'G6': 'поділ близько 40/60 з вирівнюванням', 'G7': 'менше рамок; видимі лінії на темному',
    'G8': 'одна вісь процесу', 'Y1': 'підняти розмір до порогу або винести текст', 'Y2': 'одна шкала, одна sans і одна mono', 'Y3': 'вирівняти ліворуч',
    'Y4': 'рядок 35-60 символів, колонка від 170 pt', 'Y5': 'один спосіб виділення', 'Y6': 'писати «N / M», без капсу з цифрами в mono',
    'C1': 'темніший accent-text або інше тло', 'C2': 'темніша заливка шапки', 'C3': 'градієнт лише для великих коротких написів',
    'C4': 'перемикати тему лише на роздільниках', 'C5': 'колір лише для названих сутностей', 'C6': 'приглушити контекст, активне від 7:1',
    'C7': 'крок заливки від 1.15:1 або рамка 1 pt', 'V1': 'один смисл на пристрій', 'V2': 'намалювати зв’язки', 'V3': 'підписи й прив’язка виносок',
    'V4': 'живий текст у межах полотна', 'V5': 'перестилізувати імпорт', 'V6': 'до 12 блоків, одна підсвітка', 'V7': 'код від порогу, прямі лапки, одна mono',
    'V8': 'один компонент статусу', 'D1': 'розділити слайд або винести в додаток', 'D2': 'тримати бюджет архетипу', 'D3': 'до 6x3, решту в додаток',
    'D4': 'форма як герой, до 4 висновків', 'S1': 'кроп, збільшення або виноска від 14 pt', 'S2': 'кадр результату', 'S3': 'одна підсвітка, до 3 виносок',
    'S4': 'перезняти на синтетичних даних', 'S5': 'один кадр, без смуг і колажу', 'S6': 'видимий заголовок і позначка демо',
    'K1': 'генерований номер в одному місці', 'K2': 'до 2 родин шаблонів', 'K3': 'зафіксувати рамку серії',
    'H1': 'центрування translate плюс scale, панель зарезервовано', 'H2': 'номери генерувати з DOM', 'H3': 'вбудувати шрифт, лишити запас знизу',
    'H4': 'виправити @media print', 'H5': 'viewBox під пропорції дошки', 'H6': 'нотатки, режим доповідача, свайп, огляд, тема в head',
    'H7': 'класи замість style, пігулки без переносу', 'H8': 'заповнити слоти', 'P1': 'відрендерити й переглянути кожен слайд',
    'P2': 'виправити критичні знахідки й повторити цикл', 'P3': 'звіт за шаблоном',
}


def check_order(cid):
    m = re.match(r'([A-Z]+)(\d+)', cid)
    return (FAMILY_ORDER.index(m.group(1)) if m.group(1) in FAMILY_ORDER else 99, int(m.group(2)))


def finalize(findings):
    rank = {s: i for i, s in enumerate(SEV)}
    findings.sort(key=lambda f: (rank[f['severity']], f['slide'] or 0, check_order(f['check']), str(f['_key'])))
    counter = Counter()
    for f in findings:
        slot = 'deck' if f['slide'] is None else f"{f['slide']:03d}"
        counter[(f['check'], slot)] += 1
        f['id'] = f"{f['check']}-{slot}-{counter[(f['check'], slot)]}"
        del f['_key']
    return findings


def merge_passes(per_pass):
    """Findings that agree in both font passes are merged with font_mode both."""
    if len(per_pass) == 1:
        return per_pass[0][1]
    out, index = [], {}
    for fm, fs in per_pass:
        for f in fs:
            k = (f['check'], f['slide'], str(f['_key']), f['severity'])
            if k in index:
                index[k]['font_mode'] = 'both'
            else:
                f = dict(f)
                f['font_mode'] = fm
                index[k] = f
                out.append(f)
    return out


def visual_todo(J, path, modes):
    out = []
    for cid, c in J.C.items():
        if c['measured'] not in ('V', 'A+V') or not J.selected(cid):
            continue
        if path == 'pdf' and cid.startswith('H'):
            continue
        if all(c.get(m) is None for m in modes):
            continue
        out.append(cid)
    return sorted(out, key=check_order)


def write_outputs(out_dir, stem, doc, J):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, stem + '.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write('\n')
    with open(os.path.join(out_dir, stem + '.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(render_md(doc))


def cell(v):
    return '' if v is None else str(v).replace('|', '/').replace('\n', ' ')


def render_md(doc):
    s = doc['summary']
    lines = [f"# Знахідки deck_lint ({doc['path']})", '',
             f"Критично {s['критично']} · бажано {s['бажано']} · косметика {s['косметика']} · не вдалося перевірити {s['could_not_verify']} · слайдів {s['slides']}",
             f"Режим: {doc['inputs'].get('mode')} · поріг виходу: {doc['inputs'].get('fail_on')}" + (' · план відновлено (inferred)' if doc['inputs'].get('inferred_plan') else ''), '']
    if doc['findings']:
        lines += ['| Слайд | Перевірка | Виміряно | Поріг | Урок | Власник | Що зробити |', '|---|---|---|---|---|---|---|']
        # more than 6 rows of one check, severity, unit and comparison collapse into one row; the measured
        # values and the thresholds print as ranges, so different units never share a row
        groups = defaultdict(list)
        gkey = lambda f: (f['check'], f['severity'], f['unit'], f['op'])
        for f in doc['findings']:
            groups[gkey(f)].append(f)

        def rng(vals):
            nums = [v for v in vals if isinstance(v, (int, float)) and not isinstance(v, bool)]
            if nums:
                return f'{min(nums):g}' if min(nums) == max(nums) else f'{min(nums):g}..{max(nums):g}'
            other = sorted({str(v) for v in vals if v is not None})
            return ', '.join(other[:3]) + (' …' if len(other) > 3 else '')
        done = set()
        for f in doc['findings']:
            g = gkey(f)
            if g in done:
                continue
            fs = groups[g]
            if len(fs) > 6:
                done.add(g)
                lines.append(f"| {fmt_list([x['slide'] for x in fs if x['slide']])} | {f['check']} {f['severity']}: {len(fs)} знахідок, напр. {cell(f['message'])} | {cell(rng([x['measured'] for x in fs]))} {cell(f['unit'])} | {cell(f['op'])} {cell(rng([x['threshold'] for x in fs]))} | {', '.join(f['lesson'])} | {f['owner']} | {FIX.get(f['check'], '')} |")
                continue
            sl = f['slide'] if f['slide'] is not None else 'колода'
            fm = f" [{f['font_mode']}]" if f.get('font_mode') and f['font_mode'] != 'both' else ''
            th = f"{cell(f['op'])} {cell(f['threshold'])}".strip()
            lines.append(f"| {sl} | {f['check']} {f['severity']}: {cell(f['message'])}{fm}{' (підтвердити)' if f['confirm'] else ''} | {cell(f['measured'])} {cell(f['unit'])} | {th} | {', '.join(f['lesson'])} | {f['owner']} | {FIX.get(f['check'], '')} |")
    else:
        lines.append('Знахідок немає.')
    lines += ['', '## Не вдалося перевірити', '']
    if doc['could_not_verify']:
        agg = defaultdict(list)
        for c in doc['could_not_verify']:
            agg[(c['check'], c['reason'])].append(c['slide'])
        for (cid, reason), sl in agg.items():
            ss = [x for x in sl if x]
            lines.append(f"- {cid}: {reason}" + (f" (слайди {fmt_list(ss)})" if ss else ''))
    else:
        lines.append('- нічого')
    sk = doc['summary'].get('checks_skipped') or []
    if sk:
        lines += ['', '## Пропущені перевірки', ''] + [f"- {x['check']}: {x['reason']}" for x in sk]
    if doc.get('info'):
        lines += ['', '## Довідково', ''] + [f"- {x.get('check')}: {x.get('note')}" + (f" ({x['measured']})" if x.get('measured') is not None else '') for x in doc['info'][:40]]
    hints = doc.get('visual_hints') or {}
    if doc.get('visual_todo') or hints:
        lines += ['', '## Перевірити очима', '']
        if doc.get('visual_todo'):
            lines.append('Питання з rubric.md §V для: ' + ', '.join(doc['visual_todo']))
        if hints:
            lines += [''] * bool(doc.get('visual_todo')) + [f"- {cid}: {h['note']}" + (f" (слайди {fmt_list(h['slides'])})" if h['slides'] and cid != 'T11' else '')
                             for cid, hs in hints.items() for h in hs]
    return '\n'.join(lines) + '\n'


def is_plan_row(f):
    return isinstance(f.get('_key'), tuple) and f['_key'][:1] == ('plan',)


def build_doc(J, path, inputs, slides_n, fail_rank, modes):
    findings = finalize(J.findings)
    seen, cnv = set(), []
    for c in J.cnv:
        k = (c['check'], c['slide'], c['reason'], c.get('evidence'))
        if k not in seen:
            seen.add(k)
            cnv.append(c)
    J.cnv = cnv
    counts = Counter(f['severity'] for f in findings)
    doc = {'schema': 'deck-findings/1', 'tool': 'deck_lint.py', 'path': path, 'inputs': inputs,
           'summary': {'критично': counts['критично'], 'бажано': counts['бажано'], 'косметика': counts['косметика'],
                       'could_not_verify': len(J.cnv), 'info': len(J.info), 'slides': slides_n,
                       'checks_run': sorted(J.ran, key=check_order), 'checks_skipped': J.skipped},
           'findings': findings, 'could_not_verify': J.cnv, 'info': J.info,
           'visual_todo': visual_todo(J, path, modes) if path in ('html', 'pdf') else [],
           'visual_hints': {cid: [{'note': note, 'slides': sorted(sl)} for note, sl in notes.items()]
                            for cid, notes in sorted(J.hints.items(), key=lambda kv: check_order(kv[0]))}}
    failing = sum(1 for f in findings if SEV.index(f['severity']) <= fail_rank)
    return doc, failing


def print_summary(doc, failing, fail_on):
    s = doc['summary']
    print(f"{doc['path']}: критично {s['критично']}, бажано {s['бажано']}, косметика {s['косметика']}, "
          f"не вдалося перевірити {s['could_not_verify']}; на рівні {fail_on} або вище: {failing}")
    for f in doc['findings'][:12]:
        print(f"  {f['id']}: {f['message']}")


# ------------------------------------------------------------------ main
def load_json(path, what):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except OSError as e:
        die(f'cannot read {what} {path}: {e}')
    except ValueError as e:
        die(f'{what} is not valid JSON ({e}): {path}')


def utf8_console():
    """Windows consoles and pipes default to a legacy code page; Ukrainian output must not crash."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError):
            pass


def main(argv):
    ap = argparse.ArgumentParser(prog='deck_lint.py', description='deck-review judge: HTML metrics or PDF runs against thresholds.json and deck-plan.json')
    ap.add_argument('--plan')
    ap.add_argument('--plan-only', dest='plan_only')
    ap.add_argument('--tokens')
    ap.add_argument('--metrics')
    ap.add_argument('--runs')
    ap.add_argument('--pixels')
    ap.add_argument('--thresholds', default=os.path.join(HERE, 'thresholds.json'))
    ap.add_argument('--mode', choices=['talk', 'reading', 'talk+appendix'])
    ap.add_argument('--only', default='')
    ap.add_argument('--skip', default='')
    ap.add_argument('--fail-on', dest='fail_on', choices=list(FAIL_ON))
    ap.add_argument('--out')
    a = ap.parse_args(argv)
    standalone = [x for x in (a.plan_only, a.tokens) if x]
    lint = [x for x in (a.metrics, a.runs) if x]
    if len(standalone) + (1 if lint else 0) != 1 or len(lint) > 1:
        ap.print_usage(sys.stderr)
        die('choose exactly one of --plan-only, --tokens, --metrics, --runs')
    if lint and not a.out:
        ap.print_usage(sys.stderr)
        die('--out is required with --metrics or --runs')
    if not os.path.isfile(a.thresholds):
        die(f'thresholds.json not found: {a.thresholds}')
    thr = load_json(a.thresholds, 'thresholds')
    if thr.get('schema') != 'deck-thresholds/1' or 'checks' not in thr:
        die(f'unsupported thresholds file: {a.thresholds}')
    miss = [k for k in ('tol_pt', 'nonint_tol_pt', 'scale_tol_pt', 'silent_words_max', 'title_zone_top', 'pn_max_pt',
                        'dark_bg_max', 'lum_dark_max', 'lum_light_min', 'dup_hamming_max')
            if not isinstance((thr.get('measure') or {}).get(k), (int, float))]
    if miss:
        die(f'thresholds.json measure is missing {", ".join(miss)}: {a.thresholds}')
    if round(contrast('#000000', '#FFFFFF'), 2) != 21.00 or round(contrast('#767676', '#FFFFFF'), 2) != 4.54:
        die('contrast sanity asserts failed (21.00 and 4.54 expected)')
    only = {x.strip() for x in a.only.split(',') if x.strip()}
    skip = {x.strip() for x in a.skip.split(',') if x.strip()}
    for x in only | skip:
        if x not in thr['checks'] and x not in FAMILY_ORDER:
            die(f'unknown check id or family in --only/--skip: {x}')
    enum = list(thr['archetypes'])

    if a.plan_only:
        plan = load_json(a.plan_only, 'plan')
        errs = validate_plan(plan, enum)
        if errs:
            die('plan schema violations (deck-plan.md §7):\n' + '\n'.join('  - ' + e for e in errs))
        J = Judge(thr, 'plan', only, skip)
        plan_rules(J, plan, a.mode)
        fail_on = a.fail_on or 'should'
        doc, failing = build_doc(J, 'plan', {'plan': os.path.basename(a.plan_only), 'mode': plan.get('mode'), 'fail_on': SEV[FAIL_ON[fail_on]],
                                             'thresholds': os.path.basename(a.thresholds), 'inferred_plan': bool(plan.get('inferred'))},
                                 len(plan['slides']), FAIL_ON[fail_on], [])
        if a.out:
            write_outputs(a.out, 'plan-findings', doc, J)
        print_summary(doc, failing, fail_on)
        return 1 if failing else 0

    if a.tokens:
        if not os.path.isfile(a.tokens):
            die(f'not a file: {a.tokens}')
        J = Judge(thr, 'tokens', only, skip)
        mode = a.mode if a.mode in ('talk', 'reading') else 'talk'
        rate_tokens(J, a.tokens, mode)
        fail_on = a.fail_on or 'should'
        doc, failing = build_doc(J, 'tokens', {'tokens': os.path.basename(a.tokens), 'mode': mode, 'fail_on': SEV[FAIL_ON[fail_on]],
                                               'thresholds': os.path.basename(a.thresholds)}, 0, FAIL_ON[fail_on], [])
        if a.out:
            write_outputs(a.out, 'token-findings', doc, J)
        print_summary(doc, failing, fail_on)
        return 1 if failing else 0

    # ---- lint over a rendered deck
    plan = None
    if a.plan:
        plan = load_json(a.plan, 'plan')
        errs = validate_plan(plan, enum)
        if errs:
            die('plan schema violations (deck-plan.md §7):\n' + '\n'.join('  - ' + e for e in errs))
    pixels_doc = load_json(a.pixels, 'pixels') if a.pixels else None
    pixels = {s['n']: s for s in (pixels_doc or {}).get('slides', [])} if pixels_doc else None
    fail_on = a.fail_on or 'critical'
    path = 'html' if a.metrics else 'pdf'
    J = Judge(thr, path, only, skip)
    if plan:
        plan_rules(J, plan, a.mode)
    if a.metrics:
        metrics = load_json(a.metrics, 'metrics')
        if metrics.get('schema') != 'deck-metrics/1':
            die(f'unsupported metrics schema: {metrics.get("schema")}')
        passes = norm_html(metrics)
        deck = metrics.get('deck') or {}
        D = Deck(J, passes[0][1], plan, a.mode, deck.get('mode'), deck.get('lang'))
        D.metrics_deck = deck
        for fm, ss in passes[1:]:
            Deck(J, ss, plan, a.mode, deck.get('mode'), deck.get('lang'))
        per_pass = []
        base = J.findings
        for fm, ss in passes:
            J.findings = []
            J.font_mode = fm
            slide_checks(J, D, ss, pixels)
            html_pass_checks(J, D, ss)
            for f in J.findings:
                f['font_mode'] = fm
            per_pass.append((fm, J.findings))
        merged = merge_passes(per_pass)
        J.findings = base + merged
        J.font_mode = None
        html_slide_checks(J, D, passes[0][1])
        deck_checks(J, D, passes[0][1], pixels, pixels_doc)
        html_deck_checks(J, D, passes, metrics, os.path.dirname(os.path.abspath(a.metrics)))
        slides = passes[0][1]
        if not pixels:
            J.cannot('T11', None, 'немає pixels.json: майже однакові слайди не шукали')
    else:
        runs = load_json(a.runs, 'runs')
        if isinstance(runs, dict) and runs.get('schema') not in (None, 'deck-runs/1'):
            die(f'unsupported runs schema: {runs.get("schema")}')
        slides = norm_pdf(runs, pixels_doc, J.M)
        D = Deck(J, slides, plan, a.mode, None, None)
        for s in slides:
            if s['archetype'] in TITLE_ANYWHERE:
                retitle(s, J.M)
        slide_checks(J, D, slides, pixels)
        deck_checks(J, D, slides, pixels, pixels_doc)
        if not pixels:
            J.cannot('C1', None, 'немає pixels.json: тло під рядками невідоме')
            J.cannot('C4', None, 'немає pixels.json')
            J.cannot('T11', None, 'немає pixels.json: майже однакові слайди не шукали')
        if J.on('P1'):
            P = J.par('P1', 'talk')
            npx = len(pixels) if pixels else 0
            if pixels is not None and npx != len(slides):
                J.add('P1', None, f'PNG {npx}, сторінок {len(slides)}', measured=abs(npx - len(slides)), threshold=P['missing_max'], unit='slides', op='<=', evidence='pixels.json')
            if plan and len(plan['slides']) != len(slides):
                J.add('P1', None, f"у плані {len(plan['slides'])} слайдів, у PDF {len(slides)}", measured=len(slides), threshold=len(plan['slides']), unit='slides', op='==', evidence='plan.slides')
        for cid in ('N2', 'N5', 'D2'):
            if not D.known:
                J.skip_check(cid, 'архетипи невідомі: потрібен --plan (можна відновлений, inferred: true)')
        J.skip_check('H1', 'шлях PDF: перевірки рушія HTML не застосовні')
    if not D.known:
        J.info.append({'check': 'D2', 'note': 'архетипи невідомі; слайд 1 прийнято за title'})
    # a plan row (T1, T3) and a rendered row of the same check on one slide report one defect: keep the rendered row
    rendered = {(f['check'], f['slide']) for f in J.findings if f['check'] in ('T1', 'T3') and not is_plan_row(f)}
    J.findings = [f for f in J.findings if not (is_plan_row(f) and (f['check'], f['slide']) in rendered)]
    if J.on('P2'):
        crit = sum(1 for f in J.findings if f['severity'] == 'критично')
        if crit:
            J.add('P2', None, f'цикл не завершено: {crit} критичних знахідок', measured=crit, threshold=J.par('P2', 'talk')['critical_max'], unit='findings', op='<=', evidence='findings.json')
    modes = sorted({D.smode(s) for s in slides})
    inputs = {'plan': os.path.basename(a.plan) if a.plan else None, 'metrics': os.path.basename(a.metrics) if a.metrics else None,
              'runs': os.path.basename(a.runs) if a.runs else None, 'pixels': os.path.basename(a.pixels) if a.pixels else None,
              'thresholds': os.path.basename(a.thresholds), 'mode': D.mode if D.declared else 'talk (не оголошено)',
              'fail_on': SEV[FAIL_ON[fail_on]], 'inferred_plan': bool((plan or {}).get('inferred'))}
    doc, failing = build_doc(J, path, inputs, len(slides), FAIL_ON[fail_on], modes)
    write_outputs(a.out, 'findings', doc, J)
    print_summary(doc, failing, fail_on)
    return 1 if failing else 0


if __name__ == '__main__':
    utf8_console()
    sys.exit(main(sys.argv[1:]))
