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


CRLF = '\r\n'
LF = '\n'


def _eol(path):
    """Newline convention of the file on disk.

    Power BI Desktop writes CRLF, but a checkout on Linux/macOS (or with
    core.autocrlf=false) holds LF. Hardcoding CRLF made verify_roundtrip()
    report a false mismatch there, so the convention is taken from the file.
    """
    try:
        with open(path, 'rb') as f:
            head = f.read(65536)
    except OSError:
        return CRLF
    if b'\r\n' in head:
        return CRLF
    return LF if b'\n' in head else CRLF


def load(path=None):
    path = path or PATH
    with open(path, 'rb') as f:
        return json.loads(f.read().decode('utf-8'), parse_float=Decimal)


def save(obj, path=None):
    path = path or PATH
    eol = _eol(path)
    s = _dumps(obj, indent=2).replace(CRLF, LF).replace(LF, eol)
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
    new = _dumps(load(path), indent=2).replace(CRLF, LF).replace(LF, _eol(path)).encode('utf-8')
    return orig == new


if __name__ == '__main__':
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else PATH
    print('byte-identical roundtrip:', verify_roundtrip(p))
