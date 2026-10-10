"""Turn-only lairs are distinct from HP-bearing combatants."""
import copy
import re

FIELDS = {'id','kind','name','notes','color','initiative','active','visible','in_turn'}

def normalize_lairs(raw):
    if not isinstance(raw,list) or len(raw)>1:
        raise ValueError('An encounter supports zero or one lair')
    result=copy.deepcopy(raw)
    for item in result:
        if not isinstance(item,dict) or set(item)-FIELDS:
            raise ValueError('Invalid lair fields; lairs have no HP, AC or life state')
        for key,limit in (('id',100),('name',100),('notes',2000)):
            value=item.get(key,'' if key=='notes' else None)
            if not isinstance(value,str) or len(value)>limit or (key!='notes' and not value.strip()):
                raise ValueError('Invalid lair '+key)
            item[key]=value if key=='notes' else value.strip()
        item.setdefault('color','#8064a2')
        if not isinstance(item['color'],str) or not re.fullmatch(r'#[0-9a-fA-F]{6}',item['color']):
            raise ValueError('Lair color must be #RRGGBB')
        for key,default in (('active',True),('visible',True),('in_turn',False)):
            item.setdefault(key,default)
            if type(item[key]) is not bool:raise ValueError('Invalid lair '+key)
        if item.get('kind','lair')!='lair':raise ValueError('Invalid lair kind')
        item.update(kind='lair',initiative=20)
        if item['in_turn'] and not item['active']:raise ValueError('An inactive lair cannot take a turn')
    return result

def participants(context):
    return [*context.entities(),*context.STATE.get('lairs',[])]

def initiative_key(item):
    value=20 if item.get('kind')=='lair' else item.get('initiative')
    numeric=type(value) is int
    return (0 if numeric else 1,-value if numeric else 0,1 if item.get('kind')=='lair' else 0)

def place_lair(order,lookup):
    if not any(lookup(ident).get('kind')=='lair' for ident in order):return list(order)
    # Stable sorting preserves DM-selected creature ties and pins the lair at 20.
    return sorted(order,key=lambda ident:initiative_key(lookup(ident)))
