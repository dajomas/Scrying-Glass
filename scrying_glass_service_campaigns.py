"""Campaigns services using the live server context."""

from __future__ import annotations
from typing import Any, Literal
from pathlib import Path
from fastapi import HTTPException, Request as FastAPIRequest, UploadFile


class CampaignsService:
    """Group campaigns operations without owning a separate copy of runtime state."""

    def __init__(self, context: Any) -> None:
        """Retain the live server context."""
        self.context = context

    def setup_path(self, name: str, campaign: str | None=None) -> Path:
        """Setup path."""
        return self.context.campaign_dir(self.context.require_campaign(campaign)) / (self.context.setup_slug(name) + '.json')

    def campaign_characters_path(self, slug: str) -> Path:
        """Campaign characters path."""
        return self.context.CHARACTERS_DIR / f"{slug}.json"

    def list_setups(self, campaign: str | None=None) -> list[str]:
        """List setups."""
        return sorted((p.stem for p in self.context.campaign_dir(self.context.require_campaign(campaign)).glob('*.json')), key=str.casefold)

    def campaign_dir(self, slug: str) -> Path:
        """Campaign dir."""
        return self.context.SETUPS_DIR / slug

    def read_campaigns(self) -> dict[str, Any]:
        """Read campaigns."""
        data: dict[str, Any] = {'active': None, 'campaigns': {}}
        if self.context.CAMPAIGNS_FILE.exists():
            try:
                raw = self.context.json.loads(self.context.CAMPAIGNS_FILE.read_text(encoding='utf-8'))
            except (OSError, self.context.json.JSONDecodeError):
                raw = {}
            if isinstance(raw, dict):
                if isinstance(raw.get('campaigns'), dict):
                    data['campaigns'] = {
                        str(k): v for k, v in raw['campaigns'].items() if isinstance(v, dict)
                    }
                if isinstance(raw.get('active'), str):
                    data['active'] = raw['active']
        for slug, meta in data['campaigns'].items():
            meta.setdefault('name', slug)
            meta.setdefault('description', '')
            meta.setdefault('created', self.context.now_iso())
        return data

    def write_campaigns(self, data: dict[str, Any]) -> None:
        """Write campaigns."""
        temp = self.context.CAMPAIGNS_FILE.with_suffix('.tmp')
        temp.write_text(self.context.json.dumps(data, indent=2), encoding='utf-8')
        temp.replace(self.context.CAMPAIGNS_FILE)

    def active_campaign(self) -> str:
        """Active campaign."""
        return self.context.read_campaigns()['active'] or self.context.DEFAULT_CAMPAIGN_SLUG

    def require_campaign(self, campaign: str | None) -> str:
        """Resolve an optional campaign slug/name to an existing campaign slug."""
        if campaign is None or not str(campaign).strip():
            slug = self.context.active_campaign()
        else:
            slug = self.context.campaign_slug(str(campaign))
        if slug not in self.context.read_campaigns()['campaigns']:
            raise self.context.HTTPException(404, f'Campaign not found: {slug}')
        self.context.campaign_dir(slug).mkdir(parents=True, exist_ok=True)
        return slug

    def create_default_setup(self, slug: str) -> str | None:
        'Create an empty battle setup called "Default" in a newly created campaign.\n\n    Does nothing (returns None) if the campaign already has a setup with that name.\n    '
        directory = self.context.campaign_dir(slug)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f'{self.context.DEFAULT_SETUP_NAME}.json'
        if path.exists():
            return None
        empty = self.context.normalize_state({'monsters': [], 'characters': [], 'battle_order': [], 'activity_log': [], 'display': {'background': self.context.configured_background(),}})
        temp = path.with_suffix('.tmp')
        temp.write_text(
            self.context.json.dumps(self.context.setup_snapshot(empty), indent=2),
            encoding="utf-8",
        )
        temp.replace(path)
        return self.context.DEFAULT_SETUP_NAME

    def remember_setup(self, campaign: str, name: str) -> None:
        """Record the battle setup most recently worked on (saved/loaded) in a campaign."""
        data = self.context.read_campaigns()
        meta = data['campaigns'].get(campaign)
        if meta is None:
            return
        meta['last_setup'] = name
        meta['last_setup_at'] = self.context.now_iso()
        self.context.write_campaigns(data)

    def pick_campaign_setup(self, campaign: str) -> str | None:
        'Setup to open when a campaign is activated.\n\n    1. the most recently worked on setup recorded in campaigns.json (if it still exists);\n    2. otherwise the setup file modified most recently;\n    3. None when the campaign has no setups.\n    '
        directory = self.context.campaign_dir(campaign)
        last = self.context.read_campaigns()['campaigns'].get(campaign, {}).get('last_setup')
        if isinstance(last, str) and (directory / f'{last}.json').exists():
            return last
        files = sorted(directory.glob('*.json'), key=lambda p: (-p.stat().st_mtime, p.stem.casefold()))
        return files[0].stem if files else None

    async def open_campaign_setup(self, campaign: str) -> str | None:
        """Load the campaign's most recent (or first) setup into the live battle state."""
    
        name = self.context.pick_campaign_setup(campaign)
        if name is None:
            return None
        path = self.context.campaign_dir(campaign) / f'{name}.json'
        try:
            self.context.STATE = self.context.load_setup_state(name, campaign)
        except self.context.HTTPException as exc:
            raise self.context.HTTPException(
                exc.status_code,
                f"Campaign activated, but setup {name} could not be opened: {exc.detail}",
            ) from exc
        self.context.set_active_setup(campaign, name)
        self.context.remember_setup(campaign, name)
        await self.context.changed()
        return name

    def campaigns_payload(self, moved: list[str] | None=None) -> dict[str, Any]:
        """Campaigns payload."""
        data = self.context.read_campaigns()
        items = []
        for slug, meta in data['campaigns'].items():
            setups = sorted((p.stem for p in self.context.campaign_dir(slug).glob('*.json')), key=str.casefold)
            items.append({
                'slug': slug,
                'name': meta.get('name', slug),
                'description': meta.get('description', ''),
                'created': meta.get('created'),
                'setups': setups,
                'last_setup': meta.get('last_setup') if meta.get('last_setup') in setups else None,
            })
        items.sort(key=lambda x: str(x['name']).casefold())
        return {'active': data['active'], 'campaigns': items, 'moved': moved or []}
