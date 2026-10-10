const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

async function harness() {
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
    FormData,window:{},console,
    setInterval:fn=>{tick=fn;},confirm:()=>true,alert:()=>{},location:{},
    fetch:async(url,options)=>{
      if(options.method!=='GET') writes.push({url,body:JSON.parse(options.body)});
      return {ok:true,json:async()=>JSON.parse(JSON.stringify(url==='/api/features'?summary:state))};
    }
  };
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../static/features.js'),'utf8'),context);
  const flush=()=>new Promise(resolve=>setImmediate(resolve));
  await flush();
  return {element,writes,state,flush,poll:async()=>{tick();await flush();},
          dirty:()=>{element('featureTempHp').value=99;element('featureTempHp').listeners.input();}};
}

(async()=>{
  let h=await harness(); h.dirty(); h.state.characters=[]; await h.poll();
  assert.equal(h.element('featureTarget').value,'m');
  assert.equal(h.element('featureTempHp').value,'2','Removed target must not carry dirty HP into another combatant');
  assert.equal(h.element('featureTempHp').dataset.dirty,undefined);
  console.log('PASS: automatic target replacement resets dirty fields');

  h=await harness(); h.dirty(); await h.poll();
  assert.equal(h.element('featureTarget').value,'c');
  assert.equal(h.element('featureTempHp').value,'99','Same-target polling must preserve unsaved edits');
  assert.equal(h.element('featureTempHp').dataset.dirty,'1');
  console.log('PASS: same-target polling preserves edits');

  h=await harness(); h.dirty(); h.state.characters=[]; await h.poll();
  await h.element('setTempHp').onclick();
  assert.equal(h.writes[0].url,'/api/combatants/m/features');
  assert.equal(h.writes[0].body.temp_hp,2,'Saving replacement target must not use prior target HP');
  console.log('PASS: subsequent save uses replacement target values');

  h=await harness(); h.dirty(); h.state.characters=[]; h.state.monsters=[]; await h.poll();
  assert.equal(h.element('featureTarget').value,'');
  assert.equal(h.element('featureTempHp').dataset.dirty,undefined);
  console.log('PASS: removing all targets clears dirty flags');
})().catch(error=>{console.error(error);process.exitCode=1;});
