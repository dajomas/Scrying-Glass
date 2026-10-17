"""Verify listed package files; optionally check this Python's runtime readiness."""
import argparse
import hashlib
import importlib.metadata
import importlib.util
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', action='store_true', help='also check Python, dependencies and server import')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        manifest = json.loads((root / 'package-manifest.json').read_text(encoding='utf-8'))
        for entry in manifest['files']:
            path = root / entry['path']
            if Path(entry['path']).is_absolute() or '..' in Path(entry['path']).parts:
                raise ValueError('Unsafe manifest path: ' + entry['path'])
            if not path.is_file():
                raise ValueError('Missing package file: ' + entry['path'])
            data = path.read_bytes()
            if len(data) != entry['size_bytes'] or hashlib.sha256(data).hexdigest() != entry['sha256']:
                raise ValueError('Package file differs: ' + entry['path'])
        print('Package checksums passed:', len(manifest['files']), 'listed files.')
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('Package verification failed:', error, file=sys.stderr)
        return 1
    if not args.runtime:
        return 0
    print('Python:', sys.version)
    if sys.version_info < (3, 10):
        print('Runtime requires Python 3.10 or newer.', file=sys.stderr)
        return 1
    try:
        import sqlite3
        print('SQLite:', sqlite3.sqlite_version)
    except ImportError as error:
        print('Working standard-library sqlite3 is required:', error, file=sys.stderr)
        return 1
    missing = []
    for distribution, module in [('fastapi', 'fastapi'), ('uvicorn', 'uvicorn'),
                                 ('PyYAML', 'yaml'), ('python-multipart', 'multipart'),
                                 ('pydantic', 'pydantic')]:
        try:
            version = importlib.metadata.version(distribution)
            if importlib.util.find_spec(module) is None:
                raise importlib.metadata.PackageNotFoundError(distribution)
            print(distribution + ':', version)
        except importlib.metadata.PackageNotFoundError:
            missing.append(distribution)
    if missing:
        print('Missing runtime dependencies: ' + ', '.join(missing), file=sys.stderr)
        print('Install requirements.txt using this environment, then repeat the check.', file=sys.stderr)
        return 1
    result = subprocess.run([sys.executable, '-c',
        'import fastapi, uvicorn, yaml, multipart; from pydantic import model_validator; import scrying_glass_server; print("Server import and route construction passed.")'],
        cwd=str(root))
    if result.returncode:
        return result.returncode
    print('Runtime preflight passed. Storage, listeners, browser workflows and authentication are not exercised.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
