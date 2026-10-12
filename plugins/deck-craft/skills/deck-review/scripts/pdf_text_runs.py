#!/usr/bin/env python3
"""Positioned text runs (font, size, colour) from a PDF deck, without poppler.

Uses LibreOffice's bundled xpdfimport helper (the PDF import filter of Draw).
Writes into out_dir:
  pages.json  schema deck-runs/1 (contracts: deck-review SKILL.md, scripts table)
  pages.txt   runs per page, top to bottom, for reading
  stats.txt   fonts, sizes and colours weighted by words, the share of words below the --small cut
              and below the talk Y1 floor and body sizes, words per page, silent and dense pages,
              non-integer sizes, off-canvas runs (cut-offs from thresholds.json next to this script:
              measure.silent_words_max, measure.nonint_tol_pt, checks.D1.talk.words_hard,
              checks.Y1.talk.floor_pt and body_pt)

Usage: python3 pdf_text_runs.py deck.pdf out_dir [--small 12]
Env:   XPDFIMPORT=<path to xpdfimport> when LibreOffice is not in a default place.
Exit:  0 ok; 1 xpdfimport missing or failed; 2 usage, or thresholds.json missing or incomplete.

Notes from practice (rubric lessons L77, L78):
- xpdfimport needs an options argument ("-o ''") and a password on stdin,
  otherwise it aborts with "basic_string: construction from null".
- Its stdout mixes text commands with binary image and font payloads that are
  NOT adjacent to the commands announcing them. Never skip payload bytes by
  length; read line by line and ignore every line that is not a command.
- stdout reaches about 200 MB for a 52-page deck and stderr tens of MB of image
  data: stdout is streamed, stderr goes to a temporary file. On Linux the tool
  runs under "stdbuf -o0" when available, a safeguard against losing the tail
  on a crash (buffered output was byte-identical in practice).
- drawChar coordinates are in USER space; the CTM comes separately (updateCtm,
  absolute, hundredths of a point, y down) and saveState / restoreState do not
  re-emit the restored state, so the parser keeps a state stack. A PowerPoint
  export draws text in page space, a Chrome-printed HTML deck in CSS px.
- Output y is the baseline measured from the BOTTOM of the page; sort by -y
  for reading order. Page sizes arrive in hundredths of a point.
- Blind spots: gradient-filled text arrives as #000000 ("black or gradient"),
  kerning may split a word into two runs, text under an image is present but
  invisible, raster text is absent. Confirm on the rendered pages.
"""
import collections
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

USAGE = 'usage: python3 pdf_text_runs.py deck.pdf out_dir [--small 12]'

CANDIDATES = [
    os.environ.get('XPDFIMPORT', ''),
    '/usr/lib/libreoffice/program/xpdfimport',
    '/usr/lib64/libreoffice/program/xpdfimport',
    '/usr/local/lib/libreoffice/program/xpdfimport',
    '/snap/libreoffice/current/lib/libreoffice/program/xpdfimport',
    '/Applications/LibreOffice.app/Contents/MacOS/xpdfimport',
] + [os.path.join(os.environ[v], 'LibreOffice', 'program', 'xpdfimport.exe')
     for v in ('ProgramFiles', 'ProgramFiles(x86)', 'ProgramW6432') if os.environ.get(v)]

IMAGE_COMMANDS = (b'drawImage ', b'drawMask ', b'drawColorMaskedImage ', b'drawSoftMaskedImage ')
SUBSET = re.compile(r'^[A-Z]{6}\+')
STYLE_WORDS = {
    'bold', 'semibold', 'demibold', 'extrabold', 'ultrabold', 'black', 'heavy', 'medium', 'light',
    'semilight', 'extralight', 'ultralight', 'thin', 'regular', 'normal', 'book', 'roman', 'italic',
    'oblique', 'display', 'text', 'small', 'variable', 'mt', 'ps', 'psmt',
}
BOLD = re.compile(r'bold|black|heavy', re.I)
MONO = re.compile(r'mono|code|courier|consolas|cascadia|menlo', re.I)
LIVE = re.compile(r'[^\W_]')


def fail(msg, code):
    print(msg, file=sys.stderr)
    sys.exit(code)


def stats_cutoffs():
    """Silent, dense, non-integer and type-size cut-offs for stats.txt (rubric §1, D1, Y1), never restated here."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'thresholds.json')
    try:
        with open(path, encoding='utf-8') as f:
            thr = json.load(f)
        m, y1 = thr['measure'], thr['checks']['Y1']['talk']
        cut = m['silent_words_max'], thr['checks']['D1']['talk']['words_hard'], m['nonint_tol_pt'], y1['floor_pt'], y1['body_pt']
    except (OSError, ValueError, KeyError, TypeError):
        fail(f'thresholds.json missing or incomplete: {path}', 2)
    if not all(isinstance(v, (int, float)) for v in cut):
        fail(f'thresholds.json missing or incomplete: {path}', 2)
    return cut


def find_tool():
    for c in CANDIDATES:
        if c and os.path.isfile(c):
            return c
    return shutil.which('xpdfimport')


def family_of(font):
    """Font name without subset prefix and weight, style or optical-size words."""
    name = SUBSET.sub('', font or '?')
    tokens = []
    for tok in re.split(r'[\s,\-_]+', name):
        if not tok:
            continue
        # CamelCase suffixes such as Inter-SemiboldItalic, ArialMT or CourierNewPSMT
        tok = re.sub(r'(PSMT|MT|PS)$', '', tok) if len(tok) > 4 else tok
        parts = re.findall(r'[A-Z]+(?![a-z])|[A-Z]?[a-z]+|\d+', tok) or [tok]
        while parts and parts[-1].lower() in STYLE_WORDS:
            parts.pop()
        tok = ''.join(parts)
        if tok and tok.lower() not in STYLE_WORDS:
            tokens.append(tok)
    return ' '.join(tokens) or name


def run_tool(tool, pdf):
    """Yield xpdfimport stdout lines (bytes), streamed; stderr goes to a temp file."""
    cmd = [tool, '-o', '', pdf]
    if os.name != 'nt' and shutil.which('stdbuf'):
        cmd = [shutil.which('stdbuf'), '-o0'] + cmd
    kwargs = {}
    if os.name == 'nt':
        kwargs['creationflags'] = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
    err = tempfile.TemporaryFile()
    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=err, **kwargs)
    except OSError as e:
        fail(f'xpdfimport could not start: {e}', 1)
    try:
        proc.stdin.write(b'\n')  # empty password
        proc.stdin.close()
    except OSError:
        pass
    got = 0
    for line in proc.stdout:
        got += 1
        yield line
    code = proc.wait()
    if code != 0 or not got:
        err.seek(0)
        tail = err.read(400).decode('utf-8', 'replace')
        fail(f'xpdfimport failed (exit {code}, {got} lines): {tail!r}', 1)
    err.close()


def parse(lines):
    """Stream xpdfimport commands into per-page character records in page space.

    drawChar carries USER-space coordinates and the Tf font size; the CTM arrives separately in
    updateCtm (absolute, hundredths of a point, y measured down from the page top) and the graphics
    state is pushed and popped by saveState / restoreState WITHOUT re-emitting the restored CTM, fill
    colour or font. So the parser keeps its own state stack and maps every character to page points:
    x from the left, y = baseline from the BOTTOM, size = Tf size x text-matrix scale x CTM scale.
    """
    pages, cur, stack = [], None, []
    st = {'ctm': (100.0, 0.0, 0.0, -100.0, 0.0, 0.0), 'font': '?', 'fill': '#000000'}
    for bline in lines:
        if bline.startswith(b'startPage '):
            try:
                w, h = (float(x) / 100 for x in bline.split()[1:3])
            except (ValueError, IndexError):
                continue
            cur = {'n': len(pages) + 1, 'w': round(w, 2), 'h': round(h, 2), 'chars': [], 'images': 0}
            pages.append(cur)
            stack = []
            st = {'ctm': (100.0, 0.0, 0.0, -100.0, 0.0, h * 100), 'font': st['font'], 'fill': '#000000'}
            continue
        if cur is None:
            continue
        if bline.startswith(b'drawChar '):
            m = bline.decode('utf-8', 'replace').rstrip('\r\n').split(' ', 10)
            if len(m) != 11:
                continue
            try:
                x0, y0, x1, y1, t0, t2, t1, t3, fs = (float(v) for v in m[1:10])
            except ValueError:
                continue
            a, b, c, d, e, f = st['ctm']
            px0, py0 = (a * x0 + c * y0 + e) / 100, (b * x0 + d * y0 + f) / 100
            px1 = (a * x1 + c * y1 + e) / 100
            scale = abs(a * d - b * c) ** 0.5 / 100 * abs(t0 * t3 - t1 * t2) ** 0.5
            cur['chars'].append((px0, cur['h'] - py0, px1, fs * scale, m[10], st['font'], st['fill']))
        elif bline.startswith(b'updateCtm '):
            try:
                st['ctm'] = tuple(float(v) for v in bline.split()[1:7])
            except ValueError:
                pass
        elif bline.startswith(b'saveState'):
            stack.append(dict(st))
        elif bline.startswith(b'restoreState'):
            if stack:
                st = stack.pop()
        elif bline.startswith(b'updateFont '):
            parts = bline.decode('utf-8', 'replace').rstrip('\r\n').split(' ', 7)
            if len(parts) == 8:
                st['font'] = parts[7].partition(' ')[2] or '?'
        elif bline.startswith(b'updateFillColor '):
            try:
                r, g, b_ = (round(float(x) * 255) for x in bline.split()[1:4])
                st['fill'] = '#%02X%02X%02X' % (r, g, b_)
            except (ValueError, IndexError):
                pass
        elif bline.startswith(IMAGE_COMMANDS):
            cur['images'] += 1
        # every other line is either another command or payload bytes: ignored
    return pages


def runs_of(chars):
    """Group drawChar records into runs; the rule re-joins kerning splits."""
    runs = []
    for x0, y, x1, sz, ch, fn, col in chars:
        if runs:
            r = runs[-1]
            if (abs(r['y'] - y) < 0.6 * sz and r['font'] == fn and r['color'] == col
                    and abs(r['size'] - sz) < 0.5 and -2 < x0 - r['x1'] < 0.6 * sz):
                if x0 - r['x1'] > 0.18 * sz and not r['text'].endswith(' ') and ch != ' ':
                    r['text'] += ' '
                r['text'] += ch
                r['x1'] = x1
                continue
        runs.append({'x': round(x0, 1), 'y': round(y, 1), 'x1': x1, 'size': round(sz, 1),
                     'font': fn, 'color': col, 'text': ch})
    out = []
    for r in runs:
        r['text'] = r['text'].strip()
        if not r['text']:
            continue
        fam = family_of(r['font'])
        out.append({'x': r['x'], 'y': r['y'], 'x1': round(r['x1'], 1), 'size': r['size'], 'font': r['font'],
                    'family': fam, 'bold': bool(BOLD.search(r['font'])), 'mono': bool(MONO.search(fam)),
                    'color': r['color'], 'text': r['text']})
    return out


def utf8_console():
    """Windows consoles and pipes default to a legacy code page; Ukrainian output must not crash."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError):
            pass


def main(argv):
    args = list(argv)
    small = 12.0
    if '-h' in args or '--help' in args:
        print(__doc__)
        return 0
    if '--small' in args:
        i = args.index('--small')
        try:
            small = float(args[i + 1])
        except (IndexError, ValueError):
            fail(USAGE, 2)
        del args[i:i + 2]
    if len(args) != 2 or args[0].startswith('-') or args[1].startswith('-'):
        fail(USAGE, 2)
    pdf, out = args
    if not os.path.isfile(pdf):
        fail(f'not a file: {pdf}\n{USAGE}', 2)
    silent_max, dense_over, nonint_tol, floor_pt, body_pt = stats_cutoffs()
    tool = find_tool()
    if not tool:
        fail('xpdfimport not found: install LibreOffice or set XPDFIMPORT to its xpdfimport binary', 1)
    os.makedirs(out, exist_ok=True)
    pages = parse(run_tool(tool, os.path.abspath(pdf)))
    if not pages:
        fail('xpdfimport produced no pages', 1)

    fonts, sizes, colors = collections.Counter(), collections.Counter(), collections.Counter()
    summary, offcanvas, nonint = [], [], 0
    for pg in pages:
        runs = runs_of(pg['chars'])
        words = small_words = 0
        min_size = None
        for r in runs:
            w = len(r['text'].split())
            words += w
            fonts[r['font']] += w
            sizes[r['size']] += w
            colors[r['color']] += w
            if r['size'] < small:
                small_words += w
            if abs(r['size'] - round(r['size'])) > nonint_tol:
                nonint += w
            min_size = r['size'] if min_size is None else min(min_size, r['size'])
            if r['y'] > pg['h'] or r['y'] < 0 or r['x'] > pg['w'] or r['x1'] < 0:
                offcanvas.append((pg['n'], r['y'], r['size'], len(r['text'].split())))
        summary.append({'n': pg['n'], 'size_pt': [pg['w'], pg['h']], 'words': words, 'small_words': small_words,
                        'min_size_pt': min_size, 'images': pg['images'], 'runs': runs})

    doc = {'schema': 'deck-runs/1', 'tool': 'pdf_text_runs.py', 'source': os.path.basename(pdf),
           'page_pt': summary[0]['size_pt'], 'pages': summary}
    with open(os.path.join(out, 'pages.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    with open(os.path.join(out, 'pages.txt'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# [y x size font colour] text; y = baseline from the page bottom, runs sorted top to bottom\n')
        for s in summary:
            f.write(f"\n===== PAGE {s['n']}  words={s['words']}  small(<{small:g}pt)={s['small_words']}  "
                    f"min={s['min_size_pt']}pt  images={s['images']}\n")
            for r in sorted(s['runs'], key=lambda r: (-round(r['y'] / 4), r['x'])):
                f.write(f"[y{r['y']:>6} x{r['x']:>6} {r['size']:>5}pt {r['font'][:24]:<24} {r['color']}] {r['text']}\n")
    total = sum(s['words'] for s in summary) or 1
    counts = [s['words'] for s in summary]
    silent = [s['n'] for s in summary if sum(len([t for t in r['text'].split() if LIVE.search(t)]) for r in s['runs']) <= silent_max]
    dense = [s['n'] for s in summary if s['words'] > dense_over]
    with open(os.path.join(out, 'stats.txt'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(f"pages: {len(summary)}  page size pt: {summary[0]['size_pt']}  words: {sum(counts)}\n")
        f.write(f'FONTS by words ({len(fonts)} names, {len({family_of(k) for k in fonts})} families)\n')
        f.write(''.join(f'  {k}: {v}\n' for k, v in fonts.most_common(30)))
        f.write('SIZES pt by words\n' + ''.join(f'  {k}: {v}\n' for k, v in sorted(sizes.items(), key=lambda kv: -kv[0])))
        cuts = sorted({small, float(floor_pt), float(body_pt)})
        below = [(c, sum(v for k, v in sizes.items() if k < c)) for c in cuts]
        f.write('SHARE of words below ' + ', '.join(f'{c:g} pt: {w} ({100 * w / total:.1f}%)' for c, w in below)
                + f'  (--small, Y1 talk floor_pt {floor_pt:g}, body_pt {body_pt:g})\n')
        f.write('TEXT COLOURS by words (#000000 = black or gradient text)\n')
        f.write(''.join(f'  {k}: {v}\n' for k, v in colors.most_common(25)))
        f.write('WORDS per page\n  ' + ' '.join(f"{s['n']}:{s['words']}" for s in summary) + '\n')
        f.write(f'PAGES with text under {small:g} pt: {[s["n"] for s in summary if s["small_words"] > 0]}\n')
        f.write(f'SILENT pages (<={silent_max:g} live words): {silent}\nDENSE pages (>{dense_over:g} words): {dense}\n')
        f.write(f'NON-INTEGER sizes: {nonint} words ({100 * nonint / total:.1f}%)\n')
        f.write('OFF-CANVAS runs (page, y, size, words): ' + (', '.join(map(str, offcanvas)) or 'none') + '\n')
    print(f'{len(summary)} pages at {summary[0]["size_pt"][0]:g}x{summary[0]["size_pt"][1]:g} pt, {sum(counts)} words -> {out}')
    return 0


if __name__ == '__main__':
    utf8_console()
    sys.exit(main(sys.argv[1:]))
