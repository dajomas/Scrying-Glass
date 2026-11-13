// Full statistics asset and original restoration harness; real controller/bootstrap, mock DOM/transport.
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const test=require('node:test');
const legacyPath=path.join(__dirname,'statistics-restoration.test.cjs');
const legacySource=fs.readFileSync(legacyPath,'utf8');
const boundary=legacySource.indexOf('(async()=>{');
assert(boundary>0,'original harness boundary');
const exported={exports:{}};
vm.runInNewContext(legacySource.slice(0,boundary)+'\nmodule.exports={harness,flush};',
 {require,__dirname,console,module:exported,setImmediate,process},{filename:legacyPath});
const {harness,flush}=exported.exports;
function setup(kind='characters') {
 const h=harness(),calls=[],alerts=[];
 if(kind==='monsters'){h.state.monsters=h.state.characters;h.state.characters=[];}
 h.context.alert=text=>alerts.push(text);
 const fetch=h.context.fetch;
 h.context.fetch=(url,options={})=>{calls.push({url,options});return fetch(url,options);};
 return Object.assign(h,{calls,alerts,records:()=>h.feedback.snapshot()});
}
const errorResponse=(text='Open failed')=>({ok:false,json:async()=>({detail:text})});
const stateResponse=h=>({ok:true,json:async()=>JSON.parse(JSON.stringify(h.state))});
function holdFirst(h) {
 const fetch=h.context.fetch;let release,first=true;
 h.context.fetch=(...args)=>{
  if(!first)return fetch(...args);first=false;
  return new Promise(resolve=>{release=resolve;});
 };
 return response=>release(response);
}
for(const kind of ['characters','monsters']) test(`${kind}: open failure is persistent, explicit and does not alert or mutate`,async()=>{
 const h=setup(kind);h.setFail(true);h.open();await flush();h.tick(10000);
 assert.equal(h.records().length,1);const record=h.records()[0];
 assert.equal(record.operation,'statistics.open');assert.equal(record.target,'c');assert.equal(record.region,'global');assert.equal(record.severity,'error');
 assert.equal(record.text,'Encounter changed; reopen Restore statistics');
 assert.equal(h.alerts.length,0);assert.equal(h.requests.length,0);assert.equal(h.el('statisticsModal').hidden,true);
 assert.equal(h.feedback.snapshot().filter(r=>String(r.operation).startsWith('legacy.')).map(r=>r.region).length,0);
});
test('matching retry opens and clears only its error',async()=>{
 const h=setup();h.setFail(true);h.open();await flush();
 const other=h.feedback.begin({region:'global',operation:'other.operation',target:'c',label:'Other'});
 h.feedback.publish(other,{severity:'error',text:'Other failed'});
 h.setFail(false);h.open();await flush();
 assert.deepEqual(h.records().map(r=>r.text),['Other failed']);assert.equal(h.el('statisticsModal').hidden,false);assert.equal(h.requests.length,0);
});
test('another combatant success cannot clear an independent open error',async()=>{
 const h=setup();h.setFail(true);h.open();await flush();
 h.state.characters.push({...h.state.characters[0],id:'b',name:'Beta'});
 h.button.dataset.statistics='b';h.setFail(false);h.open();await flush();
 assert.equal(h.records().length,1);assert.equal(h.records()[0].target,'c');assert.equal(h.el('statisticsTitle').textContent,'Restore statistics: Beta');
});
test('missing combatant is a persistent targeted error without mutation',async()=>{
 const h=setup();h.button.dataset.statistics='gone';h.open();await flush();
 assert.equal(h.records()[0].text,'Combatant no longer exists');assert.equal(h.records()[0].target,'gone');assert.equal(h.requests.length,0);assert.equal(h.alerts.length,0);
});
test('network error retains its wording and never retries',async()=>{
 const h=setup();let calls=0;h.context.fetch=async()=>{calls++;throw new Error('Offline');};
 h.open();await flush();assert.equal(calls,1);assert.equal(h.records()[0].text,'Offline');assert.equal(h.requests.length,0);
});
for(const success of [false,true]) test(`old-scope ${success?'success':'failure'} cannot publish or open the modal`,async()=>{
 const h=setup(),release=holdFirst(h);h.open();h.scope('other','elsewhere');
 const ticket=h.feedback.begin({region:'global',operation:'new.operation',target:'new',label:'New'});
 h.feedback.publish(ticket,{severity:'error',text:'New scope error'});
 release(success?stateResponse(h):errorResponse('Old scope error'));await flush();
 assert.deepEqual(h.records().map(r=>r.text),['New scope error']);assert.equal(h.el('statisticsModal').hidden,true);assert.equal(h.el('statisticsFields').children.length,0);
});
for(const success of [false,true]) test(`superseded open ${success?'success':'failure'} cannot replace current same-target error`,async()=>{
 const h=setup(),release=holdFirst(h);h.open();h.setFail(true);h.open();await flush();
 release(success?stateResponse(h):errorResponse('Old error'));await flush();
 assert.equal(h.records().length,1);assert.equal(h.records()[0].text,'Encounter changed; reopen Restore statistics');assert.equal(h.el('statisticsModal').hidden,true);
});
for(const success of [false,true]) test(`Close invalidates a pending open ${success?'success':'failure'}`,async()=>{
 const h=setup(),release=holdFirst(h);h.open();h.el('statisticsClose').onclick();
 release(success?stateResponse(h):errorResponse());await flush();
 assert.equal(h.records().length,0);assert.equal(h.el('statisticsModal').hidden,true);assert.equal(h.requests.length,0);
});
test('away-and-back scope epochs cannot revive pending success',async()=>{
 const h=setup(),release=holdFirst(h);h.open();h.scope('other','elsewhere');h.scope('1','test');
 release(stateResponse(h));await flush();assert.equal(h.records().length,0);assert.equal(h.el('statisticsModal').hidden,true);
});
test('successful open remains silent and focuses the original dialog',async()=>{
 const h=setup();h.open();await flush();assert.equal(h.records().length,0);assert.equal(h.el('statisticsModal').hidden,false);
 assert.equal(h.el('statisticsModal').children[0].focused,true);h.el('statisticsClose').onclick();assert.equal(h.button.focused,true);
});
test('busy restoration still ignores additional open attempts',async()=>{
 const h=setup();h.open();await flush();let release;h.setHold(new Promise(resolve=>{release=resolve;}));
 h.el('statisticsRestore').onclick();const before=h.calls.length;h.open();assert.equal(h.calls.length,before);
 h.setHold(null);release();await flush();assert.equal(h.requests.length,1);assert.equal(h.records().length,0);
});
test('restore request failures stay modal-local, not statistics.open errors',async()=>{
 const h=setup();h.open();await flush();h.setFail(true);h.el('statisticsRestore').onclick();await flush();
 assert.match(h.el('statisticsNotice').textContent,/Encounter changed/);assert.equal(h.records().length,0);assert.equal(h.requests.length,1);assert.equal(h.alerts.length,0);
});
test('open preserves its GET, no-store, response shape and absence of writes',async()=>{
 const h=setup();h.open();await flush();assert.equal(h.calls.length,1);assert.equal(h.calls[0].url,'/api/state');
 assert.equal(h.calls[0].options.cache,'no-store');assert.equal(h.calls[0].options.body,undefined);assert.equal(h.requests.length,0);
});
test('render failure reports through the same ticket and a valid retry resolves it',async()=>{
 const h=setup(),create=h.context.document.createElement;
 h.context.document.createElement=()=>{throw new Error('Render failed');};h.open();await flush();
 assert.equal(h.records().length,1);assert.equal(h.records()[0].text,'Render failed');
 h.context.document.createElement=create;h.open();await flush();assert.equal(h.records().length,0);assert.equal(h.el('statisticsModal').hidden,false);assert.equal(h.requests.length,0);
});
