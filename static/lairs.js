(() => {
    'use strict';
    const $=id=>document.getElementById(id);
    let state=null,editingId=null,actorId=null,revision=null,busy=false,opening=false,actionState=null;
    const configFields=['lairName','lairColor','lairActive','lairVisible','lairNotes'];
    const notice=text=>{$('lairNotice').textContent=text;};
    async function api(url,method='GET',body) {
        const options={method,cache:'no-store'};
        if(body!==undefined){options.headers={'Content-Type':'application/json'};options.body=JSON.stringify(body);}
        const response=await fetch(url,options);
        if(!response.ok){const data=await response.json().catch(()=>({}));throw new Error(typeof data.detail==='string'?data.detail:`Request failed (${response.status})`);}
        return response.json();
    }
    function setConfig(item) {
        const values={lairName:item?.name||'Lair',lairColor:item?.color||'#8064a2',lairActive:item?.active??true,lairVisible:item?.visible??true,lairNotes:item?.notes||''};
        for(const [id,value] of Object.entries(values))if(typeof value==='boolean')$(id).checked=value;else $(id).value=value;
        configFields.forEach(id=>delete $(id).dataset.dirty);
    }
    window.scryingLairsRender=snapshot=>{
        state=snapshot;const item=state.lairs?.[0];
        if((item?.id||null)!==editingId||!configFields.some(id=>$(id).dataset.dirty))setConfig(item);
        editingId=item?.id||null;$('saveLair').textContent=item?'Save lair':'Add lair';$('removeLair').hidden=!item;
        $('resolveLair').disabled=busy||!item?.active||!item?.in_turn;
    };
    configFields.forEach(id=>$(id).addEventListener('input',()=>{$(id).dataset.dirty='1';}));
    async function perform(action) {
        if(busy)return;busy=true;
        const controls=['saveLair','removeLair','resolveLair','applyLairAction'];controls.forEach(id=>$(id).disabled=true);
        try{await action();await load();}
        catch(error){notice(error.message);$('lairActionNotice').textContent=error.message;}
        finally{busy=false;controls.forEach(id=>$(id).disabled=false);$('resolveLair').disabled=!state?.lairs?.[0]?.in_turn;}
    }
    $('lairConfigForm').onsubmit=event=>{
        event.preventDefault();perform(async()=>{
            const body={name:$('lairName').value,color:$('lairColor').value,active:$('lairActive').checked,visible:$('lairVisible').checked,notes:$('lairNotes').value};
            await api(editingId?`/api/lairs/${encodeURIComponent(editingId)}`:'/api/lairs',editingId?'PATCH':'POST',body);
            configFields.forEach(id=>delete $(id).dataset.dirty);notice('Lair saved.');
        });
    };
    $('removeLair').onclick=()=>{
        if(editingId&&confirm('Remove this lair? Existing conditions remain; lair-anchored expiry becomes manual.'))
            perform(async()=>{await api(`/api/lairs/${encodeURIComponent(editingId)}`,'DELETE');notice('Lair removed.');});
    };
    function input(type,value,label) {
        const element=document.createElement('input');element.type=type;element.value=value;element.setAttribute('aria-label',label);return element;
    }
    window.scryingOpenLairAction=async ident=>{
        if(busy||opening)return;opening=true;
        try{
            const before=await api('/api/features');const snapshot=await api('/api/state');const after=await api('/api/features');
            if(before.revision!==after.revision)throw new Error('Encounter changed while opening targets; try again.');
            const item=snapshot.lairs?.find(x=>x.id===ident);
            if(!item?.active||!item?.in_turn)throw new Error('The lair is not currently taking its turn.');
            actionState=snapshot;actorId=ident;revision=after.revision;
            $('lairActionTitle').textContent=`Lair action: ${item.name}`;$('lairActionNotice').textContent='';$('lairTargets').replaceChildren();
            const targets=[...snapshot.characters,...snapshot.monsters].filter(x=>x.active&&x.life_state!=='dead'&&(x.death_failures||0)<3).sort((a,b)=>a.name.localeCompare(b.name));
            for(const target of targets){
                const row=document.createElement('tr');row.dataset.target=target.id;
                const check=input('checkbox','',`Select ${target.name}`);check.dataset.lairSelect='';
                const damage=input('number',$('lairDefaultDamage').value,`Damage to ${target.name}`);
                damage.min='0';damage.max='99999';damage.step='1';damage.dataset.lairDamage='';
                const conditions=input('text',$('lairDefaultConditions').value,`Conditions on ${target.name}`);conditions.maxLength=2000;conditions.dataset.lairConditions='';
                const label=`${target.name} (${target.monster_species?(target.ally?'ally monster':'monster'):'character'})`;
                for(const content of [check,label,`${target.hp}/${target.max_hp} + ${target.temp_hp||0} temp`,damage,conditions]){
                    const cell=document.createElement('td');if(typeof content==='string')cell.textContent=content;else cell.append(content);row.append(cell);
                }
                $('lairTargets').append(row);
            }
            $('lairActionModal').hidden=false;
        }catch(error){notice(error.message);}finally{opening=false;}
    };
    $('resolveLair').onclick=()=>window.scryingOpenLairAction(editingId);
    $('cancelLairAction').onclick=()=>{if(busy)return;$('lairActionModal').hidden=true;actorId=null;};
    for(const [id,selected] of [['lairSelectAll',true],['lairSelectNone',false]])
        $(id).onclick=()=>$('lairTargets').querySelectorAll('[data-lair-select]').forEach(x=>{x.checked=selected;});
    $('lairFillSelected').onclick=()=>{
        for(const row of $('lairTargets').rows)if(row.querySelector('[data-lair-select]').checked){
            row.querySelector('[data-lair-damage]').value=$('lairDefaultDamage').value;
            row.querySelector('[data-lair-conditions]').value=$('lairDefaultConditions').value;
        }
    };
    $('lairActionForm').onsubmit=event=>{
        event.preventDefault();perform(async()=>{
            const timing=$('lairConditionTiming').value,targets=[];
            for(const row of $('lairTargets').rows){
                if(!row.querySelector('[data-lair-select]').checked)continue;
                const id=row.dataset.target,damage=Number(row.querySelector('[data-lair-damage]').value);
                const names=row.querySelector('[data-lair-conditions]').value.split(',').map(x=>x.trim()).filter(Boolean);
                if(!Number.isInteger(damage)||damage<0||damage>99999)throw new Error('Enter integer damage from 0 to 99999.');
                const effects=[...new Set(names)].map(name=>({name,public:$('lairConditionsPublic').checked,
                    timing:timing==='manual'?'manual':timing==='lair-start'?'start':'end',turns:timing==='manual'?null:1,
                    anchor_id:timing==='manual'?null:timing==='lair-start'?actorId:id}));
                if(!damage&&!effects.length)throw new Error('Each selected target needs damage and/or a condition.');
                targets.push({id,damage,effects});
            }
            if(!targets.length)throw new Error('Select at least one target.');
            const descriptions=targets.map(row=>{
                const target=[...actionState.characters,...actionState.monsters].find(x=>x.id===row.id);
                return `${target.name}: ${row.damage} damage${row.effects.length?'; '+row.effects.map(x=>x.name).join(', '):''}`;
            });
            if(!confirm('Apply lair action?\n\n'+descriptions.join('\n')+'\n\nDamage uses existing temporary HP and death-state rules.'))return;
            const result=await api(`/api/lairs/${encodeURIComponent(actorId)}/actions`,'POST',{name:$('lairActionName').value,revision,targets});
            $('lairActionModal').hidden=true;actorId=null;notice(`Applied lair action to ${result.applied} target(s).`);
        });
    };
    if(typeof latest!=='undefined'&&latest)window.scryingLairsRender(latest);
})();
