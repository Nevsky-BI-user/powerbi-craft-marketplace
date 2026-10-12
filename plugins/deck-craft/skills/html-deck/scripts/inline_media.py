#!/usr/bin/env python3
"""Inline the local images of an html-deck file as data URIs, so the deck stays one self-contained file.

Usage: python3 inline_media.py deck.html [--apply]

Dry run by default: lists every <img src> between <!-- @slides:start --> and <!-- @slides:end --> with its
slide id, the file it points to and the bytes it adds, writes nothing. --apply rewrites those src attributes
in deck.html. Rules (html-deck references/engine.md §13):
- PNG, JPEG, WebP and GIF become base64 data URIs;
- SVG becomes a percent-encoded data URI (image/svg+xml): % # < > " & and line breaks are escaped, so a
  colour such as #0B1118 is written %230B1118 (a raw # ends the URI and the image does not load);
- a src that already starts with data: is kept, so a second run changes nothing; http(s) and
  protocol-relative URLs are reported and kept, because this script never downloads;
- a relative src resolves against the folder of deck.html, as the browser does from file://.
A base64 data URI is about 4/3 of the file; the total growth of the deck is printed.

Exit: 0 ok, also when nothing needs inlining; 1 a referenced file is missing or has an unsupported type
(nothing is written); 2 usage, deck not found or slide markers missing.
Stdlib only, no subprocesses, never opens a window.
"""
import base64
import html
import os
import re
import sys
from urllib.parse import quote, unquote

USAGE = 'usage: python3 inline_media.py deck.html [--apply]'
START, END = '<!-- @slides:start -->', '<!-- @slides:end -->'
RASTER = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif'}
# src of an <img>; quoted attribute values are skipped whole, so «src=» inside an alt text never matches
IMG = re.compile(r'<img\b(?:[^>"\']|"[^"]*"|\'[^\']*\')*?\ssrc\s*=\s*(?P<q>["\'])(?P<src>.*?)(?P=q)', re.I | re.S)
SECTION = re.compile(r'<section\b[^>]*\bid="([^"]*)"', re.I)
SVG_SAFE = " !$'()*+,-./:;=?@_~"  # quote() also keeps letters and digits; everything else is escaped


def fail(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


def data_uri(path):
    """(uri, None) or (None, reason)."""
    ext = os.path.splitext(path)[1].lower()
    if ext != '.svg' and ext not in RASTER:
        return None, 'unsupported type (png, jpg, jpeg, webp, gif, svg)'
    with open(path, 'rb') as f:
        raw = f.read()
    if ext == '.svg':
        try:
            return 'data:image/svg+xml,' + quote(raw.decode('utf-8-sig'), safe=SVG_SAFE), None
        except UnicodeDecodeError:
            return None, 'SVG is not UTF-8 text'
    return f'data:{RASTER[ext]};base64,' + base64.b64encode(raw).decode('ascii'), None


def main(argv):
    if '-h' in argv or '--help' in argv:
        print(__doc__)
        return 0
    apply = '--apply' in argv
    rest = [a for a in argv if a != '--apply']
    bad = [a for a in rest if a.startswith('-')]
    if bad:
        fail(f'unknown option {bad[0]}\n{USAGE}')
    if len(rest) != 1:
        fail(USAGE)
    deck = rest[0]
    if not os.path.isfile(deck):
        fail(f'deck not found: {deck}\n{USAGE}')
    with open(deck, encoding='utf-8') as f:
        doc = f.read()
    if doc.count(START) != 1 or doc.count(END) != 1 or doc.index(START) > doc.index(END):
        fail(f'{deck} must hold exactly one {START} before one {END} (the html-deck template has them)')
    a, b = doc.index(START), doc.index(END)
    region, base = doc[a:b], os.path.dirname(os.path.abspath(deck))
    sections = [(m.start(), m.group(1)) for m in SECTION.finditer(region)]

    edits, problems, remote, kept, added = [], [], [], 0, 0
    for m in IMG.finditer(region):
        src = html.unescape(m.group('src')).strip()
        slide = next((sid for pos, sid in reversed(sections) if pos < m.start()), '-')
        if src.lower().startswith('data:'):
            kept += 1
            continue
        if re.match(r'^(https?:)?//', src, re.I):
            remote.append(f'{slide}: {src}')
            continue
        rel = unquote(re.split(r'[?#]', src, maxsplit=1)[0])
        path = os.path.join(base, rel)
        if not rel or not os.path.isfile(path):
            problems.append(f'{slide}: file not found: {src}')
            continue
        uri, why = data_uri(path)
        if why:
            problems.append(f'{slide}: {src}: {why}')
            continue
        grow = len(uri) - len(m.group('src').encode('utf-8'))
        added += grow
        print(f'{slide} | {src} | {os.path.getsize(path)} bytes | adds {grow} bytes')
        q0, q1 = m.start('q') - m.start(), m.end('src') + 1 - m.start()
        tag = m.group(0)
        edits.append((m.start(), m.end(), tag[:q0] + '"' + uri + '"' + tag[q1:]))

    for r in remote:
        print(f'warning: remote image kept, the deck needs the network for it: {r}')
    if problems:
        for p in problems:
            print(f'error: {p}', file=sys.stderr)
        print(f'{len(problems)} problems: nothing written', file=sys.stderr)
        return 1
    print(f'{len(edits)} images to inline, {kept} already data URIs; the deck grows by {added} bytes '
          f'to {len(doc.encode("utf-8")) + added} bytes')
    if not edits:
        return 0
    if not apply:
        print(f'dry run: nothing written; add --apply to rewrite {deck}')
        return 0
    for s, e, new in reversed(edits):
        region = region[:s] + new + region[e:]
    out = doc[:a] + region + doc[b:]
    with open(deck, 'w', encoding='utf-8', newline='\n') as f:
        f.write(out)
    print(f'wrote {deck} ({len(out.encode("utf-8"))} bytes)')
    return 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    sys.exit(main(sys.argv[1:]))
