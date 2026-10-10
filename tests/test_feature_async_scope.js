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
             monsters:[{id:'m',name:'Goblin',hp:12,max_hp:12,temp_hp:2,life_state:'standing',effects:[]}],lairs:[],active_campaign_id:'1',active_setup:{campaign_id:'1',name:'first'}};
  const summary={checkpoints:[],displays:[],downed:[],undo:null};
  const writes=[]; let tick; const hold={enabled:false,release:null};
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
          if(hold.enabled)await new Promise(resolve=>{hold.release=resolve;});
        }
      }
      return {ok:true,json:async()=>JSON.parse(JSON.stringify(url==='/api/features'?summary:state))};
    }
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../static/features.js'),'utf8'),context);
  const flush=()=>new Promise(resolve=>setImmediate(resolve));
  await flush();
  return {hold,summary,element,writes,state,flush,poll:async()=>{tick();await flush();},
          dirty:()=>{element('featureTempHp').value=99;element('featureTempHp').listeners.input();}};
}

const checks=[
  ['new draft entered during a save survives its acknowledgement',async()=>{
    const h=await harness();h.dirty();h.hold.enabled=true;
    const saving=h.element('setTempHp').onclick();await h.flush();
    h.element('featureTempHp').value=100;h.element('featureTempHp').listeners.input();
    h.hold.release();await saving;
    assert.equal(h.writes[0].body.temp_hp,99);
    assert.equal(h.element('featureTempHp').value,'100');
    assert.equal(h.element('featureTempHp').dataset.dirty,'1');
  }],
  ['old target save acknowledgement does not clear new target draft',async()=>{
    const h=await harness();h.dirty();h.hold.enabled=true;
    const saving=h.element('setTempHp').onclick();await h.flush();
    h.element('featureTarget').value='m';h.element('featureTarget').onchange();h.dirty();
    h.hold.release();await saving;
    assert.equal(h.writes[0].url,'/api/combatants/c/features');
    assert.equal(h.element('featureTarget').value,'m');
    assert.equal(h.element('featureTempHp').value,'99');
    assert.equal(h.element('featureTempHp').dataset.dirty,'1');
  }],
  ['ordinary save still clears the submitted draft',async()=>{
    const h=await harness();h.dirty();await h.element('setTempHp').onclick();
    assert.equal(h.element('featureTempHp').value,'99');
    assert.equal(h.element('featureTempHp').dataset.dirty,undefined);
  }],
  ['campaign switch resets drafts even when combatant IDs match',async()=>{
    const h=await harness();h.dirty();
    h.state.active_campaign_id='2';h.state.active_setup={campaign_id:'2',name:'first'};
    h.state.characters[0].temp_hp=7;await h.poll();
    assert.equal(h.element('featureTarget').value,'c');
    assert.equal(h.element('featureTempHp').value,'7');
    assert.equal(h.element('featureTempHp').dataset.dirty,undefined);
  }],
  ['setup switch resets drafts even when combatant IDs match',async()=>{
    const h=await harness();h.dirty();h.state.active_setup.name='second';
    h.state.characters[0].temp_hp=8;await h.poll();
    assert.equal(h.element('featureTempHp').value,'8');
    assert.equal(h.element('featureTempHp').dataset.dirty,undefined);
  }],
  ['campaign switch with no named setup resets drafts',async()=>{
    const h=await harness();h.state.active_setup=null;await h.poll();h.dirty();
    h.state.active_campaign_id='2';h.state.characters[0].temp_hp=9;await h.poll();
    assert.equal(h.element('featureTempHp').value,'9');
    assert.equal(h.element('featureTempHp').dataset.dirty,undefined);
  }],
  ['same encounter polling continues to preserve edits',async()=>{
    const h=await harness();h.dirty();await h.poll();
    assert.equal(h.element('featureTempHp').value,'99');
    assert.equal(h.element('featureTempHp').dataset.dirty,'1');
  }],
  ['subsequent save after campaign switch uses replacement values',async()=>{
    const h=await harness();h.dirty();h.state.active_campaign_id='2';
    h.state.active_setup={campaign_id:'2',name:'first'};h.state.characters[0].temp_hp=7;
    await h.poll();await h.element('setTempHp').onclick();
    assert.equal(h.writes[0].body.temp_hp,7);
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
