"""Attach context-aware services to the existing server namespace."""
from typing import Any
from .scrying_glass_service_auth import AuthService
from .scrying_glass_service_state import StateService
from .scrying_glass_service_campaigns import CampaignsService
from .scrying_glass_service_migrations import MigrationsService
from .scrying_glass_service_persistence import PersistenceService
from .scrying_glass_service_activity import ActivityService
from .scrying_glass_service_images import ImagesService
from .scrying_glass_service_battle import BattleService
from .scrying_glass_service_notifications import NotificationsService

def install_services(context: Any) -> dict[str, Any]:
    """Bind every service before requests or startup operations can execute."""
    services = {}
    service = AuthService(context)
    services['auth'] = service
    context.auth_service = service
    context.auth_session = service.session
    context.initialize_users = service.initialize_users
    context.user = service.user
    context.require = service.require
    service = StateService(context)
    services['state'] = service
    context.entities = service.entities
    context.entity = service.entity
    context.active_combatant = service.active_combatant
    context.configured_background = service.configured_background
    context.normalize_display = service.normalize_display
    context.normalize_state = service.normalize_state
    context.public_state = service.public_state
    context.display_state = service.display_state
    context.active_setup_reference = service.active_setup_reference
    context.set_active_setup = service.set_active_setup
    context.clear_active_setup = service.clear_active_setup
    context.active_setup_exists = service.active_setup_exists
    service = CampaignsService(context)
    services['campaigns'] = service
    context.list_setups = service.list_setups
    context.read_campaigns = service.read_campaigns
    context.write_campaigns = service.write_campaigns
    context.active_campaign = service.active_campaign
    context.require_campaign = service.require_campaign
    context.create_default_setup = service.create_default_setup
    context.remember_setup = service.remember_setup
    context.pick_campaign_setup = service.pick_campaign_setup
    context.open_campaign_setup = service.open_campaign_setup
    context.campaigns_payload = service.campaigns_payload
    service = MigrationsService(context)
    services['migrations'] = service
    context.migrate_unassigned_setups = service.migrate_unassigned_setups
    context.migrate_campaign_characters = service.migrate_campaign_characters
    context.import_legacy_storage = service.import_legacy_storage
    service = PersistenceService(context)
    services['persistence'] = service
    context.load_campaign_characters = service.load_campaign_characters
    context.save_campaign_characters = service.save_campaign_characters
    context.save_active_campaign_characters = service.save_active_campaign_characters
    context.load_setup_state = service.load_setup_state
    context.load_state = service.load_state
    context.save_state = service.save_state
    context.save_active_setup_monsters = service.save_active_setup_monsters
    service = ActivityService(context)
    services['activity'] = service
    context.log_battle_action = service.log_battle_action
    context.log_hp_change = service.log_hp_change
    service = ImagesService(context)
    services['images'] = service
    context.save_image = service.save_image
    context.dnd_image = service.dnd_image
    context.make_monster = service.make_monster
    context.make_monsters = service.make_monsters
    service = BattleService(context)
    services['battle'] = service
    context.clear_turns = service.clear_turns
    context.remember_turn_successors = service.remember_turn_successors
    context.clean_order = service.clean_order
    context.insert_into_battle_order = service.insert_into_battle_order
    context.sort_admin_by_initiative = service.sort_admin_by_initiative
    context.sort_admin_by_max_hp = service.sort_admin_by_max_hp
    context.set_turn = service.set_turn
    context.eligible = service.eligible
    context.begin_battle = service.begin_battle
    context.advance_turn = service.advance_turn
    context.selected_entities = service.selected_entities
    service = NotificationsService(context)
    services['notifications'] = service
    context.broadcast = service.broadcast
    context.changed = service.changed
    context.monster_changed = service.monster_changed
    context.character_changed = service.character_changed
    context.combatants_changed = service.combatants_changed
    from .scrying_glass_service_features import FeaturesService
    context.features = FeaturesService(context)
    services["features"] = context.features
    return services
