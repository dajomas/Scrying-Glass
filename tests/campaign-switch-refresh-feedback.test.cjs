const test=require('node:test'),assert=require('node:assert/strict');
const {fixture,applied,flush}=require('./campaign-switch-fixture.cjs');
async function posted(h){h.calls[0].resolve(h.answer());await flush();}
function seed(h,operation='other',target='other'){
 return h.api.publish(h.api.begin({lane:'page',region:'campaign',operation,target,label:'Keep newer'}),{severity:'error',text:'Keep newer error'});
}
test('success precedes refresh and expires after exactly three seconds',async()=>{
 const h=fixture(),p=h.change('new');await posted(h);assert.equal(h.button.disabled,true);
 assert.equal(h.records()[0].operation,'campaign.switch');assert.equal(h.records()[0].severity,'success');
const timer=[...h.timers.values()][0];assert.equal(timer.delay,3000);
 h.observe();h.loads[0].resolve();await p;assert.equal(h.records().length,1);timer.fn();assert.equal(h.records().length,0);
});
test('refresh failure stays actionable after success expires and does not replay activation',async()=>{
 const h=fixture();seed(h);const p=h.change('new');await posted(h);h.loads[0].reject(new Error('Offline'));await p;
 const error=h.records().find(r=>r.operation==='campaign.switch.refresh');assert.equal(error.severity,'error');
 assert.match(error.text,/switched and activated.*Offline.*do not switch/);assert.equal(h.context.campaignData.active,'new');
 for(const timer of [...h.timers.values()])timer.fn();assert.equal(h.records().length,2);assert.equal(h.calls.length,1);
 await h.click();assert.equal(h.calls.length,1);assert.equal(h.button.disabled,false);
});
test('new selection, leave-return and registry suppress late refresh errors and UI work',async()=>{
 for(const action of ['selection','return','scope','registry']){
  const h=fixture(),p=h.change('new');await posted(h);
  if(action==='selection')await h.change('old');
  if(action==='return'){await h.change('old');await h.change('new');}
  if(action==='scope'){h.observe('elsewhere','x');h.observe('new','default');}
  if(action==='registry')h.context.campaignData={active:'new',campaigns:[]};
  const selected=h.select.value,registry=h.context.campaignData;
  h.loads[0].reject(new Error('Obsolete'));await p;
  assert.equal(h.select.value,selected);assert.equal(h.context.campaignData,registry);
  assert.ok(!h.records().some(r=>r.text.includes('Obsolete')));assert.equal(h.calls.length,1);
 }
});
test('empty setup branch does not render after a superseding selection',async()=>{
 const h=fixture();let count=0;h.context.renderActiveBattleSetup=()=>{count++;};
 const p=h.change('new');h.calls[0].resolve(h.answer('new',null));await flush();await h.change('old');
 h.loads[0].resolve();await p;assert.equal(count,0);assert.equal(h.select.value,'old');
});
test('newer refresh ticket survives an older completion',async()=>{
 const h=fixture(),p=h.change('new');await posted(h);seed(h,'campaign.switch.refresh',JSON.stringify(['campaign-switch','new']));
 h.loads[0].reject(new Error('Old failure'));await p;assert.equal(h.records().at(-1).text,'Keep newer error');
});
test('successful refresh resolves only its matching campaign refresh failure',async()=>{
 const h=fixture();seed(h,'campaign.switch.refresh',JSON.stringify(['campaign-switch','new']));seed(h);
 const p=h.change('new');await applied(h,p);assert.deepEqual(h.records().filter(r=>r.severity==='error').map(r=>r.text),['Keep newer error']);
});
test('stale success timer cannot remove newer matching error',async()=>{
 const h=fixture(),p=h.change('new');await applied(h,p);const old=[...h.timers.values()][0];
 seed(h,'campaign.switch',JSON.stringify(['campaign-switch','new']));old.fn();assert.equal(h.records()[0].text,'Keep newer error');
});
test('unapplied refresh is not falsely reported as recovered',async()=>{
 const h=fixture(),p=h.change('new');await posted(h);h.loads[0].resolve();await p;
 assert.match(h.records().at(-1).text,/state was not applied/);assert.equal(h.context.campaignData.active,'new');
});
test('post-activation label/render failures remain applied-refresh failures',async()=>{
 const h=fixture(),p=h.change('new');h.context.activeCampaign=()=>{throw new Error('Label failure');};
 h.calls[0].resolve(h.answer());await p;assert.equal(h.context.campaignData.active,'new');
 assert.equal(h.records()[0].operation,'campaign.switch.refresh');assert.match(h.records()[0].text,/Label failure/);
 assert.equal(h.button.disabled,false);assert.equal(h.calls.length,1);
});
test('superseding refresh prevents late empty-setup rendering',async()=>{
 const h=fixture();let count=0;h.context.renderActiveBattleSetup=()=>{count++;};
 const p=h.change('new');h.calls[0].resolve(h.answer('new',null));await flush();
 seed(h,'campaign.switch.refresh',JSON.stringify(['campaign-switch','new']));
 h.observe('new',null);h.loads[0].resolve();await p;
 assert.equal(count,0);assert.equal(h.records().at(-1).text,'Keep newer error');
});
