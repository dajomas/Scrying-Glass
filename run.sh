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
    python3.14 -m venv "${VDIR}"

    # An environment that was recreated must be set up again.
    rm -f "${INSTALL_MARKER}"
fi

source "${VDIR}/bin/activate"

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