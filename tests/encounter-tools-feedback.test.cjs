// SG-TODO-009.7 Stage 3: full features script with the real feedback controller/bootstrap; DOM and HTTP mocked.
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const test=require('node:test');
const vm=require('node:vm');
const {installFeedback}=require('./battle-action-feedback-fixture.cjs');
const code=fs.readFileSync(path.join(__dirname,'../static/features.js'),'utf8');
const flush=async()=>{for(let i=0;i<6;i++)await new Promise(resolve=>setImmediate(resolve));};
async function setup() {
    const elements=new Map(),timers=new Map();let now=0,sequence=0;
    class Element {
        constructor(){this.dataset={};this.value='';this.files=[];this.listeners={};this.checked=false;}
        addEventListener(name,fn){this.listeners[name]=fn;}
        replaceChildren(...children){this.children=children;}
        append(...children){this.children=children;}
    }
    const element=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
    const state={active_campaign_id:'fixture',active_setup:{campaign_id:'fixture',name:'setup'},lairs:[],monsters:[],
        characters:[{id:'c',name:'Hero',hp:10,max_hp:10,active:true,temp_hp:0}]};
    const summary={checkpoints:[{id:'k',name:'Start',created:0}],displays:[],downed:[],undo:null};
    const h={calls:[],allow:true,hold:null,fail:{},loads:0};
    const context={window:{scryingDamagePreview:()=>'Apply?'},document:{createElement:()=>new Element(),activeElement:null},
        FormData:class{},Option:function(name,id){this.text=name;this.value=String(id);},
        confirm:()=>h.allow,location:{},setInterval:()=>{},
        load:async rethrow=>{h.loads++;assert.equal(rethrow,true);if(h.fail.load)throw new Error('Core refresh failed');},
        fetch:async(url,request)=>{
            h.calls.push({url,method:request.method});
            if(request.method!=='GET'){
                if(h.hold)await h.hold;
                const detail=h.fail[url];
                if(detail)return {ok:false,status:422,json:async()=>({detail})};
                return {ok:true,json:async()=>({})};
            }
            if(h.fail.features&&url==='/api/features')throw new Error('Feature refresh failed');
            if(url==='/api/checkpoints/k')return {ok:true,json:async()=>({battle_round:1,monsters:0,characters:1,revision:3})};
            return {ok:true,json:async()=>url==='/api/state'?state:summary};
        }};
    const {feedback,scope}=installFeedback(context,{
        setTimeout(fn,delay){const id=++sequence;timers.set(id,{fn,deadline:now+delay});return id;},
        clearTimeout(id){timers.delete(id);},
    });
    context.document.getElementById=element;
    element('featureTarget').value='c';
    vm.runInContext(code,context,{filename:'static/features.js'});await flush();
    return Object.assign(h,{element,feedback,scope,
        records:()=>feedback.snapshot().map(r=>[r.lane,r.region,r.operation,r.severity,r.text]),
        writes:()=>h.calls.filter(call=>call.method!=='GET'),
        tick(ms){now+=ms;for(const [id,item]of [...timers])if(item.deadline<=now){timers.delete(id);item.fn();}},
        click:async id=>{await element(id).onclick();await flush();}});
}
const patch='/api/combatants/c/features';
test('tools error persists in the tools region and keeps the draft; next success resolves it',async()=>{
    const h=await setup();h.element('featureTempHp').value='7';h.element('featureTempHp').listeners.input();
    h.fail[patch]='Temporary HP rejected';await h.click('setTempHp');
    assert.deepEqual(h.records(),[['encounter','tools','tools.temp-hp','error','Temporary HP rejected']]);
    h.tick(60000);assert.equal(h.records().length,1);
    assert.equal(h.element('featureTempHp').dataset.dirty,'1');assert.equal(h.element('featureNotice').textContent,undefined);
    delete h.fail[patch];await h.click('setTempHp');
    assert.deepEqual(h.records(),[['encounter','tools','tools.temp-hp','success','Saved.']]);
    h.tick(2999);assert.equal(h.records().length,1);h.tick(1);assert.equal(h.records().length,0);
    assert.equal(h.writes().length,2);assert.deepEqual(Array.from(h.feedback.legacyRegions()),[]);
});
test('declined confirmation is silent, sends nothing and keeps the earlier error',async()=>{
    const h=await setup();h.element('featureLifeState').value='dead';
    h.fail[patch]='Rejected';await h.click('setLifeState');h.allow=false;await h.click('setLifeState');
    assert.deepEqual(h.records(),[['encounter','tools','tools.life-state','error','Rejected']]);
    assert.equal(h.writes().length,1);assert.notEqual(h.element('featureNotice').textContent,'Cancelled.');
});
test('failed refresh after success is a separate no-replay error',async()=>{
    const h=await setup();h.fail.load=true;await h.click('setTempHp');
    const r=h.records();assert.deepEqual(r[0],['encounter','tools','tools.temp-hp','success','Saved.']);
    assert.equal(r[1][2],'tools.temp-hp.refresh');assert.equal(r[1][3],'error');
    assert.match(r[1][4],/^Set temporary HP completed, but refreshing the view failed: Core refresh failed\. Reload the page; do not repeat it/);
    assert.equal(h.writes().length,1);h.tick(60000);assert.equal(h.records().length,1);
    h.fail.load=false;await h.click('setTempHp');assert.equal(h.records().filter(x=>x[2].endsWith('.refresh')).length,0);
});
test('manual refresh failure is a persistent tools error and success resolves it',async()=>{
    const h=await setup();h.fail.features=true;await h.click('featureRefresh');
    assert.deepEqual(h.records(),[['encounter','tools','tools.refresh','error','Feature refresh failed']]);
    assert.equal(h.element('featureNotice').textContent,undefined);
    h.fail.features=false;await h.click('featureRefresh');assert.deepEqual(h.records(),[]);
});
test('encounter scope change clears tools records and stale completion cannot publish',async()=>{
    const h=await setup();h.fail[patch]='Rejected';await h.click('setTempHp');
    h.scope('other','elsewhere');assert.deepEqual(h.records(),[]);
    let release;h.hold=new Promise(resolve=>{release=resolve;});delete h.fail[patch];
    const pending=h.element('setTempHp').onclick();await flush();h.scope('third','x');release();await pending;await flush();
    assert.deepEqual(h.records(),[]);
});
test('checkpoint restore success uses the page lane and survives the setup transition',async()=>{
    const h=await setup();h.element('checkpointSelect').value='k';
    let release;h.hold=new Promise(resolve=>{release=resolve;});
    const pending=h.element('restoreCheckpoint').onclick();await flush();h.scope('fixture','restored');release();await pending;await flush();
    assert.deepEqual(h.records(),[['page','tools','tools.checkpoint.restore','success','Saved.']]);
    h.scope('fixture','another');assert.equal(h.records().length,1);
});
test('busy duplicate is suppressed without starting feedback',async()=>{
    const h=await setup();let release;h.hold=new Promise(resolve=>{release=resolve;});
    const first=h.element('setTempHp').onclick();await flush();await h.element('setTempHp').onclick();
    assert.equal(h.writes().length,1);assert.deepEqual(h.records(),[]);release();await first;await flush();
    assert.equal(h.records().length,1);
});
