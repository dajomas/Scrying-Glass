"""Check this Python's runtime readiness; no package checksum verification."""
import argparse
import importlib.metadata
import importlib.util
from pathlib import Path
import subprocess
import sys


def runtime_preflight(root):
    print('Runtime preflight only; package integrity is not verified.')
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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', action='store_true',
                        help='compatibility alias; runtime preflight is now the default')
    parser.parse_args(argv)
    return runtime_preflight(Path(__file__).resolve().parents[1])


if __name__ == '__main__':
    sys.exit(main())
