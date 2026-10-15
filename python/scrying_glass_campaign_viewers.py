"""Campaign-scoped viewer authorization and player-safe snapshots."""
import copy
from types import SimpleNamespace
from .scrying_glass_service_state import StateService

SCHEMA = """CREATE TABLE campaign_viewers (
 campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
 user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 PRIMARY KEY(campaign_id,user_id))"""

class CampaignViewers:
    def __init__(self, context): self.context = context
    @property
    def db(self): return self.context.STORAGE.connection
    def initialize(self):
        storage = self.context.STORAGE
        if getattr(storage, '_campaign_viewers_ready', False): return
        if not self.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='campaign_viewers'").fetchone():
            if storage.migration_backup is None: storage._backup()
            with storage.transaction():
                self.db.execute(SCHEMA)
                self.db.execute('CREATE INDEX campaign_viewers_user ON campaign_viewers(user_id)')
                self.db.execute("""CREATE TRIGGER remove_nonclient_viewer_grants AFTER UPDATE OF role ON users
 WHEN NEW.role <> 'client' BEGIN DELETE FROM campaign_viewers WHERE user_id=NEW.id; END""")
        storage._campaign_viewers_ready = True
    def campaign(self, ident):
        if not isinstance(ident, str) or len(ident)>19 or not ident.isascii() or not ident.isdecimal() or not 0<int(ident)<=2**63-1:
            raise self.context.HTTPException(404, 'Campaign not found')
        row = self.db.execute('SELECT id,name FROM campaigns WHERE id=?', (int(ident),)).fetchone()
        if row is None: raise self.context.HTTPException(404, 'Campaign not found')
        return {'id':str(row['id']), 'name':row['name']}
    def grants(self, campaign_id):
        self.campaign(campaign_id)
        selected = {r[0] for r in self.db.execute('SELECT user_id FROM campaign_viewers WHERE campaign_id=?', (int(campaign_id),))}
        return {'campaign':self.campaign(campaign_id), 'users':[
            {'id':str(r['id']), 'username':r['username'], 'granted':r['id'] in selected}
            for r in self.db.execute("SELECT id,username FROM users WHERE role='client' ORDER BY username COLLATE NOCASE,id")]}
    def replace(self, campaign_id, body):
        self.campaign(campaign_id)
        ids = body.get('user_ids') if isinstance(body, dict) else None
        if not isinstance(body,dict) or set(body)!={'user_ids'} or not isinstance(ids,list) or len(ids)>500:
            raise self.context.HTTPException(422,'Expected user_ids list (at most 500 client users)')
        values=[]
        for value in ids:
            if not isinstance(value,str) or len(value)>19 or not value.isascii() or not value.isdecimal() or not 0<int(value)<=2**63-1:
                raise self.context.HTTPException(422,'User IDs must be positive integer strings')
            ident=int(value);row=self.db.execute('SELECT role FROM users WHERE id=?',(ident,)).fetchone()
            if row is None or row['role']!='client':
                raise self.context.HTTPException(422,'Viewer grants can only reference existing client-role users')
            if ident not in values: values.append(ident)
        with self.context.STORAGE.transaction():
            self.db.execute('DELETE FROM campaign_viewers WHERE campaign_id=?',(int(campaign_id),))
            self.db.executemany('INSERT INTO campaign_viewers(campaign_id,user_id) VALUES (?,?)',[(int(campaign_id),value) for value in values])
        return self.grants(campaign_id)
    def choices(self, session):
        user=self.context.user(session.get('username'))
        if not user or user['role']!=session.get('role'): raise self.context.HTTPException(401,'Sign in required')
        if user['role'] in {'admin','superadmin'}:
            rows=self.db.execute('SELECT id,name FROM campaigns ORDER BY name COLLATE NOCASE,id')
        else:
            rows=self.db.execute("""SELECT c.id,c.name FROM campaigns c JOIN campaign_viewers v ON v.campaign_id=c.id
 WHERE v.user_id=? ORDER BY c.name COLLATE NOCASE,c.id""",(user['id'],))
        return [{'id':str(row['id']),'name':row['name']} for row in rows]
    @staticmethod
    def empty():
        return {'campaign':None,'characters':[],'monsters':[],'lairs':[], 'battle_order':[],'display_order':[],'battle_round':0,
                'display':{'background':'#080b14','battle_order_font_size':16,'entry_direction':'from_bottom','exit_direction':'to_bottom','monster_width_percent':20}}
    def state(self, token, selected=None, *, forgiving=False):
        session=self.context.auth_session(token)
        if not session:
            if not forgiving: raise self.context.HTTPException(401,'Sign in required')
            return {**self.empty(),'viewer_campaigns':[],'viewer_auth_required':True}
        choices=self.choices(session);permitted={row['id'] for row in choices}
        denied=selected is not None and selected not in permitted
        if denied and not forgiving: raise self.context.HTTPException(403,'You do not have viewer access to this campaign')
        if denied: selected=None
        elif selected is None and len(choices)==1: selected=choices[0]['id']
        result=self.empty()
        if selected is not None:
            self.campaign(selected)
            if str(self.context.active_campaign())==selected:
                result=copy.deepcopy(self.context.display_state());result['viewer_source']='live'
            else:
                name=self.context.pick_campaign_setup(selected)
                state=self.context.normalize_state({'characters':self.context.load_campaign_characters(selected)}) if name is None else self.context.load_setup_state(name,selected)
                proxy=SimpleNamespace(**vars(self.context));proxy.STATE=state;proxy.active_campaign=lambda:selected
                projection=StateService(proxy);proxy.public_state=projection.public_state
                result=projection.display_state();result['viewer_source']='saved'
            result['campaign']=next(row for row in choices if row['id']==selected)
        result['viewer_campaigns']=choices
        result['viewer_selection_required']=selected is None and bool(choices)
        result['viewer_access_message']=('Viewer access was removed. Select another campaign.' if denied else
            'No campaign access has been granted. Ask an administrator.' if not choices else '')
        return result
    def socket_state(self, websocket):
        return self.state(websocket.cookies.get(self.context.CLIENT_SESSION_COOKIE,''),websocket.query_params.get('campaign_id'),forgiving=True)

def viewers(context):
    value=getattr(context,'campaign_viewers',None)
    if value is None: value=CampaignViewers(context);context.campaign_viewers=value
    return value
