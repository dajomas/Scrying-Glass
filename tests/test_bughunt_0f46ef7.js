/* Deterministic encounter-tools draft races for commit 0f46ef7.
 * Runs the complete production script in Node vm with DOM/fetch fixtures.
 * No real browser, database or HTTP server is exercised.
 */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const code=fs.readFileSync(path.join(__dirname,'..','static','features.js'),'utf8');
const flush=()=>new Promise(resolve=>setImmediate(resolve));
async function harness({allow=true,fail=false}={}) {
  const selects=new Set(['featureTarget','effectSource','effectAnchor','checkpointSelect']);
  const elements=new Map();
  class Element {
    constructor(id=''){this.id=id;this.dataset={};this.listeners={};this._value='';this.checked=false;}
    get value(){return this._value;}
    set value(value){this._value=String(value);}
    addEventListener(name,fn){this.listeners[name]=fn;}
    replaceChildren(...children){this.children=children;if(selects.has(this.id))this.value=children[0]?.value??'';}
    append(...children){this.children=children;}
  }
  const element=id=>{if(!elements.has(id))elements.set(id,new Element(id));return elements.get(id);};
  const state={characters:[{id:'c',name:'Cleric',hp:20,max_hp:20,temp_hp:1,life_state:'standing',effects:[]}],
    monsters:[{id:'m',name:'Goblin',hp:12,max_hp:12,temp_hp:2,life_state:'standing',effects:[]}],
    lairs:[],active_campaign_id:'1',active_setup:{campaign_id:'1',name:'first'}};
  const summary={checkpoints:[{id:1,name:'Checkpoint',created:0}],displays:[],downed:[],undo:{id:1,label:'Previous'}};
  const h={state,summary,element,writes:[],holdURL:null,release:null};
  let tick;
  class FormData{}
  const context={document:{getElementById:element,createElement:()=>new Element(),activeElement:null},
    Option:function(name,id){this.text=name;this.value=String(id);},FormData,
    window:{scryingDamagePreview:()=>"Preview"},setInterval:fn=>{tick=fn;},confirm:()=>allow,alert:()=>{},location:{},
    fetch:async(url,options)=>{
      if(options.method!=='GET') {
        const body=options.body===undefined?null:JSON.parse(options.body);
        h.writes.push({url,method:options.method,body});
        if(fail)return {ok:false,status:422,json:async()=>({detail:'Injected failure'})};
        if(options.method==='PATCH')Object.assign([...state.characters,...state.monsters].find(x=>x.id===url.split('/')[3]),body);
        if(url===h.holdURL){h.holdURL=null;await new Promise(resolve=>{h.release=resolve;});}
        return {ok:true,json:async()=>({})};
      }
      const data=url==='/api/features'?summary:url==='/api/state'?state:
        {revision:1,battle_round:1,monsters:1,characters:1,active_setup:state.active_setup};
      return {ok:true,json:async()=>JSON.parse(JSON.stringify(data))};
    }};
  vm.runInNewContext(code,context,{filename:'static/features.js'});
  await flush();element('effectTiming').value='manual';
  h.dirty=(id,value)=>{element(id).value=value;element(id).listeners.input();};
  h.select=id=>{element('featureTarget').value=id;element('featureTarget').onchange();};
  h.poll=async()=>{tick();await flush();};
  return h;
}
async function paused(operation) {
  const h=await harness();h.dirty('featureTempHp',99);
  h.holdURL=operation==='undo'?'/api/battle/undo':'/api/checkpoints/1/restore';
  h.pending=h.element(operation==='undo'?'featureUndo':'restoreCheckpoint').onclick();
  await flush();assert.equal(typeof h.release,'function');return h;
}
async function pausedEffect() {
  const h=await harness();h.element('effectName').value='Submitted';h.element('effectNotes').value='Submitted notes';
  h.holdURL='/api/combatants/c/effects';h.element('effectForm').onsubmit({preventDefault(){}});
  await flush();assert.equal(typeof h.release,'function');return h;
}
const cases=[];
for(const operation of ['undo','restore']) {
  cases.push([operation+' preserves a newer same-target draft',async()=>{
    const h=await paused(operation);h.dirty('featureTempHp',100);h.release();await h.pending;
    assert.equal(h.element('featureTempHp').value,'100');assert.equal(h.element('featureTempHp').dataset.dirty,'1');
  }]);
  cases.push([operation+' preserves a new-target draft',async()=>{
    const h=await paused(operation);h.select('m');h.dirty('featureTempHp',100);h.release();await h.pending;
    assert.equal(h.element('featureTarget').value,'m');assert.equal(h.element('featureTempHp').value,'100');
    assert.equal(h.element('featureTempHp').dataset.dirty,'1');
  }]);
  cases.push([operation+' still discards unchanged pre-operation drafts',async()=>{
    const h=await paused(operation);h.release();await h.pending;
    assert.equal(h.element('featureTempHp').value,'1');assert.equal(h.element('featureTempHp').dataset.dirty,undefined);
  }]);
}
cases.push(
 ['effect response preserves newer name',async()=>{
   const h=await pausedEffect();h.element('effectName').value='Next condition';h.release();await flush();
   assert.equal(h.element('effectName').value,'Next condition');assert.equal(h.writes[0].body.name,'Submitted');
 }],
 ['effect response preserves newer notes',async()=>{
   const h=await pausedEffect();h.element('effectNotes').value='New private notes';h.release();await flush();
   assert.equal(h.element('effectNotes').value,'New private notes');assert.equal(h.writes[0].body.notes,'Submitted notes');
 }],
 ['effect response does not clear form after target switch',async()=>{
   const h=await pausedEffect();h.select('m');h.release();await flush();
   assert.equal(h.element('effectName').value,'Submitted');assert.equal(h.element('effectNotes').value,'Submitted notes');
   assert.equal(h.writes[0].url,'/api/combatants/c/effects');
 }],
 ['unchanged effect form still clears after success',async()=>{
   const h=await pausedEffect();h.release();await flush();
   assert.equal(h.element('effectName').value,'');assert.equal(h.element('effectNotes').value,'');
 }],
 ['failed recovery request preserves drafts',async()=>{
   const h=await harness({fail:true});h.dirty('featureTempHp',99);await h.element('featureUndo').onclick();
   assert.equal(h.element('featureTempHp').value,'99');assert.equal(h.element('featureTempHp').dataset.dirty,'1');
 }],
 ['cancelled restore preserves drafts',async()=>{
   const h=await harness({allow:false});h.dirty('featureTempHp',99);await h.element('restoreCheckpoint').onclick();
   assert.equal(h.element('featureTempHp').value,'99');assert.equal(h.writes.length,0);
 }],
 ['ordinary health save still clears its own draft',async()=>{
   const h=await harness();h.dirty('featureTempHp',99);await h.element('setTempHp').onclick();
   assert.equal(h.element('featureTempHp').dataset.dirty,undefined);assert.equal(h.writes[0].body.temp_hp,99);
 }],
 ['ordinary health save preserves unrelated drafts',async()=>{
   const h=await harness();h.dirty('featureTempHp',99);h.dirty('deathSuccesses',2);await h.element('setTempHp').onclick();
   assert.equal(h.element('deathSuccesses').value,'2');assert.equal(h.element('deathSuccesses').dataset.dirty,'1');
 }],
 ['normal same-encounter polling preserves drafts',async()=>{
   const h=await harness();h.dirty('featureTempHp',99);await h.poll();assert.equal(h.element('featureTempHp').value,'99');
 }]
);
(async()=>{
 let failures=0;
 for(const [name,test] of cases){try{await test();console.log('PASS '+name);}catch(error){failures++;console.error('FAIL '+name+'\n'+error.stack);}}
 console.log(`${cases.length} tests; ${cases.length-failures} passed; ${failures} failed`);process.exitCode=failures?1:0;
})();
