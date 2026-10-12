#!/usr/bin/env python3
"""Embed OFL fonts into an html-deck file as base64 @font-face blocks (html-deck H3).

Usage: python3 embed_font.py deck.html --sans F.woff2:400 [--sans F.woff2:600] [--mono M.woff2:400]
                             [--subset] [--allow-unverified] [--apply]

Dry run by default: reads every face, checks licence and Cyrillic coverage, prints the bytes each face
adds, writes nothing. --apply rewrites the region between /* @font-embed:start */ and
/* @font-embed:end */ in deck.html: one @font-face per face (data URI) plus a :root rule that puts the
embedded family first in --font-sans / --font-mono, ahead of the metric-stable fallback stack. The region
is rebuilt from the arguments on every run (idempotent), so pass every face in one call.

Checks (html-deck references/engine.md §6):
- licence: SIL Open Font License only, confirmed by the font's name table (IDs 13, 14) or an OFL.txt /
  LICENSE file next to the font; the copyright and licence URL are copied into a CSS comment. A font
  whose OS/2 fsType forbids embedding is refused;
- coverage: і ї є ґ ’ « » № U+00A0 U+2212 must be in the cmap (read with the standard library for
  TTF, OTF and WOFF; WOFF2 needs fontTools with brotli). A face whose cmap or fsType cannot be read is
  refused (exit 2) unless --allow-unverified is given;
- names: the family, copyright and licence URL come from the font's name table, which is untrusted
  input, so they are sanitised before they enter the deck's <style>: the family keeps letters, digits,
  space, dot, underscore and hyphen; the notice loses angle brackets and comment closers; the URL is used
  only when it is a plain http(s) URL;
- --subset (needs fontTools): keeps Basic Latin, Latin-1, U+0400-04FF (Cyrillic), U+2019, U+2116,
  U+2212, the arrows U+2190-2193 and U+2026 used by the template, writes WOFF2 (WOFF without brotli),
  keeps the name table so the licence travels with the subset, and re-checks coverage on the result.
A data URI grows the file by about 4/3 of the font size; a warning is printed above 1.5 MB in total.

Exit: 0 ok; 1 a required glyph is missing from a face (or from its subset); 2 usage, missing file,
missing markers, licence not confirmed as OFL, embedding forbidden, coverage or fsType unreadable
(WOFF2 without fontTools and brotli) without --allow-unverified, or --subset without fontTools.
Stdlib only unless --subset or a WOFF2 input is used; no subprocesses; never opens a window.
"""
import base64
import io
import os
import re
import struct
import sys
import zlib

USAGE = ('usage: python3 embed_font.py deck.html --sans F.woff2:400 [--sans F.woff2:600] '
         '[--mono M.woff2:400] [--subset] [--allow-unverified] [--apply]')
START, END = '/* @font-embed:start */', '/* @font-embed:end */'
REQUIRED = [0x0456, 0x0457, 0x0454, 0x0491, 0x2019, 0x00AB, 0x00BB, 0x2116, 0x00A0, 0x2212]
SUBSET = (list(range(0x20, 0x7F)) + list(range(0xA0, 0x100)) + list(range(0x400, 0x500))
          + [0x2019, 0x2116, 0x2212, 0x2026, 0x2190, 0x2191, 0x2192, 0x2193])
FALLBACK = {'sans': 'Arial, Arimo, "Liberation Sans", sans-serif',
            'mono': '"Courier New", Cousine, "Liberation Mono", monospace'}
OFL = re.compile(r'open\s+font\s+licen[cs]e|\bOFL\b|scripts\.sil\.org/OFL|openfontlicense\.org', re.I)
MIME = {'woff2': ('font/woff2', 'woff2'), 'woff': ('font/woff', 'woff'),
        'ttf': ('font/ttf', 'truetype'), 'otf': ('font/otf', 'opentype')}
WARN_BYTES = 1_500_000
OFL_URL = 'https://openfontlicense.org'
PLAIN_URL = re.compile(r'^https?://[^\s<>*"\'\\]+$')


def fail(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


def kind_of(data):
    head = data[:4]
    if head == b'wOF2':
        return 'woff2'
    if head == b'wOFF':
        return 'woff'
    if head == b'OTTO':
        return 'otf'
    if head in (b'\x00\x01\x00\x00', b'true'):
        return 'ttf'
    return None


# ---------- minimal sfnt reader (TTF, OTF, WOFF): name, cmap, OS/2
def tables_of(data, kind):
    out = {}
    if kind == 'woff':
        num = struct.unpack('>H', data[12:14])[0]
        for i in range(num):
            tag, off, clen, olen, _ = struct.unpack('>4sIIII', data[44 + 20 * i:64 + 20 * i])
            raw = data[off:off + clen]
            out[tag.decode('latin-1')] = zlib.decompress(raw) if clen < olen else raw
    elif kind in ('ttf', 'otf'):
        num = struct.unpack('>H', data[4:6])[0]
        for i in range(num):
            tag, _, off, length = struct.unpack('>4sIII', data[12 + 16 * i:28 + 16 * i])
            out[tag.decode('latin-1')] = data[off:off + length]
    return out


def names_of(t):
    if not t:
        return {}
    _, count, base = struct.unpack('>HHH', t[:6])
    best = {}
    for i in range(count):
        pid, eid, lid, nid, length, off = struct.unpack('>HHHHHH', t[6 + 12 * i:18 + 12 * i])
        raw = t[base + off:base + off + length]
        text = raw.decode('utf-16-be', 'replace') if pid in (0, 3) else raw.decode('latin-1')
        rank = 0 if (pid == 3 and lid == 0x409) else 1 if pid in (0, 3) else 2
        if nid not in best or rank < best[nid][0]:
            best[nid] = (rank, text.strip())
    return {k: v[1] for k, v in best.items()}


def cmap_of(t):
    cps = set()
    if not t:
        return cps
    _, num = struct.unpack('>HH', t[:4])
    for i in range(num):
        _, _, off = struct.unpack('>HHI', t[4 + 8 * i:12 + 8 * i])
        fmt = struct.unpack('>H', t[off:off + 2])[0]
        if fmt == 4:
            seg2 = struct.unpack('>H', t[off + 6:off + 8])[0]
            seg = seg2 // 2
            ends = struct.unpack(f'>{seg}H', t[off + 14:off + 14 + seg2])
            starts = struct.unpack(f'>{seg}H', t[off + 16 + seg2:off + 16 + 2 * seg2])
            deltas = struct.unpack(f'>{seg}h', t[off + 16 + 2 * seg2:off + 16 + 3 * seg2])
            rpos = off + 16 + 3 * seg2
            roffs = struct.unpack(f'>{seg}H', t[rpos:rpos + seg2])
            for k in range(seg):
                for c in range(starts[k], ends[k] + 1):
                    if c == 0xFFFF:
                        continue
                    if roffs[k] == 0:
                        g = (c + deltas[k]) & 0xFFFF
                    else:
                        p = rpos + 2 * k + roffs[k] + 2 * (c - starts[k])
                        g = struct.unpack('>H', t[p:p + 2])[0]
                        g = (g + deltas[k]) & 0xFFFF if g else 0
                    if g:
                        cps.add(c)
        elif fmt == 12:
            n = struct.unpack('>I', t[off + 12:off + 16])[0]
            for k in range(n):
                s, e, g = struct.unpack('>III', t[off + 16 + 12 * k:off + 28 + 12 * k])
                cps.update(range(s if g else s + 1, e + 1))
    return cps


def facts(data, kind, fonttools):
    """name dict, set of code points and fsType; code points and fsType are None when unreadable."""
    if kind in ('ttf', 'otf', 'woff'):
        t = tables_of(data, kind)
        os2 = t.get('OS/2')
        fs_type = struct.unpack('>H', os2[8:10])[0] if os2 and len(os2) >= 10 else 0
        return names_of(t.get('name')), cmap_of(t.get('cmap')), fs_type
    if fonttools:
        try:
            from fontTools.ttLib import TTFont
            f = TTFont(io.BytesIO(data))
            names = {r.nameID: r.toUnicode() for r in f['name'].names if r.nameID in (0, 1, 13, 14, 16)}
            return names, set(f.getBestCmap() or {}), getattr(f['OS/2'], 'fsType', 0) if 'OS/2' in f else 0
        except Exception as e:  # brotli missing or a broken file
            print(f'  fontTools could not read the WOFF2 ({e})')
    return {}, None, None


def clean_family(name):
    """A family name that is safe inside a CSS string and a CSS comment."""
    return re.sub(r'\s+', ' ', re.sub(r'[^A-Za-z0-9 ._-]', '', name or '')).strip()


def clean_notice(text):
    """Name-table text for a CSS comment: one line, no angle brackets, no comment closer."""
    return re.sub(r'[<>]', '', re.sub(r'\s+', ' ', text or '')).replace('*/', '* /').strip()


def licence_file_text(font_path):
    folder = os.path.dirname(os.path.abspath(font_path))
    for n in sorted(os.listdir(folder)):
        if re.match(r'^(OFL|LICEN[CS]E|COPYING)[^/]*(\.txt|\.md)?$', n, re.I):
            try:
                with open(os.path.join(folder, n), encoding='utf-8', errors='replace') as f:
                    return n, f.read(20000)
            except OSError:
                continue
    return None, ''


def subset(data):
    from fontTools import subset as fts
    from fontTools.ttLib import TTFont
    opts = fts.Options()
    opts.name_IDs = ['*']
    opts.name_languages = ['*']
    opts.layout_features = ['*']
    opts.notdef_outline = True
    try:
        import brotli  # noqa: F401
        opts.flavor = 'woff2'
    except ImportError:
        opts.flavor = 'woff'
    font = TTFont(io.BytesIO(data))
    sub = fts.Subsetter(opts)
    sub.populate(unicodes=SUBSET)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = opts.flavor
    font.save(buf)
    return buf.getvalue(), opts.flavor


def parse_face(spec, role):
    path, weight = spec, '400'
    m = re.match(r'^(.*):(\d+)$', spec)
    if m:
        path, weight = m.group(1), m.group(2)
    if not 100 <= int(weight) <= 900:
        fail(f'--{role} {spec}: weight must be 100-900\n{USAGE}')
    return {'role': role, 'path': path, 'weight': int(weight)}


def main(argv):
    if '-h' in argv or '--help' in argv:
        print(__doc__)
        return 0
    faces, pos, do_subset, apply, allow_unverified = [], [], False, False, False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ('--sans', '--mono'):
            if i + 1 >= len(argv):
                fail(f'{a} needs FILE:WEIGHT\n{USAGE}')
            faces.append(parse_face(argv[i + 1], a[2:]))
            i += 1
        elif a == '--subset':
            do_subset = True
        elif a == '--apply':
            apply = True
        elif a == '--allow-unverified':
            allow_unverified = True
        elif a.startswith('--'):
            fail(f'unknown option {a}\n{USAGE}')
        else:
            pos.append(a)
        i += 1
    if len(pos) != 1 or not faces:
        fail(USAGE)
    deck = pos[0]
    if not os.path.isfile(deck):
        fail(f'deck not found: {deck}\n{USAGE}')
    with open(deck, encoding='utf-8') as f:
        doc = f.read()
    if doc.count(START) != 1 or doc.count(END) != 1 or doc.index(START) > doc.index(END):
        fail(f'{deck} must hold exactly one {START} before one {END} (the html-deck template has them)')
    try:
        import fontTools  # noqa: F401
        fonttools = True
    except ImportError:
        fonttools = False
    if do_subset and not fonttools:
        fail('--subset needs fontTools: pip install fonttools brotli (or run without --subset)')

    blocks, families, total, missing_any = [], {}, 0, False
    for face in faces:
        p = face['path']
        if not os.path.isfile(p):
            fail(f'font not found: {p}')
        with open(p, 'rb') as f:
            data = f.read()
        kind = kind_of(data)
        if not kind:
            fail(f'{p}: not a TTF, OTF, WOFF or WOFF2 font (collections are not supported)')
        names, cps, fs_type = facts(data, kind, fonttools)
        raw_family = names.get(16) or names.get(1) or re.split(r'[-_ ]', os.path.splitext(os.path.basename(p))[0])[0]
        family = (clean_family(raw_family) or clean_family(os.path.splitext(os.path.basename(p))[0])
                  or f"Deck {face['role']}")
        print(f"{face['role']} {face['weight']}: {os.path.basename(p)} ({kind}, {len(data)} bytes), family {family!r}")
        if family != raw_family:
            print(f'  family name sanitised from {raw_family!r}')
        lic_name, lic_text = licence_file_text(p)
        evidence = ' '.join(names.get(k, '') for k in (13, 14))
        if OFL.search(evidence):
            how = 'name table'
        elif OFL.search(lic_text):
            how = lic_name
        else:
            fail(f'{p}: licence not confirmed as SIL OFL (name IDs 13/14 and no OFL.txt or LICENSE next to the font); '
                 'html-deck embeds OFL faces only')
        if fs_type is not None and fs_type & 0x0002:
            fail(f'{p}: OS/2 fsType {fs_type:#06x} forbids embedding')
        print(f'  licence: OFL ({how})')
        if cps is None or fs_type is None:
            msg = (f'{p}: coverage and embedding permission unverified: pip install fonttools brotli, '
                   'or pass the TTF/OTF/WOFF of the same face')
            if not allow_unverified:
                fail(msg + ' (--allow-unverified embeds it anyway)')
            print('  warning: ' + msg + '; embedded anyway (--allow-unverified), not subset')
        else:
            if do_subset:
                data, kind = subset(data)
                _, cps, _ = facts(data, kind, fonttools)
                print(f'  subset: {kind}, {len(data)} bytes')
            gaps = [f'U+{c:04X} {chr(c)!r}' for c in REQUIRED if c not in (cps or ())]
            if gaps:
                missing_any = True
                print(f"  MISSING glyphs: {', '.join(gaps)}")
            else:
                print('  coverage: і ї є ґ ’ « » № NBSP minus present')
        mime, fmt = MIME[kind]
        b64 = base64.b64encode(data).decode('ascii')
        total += len(b64)
        notice = clean_notice(names.get(0, ''))
        url = names.get(14, '').strip()
        url = url if PLAIN_URL.match(url) else OFL_URL
        blocks.append(f"/* {family} {face['weight']}: {notice} Licence: SIL Open Font License 1.1, {url} */\n"
                      f"@font-face{{font-family:\"{family}\";font-style:normal;font-weight:{face['weight']};"
                      f"font-display:block;src:url(data:{mime};base64,{b64}) format(\"{fmt}\")}}")
        families.setdefault(face['role'], family)
        print(f'  adds {len(b64)} bytes as a data URI')
    if missing_any:
        print('refused: a face lacks required Ukrainian glyphs; pick another OFL face with full Cyrillic', file=sys.stderr)
        return 1
    root = ';'.join(f'--font-{r}:"{fam}", ' + FALLBACK[r].replace(f'"{fam}", ', '')
                    for r, fam in sorted(families.items()))
    region = START + '\n' + '\n'.join(blocks) + f'\n:root{{{root}}}\n' + END
    new = doc[:doc.index(START)] + region + doc[doc.index(END) + len(END):]
    print(f'total {total} bytes of fonts; deck grows from {len(doc.encode())} to {len(new.encode())} bytes')
    if total > WARN_BYTES:
        print('warning: more than 1.5 MB of fonts; subset (--subset) or drop a weight')
    if not apply:
        print('dry run: nothing written; add --apply to write the fonts into the deck')
        return 0
    with open(deck, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new)
    print(f'wrote {deck}; run the deck-review lint in both font modes (H3)')
    return 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    sys.exit(main(sys.argv[1:]))
