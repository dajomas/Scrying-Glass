"""Migrations services using the live server context."""

from __future__ import annotations
from typing import Any, Literal
from pathlib import Path
from fastapi import HTTPException, Request as FastAPIRequest, UploadFile


class MigrationsService:
    """Group migrations operations without owning a separate copy of runtime state."""

    def __init__(self, context: Any) -> None:
        """Retain the live server context."""
        self.context = context

    def migrate_unassigned_setups(self) -> list[str]:
        'Move battle setups that are not connected to a campaign into "Default".\n\n    Also keeps the registry and the directories consistent:\n      * campaign directories without a registry entry are registered;\n      * registry entries without a directory get their directory recreated;\n      * there is always at least one campaign and a valid active campaign.\n    Returns the names of the setups that were moved.\n    '
        data = self.context.read_campaigns()
        dirty = not self.context.CAMPAIGNS_FILE.exists()
        campaigns = data['campaigns']

        for directory in self.context.SETUPS_DIR.iterdir():
            if directory.is_dir() and directory.name not in campaigns:
                campaigns[directory.name] = {
                    'name': directory.name.replace('-', ' ').title(),
                    'description': '',
                    'created': self.context.now_iso(),
                }
                dirty = True

        for slug in campaigns:
            self.context.campaign_dir(slug).mkdir(parents=True, exist_ok=True)

        moved: list[str] = []
        loose = sorted(self.context.SETUPS_DIR.glob('*.json'), key=lambda p: p.name.casefold())
        if loose or not campaigns:
            created_default = self.context.DEFAULT_CAMPAIGN_SLUG not in campaigns
            if created_default:
                campaigns[self.context.DEFAULT_CAMPAIGN_SLUG] = {
                    'name': self.context.DEFAULT_CAMPAIGN_NAME,
                    'description': 'Battle setups that were not connected to a campaign',
                    'created': self.context.now_iso(),
                }
                dirty = True
            target = self.context.campaign_dir(self.context.DEFAULT_CAMPAIGN_SLUG)
            target.mkdir(parents=True, exist_ok=True)
            newest: tuple[float, str] | None = None
            for src in loose:
                mtime = src.stat().st_mtime
                dst = self.context.unique_setup_path(target, src.stem)
                src.replace(dst)
                moved.append(dst.stem)
                if newest is None or mtime > newest[0]:
                    newest = (mtime, dst.stem)
            if created_default:
                # New campaign: add the empty "Default" battle setup (skipped if a
                # moved setup already uses that name).
                self.context.create_default_setup(self.context.DEFAULT_CAMPAIGN_SLUG)
                if newest is not None:
                    # The most recently modified moved setup counts as "most recently
                    # worked on", so activating Default opens it instead of the empty one.
                    campaigns[self.context.DEFAULT_CAMPAIGN_SLUG]['last_setup'] = newest[1]

        if data['active'] not in campaigns:
            data['active'] = self.context.DEFAULT_CAMPAIGN_SLUG if self.context.DEFAULT_CAMPAIGN_SLUG in campaigns else sorted(campaigns, key=str.casefold)[0]
            dirty = True

        if dirty or moved:
            self.context.write_campaigns(data)
        if moved:
            print(f'Moved {len(moved)} unassigned battle setup(s) into campaign "{campaigns[self.context.DEFAULT_CAMPAIGN_SLUG]["name"]}": {", ".join(moved)}')
        return moved

    def migrate_campaign_characters(self) -> None:
        """Create missing campaign character rosters from existing setup snapshots."""
        self.context.CHARACTERS_DIR.mkdir(parents=True, exist_ok=True)

        data = self.context.read_campaigns()

        for slug, metadata in data["campaigns"].items():
            roster_path = self.context.campaign_characters_path(slug)

            if roster_path.exists():
                continue

            names = self.context.list_setups(slug)
            preferred = metadata.get("last_setup")

            if preferred in names:
                source_name = preferred
            elif names:
                source_name = max(
                    names,
                    key=lambda name: self.context.setup_path(name, slug).stat().st_mtime,
                )
            else:
                source_name = None

            characters: list[dict[str, Any]] = []

            if source_name is not None:
                try:
                    raw = self.context.json.loads(
                        self.context.setup_path(source_name, slug).read_text(encoding="utf-8")
                    )
                    characters = self.context.normalize_state(raw)["characters"]
                except (OSError, self.context.json.JSONDecodeError, ValueError):
                    characters = []

            self.context.save_campaign_characters(slug, characters)
