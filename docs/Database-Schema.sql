-- Schema v4; reference only. Let the application migrate existing databases.

CREATE TABLE activity_log_entries (id INTEGER PRIMARY KEY AUTOINCREMENT, encounter_id INTEGER NOT NULL REFERENCES encounters(id) ON DELETE CASCADE, event_id TEXT NOT NULL, position INTEGER NOT NULL CHECK(position>=0), timestamp TEXT, active_combatant_id TEXT, active_combatant TEXT, active_combatant_state TEXT, target_combatant_id TEXT, target_combatant TEXT, target_combatant_state TEXT, action TEXT, amount INTEGER, UNIQUE(encounter_id,event_id));

CREATE TABLE activity_log_entries_attributes (id INTEGER PRIMARY KEY AUTOINCREMENT, parent_id INTEGER NOT NULL REFERENCES activity_log_entries(id) ON DELETE CASCADE, field_name TEXT NOT NULL, value_kind TEXT NOT NULL CHECK(value_kind IN ('null','text','integer','real','boolean','present')), text_value TEXT, integer_value INTEGER, real_value REAL, UNIQUE(parent_id,field_name));

CREATE TABLE application_state (id INTEGER PRIMARY KEY CHECK(id=1), active_campaign_id INTEGER REFERENCES campaigns(id) ON DELETE SET NULL, runtime_encounter_id INTEGER REFERENCES encounters(id), legacy_import_complete INTEGER NOT NULL DEFAULT 0 CHECK(legacy_import_complete IN (0,1)), import_at TEXT, imported_campaigns INTEGER NOT NULL DEFAULT 0, imported_setups INTEGER NOT NULL DEFAULT 0, imported_characters INTEGER NOT NULL DEFAULT 0);

CREATE TABLE battle_setups (id INTEGER PRIMARY KEY AUTOINCREMENT, campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE, name TEXT NOT NULL, encounter_id INTEGER NOT NULL UNIQUE REFERENCES encounters(id), updated_at REAL NOT NULL, UNIQUE(campaign_id,name));

CREATE TABLE campaigns (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL COLLATE NOCASE UNIQUE, description TEXT NOT NULL DEFAULT '', created TEXT NOT NULL, last_setup_id INTEGER REFERENCES battle_setups(id) ON DELETE SET NULL, last_setup_at TEXT);

CREATE TABLE campaigns_attributes (id INTEGER PRIMARY KEY AUTOINCREMENT, parent_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE, field_name TEXT NOT NULL, value_kind TEXT NOT NULL CHECK(value_kind IN ('null','text','integer','real','boolean','present')), text_value TEXT, integer_value INTEGER, real_value REAL, UNIQUE(parent_id,field_name));

CREATE TABLE character_rosters (id INTEGER PRIMARY KEY AUTOINCREMENT, campaign_id INTEGER NOT NULL UNIQUE REFERENCES campaigns(id) ON DELETE CASCADE);

CREATE TABLE characters (id INTEGER PRIMARY KEY AUTOINCREMENT, roster_id INTEGER NOT NULL REFERENCES character_rosters(id) ON DELETE CASCADE, combatant_id TEXT NOT NULL, position INTEGER NOT NULL CHECK(position>=0), name TEXT, color TEXT, monster_species TEXT, image_url TEXT, ac INTEGER, hp INTEGER, max_hp INTEGER, original_hp INTEGER, initiative INTEGER, original_initiative INTEGER, alive INTEGER CHECK(alive IN (0,1) OR alive IS NULL), active INTEGER CHECK(active IN (0,1) OR active IS NULL), visible INTEGER CHECK(visible IN (0,1) OR visible IS NULL), in_turn INTEGER CHECK(in_turn IN (0,1) OR in_turn IS NULL), ally INTEGER CHECK(ally IN (0,1) OR ally IS NULL), show_ac INTEGER CHECK(show_ac IN (0,1) OR show_ac IS NULL), show_hp INTEGER CHECK(show_hp IN (0,1) OR show_hp IS NULL), show_initiative INTEGER CHECK(show_initiative IN (0,1) OR show_initiative IS NULL), UNIQUE(roster_id,combatant_id));

CREATE TABLE characters_attributes (id INTEGER PRIMARY KEY AUTOINCREMENT, parent_id INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE, field_name TEXT NOT NULL, value_kind TEXT NOT NULL CHECK(value_kind IN ('null','text','integer','real','boolean','present')), text_value TEXT, integer_value INTEGER, real_value REAL, UNIQUE(parent_id,field_name));

CREATE TABLE encounters (id INTEGER PRIMARY KEY AUTOINCREMENT, battle_round INTEGER NOT NULL DEFAULT 0 CHECK(battle_round>=0), background TEXT NOT NULL DEFAULT '#080b14', battle_order_font_size INTEGER NOT NULL DEFAULT 16, active_setup_id INTEGER REFERENCES battle_setups(id) ON DELETE SET NULL, active_turn_id TEXT, has_active_turn_marker INTEGER NOT NULL DEFAULT 0 CHECK(has_active_turn_marker IN (0,1)));

CREATE TABLE legacy_campaign_maps (id INTEGER PRIMARY KEY AUTOINCREMENT, old_slug TEXT NOT NULL UNIQUE, campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE);

CREATE TABLE migration_campaign_maps (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER NOT NULL REFERENCES migration_runs(id) ON DELETE CASCADE, old_key TEXT NOT NULL, campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE, UNIQUE(run_id,old_key));

CREATE TABLE migration_runs (id INTEGER PRIMARY KEY AUTOINCREMENT, source_version INTEGER NOT NULL, target_version INTEGER NOT NULL, migrated_at REAL NOT NULL, backup_path TEXT);

CREATE TABLE monsters (id INTEGER PRIMARY KEY AUTOINCREMENT, encounter_id INTEGER NOT NULL REFERENCES encounters(id) ON DELETE CASCADE, combatant_id TEXT NOT NULL, position INTEGER NOT NULL CHECK(position>=0), name TEXT, color TEXT, monster_species TEXT, image_url TEXT, ac INTEGER, hp INTEGER, max_hp INTEGER, original_hp INTEGER, initiative INTEGER, original_initiative INTEGER, alive INTEGER CHECK(alive IN (0,1) OR alive IS NULL), active INTEGER CHECK(active IN (0,1) OR active IS NULL), visible INTEGER CHECK(visible IN (0,1) OR visible IS NULL), in_turn INTEGER CHECK(in_turn IN (0,1) OR in_turn IS NULL), ally INTEGER CHECK(ally IN (0,1) OR ally IS NULL), show_ac INTEGER CHECK(show_ac IN (0,1) OR show_ac IS NULL), show_hp INTEGER CHECK(show_hp IN (0,1) OR show_hp IS NULL), show_initiative INTEGER CHECK(show_initiative IN (0,1) OR show_initiative IS NULL), UNIQUE(encounter_id,combatant_id));

CREATE TABLE monsters_attributes (id INTEGER PRIMARY KEY AUTOINCREMENT, parent_id INTEGER NOT NULL REFERENCES monsters(id) ON DELETE CASCADE, field_name TEXT NOT NULL, value_kind TEXT NOT NULL CHECK(value_kind IN ('null','text','integer','real','boolean','present')), text_value TEXT, integer_value INTEGER, real_value REAL, UNIQUE(parent_id,field_name));

CREATE TABLE ordered_combatants (id INTEGER PRIMARY KEY AUTOINCREMENT, encounter_id INTEGER NOT NULL REFERENCES encounters(id) ON DELETE CASCADE, list_kind TEXT NOT NULL CHECK(list_kind IN ('battle_order','turn_successors','turn_successors_before_wrap')), combatant_id TEXT NOT NULL, occurrence INTEGER NOT NULL DEFAULT 0, position INTEGER NOT NULL CHECK(position>=0), UNIQUE(encounter_id,list_kind,combatant_id,occurrence));

CREATE TRIGGER cleanup_setup_encounter AFTER DELETE ON battle_setups BEGIN DELETE FROM encounters WHERE id=OLD.encounter_id; END;

-- Schema v4: database-backed accounts and one-time import marker.
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL CHECK(role IN ('superadmin','admin','client')),
    password_hash TEXT NOT NULL
);
CREATE TABLE account_migration (
    id INTEGER PRIMARY KEY CHECK(id=1),
    completed INTEGER NOT NULL CHECK(completed=1)
);

-- Schema v6 addition: encounter-owned lairs (initiative is fixed at 20 in code).
CREATE TABLE IF NOT EXISTS lairs (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 encounter_id INTEGER NOT NULL UNIQUE REFERENCES encounters(id) ON DELETE CASCADE,
 participant_id TEXT NOT NULL, name TEXT NOT NULL, notes TEXT NOT NULL DEFAULT '', color TEXT NOT NULL,
 active INTEGER NOT NULL CHECK(active IN (0,1)), visible INTEGER NOT NULL CHECK(visible IN (0,1)),
 in_turn INTEGER NOT NULL CHECK(in_turn IN (0,1)), UNIQUE(encounter_id,participant_id));
PRAGMA user_version=6;
