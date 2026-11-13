const test=require('node:test'),assert=require('node:assert/strict');
const {fixture,seed,deferred,flush}=require('./campaign-delete-fixture.cjs');
const target=JSON.stringify(['campaign-delete','b']);
async function held(){const h=fixture(),gate=deferred();h.context.applyOpenedSetup=()=>gate.promise;
 const p=h.submit();h.calls[0].resolve(h.result);await flush();return {h,gate,p};}
test('own modal close and applied registry do not suppress a relevant explicit success',async()=>{
 const {h,gate,p}=await held();assert.equal(h.context.campaignData,h.result);assert.equal(h.modal.hidden,true);
 assert.equal(h.node('#campaignDeleteForm .danger').disabled,true);gate.resolve('; opened battle setup before');await p;
 assert.match(h.records().find(r=>r.severity==='success').text,/Deleted campaign: Victim.*opened battle setup before/);assert.equal(h.calls.length,1);
 assert.equal(h.node('#campaignDeleteForm .danger').disabled,false);
});
test('relevant helper rejection reports applied-deletion refresh error, not DELETE failure',async()=>{
 const {h,gate,p}=await held();gate.reject(new Error('Legacy refresh'));await p;
 assert.match(h.records().find(r=>r.operation==='campaign.delete.refresh').text,/Legacy refresh.*do not delete/);assert.equal(h.context.campaignData,h.result);
 assert.equal(h.records().filter(r=>r.operation==='campaign.delete'&&r.severity==='success').length,1);assert.equal(h.calls.length,1);
});
test('reopened dialog, newer options, registry and leave-return suppress late success/error',async()=>{
 for(const action of ['reopen','revision','registry','scope'])for(const failure of [false,true]){
  const {h,gate,p}=await held();
  if(action==='reopen'){h.result.campaigns.push({id:'b',name:'Victim',setups:['one']});h.open();h.change('#campaignDeleteTarget','b');}
  if(action==='revision')h.node('#campaignDeleteForm').listeners.reset[0]();
  if(action==='registry')h.context.campaignData={...h.result};
  if(action==='scope'){h.observe('other','x');h.observe('a','before');}
  const registry=h.context.campaignData,hidden=h.modal.hidden,selection=h.node('#campaignDeleteTarget').value;
  if(failure)gate.reject(new Error('Obsolete'));else gate.resolve('');await p;
  assert.equal(h.legacy.length,0);assert.ok(!h.records().some(r=>r.text.includes('Obsolete')));assert.equal(h.context.campaignData,registry);assert.equal(h.modal.hidden,hidden);
  assert.equal(h.node('#campaignDeleteTarget').value,selection);assert.equal(h.calls.length,1);
 }
});
test('independent refresh ownership protects newer same-target feedback',async()=>{
 for(const failure of [false,true]){const {h,gate,p}=await held();seed(h,'campaign.delete.refresh',target);
  if(failure)gate.reject(new Error('Obsolete'));else gate.resolve('');await p;
  assert.equal(h.legacy.length,0);assert.equal(h.records().at(-1).text,'Keep newer error');}
});
test('expected activation during follow-up remains relevant for opened and empty setups',async()=>{
 for(const setup of ['default',null]){const h=fixture(),gate=deferred();h.result.active='c';h.result.opened_setup=setup;
  h.context.applyOpenedSetup=()=>gate.promise;const p=h.submit();h.calls[0].resolve(h.result);await flush();
  h.observe('c',setup);gate.resolve('');await p;assert.equal(h.records().filter(r=>r.severity==='success').length,1);assert.equal(h.legacy.length,0);assert.equal(h.context.campaignData.active,'c');}
});
test('matching refresh resolution preserves unrelated target and operation feedback',async()=>{
 const h=fixture();seed(h,'campaign.delete.refresh',target);seed(h,'campaign.delete.refresh','other-target');seed(h);
 const p=h.submit();h.calls[0].resolve(h.result);await p;
 assert.equal(h.records().filter(r=>r.severity==='error').length,2);assert.ok(h.records().filter(r=>r.severity==='error').every(r=>r.target!==target));assert.equal(h.records().filter(r=>r.severity==='success').length,1);assert.equal(h.legacy.length,0);
});
test('duplicate DELETE stays blocked until follow-up completes, including after reopen',async()=>{
 const {h,gate,p}=await held();h.open();await h.submit();assert.equal(h.calls.length,1);gate.resolve('');await p;
 assert.equal(h.node('#campaignDeleteForm .danger').disabled,false);
});
test('persistent request failure, confirmation, method/query and retry safeguards remain',async()=>{
 const h=fixture();h.change('#campaignDeleteMoveTo','c');let p=h.submit();
 assert.equal(h.calls[0].url,'/api/campaigns/b?move_to=c');assert.equal(JSON.stringify(h.calls[0].options),JSON.stringify({method:'DELETE'}));
 assert.equal(h.confirms[0],'Delete campaign Victim?\n\nIts 1 battle setup(s) will be moved to Destination.');
 h.calls[0].reject(new Error('Denied'));await p;assert.equal(h.records()[0].text,'Denied');assert.equal(h.modal.hidden,false);
 p=h.submit();h.calls[1].resolve(h.result);await p;assert.equal(h.records().filter(r=>r.severity==='error').length,0);assert.equal(h.records().filter(r=>r.severity==='success').length,1);assert.equal(h.legacy.length,0);
});
