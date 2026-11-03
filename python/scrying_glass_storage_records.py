"""Typed records and encounters staged for the Storage split; not yet wired."""
import uuid
from .scrying_glass_storage_fields import (
    TEXT_FIELDS, INT_FIELDS, BOOL_FIELDS, ENTITY_FIELDS, LOG_FIELDS, LIST_FIELDS, STATE_FIELDS,
)


class StorageRecordsMixin:
    """Use the facade's connection and caller transaction boundaries at activation."""

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
        has_lair=state.get('has_lair',bool(state.get('lairs')))
        if type(has_lair) is not bool:raise ValueError("has_lair must be a boolean")
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
        if self.connection.execute("PRAGMA user_version").fetchone()[0] >= 7:
            self.connection.execute("UPDATE encounters SET has_lair=? WHERE id=?",(int(has_lair),encounter))
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
        result['has_lair'] = bool(row['has_lair']) if 'has_lair' in row.keys() else False
        from .scrying_glass_lair_storage import load_lairs
        result['lairs'] = load_lairs(self, encounter) if self.connection.execute('PRAGMA user_version').fetchone()[0] >= 6 else []
        for kind in LIST_FIELDS:
            result[kind]=[r[0] for r in self.connection.execute("SELECT combatant_id FROM ordered_combatants WHERE encounter_id=? AND list_kind=? ORDER BY position,id",(encounter,kind))]
        if row['has_active_turn_marker']:result['active_turn_id']=row['active_turn_id']
        return result

