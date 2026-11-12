const test=require('node:test'),assert=require('node:assert/strict');
const {fixture,applied,flush}=require('./campaign-switch-fixture.cjs');
test('empty selection and already-active validation do not mutate and recover by matching identity',async()=>{
 const h=fixture();await h.change('');assert.equal(h.select.value,'old');assert.equal(h.calls.length,0);
 assert.equal(h.records()[0].severity,'error');assert.equal(h.timers.size,0);await h.click();
 assert.equal(h.records().length,1);assert.equal(h.records()[0].severity,'info');assert.match(h.records()[0].text,/Old is already/);
 const p=h.change('new');assert.equal(h.records().length,0);await applied(h,p);
});
test('confirmation cancellation reverts, preserves existing warning and performs no request',async()=>{
 const h=fixture();h.context.confirmed=false;await h.change('new');assert.equal(h.select.value,'old');
 assert.equal(h.calls.length,0);assert.equal(h.confirmations[0],`Switch to campaign New?\n\n${h.context.REPLACE_WARNING}`);
});
test('exact encoded activation POST has no invented headers or payload; rejection is persistent',async()=>{
 const h=fixture(),p=h.change('a/b ?');assert.equal(h.calls[0].url,'/api/campaigns/a%2Fb%20%3F/activate');
 assert.equal(JSON.stringify(h.calls[0].options),JSON.stringify({method:'POST'}));h.calls[0].reject(new Error('Denied'));await p;
 assert.equal(h.records()[0].operation,'campaign.switch');assert.equal(h.records()[0].target,JSON.stringify(['campaign-switch','a/b ?']));
 assert.equal(h.records()[0].text,'Denied');assert.equal(h.timers.size,0);assert.equal(h.select.value,'old');assert.equal(h.loads.length,0);
});
test('successful retry resolves matching request error but preserves another target',async()=>{
 const h=fixture();let p=h.change('other');h.calls[0].reject(new Error('Other'));await p;
 p=h.change('new');h.calls[1].reject(new Error('Denied'));await p;p=h.change('new');await applied(h,p);
 assert.deepEqual(h.records().filter(r=>r.severity==='error').map(r=>r.text),['Other']);
 assert.match(h.records().find(r=>r.severity==='success').text,/Switched to campaign: New; opened battle setup default/);
 assert.equal(h.legacy.length,0);
});
test('button and dropdown duplicate submissions are blocked through refresh',async()=>{
 const h=fixture(),p=h.change('new');await h.click();assert.equal(h.calls.length,1);
 h.calls[0].resolve(h.answer());await flush();assert.equal(h.button.disabled,true);await h.click();
 assert.equal(h.calls.length,1);h.observe();h.loads[0].resolve();await p;assert.equal(h.button.disabled,false);
});
test('new selection, away-return, registry and encounter epoch suppress stale success/rejection',async()=>{
 for(const action of ['selection','return','registry','scope'])for(const reject of [false,true]){
  const h=fixture(),p=h.change('new');
  if(action==='selection')await h.change('other');
  if(action==='return'){await h.change('other');await h.change('new');}
  if(action==='registry')h.context.campaignData={active:'other',campaigns:[]};
  if(action==='scope'){h.observe('away','fight');h.observe('old','before');}
  const registry=h.context.campaignData,selected=h.select.value;
  if(reject)h.calls[0].reject(new Error('Obsolete'));else h.calls[0].resolve(h.answer());await p;
  assert.equal(h.context.campaignData,registry);assert.equal(h.select.value,selected);assert.equal(h.records().length,0);
  assert.equal(h.legacy.length,0);assert.equal(h.loads.length,0);assert.equal(h.button.disabled,false);
 }
});
test('newer same-target feedback supersedes old completion',async()=>{
 const h=fixture(),p=h.change('new');h.api.publish(h.api.begin({lane:'page',region:'campaign',operation:'campaign.switch',
  target:JSON.stringify(['campaign-switch','new']),label:'New attempt'}),{severity:'error',text:'Keep newer'});
 h.calls[0].resolve(h.answer());await p;assert.equal(h.records()[0].text,'Keep newer');assert.equal(h.loads.length,0);
});
test('expected activation arriving before response remains valid',async()=>{
 const h=fixture(),p=h.change('new');h.observe('new','default');await applied(h,p);assert.equal(h.context.campaignData.active,'new');
 assert.equal(h.records().filter(r=>r.severity==='success').length,1);assert.equal(h.legacy.length,0);
});
test('both opened and empty setup paths retain setup behavior with propagated refresh errors',async()=>{
 for(const opened of ['default',null]){const h=fixture(),p=h.change('new');await applied(h,p,opened);
  assert.equal(h.node('#setupName').value,opened||'');assert.equal(h.loads[0].flag,true);
  assert.equal(h.records()[0].text,'Switched to campaign: New'+(opened?'; opened battle setup default':''));}
});
test('prior disabled state is restored and rendering failure is separate from activation failure',async()=>{
 const h=fixture();h.button.disabled=true;h.context.renderCampaigns=()=>{throw new Error('View error');};
 const p=h.change('new');h.calls[0].resolve(h.answer());await p;
 assert.equal(h.button.disabled,true);assert.equal(h.records()[0].severity,'success');
 assert.equal(h.records()[1].operation,'campaign.switch.refresh');assert.match(h.records()[1].text,/View error/);
 assert.equal(h.context.campaignData.active,'new');assert.equal(h.calls.length,1);assert.equal(h.legacy.length,0);
});
