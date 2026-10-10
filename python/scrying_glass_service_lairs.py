"""Lair configuration and atomic mixed-target action resolution."""
import copy
import uuid
from .scrying_glass_lair_rules import normalize_lairs
from .scrying_glass_feature_rules import apply_hp,validate_effects
from .scrying_glass_turn_rules import permanently_dead

class LairService:
    def __init__(self,context):self.context=context
    def lair(self,ident):
        item=next((x for x in self.context.STATE.get('lairs',[]) if x['id']==ident),None)
        if item is None:raise self.context.HTTPException(404,'Lair not found')
        return item
    def validate(self,item):
        try:return normalize_lairs([item])[0]
        except ValueError as exc:raise self.context.HTTPException(422,str(exc)) from exc
    async def persist(self):await self.context.combatants_changed(monsters=True,characters=True)
    async def create_lair(self,body):
        if self.context.STATE.get('lairs'):raise self.context.HTTPException(409,'This encounter already has a lair')
        if not isinstance(body,dict) or set(body)-{'name','notes','color','active','visible'}:
            raise self.context.HTTPException(422,'Invalid lair creation fields')
        item=self.validate({'id':'lair-'+uuid.uuid4().hex,**body})
        self.context.STATE['lairs']=[item]
        self.context.insert_into_battle_order(item)
        self.context.clean_order()
        self.context.features.log('lair-created',note=item['name'])
        await self.persist();return item
    async def update_lair(self,ident,body):
        item=self.lair(ident)
        if not isinstance(body,dict) or not body or set(body)-{'name','notes','color','active','visible','in_turn'}:
            raise self.context.HTTPException(422,'Initiative is fixed at 20; invalid lair update fields')
        if 'in_turn' in body and type(body['in_turn']) is not bool:
            raise self.context.HTTPException(422, 'in_turn must be boolean')
        requested_turn = body.get('in_turn')
        if requested_turn is True and not body.get('active', item['active']):
            raise self.context.HTTPException(400, 'Only an active lair may have the battle turn')
        candidate={**item,**body}
        if not candidate['active']:candidate['in_turn']=False
        candidate=self.validate(candidate)
        self.context.remember_turn_successors();item.update(candidate)
        self.context.set_turn(item, requested_turn)
        self.context.clean_order();self.context.insert_into_battle_order(item);self.context.clean_order()
        self.context.features.log('lair-updated',note=item['name'])
        await self.persist();return item
    async def delete_lair(self,ident):
        item=self.lair(ident);self.context.remember_turn_successors()
        self.context.STATE['lairs']=[];self.context.clean_order()
        for target in self.context.entities():
            for effect in target.get('effects',[]):
                if effect.get('source_id')==ident:effect['source_id']=None
                if effect.get('anchor_id')==ident:effect.update(timing='manual',turns=None,anchor_id=None)
        self.context.features.log('lair-removed',note=item['name'])
        await self.persist();return {'removed':ident}
    async def apply_lair_action(self,ident,body):
        lair=self.lair(ident)
        if not lair['active'] or not lair['in_turn']:
            raise self.context.HTTPException(409,'Lair actions can only be resolved during the lair turn')
        if not isinstance(body,dict) or set(body)-{'name','targets','revision'}:
            raise self.context.HTTPException(422,'Invalid lair action')
        if type(body.get('revision')) is not int or body['revision']!=self.context.features.store.revision():
            raise self.context.HTTPException(409,'Encounter changed; reopen the lair action targets')
        name=body.get('name','Lair action');rows=body.get('targets')
        if not isinstance(name,str) or not 1<=len(name.strip())<=100:
            raise self.context.HTTPException(422,'Action name must be 1-100 characters')
        if not isinstance(rows,list) or not 1<=len(rows)<=100:
            raise self.context.HTTPException(422,'Select 1-100 targets')
        prepared=[];seen=set()
        for row in rows:
            if not isinstance(row,dict) or set(row)-{'id','damage','effects'}:
                raise self.context.HTTPException(422,'Invalid target row')
            target_id=row.get('id')
            if not isinstance(target_id,str) or target_id in seen:
                raise self.context.HTTPException(422,'Targets must have unique string IDs')
            seen.add(target_id)
            target=next((x for x in self.context.entities() if x['id']==target_id),None)
            if target is None or not target.get('active') or permanently_dead(target):
                raise self.context.HTTPException(422,'Targets must be active, non-dead characters or monsters')
            damage=row.get('damage',0);effects=row.get('effects',[])
            if type(damage) is not int or not 0<=damage<=99999:
                raise self.context.HTTPException(422,'Damage must be an integer from 0 to 99999')
            if not isinstance(effects,list) or len(effects)>20 or (damage==0 and not effects):
                raise self.context.HTTPException(422,'Each target needs damage and/or up to 20 conditions')
            candidate=copy.deepcopy(target);was_concentrating=bool(candidate.get('concentrating'))
            result=apply_hp(candidate,-damage) if damage else None;created=[]
            for spec in effects:
                if not isinstance(spec,dict) or set(spec)-{'name','notes','public','timing','turns','anchor_id'}:
                    raise self.context.HTTPException(422,'Invalid condition fields')
                effect=dict(id=uuid.uuid4().hex,name=spec.get('name'),notes=spec.get('notes',''),
                    public=spec.get('public',False),source_id=ident,concentration=False,
                    timing=spec.get('timing','manual'),turns=spec.get('turns'),anchor_id=spec.get('anchor_id'))
                try:validate_effects(candidate.get('effects',[])+created+[effect])
                except ValueError as exc:raise self.context.HTTPException(422,str(exc)) from exc
                if effect['timing']!='manual':
                    anchor=self.context.entity(effect['anchor_id'])
                    if anchor is None or not anchor.get('active'):
                        raise self.context.HTTPException(422,'Condition anchor must exist and be active')
                created.append(effect)
            candidate.setdefault('effects',[]).extend(created)
            prepared.append((target,candidate,damage,created,result,was_concentrating))
        self.context.remember_turn_successors()
        for target,candidate,damage,effects,result,was_concentrating in prepared:
            target.update(candidate)
            if damage:
                self.context.log_battle_action(lair,target,'damage',damage)
                # Keep the action name on the single authoritative damage row.
                self.context.STATE['activity_log'][-1]['note'] = name.strip()
                if was_concentrating:self.context.features.log('concentration-reminder',target,note='Resolve concentration manually')
                if result['instant_death']:self.context.features.log('instant-death',target,note='Excess damage reached maximum HP')
                elif result['failed_saves']:self.context.features.log('death-save-failure',target,result['failed_saves'],note='Lair damage at 0 HP')
            for effect in effects:self.context.features.log('effect-added',target,note=name+': '+effect['name'])
        self.context.clean_order();await self.persist()
        return {'applied':len(prepared)}
