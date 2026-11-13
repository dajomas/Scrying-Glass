const test=require('node:test'),assert=require('node:assert/strict');
const {harness,other}=require('./campaign-feedback-fixture.cjs');
function fixture(id='edit') {
    const h=harness();h.context.openCampaignModal({id,name:'Old'});h.values(' Updated ',' Description ');
    h.node('#campaignSelect').value=id;return h;
}
async function ok(h,p){h.calls.at(-1).resolve({active:'old',campaigns:[{id:'edit',name:'Updated'}]});await p;}
test('edit selection validation is persistent and resolves on a valid selection',()=>{
    const h=harness();h.node('#editCampaign').onclick();assert.equal(h.records()[0].operation,'campaign.edit.open');
    assert.equal(h.timers.size,0);h.node('#campaignSelect').value='edit';h.node('#editCampaign').onclick();
    assert.equal(h.records().length,0);assert.equal(h.context.campaignEditing,'edit');
});
test('empty name and native form validation block PATCH; matching validation resolves',async()=>{
    const h=fixture();h.values(' ');await h.submit();assert.equal(h.calls.length,0);
    assert.equal(h.records()[0].operation,'campaign.edit.validation');h.values();h.form.valid=false;await h.submit();
    assert.equal(h.calls.length,0);h.form.valid=true;const p=h.submit();assert.equal(h.records().length,0);await ok(h,p);
});
test('PATCH has exact encoded target and trimmed metadata, with no confirmation/reload',async()=>{
    const h=fixture('a/b ?'),p=h.submit(),c=h.calls[0];assert.equal(c.url,'/api/campaigns/a%2Fb%20%3F');
    assert.equal(c.options.method,'PATCH');assert.equal(c.options.headers['Content-Type'],'application/json');
    assert.deepEqual(JSON.parse(c.options.body),{name:'Updated',description:'Description'});await ok(h,p);
    assert.equal(h.confirmations.length,0);assert.equal(h.loads.length,0);assert.equal(h.context.campaignModal.hidden,true);
    assert.equal(h.node('#campaignSelect').value,'a/b ?');assert.equal(h.records()[0].text,'Updated campaign: Updated');
    const t=[...h.timers.values()][0];assert.equal(t.delay,3000);t.fn();assert.equal(h.records().length,0);
});
test('request failure retains draft, modal and persistent campaign identity',async()=>{
    const h=fixture(),p=h.submit();h.calls[0].reject(new Error('Denied'));await p;
    assert.equal(h.records()[0].target,JSON.stringify(['campaign-edit','edit']));assert.equal(h.timers.size,0);
    assert.equal(h.context.campaignModal.hidden,false);assert.equal(h.form.elements.name.value,' Updated ');
    assert.equal(h.node('#campaignSubmit').disabled,false);assert.equal(h.loads.length,0);
});
test('successful retry resolves only matching campaign error, including a reopened edit',async()=>{
    const h=fixture();other(h);let p=h.submit();h.calls[0].reject(new Error('Denied'));await p;
    h.context.closeCampaignModal();h.context.openCampaignModal({id:'edit',name:'Updated'});p=h.submit();await ok(h,p);
    assert.deepEqual(h.records().filter(r=>r.severity==='error').map(r=>r.text),['Keep newer error']);
});
test('other campaign errors remain independent',async()=>{
    const h=fixture();let p=h.submit();h.calls[0].reject(new Error('First'));await p;
    h.context.openCampaignModal({id:'second',name:'Second'});p=h.submit();await ok(h,p);
    assert.equal(h.records().find(r=>r.severity==='error').text,'First');
});
test('newer input and edit-revert suppress obsolete success and rejection',async()=>{
    for(const reject of [true,false])for(const revert of [true,false]){
        const h=fixture(),p=h.submit();h.values('Newer');if(revert)h.values(' Updated ',' Description ');
        if(reject)h.calls[0].reject(new Error('Old'));else h.calls[0].resolve({active:'old',campaigns:[]});await p;
        assert.equal(h.records().length,0);assert.equal(h.context.campaignModal.hidden,false);
        assert.equal(h.form.elements.name.value,revert?' Updated ':'Newer');
    }
});
test('cancel, reopen, target, selection, registry and leave-return guard obsolete outcomes',async()=>{
    for(const action of ['cancel','reopen','same-target','target','selection','registry','scope'])for(const reject of [false,true]){
        const h=fixture(),registry=h.context.campaignData,p=h.submit();
        if(action==='cancel')h.node('#cancelCampaign').onclick();
        if(action==='reopen'){h.context.closeCampaignModal();h.context.openCampaignModal({id:'edit',name:'Keep'});}
        if(action==='same-target')h.context.openCampaignModal({id:'edit',name:'Keep'});
        if(action==='target')h.context.openCampaignModal({id:'other',name:'Keep'});
        if(action==='selection')h.node('#campaignSelect').value='other';
        if(action==='registry')h.context.campaignData={active:'newer',campaigns:[]};
        if(action==='scope'){h.observe('away','fight');h.observe('old','before');}
        const expected=h.context.campaignData;
        if(reject)h.calls[0].reject(new Error('Obsolete'));else h.calls[0].resolve({active:'wrong',campaigns:[]});await p;
        assert.equal(h.records().length,0);assert.equal(h.context.campaignData,expected);
        assert.equal(h.node('#campaignSubmit').disabled,false);
    }
});
test('busy edit blocks edit and reopened create, then restores prior disabled state',async()=>{
    for(const disabled of [false,true]){const h=fixture();h.node('#campaignSubmit').disabled=disabled;
        const p=h.submit();assert.equal(h.node('#campaignSubmit').disabled,true);await h.submit();
        h.open();await h.submit();assert.equal(h.calls.length,1);h.calls[0].reject(new Error('Old'));await p;
        assert.equal(h.node('#campaignSubmit').disabled,disabled);}
});
test('render failure reports saved metadata and never replays PATCH',async()=>{
    const h=fixture();h.context.renderCampaigns=()=>{assert.equal(h.node('#campaignSubmit').disabled,true);h.node('#campaignSelect').value='render-default';throw new Error('UI failed');};
    const p=h.submit();await ok(h,p);assert.equal(h.calls.length,1);assert.equal(h.records()[0].severity,'success');
    assert.equal(h.records()[1].operation,'campaign.edit.render');assert.match(h.records()[1].text,/Campaign saved.*do not save/);
    for(const t of [...h.timers.values()])t.fn();assert.equal(h.records().length,1);assert.equal(h.records()[0].severity,'error');
});
test('newer feedback supersedes old results and old timers cannot dismiss new errors',async()=>{
    const h=fixture(),p=h.submit();other(h,{operation:'campaign.edit.render',target:JSON.stringify(['campaign-edit','edit'])});
    await ok(h,p);assert.equal(h.records().length,1);assert.equal(h.records()[0].text,'Keep newer error');
    const k=fixture(),q=k.submit();await ok(k,q);const r=k.records()[0],t=[...k.timers.values()][0];
    other(k,{operation:r.operation,target:r.target});t.fn();assert.equal(k.records()[0].text,'Keep newer error');
});
