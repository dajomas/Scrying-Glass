const test=require('node:test'),assert=require('node:assert/strict');
const {fixture,seed,deferred,flush}=require('./campaign-delete-fixture.cjs');
async function ok(h,p){h.calls.at(-1).resolve(h.result);await p;}
test('last-campaign opening validation persists and resolves after another campaign exists',()=>{
 const h=fixture();h.modal.hidden=true;const all=h.context.campaignData.campaigns;h.context.campaignData.campaigns=[all[0]];h.open();
 assert.equal(h.records()[0].operation,'campaign.delete.open');assert.equal(h.records()[0].text,'The last remaining campaign cannot be deleted');
 assert.equal(h.modal.hidden,true);assert.equal(h.calls.length,0);assert.equal(h.timers.size,0);
 h.context.campaignData.campaigns=all;h.open();assert.equal(h.records().length,0);assert.equal(h.modal.hidden,false);
 assert.equal(h.node('#campaignDeleteTarget').value,'b');assert.equal(h.node('#campaignDeleteAction').value,'move');
});
test('missing campaign and invalid move destination validate without DELETE; matching correction resolves',async()=>{
 const h=fixture();h.change('#campaignDeleteTarget','');await h.submit();assert.equal(h.records()[0].text,'Choose a campaign to delete');
 h.change('#campaignDeleteTarget','b');h.change('#campaignDeleteMoveTo','');await h.submit();
 assert.equal(h.records()[0].text,'Choose another campaign to move the battle setups to');h.change('#campaignDeleteMoveTo','b');await h.submit();
 assert.equal(h.calls.length,0);h.change('#campaignDeleteMoveTo','c');const p=h.submit();assert.equal(h.records().length,0);await ok(h,p);
});
test('move, permanent-delete and empty campaign keep exact endpoint/query/options',async()=>{
 for(const mode of ['move','delete','empty']){
  const h=fixture(mode==='empty'?[]:['one']);h.context.campaignData.campaigns[1].id='b /?';h.open();
  h.change('#campaignDeleteTarget','b /?');h.change('#campaignDeleteAction',mode==='delete'?'delete':'move');
  if(mode==='move'){h.context.campaignData.campaigns[2].id='c /?';h.change('#campaignDeleteMoveTo','c /?');}
  const p=h.submit(),call=h.calls[0];assert.equal(call.url,'/api/campaigns/b%20%2F%3F'+(mode==='move'?'?move_to=c%20%2F%3F':mode==='delete'?'?delete_setups=true':''));
  assert.equal(JSON.stringify(call.options),JSON.stringify({method:'DELETE'}));await ok(h,p);assert.equal(h.calls.length,1);
 }
});
test('confirmation cancellation preserves modal, options and exact move warning',async()=>{
 const h=fixture();h.change('#campaignDeleteMoveTo','c');h.context.confirmed=false;await h.submit();
 assert.equal(h.confirms[0],'Delete campaign Victim?\n\nIts 1 battle setup(s) will be moved to Destination.');
 assert.equal(h.modal.hidden,false);assert.equal(h.node('#campaignDeleteMoveTo').value,'c');assert.equal(h.calls.length,0);
});
test('active and destructive confirmations retain replacement/permanent-deletion warnings',async()=>{
 const h=fixture();h.change('#campaignDeleteTarget','a');h.change('#campaignDeleteAction','delete');h.context.confirmed=false;await h.submit();
 assert.equal(h.confirms[0],`Active is the active campaign. After deleting it another campaign becomes active.\n\nIts 1 battle setup(s) will be PERMANENTLY DELETED: active\n\n${h.context.REPLACE_WARNING}`);
 assert.equal(h.calls.length,0);
});
test('DELETE rejection retains dialog/options and persistent campaign identity',async()=>{
 const h=fixture();h.change('#campaignDeleteMoveTo','c');const p=h.submit();h.calls[0].reject(new Error('Forbidden'));await p;
 assert.equal(h.records()[0].operation,'campaign.delete');assert.equal(h.records()[0].target,JSON.stringify(['campaign-delete','b']));
 assert.equal(h.records()[0].text,'Forbidden');assert.equal(h.timers.size,0);assert.equal(h.modal.hidden,false);
 assert.equal(h.node('#campaignDeleteMoveTo').value,'c');assert.equal(h.node('#campaignDeleteForm .danger').disabled,false);assert.equal(h.follow.length,0);
});
test('successful retry resolves only matching delete error, preserving other target errors',async()=>{
 const h=fixture();seed(h);let p=h.submit();h.calls[0].reject(new Error('Denied'));await p;
 p=h.submit();await ok(h,p);assert.deepEqual(h.records().filter(r=>r.severity==='error').map(r=>r.text),['Keep newer error']);
 assert.equal(h.modal.hidden,true);assert.equal(h.follow.length,1);assert.equal(h.records().find(r=>r.severity==='success').text,'Deleted campaign: Victim (moved 1 setup(s)); opened battle setup before');
});
test('cancel, Escape/reopen, same-dialog reopen and changed target/options suppress old responses',async()=>{
 for(const action of ['cancel','escape','reopen','target','action','destination','return','reset','registry','scope'])for(const reject of [false,true]){
  const h=fixture(),p=h.submit();
  if(action==='cancel')h.node('#cancelCampaignDelete').onclick();
  if(action==='escape'){h.modal.hidden=true;h.open();}
  if(action==='reopen')h.open();
  if(action==='target')h.change('#campaignDeleteTarget','c');
  if(action==='action')h.change('#campaignDeleteAction','delete');
  if(action==='destination')h.change('#campaignDeleteMoveTo','c');
  if(action==='return'){h.change('#campaignDeleteAction','delete');h.change('#campaignDeleteAction','move');}
  if(action==='reset')h.node('#campaignDeleteForm').listeners.reset[0]();
  if(action==='registry')h.context.campaignData={active:'a',campaigns:[]};
  if(action==='scope'){h.observe('other','x');h.observe('a','before');}
  const registry=h.context.campaignData,hidden=h.modal.hidden,target=h.node('#campaignDeleteTarget').value;
  if(reject)h.calls[0].reject(new Error('Obsolete'));else h.calls[0].resolve(h.result);await p;
  assert.equal(h.context.campaignData,registry);assert.equal(h.modal.hidden,hidden);assert.equal(h.node('#campaignDeleteTarget').value,target);
  assert.equal(h.records().length,0);assert.equal(h.follow.length,0);assert.equal(h.node('#campaignDeleteForm .danger').disabled,false);
 }
});
test('newer same-operation feedback supersedes an older completion',async()=>{
 const h=fixture(),p=h.submit();seed(h,'campaign.delete',JSON.stringify(['campaign-delete','b']));await ok(h,p);
 assert.equal(h.records()[0].text,'Keep newer error');assert.equal(h.follow.length,0);assert.equal(h.modal.hidden,false);
});
test('duplicates are blocked through retained follow-up, including a reopened dialog',async()=>{
 const h=fixture(),gate=deferred();h.context.applyOpenedSetup=()=>gate.promise;
 const p=h.submit();await h.submit();assert.equal(h.calls.length,1);h.calls[0].resolve(h.result);await flush();
 assert.equal(h.node('#campaignDeleteForm .danger').disabled,true);h.open();await h.submit();assert.equal(h.calls.length,1);
 gate.resolve('');await p;assert.equal(h.node('#campaignDeleteForm .danger').disabled,false);
});
test('prior disabled state is restored and legacy follow-up errors are not DELETE errors',async()=>{
 const h=fixture();h.node('#campaignDeleteForm .danger').disabled=true;h.context.applyOpenedSetup=async()=>{throw new Error('Legacy refresh');};
 const p=h.submit();await ok(h,p);assert.equal(h.context.campaignData,h.result);assert.equal(h.records().find(r=>r.operation==='campaign.delete').severity,'success');
 assert.match(h.records().find(r=>r.operation==='campaign.delete.refresh').text,/Legacy refresh.*do not delete/);assert.equal(h.node('#campaignDeleteForm .danger').disabled,true);assert.equal(h.calls.length,1);
});
test('the expected active-campaign transition before DELETE response remains allowed',async()=>{
 const h=fixture();h.change('#campaignDeleteTarget','a');h.result.active='c';h.result.opened_setup='default';
 const p=h.submit();h.observe('c','default');await ok(h,p);assert.equal(h.context.campaignData.active,'c');assert.equal(h.follow.length,1);
});
