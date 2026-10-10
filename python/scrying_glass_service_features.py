"""Encounter features: recovery, reminders, life states and display status."""
import copy
import hashlib
import json
import time
import uuid
from .scrying_glass_feature_rules import normalize_features,apply_hp,validate_effects
from .scrying_glass_feature_storage import FeatureStorage
from .scrying_glass_feature_logging import feature_changes
from .scrying_glass_turn_rules import can_take_turn

TRACKED={'update_monster','update_character','bulk_monsters','bulk_characters','reset_one_combatant','reset_all','battle_start','battle_next','battle_end','apply_battle_actions','edit_features','add_effect','remove_effect','end_concentration','restore_checkpoint','create_lair','update_lair','delete_lair','apply_lair_action'}
BOUNDARIES={'load_setup','new_setup','activate_campaign','delete_campaign','delete_setup','rename_setup','add_setup_to_campaign','clear_activity_log'}

def fingerprint(state):
    payload=copy.deepcopy(state);payload.pop('activity_log',None);payload.pop('active_turn_id',None)
    for item in payload.get('monsters',[])+payload.get('characters',[]): normalize_features(item)
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()

class FeaturesService:
    def __init__(self,context): self.context=context;self.displays={}
    @property
    def store(self): return FeatureStorage(self.context.STORAGE)
    def log(self,action,target=None,amount=None,note=''):
        actor=self.context.active_combatant()
        self.context.STATE.setdefault('activity_log',[]).append({'id':uuid.uuid4().hex,'timestamp':self.context.now_iso(),'active_combatant_id':actor['id'] if actor else None,'active_combatant':actor['name'] if actor else 'System','active_combatant_state':self.context.combatant_state(actor),'target_combatant_id':target['id'] if target else None,'target_combatant':target['name'] if target else 'Encounter','target_combatant_state':self.context.combatant_state(target),'action':action,'amount':amount,'note':note})
    def after_transaction(self,name,before,campaign_before):
        campaign=self.context.active_campaign();different=fingerprint(before)!=fingerprint(self.context.STATE)
        if name=='undo': self.store.bump();return
        if campaign!=campaign_before or name in BOUNDARIES: self.store.clear_undo()
        elif different:
            if name in TRACKED:
                label=name.replace('_',' ').capitalize()
                previous={x['id']:x for x in before.get('monsters',[])+before.get('characters',[])}
                if name in ('update_monster','update_character','edit_features'):
                    for x in self.context.entities():
                        old=previous.get(x['id'])
                        if old and (old.get('hp')!=x.get('hp') or old.get('temp_hp',0)!=x.get('temp_hp',0)):
                            label=f"{x['name']}: HP {old.get('hp')} → {x.get('hp')}; temporary HP {old.get('temp_hp',0)} → {x.get('temp_hp',0)}";break
                self.store.save_snapshot(campaign,before,'undo',label,fingerprint(self.context.STATE))
            else: self.store.clear_undo()
        if different or campaign!=campaign_before: self.store.bump()
    def summary(self):
        top=self.store.latest_undo(self.context.active_campaign());revision=self.store.revision();displays=[]
        for ws,data in list(self.displays.items()):
            if ws not in self.context.SOCKETS: self.displays.pop(ws,None);continue
            status='stale' if time.time()-data['seen']>35 else ('live' if data['revision']==revision else 'behind')
            displays.append({'username':data['username'],'revision':data['revision'],'last_seen':data['seen'],'status':status})
        return {'revision':revision,'undo':{'id':top['id'],'label':top['name']} if top and top['after_digest']==fingerprint(self.context.STATE) else None,'checkpoints':self.store.list(self.context.active_campaign(),'checkpoint'),'displays':displays,'downed':[{'id':x['id'],'name':x['name']} for x in self.context.STATE['characters'] if x.get('active') and x.get('life_state')=='down']}
    def target(self,ident):
        target=self.context.entity(ident)
        if target is None: raise self.context.HTTPException(404,'Combatant not found')
        if target.get('kind') == 'lair': raise self.context.HTTPException(400,'Lairs have no HP, conditions or concentration')
        normalize_features(target);return target
    async def persist(self): await self.context.combatants_changed(monsters=True,characters=True)
    def restore_state(self,state):
        ref=state.get('active_setup')
        if ref and (str(ref['campaign_id'])!=str(self.context.active_campaign()) or not self.context.STORAGE.setup_exists(ref['campaign_id'],ref['name'])):
            raise self.context.HTTPException(409,'Referenced setup no longer exists')
        try: candidate=self.context.normalize_state(state)
        except ValueError as exc: raise self.context.HTTPException(422,str(exc)) from exc
        candidate['activity_log']=copy.deepcopy(self.context.STATE.get('activity_log',[]))
        self.context.STATE=candidate
    async def undo(self,body):
        top=self.store.latest_undo(self.context.active_campaign())
        if not top: raise self.context.HTTPException(409,'Nothing to undo')
        if body.get('id')!=top['id'] or top['after_digest']!=fingerprint(self.context.STATE): raise self.context.HTTPException(409,'Encounter changed; refresh before undoing')
        self.restore_state(self.store.load(top['id'],self.context.active_campaign(),'undo'))
        self.store.delete(top['id'],self.context.active_campaign(),'undo');self.log('undo',note=top['name'])
        await self.persist();return {'undone':top['name']}
    async def edit_features(self,ident,body):
        allowed={'temp_hp','life_state','death_successes','death_failures','concentrating','hp_delta','absorb_temp'}
        if not isinstance(body,dict) or set(body)-allowed or not body: raise self.context.HTTPException(422,'Invalid feature fields')
        target=self.target(ident)
        before=copy.deepcopy(target)
        candidate=copy.deepcopy(target)
        delta=body.get('hp_delta')
        if delta is not None and (type(delta) is not int or not -99999<=delta<=99999): raise self.context.HTTPException(422,'Invalid HP delta')
        if 'absorb_temp' in body and type(body['absorb_temp']) is not bool: raise self.context.HTTPException(422,'absorb_temp must be boolean')
        if delta is not None: apply_hp(candidate,delta,absorb=body.get('absorb_temp',True))
        for key in allowed-{'hp_delta','absorb_temp'}:
            if key in body: candidate[key]=body[key]
        state=body.get('life_state')
        if state=='standing':
            candidate['hp']=max(candidate['hp'],1);candidate['death_successes']=candidate['death_failures']=0
        elif state in ('down','stable'): candidate['hp']=min(candidate['hp'],0)
        if 'death_successes' in body or 'death_failures' in body:
            if candidate.get('life_state') not in ('down','stable'): raise self.context.HTTPException(422,'Death-save counters require down/stable state')
            if candidate['death_failures']==3: candidate['life_state']='dead'
            elif candidate['death_successes']==3: candidate['life_state']='stable'
        try: normalize_features(candidate)
        except ValueError as exc: raise self.context.HTTPException(422,str(exc)) from exc
        if body.get('concentrating') is True and not candidate['alive']: raise self.context.HTTPException(422,'Only standing combatants may concentrate')
        self.context.remember_turn_successors();target.update(candidate)
        if not target['alive']: target['visible']=True
        if delta is not None and delta<0 and target.get('concentrating'): self.log('concentration-reminder',target,note='Resolve concentration manually')
        if not target['alive'] or ('concentrating' in body and not target['concentrating']): self.clear_concentration(ident)
        self.context.clean_order()
        if can_take_turn(target): self.context.insert_into_battle_order(target)
        for action,amount,note in feature_changes(before,target,delta):
            self.log(action,target,amount,note=note)
        await self.persist();return target
    async def add_effect(self,ident,body):
        if not isinstance(body,dict) or set(body)-{'name','source_id','notes','public','concentration','timing','turns','anchor_id'}: raise self.context.HTTPException(422,'Invalid effect fields')
        target=self.target(ident)
        effect={'id':uuid.uuid4().hex,'name':body.get('name'),'source_id':body.get('source_id'),'notes':body.get('notes',''),'public':body.get('public',False),'concentration':body.get('concentration',False),'timing':body.get('timing','manual'),'turns':body.get('turns'),'anchor_id':body.get('anchor_id')}
        try: validate_effects(target['effects']+[effect])
        except ValueError as exc: raise self.context.HTTPException(422,str(exc)) from exc
        for key in ('source_id','anchor_id'):
            if effect[key] and self.context.entity(effect[key]) is None: raise self.context.HTTPException(422,'Effect source/anchor must exist')
        if effect['concentration']:
            source=self.target(effect['source_id'])
            if not source['alive']: raise self.context.HTTPException(422,'Concentration source must be standing')
            was_concentrating=source.get('concentrating',False)
            source['concentrating']=True
            if not was_concentrating:
                self.log('concentration-started',source,note='Concentration started for effect: '+effect['name'])
        target['effects'].append(effect);self.log('effect-added',target,note=effect['name'])
        await self.persist();return effect
    async def remove_effect(self,ident,effect_id):
        target=self.target(ident);effect=next((e for e in target['effects'] if e['id']==effect_id),None)
        if effect is None: raise self.context.HTTPException(404,'Effect not found')
        target['effects'].remove(effect);self.log('effect-removed',target,note=effect['name'])
        await self.persist();return {'removed':effect_id}
    def clear_concentration(self,source_id):
        source=self.context.entity(source_id)
        if source: source['concentrating']=False
        for item in self.context.entities(): item['effects']=[e for e in item.get('effects',[]) if not(e.get('concentration') and e.get('source_id')==source_id)]
    async def end_concentration(self,ident):
        target=self.target(ident)
        names=[e['name'] for x in self.context.entities() for e in x.get('effects',[]) if e.get('concentration') and e.get('source_id')==ident]
        self.clear_concentration(ident)
        note='Concentration ended'
        if names: note+='; removed linked effects: '+', '.join(dict.fromkeys(names))
        self.log('concentration-ended',target,note=note)
        await self.persist();return {'ended':ident}
    def expire(self,anchor_id,timing):
        if not anchor_id: return
        for item in self.context.entities():
            keep=[]
            for e in item.get('effects',[]):
                if e.get('timing')==timing and e.get('anchor_id')==anchor_id:
                    e['turns']-=1
                    if e['turns']<=0: self.log('effect-expired',item,note=e['name']);continue
                keep.append(e)
            item['effects']=keep
    def reconcile(self):
        ids={x['id'] for x in self.context.entities()}
        for item in self.context.entities():
            normalize_features(item)
            if item.get('concentrating') and not item['alive']: self.clear_concentration(item['id'])
            item['effects']=[e for e in item['effects'] if not(e.get('concentration') and e.get('source_id') not in ids)]
    async def save_checkpoint(self,body):
        name=body.get('name') if isinstance(body,dict) else None
        if not isinstance(name,str) or not 1<=len(name.strip())<=100: raise self.context.HTTPException(422,'Checkpoint name must be 1-100 characters')
        return {'id':self.store.save_snapshot(self.context.active_campaign(),self.context.STATE,'checkpoint',name.strip())}
    def preview_checkpoint(self,ident):
        try: state=self.store.load(ident,self.context.active_campaign(),'checkpoint')
        except ValueError as exc: raise self.context.HTTPException(404,str(exc)) from exc
        return {'id':ident,'revision':self.store.revision(),'battle_round':state['battle_round'],'monsters':len(state['monsters']),'characters':len(state['characters']),'active_setup':state['active_setup'],'combatants':[{'name':x['name'],'hp':x.get('hp'),'life_state':x.get('life_state')} for x in state['monsters']+state['characters']]}
    async def restore_checkpoint(self,ident,body):
        if body.get('confirm') is not True or body.get('revision')!=self.store.revision(): raise self.context.HTTPException(409,'Preview and confirm against current revision')
        try: state=self.store.load(ident,self.context.active_campaign(),'checkpoint')
        except ValueError as exc: raise self.context.HTTPException(404,str(exc)) from exc
        self.restore_state(state);self.log('checkpoint-restored',note=str(ident));await self.persist();return {'restored':ident}
    async def delete_checkpoint(self,ident):
        if not self.store.row(ident,self.context.active_campaign(),'checkpoint'): raise self.context.HTTPException(404,'Checkpoint not found')
        self.store.delete(ident,self.context.active_campaign(),'checkpoint');return {'deleted':ident}
    def export_bundle(self):
        from .scrying_glass_campaign_bundle import export_bundle
        return export_bundle(self.context)
    async def import_bundle(self,raw):
        from .scrying_glass_campaign_bundle import import_bundle
        return import_bundle(self.context,raw)
