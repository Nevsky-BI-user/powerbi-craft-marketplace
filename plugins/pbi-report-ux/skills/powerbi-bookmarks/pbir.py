"""Byte-faithful load/save for Power BI PBIR-Legacy report.json.

report.json is json.dumps(indent=2, ensure_ascii=False) with CRLF, no BOM, no
trailing newline. Naive load->dump rewrites floats (PBI writes 980.00, Python
gives 980.0) -> thousands of diff lines. We parse floats as Decimal, wrap each
in a sentinel string, dump, then regex-strip the sentinel back to a bare number,
reproducing the file byte-for-byte.

Embedded strings (report-level `config`, each visualContainer `config`, section
`filters`) are themselves compact JSON strings -> use load_config / dump_config.

Usage:
    import pbir
    d   = pbir.load(r'C:\\path\\report.json')
    cfg = pbir.load_config(d['config'])
    ... edit ...
    d['config'] = pbir.dump_config(cfg)
    pbir.save(d, r'C:\\path\\report.json')
"""
import json
import re
from decimal import Decimal

RAW = '@@RAWNUM@@'
END = '@@ENDRAW@@'
PATH = None  # optionally set a default path


def _wrap(o):
    if isinstance(o, Decimal):
        return RAW + str(o) + END
    if isinstance(o, dict):
        return {k: _wrap(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_wrap(v) for v in o]
    return o


def _dumps(obj, indent):
    wrapped = _wrap(obj)
    if indent is None:
        s = json.dumps(wrapped, ensure_ascii=False, separators=(',', ':'))
    else:
        s = json.dumps(wrapped, ensure_ascii=False, indent=indent)
    return re.sub(r'"' + RAW + r'(.*?)' + END + r'"', r'\1', s)


def load(path=None):
    path = path or PATH
    with open(path, 'rb') as f:
        return json.loads(f.read().decode('utf-8'), parse_float=Decimal)


def save(obj, path=None):
    path = path or PATH
    s = _dumps(obj, indent=2).replace('\r\n', '\n').replace('\n', '\r\n')
    with open(path, 'wb') as f:
        f.write(s.encode('utf-8'))


def load_config(s):
    """Parse an embedded compact JSON string (config / filters) -> python obj."""
    return json.loads(s, parse_float=Decimal)


def dump_config(obj):
    """Serialize back to a compact JSON string (PBI style, separators=(',',':'))."""
    return _dumps(obj, indent=None)


def verify_roundtrip(path):
    """Sanity check: load+save reproduces the file byte-for-byte."""
    with open(path, 'rb') as f:
        orig = f.read()
    new = _dumps(load(path), indent=2).replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-8')
    return orig == new


# --------------------------------------------------------------------------
# Geometry lives in TWO places per visualContainer:
#   1. cfg['layouts'][0]['position']  <- what Power BI Desktop actually renders
#   2. vc['x'|'y'|'width'|'height'|'z'] <- mirror copy, 2 decimals
# Writing only the mirror is a silent no-op on the canvas (a task can "pass"
# its own check and change nothing visible). ALWAYS write both -> set_position.
# --------------------------------------------------------------------------
GEOM_KEYS = ('x', 'y', 'z', 'width', 'height')


def set_position(vc, cfg, **kw):
    """Write geometry to both copies. kw: x/y/z/width/height (Decimal or number).

    Re-serializes vc['config'] from cfg, so call it after any other cfg edits
    or pass the same cfg object you keep editing.
    """
    pos = cfg['layouts'][0]['position']
    for key, val in kw.items():
        if key not in GEOM_KEYS:
            raise KeyError('unknown geometry key %r' % key)
        if val is None:
            continue
        val = val if isinstance(val, Decimal) else Decimal(str(val))
        pos[key] = val
        vc[key] = Decimal('%.2f' % val)
    vc['config'] = dump_config(cfg)
    return pos


def geometry_mismatches(obj, tol=0.011):
    """Containers whose mirror geometry disagrees with layouts[0].position.

    Returns [(section, visualName, key, mirror, config)]. tol allows for the
    2-decimal rounding PBI writes into the mirror copy.
    """
    out = []
    for s in obj.get('sections', []):
        for vc in s.get('visualContainers', []):
            cfg = load_config(vc['config'])
            layouts = cfg.get('layouts') or []
            if not layouts:
                continue
            pos = layouts[0].get('position') or {}
            for key in GEOM_KEYS:
                a, b = vc.get(key), pos.get(key)
                if a is None or b is None:
                    continue
                if abs(float(a) - float(b)) > tol:
                    out.append((s.get('displayName'), cfg.get('name'), key, a, b))
    return out


if __name__ == '__main__':
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else PATH
    print('byte-identical roundtrip:', verify_roundtrip(p))
    bad = geometry_mismatches(load(p))
    print('geometry mismatches (mirror vs layouts[0].position):', len(bad))
    for row in bad[:20]:
        print('   %s | %s | %s: mirror=%s config=%s' % row)
