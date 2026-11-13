const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {fixture,seed,deferred,flush}=require('./campaign-delete-fixture.cjs');
const source=fs.readFileSync(require('node:path').join(__dirname,'../static/admin/040-source.js'),'utf8');
const helper=source.slice(source.indexOf('async function applyOpenedSetup('),source.indexOf('const REPLACE_WARNING'));
function realHelper(h){h.context.renderCampaigns=()=>{};h.context.syncActiveBattleSetupControls=()=>{};
 h.context.renderActiveBattleSetup=()=>{};vm.runInContext(helper,h.context);}
test('success precedes refresh, lasts exactly 3000ms and busy spans completion',async()=>{
 const h=fixture(),gate=deferred();h.context.applyOpenedSetup=()=>gate.promise;
 const p=h.submit();h.calls[0].resolve(h.result);await flush();
 assert.equal(h.records()[0].severity,'success');assert.equal(h.node('#campaignDeleteForm .danger').disabled,true);
 const timer=[...h.timers.values()][0];assert.equal(timer.ms,3000);gate.resolve('');await p;
 timer.fn();assert.equal(h.records().length,0);assert.equal(h.calls.length,1);
});
test('refresh failure persists after success expiry, preserves applied mutation and never replays',async()=>{
 const h=fixture();seed(h);h.context.applyOpenedSetup=async()=>{throw new Error('Offline');};
 const p=h.submit();h.calls[0].resolve(h.result);await p;
 const error=h.records().find(r=>r.operation==='campaign.delete.refresh');assert.match(error.text,/Campaign deleted.*Offline.*Reload.*do not delete/);
 for(const timer of [...h.timers.values()])timer.fn();assert.equal(h.records().length,2);
 assert.equal(h.context.campaignData,h.result);assert.equal(h.calls.length,1);assert.equal(h.node('#campaignDeleteForm .danger').disabled,false);
});
test('obsolete success timer cannot remove a newer matching DELETE error',async()=>{
 const h=fixture(),p=h.submit();h.calls[0].resolve(h.result);await p;const timer=[...h.timers.values()][0];
 seed(h,'campaign.delete',JSON.stringify(['campaign-delete','b']));timer.fn();assert.equal(h.records()[0].text,'Keep newer error');
});
test('actual setup helper forwards owner and strict errors for opened/empty paths',async()=>{
 for(const setup of ['before',null]){const h=fixture();realHelper(h);h.result.opened_setup=setup;let strict,owner;
  h.context.load=async(flag,current)=>{strict=flag;owner=current;h.observe('a',setup);};
  const p=h.submit();h.calls[0].resolve(h.result);await p;assert.equal(strict,true);assert.equal(typeof owner,'function');
  assert.equal(h.node('#setupName').value,setup||'');assert.ok(!h.records().some(r=>r.operation==='campaign.delete.refresh'));
 }
});
test('actual helper cannot render an empty setup after dialog reopening during load',async()=>{
 const h=fixture(),gate=deferred();realHelper(h);h.result.opened_setup=null;let renders=0;
 h.context.renderActiveBattleSetup=()=>renders++;h.context.load=()=>gate.promise;
 const p=h.submit();h.calls[0].resolve(h.result);await flush();h.open();const selected=h.node('#campaignDeleteTarget').value;
 gate.resolve();await p;assert.equal(renders,0);assert.equal(h.node('#campaignDeleteTarget').value,selected);
 assert.equal(h.modal.hidden,false);assert.ok(!h.records().some(r=>r.operation==='campaign.delete.refresh'));
});
test('default setup helper keeps legacy load and return behavior for other callers',async()=>{
 for(const setup of ['before',null]){const h=fixture();realHelper(h);let flag='unset';h.context.load=async value=>{flag=value;};
  const text=await h.context.applyOpenedSetup({...h.result,opened_setup:setup});assert.equal(flag,undefined);
  assert.equal(text,setup?'; opened battle setup before':'');assert.equal(h.node('#setupName').value,setup||'');}
});
test('render failure after DELETE is explicitly a refresh failure',async()=>{
 const h=fixture();realHelper(h);h.context.renderCampaigns=()=>{throw new Error('View exploded');};
 const p=h.submit();h.calls[0].resolve(h.result);await p;assert.equal(h.context.campaignData,h.result);
 assert.match(h.records().find(r=>r.operation==='campaign.delete.refresh').text,/View exploded/);assert.equal(h.calls.length,1);
});
test('unapplied active-campaign refresh is not falsely resolved',async()=>{
 const h=fixture();h.result.active='c';h.result.opened_setup='default';const p=h.submit();h.calls[0].resolve(h.result);await p;
 assert.match(h.records().find(r=>r.operation==='campaign.delete.refresh').text,/state was not applied/);
 assert.equal(h.context.campaignData.active,'c');assert.equal(h.calls.length,1);
});
