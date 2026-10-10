(() => {
    'use strict';
    const $=id=>document.getElementById(id);
    let state=null,summary=null,busy=false,polling=false;
    const editable=['featureTempHp','featureLifeState','deathSuccesses','deathFailures'];
    const notice=text=>{$('featureNotice').textContent=text;};
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
    function draw(force=false) {
        const item=target();if(!item){$('featureHealth').textContent='No combatants';$('featureEffects').replaceChildren();return;}
        $('featureHealth').textContent=`${item.name}: ${item.life_state||'standing'} · HP ${item.hp}/${item.max_hp} · Temporary HP ${item.temp_hp||0} · Death saves ${item.death_successes||0}/${item.death_failures||0}${item.concentrating?' · Concentrating':''}`;
        const values={featureTempHp:item.temp_hp||0,featureLifeState:item.life_state||'standing',deathSuccesses:item.death_successes||0,deathFailures:item.death_failures||0};
        for(const [id,value]of Object.entries(values))if(force||($(id)!==document.activeElement&&!$(id).dataset.dirty))$(id).value=value;
        $('featureEffects').replaceChildren(...(item.effects||[]).map(e=>{
            const li=document.createElement('li'),label=document.createElement('span'),remove=document.createElement('button');
            const participants=[...combatants(),...(state?.lairs||[])];
            const source=participants.find(x=>x.id===e.source_id),anchor=participants.find(x=>x.id===e.anchor_id);
            label.textContent=`${e.name} [${e.public?'public':'private'}]${source?' — '+source.name:''}${e.concentration?' · concentration':''}${e.timing!=='manual'?` · ${e.turns} × ${e.timing} of ${anchor?.name||'missing anchor'} turn`:''}${e.notes?' · '+e.notes:''} `;
            remove.type='button';remove.textContent='Remove';remove.onclick=()=>perform(()=>api(`/api/combatants/${encodeURIComponent(item.id)}/effects/${encodeURIComponent(e.id)}`,'DELETE'));
            li.append(label,remove);return li;
        }));
    }
    async function refresh(force=false) {
        if(polling)return;polling=true;
        try {
            [state,summary]=await Promise.all([api('/api/state'),api('/api/features')]);
            choices($('featureTarget'),combatants());choices($('effectSource'),[...combatants(),...(state?.lairs||[])],true);choices($('effectAnchor'),[...combatants(),...(state?.lairs||[])],true);
            choices($('checkpointSelect'),summary.checkpoints.map(x=>({...x,name:x.name+' — '+new Date(x.created*1000).toLocaleString()})));
            $('featureUndo').disabled=!summary.undo||busy;$('featureUndo').textContent=summary.undo?'Undo: '+summary.undo.label:'Nothing to undo';
            $('displayConnections').textContent=`${summary.displays.length} display(s) connected${summary.displays.length?': '+summary.displays.map(x=>x.username+' ('+x.status+')').join(', '):''}`;
            $('downedReminder').hidden=!summary.downed.length;
            $('downedReminder').textContent='Death-save reminder: '+summary.downed.map(x=>x.name).join(', ')+'. Downed characters keep their initiative turns. Damage at 0 HP adds failed saves automatically; record rolled saves manually.';
            draw(force);
        }catch(error){notice(error.message);}finally{polling=false;}
    }
    async function perform(action) {
        if(busy)return;busy=true;
        try{await action();notice('Saved.');editable.forEach(id=>delete $(id).dataset.dirty);await refresh(true);if(typeof load==='function')await load();}
        catch(error){notice(error.message);}finally{busy=false;if(summary)$('featureUndo').disabled=!summary.undo;}
    }
    function edit(body){const item=target();if(!item)throw new Error('Select a combatant');return api(`/api/combatants/${encodeURIComponent(item.id)}/features`,'PATCH',body);}
    editable.forEach(id=>$(id).addEventListener('input',()=>{$(id).dataset.dirty='1';}));
    $('featureTarget').onchange=()=>{editable.forEach(id=>delete $(id).dataset.dirty);draw(true);};
    $('featureRefresh').onclick=()=>refresh(true);
    $('featureUndo').onclick=()=>perform(()=>api('/api/battle/undo','POST',{id:summary.undo?.id}));
    $('setTempHp').onclick=()=>perform(()=>edit({temp_hp:Number($('featureTempHp').value)}));
    $('setLifeState').onclick=()=>perform(async()=>{const value=$('featureLifeState').value;if(value!=='dead'||confirm('Mark this combatant dead?'))await edit({life_state:value});});
    $('setDeathSaves').onclick=()=>perform(()=>edit({death_successes:Number($('deathSuccesses').value),death_failures:Number($('deathFailures').value)}));
    $('startConcentration').onclick=()=>perform(()=>edit({concentrating:true}));
    $('endConcentration').onclick=()=>perform(()=>{const item=target();if(!item)throw new Error('Select a combatant');return api(`/api/combatants/${encodeURIComponent(item.id)}/concentration/end`,'POST');});
    $('applyFeatureHp').onclick=()=>perform(async()=>{
        const item=target();if(!item)throw new Error('Select a combatant');const delta=Number($('featureHpDelta').value),absorb=$('featureAbsorbTemp').checked;
        if(!Number.isInteger(delta))throw new Error('HP change must be an integer');
        if(confirm(window.scryingDamagePreview(item,delta,absorb)))await edit({hp_delta:delta,absorb_temp:absorb});
    });
    $('effectForm').onsubmit=event=>{event.preventDefault();perform(async()=>{
        const item=target();if(!item)throw new Error('Select a combatant');const timing=$('effectTiming').value;
        await api(`/api/combatants/${encodeURIComponent(item.id)}/effects`,'POST',{name:$('effectName').value,source_id:$('effectSource').value||null,notes:$('effectNotes').value,public:$('effectPublic').checked,concentration:$('effectConcentration').checked,timing,anchor_id:timing==='manual'?null:$('effectAnchor').value||null,turns:timing==='manual'?null:Number($('effectTurns').value)});
        $('effectName').value='';$('effectNotes').value='';
    });};
    $('saveCheckpoint').onclick=()=>perform(()=>api('/api/checkpoints','POST',{name:$('checkpointName').value||'Encounter checkpoint'}));
    $('restoreCheckpoint').onclick=()=>perform(async()=>{
        const id=$('checkpointSelect').value;if(!id)throw new Error('Select a checkpoint');const p=await api(`/api/checkpoints/${id}`);
        if(confirm(`Restore checkpoint?\nRound ${p.battle_round}; ${p.monsters} monsters; ${p.characters} characters.\nSetup: ${p.active_setup?.name||'None'}\nCurrent HP, effects, roster and turn state will be replaced. Audit history is retained.`))await api(`/api/checkpoints/${id}/restore`,'POST',{confirm:true,revision:p.revision});
    });
    $('deleteCheckpoint').onclick=()=>perform(async()=>{const id=$('checkpointSelect').value;if(!id)throw new Error('Select a checkpoint');if(confirm('Permanently delete checkpoint?'))await api(`/api/checkpoints/${id}`,'DELETE');});
    $('exportBundle').onclick=()=>{location.href='/api/campaign-bundle';};
    $('importBundle').onchange=()=>perform(async()=>{
        const file=$('importBundle').files[0];if(!file||!confirm('Import as a NEW campaign, leaving the active campaign unchanged?'))return;
        const body=new FormData();body.append('file',file);const result=await api('/api/campaign-bundle','POST',body);
        alert(`Imported ${result.name}. Switch campaigns, then restore the "Imported encounter" checkpoint to resume its runtime state.`);
        if(typeof setups==='function')await setups();$('importBundle').value='';
    });
    refresh();setInterval(()=>{if(!busy)refresh();},3000);
})();
