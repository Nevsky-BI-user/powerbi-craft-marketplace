#!/usr/bin/env python3
"""Scaffold an html-deck presentation from deck-plan.json (deck-plan/1).

Usage: python3 scaffold_deck.py deck-plan.json out.html [--template ../assets/deck-template.html] [--apply] [--force]

Dry run by default: validates the plan against the template, prints the table
n | id | archetype | part | title | budget and the unfilled slots per slide, writes nothing.
--apply writes out.html; an existing file is kept unless --force is given.

What it does (html-deck references/engine.md §13):
- clones one <template data-archetype="..."> snippet per plan slide into the space between
  <!-- @slides:start --> and <!-- @slides:end --> of the template; nothing outside the markers changes
  except <title>, <html lang> and script#deck-data;
- sets section id, data-part, data-mode="reading" (reading decks and appendix slides) and data-appendix;
- fills the slots eyebrow, title, dek, notes, list, media, plus context (title slide) and next, url
  (close and cta) from the plan; removes optional slots the plan leaves empty;
- writes media[0].file as a relative img src and warns: inline_media.py turns it into a data URI;
- keeps data-todo on every other slot, so an unfilled scaffold fails deck-review H8 (critical);
- writes script#deck-data = {meta, parts, lists, minutes} for the engine (lists, route, presenter timer).

Exit: 0 ok; 1 refused to overwrite without --force; 2 usage, invalid plan, missing template or snippet.
Stdlib only, deterministic output, no subprocesses, never opens a window.
"""
import html
import json
import os
import re
import sys

USAGE = ('usage: python3 scaffold_deck.py deck-plan.json out.html '
         '[--template ../assets/deck-template.html] [--apply] [--force]')
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATE = os.path.join(HERE, '..', 'assets', 'deck-template.html')
THRESHOLDS = os.path.join(HERE, '..', '..', 'deck-review', 'scripts', 'thresholds.json')
MODES = ('talk', 'reading', 'talk+appendix')
SLUG = re.compile(r'^[a-z0-9][a-z0-9-]*$')
START, END = '<!-- @slides:start -->', '<!-- @slides:end -->'
NOTES_HINT = 'нотатки: підказка, тези, числа з базою, перехід, позначка часу'


def fail(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


def esc(text):
    """HTML-escape slide text; keep NBSP visible in the source as &nbsp;."""
    return html.escape(str(text), quote=False).replace(' ', '&nbsp;')


def esc_attr(text):
    return html.escape(str(text), quote=True).replace(' ', '&nbsp;')


# ---------- snippet editing (snippets are ours: a slot element never nests an element of its own tag)
def slot_re(name):
    return re.compile(r'(?P<indent>[ \t]*)<(?P<tag>[a-zA-Z][\w-]*)(?P<attrs>[^>]*\bdata-slot="' + re.escape(name)
                      + r'"[^>]*)>(?P<inner>.*?)</(?P=tag)>(?P<nl>\n?)', re.S)


def has_slot(snip, name):
    return bool(slot_re(name).search(snip))


def drop_todo(attrs):
    return re.sub(r'\s+data-todo(="[^"]*")?', '', attrs)


def fill(snip, name, text=None, attrs=None, inner=None, keep_todo=None):
    """Fill one slot: text (escaped) or raw inner HTML, extra attributes; removes data-todo unless keep_todo."""
    m = slot_re(name).search(snip)
    if not m:
        return snip, False
    a = m.group('attrs')
    for k, v in (attrs or {}).items():
        a = re.sub(r'\s+' + re.escape(k) + r'(="[^"]*")?', '', a)
        a += f' {k}' if v is True else f' {k}="{esc_attr(v)}"'
    a = drop_todo(a)
    if keep_todo is not None:
        a += f' data-todo="{esc_attr(keep_todo)}"'
    body = m.group('inner') if text is None and inner is None else (inner if inner is not None else esc(text))
    new = f"{m.group('indent')}<{m.group('tag')}{a}>{body}</{m.group('tag')}>{m.group('nl')}"
    return snip[:m.start()] + new + snip[m.end():], True


def remove(snip, name):
    m = slot_re(name).search(snip)
    return (snip[:m.start()] + snip[m.end():], True) if m else (snip, False)


def set_img(snip, media, title, out_dir):
    """media slot: img src, alt, data-ui-px, data-native-width from media[0]; data-todo stays if the file is missing."""
    m = slot_re('media').search(snip)
    if not m:
        return snip, None
    item = media[0]
    inner = m.group('inner')
    img = re.search(r'<img\b[^>]*>', inner)
    attrs = {'src': item.get('file', ''), 'alt': title}
    if item.get('ui_px') is not None:
        attrs['data-ui-px'] = item['ui_px']
    if item.get('native_px') is not None:
        attrs['data-native-width'] = item['native_px']
    tag = '<img' + ''.join(f' {k}="{esc_attr(v)}"' for k, v in attrs.items()) + '>'
    inner = inner[:img.start()] + tag + inner[img.end():] if img else tag
    path = os.path.join(out_dir, item.get('file', ''))
    missing = not item.get('file') or not os.path.isfile(path)
    hint = f"файл не знайдено: {item.get('file', '')}" if missing else None
    snip, _ = fill(snip, 'media', inner=inner, keep_todo=hint)
    return snip, hint


# ---------- plan checks (contract errors only; deck_lint.py --plan-only judges the deck)
def validate(plan, snippets):
    errs = []
    if not isinstance(plan, dict):
        return ['plan is not a JSON object']
    if plan.get('schema') != 'deck-plan/1':
        errs.append(f"schema must be 'deck-plan/1', got {plan.get('schema')!r}")
    for key in ('title', 'lang', 'mode', 'slides'):
        if key not in plan:
            errs.append(f'missing required field: {key}')
    if plan.get('mode') not in MODES:
        errs.append(f"mode must be one of {', '.join(MODES)}, got {plan.get('mode')!r}")
    parts = {p.get('id') for p in plan.get('parts') or [] if isinstance(p, dict)}
    lists = plan.get('lists') or {}
    slides = plan.get('slides')
    if not isinstance(slides, list) or not slides:
        errs.append('slides must be a non-empty array')
        return errs
    seen = set()
    for k, s in enumerate(slides):
        where = f'slides[{k}]'
        if not isinstance(s, dict):
            errs.append(f'{where} is not an object')
            continue
        if s.get('n') != k + 1:
            errs.append(f"{where}.n is {s.get('n')!r}, expected {k + 1}")
        sid = s.get('id')
        if not isinstance(sid, str) or not SLUG.match(sid):
            errs.append(f'{where}.id {sid!r} is not a slug [a-z0-9][a-z0-9-]*')
        elif sid in seen:
            errs.append(f'{where}.id {sid!r} is a duplicate')
        seen.add(sid)
        if s.get('archetype') not in snippets:
            errs.append(f"{where}.archetype {s.get('archetype')!r} has no <template data-archetype> in the template")
        if not s.get('title'):
            errs.append(f'{where}.title is missing')
        if s.get('part') is not None and s.get('part') not in parts:
            errs.append(f"{where}.part {s.get('part')!r} is not in parts")
        if s.get('list') and s['list'] not in lists and s['list'] != 'parts':
            errs.append(f"{where}.list {s['list']!r} is not in lists")
        ser = s.get('series')
        if ser:
            items = [i.get('id') for i in lists.get(ser.get('list'), [])]
            if not items:
                errs.append(f"{where}.series.list {ser.get('list')!r} is not in lists")
            elif ser.get('item') not in items:
                errs.append(f"{where}.series.item {ser.get('item')!r} is not in lists.{ser.get('list')}")
        if s.get('media') is not None and (not isinstance(s['media'], list) or not s['media']
                                           or not isinstance(s['media'][0], dict)):
            errs.append(f'{where}.media must be a non-empty array of objects')
    return errs


def recap_source(plan):
    recap = (plan.get('close') or {}).get('recap') or []
    if not recap:
        return None
    if sorted(recap) == sorted(p.get('title') for p in plan.get('parts') or []):
        return 'parts'
    for name, items in sorted((plan.get('lists') or {}).items()):
        if sorted(recap) == sorted(i.get('label') for i in items):
            return name
    return None


def budget(th, plan, s):
    if not th:
        return '-'
    arch = th.get('archetypes', {}).get(s['archetype'], {})
    mode = 'reading' if plan['mode'] == 'reading' or s.get('appendix') else 'talk'
    d1 = (th['checks'].get('D1') or {}).get(mode) or {}
    y1 = (th['checks'].get('Y1') or {}).get(mode) or {}
    if mode == 'reading' and arch.get('mode') == 'talk':
        words, mpt = d1.get('words_max'), y1.get('floor_pt')
    else:
        words = arch.get('words_max') or d1.get('words_max')
        mpt = arch.get('min_pt') or y1.get('floor_pt')
    return f'{words}w {mpt}pt'


def build_slide(plan, s, snippet, out_dir, warnings):
    a = s['archetype']
    reading = plan['mode'] == 'reading' or bool(s.get('appendix'))
    main_talk = not reading
    close = plan.get('close') or {}
    snip = snippet.strip('\n')
    head = re.search(r'<section\b[^>]*>', snip)
    if not head:
        fail(f'snippet {a!r} has no <section> element', 2)
    attrs = f'class="slide a-{a}" id="{esc_attr(s["id"])}" data-archetype="{a}"'
    if s.get('part'):
        attrs += f' data-part="{esc_attr(s["part"])}"'
    if reading:
        attrs += ' data-mode="reading"'
    if s.get('appendix'):
        attrs += ' data-appendix'
    snip = snip[:head.start()] + f'<section {attrs}>' + snip[head.end():]

    snip, ok = fill(snip, 'title', s['title'])
    if not ok:
        warnings.append(f"{s['id']}: snippet {a!r} has no title slot")
    # eyebrow: plan text, else a generated series label, else removed
    if s.get('eyebrow'):
        snip, ok = fill(snip, 'eyebrow', s['eyebrow'])
        if not ok:
            warnings.append(f"{s['id']}: eyebrow ignored, archetype {a!r} has no eyebrow slot")
    elif a == 'series-item' and s.get('series'):
        snip = slot_re('eyebrow').sub(lambda m: f"{m.group('indent')}<p class=\"eyebrow\" data-item-n></p>{m.group('nl')}", snip, 1)
    else:
        snip, _ = remove(snip, 'eyebrow')
    # dek: plan text; the title slide falls back to the promise; optional elsewhere
    dek = s.get('dek') or (plan.get('promise') if a == 'title' else None)
    if dek:
        snip, ok = fill(snip, 'dek', dek)
        if not ok:
            warnings.append(f"{s['id']}: dek ignored, archetype {a!r} has no dek slot")
    elif not (a == 'title' and main_talk):
        snip, _ = remove(snip, 'dek')
    if a == 'title':
        if plan.get('context'):
            snip, _ = fill(snip, 'context', plan['context'])
        elif not main_talk:
            snip, _ = remove(snip, 'context')
    # notes: required on main talk slides (H6), backup answers elsewhere
    if s.get('notes'):
        snip, _ = fill(snip, 'notes', s['notes'])
    elif main_talk:
        snip, _ = fill(snip, 'notes', keep_todo=NOTES_HINT)
    else:
        snip, _ = remove(snip, 'notes')
    # list: hub and journey from slide.list, series items from series, close from the recap
    name, cur = s.get('list'), None
    if s.get('series'):
        name, cur = s['series']['list'], s['series']['item']
    if a == 'close' and not name:
        name = recap_source(plan)
        if close.get('recap') and not name:
            snip, _ = fill(snip, 'list', keep_todo='recap не збігається з plan.parts чи plan.lists: виправте план')
    if name:
        extra = {'data-list': name}
        if cur:
            extra['data-current'] = cur
        inner = None
        if a == 'hub':
            items = (plan.get('lists') or {}).get(name, [])
            inner = ''.join(f'<li data-item="{esc_attr(i.get("id"))}" data-todo="відмінність пункту, одне речення"></li>'
                            for i in items)
        snip, ok = fill(snip, 'list', attrs=extra, inner=inner)
        if not ok:
            warnings.append(f"{s['id']}: list {name!r} ignored, archetype {a!r} has no list slot")
    # media: screenshots and photos
    if s.get('media'):
        snip, hint = set_img(snip, s['media'], s.get('claim') or s['title'], out_dir)
        if hint:
            warnings.append(f"{s['id']}: {hint}")
    # close and cta: next step and URL from plan.close
    if a in ('close', 'cta'):
        if close.get('next_step'):
            snip, _ = fill(snip, 'next', close['next_step'])
        if close.get('url'):
            snip, _ = fill(snip, 'url', close['url'])
        elif a == 'close':
            snip = re.sub(r'[ \t]*<p><span class="pill url"[^>]*></span></p>\n?', '', snip)
    return snip


def main(argv):
    if '-h' in argv or '--help' in argv:
        print(__doc__)
        return 0
    pos, template, apply, force = [], DEFAULT_TEMPLATE, False, False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == '--template':
            if i + 1 >= len(argv):
                fail(f'--template needs a path\n{USAGE}')
            template = argv[i + 1]
            i += 1
        elif a == '--apply':
            apply = True
        elif a == '--force':
            force = True
        elif a.startswith('--'):
            fail(f'unknown option {a}\n{USAGE}')
        else:
            pos.append(a)
        i += 1
    if len(pos) != 2:
        fail(USAGE)
    plan_path, out_path = pos
    if not os.path.isfile(plan_path):
        fail(f'plan not found: {plan_path}\n{USAGE}')
    if not os.path.isfile(template):
        fail(f'template not found: {template}')
    out_dir = os.path.dirname(os.path.abspath(out_path))
    if not os.path.isdir(out_dir):
        fail(f'output folder does not exist: {out_dir}')
    try:
        with open(plan_path, encoding='utf-8') as f:
            plan = json.load(f)
    except (OSError, ValueError) as e:
        fail(f'cannot read plan {plan_path}: {e}')
    with open(template, encoding='utf-8') as f:
        tpl = f.read()
    if tpl.count(START) != 1 or tpl.count(END) != 1 or tpl.index(START) > tpl.index(END):
        fail(f'template {template} must hold exactly one {START} before one {END}')
    snippets = {}
    for m in re.finditer(r'<template data-archetype="([a-z0-9-]+)">(.*?)</template>', tpl, re.S):
        if m.group(1) in snippets:
            fail(f'template has two snippets for {m.group(1)!r}')
        snippets[m.group(1)] = m.group(2)
    errs = validate(plan, snippets)
    if errs:
        print(f'invalid plan {plan_path} ({len(errs)} problems):', file=sys.stderr)
        for e in errs:
            print(f'  - {e}', file=sys.stderr)
        return 2
    th = None
    if os.path.isfile(THRESHOLDS):
        try:
            with open(THRESHOLDS, encoding='utf-8') as f:
                th = json.load(f)
        except (OSError, ValueError):
            th = None

    warnings, sections, rows = [], [], []
    for s in plan['slides']:
        sec = build_slide(plan, s, snippets[s['archetype']], out_dir, warnings)
        sections.append(sec)
        todo = len(re.findall(r'\bdata-todo\b', sec))
        rows.append((str(s['n']), s['id'], s['archetype'], s.get('part') or '-', s['title'], budget(th, plan, s), str(todo)))

    data = {
        'meta': {k: plan.get(k) for k in ('title', 'lang', 'mode', 'minutes', 'qa_minutes', 'dash_policy')},
        'parts': plan.get('parts') or [],
        'lists': plan.get('lists') or {},
        'minutes': {s['id']: s['minutes'] for s in plan['slides'] if s.get('minutes') is not None},
    }
    blob = json.dumps(data, ensure_ascii=False, indent=2).replace('</', '<\\/')
    a, b = tpl.index(START) + len(START), tpl.index(END)
    out = tpl[:a] + '\n' + '\n'.join(sections) + '\n' + tpl[b:]
    out, n = re.subn(r'(<script\b[^>]*\bid="deck-data"[^>]*>).*?(</script>)', lambda m: m.group(1) + '\n' + blob + '\n' + m.group(2), out, count=1, flags=re.S)
    if not n:
        fail(f'template {template} has no script#deck-data')
    out = re.sub(r'<title>.*?</title>', lambda m: f'<title>{esc(plan["title"])}</title>', out, count=1, flags=re.S)
    out = re.sub(r'<html\b[^>]*>', lambda m: f'<html lang="{esc_attr(plan["lang"])}">', out, count=1)

    head = ('n', 'id', 'archetype', 'part', 'title', 'budget', 'todo')
    widths = [max(len(r[c]) for r in rows + [head]) for c in range(len(head))]
    widths[4] = min(widths[4], 44)
    for r in [head] + rows:
        print(' | '.join((r[c] if c != 4 or len(r[c]) <= 44 else r[c][:43] + '…').ljust(widths[c]) for c in range(len(head))).rstrip())
    total = sum(int(r[6]) for r in rows)
    print(f'\n{len(rows)} slides, {total} unfilled slots (data-todo: deck-review H8 is critical until each is filled)')
    status = (plan.get('approval') or {}).get('status')
    if status != 'approved':
        warnings.append(f'approval.status is {status!r}: deck-storyline builds nothing before an approved storyboard')
    if not th:
        warnings.append('deck-review thresholds.json not found next to this skill: budget column empty')
    shots = [s['id'] for s in plan['slides'] if s.get('media')]
    if shots:
        warnings.append(f"media src is a relative path on {', '.join(shots)}: run inline_media.py on the deck "
                        'before sending, so it stays one file')
    for w in warnings:
        print(f'warning: {w}')
    if not apply:
        print(f'dry run: nothing written; add --apply to write {out_path}')
        return 0
    if os.path.exists(out_path) and not force:
        print(f'refused: {out_path} exists; add --force to overwrite', file=sys.stderr)
        return 1
    with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(out)
    print(f'wrote {out_path} ({len(out.encode("utf-8"))} bytes)')
    return 0


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    sys.exit(main(sys.argv[1:]))
