(() => {
    'use strict';
    const $=id=>document.getElementById(id);
    const stats=[['max_hp','Max HP'],['strength','STR'],['dexterity','DEX'],['constitution','CON'],['intelligence','INT'],['wisdom','WIS'],['charisma','CHA']];
    let scope=null, target=null, snapshot=null, generation=0, busy=false;
    const stateScope=s=>JSON.stringify([s.active_campaign_id,s.active_setup]);
    const notice=text=>{$('statisticsNotice').textContent=text;};
    async function api(url,body) {
        const options=body===undefined?{cache:'no-store'}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)};
        const response=await fetch(url,options), data=await response.json();
        if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:'Statistics request failed');
        return data;
    }
    function close() {if(busy)return;generation++;target=null;snapshot=null;$('statisticsModal').hidden=true;}
    window.scryingStatisticsState=s=>{
        const next=stateScope(s);
        if(scope!==null&&next!==scope) {
            generation++;target=null;snapshot=null;$('statisticsModal').hidden=true;
            if(typeof closeBattleActions==='function')closeBattleActions();
        }
        scope=next;
    };
    function draw(item) {
        $('statisticsTitle').textContent='Restore statistics: '+item.name;
        $('statisticsFields').replaceChildren(...stats.map(([stat,label])=>{
            const field=document.createElement('label'),caption=document.createElement('span'),input=document.createElement('input');
            const base=item['base_'+stat]??(stat==='max_hp'?item.max_hp:null);
            const effects=(item.effects||[]).filter(e=>e.mechanical?.stat===stat);
            caption.textContent=`${label}: effective ${item[stat]??'unknown'}; reduction ${effects.reduce((sum,e)=>sum+e.mechanical.amount,0)}. Original/base:`;
            input.type='number';input.min='0';input.max=stat==='max_hp'?String(Number.MAX_SAFE_INTEGER):'30';input.step='1';input.dataset.baseStat=stat;input.value=base??'';
            if(stat==='max_hp')input.required=true;
            field.append(caption,input);return field;
        }));
    }
    async function open(id) {
        if(busy)return;
        const ticket=++generation;
        try {
            const state=await api('/api/state');if(ticket!==generation)return;
            const item=[...state.characters,...state.monsters].find(x=>x.id===id);
            if(!item)throw new Error('Combatant no longer exists');
            window.scryingStatisticsState(state);
            target=id;snapshot=state;draw(item);notice('');$('statisticsModal').hidden=false;
        }catch(error){if(ticket===generation)alert(error.message);}
    }
    async function save(body) {
        if(busy||!target||!snapshot)return;
        const id=target,ticket=generation,token=snapshot.statistics_token;
        if(!confirm(body.operation==='restore'?'Restore selected statistics to their original/base values? Current HP will not heal.':'Save the entered original/base statistics? This does not heal.'))return;
        busy=true;const controls=[...$('statisticsModal').querySelectorAll('input,select,button')];controls.forEach(x=>x.disabled=true);
        try {
            await api(`/api/combatants/${encodeURIComponent(id)}/statistics`,{...body,token});
            if(ticket!==generation||target!==id)return;
            notice('Saved.');
            if(typeof load==='function')await load(true);
            if(ticket!==generation||target!==id)return;
            const state=await api('/api/state');if(ticket!==generation)return;
            snapshot=state;const item=[...state.characters,...state.monsters].find(x=>x.id===id);
            if(item)draw(item);
        }catch(error){if(ticket===generation)notice(error.message);}
        finally {busy=false;controls.forEach(x=>x.disabled=false);}
    }
    document.addEventListener('click',event=>{
        const button=event.target.closest('[data-statistics]');if(button)open(button.dataset.statistics);
    });
    $('statisticsClose').onclick=close;
    $('statisticsModal').addEventListener('click',event=>{if(event.target===$('statisticsModal'))close();});
    $('statisticsRestore').onclick=()=>save({operation:'restore',stat:$('statisticsRestoreStat').value});
    $('statisticsBasesForm').onsubmit=event=>{
        event.preventDefault();if(!$('statisticsBasesForm').reportValidity())return;
        const bases={};
        for(const input of $('statisticsFields').querySelectorAll('[data-base-stat]')) {
            const value=input.value===''?null:Number(input.value);
            if(value!==null&&!Number.isSafeInteger(value)){notice('Use whole numbers within the browser safe-integer range.');return;}
            bases[input.dataset.baseStat]=value;
        }
        save({operation:'bases',bases});
    };
})();
