#!/usr/bin/env python3
"""selftest.py: the deck-review self-test (QA of the review kit itself).

Sections, in this order:
  sync    rubric.md equals thresholds.json (every check row: name, family, thresholds per mode, by, auto,
          severity and its rule, lessons, owner; archetype budgets; measurement parameters; groups); §V asks
          one question per V or A+V check; the archetype enum agrees across rubric.md and thresholds.json,
          deck-storyline references/deck-plan.md §6, slide-design references/archetypes.md (headings, modes,
          budget lines) and the <template data-archetype> snippets of the html-deck template.
  plan    deck_lint.py --plan-only: deck-storyline assets/deck-plan.example.json and fixtures/clean.plan.json
          pass; fixtures/seeded.plan.json reports every expected.json "plan" entry.
  tokens  deck_lint.py --tokens: slide-design assets/tokens.example.json and the html-deck template pass;
          #F2C811 text on #FFFFFF fails at 1.61:1, as a token sheet and as deck CSS.
  html    html_deck_lint.mjs, pixels.mjs and deck_lint.py on fixtures/seeded.html and fixtures/clean.html:
          every expected.json "html" entry is found (100% recall), seeded.html has no other критично,
          clean.html has no критично, none of the seeded findings (the twin check) and no finding of a check
          outside expected.json "clean_noise" (known lint noise, each entry with its reason).
  pdf     the print.pdf of each fixture through pdf_text_runs.py, pixels.mjs and deck_lint.py --runs with the
          "pdf" list; slides without a seed must print identically in both fixtures (exact print). Skipped
          with a warning when LibreOffice (xpdfimport) is absent.

Fixtures (scripts/fixtures): seeded.html carries the planted defects listed in expected.json (one or more per
slide, each of a different check) and clean.html is the same deck without them (twins). Both own only their <title>, the /* @fixture:start */ CSS
block, the slides between <!-- @slides:start --> and <!-- @slides:end --> and script#deck-data; everything
else is the html-deck template. Before linting, the fixtures are rebuilt on the current template, so the
test always runs the real engine; --refresh-fixtures writes that rebuild back into the fixture files.

Usage: python3 selftest.py [--html-only|--pdf-only|--sync-only] [--keep out_dir] [--refresh-fixtures]
Env:   as the scripts it runs: CHROME_PATH, PLAYWRIGHT_MODULE, XPDFIMPORT. Headless; no window opens.
Exit:  0 all pass; 1 a miss, a false positive on clean.html or a sync mismatch; 2 usage, or a required tool
       missing (Node, Playwright, Chromium; xpdfimport only for the PDF path, which is skipped instead).
Writes only into a temporary folder (or --keep out_dir); --refresh-fixtures writes the two fixture files.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
SKILLS = os.path.dirname(SKILL)
FIX = os.path.join(HERE, 'fixtures')
RUBRIC = os.path.join(SKILL, 'references', 'rubric.md')
THRESHOLDS = os.path.join(HERE, 'thresholds.json')
DECK_PLAN_MD = os.path.join(SKILLS, 'deck-storyline', 'references', 'deck-plan.md')
PLAN_EXAMPLE = os.path.join(SKILLS, 'deck-storyline', 'assets', 'deck-plan.example.json')
ARCHETYPES_MD = os.path.join(SKILLS, 'slide-design', 'references', 'archetypes.md')
TOKENS_EXAMPLE = os.path.join(SKILLS, 'slide-design', 'assets', 'tokens.example.json')
TEMPLATE = os.path.join(SKILLS, 'html-deck', 'assets', 'deck-template.html')
CRIT = 'критично'
NAMES = ('seeded', 'clean')


class ToolMissing(Exception):
    pass


class Report:
    def __init__(self):
        self.passed = self.failed = self.skipped = 0

    def ok(self, sec, msg):
        self.passed += 1
        print(f'ok    {sec:6} {msg}')

    def fail(self, sec, msg, details=()):
        self.failed += 1
        print(f'FAIL  {sec:6} {msg}')
        for d in list(details)[:40]:
            print(f'        {d}')

    def check(self, sec, cond, msg, details=()):
        (self.ok(sec, msg) if cond else self.fail(sec, msg, details))

    def skip(self, sec, msg):
        self.skipped += 1
        print(f'skip  {sec:6} {msg}')

    @staticmethod
    def info(sec, msg):
        print(f'      {sec:6} {msg}')


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def run(cmd, timeout=900):
    kw = {'creationflags': getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)} if os.name == 'nt' else {}
    p = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout, **kw)
    return p.returncode, p.stdout, p.stderr


def py(script, *args):
    return run([sys.executable, '-I', os.path.join(HERE, script), *args])


def node(script, *args):
    exe = shutil.which('node')
    if not exe:
        raise ToolMissing('Node.js 18+ not found on PATH (needed by html_deck_lint.mjs and pixels.mjs)')
    code, out, err = run([exe, os.path.join(HERE, script), *args])
    if code == 2:
        raise ToolMissing(f'{script}: {err.strip().splitlines()[-1] if err.strip() else "exit 2"}')
    return code, out, err


def tail(err):
    return (err.strip().splitlines() or ['(no output)'])[-1][:200]


# ------------------------------------------------------------------ rubric grammar (contracts §12)
def num(s):
    s = s.strip()
    return int(s) if re.fullmatch(r'-?\d+', s) else float(s)


def value(v):
    v = v.strip()
    if v == 'mode':
        return None
    if re.fullmatch(r'\d+x\d+(?:,\d+x\d+)+', v):
        return [[int(a) for a in p.split('x')] for p in v.split(',')]
    if re.fullmatch(r'\d+x\d+', v):
        return [int(a) for a in v.split('x')]
    if '..' in v:
        lo, hi = v.split('..')
        return [num(lo), num(hi)]
    return num(v)


def cell(c):
    c = c.replace('`', '').strip()
    if c == 'n/a':
        return None
    if c == 'none':
        return {}
    out = {}
    for item in c.split('; '):
        k, sep, v = item.partition('=')
        if not sep:
            raise ValueError(f'not key=value: {item!r}')
        out[k.strip()] = value(v)
    return out


def cells(line):
    return [c.strip() for c in line.strip().strip('|').split('|')]


def parse_rubric(text):
    """Check rows, archetype rows, measurement rows, groups, §V questions and family names."""
    checks, arch, measure, groups, errors = {}, {}, {}, {}, []
    family, table = {}, None
    for line in text.splitlines():
        h = re.match(r'^## §\d+\. ([A-Z]): (.+)$', line)
        if h:
            family[h.group(1)] = h.group(2).strip()
        if line.startswith('| Parameter |'):
            table = 'measure'
        elif line.startswith('| Group |'):
            table = 'groups'
        elif line.startswith('| Archetype |'):
            table = 'arch'
        elif line.startswith('| ID |'):
            table = 'checks'
        elif not line.startswith('|'):
            table = None if line.strip() else table
        if not line.startswith('|') or re.match(r'^\|[-| ]+\|$', line) or table is None:
            continue
        c = cells(line)
        try:
            if table == 'checks' and re.fullmatch(r'[A-Z]\d+', c[0]):
                if len(c) != 9:
                    raise ValueError(f'{len(c)} cells, 9 expected')
                m = re.match(r'\*\*(.+?)\.\*\*', c[1])
                sev = re.match(r'^(\S+)(?:\s*\((.+)\))?$', c[6])
                checks[c[0]] = {
                    'name': m.group(1) if m else None, 'family': family.get(c[0][0]),
                    'talk': cell(c[2]), 'reading': cell(c[3]), 'measured': c[4],
                    'auto': [] if c[5] == 'none' else [a.strip() for a in c[5].split(',')],
                    'severity': sev.group(1), 'severity_rule': sev.group(2),
                    'lessons': [x.strip() for x in c[7].split(',')], 'owner': c[8].strip('`')}
            elif table == 'arch' and c[0].startswith('`'):
                if len(c) != 6:
                    raise ValueError(f'{len(c)} cells, 6 expected')
                d = {'mode': c[1], 'words_max': value(c[2]), 'min_pt': value(c[3])}
                d.update(cell(c[4]))
                arch[c[0].strip('`')] = d
            elif table == 'measure' and c[0].startswith('`'):
                measure[c[0].strip('`')] = value(c[1])
            elif table == 'groups' and c[0].startswith('`'):
                groups[c[0].strip('`')] = [x.strip() for x in c[1].split(',')]
        except (ValueError, AttributeError, IndexError) as e:
            errors.append(f'rubric row {c[0]}: {e}')
    sec_v = text.split('## §V.', 1)[1].split('\n## ', 1)[0] if '## §V.' in text else ''
    questions = re.findall(r'^- \*\*([A-Z]\d+)\*\*', sec_v, re.M)
    return checks, arch, measure, groups, questions, errors


def sync_rubric(R, thr):
    sec = 'sync'
    checks, arch, measure, groups, questions, errors = parse_rubric(read(RUBRIC))
    R.check(sec, not errors, f'rubric.md tables parse ({len(checks)} checks, {len(arch)} archetypes, '
                             f'{len(measure)} parameters, {len(groups)} groups)', errors)
    tc, diffs = thr['checks'], []
    for cid in sorted(set(checks) | set(tc)):
        if cid not in checks or cid not in tc:
            diffs.append(f'{cid}: only in {"thresholds.json" if cid in tc else "rubric.md"}')
            continue
        a, b = checks[cid], tc[cid]
        for k in ('name', 'family', 'measured', 'auto', 'severity', 'lessons', 'owner', 'talk', 'reading'):
            if a[k] != b.get(k):
                diffs.append(f'{cid}.{k}: rubric {a[k]!r} != thresholds {b.get(k)!r}')
        if a['severity_rule'] != b.get('severity_rule'):
            diffs.append(f'{cid}.severity_rule: rubric {a["severity_rule"]!r} != thresholds {b.get("severity_rule")!r}')
    R.check(sec, not diffs, f'rubric.md check rows equal thresholds.json ({len(tc)} checks)', diffs)
    ad = [f'{k}: rubric {arch.get(k)} != thresholds {thr["archetypes"].get(k)}' for k in sorted(set(arch) | set(thr['archetypes']))
          if arch.get(k) != thr['archetypes'].get(k)]
    if list(arch) != list(thr['archetypes']) and not ad:
        ad.append('archetype order differs between rubric §13 and thresholds.json')
    R.check(sec, not ad, f'rubric §13 archetype budgets equal thresholds.json ({len(arch)})', ad)
    md = [f'{k}: rubric {measure.get(k)} != thresholds {thr["measure"].get(k)}' for k in sorted(set(measure) | set(thr['measure']))
          if measure.get(k) != thr['measure'].get(k)]
    R.check(sec, not md, f'measurement parameters equal ({len(measure)})', md)
    gd = [f'{k}: rubric {groups.get(k)} != thresholds {thr["groups"].get(k)}' for k in sorted(set(groups) | set(thr['groups']))
          if groups.get(k) != thr['groups'].get(k)]
    R.check(sec, not gd, f'archetype groups equal ({len(groups)})', gd)
    need = [k for k, v in tc.items() if v['measured'] in ('V', 'A+V')]
    vd = [f'{k}: no §V question' for k in need if k not in questions] + [f'{k}: §V question for a check that is not V or A+V' for k in questions if k not in need]
    R.check(sec, not vd and len(questions) == len(set(questions)), f'§V asks one question per V or A+V check ({len(need)})', vd)


def sync_enum(R, thr):
    sec = 'sync'
    enum = list(thr['archetypes'])
    modes = {k: v['mode'] for k, v in thr['archetypes'].items()}
    bad = [f'group {g}: {x} not in the enum' for g, xs in thr['groups'].items() for x in xs if x not in modes]
    R.check(sec, not bad, 'every archetype group member is in the enum', bad)
    # deck-storyline references/deck-plan.md §6
    if not os.path.isfile(DECK_PLAN_MD):
        R.skip(sec, 'deck-storyline not installed: deck-plan.md §6 not compared')
    else:
        txt = read(DECK_PLAN_MD)
        sec6 = txt.split('## §6.', 1)[1].split('\n## ', 1)[0] if '## §6.' in txt else ''
        bullets, cur = [], None
        for line in sec6.splitlines():
            if line.startswith('- '):
                cur = [line]
                bullets.append(cur)
            elif cur is not None and line.startswith('  ') and line.strip():
                cur.append(line)
            elif cur is not None:
                cur = None
                if not line.strip() and len(bullets) >= 3:
                    break
        ids, diffs = [], []
        for b in bullets:
            text = ' '.join(b)
            label = re.match(r'-\s*(\w+)', text).group(1).lower()
            mode = {'talk': 'talk', 'reading': 'reading', 'either': 'any', 'any': 'any'}.get(label)
            got = re.findall(r'`([a-z][a-z-]*)`', text)
            declared = re.search(r'\((\d+)\)', text)
            if declared and int(declared.group(1)) != len(got):
                diffs.append(f'deck-plan.md §6 {label}: declares {declared.group(1)}, lists {len(got)}')
            diffs += [f'deck-plan.md §6: {x} listed as {mode}, thresholds says {modes.get(x)}' for x in got if modes.get(x) != mode]
            ids += got
        if ids != enum:
            diffs.append(f'deck-plan.md §6 ids differ: missing {[x for x in enum if x not in ids]}, extra {[x for x in ids if x not in enum]}'
                         + ('' if set(ids) != set(enum) else ', order differs'))
        R.check(sec, not diffs, f'deck-plan.md §6 lists the enum in order ({len(ids)})', diffs)
    # slide-design references/archetypes.md
    if not os.path.isfile(ARCHETYPES_MD):
        R.skip(sec, 'slide-design not installed: archetypes.md not compared')
    else:
        txt = read(ARCHETYPES_MD)
        heads = list(re.finditer(r'^### (?:(\d+)\. |R(\d+)\. )?([a-z][a-z-]*)\s*$', txt, re.M))
        ids = [m.group(3) for m in heads]
        diffs = []
        for i, m in enumerate(heads):
            aid = m.group(3)
            mode = 'talk' if m.group(1) else 'reading' if m.group(2) else 'any'
            if modes.get(aid) != mode:
                diffs.append(f'archetypes.md: {aid} headed as {mode}, thresholds says {modes.get(aid)}')
            body = txt[m.end():heads[i + 1].start() if i + 1 < len(heads) else len(txt)]
            bl = re.search(r'^- \*\*Budget \(D2\):\*\*\s*(.+)$', body, re.M)
            if not bl:
                diffs.append(f'archetypes.md: {aid} has no Budget (D2) line')
                continue
            try:
                got = cell(bl.group(1))
            except ValueError as e:
                diffs.append(f'archetypes.md: {aid} budget line: {e}')
                continue
            want = {k: v for k, v in (thr['archetypes'].get(aid) or {}).items() if k != 'mode'}
            if got != want:
                diffs.append(f'archetypes.md: {aid} budget {got} != thresholds {want}')
        talk_nums = [int(m.group(1)) for m in heads if m.group(1)]
        read_nums = [int(m.group(2)) for m in heads if m.group(2)]
        if talk_nums != list(range(1, len(talk_nums) + 1)) or read_nums != list(range(1, len(read_nums) + 1)):
            diffs.append('archetypes.md: entry numbers are not 1..n and R1..Rn in order')
        if ids != enum:
            diffs.append(f'archetypes.md headings differ: missing {[x for x in enum if x not in ids]}, extra {[x for x in ids if x not in enum]}'
                         + ('' if set(ids) != set(enum) else ', order differs'))
        R.check(sec, not diffs, f'archetypes.md has one entry per enum id, in order, with equal budgets ({len(ids)})', diffs)
    # html-deck template snippets
    if not os.path.isfile(TEMPLATE):
        R.skip(sec, 'html-deck not installed: template snippets not compared')
    else:
        txt = read(TEMPLATE)
        snips = re.findall(r'<template data-archetype="([^"]+)">\s*<section class="slide a-([^" ]+)"[^>]*data-archetype="([^"]+)"', txt)
        all_ids = re.findall(r'<template data-archetype="([^"]+)">', txt)
        diffs = [f'template: snippet {a} wraps a section of a-{b} / {c}' for a, b, c in snips if not a == b == c]
        diffs += [f'template: {x} appears {all_ids.count(x)} times' for x in sorted(set(all_ids)) if all_ids.count(x) > 1]
        if len(snips) != len(all_ids):
            diffs.append('template: a snippet does not start with <section class="slide a-<id>" data-archetype="<id>">')
        if set(all_ids) != set(enum):
            diffs.append(f'template snippets differ: missing {[x for x in enum if x not in all_ids]}, extra {[x for x in all_ids if x not in enum]}')
        R.check(sec, not diffs, f'html-deck template has exactly one snippet per enum id ({len(all_ids)})', diffs)


# ------------------------------------------------------------------ fixtures
SLIDES = ('<!-- @slides:start -->', '<!-- @slides:end -->')
CSS_START = '/* @fixture:start */'
DATA = re.compile(r'(<script type="application/json" id="deck-data">)(.*?)(</script>)', re.S)
TITLE = re.compile(r'<title>.*?</title>', re.S)


def assemble(fixture, template):
    """The fixture's own parts (title, fixture CSS, slides, deck-data) on the current template."""
    for anchor in (SLIDES[0], SLIDES[1], '</style>'):
        if anchor not in template:
            raise ValueError(f'html-deck template lost the anchor {anchor}')
    if not DATA.search(template) or not TITLE.search(template):
        raise ValueError('html-deck template lost <title> or script#deck-data')
    try:
        title = TITLE.search(fixture).group(0)
        c0 = fixture.index(CSS_START)
        css = fixture[c0:fixture.index('</style>', c0)]
        s0, s1 = fixture.index(SLIDES[0]), fixture.index(SLIDES[1])
        data = DATA.search(fixture).group(2)
    except (ValueError, AttributeError):
        raise ValueError('fixture lost one of its own parts (title, fixture CSS, slides markers, deck-data)')
    t = TITLE.sub(lambda m: title, template, count=1)
    i = t.index('</style>')
    t = t[:i] + css + t[i:]
    a, b = t.index(SLIDES[0]), t.index(SLIDES[1])
    t = t[:a] + fixture[s0:s1] + t[b:]
    m = DATA.search(t)
    return t[:m.start(2)] + data + t[m.end(2):]


def build_fixtures(R, work, refresh=False):
    out = {}
    tpl = read(TEMPLATE) if os.path.isfile(TEMPLATE) else None
    for name in NAMES:
        src = os.path.join(FIX, f'{name}.html')
        text = read(src)
        if tpl is None:
            R.info('fix', f'html-deck not installed: {name}.html runs on its committed engine copy')
            out[name] = src
            continue
        try:
            new = assemble(text, tpl)
        except ValueError as e:
            R.fail('sync', f'{name}.html cannot be rebuilt on the template: {e}')
            out[name] = src
            continue
        if refresh:
            if new != text:
                with open(src, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(new)
            R.info('fix', f'{name}.html {"refreshed from" if new != text else "already equals"} the current template')
            continue
        if new != text:
            R.info('fix', f'{name}.html rebuilt on the current template (its engine copy is older; --refresh-fixtures updates it)')
        path = os.path.join(work, f'{name}.html')
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(new)
        out[name] = path
    return out


# ------------------------------------------------------------------ judging helpers
def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def key(e):
    return f"{e['check']} on {'the deck' if e['slide'] is None else 'slide ' + str(e['slide'])} ({e['severity']})"


def present(findings, e):
    return any(f['check'] == e['check'] and f['slide'] == e['slide'] and f['severity'] == e['severity'] for f in findings)


def assert_fixtures(R, sec, docs, expected, noise):
    seeded, clean = docs['seeded']['findings'], docs['clean']['findings']
    miss = [f'missing {key(e)}: {e.get("seed", "")}' for e in expected if not present(seeded, e)]
    R.check(sec, not miss, f'seeded.html: {len(expected) - len(miss)} of {len(expected)} planted defects found', miss)
    planted = {(e['check'], e['slide']) for e in expected}
    extra = [f"{f['id']}: {f['message']}" for f in seeded if f['severity'] == CRIT and (f['check'], f['slide']) not in planted]
    R.check(sec, not extra, 'seeded.html: no критично beyond the planted ones', extra)
    crit = [f"{f['id']}: {f['message']}" for f in clean if f['severity'] == CRIT]
    R.check(sec, not crit, 'clean.html: 0 критично', crit)
    twin = [f'clean twin still shows {key(e)}' for e in expected if e['slide'] is not None and present(clean, e)]
    R.check(sec, not twin, 'clean.html: no planted finding survives on its twin slide', twin)
    other = [f"{f['id']} ({f['severity']}): {f['message']}" for f in clean if f['check'] not in noise]
    R.check(sec, not other, f'clean.html: only the known-noise checks of expected.json fire ({", ".join(sorted(noise)) or "none"})', other)
    for name in NAMES:
        s = docs[name]['summary']
        R.info(sec, f'{name}.html: критично {s[CRIT]}, бажано {s["бажано"]}, косметика {s["косметика"]}, '
                    f'не вдалося перевірити {s["could_not_verify"]}')


def judge(R, sec, name, args, out):
    code, _, err = py('deck_lint.py', '--plan', os.path.join(FIX, f'{name}.plan.json'), *args, '--out', out)
    if code not in (0, 1):
        R.fail(sec, f'{name}: deck_lint.py exit {code}: {tail(err)}')
        return None
    doc = load(os.path.join(out, 'findings.json'))
    want = 1 if doc['summary'][CRIT] else 0
    if code != want:
        R.fail(sec, f'{name}: deck_lint.py exit {code}, expected {want} for {doc["summary"][CRIT]} критично')
    return doc


# ------------------------------------------------------------------ sections
def section_plan(R, work, expected):
    sec = 'plan'
    for path, label in ((PLAN_EXAMPLE, 'deck-storyline deck-plan.example.json'), (os.path.join(FIX, 'clean.plan.json'), 'fixtures/clean.plan.json')):
        if not os.path.isfile(path):
            R.skip(sec, f'{label} not found')
            continue
        code, out, err = py('deck_lint.py', '--plan-only', path)
        R.check(sec, code == 0, f'--plan-only {label} passes', [out.strip() or tail(err)] if code else ())
    out_dir = os.path.join(work, 'plan-seeded')
    code, out, err = py('deck_lint.py', '--plan-only', os.path.join(FIX, 'seeded.plan.json'), '--out', out_dir)
    if code not in (0, 1):
        R.fail(sec, f'--plan-only fixtures/seeded.plan.json exit {code}: {tail(err)}')
        return
    found = load(os.path.join(out_dir, 'plan-findings.json'))['findings']
    exp = expected.get('plan', [])
    miss = [f'missing {e["check"]} on slide {e["slide"]}' for e in exp
            if not any(f['check'] == e['check'] and f['slide'] == e['slide'] and f['severity'] == e.get('severity', f['severity']) for f in found)]
    R.check(sec, not miss and code == (1 if exp else 0), f'--plan-only fixtures/seeded.plan.json reports {len(exp) - len(miss)} of {len(exp)} planted plan findings', miss)


def section_tokens(R, work):
    sec = 'tokens'
    for path, label in ((TOKENS_EXAMPLE, 'slide-design tokens.example.json'), (TEMPLATE, 'html-deck deck-template.html')):
        if not os.path.isfile(path):
            R.skip(sec, f'{label} not found')
            continue
        code, out, err = py('deck_lint.py', '--tokens', path)
        R.check(sec, code == 0, f'--tokens {label} passes', [out.strip() or tail(err)] if code else ())
    bad = []
    if os.path.isfile(TOKENS_EXAMPLE):
        sheet = load(TOKENS_EXAMPLE)
        sheet['themes']['light']['colors']['accent-text'] = '#F2C811'
        p = os.path.join(work, 'tokens-bad.json')
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(sheet, f, ensure_ascii=False)
        bad.append((p, 'token sheet with accent-text #F2C811', ('light', 'accent-text', 'surface')))
    p = os.path.join(work, 'tokens-bad.html')
    with open(p, 'w', encoding='utf-8') as f:
        f.write('<!doctype html><style>:root{--surface:#FFFFFF;--ink:#F2C811}</style>\n')
    bad.append((p, 'deck CSS with --ink #F2C811 on --surface #FFFFFF', ('light', 'ink', 'surface')))
    for path, label, (theme, fg, bg) in bad:
        out_dir = path + '.out'
        code, _, err = py('deck_lint.py', '--tokens', path, '--out', out_dir)
        if code not in (0, 1):
            R.fail(sec, f'--tokens {label}: exit {code}: {tail(err)}')
            continue
        hits = [f for f in load(os.path.join(out_dir, 'token-findings.json'))['findings']
                if f['check'] == 'C1' and f['theme'] == theme and f['evidence'] == f'{fg} на {bg}']
        r = hits[0]['measured'] if hits else None
        R.check(sec, code == 1 and r is not None and abs(r - 1.61) <= 0.01,
                f'--tokens {label} fails C1 at {r}:1 (1.61 expected)', [f'exit {code}, C1 findings {hits}'])


def lint_html(R, sec, fixtures, out, fonts='both', presenter=True):
    for name in NAMES:
        d = os.path.join(out, name)
        args = [fixtures[name], d, '--fonts', fonts] + ([] if presenter else ['--no-presenter'])
        code, _, err = node('html_deck_lint.mjs', *args)
        if code != 0:
            R.fail(sec, f'{name}: html_deck_lint.mjs exit {code}: {tail(err)}')
            return False
        code, _, err = node('pixels.mjs', os.path.join(d, 'png'), d)
        if code != 0:
            R.fail(sec, f'{name}: pixels.mjs exit {code}: {tail(err)}')
            return False
    return True


def section_html(R, out, expected):
    sec = 'html'
    docs = {}
    for name in NAMES:
        d = os.path.join(out, name)
        doc = judge(R, sec, name, ['--metrics', os.path.join(d, 'metrics.json'), '--pixels', os.path.join(d, 'pixels.json')], d)
        if doc is None:
            return
        docs[name] = doc
    assert_fixtures(R, sec, docs, expected['html'], (expected.get('clean_noise') or {}).get('html', {}))


def section_pdf(R, out, expected):
    sec = 'pdf'
    docs, runs = {}, {}
    for name in NAMES:
        d = os.path.join(out, name)
        pdf = os.path.join(d, 'print.pdf')
        if not os.path.isfile(pdf):
            R.fail(sec, f'{name}: html_deck_lint.mjs wrote no print.pdf')
            return
        code, _, err = py('pdf_text_runs.py', pdf, os.path.join(d, 'runs'))
        if code == 1 and 'not found' in err:
            R.skip(sec, f'PDF path skipped: {tail(err)}')
            return
        if code != 0:
            R.fail(sec, f'{name}: pdf_text_runs.py exit {code}: {tail(err)}')
            return
        pages = os.path.join(d, 'runs', 'pages.json')
        runs[name] = load(pages)
        # the HTML pass PNGs are the print render (one PNG pixel per design px; pixels.mjs scales by page width)
        code, _, err = node('pixels.mjs', os.path.join(d, 'png'), os.path.join(d, 'pdf'), '--runs', pages)
        if code != 0:
            R.fail(sec, f'{name}: pixels.mjs --runs exit {code}: {tail(err)}')
            return
        doc = judge(R, sec, name, ['--runs', pages, '--pixels', os.path.join(d, 'pdf', 'pixels.json')], os.path.join(d, 'pdf'))
        if doc is None:
            return
        docs[name] = doc
    assert_fixtures(R, sec, docs, expected['pdf'], (expected.get('clean_noise') or {}).get('pdf', {}))
    seeded_slides = {e['slide'] for e in expected['html'] if e['slide'] is not None}
    a, b = runs['seeded']['pages'], runs['clean']['pages']
    diff = [f'slide {p["n"]}: runs differ between the two prints' for p, q in zip(a, b) if p['n'] not in seeded_slides and p['runs'] != q['runs']]
    if len(a) != len(b):
        diff.append(f'page count {len(a)} != {len(b)}')
    R.check(sec, not diff, f'exact print: the {len(a) - len(seeded_slides)} unseeded slides print identically in both fixtures', diff)


def main(argv):
    ap = argparse.ArgumentParser(prog='selftest.py', description='deck-review self-test: fixtures, sync and gates')
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--html-only', action='store_true')
    g.add_argument('--pdf-only', action='store_true')
    g.add_argument('--sync-only', action='store_true')
    g.add_argument('--refresh-fixtures', action='store_true')
    ap.add_argument('--keep', metavar='out_dir')
    a = ap.parse_args(argv)
    for f in (RUBRIC, THRESHOLDS, os.path.join(FIX, 'expected.json')):
        if not os.path.isfile(f):
            print(f'missing {f}', file=sys.stderr)
            return 2
    R = Report()
    if a.refresh_fixtures:
        build_fixtures(R, None, refresh=True)
        return 1 if R.failed else 0
    thr = load(THRESHOLDS)
    expected = load(os.path.join(FIX, 'expected.json'))
    if expected.get('schema') != 'deck-expected/1':
        print('fixtures/expected.json: schema deck-expected/1 expected', file=sys.stderr)
        return 2
    want = {'sync', 'plan', 'tokens', 'html', 'pdf'}
    if a.sync_only:
        want = {'sync', 'plan', 'tokens'}
    elif a.html_only:
        want = {'html'}
    elif a.pdf_only:
        want = {'pdf'}
    work = os.path.abspath(a.keep) if a.keep else tempfile.mkdtemp(prefix='deck-selftest-')
    os.makedirs(work, exist_ok=True)
    code = 0
    try:
        if 'sync' in want:
            sync_rubric(R, thr)
            sync_enum(R, thr)
        if 'plan' in want:
            section_plan(R, work, expected)
        if 'tokens' in want:
            section_tokens(R, work)
        if want & {'html', 'pdf'}:
            fixtures = build_fixtures(R, work)
            out = os.path.join(work, 'out')
            sec = 'html' if 'html' in want else 'pdf'
            fonts, presenter = ('both', True) if 'html' in want else ('native', False)
            if lint_html(R, sec, fixtures, out, fonts, presenter):
                if 'html' in want:
                    section_html(R, out, expected)
                if 'pdf' in want:
                    section_pdf(R, out, expected)
    except ToolMissing as e:
        print(f'tool missing: {e}', file=sys.stderr)
        code = 2
    except subprocess.TimeoutExpired as e:
        R.fail('run', f'timeout: {" ".join(map(str, e.cmd))[:160]}')
    finally:
        if not a.keep:
            shutil.rmtree(work, ignore_errors=True)
    print(f'selftest: {R.passed} passed, {R.failed} failed, {R.skipped} skipped' + (f'; outputs in {work}' if a.keep else ''))
    return code or (1 if R.failed else 0)


if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
        except (AttributeError, ValueError):
            pass
    sys.exit(main(sys.argv[1:]))
