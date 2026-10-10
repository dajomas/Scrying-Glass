"""Normalized SQLite schema v5: effects, recovery snapshots and revisions."""
import copy
import time
from .scrying_glass_storage import TEXT_FIELDS,INT_FIELDS,BOOL_FIELDS

def upgrade_features(storage,*,backup=True):
    db=storage.connection
    if db.execute('PRAGMA user_version').fetchone()[0] in (5, 6): return
    if backup and storage.migration_backup is None: storage._backup()
    with storage.transaction():
        db.execute('CREATE TABLE feature_state (id INTEGER PRIMARY KEY CHECK(id=1), revision INTEGER NOT NULL DEFAULT 0)')
        db.execute('INSERT INTO feature_state(id) VALUES (1)')
        db.execute("CREATE TABLE encounter_snapshots (id INTEGER PRIMARY KEY AUTOINCREMENT, campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE, encounter_id INTEGER NOT NULL UNIQUE REFERENCES encounters(id), kind TEXT NOT NULL CHECK(kind IN ('undo','checkpoint')), name TEXT NOT NULL, created REAL NOT NULL, setup_name TEXT, after_digest TEXT)")
        db.execute('CREATE TRIGGER cleanup_snapshot AFTER DELETE ON encounter_snapshots BEGIN DELETE FROM encounters WHERE id=OLD.encounter_id; END')
        columns=', '.join([f'{n} TEXT' for n in TEXT_FIELDS]+[f'{n} INTEGER' for n in INT_FIELDS]+[f'{n} INTEGER CHECK({n} IN (0,1) OR {n} IS NULL)' for n in BOOL_FIELDS])
        db.execute(f'CREATE TABLE snapshot_characters (id INTEGER PRIMARY KEY AUTOINCREMENT, snapshot_id INTEGER NOT NULL REFERENCES encounter_snapshots(id) ON DELETE CASCADE, combatant_id TEXT NOT NULL, position INTEGER NOT NULL CHECK(position>=0), {columns}, UNIQUE(snapshot_id,combatant_id))')
        db.execute('CREATE TABLE snapshot_characters_attributes (id INTEGER PRIMARY KEY AUTOINCREMENT, parent_id INTEGER NOT NULL REFERENCES snapshot_characters(id) ON DELETE CASCADE, field_name TEXT NOT NULL, value_kind TEXT NOT NULL, text_value TEXT, integer_value INTEGER, real_value REAL, UNIQUE(parent_id,field_name))')
        for table in ('characters','monsters','snapshot_characters'):
            db.execute(f"CREATE TABLE {table}_effects (id INTEGER PRIMARY KEY AUTOINCREMENT, parent_id INTEGER NOT NULL REFERENCES {table}(id) ON DELETE CASCADE, effect_id TEXT NOT NULL, position INTEGER NOT NULL, name TEXT NOT NULL, source_id TEXT, notes TEXT NOT NULL DEFAULT '', public INTEGER NOT NULL CHECK(public IN (0,1)), concentration INTEGER NOT NULL CHECK(concentration IN (0,1)), timing TEXT NOT NULL, turns INTEGER, anchor_id TEXT, UNIQUE(parent_id,effect_id))")
        db.execute('PRAGMA user_version=5')

def save_effects(storage,table,parent,effects):
    from .scrying_glass_feature_rules import validate_effects
    validate_effects(effects)
    storage.connection.execute(f'DELETE FROM {table}_effects WHERE parent_id=?',(parent,))
    for position,e in enumerate(effects):
        storage.connection.execute(f'INSERT INTO {table}_effects(parent_id,effect_id,position,name,source_id,notes,public,concentration,timing,turns,anchor_id) VALUES (?,?,?,?,?,?,?,?,?,?,?)',(parent,e['id'],position,e['name'],e.get('source_id'),e.get('notes',''),int(e['public']),int(e['concentration']),e['timing'],e.get('turns'),e.get('anchor_id')))

def load_effects(storage,table,parent):
    return [dict(id=r['effect_id'],name=r['name'],source_id=r['source_id'],notes=r['notes'],public=bool(r['public']),concentration=bool(r['concentration']),timing=r['timing'],turns=r['turns'],anchor_id=r['anchor_id']) for r in storage.connection.execute(f'SELECT * FROM {table}_effects WHERE parent_id=? ORDER BY position,id',(parent,))]

class FeatureStorage:
    def __init__(self,storage): self.storage=storage;self.db=storage.connection
    def revision(self): return self.db.execute('SELECT revision FROM feature_state WHERE id=1').fetchone()[0]
    def bump(self): self.db.execute('UPDATE feature_state SET revision=revision+1 WHERE id=1')
    def save_snapshot(self,campaign,state,kind,name,digest=None):
        encounter=self.db.execute('INSERT INTO encounters DEFAULT VALUES').lastrowid
        reference=state.get('active_setup')
        ident=self.db.execute('INSERT INTO encounter_snapshots(campaign_id,encounter_id,kind,name,created,setup_name,after_digest) VALUES (?,?,?,?,?,?,?)',(campaign,encounter,kind,name,time.time(),reference.get('name') if reference else None,digest)).lastrowid
        payload=copy.deepcopy(state);payload['characters']=[];payload['active_setup']=None
        self.storage._save_encounter(encounter,payload)
        self.storage._save_entities('snapshot_characters','snapshot_id',ident,state.get('characters',[]))
        limit=30 if kind=='undo' else 50
        for r in self.db.execute('SELECT id FROM encounter_snapshots WHERE campaign_id=? AND kind=? ORDER BY id DESC LIMIT -1 OFFSET ?',(campaign,kind,limit)).fetchall(): self.delete(r[0],campaign,kind)
        return ident
    def row(self,ident,campaign,kind): return self.db.execute('SELECT * FROM encounter_snapshots WHERE id=? AND campaign_id=? AND kind=?',(ident,campaign,kind)).fetchone()
    def load(self,ident,campaign,kind):
        row=self.row(ident,campaign,kind)
        if row is None: raise ValueError('Snapshot not found in active campaign')
        state=self.storage._load_encounter(row['encounter_id']);state.pop('active_turn_id',None)
        state['characters']=self.storage._load_entities('snapshot_characters','snapshot_id',ident)
        state['active_setup']={'campaign_id':str(campaign),'name':row['setup_name']} if row['setup_name'] else None
        return state
    def delete(self,ident,campaign,kind): self.db.execute('DELETE FROM encounter_snapshots WHERE id=? AND campaign_id=? AND kind=?',(ident,campaign,kind))
    def clear_undo(self): self.db.execute("DELETE FROM encounter_snapshots WHERE kind='undo'")
    def list(self,campaign,kind): return [dict(r) for r in self.db.execute('SELECT id,name,created FROM encounter_snapshots WHERE campaign_id=? AND kind=? ORDER BY id DESC',(campaign,kind))]
    def latest_undo(self,campaign): return self.db.execute("SELECT * FROM encounter_snapshots WHERE campaign_id=? AND kind='undo' ORDER BY id DESC LIMIT 1",(campaign,)).fetchone()
