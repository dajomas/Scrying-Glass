#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VDIR="${HOME}/dnd"

if [[ ! -x "${VDIR}/bin/python" || ! -f "${VDIR}/bin/activate" ]]; then
    python3.14 -m venv "${VDIR}"
fi

source "${VDIR}/bin/activate"

python -m pip install --upgrade pip
python -m pip install \
    "fastapi>=0.115" \
    "uvicorn[standard]>=0.30" \
    "PyYAML>=6.0" \
    python-multipart

exec python scrying_glass_server.py --config config.yaml