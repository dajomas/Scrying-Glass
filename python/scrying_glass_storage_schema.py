"""Base schema and legacy upgrades staged for the Storage split; not yet wired."""
import copy
import json
import time
from .scrying_glass_storage_fields import TEXT_FIELDS, INT_FIELDS, BOOL_FIELDS


class StorageSchemaMixin:
    """Use the facade's connection and transactional storage helpers at activation."""

    def _create_schema(self):
        statements = [
            "CREATE TABLE campaigns (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL COLLATE NOCASE UNIQUE, description TEXT NOT NULL DEFAULT '', created TEXT NOT NULL, last_setup_id INTEGER REFERENCES battle_setups(id) ON DELETE SET NULL, last_setup_at TEXT)",
            "CREATE TABLE encounters (id INTEGER PRIMARY KEY AUTOINCREMENT, battle_round INTEGER NOT NULL DEFAULT 0 CHECK(battle_round>=0), background TEXT NOT NULL DEFAULT '#080b14', battle_order_font_size INTEGER NOT NULL DEFAULT 16, active_setup_id INTEGER REFERENCES battle_setups(id) ON DELETE SET NULL, active_turn_id TEXT, has_active_turn_marker INTEGER NOT NULL DEFAULT 0 CHECK(has_active_turn_marker IN (0,1)))",
            "CREATE TABLE battle_setups (id INTEGER PRIMARY KEY AUTOINCREMENT, campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE, name TEXT NOT NULL, encounter_id INTEGER NOT NULL UNIQUE REFERENCES encounters(id), updated_at REAL NOT NULL, UNIQUE(campaign_id,name))",
            "CREATE TABLE application_state (id INTEGER PRIMARY KEY CHECK(id=1), active_campaign_id INTEGER REFERENCES campaigns(id) ON DELETE SET NULL, runtime_encounter_id INTEGER REFERENCES encounters(id), legacy_import_complete INTEGER NOT NULL DEFAULT 0 CHECK(legacy_import_complete IN (0,1)), import_at TEXT, imported_campaigns INTEGER NOT NULL DEFAULT 0, imported_setups INTEGER NOT NULL DEFAULT 0, imported_characters INTEGER NOT NULL DEFAULT 0)",
            "CREATE TABLE character_rosters (id INTEGER PRIMARY KEY AUTOINCREMENT, campaign_id INTEGER NOT NULL UNIQUE REFERENCES campaigns(id) ON DELETE CASCADE)",
            "CREATE TABLE ordered_combatants (id INTEGER PRIMARY KEY AUTOINCREMENT, encounter_id INTEGER NOT NULL REFERENCES encounters(id) ON DELETE CASCADE, list_kind TEXT NOT NULL CHECK(list_kind IN ('battle_order','turn_successors','turn_successors_before_wrap')), combatant_id TEXT NOT NULL, occurrence INTEGER NOT NULL DEFAULT 0, position INTEGER NOT NULL CHECK(position>=0), UNIQUE(encounter_id,list_kind,combatant_id,occurrence))",
            "CREATE TABLE activity_log_entries (id INTEGER PRIMARY KEY AUTOINCREMENT, encounter_id INTEGER NOT NULL REFERENCES encounters(id) ON DELETE CASCADE, event_id TEXT NOT NULL, position INTEGER NOT NULL CHECK(position>=0), timestamp TEXT, active_combatant_id TEXT, active_combatant TEXT, active_combatant_state TEXT, target_combatant_id TEXT, target_combatant TEXT, target_combatant_state TEXT, action TEXT, amount INTEGER, UNIQUE(encounter_id,event_id))",
            "CREATE TABLE migration_runs (id INTEGER PRIMARY KEY AUTOINCREMENT, source_version INTEGER NOT NULL, target_version INTEGER NOT NULL, migrated_at REAL NOT NULL, backup_path TEXT)",
            "CREATE TABLE migration_campaign_maps (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER NOT NULL REFERENCES migration_runs(id) ON DELETE CASCADE, old_key TEXT NOT NULL, campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE, UNIQUE(run_id,old_key))",
            "CREATE TABLE legacy_campaign_maps (id INTEGER PRIMARY KEY AUTOINCREMENT, old_slug TEXT NOT NULL UNIQUE, campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE)",
            "CREATE TRIGGER cleanup_setup_encounter AFTER DELETE ON battle_setups BEGIN DELETE FROM encounters WHERE id=OLD.encounter_id; END",
        ]
        entity_columns = ', '.join([f'{name} TEXT' for name in TEXT_FIELDS] + [f'{name} INTEGER' for name in INT_FIELDS] + [f'{name} INTEGER CHECK({name} IN (0,1) OR {name} IS NULL)' for name in BOOL_FIELDS])
        for table, owner in (("characters", "roster_id INTEGER NOT NULL REFERENCES character_rosters(id) ON DELETE CASCADE"), ("monsters", "encounter_id INTEGER NOT NULL REFERENCES encounters(id) ON DELETE CASCADE")):
            owner_name = owner.split()[0]
            statements.append(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY AUTOINCREMENT, {owner}, combatant_id TEXT NOT NULL, position INTEGER NOT NULL CHECK(position>=0), {entity_columns}, UNIQUE({owner_name},combatant_id))")
        # Presence rows preserve absent versus explicit NULL fields in older payloads.
        # Scalar extension attributes are typed records, never serialized objects.
        for table in ("characters", "monsters", "activity_log_entries", "campaigns"):
            statements.append(f"CREATE TABLE {table}_attributes (id INTEGER PRIMARY KEY AUTOINCREMENT, parent_id INTEGER NOT NULL REFERENCES {table}(id) ON DELETE CASCADE, field_name TEXT NOT NULL, value_kind TEXT NOT NULL CHECK(value_kind IN ('null','text','integer','real','boolean','present')), text_value TEXT, integer_value INTEGER, real_value REAL, UNIQUE(parent_id,field_name))")
        for statement in statements: self.connection.execute(statement)
        self.connection.execute("INSERT INTO application_state(id) VALUES (1)")

    @staticmethod
    def convert_campaign_references(value,mapping,*,strict=True):
        result=copy.deepcopy(value)
        if not isinstance(result,dict):raise ValueError("State must be an object")
        reference=result.get('active_setup')
        if reference is not None:
            if not isinstance(reference,dict):raise ValueError("Invalid active_setup")
            old=reference.get('campaign_id',reference.get('campaign'))
            if str(old) not in mapping:
                if strict:raise ValueError(f"Unknown campaign reference: {old}")
                result['active_setup']=None
            else:
                reference.pop('campaign',None);reference['campaign_id']=str(mapping[str(old)])
        return result

    def _upgrade(self,version):
        with self.transaction():
            self._check_foreign_keys()
            if version==1:
                campaigns=[(r['slug'],json.loads(r['metadata_json'])) for r in self.connection.execute("SELECT * FROM campaigns ORDER BY slug")]
                owner='campaign_slug'
            else:
                campaigns=[];owner='campaign_id'
                for row in self.connection.execute("SELECT * FROM campaigns ORDER BY id"):
                    meta=json.loads(row['metadata_json']);meta.update(name=row['name'],description=row['description'],created=row['created'])
                    campaigns.append((str(row['id']),meta))
            rosters=[(str(r[owner]),json.loads(r['characters_json'])) for r in self.connection.execute("SELECT * FROM campaign_characters")]
            setups=[(str(r[owner]),r['name'],json.loads(r['snapshot_json']),r['updated_at']) for r in self.connection.execute("SELECT * FROM battle_setups")]
            values={r['key']:json.loads(r['value_json']) for r in self.connection.execute("SELECT * FROM application_state")}
            supported={'active_campaign','runtime_state','legacy_import_complete','legacy_campaign_id_map','campaign_id_migration'}
            if set(values)-supported:raise ValueError(f"Unsupported old state keys: {set(values)-supported}")
            for table in ('battle_setups','campaign_characters','campaigns','application_state'):self.connection.execute(f'DROP TABLE {table}')
            self._create_schema();mapping={}
            for old,meta in campaigns:
                if not isinstance(meta,dict):raise ValueError("Invalid campaign metadata")
                mapping[str(old)]=self.create_campaign(meta.get('name',old),meta.get('description',''),meta.get('created',''),metadata=meta,explicit_id=int(old) if version==2 else None)
            for old,items in rosters:self.save_characters(mapping[old],items)
            for old,name,snapshot,updated in setups:
                snapshot=self.convert_campaign_references(snapshot,mapping,strict=False)
                # Setup characters, if present in a transitional database, must not disappear.
                if snapshot.get('characters'):raise ValueError("Embedded setup characters require manual campaign-roster reconciliation")
                self.save_setup(mapping[old],name,snapshot,updated)
            for old,meta in campaigns:self._campaign_metadata(mapping[str(old)],meta)
            active=values.get('active_campaign')
            if active is not None:
                if str(active) not in mapping:raise ValueError("Unknown active campaign")
                self.set_value('active_campaign',mapping[str(active)])
            if 'runtime_state' in values:
                runtime=self.convert_campaign_references(values['runtime_state'],mapping)
                reference=runtime.get('active_setup')
                if reference and reference['campaign_id']!=self.get_value('active_campaign'):raise ValueError("Active campaign/setup mismatch")
                self.set_value('runtime_state',runtime)
            self.set_value('legacy_import_complete',values.get('legacy_import_complete',{'at':str(time.time()),'counts':{'campaigns':len(campaigns),'setups':len(setups),'characters':sum(len(x[1]) for x in rosters)}}))
            legacy=values.get('legacy_campaign_id_map')
            if legacy:self.set_value('legacy_campaign_id_map',{old:mapping[str(ident)] for old,ident in legacy.items()})
            previous=values.get('campaign_id_migration',{}).get('slug_to_id',{})
            if previous:self.set_value('legacy_campaign_id_map',{old:mapping[str(ident)] for old,ident in previous.items()})
            run=self.connection.execute("INSERT INTO migration_runs(source_version,target_version,migrated_at,backup_path) VALUES (?,3,?,?)",(version,time.time(),str(self.migration_backup))).lastrowid
            for old,ident in mapping.items():self.connection.execute("INSERT INTO migration_campaign_maps(run_id,old_key,campaign_id) VALUES (?,?,?)",(run,old,ident))
            self._check_foreign_keys();self.connection.execute("PRAGMA user_version=3")
