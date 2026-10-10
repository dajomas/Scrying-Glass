"""Campaigns services using the live server context."""

from __future__ import annotations
from typing import Any, Literal
from pathlib import Path


class CampaignsService:
    """Group campaigns operations without owning a separate copy of runtime state."""

    def __init__(self, context: Any) -> None:
        """Retain the live server context."""
        self.context = context





    def list_setups(self, campaign: str | None = None) -> list[str]:
        return self.context.STORAGE.list_setups(self.context.require_campaign(campaign))



    def read_campaigns(self) -> dict[str, Any]:
        return self.context.STORAGE.read_campaigns()

    def write_campaigns(self, data: dict[str, Any]) -> None:
        self.context.STORAGE.write_campaigns(data)

    def active_campaign(self) -> str:
        value = self.context.STORAGE.get_value("active_campaign")
        if value is None:
            raise self.context.HTTPException(404, "No active campaign")
        return str(value)

    def require_campaign(self, campaign: str | None) -> str:
        value = self.context.active_campaign() if campaign is None or not str(campaign).strip() else str(campaign).strip()
        if not value.isascii() or not value.isdecimal():
            raise self.context.HTTPException(404, f"Invalid campaign ID: {value}")
        ident = value.lstrip("0") or "0"
        maximum = "9223372036854775807"
        if ident == "0" or len(ident) > len(maximum) or (
            len(ident) == len(maximum) and ident > maximum
        ):
            raise self.context.HTTPException(404, "Campaign ID is outside the supported range")
        if not self.context.STORAGE.campaign_exists(ident):
            raise self.context.HTTPException(404, f"Campaign not found: {ident}")
        return ident

    def create_default_setup(self, campaign_id: str) -> str | None:
        name = self.context.DEFAULT_SETUP_NAME
        if self.context.STORAGE.setup_exists(campaign_id, name):
            return None
        empty = self.context.normalize_state({"display": {"background": self.context.configured_background()}})
        self.context.STORAGE.save_setup(campaign_id, name, self.context.setup_snapshot(empty))
        return name

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
        last = self.context.read_campaigns()["campaigns"].get(campaign, {}).get("last_setup")
        if isinstance(last, str) and self.context.STORAGE.setup_exists(campaign, last):
            return last
        return self.context.STORAGE.newest_setup(campaign)

    async def open_campaign_setup(self, campaign: str) -> str | None:
        """Load the campaign's most recent (or first) setup into the live battle state."""
    
        name = self.context.pick_campaign_setup(campaign)
        if name is None:
            return None
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
        for campaign_id, meta in data['campaigns'].items():
            setups = self.context.STORAGE.list_setups(campaign_id)
            items.append({
                'id': campaign_id,
                'name': meta.get('name', campaign_id),
                'description': meta.get('description', ''),
                'created': meta.get('created'),
                'setups': setups,
                'last_setup': meta.get('last_setup') if meta.get('last_setup') in setups else None,
            })
        items.sort(key=lambda x: str(x['name']).casefold())
        return {'active': data['active'], 'campaigns': items, 'moved': moved or []}
