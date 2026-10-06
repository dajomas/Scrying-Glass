"""Optional extracted admin/client endpoints for Scrying Glass."""
from __future__ import annotations
from typing import Any, get_type_hints
from fastapi import Depends, FastAPI, File, Form

class AdminAPI:
    """Own admin endpoints; access live state through the supplied server context."""

    def __init__(self, context: Any, app: FastAPI) -> None:
        """Bind handlers, resolve request types, and register routes on the application."""
        self.context = context
        self.app = app
        self.register_routes()

    def register_routes(self) -> None:
        """Register bound methods while preserving authentication and route metadata."""
        handler = self.admin_login_get
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/login', handler, methods=['GET'])
        handler = self.admin_login_post
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/login', handler, methods=['POST'])
        handler = self.admin_home
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/', handler, methods=['GET'])
        handler = self.admin_get_state
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/state', handler, methods=['GET'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.dndbeyond_monster_stats
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/dndbeyond/monster-stats', handler, methods=['GET'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.update_display_background
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/display/background', handler, methods=['PATCH'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.upload_display_background_image
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/display/background-image', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.get_setups
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/setups', handler, methods=['GET'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.get_campaigns
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/campaigns', handler, methods=['GET'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.create_campaign
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/campaigns', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.update_campaign
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/campaigns/{slug}', handler, methods=['PATCH'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.delete_campaign
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/campaigns/{slug}', handler, methods=['DELETE'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.activate_campaign
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/campaigns/{slug}/activate', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.add_setup_to_campaign
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/campaigns/{slug}/setups', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.new_setup
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/setups/new', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.save_setup
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/setups/save', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.load_setup
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/setups/load', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.rename_setup
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/setups/rename', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.delete_setup
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/setups/{name}', handler, methods=['DELETE'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.import_setup
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/setups/import', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.roll_monster_initiative
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/monsters/roll-initiative', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.create_monster
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/monsters', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.import_monster
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/monsters/import', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.import_monsters_csv
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/monsters/import-csv', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.import_characters_csv
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/characters/import-csv', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.edit_monster
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/monsters/{ident}/edit', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.update_monster
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/monsters/{ident}', handler, methods=['PATCH'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.create_character
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/characters', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.update_character
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/characters/{ident}', handler, methods=['PATCH'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.delete_combatant
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/combatants/{ident}', handler, methods=['DELETE'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.reset_one_combatant
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/combatants/{ident}/reset', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.bulk_characters
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/characters/bulk', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.bulk_monsters
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/monsters/bulk', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.battle_end
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/battle/end', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.reset_all
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/battle/reset-all', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.battle_start
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/battle/start', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.battle_next
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/battle/next', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.apply_battle_actions
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/battle/actions', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.export_activity_log_json
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/activity-log.json', handler, methods=['GET'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.export_activity_log_csv
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/activity-log.csv', handler, methods=['GET'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])
        handler = self.clear_activity_log
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/api/activity-log/clear', handler, methods=['POST'], dependencies=[Depends(self.context.require('admin', self.context.ADMIN_SESSION_COOKIE))])

    # ============================================================================
    # Login and HTML pages
    # ============================================================================


    def admin_login_get(self):
        """Admin login get."""
        return self.context.login()

    def admin_login_post(self, username: str=Form(...), password: str=Form(...)):
        """Admin login post."""
        u = self.context.user(username)
        if not u or u.get('role') != 'admin' or (not self.context.password_ok(password, str(u.get('password', '')))):
            return self.context.login('Invalid admin credentials')
        token = self.context.secrets.token_urlsafe(32)
        self.context.SESSIONS[token] = {'username': username, 'role': 'admin'}
        r = self.context.RedirectResponse('/', 303)
        r.set_cookie(self.context.ADMIN_SESSION_COOKIE, token, httponly=True, samesite='lax', secure=False)
        for legacy in self.context.LEGACY_SESSION_COOKIES:
            r.delete_cookie(legacy)
        return r

    def admin_home(self, request: FastAPIRequest):
        """Admin home."""
        return self.context.HTMLResponse(self.context.ADMIN_HTML) if self.context.SESSIONS.get(request.cookies.get(self.context.ADMIN_SESSION_COOKIE, ''), {}).get('role') == 'admin' else self.context.RedirectResponse('/login', 303)

    # ============================================================================
    # State and live updates
    # ============================================================================


    def admin_get_state(self):
        """Admin get state."""
        return self.context.public_state()

    # ============================================================================
    # Display and optional D&D Beyond lookup
    # ============================================================================


    async def dndbeyond_monster_stats(self, species: str) -> dict[str, Any]:
        """
        Return non-persistent AC and HP suggestions for a canonical species name.

        The lookup is optional and must never mutate STATE or prevent manual
        monster creation.
        """
        monster_species = species.strip()

        if not monster_species:
            raise self.context.HTTPException(400, "Monster species is required")

        if not self.context.CONFIG["display"].get("dndbeyond_image_lookup", True):
            return {
                "found": False,
                "reason": "D&D Beyond lookup is disabled",
            }

        try:
            candidates = self.context.dnd_monster_candidates(monster_species)

            for is_legacy, href in candidates:
                monster_html = self.context.dnd_monster_detail_html(href)
                ac, hp, hp_source = self.context.dnd_monster_stats_from_html(
                    monster_html
                )

                if ac is None and hp is None:
                    continue

                return {
                    "found": True,
                    "species": monster_species,
                    "ac": ac,
                    "hp": hp,
                    "hp_source": hp_source,
                    "legacy": is_legacy,
                    "source_url": f"https://www.dndbeyond.com{href}",
                }

            return {
                "found": False,
                "species": monster_species,
            }

        except Exception:
            # This endpoint is convenience-only. Do not expose remote errors or
            # make a temporary D&D Beyond failure look like a local server failure.
            return {
                "found": False,
                "species": monster_species,
            }

    async def update_display_background(self, payload: DisplayBackgroundUpdate) -> dict[str, Any]:
        """Update display background."""
        background = payload.background.strip()

        if not background:
            raise self.context.HTTPException(400, 'Background is required')

        self.context.STATE['display']['background'] = background
        await self.context.changed()
        return self.context.public_state()

    async def upload_display_background_image(self, image: UploadFile=File(...)) -> dict[str, Any]:
        """Upload display background image."""
        image_url = self.context.save_image(image)
        self.context.STATE['display']['background'] = f'url("{image_url}")'
        await self.context.changed()

        return {
            'background': self.context.STATE['display']['background'],
            'image_url': image_url,
        }

    # ============================================================================
    # Battle setup management
    # ============================================================================


    async def get_setups(self, campaign: str | None=None):
        """Get setups."""
        self.context.migrate_unassigned_setups()
        slug = self.context.require_campaign(campaign)
        return {'campaign': slug, 'names': self.context.list_setups(slug)}

    async def new_setup(self):
        """New setup."""
    

        campaign = self.context.require_campaign(None)

        STATE = self.context.normalize_state({
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
        STATE = self.context.load_setup_state(name, campaign)
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
            STATE = self.context.load_setup_state(next_name, campaign)
        except self.context.HTTPException as exc:
            raise self.context.HTTPException(
                exc.status_code,
                f"Setup {name} was deleted, but {next_name} could not be opened: "
                f"{exc.detail}",
            ) from exc
        self.context.set_active_setup(campaign, name)
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

    # ============================================================================
    # Campaign management
    # ============================================================================


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
        reactivated = data['active'] == slug
        if reactivated:
            data['active'] = target_slug or sorted(data['campaigns'], key=str.casefold)[0]
        self.context.write_campaigns(data)
        opened = await self.context.open_campaign_setup(data['active']) if reactivated else None
        return {**self.context.campaigns_payload(), 'moved': moved, 'deleted_setups': deleted_setups, 'opened_setup': opened}

    async def activate_campaign(self, slug: str):
        """Activate campaign."""
        self.context.migrate_unassigned_setups()
        slug = self.context.require_campaign(slug)
        data = self.context.read_campaigns()
        data['active'] = slug
        self.context.write_campaigns(data)
        opened = await self.context.open_campaign_setup(slug)
        return {**self.context.campaigns_payload(), 'opened_setup': opened}

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
        if payload.mode == 'copy':
            self.context.shutil.copy2(src, dst)
        else:
            src.replace(dst)
        return {**self.context.campaigns_payload(), 'setup': dst.stem, 'campaign': target_slug, 'mode': payload.mode}

    # ============================================================================
    # Monster management
    # ============================================================================


    async def roll_monster_initiative(self):
        """Roll monster initiative."""
        for monster in self.context.STATE['monsters']:
            monster['initiative'] = self.context.random.randint(1, 20)
        await self.context.combatants_changed(monsters=True, characters=False)
        return {'count': len(self.context.STATE['monsters'])}

    async def create_monster(self, name: str=Form(...), monster_species: str=Form(...), ac: int=Form(...), hprangestart: str=Form(...), hprangeend: str=Form(''), color: str=Form(...), quantity: int=Form(1, ge=1, le=50), image: UploadFile | None=File(None)) -> list[dict[str, Any]]:
        """Create monster."""
        next_hp = self.context.hp_value_factory(hprangestart, hprangeend)

        fields = {
            "name": name.strip(),
            "monster_species": monster_species.strip(),
            "ac": ac,
        }
        image_url = (
            self.context.save_image(image)
            if image is not None and image.filename
            else self.context.dnd_image(fields["monster_species"])
        )

        created = []

        for number in range(1, quantity + 1):
            generated_name = (
                fields["name"]
                if quantity == 1
                else f"{fields['name']} - {number}"
            )
            rolled_hp = next_hp()

            created.append(
                self.context.make_monster(
                    {
                        **fields,
                        "name": generated_name,
                        "hp": rolled_hp,
                    },
                    color,
                    None,
                    image_url,
                )
            )

        self.context.STATE["monsters"].extend(created)
        await self.context.combatants_changed(monsters=True, characters=False)
        return created

    async def import_monster(self, monster_file: UploadFile=File(...), color: str=Form(...), quantity: int=Form(1, ge=1, le=50), image: UploadFile | None=File(None)):
        """Import monster."""
        if not (monster_file.filename or '').lower().endswith('.monster'):
            raise self.context.HTTPException(400, 'Upload a .monster file')
        fields = self.context.parse_monster(await monster_file.read())
        image_url = (
            self.context.save_image(image)
            if image and image.filename
            else self.context.dnd_image(fields['monster_species'])
        )

        created = self.context.make_monsters(fields, color, quantity, image_url)

        self.context.STATE['monsters'].extend(created)
        await self.context.combatants_changed(monsters=True, characters=False)
        return created

    async def import_monsters_csv(self, csv_file: UploadFile=File(...)) -> dict[str, int]:
        """Import monsters csv."""
        if not (csv_file.filename or "").lower().endswith(".csv"):
            raise self.context.HTTPException(400, "Upload a .csv file")

        rows = self.context.csv_rows(await csv_file.read())
        imported = [
            self.context.csv_monster(row, row_number)
            for row_number, row in enumerate(rows, start=2)
        ]

        ids = [monster["id"] for monster in imported]
        existing_ids = {monster["id"] for monster in self.context.STATE["monsters"]}
        existing_ids.update(character["id"] for character in self.context.STATE["characters"])

        if len(ids) != len(set(ids)):
            raise self.context.HTTPException(400, "CSV contains duplicate IDs")

        conflicting = set(ids) & existing_ids
        if conflicting:
            raise self.context.HTTPException(
                400,
                "CSV ID already exists in the current setup: "
                + ", ".join(sorted(conflicting)[:5]),
            )

        self.context.STATE["monsters"].extend(imported)
        await self.context.combatants_changed(monsters=True, characters=False)

        return {"count": len(imported)}

    async def edit_monster(self, ident: str, name: str=Form(...), monster_species: str=Form(...), ac: int=Form(...), hp: int=Form(...), max_hp: int=Form(...), original_hp: int=Form(...), color: str=Form(...), initiative: str=Form(''), ally: str=Form('false'), image: UploadFile | None=File(None)):
        """Edit monster."""
        m = next((x for x in self.context.STATE['monsters'] if x['id'] == ident), None)
        if not m:
            raise self.context.HTTPException(404, 'Monster not found')
        parsed_initiative = None if initiative.strip() == '' else int(initiative)
        if parsed_initiative is not None and (not -100 <= parsed_initiative <= 100):
            raise self.context.HTTPException(400, 'Initiative must be between -100 and 100')
        m.update({'name': name.strip(), 'monster_species': monster_species.strip(), 'ac': ac, 'hp': hp, 'max_hp': max_hp, 'original_hp': original_hp, 'color': color, 'initiative': parsed_initiative, 'ally': ally.lower() == 'true'})
        if image and image.filename:
            m['image_url'] = self.context.save_image(image)
        if m['hp'] <= 0:
            m['alive'] = False
            m['visible'] = True
            m['in_turn'] = False
        self.context.clean_order()
        await self.context.combatants_changed(monsters=True, characters=False)
        return m

    async def update_monster(self, ident: str, update: MonsterUpdate) -> dict[str, Any]:
        """Update monster."""
        monster = next(
            (item for item in self.context.STATE["monsters"] if item["id"] == ident),
            None,
        )

        if not monster:
            raise self.context.HTTPException(404, "Monster not found")

        values = update.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        hp_delta = values.pop("hp_delta", None)

        for key, value in values.items():
            if key != "in_turn":
                monster[key] = value

        if hp_delta is not None:
            monster["hp"] += hp_delta

        if monster["hp"] <= 0:
            monster["alive"] = False
            monster["visible"] = True
            monster["in_turn"] = False
        else:
            monster["alive"] = True

        if hp_delta is not None:
            self.context.log_hp_change(monster, hp_delta)

        if values.get("active") is True:
            self.context.insert_into_battle_order(monster)

        if values.get("active") is False:
            monster["in_turn"] = False

        self.context.set_turn(monster, values.get("in_turn"))
        self.context.clean_order()

        await self.context.combatants_changed(monsters=True, characters=False)
        return monster

    async def bulk_monsters(self, body: BulkCombatantAction) -> dict[str, int]:
        """Apply one validated bulk action to selected monsters."""
        fields = {
            "join-battle": ("active", True),
            "leave-battle": ("active", False),
            "set-ally": ("ally", True),
            "unset-ally": ("ally", False),
            "show-ac": ("show_ac", True),
            "hide-ac": ("show_ac", False),
            "show-hp": ("show_hp", True),
            "hide-hp": ("show_hp", False),
            "show-initiative": ("show_initiative", True),
            "hide-initiative": ("show_initiative", False),
        }
        allowed = {*fields, "reset", "remove"}

        if body.action not in allowed:
            raise self.context.HTTPException(400, "Unsupported bulk monster action")

        targets = self.context.selected_entities("monsters", body.ids)

        if body.action in fields:
            field, value = fields[body.action]

            if body.action == "join-battle":
                for monster in targets:
                    # Prefer the existing activation helper where available.
                    monster[field] = value
            elif body.action == "leave-battle":
                removed_ids = {monster["id"] for monster in targets}
                for monster in targets:
                    monster[field] = value
                    monster["in_turn"] = False
                self.context.STATE["battle_order"] = [
                    ident for ident in self.context.STATE["battle_order"]
                    if ident not in removed_ids
                ]
            else:
                for monster in targets:
                    monster[field] = value

        elif body.action == "reset":
            for monster in targets:
                self.context.reset_entity(monster)

            self.context.clean_order()

        else:  # remove
            removed_ids = {monster["id"] for monster in targets}
            self.context.STATE["monsters"] = [
                monster for monster in self.context.STATE["monsters"]
                if monster["id"] not in removed_ids
            ]
            self.context.STATE["battle_order"] = [
                ident for ident in self.context.STATE["battle_order"]
                if ident not in removed_ids
            ]

        await self.context.combatants_changed(monsters=True, characters=False)
        return {"count": len(targets)}

    # ============================================================================
    # Character management
    # ============================================================================


    async def import_characters_csv(self, csv_file: UploadFile=File(...)) -> dict[str, int]:
        """Import characters csv."""
        if not (csv_file.filename or "").lower().endswith(".csv"):
            raise self.context.HTTPException(400, "Upload a .csv file")

        rows = self.context.csv_rows(await csv_file.read())
        imported = [
            self.context.csv_character(row, row_number)
            for row_number, row in enumerate(rows, start=2)
        ]

        ids = [character["id"] for character in imported]
        existing_ids = {monster["id"] for monster in self.context.STATE["monsters"]}
        existing_ids.update(character["id"] for character in self.context.STATE["characters"])

        if len(ids) != len(set(ids)):
            raise self.context.HTTPException(400, "CSV contains duplicate IDs")

        conflicting = set(ids) & existing_ids
        if conflicting:
            raise self.context.HTTPException(
                400,
                "CSV ID already exists in the active campaign encounter: "
                + ", ".join(sorted(conflicting)[:5]),
            )

        self.context.STATE["characters"].extend(imported)
        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=False, characters=True)

        return {"count": len(imported)}

    async def create_character(self, character: CharacterCreate):
        """Create character."""
        c = {'id': self.context.uuid.uuid4().hex, **character.model_dump(), 'max_hp': character.hp, 'original_hp': character.hp, 'original_initiative': character.initiative, 'active': False, 'alive': character.hp >= 0, 'visible': False, 'in_turn': False}
        self.context.STATE["characters"].append(c)
        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=False, characters=True)

        return c

    async def update_character(self, ident: str, update: CharacterUpdate) -> dict[str, Any]:
        """Update character."""
        character = next(
            (item for item in self.context.STATE["characters"] if item["id"] == ident),
            None,
        )

        if not character:
            raise self.context.HTTPException(404, "Character not found")

        values = update.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        hp_delta = values.pop("hp_delta", None)

        for key, value in values.items():
            if key != "in_turn":
                character[key] = value

        if hp_delta is not None:
            character["hp"] += hp_delta

        if "max_hp" in values:
            character["original_hp"] = values["max_hp"]

        if character["hp"] <= 0:
            character["alive"] = False
            character["visible"] = True
            character["in_turn"] = False
        else:
            character["alive"] = True

        if hp_delta is not None:
            self.context.log_hp_change(character, hp_delta)

        if values.get("active") is True:
            self.context.insert_into_battle_order(character)

        if values.get("alive") is False:
            character["visible"] = True
            character["in_turn"] = False

        if values.get("active") is False:
            character["in_turn"] = False

        self.context.set_turn(character, values.get("in_turn"))
        self.context.clean_order()
        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=False, characters=True)

        return character

    async def bulk_characters(self, body: BulkCombatantAction) -> dict[str, int]:
        """Apply one validated bulk action to selected campaign characters."""
        allowed = {"join-battle", "leave-battle", "reset", "remove"}

        if body.action not in allowed:
            raise self.context.HTTPException(400, "Unsupported bulk character action")

        targets = self.context.selected_entities("characters", body.ids)

        if body.action == "join-battle":
            for character in targets:
                character["active"] = True

        elif body.action == "leave-battle":
            for character in targets:
                character["active"] = False
                character["in_turn"] = False
            self.context.STATE["battle_order"] = [
                ident for ident in self.context.STATE["battle_order"]
                if ident not in {character["id"] for character in targets}
            ]

        elif body.action == "reset":
            for character in targets:
                self.context.reset_entity(character)

            self.context.clean_order()

        else:  # remove
            removed_ids = {character["id"] for character in targets}
            self.context.STATE["characters"] = [
                character for character in self.context.STATE["characters"]
                if character["id"] not in removed_ids
            ]
            self.context.STATE["battle_order"] = [
                ident for ident in self.context.STATE["battle_order"]
                if ident not in removed_ids
            ]

        # Character records are owned by the active campaign.
        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=False, characters=True)
        return {"count": len(targets)}

    # ============================================================================
    # Shared combatant operations
    # ============================================================================


    async def delete_combatant(self, ident: str) -> dict[str, str]:
        """Delete combatant."""
        monster_index = next(
            (
                index
                for index, monster in enumerate(self.context.STATE["monsters"])
                if monster["id"] == ident
            ),
            None,
        )

        removed_character = False
        is_monster = monster_index is None
        is_character = not is_monster

        if monster_index is not None:
            removed = self.context.STATE["monsters"].pop(monster_index)
        else:
            character_index = next(
                (
                    index
                    for index, character in enumerate(self.context.STATE["characters"])
                    if character["id"] == ident
                ),
                None,
            )

            is_character = character_index is not None
            if character_index is None:
                raise self.context.HTTPException(404, "Combatant not found")

            removed = self.context.STATE["characters"].pop(character_index)
            removed_character = True

        self.context.STATE["battle_order"] = [
            combatant_id
            for combatant_id in self.context.STATE["battle_order"]
            if combatant_id != ident
        ]

        if removed_character:
            self.context.save_active_campaign_characters()

        await self.context.combatants_changed(monsters=is_monster, characters=is_character)

        return {
            "id": ident,
            "name": str(removed.get("name", "Combatant")),
        }

    async def reset_one_combatant(self, ident: str):
        """Reset one combatant."""
        x = self.context.entity(ident)

        if not x:
            raise self.context.HTTPException(404, "Combatant not found")

        is_character = x in self.context.STATE["characters"]

        self.context.reset_entity(x)
        self.context.clean_order()

        if is_character:
            self.context.save_active_campaign_characters()

        await self.context.combatants_changed(monsters=not is_character, characters=is_character)


        return x

    # ============================================================================
    # Battle actions and lifecycle
    # ============================================================================


    async def battle_end(self) -> dict[str, str]:
        """Battle end."""
        self.context.clear_turns()
        self.context.STATE["battle_order"] = []

        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=True, characters=True)

        return {"status": "ended"}

    async def reset_all(self):
        """Reset all."""
        for combatant in self.context.entities():
            self.context.reset_entity(combatant)

        self.context.sort_admin_by_max_hp()
        self.context.STATE["battle_order"] = []

        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=True, characters=True)

        return {"status": "reset"}

    async def battle_start(self, payload: BattleStart):
        """Battle start."""
        self.context.begin_battle(payload.order)
        self.context.sort_admin_by_initiative()

        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=True, characters=True)

        return self.context.public_state()

    async def battle_next(self):
        """Battle next."""
        current = self.context.advance_turn()

        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=True, characters=True)

        return {"current": current}

    async def apply_battle_actions(self, payload: BattleActions) -> dict[str, Any]:
        """Apply battle actions."""
        actor = self.context.entity(payload.actor_id)

        if actor is None:
            raise self.context.HTTPException(404, "Active combatant was not found")

        if not actor.get("active") or not actor.get("alive", True):
            raise self.context.HTTPException(400, "The acting combatant must be active and alive")

        if not actor.get("in_turn"):
            raise self.context.HTTPException(
                400,
                "Only the current active combatant may apply battle actions",
            )

        valid_actions = {"damage", "heal", "buff", "debuff"}
        prepared: list[tuple[dict[str, Any], str, int | None]] = []

        # Validate all rows before changing state, so a malformed row cannot leave
        # prior rows partially applied.
        for row in payload.actions:
            if row.action not in valid_actions:
                raise self.context.HTTPException(400, "Unsupported battle action")

            target = self.context.entity(row.target_id)

            if target is None:
                raise self.context.HTTPException(404, "Target combatant was not found")

            if not target.get("active") or not target.get("alive", True):
                raise self.context.HTTPException(
                    400,
                    f"Target {target['name']} must be active and alive",
                )

            if row.action in {"damage", "heal"}:
                if row.amount is None or row.amount <= 0:
                    raise self.context.HTTPException(
                        400,
                        f"{row.action.title()} requires an amount greater than zero",
                    )
                amount: int | None = row.amount
            else:
                if row.amount is not None:
                    raise self.context.HTTPException(
                        400,
                        f"{row.action.title()} must not include an amount",
                    )
                amount = None

            prepared.append((target, row.action, amount))

        # Apply only after every row passed validation.
        for target, action, amount in prepared:
            if action == "damage":
                target["hp"] -= amount
                self.context.update_alive_state(target)
            elif action == "heal":
                target["hp"] += amount
                self.context.update_alive_state(target)

            self.context.log_battle_action(actor, target, action, amount)

        self.context.clean_order()
        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=True, characters=True)

        return {
            "applied": len(prepared),
            "activity_log": self.context.STATE["activity_log"],
        }

    # ============================================================================
    # Activity log exports and maintenance
    # ============================================================================


    async def export_activity_log_json(self) -> Response:
        """Export activity log json."""
        content = self.context.json.dumps(
            self.context.STATE["activity_log"],
            indent=2,
            ensure_ascii=False,
        )

        return self.context.Response(
            content=content,
            media_type="application/json",
            headers={
                "Content-Disposition":
                    'attachment; filename="activity-log.json"',
            },
        )

    async def export_activity_log_csv(self) -> Response:
        """Export activity log csv."""
        fieldnames = [
            "id",
            "timestamp",
            "active_combatant_id",
            "active_combatant",
            "active_combatant_state",
            "target_combatant_id",
            "target_combatant",
            "target_combatant_state",
            "action",
            "amount",
        ]

        output = self.context.io.StringIO(newline="")
        writer = self.context.csv.DictWriter(
            output,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )

        writer.writeheader()

        for entry in self.context.STATE["activity_log"]:
            writer.writerow(entry)

        return self.context.Response(
            content=output.getvalue(),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition":
                    'attachment; filename="activity-log.csv"',
            },
        )

    async def clear_activity_log(self) -> dict[str, int]:
        """Clear activity log."""
        cleared = len(self.context.STATE["activity_log"])
        self.context.STATE["activity_log"] = []

        await self.context.changed()

        return {"cleared": cleared}
