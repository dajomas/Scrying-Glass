(() => {
    'use strict';
    const $=id=>document.getElementById(id);
    const stats=[['max_hp','Max HP'],['strength','STR'],['dexterity','DEX'],['constitution','CON'],['intelligence','INT'],['wisdom','WIS'],['charisma','CHA']];
    let scope=null, target=null, snapshot=null, generation=0, busy=false, editingBases=false, returnFocus=null;
    const stateScope=s=>JSON.stringify([s.active_campaign_id,s.active_setup]);
    const notice=text=>{$('statisticsNotice').textContent=text;};
    const reduction=(item,stat)=>(item.effects||[]).filter(e=>e.mechanical?.version===1&&e.mechanical.stat===stat)
        .reduce((sum,e)=>sum+e.mechanical.amount,0);
    const affected=item=>stats.filter(([stat])=>reduction(item,stat)>0);
    const currentItem=()=>snapshot&&[...snapshot.characters,...snapshot.monsters].find(x=>x.id===target);
    async function api(url,body) {
        const options=body===undefined?{cache:'no-store'}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)};
        const response=await fetch(url,options), data=await response.json();
        if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:'Statistics request failed');
        return data;
    }
    function close() {
        if(busy)return;
        generation++;target=null;snapshot=null;editingBases=false;$('statisticsModal').hidden=true;
        returnFocus?.focus?.();
    }
    window.scryingStatisticsState=s=>{
        const next=stateScope(s);
        if(scope!==null&&next!==scope) {
            generation++;target=null;snapshot=null;editingBases=false;$('statisticsModal').hidden=true;
            if(typeof closeBattleActions==='function')closeBattleActions();
        }
        scope=next;
    };
    function textCell(tag,text) {
        const node=document.createElement(tag);node.textContent=text;return node;
    }
    function draw(item) {
        const reduced=affected(item), visible=editingBases?stats:reduced;
        $('statisticsTitle').textContent=(editingBases?'Original/base statistics: ':'Restore statistics: ')+item.name;
        $('statisticsHelp').textContent=editingBases
            ?'Enter known original/base scores. Blank ability scores mean unknown. Saving does not heal; active reductions remain in place.'
            :'Only statistics with active reductions are shown. Restoring removes reductions; it never heals current HP or revives a combatant.';
        $('statisticsSaveBases').hidden=!editingBases;
        $('statisticsRestoreControls').hidden=editingBases;
        $('statisticsEditBases').hidden=editingBases;
        $('statisticsBack').hidden=!editingBases;
        $('statisticsFields').replaceChildren();
        if(!visible.length) {
            const empty=textCell('p','No statistic reductions to restore.');empty.className='statistics-empty';
            $('statisticsFields').append(empty);
        } else {
            const table=document.createElement('table'), head=document.createElement('thead'), header=document.createElement('tr'), body=document.createElement('tbody');
            table.append(textCell('caption',editingBases?'Original/base score editor':'Affected statistics'));
            for(const title of ['Statistic','Original/base','Reduction','Effective']) {
                const th=textCell('th',title);th.scope='col';header.append(th);
            }
            head.append(header);table.append(head);
            visible.forEach(([stat,label])=>{
                const row=document.createElement('tr'), name=textCell('th',label), original=document.createElement('td');name.scope='row';row.dataset.stat=stat;
                const base=item['base_'+stat]??(stat==='max_hp'?item.max_hp:null);
                if(editingBases) {
                    const input=document.createElement('input');input.type='number';input.min='0';input.max=stat==='max_hp'?String(Number.MAX_SAFE_INTEGER):'30';input.step='1';input.dataset.baseStat=stat;input.value=base??'';
                    input.setAttribute('aria-label',label+' original/base value');
                    if(stat==='max_hp')input.required=true;original.append(input);
                } else original.textContent=base??'Unknown';
                row.append(name,original,textCell('td',String(reduction(item,stat))),textCell('td',item[stat]??'Unknown'));body.append(row);
            });
            table.append(body);$('statisticsFields').append(table);
        }
        const previous=$('statisticsRestoreStat').value, select=$('statisticsRestoreStat');
        select.replaceChildren();
        const choices=reduced.length>1?[['all','All affected statistics'],...reduced]:reduced;
        choices.forEach(([value,label])=>{const option=textCell('option',label);option.value=value;select.append(option);});
        select.value=choices.some(([value])=>value===previous)?previous:(choices[0]?.[0]||'');
        select.disabled=!reduced.length;$('statisticsRestore').disabled=!reduced.length;
    }
    async function open(id,button) {
        if(busy)return;
        const ticket=++generation;
        const feedback=window.scryingAdminFeedback;
        const attempt=feedback.begin({region:'global',operation:'statistics.open',
            target:String(id),label:'Open combatant statistics'});
        const owns=()=>ticket===generation&&feedback.isCurrent(attempt);
        try {
            const state=await api('/api/state');if(!owns())return;
            const item=[...state.characters,...state.monsters].find(x=>x.id===id);
            if(!item)throw new Error('Combatant no longer exists');
            window.scryingStatisticsState(state);
            if(!feedback.isCurrent(attempt))return;
            target=id;snapshot=state;editingBases=false;returnFocus=button;draw(item);notice('');$('statisticsModal').hidden=false;
            $('statisticsModal').querySelector('[role="dialog"]')?.focus?.();
            feedback.resolve(attempt);
        }catch(error){if(owns())feedback.publish(attempt,{severity:'error',text:error.message});}
    }
    async function save(body) {
        if(busy||!target||!snapshot)return;
        if(body.operation==='restore'&&!affected(currentItem()).length)return;
        const id=target,ticket=generation,token=snapshot.statistics_token;
        const who=currentItem()?.name?`“${currentItem().name}”`:'this combatant';if(!confirm(body.operation==='restore'?`Restore selected statistics of ${who} to their original/base values? Current HP will not heal.`:`Save the entered original/base statistics of ${who}? This does not heal.`))return;
        busy=true;const controls=[...$('statisticsModal').querySelectorAll('input,select,button')];
        const previousDisabled=controls.map(x=>x.disabled);controls.forEach(x=>x.disabled=true);
        try {
            await api(`/api/combatants/${encodeURIComponent(id)}/statistics`,{...body,token});
            if(ticket!==generation||target!==id)return;
            notice('Saved.');
            if(typeof load==='function')await load(true);
            if(ticket!==generation||target!==id)return;
            const state=await api('/api/state');if(ticket!==generation)return;
            if(stateScope(state)!==scope){window.scryingStatisticsState(state);return;}
            snapshot=state;const item=currentItem();if(item)draw(item);
        }catch(error){if(ticket===generation)notice(error.message);}
        finally {
            busy=false;controls.forEach((x,i)=>x.disabled=previousDisabled[i]);
            const item=currentItem();if(item&&!affected(item).length){$('statisticsRestore').disabled=true;$('statisticsRestoreStat').disabled=true;}
        }
    }
    document.addEventListener('click',event=>{
        const button=event.target.closest('[data-statistics]');if(button)open(button.dataset.statistics,button);
    });
    $('statisticsClose').onclick=close;
    $('statisticsModal').addEventListener('click',event=>{if(event.target===$('statisticsModal'))close();});
    document.addEventListener('keydown',event=>{if(event.key==='Escape'&&!$('statisticsModal').hidden)close();});
    $('statisticsRestore').onclick=()=>save({operation:'restore',stat:$('statisticsRestoreStat').value});
    $('statisticsEditBases').onclick=()=>{if(!busy&&currentItem()){editingBases=true;draw(currentItem());notice('');}};
    $('statisticsBack').onclick=()=>{if(!busy&&currentItem()){editingBases=false;draw(currentItem());notice('');}};
    $('statisticsBasesForm').onsubmit=event=>{
        event.preventDefault();if(!editingBases||!$('statisticsBasesForm').reportValidity())return;
        const bases={};
        for(const input of $('statisticsFields').querySelectorAll('[data-base-stat]')) {
            const value=input.value===''?null:Number(input.value);
            if(value!==null&&!Number.isSafeInteger(value)){notice('Use whole numbers within the browser safe-integer range.');return;}
            bases[input.dataset.baseStat]=value;
        }
        save({operation:'bases',bases});
    };
})();
