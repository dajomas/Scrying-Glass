"""Assemble the admin page from ordered, UTF-8 HTML fragments.

ADMIN_HTML retains the existing server interface. Files load once at import;
restart the server after editing a fragment. No template engine is required.
"""
from pathlib import Path

_TEMPLATE_DIR = (
    Path(__file__).resolve().parent.parent / "templates" / "admin"
)

# Explicit order preserves the original DOM and markup boundaries.
_PARTS = (
    '000_document_start.html',
    '010_pane_controls.html',
    '020_battle_controls.html',
    '030_campaign_input.html',
    '040_character_input.html',
    '050_setup_input.html',
    '060_monster_input.html',
    '070_character_display.html',
    '080_monster_display.html',
    '090_activity_log.html',
    '100_tie_modal.html',
    '110_edit_modal.html',
    '120_setup_import_modal.html',
    '130_monster_help_modal.html',
    '140_campaign_modal.html',
    '150_campaign_setup_modal.html',
    '160_campaign_delete_modal.html',
    '170_csv_import_modal.html',
    '180_battle_action_modal.html',
    '190_document_end.html',
)


def build_admin_html() -> str:
    """Read and concatenate the trusted local fragments in document order."""
    return "".join(
        (_TEMPLATE_DIR / filename).read_text(encoding="utf-8")
        for filename in _PARTS
    )


# Existing callers continue to use: from admin_html import ADMIN_HTML.
ADMIN_HTML = build_admin_html()
