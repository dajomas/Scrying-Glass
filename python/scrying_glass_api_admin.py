"""Compose admin handler groups and register routes in their original order."""
from __future__ import annotations
from typing import Any, get_type_hints
from fastapi import Depends, FastAPI
from .scrying_glass_database_transactions import transactional_handler, serialized_handler
from .scrying_glass_request_security import same_origin
from .scrying_glass_admin_pages import AdminPagesMixin
from .scrying_glass_admin_display import AdminDisplayMixin
from .scrying_glass_admin_setups import AdminSetupsMixin
from .scrying_glass_admin_campaigns import AdminCampaignsMixin
from .scrying_glass_admin_monsters import AdminMonstersMixin
from .scrying_glass_admin_characters import AdminCharactersMixin
from .scrying_glass_admin_combatants import AdminCombatantsMixin
from .scrying_glass_admin_battle import AdminBattleMixin
from .scrying_glass_admin_activity import AdminActivityMixin

# Path, handler name, HTTP method, authentication required.
ADMIN_ROUTES = (
    ('/login', 'admin_login_get', 'GET', False),
    ('/login', 'admin_login_post', 'POST', False),
    ('/', 'admin_home', 'GET', False),
    ('/api/state', 'admin_get_state', 'GET', True),
    ('/api/dndbeyond/monster-stats', 'dndbeyond_monster_stats', 'GET', True),
    ('/api/display/battle-order-font', 'adjust_battle_order_font', 'POST', True),
    ('/api/display/background', 'update_display_background', 'PATCH', True),
    ('/api/display/background-image', 'upload_display_background_image', 'POST', True),
    ('/api/setups', 'get_setups', 'GET', True),
    ('/api/campaigns', 'get_campaigns', 'GET', True),
    ('/api/campaigns', 'create_campaign', 'POST', True),
    ('/api/campaigns/{campaign_id}', 'update_campaign', 'PATCH', True),
    ('/api/campaigns/{campaign_id}', 'delete_campaign', 'DELETE', True),
    ('/api/campaigns/{campaign_id}/activate', 'activate_campaign', 'POST', True),
    ('/api/campaigns/{campaign_id}/setups', 'add_setup_to_campaign', 'POST', True),
    ('/api/setups/new', 'new_setup', 'POST', True),
    ('/api/setups/save', 'save_setup', 'POST', True),
    ('/api/setups/load', 'load_setup', 'POST', True),
    ('/api/setups/rename', 'rename_setup', 'POST', True),
    ('/api/setups/{name}', 'delete_setup', 'DELETE', True),
    ('/api/setups/import', 'import_setup', 'POST', True),
    ('/api/monsters/roll-initiative', 'roll_monster_initiative', 'POST', True),
    ('/api/monsters', 'create_monster', 'POST', True),
    ('/api/monsters/import', 'import_monster', 'POST', True),
    ('/api/monsters/import-csv', 'import_monsters_csv', 'POST', True),
    ('/api/characters/import-csv', 'import_characters_csv', 'POST', True),
    ('/api/monsters/{ident}/edit', 'edit_monster', 'POST', True),
    ('/api/monsters/{ident}', 'update_monster', 'PATCH', True),
    ('/api/characters', 'create_character', 'POST', True),
    ('/api/characters/{ident}', 'update_character', 'PATCH', True),
    ('/api/combatants/{ident}', 'delete_combatant', 'DELETE', True),
    ('/api/combatants/{ident}/reset', 'reset_one_combatant', 'POST', True),
    ('/api/characters/bulk', 'bulk_characters', 'POST', True),
    ('/api/monsters/bulk', 'bulk_monsters', 'POST', True),
    ('/api/battle/end', 'battle_end', 'POST', True),
    ('/api/battle/reset-all', 'reset_all', 'POST', True),
    ('/api/battle/start', 'battle_start', 'POST', True),
    ('/api/battle/next', 'battle_next', 'POST', True),
    ('/api/battle/actions', 'apply_battle_actions', 'POST', True),
    ('/api/activity-log.json', 'export_activity_log_json', 'GET', True),
    ('/api/activity-log.csv', 'export_activity_log_csv', 'GET', True),
    ('/api/activity-log/clear', 'clear_activity_log', 'POST', True),
)
class AdminAPI(AdminPagesMixin, AdminDisplayMixin, AdminSetupsMixin, AdminCampaignsMixin, AdminMonstersMixin, AdminCharactersMixin, AdminCombatantsMixin, AdminBattleMixin, AdminActivityMixin):
    """Compose domain handlers into the existing admin API interface."""

    def __init__(self, context: Any, app: FastAPI) -> None:
        """Bind handlers, resolve request types, and register routes on the application."""
        self.context = context
        self.app = app
        self.register_routes()
        from .scrying_glass_admin_users import install_user_routes
        install_user_routes(context, app)
        from .scrying_glass_logout import install_logout
        install_logout(context, app, context.ADMIN_SESSION_COOKIE)

    def register_routes(self) -> None:
        """Resolve types and register routes with unchanged paths and authorization."""
        for path, name, method, authenticated in ADMIN_ROUTES:
            handler = getattr(self, name)
            handler.__func__.__annotations__ = get_type_hints(
                handler.__func__, globalns=vars(self.context),
            )
            dependencies = []
            if authenticated:
                dependencies.append(Depends(self.context.require(
                    "admin", self.context.ADMIN_SESSION_COOKIE,
                )))
            if authenticated and method != "GET":
                dependencies.append(Depends(same_origin))
                handler = transactional_handler(
                    self.context, handler, role="admin",
                    cookie_name=self.context.ADMIN_SESSION_COOKIE,
                )
            elif authenticated and name != "dndbeyond_monster_stats":
                handler = serialized_handler(
                    self.context, handler, role="admin",
                    cookie_name=self.context.ADMIN_SESSION_COOKIE,
                )
            self.app.add_api_route(
                path, handler, methods=[method], dependencies=dependencies,
            )
