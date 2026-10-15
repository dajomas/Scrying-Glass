"""One-time campaign ownership migration and request-scoped authorization."""
import copy
import inspect
from contextlib import contextmanager
from contextvars import ContextVar

_ACTOR = ContextVar('campaign_owner_actor', default=None)

def actor(context):
    value = _ACTOR.get()
    return value[1] if value is not None and value[0] is context else None

@contextmanager
def internal_campaign_access():
    token = _ACTOR.set(None)
    try:
        yield
    finally:
        _ACTOR.reset(token)

class CampaignOwnership:
    def __init__(self, context): self.context = context
    @property
    def db(self): return self.context.STORAGE.connection
    def initialize(self):
        storage = self.context.STORAGE
        if getattr(storage, '_campaign_ownership_ready', False): return
        exists = self.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='campaign_owners'").fetchone()
        if not exists:
            if storage.migration_backup is None: storage._backup()
            with storage.transaction():
                self.db.execute("""CREATE TABLE campaign_owners (
 campaign_id INTEGER PRIMARY KEY REFERENCES campaigns(id) ON DELETE CASCADE,
 owner_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL)""")
                self.db.execute('CREATE INDEX campaign_owners_user ON campaign_owners(owner_user_id)')
                admins = list(self.db.execute("SELECT id FROM users WHERE role='admin' ORDER BY id"))
                owner = admins[0]['id'] if len(admins) == 1 else None
                self.db.execute('INSERT INTO campaign_owners(campaign_id,owner_user_id) SELECT id,? FROM campaigns', (owner,))
                self.db.execute("""CREATE TRIGGER clear_ineligible_campaign_owner AFTER UPDATE OF role ON users
 WHEN NEW.role <> 'admin' BEGIN UPDATE campaign_owners SET owner_user_id=NULL WHERE owner_user_id=NEW.id; END""")
        storage._campaign_ownership_ready = True
    def owner(self, campaign_id):
        row = self.db.execute('SELECT owner_user_id FROM campaign_owners WHERE campaign_id=?', (campaign_id,)).fetchone()
        return str(row[0]) if row and row[0] is not None else None
    def allowed(self, campaign_id, user=None):
        user = actor(self.context) if user is None else user
        if user is None or user.get('role') == 'superadmin': return True
        return user.get('role') == 'admin' and self.owner(str(campaign_id)) == str(user['id'])
    def require(self, campaign_id, user=None):
        if not self.allowed(campaign_id, user):
            raise self.context.HTTPException(403, 'This campaign is not assigned to your admin account')
    def assign_created(self, campaign_id):
        user = actor(self.context)
        value = int(user['id']) if user and user['role'] == 'admin' else None
        self.db.execute('INSERT OR IGNORE INTO campaign_owners(campaign_id,owner_user_id) VALUES (?,?)', (campaign_id, value))
    def ids(self):
        return {str(row[0]) for row in self.db.execute('SELECT id FROM campaigns')}
    def catalog(self):
        return {'admins': [{'id':str(row['id']), 'username':row['username']}
                           for row in self.db.execute("SELECT id,username FROM users WHERE role='admin' ORDER BY username COLLATE NOCASE,id")],
                'campaigns': [{'id':str(row['id']), 'name':row['name'],
                    'owner_user_id':str(row['owner_user_id']) if row['owner_user_id'] is not None else None,
                    'owner_username':row['username']}
                    for row in self.db.execute("""SELECT c.id,c.name,o.owner_user_id,u.username FROM campaigns c
 LEFT JOIN campaign_owners o ON o.campaign_id=c.id LEFT JOIN users u ON u.id=o.owner_user_id
 ORDER BY c.name COLLATE NOCASE,c.id""")]}
    def reassign(self, campaign_id, body):
        if not isinstance(campaign_id,str) or len(campaign_id)>19 or not campaign_id.isascii() or not campaign_id.isdecimal() or not 0<int(campaign_id)<=2**63-1:
            raise self.context.HTTPException(404, 'Campaign not found')
        if not self.context.STORAGE.campaign_exists(campaign_id): raise self.context.HTTPException(404, 'Campaign not found')
        if not isinstance(body,dict) or set(body) != {'owner_user_id'}:
            raise self.context.HTTPException(422, 'Expected owner_user_id (admin ID or null)')
        value = body['owner_user_id']
        if value is not None:
            if not isinstance(value,str) or len(value)>19 or not value.isascii() or not value.isdecimal() or not 0<int(value)<=2**63-1:
                raise self.context.HTTPException(422, 'Owner must be an existing regular admin ID')
            row = self.db.execute('SELECT role FROM users WHERE id=?', (int(value),)).fetchone()
            if not row or row['role'] != 'admin': raise self.context.HTTPException(422, 'Owner must have the admin role')
            value = int(value)
        self.db.execute("""INSERT INTO campaign_owners(campaign_id,owner_user_id) VALUES (?,?)
 ON CONFLICT(campaign_id) DO UPDATE SET owner_user_id=excluded.owner_user_id""", (int(campaign_id),value))
        return {'campaign_id':str(int(campaign_id)), 'owner_user_id':str(value) if value is not None else None}

def ownership(context):
    value = getattr(context, 'campaign_ownership', None)
    if value is None: value = CampaignOwnership(context);context.campaign_ownership = value
    return value

def require_campaign_owner(context, campaign_id):
    if actor(context) is not None: ownership(context).require(campaign_id)

def assign_created_campaign(context, campaign_id):
    if actor(context) is not None: ownership(context).assign_created(campaign_id)

def campaign_payload(context, payload):
    user = actor(context)
    if user is None: return payload
    result = copy.deepcopy(payload)
    result['campaigns'] = [item for item in result.get('campaigns', []) if ownership(context).allowed(item['id'], user)]
    visible = {item['id'] for item in result['campaigns']}
    if result.get('active') not in visible: result['active'] = None
    if user['role'] == 'admin': result['moved'] = []
    for item in result['campaigns']: item['owner_user_id'] = ownership(context).owner(item['id'])
    result['ownership'] = {'assigned_count':len(result['campaigns']), 'active_accessible':result.get('active') is not None}
    return result

def admin_state(context, state):
    user = actor(context)
    if user is None or user['role'] == 'superadmin': return state
    try: active = context.active_campaign()
    except context.HTTPException: active = None
    if active is not None and ownership(context).allowed(active, user): return state
    return {'active_campaign_id':None,'active_setup':None,'monsters':[],'characters':[],
            'lairs':[],'has_lair':False,'battle_order':[],'battle_round':0,'activity_log':[],
            'display':{'background':'#080b14','battle_order_font_size':16,
                       'entry_direction':'from_bottom','exit_direction':'to_bottom','monster_width_percent':20}}

def authorize_request(context, handler, args, kwargs, request):
    user = actor(context)
    if user is None or user['role'] == 'superadmin': return
    name = handler.__name__
    if name in {'get_campaigns','create_campaign','admin_get_state','dndbeyond_monster_stats','import_bundle'}: return
    params = inspect.signature(handler).bind_partial(*args, **kwargs).arguments
    targets = []
    keys = {'campaign_id','campaign','from_campaign','move_to'}
    for key,value in params.items():
        if key in keys and value is not None and str(value).strip(): targets.append(str(value))
        data = value.model_dump(exclude_unset=True) if hasattr(value,'model_dump') else value if isinstance(value,dict) else {}
        for field in keys:
            if data.get(field) is not None and str(data[field]).strip(): targets.append(str(data[field]))
    for target in targets: ownership(context).require(target, user)
    path = getattr(getattr(request,'url',None),'path','')
    campaign_operation = path.startswith('/api/campaigns/') or name in {
        'update_campaign','delete_campaign','activate_campaign','add_setup_to_campaign','get_viewers','set_viewers'}
    if campaign_operation and targets: return
    ownership(context).require(context.active_campaign(), user)

@contextmanager
def ownership_request(context, session, handler, args, kwargs, request):
    user = None
    if session and session.get('role') in {'admin','superadmin'}:
        user = context.user(session['username'])
        if user is None or user['role'] != session['role']: raise context.HTTPException(401, 'Sign in required')
    token = _ACTOR.set((context,user) if user is not None else None)
    try:
        authorize_request(context, handler, args, kwargs, request)
        yield
    finally:
        _ACTOR.reset(token)
