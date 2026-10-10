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
  const writes=[]; let tick; const hold={enabled:false,release:null,fail:false};let reads=0;
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
      const snapshot=JSON.parse(JSON.stringify(url==='/api/features'?summary:state));
      if(url==='/api/state') {
        reads++;
        if(hold.enabled) {
          await new Promise(resolve=>{hold.release=resolve;});
          if(hold.fail)return {ok:false,status:500,json:async()=>({detail:'Polling failed'})};
        }
      }
      return {ok:true,json:async()=>snapshot};
    }
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../static/features.js'),'utf8'),context);
  const flush=()=>new Promise(resolve=>setImmediate(resolve));
  await flush();
  return {hold,reads:()=>reads,summary,element,writes,state,flush,poll:async()=>{tick();await flush();},
          dirty:()=>{element('featureTempHp').value=99;element('featureTempHp').listeners.input();}};
}

const checks=[
  ['automatic polling coalesces behind a slow request',async()=>{
    const h=await harness();h.hold.enabled=true;await h.poll();
    await h.poll();await h.poll();assert.equal(h.reads(),2);
    h.hold.enabled=false;h.hold.release();await h.flush();await h.flush();
    assert.equal(h.reads(),2,'Periodic ticks must not create a request backlog');
    await h.poll();assert.equal(h.reads(),3);
  }],
  ['save queues a fresh snapshot behind an existing poll',async()=>{
    const h=await harness();h.hold.enabled=true;await h.poll();h.dirty();
    const saving=h.element('setTempHp').onclick();await h.flush();
    h.hold.enabled=false;h.hold.release();await saving;await h.flush();
    assert.equal(h.element('featureTempHp').value,'99');
    assert.ok(h.reads()>=3,'A post-save snapshot must be requested');
  }],
  ['manual refresh is awaited and not dropped behind a poll',async()=>{
    const h=await harness();h.hold.enabled=true;await h.poll();
    h.state.characters[0].temp_hp=7;
    const refreshing=h.element('featureRefresh').onclick();await h.flush();
    h.hold.enabled=false;h.hold.release();await refreshing;await h.flush();
    assert.equal(h.element('featureTempHp').value,'7');
    assert.ok(h.reads()>=3);
  }],
  ['queued refresh recovers after the earlier poll fails',async()=>{
    const h=await harness();h.hold.enabled=true;h.hold.fail=true;await h.poll();
    h.state.characters[0].temp_hp=8;
    const refreshing=h.element('featureRefresh').onclick();await h.flush();
    h.hold.enabled=false;h.hold.release();await refreshing;await h.flush();
    assert.equal(h.element('featureTempHp').value,'8');
    assert.ok(h.reads()>=3);
  }],
  ['ordinary save without a concurrent poll still refreshes',async()=>{
    const h=await harness();h.dirty();await h.element('setTempHp').onclick();
    assert.equal(h.element('featureTempHp').value,'99');
    assert.equal(h.element('featureTempHp').dataset.dirty,undefined);
  }],
  ['concurrent manual refreshes complete without a stuck gate',async()=>{
    const h=await harness();h.hold.enabled=true;await h.poll();
    const first=h.element('featureRefresh').onclick();
    const second=h.element('featureRefresh').onclick();await h.flush();
    h.hold.enabled=false;h.hold.release();await Promise.all([first,second]);await h.flush();
    assert.ok(h.reads()>=4,'Both queued refresh calls must run');
    await h.poll();assert.ok(h.reads()>=5,'Later polling must remain functional');
  }],
];
(async()=>{
  let failures=0;
  for(const [name,check] of checks){
    try{await check();console.log('PASS: '+name);}
    catch(error){failures++;console.error('FAIL: '+name+' — '+error.message);}
  }
  console.log(`${checks.length} checks, ${failures} failures`);
  if(failures)process.exitCode=1;
})().catch(error=>{console.error(error);process.exitCode=1;});
