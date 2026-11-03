"""Campaign, roster, setup and application-state operations; staged, not wired."""
import time
from .scrying_glass_identity_rules import validate_roster_setup_ids


class StorageOperationsMixin:
    """Use the facade's record helpers and existing transaction boundaries."""

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
            validate_roster_setup_ids(
                self.load_characters(target) or [], {result: snapshot},
                label="Destination roster",
            )
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
