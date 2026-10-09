BRANCH=$(git rev-parse --abbrev-ref HEAD)
HASH=$(git rev-parse ${BRANCH} | cut -c1-7)

echo "Create git archive for branch ${BRANCH}"
git archive --format=zip --output=scrying-glass-source.zip ${BRANCH}

echo "Convert zip file to base64"
python3 - ${HASH}<<'PY'
import base64, sys
from pathlib import Path

HASH=sys.argv[1]
source = Path("scrying-glass-source.zip")
target = Path(f"scrying-glass-source-{HASH}-base64.txt")
target.write_text(
    base64.b64encode(source.read_bytes()).decode("ascii"),
    encoding="ascii",
)
PY
