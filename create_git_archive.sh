BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo "Create git archive for branch ${BRANCH}"
git archive --format=zip --output=scrying-glass-source.zip ${BRANCH}

echo "Convert zip file to base64"
python3 - <<'PY'
import base64
from pathlib import Path

source = Path("scrying-glass-source.zip")
target = Path("scrying-glass-source-base64.txt")
target.write_text(
    base64.b64encode(source.read_bytes()).decode("ascii"),
    encoding="ascii",
)
PY
