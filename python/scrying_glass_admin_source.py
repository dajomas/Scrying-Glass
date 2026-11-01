"""Assemble the Admin classic script without changing its execution scope."""
from pathlib import Path

ADMIN_SCRIPT_PARTS = (
    "010-source.js",
    "020-source.js",
    "030-source.js",
    "040-source.js",
    "050-source.js",
)
MAX_SOURCE_BYTES = 25_000


def read_admin_script(static_directory: Path) -> bytes:
    """Concatenate trusted source fragments in their explicit original order.

    The resulting HTTP response is one classic script, not five independently
    executed scripts. Do not insert separators: the fragments retain every
    original byte, including whitespace and comments at their boundaries.
    """
    directory = Path(static_directory) / "admin"
    parts = []
    for name in ADMIN_SCRIPT_PARTS:
        data = (directory / name).read_bytes()
        if len(data) > MAX_SOURCE_BYTES:
            raise ValueError(f"Admin script source exceeds {MAX_SOURCE_BYTES} bytes: {name}")
        data.decode("utf-8")
        parts.append(data)
    return b"".join(parts)
