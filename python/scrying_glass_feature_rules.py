"""Pure validation and HP operations for encounter features."""
STATES = {'standing', 'down', 'stable', 'dead'}

def validate_effects(effects):
    if not isinstance(effects,list) or len(effects)>100: raise ValueError('At most 100 effects are allowed')
    seen=set()
    for e in effects:
        if not isinstance(e,dict) or set(e)-{'id','name','source_id','notes','public','concentration','timing','turns','anchor_id'}:
            raise ValueError('Invalid effect object')
        for k,limit in (('id',100),('name',100),('notes',2000)):
            value=e.get(k,'' if k=='notes' else None)
            if not isinstance(value,str) or len(value)>limit or (k!='notes' and not value.strip()): raise ValueError('Invalid effect '+k)
        if e['id'] in seen: raise ValueError('Duplicate effect ID')
        seen.add(e['id'])
        for k in ('source_id','anchor_id'):
            if e.get(k) is not None and (not isinstance(e[k],str) or not 1<=len(e[k])<=100): raise ValueError('Invalid effect '+k)
        for k in ('public','concentration'):
            if type(e.get(k)) is not bool: raise ValueError('Invalid effect '+k)
        if e['concentration'] and not e.get('source_id'): raise ValueError('Concentration requires a source')
        if e.get('timing') not in ('manual','start','end'): raise ValueError('Invalid timing')
        turns=e.get('turns')
        if e['timing']=='manual':
            if turns is not None: raise ValueError('Manual effects cannot have a counter')
        elif not e.get('anchor_id') or type(turns) is not int or not 1<=turns<=10000:
            raise ValueError('Timed effects require an anchor and positive counter')

def normalize_features(item):
    if 'life_state' not in item:
        item['life_state']='standing' if item.get('hp',0)>0 and item.get('alive',True) else ('dead' if item.get('hp',0)>0 else 'down')
    state=item['life_state']
    if not isinstance(state,str) or state not in STATES: raise ValueError('Invalid life state')
    if state=='standing' and item.get('hp',0)<=0: raise ValueError('Standing requires positive HP')
    if state in ('down','stable') and item.get('hp',0)>0: raise ValueError('Down/stable requires nonpositive HP')
    for k,limit in (('temp_hp',99999),('death_successes',3),('death_failures',3)):
        item.setdefault(k,0)
        if type(item[k]) is not int or not 0<=item[k]<=limit: raise ValueError('Invalid '+k)
    item.setdefault('concentrating',False)
    if type(item['concentrating']) is not bool: raise ValueError('Invalid concentrating flag')
    item.setdefault('effects',[]);validate_effects(item['effects'])
    item['alive']=state=='standing'
    if not item['alive']: item['in_turn']=False
    return item

def sync_health(item):
    old=item.get('life_state')
    if old=='dead': item['alive']=False
    elif item.get('hp',0)>0:
        item['life_state']='standing';item['alive']=True
        item['death_successes']=item['death_failures']=0
    else:
        item['life_state']='stable' if old=='stable' else 'down';item['alive']=False
    if not item['alive']: item['visible']=True;item['in_turn']=False

def apply_hp(item,delta,*,absorb=True):
    if type(delta) is not int: raise ValueError('HP change must be an integer')
    normalize_features(item)
    if delta<0 and absorb:
        consumed=min(item['temp_hp'],-delta);item['temp_hp']-=consumed;delta+=consumed
    if delta<0 and item['life_state']=='stable': item['life_state']='down'
    item['hp']+=delta;sync_health(item)

def public_features(item):
    return {'life_state':item.get('life_state','standing' if item.get('alive',True) else 'down'),
            'effects':[{'name':e['name']} for e in item.get('effects',[]) if e.get('public')]}
