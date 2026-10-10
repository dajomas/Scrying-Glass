const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

async function harness({allow=true,fail=false}={}) {
  const selects = new Set(['featureTarget','effectSource','effectAnchor','checkpointSelect']);
  const elements = new Map();
  class Element {
    constructor(id='') { this.id=id; this.dataset={}; this.listeners={}; this._value=''; }
    get value() { return this._value; }
    set value(value) { this._value=String(value); }
    addEventListener(name,fn) { this.listeners[name]=fn; }
    replaceChildren(...children) {
      this.children=children;
      if(selects.has(this.id)) this.value=children[0]?.value ?? '';
    }
    append(...children) { this.children=children; }
  }
  const element=id => {
    if(!elements.has(id)) elements.set(id,new Element(id));
    return elements.get(id);
  };
  let state={characters:[{id:'c',name:'Cleric',hp:20,max_hp:20,temp_hp:1,life_state:'standing',effects:[]}],
             monsters:[{id:'m',name:'Goblin',hp:12,max_hp:12,temp_hp:2,life_state:'standing',effects:[]}],lairs:[]};
  const summary={checkpoints:[],displays:[],downed:[],undo:null};
  const writes=[]; let tick;
  class FormData {}
  const context={
    document:{getElementById:element,createElement:()=>new Element(),activeElement:null},
    Option:function(name,id) { this.text=name; this.value=String(id); },
    FormData,window:{scryingDamagePreview:()=>"Preview"},console,
    setInterval:fn=>{tick=fn;},confirm:()=>allow,alert:()=>{},location:{},
    fetch:async(url,options)=>{
      if(options.method!=='GET') {
        const body=options.body===undefined?null:JSON.parse(options.body);
        if(fail)return {ok:false,status:422,json:async()=>({detail:'Injected failure'})};
        writes.push({url,body});
        if(options.method==='PATCH') {
          const id=url.split('/')[3];
          Object.assign([...state.characters,...state.monsters].find(x=>x.id===id),body);
        }
      }
      return {ok:true,json:async()=>JSON.parse(JSON.stringify(url==='/api/features'?summary:state))};
    }
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../static/features.js'),'utf8'),context);
  const flush=()=>new Promise(resolve=>setImmediate(resolve));
  await flush();
  return {summary,element,writes,state,flush,poll:async()=>{tick();await flush();},
          dirty:()=>{element('featureTempHp').value=99;element('featureTempHp').listeners.input();}};
}

const checks=[
  ['confirmed undo deliberately resets feature drafts',async()=>{
    const h=await harness();h.summary.undo={id:1,label:'Undo'};h.dirty();await h.poll();
    await h.element('featureUndo').onclick();
    assert.equal(h.element('featureTempHp').dataset.dirty,undefined);
    assert.equal(h.element('featureTempHp').value,'1');
  }],
  ['confirmed checkpoint restore deliberately resets feature drafts',async()=>{
    const h=await harness();h.summary.checkpoints=[{id:1,name:'Checkpoint',created:0}];
    h.dirty();await h.poll();await h.element('restoreCheckpoint').onclick();
    assert.equal(h.element('featureTempHp').dataset.dirty,undefined);
    assert.equal(h.element('featureTempHp').value,'1');
  }],
  ['confirmed life-state save clears only its own draft',async()=>{
    const h=await harness();h.dirty();h.element('featureLifeState').value='dead';
    h.element('featureLifeState').listeners.input();await h.element('setLifeState').onclick();
    assert.equal(h.element('featureLifeState').dataset.dirty,undefined);
    assert.equal(h.element('featureTempHp').value,'99');
    assert.equal(h.element('featureTempHp').dataset.dirty,'1');
  }],
  ['cancelled bundle import preserves drafts',async()=>{
    const h=await harness({allow:false});h.dirty();h.element('importBundle').files=[{}];
    await h.element('importBundle').onchange();
    assert.equal(h.writes.length,0);assert.equal(h.element('featureTempHp').value,'99');
    assert.notEqual(h.element('featureNotice').textContent,'Saved.');
  }],
  ['saving temporary HP preserves unsaved death saves',async()=>{
    const h=await harness();h.dirty();
    h.element('deathSuccesses').value=2;h.element('deathSuccesses').listeners.input();
    await h.element('setTempHp').onclick();
    assert.equal(h.element('deathSuccesses').value,'2');
    assert.equal(h.element('deathSuccesses').dataset.dirty,'1');
    assert.equal(h.element('featureTempHp').dataset.dirty,undefined);
    assert.equal(h.element('featureTempHp').value,'99');
  }],
  ['saving death saves preserves unsaved temporary HP',async()=>{
    const h=await harness();h.dirty();
    h.element('deathSuccesses').value=1;h.element('deathSuccesses').listeners.input();
    h.element('deathFailures').value=2;h.element('deathFailures').listeners.input();
    await h.element('setDeathSaves').onclick();
    assert.equal(h.element('featureTempHp').value,'99');
    assert.equal(h.element('featureTempHp').dataset.dirty,'1');
    assert.equal(h.element('deathSuccesses').dataset.dirty,undefined);
    assert.equal(h.element('deathFailures').dataset.dirty,undefined);
  }],
  ['saving a checkpoint preserves feature edits',async()=>{
    const h=await harness();h.dirty();await h.element('saveCheckpoint').onclick();
    assert.equal(h.element('featureTempHp').value,'99');
    assert.equal(h.element('featureTempHp').dataset.dirty,'1');
  }],
  ['starting concentration preserves feature edits',async()=>{
    const h=await harness();h.dirty();await h.element('startConcentration').onclick();
    assert.equal(h.element('featureTempHp').value,'99');
    assert.equal(h.element('featureTempHp').dataset.dirty,'1');
  }],
  ['cancelled death marking preserves edits and is not reported saved',async()=>{
    const h=await harness({allow:false});h.dirty();
    h.element('featureLifeState').value='dead';h.element('featureLifeState').listeners.input();
    await h.element('setLifeState').onclick();
    assert.equal(h.writes.length,0);
    assert.equal(h.element('featureTempHp').value,'99');
    assert.equal(h.element('featureLifeState').value,'dead');
    assert.equal(h.element('featureLifeState').dataset.dirty,'1');
    assert.notEqual(h.element('featureNotice').textContent,'Saved.');
  }],
  ['cancelled HP confirmation preserves feature edits',async()=>{
    const h=await harness({allow:false});h.dirty();h.element('featureHpDelta').value=-1;
    await h.element('applyFeatureHp').onclick();
    assert.equal(h.writes.length,0);
    assert.equal(h.element('featureTempHp').value,'99');
    assert.notEqual(h.element('featureNotice').textContent,'Saved.');
  }],
  ['cancelled checkpoint restore preserves edits',async()=>{
    const h=await harness({allow:false});h.dirty();h.element('checkpointSelect').value=1;
    await h.element('restoreCheckpoint').onclick();
    assert.equal(h.writes.length,0);
    assert.equal(h.element('featureTempHp').value,'99');
    assert.notEqual(h.element('featureNotice').textContent,'Saved.');
  }],
  ['cancelled checkpoint deletion preserves edits',async()=>{
    const h=await harness({allow:false});h.dirty();h.element('checkpointSelect').value=1;
    await h.element('deleteCheckpoint').onclick();
    assert.equal(h.writes.length,0);
    assert.equal(h.element('featureTempHp').value,'99');
    assert.notEqual(h.element('featureNotice').textContent,'Saved.');
  }],
  ['failed request preserves edits',async()=>{
    const h=await harness({fail:true});h.dirty();await h.element('setTempHp').onclick();
    assert.equal(h.element('featureTempHp').value,'99');
    assert.equal(h.element('featureTempHp').dataset.dirty,'1');
    assert.equal(h.element('featureNotice').textContent,'Injected failure');
  }],
];
(async()=>{
  let failures=0;
  for(const [name,check] of checks) {
    try{await check();console.log('PASS: '+name);}
    catch(error){failures++;console.error('FAIL: '+name+' — '+error.message);}
  }
  console.log(`${checks.length} checks, ${failures} failures`);
  if(failures)process.exitCode=1;
})().catch(error=>{console.error(error);process.exitCode=1;});
