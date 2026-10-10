"""Schema v4: SQLite accounts plus typed columns and ID-bearing child rows; JSON read only for upgrades."""
from __future__ import annotations
import copy
import json
import sqlite3
import time
import uuid
from contextlib import contextmanager, closing
from pathlib import Path

TEXT_FIELDS = ("name", "color", "monster_species", "image_url")
INT_FIELDS = ("ac", "hp", "max_hp", "original_hp", "initiative", "original_initiative")
BOOL_FIELDS = ("alive", "active", "visible", "in_turn", "ally", "show_ac", "show_hp", "show_initiative")
ENTITY_FIELDS = TEXT_FIELDS + INT_FIELDS + BOOL_FIELDS
LOG_FIELDS = ("timestamp", "active_combatant_id", "active_combatant", "active_combatant_state", "target_combatant_id", "target_combatant", "target_combatant_state", "action", "amount")
LIST_FIELDS = ("battle_order", "turn_successors", "turn_successors_before_wrap")
STATE_FIELDS = set(LIST_FIELDS) | {"monsters", "characters", "activity_log", "display", "active_setup", "active_turn_id", "battle_round", "lairs"}

class SQLiteStorage:
    SCHEMA_VERSION = 6

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        self.migration_backup = None
        try:
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys=ON")
            self.connection.execute("PRAGMA busy_timeout=10000")
            version = self.connection.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1, 2, 3, 4, 5, 6):
                raise RuntimeError(f"Unsupported schema version: {version}")
            if version == 0:
                if self.connection.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchone():
                    raise RuntimeError("Nonempty unversioned database; refusing to overwrite")
                with self.transaction():
                    self._create_schema()
                    self.connection.execute("PRAGMA user_version=3")
            elif version in (1, 2):
                self._backup()
                self._upgrade(version)
            if version not in (4, 5, 6):
                if version == 3:
                    self._backup()
                with self.transaction():
                    self.connection.execute("CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, role TEXT NOT NULL CHECK(role IN ('superadmin','admin','client')), password_hash TEXT NOT NULL)")
                    self.connection.execute("CREATE TABLE account_migration (id INTEGER PRIMARY KEY CHECK(id=1), completed INTEGER NOT NULL CHECK(completed=1))")
                    self.connection.execute("PRAGMA user_version=4")
            from .scrying_glass_feature_storage import upgrade_features
            upgrade_features(self, backup=version != 0)
            from .scrying_glass_lair_storage import upgrade_lairs
            upgrade_lairs(self, backup=version != 0)
            self._check_foreign_keys()
        except BaseException:
            self.close()
            raise

    @contextmanager
    def transaction(self):
        if self.connection.in_transaction:
            savepoint = "nested_" + uuid.uuid4().hex
            self.connection.execute(f"SAVEPOINT {savepoint}")
            try:
                yield self
                self.connection.execute(f"RELEASE SAVEPOINT {savepoint}")
            except BaseException:
                self.connection.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
                self.connection.execute(f"RELEASE SAVEPOINT {savepoint}")
                raise
            return
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            yield self
            self.connection.execute("COMMIT")
        except BaseException:
            if self.connection.in_transaction:
                self.connection.execute("ROLLBACK")
            raise


    def close(self): self.connection.close()

    def _check_foreign_keys(self):
        rows = list(self.connection.execute("PRAGMA foreign_key_check"))
        if rows: raise RuntimeError(f"Foreign-key violations: {[tuple(r) for r in rows]}")

    def _backup(self):
        target = self.path.with_name(self.path.name + ".before-normalization.bak")
        number = 2
        while target.exists():
            target = self.path.with_name(self.path.name + f".before-normalization-{number}.bak")
            number += 1
        with closing(sqlite3.connect(target)) as destination, destination:
            self.connection.backup(destination)
        self.migration_backup = target

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
    def _typed(value):
        if value is None: return ('null', None, None, None)
        if type(value) is bool: return ('boolean', None, int(value), None)
        if type(value) is int: return ('integer', None, value, None)
        if type(value) is float:
            import math
            if not math.isfinite(value): raise ValueError("Non-finite numeric attribute")
            return ('real', None, None, value)
        if isinstance(value, str): return ('text', value, None, None)
        raise ValueError(f"Unsupported nested attribute value: {type(value).__name__}")

    def _attributes(self, table, parent, extras, present=()):
        name = table + '_attributes'
        keep = set(extras) | set(present)
        for field, value in extras.items():
            kind, text, integer, real = self._typed(value)
            self.connection.execute(f"INSERT INTO {name}(parent_id,field_name,value_kind,text_value,integer_value,real_value) VALUES (?,?,?,?,?,?) ON CONFLICT(parent_id,field_name) DO UPDATE SET value_kind=excluded.value_kind,text_value=excluded.text_value,integer_value=excluded.integer_value,real_value=excluded.real_value", (parent,field,kind,text,integer,real))
        for field in present:
            self.connection.execute(f"INSERT INTO {name}(parent_id,field_name,value_kind) VALUES (?,?,'present') ON CONFLICT(parent_id,field_name) DO UPDATE SET value_kind='present',text_value=NULL,integer_value=NULL,real_value=NULL",(parent,field))
        for row in self.connection.execute(f"SELECT field_name FROM {name} WHERE parent_id=?",(parent,)).fetchall():
            if row[0] not in keep: self.connection.execute(f"DELETE FROM {name} WHERE parent_id=? AND field_name=?",(parent,row[0]))

    def _read_attributes(self, table, parent):
        extra, present = {}, set()
        for row in self.connection.execute(f"SELECT * FROM {table}_attributes WHERE parent_id=?",(parent,)):
            kind = row['value_kind']; field = row['field_name']
            if kind == 'present': present.add(field)
            elif kind == 'null': extra[field] = None
            elif kind == 'boolean': extra[field] = bool(row['integer_value'])
            else: extra[field] = row[{'text':'text_value','integer':'integer_value','real':'real_value'}[kind]]
        return extra, present

    def _save_entities(self, table, owner_name, owner, items):
        if not isinstance(items, list): raise ValueError(f"{table} must be a list")
        seen = set()
        for position, item in enumerate(items):
            if not isinstance(item, dict): raise ValueError("Combatants must be objects")
            ident = item['id'] if 'id' in item else uuid.uuid4().hex
            if not isinstance(ident, str) or not ident.strip() or ident in seen: raise ValueError("Invalid/duplicate combatant ID")
            seen.add(ident)
            for field in ENTITY_FIELDS:
                value = item.get(field)
                if value is not None:
                    if field in TEXT_FIELDS and not isinstance(value,str): raise ValueError(f"{field} must be text")
                    if field in INT_FIELDS and type(value) is not int: raise ValueError(f"{field} must be integer")
                    if field in BOOL_FIELDS and type(value) is not bool: raise ValueError(f"{field} must be boolean")
            names = (owner_name,'combatant_id','position') + ENTITY_FIELDS
            values = (owner,ident,position) + tuple(int(item[f]) if f in BOOL_FIELDS and item.get(f) is not None else item.get(f) for f in ENTITY_FIELDS)
            updates = ','.join(f'{f}=excluded.{f}' for f in ('position',)+ENTITY_FIELDS)
            self.connection.execute(f"INSERT INTO {table}({','.join(names)}) VALUES ({','.join('?' for _ in names)}) ON CONFLICT({owner_name},combatant_id) DO UPDATE SET {updates}",values)
            record = self.connection.execute(f"SELECT id FROM {table} WHERE {owner_name}=? AND combatant_id=?",(owner,ident)).fetchone()[0]
            extra = {k:v for k,v in item.items() if k not in set(ENTITY_FIELDS)|{'id','effects'}}
            present=[f for f in ENTITY_FIELDS if f in item]
            if 'effects' in item: present.append('effects')
            self._attributes(table,record,extra,present=present)
            if self.connection.execute('PRAGMA user_version').fetchone()[0]>=5:
                from .scrying_glass_feature_storage import save_effects
                save_effects(self,table,record,item.get('effects',[]))
        for row in self.connection.execute(f"SELECT combatant_id FROM {table} WHERE {owner_name}=?",(owner,)).fetchall():
            if row[0] not in seen: self.connection.execute(f"DELETE FROM {table} WHERE {owner_name}=? AND combatant_id=?",(owner,row[0]))

    def _load_entities(self, table, owner_name, owner):
        result=[]
        for row in self.connection.execute(f"SELECT * FROM {table} WHERE {owner_name}=? ORDER BY position,id",(owner,)):
            extra,present=self._read_attributes(table,row['id'])
            item={'id':row['combatant_id']}
            for field in present - {"effects"}:
                value=row[field]
                item[field]=bool(value) if field in BOOL_FIELDS and value is not None else value
            if 'effects' in present:
                from .scrying_glass_feature_storage import load_effects
                item['effects']=load_effects(self,table,row['id'])
            item.update(extra);result.append(item)
        return result

    def _save_log(self, encounter, items):
        if not isinstance(items,list): raise ValueError("Activity log must be a list")
        seen=set()
        for position,item in enumerate(items):
            if not isinstance(item,dict): raise ValueError("Activity entries must be objects")
            ident=item['id'] if 'id' in item else uuid.uuid4().hex
            if not isinstance(ident,str) or not ident.strip() or ident in seen: raise ValueError("Invalid/duplicate activity ID")
            seen.add(ident)
            for field in LOG_FIELDS:
                value=item.get(field)
                if value is not None and (type(value) is not int if field=='amount' else not isinstance(value,str)):
                    raise ValueError(f"Invalid log field {field}")
            names=('encounter_id','event_id','position')+LOG_FIELDS
            self.connection.execute(f"INSERT INTO activity_log_entries({','.join(names)}) VALUES ({','.join('?' for _ in names)}) ON CONFLICT(encounter_id,event_id) DO UPDATE SET "+','.join(f'{f}=excluded.{f}' for f in ('position',)+LOG_FIELDS),(encounter,ident,position)+tuple(item.get(f) for f in LOG_FIELDS))
            record=self.connection.execute("SELECT id FROM activity_log_entries WHERE encounter_id=? AND event_id=?",(encounter,ident)).fetchone()[0]
            self._attributes('activity_log_entries',record,{k:v for k,v in item.items() if k not in set(LOG_FIELDS)|{'id'}},present=[f for f in LOG_FIELDS if f in item])
        for row in self.connection.execute("SELECT event_id FROM activity_log_entries WHERE encounter_id=?",(encounter,)).fetchall():
            if row[0] not in seen:self.connection.execute("DELETE FROM activity_log_entries WHERE encounter_id=? AND event_id=?",(encounter,row[0]))

    def _load_log(self,encounter):
        result=[]
        for row in self.connection.execute("SELECT * FROM activity_log_entries WHERE encounter_id=? ORDER BY position,id",(encounter,)):
            extra,present=self._read_attributes('activity_log_entries',row['id'])
            item={'id':row['event_id']};item.update({f:row[f] for f in present});item.update(extra);result.append(item)
        return result

    def _save_lists(self, encounter, state):
        for kind in LIST_FIELDS:
            values=state.get(kind,[])
            if not isinstance(values,list):raise ValueError(f"{kind} must be a list")
            seen=set();counts={}
            for position,ident in enumerate(values):
                if not isinstance(ident,str) or not ident:raise ValueError("Invalid ordered combatant ID")
                occurrence=counts.get(ident,0);counts[ident]=occurrence+1;seen.add((ident,occurrence))
                self.connection.execute("INSERT INTO ordered_combatants(encounter_id,list_kind,combatant_id,occurrence,position) VALUES (?,?,?,?,?) ON CONFLICT(encounter_id,list_kind,combatant_id,occurrence) DO UPDATE SET position=excluded.position",(encounter,kind,ident,occurrence,position))
            for row in self.connection.execute("SELECT combatant_id,occurrence FROM ordered_combatants WHERE encounter_id=? AND list_kind=?",(encounter,kind)).fetchall():
                if tuple(row) not in seen:self.connection.execute("DELETE FROM ordered_combatants WHERE encounter_id=? AND list_kind=? AND combatant_id=? AND occurrence=?",(encounter,kind,*row))

    def _save_encounter(self,encounter,state,*,runtime=False):
        if not isinstance(state,dict):raise ValueError("Encounter must be an object")
        unknown=set(state)-STATE_FIELDS
        if unknown:raise ValueError(f"Unsupported encounter fields: {sorted(unknown)}")
        if state.get('characters'):raise ValueError("Characters must be saved to campaign rosters")
        display=state.get('display',{})
        if not isinstance(display,dict) or set(display)-{'background','battle_order_font_size'}:raise ValueError("Unsupported display structure")
        background=display.get('background','#080b14');font=display.get('battle_order_font_size',16);round_=state.get('battle_round',0)
        if not isinstance(background,str) or type(font) is not int or type(round_) is not int or round_<0:raise ValueError("Invalid encounter/display fields")
        reference=state.get('active_setup') if runtime else None
        active_setup=None
        if reference is not None:
            if not isinstance(reference,dict):raise ValueError("Invalid setup reference")
            row=self.connection.execute("SELECT id FROM battle_setups WHERE campaign_id=? AND name=?",(reference.get('campaign_id'),reference.get('name'))).fetchone()
            if row is None:raise ValueError("Referenced active setup does not exist")
            active_setup=row[0]
        marker=state.get('active_turn_id')
        if marker is not None and not isinstance(marker,str):raise ValueError("Invalid active turn ID")
        self.connection.execute("UPDATE encounters SET battle_round=?,background=?,battle_order_font_size=?,active_setup_id=?,active_turn_id=?,has_active_turn_marker=? WHERE id=?",(round_,background,font,active_setup,marker,int('active_turn_id' in state),encounter))
        self._save_entities('monsters','encounter_id',encounter,state.get('monsters',[]))
        from .scrying_glass_lair_storage import save_lairs
        if self.connection.execute('PRAGMA user_version').fetchone()[0] >= 6:
            save_lairs(self, encounter, state.get('lairs', []))
        self._save_lists(encounter,state)
        self._save_log(encounter,state.get('activity_log',[]))

    def _load_encounter(self,encounter):
        row=self.connection.execute("SELECT * FROM encounters WHERE id=?",(encounter,)).fetchone()
        if row is None:raise RuntimeError("Encounter is missing")
        reference=None
        if row['active_setup_id'] is not None:
            setup=self.connection.execute("SELECT campaign_id,name FROM battle_setups WHERE id=?",(row['active_setup_id'],)).fetchone()
            reference={'campaign_id':str(setup['campaign_id']),'name':setup['name']}
        result={'monsters':self._load_entities('monsters','encounter_id',encounter),'characters':[],'activity_log':self._load_log(encounter),'display':{'background':row['background'],'battle_order_font_size':row['battle_order_font_size']},'active_setup':reference,'battle_round':row['battle_round']}
        from .scrying_glass_lair_storage import load_lairs
        result['lairs'] = load_lairs(self, encounter) if self.connection.execute('PRAGMA user_version').fetchone()[0] >= 6 else []
        for kind in LIST_FIELDS:
            result[kind]=[r[0] for r in self.connection.execute("SELECT combatant_id FROM ordered_combatants WHERE encounter_id=? AND list_kind=? ORDER BY position,id",(encounter,kind))]
        if row['has_active_turn_marker']:result['active_turn_id']=row['active_turn_id']
        return result

    def create_campaign(self,name,description,created,*,metadata=None,explicit_id=None):
        cursor=self.connection.execute("INSERT INTO campaigns(id,name,description,created,last_setup_at) VALUES (?,?,?,?,?)",(explicit_id,name,description,created,(metadata or {}).get('last_setup_at')))
        ident=explicit_id or cursor.lastrowid
        self._campaign_metadata(str(ident),metadata or {})
        return str(ident)

    def _campaign_metadata(self,ident,meta):
        extra={k:v for k,v in meta.items() if k not in {'id','name','description','created','last_setup','last_setup_at'}}
        self._attributes('campaigns',int(ident),extra)
        last=meta.get('last_setup');setup=None
        if last is not None:
            row=self.connection.execute("SELECT id FROM battle_setups WHERE campaign_id=? AND name=?",(ident,last)).fetchone()
            if row:setup=row[0]
        self.connection.execute("UPDATE campaigns SET last_setup_id=?,last_setup_at=? WHERE id=?",(setup,meta.get('last_setup_at'),ident))

    def read_campaigns(self):
        items={}
        for row in self.connection.execute("SELECT c.*,s.name AS last_setup_name FROM campaigns c LEFT JOIN battle_setups s ON s.id=c.last_setup_id"):
            extra,_=self._read_attributes('campaigns',row['id'])
            meta={'name':row['name'],'description':row['description'],'created':row['created']}
            if row['last_setup_name'] is not None:meta['last_setup']=row['last_setup_name']
            if row['last_setup_at'] is not None:meta['last_setup_at']=row['last_setup_at']
            meta.update(extra);items[str(row['id'])]=meta
        return {'active':self.get_value('active_campaign'),'campaigns':items}

    def write_campaigns(self,data):
        with self.transaction():
            existing=self.read_campaigns()['campaigns']
            if set(data['campaigns'])-set(existing):raise ValueError("Use create_campaign to allocate IDs")
            for ident,meta in data['campaigns'].items():
                if meta==existing[ident]:continue
                self.connection.execute("UPDATE campaigns SET name=?,description=?,created=? WHERE id=?",(meta['name'],meta.get('description',''),meta.get('created',''),ident))
                self._campaign_metadata(ident,meta)
            for ident in set(existing)-set(data['campaigns']):self.connection.execute("DELETE FROM campaigns WHERE id=?",(ident,))
            self.set_value('active_campaign',data.get('active'))

    def update_campaign(self,ident,*,name=None,description=None):
        self.connection.execute("UPDATE campaigns SET name=COALESCE(?,name),description=COALESCE(?,description) WHERE id=?",(name,description,ident))

    def campaign_exists(self,ident):return self.connection.execute("SELECT 1 FROM campaigns WHERE id=?",(ident,)).fetchone() is not None
    def campaign_name_exists(self,name,exclude=None):return any(meta['name'].casefold()==name.casefold() for ident,meta in self.read_campaigns()['campaigns'].items() if ident!=exclude)

    def load_characters(self,campaign):
        row=self.connection.execute("SELECT id FROM character_rosters WHERE campaign_id=?",(campaign,)).fetchone()
        return self._load_entities('characters','roster_id',row[0]) if row else None

    def save_characters(self,campaign,characters):
        with self.transaction():
            self.connection.execute("INSERT INTO character_rosters(campaign_id) VALUES (?) ON CONFLICT(campaign_id) DO NOTHING",(campaign,))
            ident=self.connection.execute("SELECT id FROM character_rosters WHERE campaign_id=?",(campaign,)).fetchone()[0]
            self._save_entities('characters','roster_id',ident,characters)

    def list_setups(self,campaign):return sorted((r[0] for r in self.connection.execute("SELECT name FROM battle_setups WHERE campaign_id=?",(campaign,))),key=str.casefold)
    def setup_exists(self,campaign,name):return self.connection.execute("SELECT 1 FROM battle_setups WHERE campaign_id=? AND name=?",(campaign,name)).fetchone() is not None
    def load_setup(self,campaign,name):
        row=self.connection.execute("SELECT encounter_id FROM battle_setups WHERE campaign_id=? AND name=?",(campaign,name)).fetchone()
        if row is None:raise FileNotFoundError(f"{campaign}/{name}")
        return self._load_encounter(row[0])

    def save_setup(self,campaign,name,snapshot,updated_at=None):
        with self.transaction():
            row=self.connection.execute("SELECT encounter_id FROM battle_setups WHERE campaign_id=? AND name=?",(campaign,name)).fetchone()
            if row:encounter=row[0]
            else:
                encounter=self.connection.execute("INSERT INTO encounters DEFAULT VALUES").lastrowid
                self.connection.execute("INSERT INTO battle_setups(campaign_id,name,encounter_id,updated_at) VALUES (?,?,?,?)",(campaign,name,encounter,time.time() if updated_at is None else updated_at))
            self._save_encounter(encounter,snapshot)
            self.connection.execute("UPDATE battle_setups SET updated_at=? WHERE campaign_id=? AND name=?",(time.time() if updated_at is None else updated_at,campaign,name))

    def rename_setup(self, campaign, old, new):
        """Rename a setup and its checkpoint references atomically."""
        with self.transaction():
            cursor = self.connection.execute(
                "UPDATE battle_setups SET name=? WHERE campaign_id=? AND name=?",
                (new, campaign, old),
            )
            if cursor.rowcount:
                self.connection.execute(
                    "UPDATE encounter_snapshots SET setup_name=? "
                    "WHERE campaign_id=? AND setup_name=? AND kind='checkpoint'",
                    (new, campaign, old),
                )
    def delete_setup(self,campaign,name):self.connection.execute("DELETE FROM battle_setups WHERE campaign_id=? AND name=?",(campaign,name))
    def unique_setup_name(self, campaign, name):
        """Reserve suffix space within the API's 80-character setup-name limit."""
        base = name[:80]
        result = base
        number = 2
        while self.setup_exists(campaign, result):
            suffix = f"-{number}"
            stem = base[:80 - len(suffix)].rstrip("-")
            result = f"{stem}{suffix}"
            number += 1
        return result

    def transfer_setup(self, source, target, name, mode):
        """Transfer a setup without attaching effects to another campaign's roster."""
        if mode not in ('move', 'copy'):
            raise ValueError("Invalid mode")
        with self.transaction():
            result = self.unique_setup_name(target, name)
            row = self.connection.execute(
                "SELECT updated_at FROM battle_setups WHERE campaign_id=? AND name=?",
                (source, name),
            ).fetchone()
            if row is None:
                raise FileNotFoundError(name)
            snapshot = self.load_setup(source, name)
            if str(source) != str(target):
                internal_ids = {
                    item['id']
                    for item in [*snapshot['monsters'], *snapshot.get('lairs', [])]
                }
                for monster in snapshot['monsters']:
                    effects = []
                    for effect in monster.get('effects', []):
                        if effect.get('source_id') not in internal_ids:
                            if effect.get('concentration'):
                                continue
                            effect['source_id'] = None
                        if effect.get('anchor_id') not in internal_ids:
                            effect['anchor_id'] = None
                            if effect.get('timing') != 'manual':
                                effect.update(timing='manual', turns=None)
                        effects.append(effect)
                    monster['effects'] = effects
            # Saved setup references must not retain their former owner/name.
            snapshot['active_setup'] = None
            if mode == 'move':
                setup_id = self.connection.execute(
                    "SELECT id FROM battle_setups WHERE campaign_id=? AND name=?",
                    (source, name),
                ).fetchone()[0]
                self.connection.execute(
                    "UPDATE campaigns SET last_setup_id=NULL WHERE id=? AND last_setup_id=?",
                    (source, setup_id),
                )
                self.connection.execute(
                    "UPDATE battle_setups SET campaign_id=?,name=? WHERE id=?",
                    (target, result, setup_id),
                )
            self.save_setup(target, result, snapshot, row[0])
            return result
    def newest_setup(self,campaign):
        rows=list(self.connection.execute("SELECT name,updated_at FROM battle_setups WHERE campaign_id=?",(campaign,)))
        return min(rows,key=lambda r:(-r[1],r[0].casefold()))[0] if rows else None

    def get_value(self,key,default=None):
        state=self.connection.execute("SELECT * FROM application_state WHERE id=1").fetchone()
        if key=='active_campaign':return str(state['active_campaign_id']) if state['active_campaign_id'] is not None else default
        if key=='runtime_state':return self._load_encounter(state['runtime_encounter_id']) if state['runtime_encounter_id'] is not None else default
        if key=='legacy_import_complete':
            return {'at':state['import_at'],'counts':{'campaigns':state['imported_campaigns'],'setups':state['imported_setups'],'characters':state['imported_characters']}} if state['legacy_import_complete'] else default
        if key=='legacy_campaign_id_map':return {r['old_slug']:str(r['campaign_id']) for r in self.connection.execute("SELECT * FROM legacy_campaign_maps")}
        if key=='campaign_id_migration':
            row=self.connection.execute("SELECT * FROM migration_runs ORDER BY id DESC LIMIT 1").fetchone()
            return {'at':row['migrated_at'],'slug_to_id':{r['old_key']:str(r['campaign_id']) for r in self.connection.execute("SELECT * FROM migration_campaign_maps WHERE run_id=?",(row['id'],))}} if row else default
        raise ValueError(f"Unsupported application state key: {key}")

    def set_value(self,key,value):
        with self.transaction():
            if key=='active_campaign':self.connection.execute("UPDATE application_state SET active_campaign_id=? WHERE id=1",(value,))
            elif key=='runtime_state':
                row=self.connection.execute("SELECT runtime_encounter_id FROM application_state WHERE id=1").fetchone()
                encounter=row[0]
                if encounter is None:
                    encounter=self.connection.execute("INSERT INTO encounters DEFAULT VALUES").lastrowid
                    self.connection.execute("UPDATE application_state SET runtime_encounter_id=? WHERE id=1",(encounter,))
                self._save_encounter(encounter,value,runtime=True)
            elif key=='legacy_import_complete':
                counts=value.get('counts',{}) if isinstance(value,dict) else {}
                self.connection.execute("UPDATE application_state SET legacy_import_complete=?,import_at=?,imported_campaigns=?,imported_setups=?,imported_characters=? WHERE id=1",(int(bool(value)),value.get('at') if isinstance(value,dict) else None,counts.get('campaigns',0),counts.get('setups',0),counts.get('characters',0)))
            elif key=='legacy_campaign_id_map':
                for old,ident in value.items():self.connection.execute("INSERT INTO legacy_campaign_maps(old_slug,campaign_id) VALUES (?,?) ON CONFLICT(old_slug) DO UPDATE SET campaign_id=excluded.campaign_id",(old,ident))
            else:raise ValueError(f"Unsupported application state key: {key}")

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
