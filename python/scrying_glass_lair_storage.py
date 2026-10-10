"""Schema v6: typed encounter-owned lairs, including recovery snapshots."""
from .scrying_glass_lair_rules import normalize_lairs
SCHEMA = """CREATE TABLE IF NOT EXISTS lairs (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 encounter_id INTEGER NOT NULL UNIQUE REFERENCES encounters(id) ON DELETE CASCADE,
 participant_id TEXT NOT NULL, name TEXT NOT NULL, notes TEXT NOT NULL DEFAULT '', color TEXT NOT NULL,
 active INTEGER NOT NULL CHECK(active IN (0,1)), visible INTEGER NOT NULL CHECK(visible IN (0,1)),
 in_turn INTEGER NOT NULL CHECK(in_turn IN (0,1)), UNIQUE(encounter_id,participant_id))"""

def upgrade_lairs(storage,*,backup=True):
    if storage.connection.execute('PRAGMA user_version').fetchone()[0]==6:return
    if backup and storage.migration_backup is None:storage._backup()
    with storage.transaction():
        storage.connection.execute(SCHEMA)
        storage.connection.execute('PRAGMA user_version=6')

def save_lairs(storage,encounter,raw):
    items=normalize_lairs(raw);db=storage.connection
    if not items:
        db.execute('DELETE FROM lairs WHERE encounter_id=?',(encounter,));return
    item=items[0]
    db.execute('DELETE FROM lairs WHERE encounter_id=? AND participant_id<>?',(encounter,item['id']))
    db.execute("""INSERT INTO lairs(encounter_id,participant_id,name,notes,color,active,visible,in_turn)
 VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(encounter_id,participant_id) DO UPDATE SET
 name=excluded.name,notes=excluded.notes,color=excluded.color,active=excluded.active,
 visible=excluded.visible,in_turn=excluded.in_turn""",(encounter,item['id'],item['name'],item['notes'],
 item['color'],int(item['active']),int(item['visible']),int(item['in_turn'])))

def load_lairs(storage,encounter):
    return [dict(id=r['participant_id'],kind='lair',initiative=20,name=r['name'],notes=r['notes'],color=r['color'],
 active=bool(r['active']),visible=bool(r['visible']),in_turn=bool(r['in_turn']))
 for r in storage.connection.execute('SELECT * FROM lairs WHERE encounter_id=?',(encounter,))]
