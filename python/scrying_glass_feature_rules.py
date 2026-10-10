"""Nonnegative HP, excess-damage death, zero-HP saves and effect validation."""
from .scrying_glass_turn_rules import permanently_dead,can_take_turn,is_character
from .scrying_glass_health_limits import MAX_STORED_HP, HpStorageRangeError
STATES={'standing','down','stable','dead'}

def validate_effects(effects):
    if not isinstance(effects,list) or len(effects)>100: raise ValueError('At most 100 effects are allowed')
    seen=set()
    for e in effects:
        if not isinstance(e,dict) or set(e)-{'id','name','source_id','notes','public','concentration','timing','turns','anchor_id'}: raise ValueError('Invalid effect object')
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
        elif not e.get('anchor_id') or type(turns) is not int or not 1<=turns<=10000: raise ValueError('Timed effects require anchor and positive counter')

def normalize_features(item):
    if type(item.get('hp',0)) is not int or type(item.get('max_hp',0)) is not int: raise ValueError('HP and maximum HP must be integers')
    # Historical negatives are normalized, not reinterpreted as damage events.
    item['hp']=max(0,item.get('hp',0));item['max_hp']=max(0,item.get('max_hp',0))
    if 'original_hp' in item and type(item['original_hp']) is int: item['original_hp']=max(0,item['original_hp'])
    if 'life_state' not in item: item['life_state']='standing' if item['hp']>0 and item.get('alive',True) else ('dead' if item['hp']>0 else 'down')
    state=item['life_state']
    if not isinstance(state,str) or state not in STATES: raise ValueError('Invalid life state')
    for k,limit in (('temp_hp',99999),('death_successes',3),('death_failures',3)):
        item.setdefault(k,0)
        if type(item[k]) is not int or not 0<=item[k]<=limit: raise ValueError('Invalid '+k)
    if permanently_dead(item): item['life_state']='dead';item['hp']=0
    elif item['hp']>0:
        item['life_state']='standing';item['death_successes']=item['death_failures']=0
    elif state=='standing': item['life_state']='down'
    if item['life_state']=='stable': item['death_successes']=item['death_failures']=0
    item.setdefault('concentrating',False)
    if type(item['concentrating']) is not bool: raise ValueError('Invalid concentrating flag')
    item.setdefault('effects',[]);validate_effects(item['effects'])
    item['alive']=item['life_state']=='standing'
    if not can_take_turn(item): item['in_turn']=False
    return item

def sync_health(item):
    normalize_features(item)
    if not item['alive']: item['visible']=True

def apply_hp(item,delta,*,absorb=True,critical=False):
    """Apply one damage/healing event; never retain or accumulate negative HP."""
    if type(delta) is not int or type(critical) is not bool: raise ValueError('Invalid HP change/critical flag')
    normalize_features(item)
    before=item['hp'];temporary=item['temp_hp'];old_failures=item['death_failures']
    result={'damage':0,'excess':0,'instant_death':False,'failed_saves':0,'temp_consumed':0}
    if permanently_dead(item): return result
    if delta>=0:
        if item['hp'] + delta > MAX_STORED_HP:
            raise HpStorageRangeError(f"Resulting HP must not exceed {MAX_STORED_HP}")
        if delta: item['hp']+=delta;item['life_state']='standing';item['death_successes']=item['death_failures']=0
        sync_health(item);return result
    damage=-delta
    consumed=min(temporary,damage) if absorb else 0
    item['temp_hp']-=consumed;damage-=consumed
    result.update(damage=damage,temp_consumed=consumed)
    if not damage and not (before==0 and is_character(item)): return result
    item['hp']=max(0,before-damage)
    if is_character(item):
        excess=max(0,damage-before);result['excess']=excess
        if item['hp']==0 and excess>0 and excess>=item['max_hp']:
            item['life_state']='dead';result['instant_death']=True
        elif before==0:
            if item['life_state']=='stable': item['death_successes']=item['death_failures']=0
            previous=item['death_failures']
            item['death_failures']=min(3,previous+(2 if critical else 1))
            result['failed_saves']=item['death_failures']-previous
            item['life_state']='dead' if item['death_failures']>=3 else 'down'
        elif item['hp']==0: item['life_state']='down'
    elif item['hp']==0: item['life_state']='dead'
    sync_health(item)
    return result

def public_features(item):
    return {'life_state':item.get('life_state','standing' if item.get('alive',True) else 'down'),'effects':[{'name':e['name']} for e in item.get('effects',[]) if e.get('public')]}
