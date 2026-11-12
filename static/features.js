(() => {
    'use strict';
    const $=id=>document.getElementById(id);
    let state=null,summary=null,busy=false,polling=null;
    window.scryingEncounterToolsBusy=()=>busy;
    const editable=['featureTempHp','featureLifeState','deathSuccesses','deathFailures'];
    // featureNotice keeps background-poll status (Deliverable 2); operation outcomes use the
    // managed tools region (SG-TODO-009.7 Stage 3), encounter lane: a scope change clears them.
    const notice=text=>{$('featureNotice').textContent=text;};
    const feedback=()=>window.scryingAdminFeedback;
    function ticket(spec,suffix=''){
        const api=feedback();if(!api)return null;
        return api.begin({lane:spec.lane,region:spec.region||'tools',operation:spec.operation+suffix,
            target:spec.region==='global'?spec.target:JSON.stringify([spec.operation,spec.target]),label:spec.label});
    }
    const say=(t,severity,text)=>{if(t)feedback().publish(t,{severity,text});};
    let refreshError='';
    function connectionText(summary,state) {
        const campaign=state?.active_campaign_id??state?.active_setup?.campaign_id??null;
        if(summary.display_scope_available===false||!Array.isArray(summary.displays)||
            (summary.display_campaign_id!==undefined&&summary.display_campaign_id!==String(campaign??'')))
            return 'Connection status unavailable';
        return `${summary.displays.length} display(s) connected${summary.displays.length?': '+summary.displays.map(x=>x.username+' ('+x.status+')').join(', '):''}`;
    }
    async function api(url,method='GET',body) {
        const options={method,cache:'no-store'};
        if(body instanceof FormData) options.body=body;
        else if(body!==undefined) {options.headers={'Content-Type':'application/json'};options.body=JSON.stringify(body);}
        const response=await fetch(url,options);
        if(!response.ok) {
            let data;try {data=await response.json();} catch {data=null;}
            throw new Error(typeof data?.detail==='string'?data.detail:`Request failed (${response.status})`);
        }
        return response.json();
    }
    function choices(select,items,optional=false) {
        const previous=select.value,values=items.map(x=>[String(x.id),x.name]);
        if(optional) values.unshift(['','None']);
        const signature=JSON.stringify(values);if(select.dataset.choices===signature)return;
        select.replaceChildren(...values.map(([id,name])=>new Option(name,id)));select.dataset.choices=signature;
        if(values.some(([id])=>id===previous))select.value=previous;
    }
    const combatants=()=>[...(state?.characters||[]),...(state?.monsters||[])];
    const target=()=>combatants().find(x=>x.id===$('featureTarget').value);
    const encounterScope=()=>JSON.stringify([state?.active_campaign_id??state?.active_setup?.campaign_id??null,state?.active_setup?.name??null]);
    const targetScope=()=>JSON.stringify([encounterScope(),$('featureTarget').value]);
    const currentTurnId=()=>[...combatants(),...(state?.lairs||[])]
        .find(item=>item.active&&item.in_turn)?.id??null;
    function followCurrentTurn(previousTurnId,scopeChanged) {
        const turnId=currentTurnId();
        if((scopeChanged||turnId!==previousTurnId)&&
            combatants().some(item=>item.id===turnId)) {
            $('featureTarget').value=String(turnId);
        }
    }
    function draw(force=false) {
        const item=target();if(!item){$('featureHealth').textContent='No combatants';$('featureEffects').replaceChildren();return;}
        $('featureHealth').textContent=`${item.name}: ${item.life_state||'standing'} · HP ${item.hp}/${item.max_hp} · Temporary HP ${item.temp_hp||0} · Death saves ${item.death_successes||0}/${item.death_failures||0}${item.concentrating?' · Concentrating':''}`;
        const values={featureTempHp:item.temp_hp||0,featureLifeState:item.life_state||'standing',deathSuccesses:item.death_successes||0,deathFailures:item.death_failures||0};
        for(const [id,value]of Object.entries(values))if(force||($(id)!==document.activeElement&&!$(id).dataset.dirty))$(id).value=value;
        $('featureEffects').replaceChildren(...(item.effects||[]).filter(e=>!e.mechanical).map(e=>{
            const li=document.createElement('li'),label=document.createElement('span'),remove=document.createElement('button');
            const participants=[...combatants(),...(state?.lairs||[])];
            const source=participants.find(x=>x.id===e.source_id),anchor=participants.find(x=>x.id===e.anchor_id);
            label.textContent=`${e.name} [${e.public?'public':'private'}]${source?' — '+source.name:''}${e.concentration?' · concentration':''}${e.timing!=='manual'?` · ${e.turns} × ${e.timing} of ${anchor?.name||'missing anchor'} turn`:''}${e.notes?' · '+e.notes:''} `;
            remove.type='button';remove.textContent='Remove';remove.onclick=()=>perform({operation:'tools.effect.remove',label:'Remove effect',target:[item.id,e.id]},()=>api(`/api/combatants/${encodeURIComponent(item.id)}/effects/${encodeURIComponent(e.id)}`,'DELETE'));
            li.append(label,remove);return li;
        }));
    }
    async function refresh(force=false, fresh=false, discardDrafts=null, report=true) {
        if(polling&&!force&&!fresh){await polling;return;}
        while(polling)await polling;
        let finishPoll;
        polling=new Promise(resolve=>{finishPoll=resolve;});
        try {
            const previousScope=encounterScope();
            const previousTurnId=currentTurnId();
            [state,summary]=await Promise.all([api('/api/state'),api('/api/features')]);
            const scopeChanged=encounterScope()!==previousScope;
            const previousTarget=$('featureTarget').value;
            choices($('featureTarget'),combatants());
            followCurrentTurn(previousTurnId,scopeChanged);
            const targetChanged=$('featureTarget').value!==previousTarget||scopeChanged;
            if(targetChanged)editable.forEach(id=>delete $(id).dataset.dirty);
            choices($('effectSource'),[...combatants(),...(state?.lairs||[])],true);choices($('effectAnchor'),[...combatants(),...(state?.lairs||[])],true);
            choices($('checkpointSelect'),summary.checkpoints.map(x=>({...x,name:x.name+' — '+new Date(x.created*1000).toLocaleString()})));
            $('featureUndo').disabled=!summary.undo||busy;$('featureUndo').textContent=summary.undo?'Undo: '+summary.undo.label:'Nothing to undo';
            $('displayConnections').textContent=connectionText(summary,state);
            $('downedReminder').hidden=!summary.downed.length;
            $('downedReminder').textContent='Death-save reminder: '+summary.downed.map(x=>x.name).join(', ')+'. Downed characters keep their initiative turns. Damage at 0 HP adds failed saves automatically; record rolled saves manually.';
            if(discardDrafts&&targetScope()===discardDrafts.target){
                discardDrafts.values.forEach((value,id)=>{
                    if($(id).value===value)delete $(id).dataset.dirty;
                });
            }
            draw(force||targetChanged);
            return true;
        }catch(error){$('displayConnections').textContent='Connection status unavailable';refreshError=error.message;if(report)notice(error.message);return false;}finally{polling=null;finishPoll();}
    }
    /* spec: operation, label, target (identity), optional region/success(result)/after(result).
     * Validation and request errors persist on the operation/target; cancellation is silent and keeps
     * earlier errors; success expires; a failed refresh after success is a separate no-replay error. */
    async function perform(spec, action, savedFields=[]) {
        if(busy)return;busy=true;
        const submittedTarget=targetScope();
        const submittedValues=new Map(savedFields.map(id=>[id,$(id).value]));
        const own=ticket(spec),again=ticket({...spec,region:'tools',target:JSON.stringify(spec.target)},'.refresh');
        try{
            let result;
            try{result=await action();}catch(error){if(own)say(own,'error',error.message);else notice(error.message);return;}
            if(result===false)return;
            say(own,'success',spec.success?spec.success(result):'Saved.');
            const sameTarget=targetScope()===submittedTarget;
            savedFields.forEach(id=>{
                if(sameTarget&&$(id).value===submittedValues.get(id))
                    delete $(id).dataset.dirty;
            });
            const failures=[];
            try{await spec.after?.(result);}catch(error){failures.push(error.message);}
            if(!await refresh(false,true,null,false))failures.push(refreshError);
            if(typeof load==='function')try{await load(true);}catch(error){failures.push(error.message);}
            if(failures.length)say(again,'error',`${spec.label} completed, but refreshing the view failed: `+
                `${failures.join('; ')}. Reload the page; do not repeat it to retry the refresh.`);
            else if(again)feedback().resolve(again);
        }finally{busy=false;if(summary)$('featureUndo').disabled=!summary.undo;}
    }
    const selected=()=>$('featureTarget').value;
    function edit(body){const item=target();if(!item)throw new Error('Select a combatant');return api(`/api/combatants/${encodeURIComponent(item.id)}/features`,'PATCH',body);}
    editable.forEach(id=>$(id).addEventListener('input',()=>{$(id).dataset.dirty='1';}));
    $('featureTarget').onchange=()=>{editable.forEach(id=>delete $(id).dataset.dirty);draw(true);};
    $('featureRefresh').onclick=async()=>{
        const own=ticket({operation:'tools.refresh',label:'Refresh status',target:'status'});
        const ok=await refresh(false,true,{
            target:targetScope(),
            values:new Map(editable.map(id=>[id,$(id).value])),
        },!own);
        if(own){if(ok)feedback().resolve(own);else say(own,'error',refreshError);}
        return ok;
    };
    $('featureUndo').onclick=()=>perform({operation:'tools.undo',label:'Undo',target:'undo'},()=>api('/api/battle/undo','POST',{id:summary.undo?.id}),editable);
    $('setTempHp').onclick=()=>perform({operation:'tools.temp-hp',label:'Set temporary HP',target:selected()},()=>edit({temp_hp:Number($('featureTempHp').value)}),['featureTempHp']);
    $('setLifeState').onclick=()=>perform({operation:'tools.life-state',label:'Set life state',target:selected()},async()=>{const value=$('featureLifeState').value;if(value==='dead'&&!confirm('Mark this combatant dead?'))return false;return edit({life_state:value});},['featureLifeState']);
    $('setDeathSaves').onclick=()=>perform({operation:'tools.death-saves',label:'Set death saves',target:selected()},()=>edit({death_successes:Number($('deathSuccesses').value),death_failures:Number($('deathFailures').value)}),['deathSuccesses','deathFailures']);
    $('startConcentration').onclick=()=>perform({operation:'tools.concentration',label:'Start concentration',target:selected()},()=>edit({concentrating:true}));
    $('endConcentration').onclick=()=>perform({operation:'tools.concentration',label:'End concentration',target:selected()},()=>{const item=target();if(!item)throw new Error('Select a combatant');return api(`/api/combatants/${encodeURIComponent(item.id)}/concentration/end`,'POST');});
    $('applyFeatureHp').onclick=()=>perform({operation:'tools.hp',label:'Apply HP change',target:selected()},async()=>{
        const item=target();if(!item)throw new Error('Select a combatant');const delta=Number($('featureHpDelta').value),absorb=$('featureAbsorbTemp').checked;
        if(!Number.isInteger(delta))throw new Error('HP change must be an integer');
        if(!confirm(window.scryingDamagePreview(item,delta,absorb)))return false;
        return edit({hp_delta:delta,absorb_temp:absorb});
    });
    $('effectForm').onsubmit=event=>{event.preventDefault();perform({operation:'tools.effect.add',label:'Add effect',target:selected()},async()=>{
        const item=target();if(!item)throw new Error('Select a combatant');const timing=$('effectTiming').value;
        const submittedTarget=targetScope(),name=$('effectName').value,notes=$('effectNotes').value;
        await api(`/api/combatants/${encodeURIComponent(item.id)}/effects`,'POST',{name,source_id:$('effectSource').value||null,notes,public:$('effectPublic').checked,concentration:$('effectConcentration').checked,timing,anchor_id:timing==='manual'?null:$('effectAnchor').value||null,turns:timing==='manual'?null:Number($('effectTurns').value)});
        if(targetScope()===submittedTarget){
            if($('effectName').value===name)$('effectName').value='';
            if($('effectNotes').value===notes)$('effectNotes').value='';
        }
    });};
    $('saveCheckpoint').onclick=()=>perform({operation:'tools.checkpoint.save',label:'Save checkpoint',target:'checkpoint'},()=>api('/api/checkpoints','POST',{name:$('checkpointName').value||'Encounter checkpoint'}));
    $('restoreCheckpoint').onclick=()=>perform({lane:'page',operation:'tools.checkpoint.restore',label:'Restore checkpoint',target:$('checkpointSelect').value},async()=>{
        const id=$('checkpointSelect').value;if(!id)throw new Error('Select a checkpoint');const p=await api(`/api/checkpoints/${id}`);
        if(!confirm(`Restore checkpoint?\nRound ${p.battle_round}; ${p.monsters} monsters; ${p.characters} characters.\nSetup: ${p.active_setup?.name||'None'}\nCurrent HP, effects, roster and turn state will be replaced. Audit history is retained.`))return false;
        return api(`/api/checkpoints/${id}/restore`,'POST',{confirm:true,revision:p.revision});
    },editable);
    $('deleteCheckpoint').onclick=()=>perform({operation:'tools.checkpoint.delete',label:'Delete checkpoint',target:$('checkpointSelect').value},async()=>{const id=$('checkpointSelect').value;if(!id)throw new Error('Select a checkpoint');if(!confirm('Permanently delete checkpoint?'))return false;return api(`/api/checkpoints/${id}`,'DELETE');});
    $('exportBundle').onclick=()=>{location.href='/api/campaign-bundle';};
    // Success stays global (4A.13); a rejection is a persistent tools-region error with the same
    // operation/target identity, so the next successful import resolves it.
    $('importBundle').onchange=()=>{
        const file=$('importBundle').files[0];if(!file||!confirm('Import as a NEW campaign, leaving the active campaign unchanged?'))return;
        const spec={region:'global',operation:'campaign-bundle.import',target:'import',label:'Import campaign bundle',
            success:result=>`Imported ${result.name}. Switch campaigns, then restore the "Imported encounter" checkpoint to resume its runtime state.`,
            async after(){$('importBundle').value='';if(typeof setups==='function')await setups();}};
        return perform(spec,async()=>{
            const body=new FormData();body.append('file',file);
            try{return await api('/api/campaign-bundle','POST',body);}
            catch(error){const api=feedback();if(!api)throw error;
                api.publish(api.begin({region:'tools',operation:spec.operation,target:spec.target,label:spec.label}),{severity:'error',text:error.message});return false;}
        });
    };
    refresh();setInterval(()=>{if(!busy)refresh();},3000);
})();
