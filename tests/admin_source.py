"""static/admin.js is one classic script; browser tests that run part of it take the lines
from one marker line up to (not including) another. Mirrors tests/admin-source.cjs."""
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / 'static' / 'admin.js').read_text(encoding='utf-8')


def _line_start(marker):
    first = SOURCE.find(marker)
    if first < 0 or SOURCE.find(marker, first + 1) >= 0:
        raise ValueError(f'Admin marker must occur once: {marker}')
    if first > 0 and SOURCE[first - 1] != '\n':
        raise ValueError(f'Admin marker must start a line: {marker}')
    return first


def admin_range(start=None, end=None):
    return SOURCE[_line_start(start) if start else 0:_line_start(end) if end else len(SOURCE)]
