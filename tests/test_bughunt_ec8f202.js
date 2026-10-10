/* Complete lairs.js executed with Node vm DOM/fetch fixtures.
 * Deferred responses reproduce configuration draft races. No live browser/server.
 */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const code=fs.readFileSync(path.join(__dirname,'..','static','lairs.js'),'utf8');
const flush=()=>new Promise(resolve=>setImmediate(resolve));
async function harness({fail=false}={}) {
  class Element {
    constructor(){this.dataset={};this.listeners={};this.value='';this.checked=false;this.disabled=false;this.children=[];}
    addEventListener(name,fn){this.listeners[name]=fn;}
    append(...nodes){this.children.push(...nodes);}
    replaceChildren(...nodes){this.children=nodes;}
    setAttribute(name,value){this[name]=value;}
  }
  const elements=new Map(),element=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
  const h={element,writes:[],hold:false,release:null,state:{active_campaign_id:'1',active_setup:{campaign_id:'1',name:'first'},
    lairs:[{id:'l',name:'Lair',notes:'Notes',color:'#8064a2',active:true,visible:true,in_turn:false}],characters:[],monsters:[]}};
  const window={};
  const context={document:{getElementById:element,createElement:()=>new Element()},window,confirm:()=>true,
    load:async()=>window.scryingLairsRender(h.state),fetch:async(url,options)=>{
      const body=options.body?JSON.parse(options.body):null;h.writes.push({url,method:options.method,body});
      if(fail)return {ok:false,status:422,json:async()=>({detail:'Rejected'})};
      if(options.method==='PATCH')Object.assign(h.state.lairs[0],body);
      if(h.hold){h.hold=false;await new Promise(resolve=>{h.release=resolve;});}
      return {ok:true,json:async()=>({})};
    }};
  vm.runInNewContext(code,context,{filename:'static/lairs.js'});window.scryingLairsRender(h.state);
  h.render=()=>window.scryingLairsRender(h.state);
  h.dirty=(id,value)=>{element(id).value=value;element(id).listeners.input();};
  h.submit=()=>element('lairConfigForm').onsubmit({preventDefault(){}});
  h.finish=async()=>{h.release();await flush();};
  return h;
}
async function paused(){const h=await harness();h.dirty('lairName','Submitted');h.hold=true;h.submit();await flush();assert.equal(typeof h.release,'function');return h;}
const cases=[
 ['new name entered during save survives reload',async()=>{
   const h=await paused();h.dirty('lairName','New unsaved name');await h.finish();
   assert.equal(h.element('lairName').value,'New unsaved name');assert.equal(h.element('lairName').dataset.dirty,'1');assert.equal(h.writes[0].body.name,'Submitted');
 }],
 ['new notes entered during save survive reload',async()=>{
   const h=await paused();h.dirty('lairNotes','New unsaved notes');await h.finish();
   assert.equal(h.element('lairNotes').value,'New unsaved notes');assert.equal(h.element('lairNotes').dataset.dirty,'1');
 }],
 ['new color entered during save survives reload',async()=>{
   const h=await paused();h.dirty('lairColor','#112233');await h.finish();
   assert.equal(h.element('lairColor').value,'#112233');assert.equal(h.element('lairColor').dataset.dirty,'1');
 }],
 ['unchanged submitted field clears while newer field stays dirty',async()=>{
   const h=await paused();h.dirty('lairNotes','New draft');await h.finish();
   assert.equal(h.element('lairName').dataset.dirty,undefined);assert.equal(h.element('lairNotes').dataset.dirty,'1');
 }],
 ['response for previous lair cannot clear replacement draft',async()=>{
   const h=await paused();h.state.lairs=[{...h.state.lairs[0],id:'other',name:'Other'}];h.render();h.dirty('lairName','Other draft');await h.finish();
   assert.equal(h.element('lairName').value,'Other draft');assert.equal(h.element('lairName').dataset.dirty,'1');
 }],
 ['campaign switch resets old drafts even for same lair ID',async()=>{
   const h=await harness();h.dirty('lairName','Old campaign draft');h.state.active_campaign_id='2';h.state.active_setup={campaign_id:'2',name:'first'};h.state.lairs[0].name='New campaign';h.render();
   assert.equal(h.element('lairName').value,'New campaign');assert.equal(h.element('lairName').dataset.dirty,undefined);
 }],
 ['setup switch resets old drafts even for same lair ID',async()=>{
   const h=await harness();h.dirty('lairNotes','Old setup notes');h.state.active_setup.name='second';h.state.lairs[0].notes='Second setup notes';h.render();
   assert.equal(h.element('lairNotes').value,'Second setup notes');assert.equal(h.element('lairNotes').dataset.dirty,undefined);
 }],
 ['unnamed encounter campaign switch resets drafts',async()=>{
   const h=await harness();h.state.active_setup=null;h.render();h.dirty('lairName','Old unnamed');h.state.active_campaign_id='2';h.state.lairs[0].name='New unnamed';h.render();
   assert.equal(h.element('lairName').value,'New unnamed');
 }],
 ['old-scope response preserves a new-scope draft',async()=>{
   const h=await paused();h.state.active_setup.name='second';h.state.lairs[0].notes='Other notes';h.render();h.dirty('lairNotes','New encounter draft');await h.finish();
   assert.equal(h.element('lairNotes').value,'New encounter draft');assert.equal(h.element('lairNotes').dataset.dirty,'1');
 }],
 ['ordinary successful save clears unchanged draft',async()=>{
   const h=await paused();await h.finish();assert.equal(h.element('lairName').value,'Submitted');assert.equal(h.element('lairName').dataset.dirty,undefined);
 }],
 ['failed save preserves drafts',async()=>{
   const h=await harness({fail:true});h.dirty('lairName','Unsaved');h.submit();await flush();
   assert.equal(h.element('lairName').value,'Unsaved');assert.equal(h.element('lairName').dataset.dirty,'1');assert.equal(h.element('lairNotice').textContent,'Rejected');
 }],
 ['same-encounter polling preserves drafts',async()=>{
   const h=await harness();h.dirty('lairNotes','Unsaved');h.render();assert.equal(h.element('lairNotes').value,'Unsaved');
 }],
 ['save controls remain guarded and are restored',async()=>{
   const h=await paused();assert.equal(h.element('saveLair').disabled,true);h.submit();assert.equal(h.writes.length,1);await h.finish();
   assert.equal(h.element('saveLair').disabled,false);assert.equal(h.element('resolveLair').disabled,true);
 }]
];
(async()=>{
 let failures=0;for(const [name,test]of cases){try{await test();console.log('PASS '+name);}catch(error){failures++;console.error('FAIL '+name+'\n'+error.stack);}}
 console.log(`${cases.length} tests; ${cases.length-failures} passed; ${failures} failed`);process.exitCode=failures?1:0;
})();
