"""Admin campaigns endpoint handlers; route registration stays in AdminAPI."""

from __future__ import annotations
from typing import Any

class AdminCampaignsMixin:
    """Implement admin campaigns handlers using the shared server context."""

    async def get_campaigns(self):
        """Get campaigns."""
        moved = self.context.migrate_unassigned_setups()
        return self.context.campaigns_payload(moved)

    async def create_campaign(self, payload: CampaignCreate):
        name = payload.name.strip()
        if not name:
            raise self.context.HTTPException(400, "Campaign name is required")
        if self.context.STORAGE.campaign_name_exists(name):
            raise self.context.HTTPException(409, "Campaign name already exists")
        ident = self.context.STORAGE.create_campaign(name, payload.description.strip(), self.context.now_iso())
        self.context.create_default_setup(ident)
        self.context.save_campaign_characters(ident, [])
        if payload.activate:
            self.context.STORAGE.set_value("active_campaign", ident)
        opened = await self.context.open_campaign_setup(ident) if payload.activate else None
        return {**self.context.campaigns_payload(), "created_campaign_id": ident, "opened_setup": opened}

    async def update_campaign(self, campaign_id: str, payload: CampaignUpdate):
        ident = self.context.require_campaign(campaign_id)
        name = payload.name.strip() if payload.name is not None else None
        description = payload.description.strip() if payload.description is not None else None
        if name is not None:
            if not name:
                raise self.context.HTTPException(400, "Campaign name is required")
            if self.context.STORAGE.campaign_name_exists(name, exclude=ident):
                raise self.context.HTTPException(409, "Campaign name already exists")
        self.context.STORAGE.update_campaign(ident, name=name, description=description)
        return self.context.campaigns_payload()

    async def delete_campaign(self, campaign_id: str, move_to: str | None=None, delete_setups: bool=False):
        """Delete campaign."""
        self.context.migrate_unassigned_setups()
        campaign_id = self.context.require_campaign(campaign_id)
        data = self.context.read_campaigns()
        if len(data['campaigns']) <= 1:
            raise self.context.HTTPException(400, 'The last remaining campaign cannot be deleted')
        setups = self.context.STORAGE.list_setups(campaign_id)
        target_id = None
        if move_to and delete_setups:
            raise self.context.HTTPException(400, 'Choose either move_to or delete_setups, not both')
        if move_to:
            target_id = self.context.require_campaign(move_to)
            if target_id == campaign_id:
                raise self.context.HTTPException(400, 'Cannot move setups into the campaign being deleted')
        if setups and target_id is None and not delete_setups:
            raise self.context.HTTPException(409, f'Campaign still contains {len(setups)} setup(s); choose a campaign to move them to, or delete them')

        reactivated = data["active"] == campaign_id
        replacement_id = None
        replacement_name = None
        replacement_state = None

        if reactivated:
            replacement_id = target_id or sorted(
                campaign
                for campaign in data["campaigns"]
                if campaign != campaign_id
            )[0]

            replacement_name = self.context.pick_campaign_setup(
                replacement_id
            )

            if replacement_name is None:
                raise self.context.HTTPException(
                    409,
                    "The replacement campaign has no setup. "
                    "Create a setup there before deleting the active campaign.",
                )

            replacement_state = self.context.load_setup_state(
                replacement_name,
                replacement_id,
            )

        deleted_setups = list(setups) if delete_setups else []
        moved = []
        if target_id is not None:
            for name in setups:
                moved.append(self.context.STORAGE.transfer_setup(campaign_id, target_id, name, "move"))
        reference = self.context.active_setup_reference()

        if reference is not None and reference["campaign_id"] == campaign_id:
            self.context.clear_active_setup()


        del data["campaigns"][campaign_id]

        if reactivated:
            data["active"] = replacement_id

        self.context.write_campaigns(data)

        opened = None

        if reactivated:
            self.context.STATE = replacement_state
            self.context.set_active_setup(
                replacement_id,
                replacement_name,
            )
            self.context.remember_setup(
                replacement_id,
                replacement_name,
            )
            opened = replacement_name

        await self.context.changed()
        return {**self.context.campaigns_payload(), 'moved': moved, 'deleted_setups': deleted_setups, 'opened_setup': opened}

    async def activate_campaign(self, campaign_id: str):
        """Validate the destination before changing the active campaign."""
        self.context.migrate_unassigned_setups()
        campaign_id = self.context.require_campaign(campaign_id)

        name = self.context.pick_campaign_setup(campaign_id)

        if name is None:
            next_state = self.context.normalize_state({
                "monsters": [],
                "characters": self.context.load_campaign_characters(campaign_id),
                "battle_order": [],
                "activity_log": [],
                "display": {
                    "background": self.context.configured_background(),
                },
            })
        else:
            next_state = self.context.load_setup_state(name, campaign_id)

        data = self.context.read_campaigns()
        data["active"] = campaign_id
        self.context.write_campaigns(data)

        self.context.STATE = next_state

        if name is None:
            self.context.clear_active_setup()
        else:
            self.context.set_active_setup(campaign_id, name)
            self.context.remember_setup(campaign_id, name)

        await self.context.changed()

        return {
            **self.context.campaigns_payload(),
            "opened_setup": name,
        }

    async def add_setup_to_campaign(self, campaign_id: str, payload: CampaignSetupAdd):
        """Add setup to campaign."""
        self.context.migrate_unassigned_setups()
        target_id = self.context.require_campaign(campaign_id)
        source_id = self.context.require_campaign(payload.from_campaign)
        name = self.context.setup_slug(payload.setup)
        if not self.context.STORAGE.setup_exists(source_id, name):
            raise self.context.HTTPException(404, 'Saved setup not found')
        if source_id == target_id:
            raise self.context.HTTPException(400, 'Setup is already in this campaign')
        reference = self.context.active_setup_reference()
        moving_loaded_setup = (
            payload.mode == "move"
            and reference is not None
            and reference["campaign_id"] == source_id
            and reference["name"] == name
        )

        destination = self.context.STORAGE.transfer_setup(source_id, target_id, name, payload.mode)
        if moving_loaded_setup:
            self.context.clear_active_setup()
            await self.context.changed()
        return {**self.context.campaigns_payload(), 'setup': destination, 'campaign': target_id, 'mode': payload.mode}
