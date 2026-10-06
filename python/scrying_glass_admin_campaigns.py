"""Admin campaigns endpoint handlers; route registration stays in AdminAPI."""

from __future__ import annotations
from typing import Any
from fastapi import File, Form

class AdminCampaignsMixin:
    """Implement admin campaigns handlers using the shared server context."""

    async def get_campaigns(self):
        """Get campaigns."""
        moved = self.context.migrate_unassigned_setups()
        return self.context.campaigns_payload(moved)

    async def create_campaign(self, payload: CampaignCreate):
        """Create campaign."""
        self.context.migrate_unassigned_setups()
        slug = self.context.campaign_slug(payload.name)
        data = self.context.read_campaigns()
        if slug in data['campaigns'] or self.context.campaign_dir(slug).exists():
            raise self.context.HTTPException(409, f'Campaign already exists: {slug}')
    
        self.context.campaign_dir(slug).mkdir(parents=True, exist_ok=False)
        self.context.create_default_setup(slug)
        self.context.save_campaign_characters(slug, [])

        data["campaigns"][slug] = {
            'name': payload.name.strip(),
            'description': payload.description.strip(),
            'created': self.context.now_iso(),
        }
        if payload.activate:
            data['active'] = slug
        self.context.write_campaigns(data)
        opened = await self.context.open_campaign_setup(slug) if payload.activate else None
        return {**self.context.campaigns_payload(), 'opened_setup': opened}

    async def update_campaign(self, slug: str, payload: CampaignUpdate):
        """Update campaign."""
        self.context.migrate_unassigned_setups()
        slug = self.context.require_campaign(slug)
        data = self.context.read_campaigns()
        meta = data['campaigns'][slug]
        if payload.description is not None:
            meta['description'] = payload.description.strip()
        if payload.name is not None:
            new_slug = self.context.campaign_slug(payload.name)
            if new_slug != slug:
                if new_slug in data['campaigns'] or self.context.campaign_dir(new_slug).exists():
                    raise self.context.HTTPException(409, f'Campaign already exists: {new_slug}')
                self.context.campaign_dir(slug).rename(self.context.campaign_dir(new_slug))
                old_characters_path = self.context.campaign_characters_path(slug)
                new_characters_path = self.context.campaign_characters_path(new_slug)
                if old_characters_path.exists():
                    old_characters_path.rename(new_characters_path)
                else:
                    self.context.save_campaign_characters(new_slug, [])
                data["campaigns"][new_slug] = data["campaigns"].pop(slug)
                if data['active'] == slug:
                    data['active'] = new_slug
                meta = data['campaigns'][new_slug]
            meta['name'] = payload.name.strip()
        self.context.write_campaigns(data)
        if payload.name is not None and new_slug != slug:
            reference = self.context.active_setup_reference()
            if reference is not None and reference["campaign"] == slug:
                self.context.set_active_setup(new_slug, reference["name"])
        await self.context.changed()
        return self.context.campaigns_payload()

    async def delete_campaign(self, slug: str, move_to: str | None=None, delete_setups: bool=False):
        """Delete campaign."""
        self.context.migrate_unassigned_setups()
        slug = self.context.require_campaign(slug)
        data = self.context.read_campaigns()
        if len(data['campaigns']) <= 1:
            raise self.context.HTTPException(400, 'The last remaining campaign cannot be deleted')
        source = self.context.campaign_dir(slug)
        setups = sorted(source.glob('*.json'))
        target_slug = None
        if move_to and delete_setups:
            raise self.context.HTTPException(400, 'Choose either move_to or delete_setups, not both')
        if move_to:
            target_slug = self.context.require_campaign(move_to)
            if target_slug == slug:
                raise self.context.HTTPException(400, 'Cannot move setups into the campaign being deleted')
        if setups and target_slug is None and not delete_setups:
            raise self.context.HTTPException(409, f'Campaign still contains {len(setups)} setup(s); choose a campaign to move them to, or delete them')

        reactivated = data["active"] == slug
        replacement_slug = None
        replacement_name = None
        replacement_state = None

        if reactivated:
            replacement_slug = target_slug or sorted(
                campaign
                for campaign in data["campaigns"]
                if campaign != slug
            )[0]

            replacement_name = self.context.pick_campaign_setup(
                replacement_slug
            )

            if replacement_name is None:
                raise self.context.HTTPException(
                    409,
                    "The replacement campaign has no setup. "
                    "Create a setup there before deleting the active campaign.",
                )

            replacement_state = self.context.load_setup_state(
                replacement_name,
                replacement_slug,
            )

        deleted_setups = [src.stem for src in setups] if delete_setups else []
        moved = []
        if target_slug is not None:
            for src in setups:
                dst = self.context.unique_setup_path(self.context.campaign_dir(target_slug), src.stem)
                src.replace(dst)
                moved.append(dst.stem)
        reference = self.context.active_setup_reference()

        if reference is not None and reference["campaign"] == slug:
            self.context.clear_active_setup()

        self.context.shutil.rmtree(source, ignore_errors=True)
        self.context.campaign_characters_path(slug).unlink(missing_ok=True)

        del data["campaigns"][slug]

        if reactivated:
            data["active"] = replacement_slug

        self.context.write_campaigns(data)

        opened = None

        if reactivated:
            self.context.STATE = replacement_state
            self.context.set_active_setup(
                replacement_slug,
                replacement_name,
            )
            self.context.remember_setup(
                replacement_slug,
                replacement_name,
            )
            opened = replacement_name

        await self.context.changed()
        return {**self.context.campaigns_payload(), 'moved': moved, 'deleted_setups': deleted_setups, 'opened_setup': opened}

    async def activate_campaign(self, slug: str):
        """Validate the destination before changing the active campaign."""
        self.context.migrate_unassigned_setups()
        slug = self.context.require_campaign(slug)

        name = self.context.pick_campaign_setup(slug)

        if name is None:
            next_state = self.context.normalize_state({
                "monsters": [],
                "characters": self.context.load_campaign_characters(slug),
                "battle_order": [],
                "activity_log": [],
                "display": {
                    "background": self.context.configured_background(),
                },
            })
        else:
            next_state = self.context.load_setup_state(name, slug)

        data = self.context.read_campaigns()
        data["active"] = slug
        self.context.write_campaigns(data)

        self.context.STATE = next_state

        if name is None:
            self.context.clear_active_setup()
        else:
            self.context.set_active_setup(slug, name)
            self.context.remember_setup(slug, name)

        await self.context.changed()

        return {
            **self.context.campaigns_payload(),
            "opened_setup": name,
        }

    async def add_setup_to_campaign(self, slug: str, payload: CampaignSetupAdd):
        """Add setup to campaign."""
        self.context.migrate_unassigned_setups()
        target_slug = self.context.require_campaign(slug)
        source_slug = self.context.require_campaign(payload.from_campaign)
        src = self.context.setup_path(payload.setup, source_slug)
        if not src.exists():
            raise self.context.HTTPException(404, 'Saved setup not found')
        if source_slug == target_slug:
            raise self.context.HTTPException(400, 'Setup is already in this campaign')
        dst = self.context.unique_setup_path(self.context.campaign_dir(target_slug), src.stem)
        reference = self.context.active_setup_reference()
        moving_loaded_setup = (
            payload.mode == "move"
            and reference is not None
            and reference["campaign"] == source_slug
            and reference["name"] == src.stem
        )

        if payload.mode == "copy":
            self.context.shutil.copy2(src, dst)
        else:
            src.replace(dst)

            if moving_loaded_setup:
                self.context.clear_active_setup()
                await self.context.changed()
        return {**self.context.campaigns_payload(), 'setup': dst.stem, 'campaign': target_slug, 'mode': payload.mode}
