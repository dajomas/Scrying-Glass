"""Assemble the Admin classic script without changing its execution scope."""
from pathlib import Path

ADMIN_SCRIPT_PARTS = (
    "010-source.js", "020-source.js", "030-source.js", "040-source.js",
    "050-source.js", "060-source.js", "070-source.js", "080-source.js",
)
MAX_SOURCE_BYTES = 20_000


def read_admin_script(static_directory: Path) -> bytes:
    """Join trusted UTF-8 fragments without inserting separators."""
    directory = Path(static_directory) / "admin"
    parts = []
    for name in ADMIN_SCRIPT_PARTS:
        data = (directory / name).read_bytes()
        if len(data) > MAX_SOURCE_BYTES:
            raise ValueError(f"Admin script source exceeds {MAX_SOURCE_BYTES} bytes: {name}")
        data.decode("utf-8")
        parts.append(data)
    return b"".join(parts)
