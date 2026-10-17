#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VDIR="${HOME}/dnd"
INSTALL_MARKER="${VDIR}/.scrying-glass-dependencies"

DEPENDENCIES=(
    "fastapi>=0.115"
    "uvicorn[standard]>=0.30"
    "PyYAML>=6.0"
    "python-multipart"
)

# Record the dependency specifications so changes trigger installation.
DEPENDENCY_SPEC="$(printf '%s\n' "${DEPENDENCIES[@]}")"

if [[ ! -x "${VDIR}/bin/python" || ! -f "${VDIR}/bin/activate" ]]; then
    PYTHON_COMMAND=""
    for candidate in python3 python3.14 python3.13 python3.12 python3.11 python3.10 python; do
        if command -v "$candidate" >/dev/null 2>&1 &&
           "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
            PYTHON_COMMAND="$candidate"
            break
        fi
    done

    if [[ -z "$PYTHON_COMMAND" ]]; then
        echo "ERROR: Python 3.10 or newer was not found on PATH." >&2
        exit 1
    fi

    "$PYTHON_COMMAND" -m venv "${VDIR}"

    # An environment that was recreated must be set up again.
    rm -f "${INSTALL_MARKER}"
fi

if ! "${VDIR}/bin/python" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
    echo "ERROR: Existing virtual environment requires Python 3.10 or newer. Recreate ${VDIR} after backing up any files stored there." >&2
    exit 1
fi

source "${VDIR}/bin/activate"

if ! python -c 'import sqlite3; print("SQLite:", sqlite3.sqlite_version)'; then
    echo "ERROR: This Python installation lacks sqlite3 support; repair Python, not pip dependencies." >&2
    exit 1
fi

if [[ ! -f "${INSTALL_MARKER}" ]] ||
   [[ "$(< "${INSTALL_MARKER}")" != "${DEPENDENCY_SPEC}" ]]; then
    echo "Installing Python dependencies..."

    python -m pip install --upgrade pip
    python -m pip install "${DEPENDENCIES[@]}"

    # Only mark installation complete after both commands succeed.
    printf '%s\n' "${DEPENDENCY_SPEC}" > "${INSTALL_MARKER}"
else
    echo "Python dependencies already installed; skipping pip."
fi

exec python scrying_glass_server.py --config config.yaml
