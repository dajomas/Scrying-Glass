// Complete 080 with production controller; DOM, transport, context and legacy owners are mocked.
const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const {createController} = require(path.join(root, 'static/admin-feedback-controller.js'));
const source = fs.readFileSync(path.join(root, 'static/admin/080-source.js'), 'utf8');
const {harness,deferred,flush,applied,finish,other}=require('./campaign-feedback-fixture.cjs');
test('validation and confirmation cancellation preserve drafts without POST',async()=>{
    const h=harness();other(h);h.values(' ');await h.submit();assert.equal(h.calls.length,0);
    assert.equal(h.records().at(-1).operation,'campaign.create.validation');assert.equal(h.timers.size,0);
    h.values();h.form.valid=false;await h.submit();assert.equal(h.calls.length,0);
    h.form.valid=true;h.context.confirmed=false;await h.submit();assert.equal(h.records().length,1);
    assert.match(h.confirmations[0],/Create and switch to campaign New/);assert.match(h.confirmations[0],/Unsaved changes will be lost/);
    assert.equal(h.form.elements.name.value,' New ');
});
test('exact POST, early success, own transition and three-second pane expiry',async()=>{
    const h=harness(),p=h.submit();assert.equal(h.calls[0].url,'/api/campaigns');assert.equal(h.calls[0].options.method,'POST');
    assert.equal(h.calls[0].options.headers['Content-Type'],'application/json');
    assert.deepEqual(JSON.parse(h.calls[0].options.body),{name:'New',description:'Desc',activate:true});
    await applied(h);assert.equal(h.records()[0].severity,'success');assert.equal(h.context.campaignModal.hidden,true);
    assert.equal(h.loads[0].flag,true);await finish(h,p);const timer=[...h.timers.values()][0];assert.equal(timer.delay,3000);
    timer.fn();assert.equal(h.records().length,0);
});
test('request rejection preserves inputs and matching retry preserves unrelated error',async()=>{
    const h=harness();other(h);let p=h.submit();h.calls[0].reject(new Error('Denied'));await p;
    assert.equal(h.context.campaignModal.hidden,false);assert.equal(h.form.elements.name.value,' New ');assert.equal(h.loads.length,0);
    p=h.submit();await applied(h);await finish(h,p);assert.deepEqual(h.records().filter(x=>x.severity==='error').map(x=>x.text),['Keep newer error']);
});
test('applied creation plus refresh failure persists with no mutation replay',async()=>{
    const h=harness();other(h);const p=h.submit();await applied(h);h.loads[0].reject(new Error('Offline'));await p;
    assert.match(h.records().at(-1).text,/created and activated.*do not create the campaign again/);
    for(const timer of [...h.timers.values()])timer.fn();assert.equal(h.records().length,2);assert.equal(h.calls.length,1);
    assert.equal(h.context.campaignData.active,'new');assert.equal(h.node('#campaignSubmit').disabled,false);
});
test('duplicate protection covers POST, refresh and edit delegation',async()=>{
    const h=harness(),p=h.submit();await h.submit();assert.equal(h.calls.length,1);await applied(h);await h.submit();
    h.open(true);await h.submit();assert.equal(h.edits.length,0);h.loads[0].resolve();await p;
    const saved=h.submit();assert.equal(h.calls.length,2);assert.equal(h.calls[1].options.method,'PATCH');
    h.calls[1].resolve(h.result);await saved;assert.equal(h.edits.length,0);
});
test('new input, including edit-revert, suppresses old success and retains modal',async()=>{
    for(const revert of [false,true]){const h=harness(),p=h.submit();h.values('New draft');if(revert)h.values();
        await applied(h);assert.equal(h.records().length,0);assert.equal(h.context.campaignModal.hidden,false);await finish(h,p);
        assert.equal(h.form.elements.name.value,revert?' New ':'New draft');}
});
test('cancel/reopen and unrelated scope suppress obsolete POST completion',async()=>{
    for(const action of ['cancel','reopen','scope']){const h=harness(),p=h.submit();
        if(action==='scope')h.observe('other','fight');else h.node('#cancelCampaign').onclick();
        if(action==='reopen'){h.open(true);h.values('Keep edit');}h.calls[0].resolve(h.result);await p;
        assert.equal(h.records().length,0);assert.equal(h.loads.length,0);assert.equal(h.context.campaignData.active,'old');
        if(action==='reopen')assert.equal(h.form.elements.name.value,'Keep edit');}
});
test('expected transition may arrive before POST response',async()=>{
    const h=harness(),p=h.submit();h.observe();await applied(h);h.loads[0].resolve();await p;
    assert.equal(h.records()[0].severity,'success');assert.equal(h.records().length,1);
});
test('leave-return, reopened modal and newer feedback suppress late refresh errors',async()=>{
    for(const action of ['scope','reopen','feedback']){const h=harness(),p=h.submit();await applied(h);
        if(action==='scope'){h.observe('other','fight');h.observe();}
        if(action==='reopen'){h.open();h.values('Keep new');}
        if(action==='feedback')other(h,{operation:'campaign.create.refresh',target:h.records()[0].target});
        h.loads[0].reject(new Error('Obsolete'));await p;assert.ok(!h.records().some(x=>x.text.includes('Obsolete')));}
});
test('older success timer cannot clear newer same-identity error',async()=>{
    const h=harness(),p=h.submit();await applied(h);await finish(h,p);const record=h.records()[0],timer=[...h.timers.values()][0];
    other(h,{operation:record.operation,target:record.target});timer.fn();assert.equal(h.records()[0].text,'Keep newer error');
});
test('no-setup branch, unapplied state and disabled-state restoration are guarded',async()=>{
    const h=harness();h.result.opened_setup=null;h.node('#campaignSubmit').disabled=true;const p=h.submit();await applied(h);
    assert.equal(h.node('#setupName').value,'');h.loads[0].resolve();await p;
    assert.match(h.records().at(-1).text,/state was not applied/);assert.equal(h.node('#campaignSubmit').disabled,true);
});
test('newer input suppresses obsolete request rejection',async()=>{
    const h=harness(),p=h.submit();h.values('Keep new');h.calls[0].reject(new Error('Obsolete'));await p;
    assert.equal(h.records().length,0);assert.equal(h.form.elements.name.value,'Keep new');
});
test('empty setup success has no invented opened-setup suffix',async()=>{
    const h=harness();h.result.opened_setup=null;const p=h.submit();await applied(h);
    h.observe('new',null);h.loads[0].resolve();await p;
    assert.equal(h.records()[0].text,'Created and switched to campaign: New');assert.equal(h.records().length,1);
});
test('isolated fragment readers without campaign owners keep startup wiring',()=>{
    let loads=0,setups=0,previews=0;
    const context=vm.createContext({document:{querySelector:()=>({addEventListener(){}})},
        installColorPreview(){previews++;},load(){loads++;},setups(){setups++;}});
    assert.doesNotThrow(()=>vm.runInContext(source,context));
    assert.equal(loads,1);assert.equal(setups,1);assert.equal(previews,4);
});
