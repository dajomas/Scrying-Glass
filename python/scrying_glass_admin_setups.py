"""Admin setups endpoint handlers; route registration stays in AdminAPI."""

from __future__ import annotations
from typing import Any
from fastapi import File, Form

class AdminSetupsMixin:
    """Implement admin setups handlers using the shared server context."""

    async def get_setups(self, campaign: str | None=None):
        """Get setups."""
        self.context.migrate_unassigned_setups()
        slug = self.context.require_campaign(campaign)
        return {'campaign': slug, 'names': self.context.list_setups(slug)}

    async def new_setup(self):
        """New setup."""
    

        campaign = self.context.require_campaign(None)

        self.context.STATE = self.context.normalize_state({
            "monsters": [],
            "characters": self.context.load_campaign_characters(campaign),
            "battle_order": [],
            "activity_log": [],
            "display": {
                "background": self.context.configured_background(),
            },
        })

        self.context.clear_active_setup()

        await self.context.changed()

        return self.context.public_state()

    async def save_setup(self, payload: SetupName):
        """Save setup."""
        name = self.context.setup_slug(payload.name)
        campaign = self.context.require_campaign(payload.campaign)
        if campaign != self.context.active_campaign():
            raise self.context.HTTPException(
                409,
                "Activate this campaign before saving, loading, or deleting its setup",
            )
        path = self.context.setup_path(name, campaign)

        temp = path.with_suffix(".tmp")
        temp.write_text(
            self.context.json.dumps(self.context.setup_snapshot(self.context.STATE), indent=2),
            encoding="utf-8",
        )
        temp.replace(path)

        # Characters are campaign-owned, so save their current state separately.
        self.context.save_campaign_characters(campaign, self.context.STATE["characters"])

        self.context.set_active_setup(campaign, name)
        self.context.remember_setup(campaign, name)

        await self.context.changed()

        return {
            "name": name,
            "campaign": campaign,
        }

    async def load_setup(self, payload: SetupName):
        """Load setup."""
    
        name = self.context.setup_slug(payload.name)
        campaign = self.context.require_campaign(payload.campaign)
        if campaign != self.context.active_campaign():
            raise self.context.HTTPException(
                409,
                "Activate this campaign before saving, loading, or deleting its setup",
            )
        self.context.STATE = self.context.load_setup_state(name, campaign)
        self.context.set_active_setup(campaign, name)
        self.context.remember_setup(campaign, name)
        await self.context.changed()
        return {'name': name, 'campaign': campaign}

    async def rename_setup(self, payload: SetupRename):
        """Rename setup."""
        campaign = self.context.require_campaign(payload.campaign)
        old = self.context.setup_slug(payload.name)
        new = self.context.setup_slug(payload.new_name)

        src = self.context.setup_path(old, campaign)

        if not src.exists():
            raise self.context.HTTPException(404, "Saved setup not found")

        if new == old:
            return {
                "name": new,
                "old_name": old,
                "campaign": campaign,
            }

        dst = self.context.setup_path(new, campaign)

        if dst.exists():
            raise self.context.HTTPException(
                409,
                f"A battle setup called {new} already exists in this campaign",
            )

        src.rename(dst)

        data = self.context.read_campaigns()
        meta = data["campaigns"].get(campaign)

        if meta is not None and meta.get("last_setup") == old:
            meta["last_setup"] = new

        self.context.write_campaigns(data)

        reference = self.context.active_setup_reference()

        if (
            reference is not None
            and reference["campaign"] == campaign
            and reference["name"] == old
        ):
            self.context.set_active_setup(campaign, new)
            await self.context.changed()

        return {
            "name": new,
            "old_name": old,
            "campaign": campaign,
        }

    async def delete_setup(self, name: str, campaign: str | None=None):
        """Delete a battle setup, then open the next one in the campaign.

        "Next" is the setup that follows the deleted one alphabetically (wrapping
        around to the first). When the campaign has no setups left, an empty
        "Default" setup is created and opened.
        """
    
        campaign = self.context.require_campaign(campaign)
        if campaign != self.context.active_campaign():
            raise self.context.HTTPException(
                409,
                "Activate this campaign before saving, loading, or deleting its setup",
            )
        name = self.context.setup_slug(name)
        path = self.context.setup_path(name, campaign)
        if not path.exists():
            raise self.context.HTTPException(404, 'Saved setup not found')
        reference = self.context.active_setup_reference()

        if (
            reference is not None
            and reference["campaign"] == campaign
            and reference["name"] == name
        ):
            self.context.clear_active_setup()

        path.unlink()
        remaining = self.context.list_setups(campaign)
        created_default = False
        if remaining:
            following = [x for x in remaining if x.casefold() > name.casefold()]
            next_name = following[0] if following else remaining[0]
        else:
            self.context.create_default_setup(campaign)
            next_name = self.context.DEFAULT_SETUP_NAME
            created_default = True
        try:
            self.context.STATE = self.context.load_setup_state(next_name, campaign)
        except self.context.HTTPException as exc:
            raise self.context.HTTPException(
                exc.status_code,
                f"Setup {name} was deleted, but {next_name} could not be opened: "
                f"{exc.detail}",
            ) from exc
        self.context.set_active_setup(campaign, next_name)
        self.context.remember_setup(campaign, next_name)
        await self.context.changed()
        return {'deleted': name, 'opened_setup': next_name, 'created_default': created_default, 'campaign': campaign}

    async def import_setup(self, payload: SetupImport):
        """Import setup."""
        name = self.context.setup_slug(payload.name)
        campaign = self.context.require_campaign(payload.campaign)

        if payload.kind != "monsters":
            raise self.context.HTTPException(
                400,
                "Characters belong to campaigns and cannot be imported "
                "from a battle setup",
            )

        source = self.context.load_setup_state(name, campaign)

        imported_monsters = [
            self.context.reset_imported_monster(item)
            for item in source["monsters"]
        ]

        self.context.STATE["monsters"].extend(imported_monsters)

        await self.context.combatants_changed(monsters=True, characters=False)

        return {
            "name": name,
            "campaign": campaign,
            "monsters": len(imported_monsters),
        }
