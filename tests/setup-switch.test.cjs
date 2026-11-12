const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../static/setup-switch.js'),'utf8');
// SG-TODO-009.7 Step 2C: failures now publish through the production feedback controller.
const {createController}=require(path.join(__dirname,'../static/admin-feedback-controller.js'));
const controller=createController({setTimeout(){return 0;},clearTimeout(){}});
controller.setScope('page','page');
let scope=JSON.stringify(['campaign','campaign','old']),epoch=1;
const observe=name=>{const next=JSON.stringify(['campaign','campaign',name]);if(next!==scope){scope=next;epoch++;}};
const feedback={...controller,encounterContext:()=>({scope,epoch}),begin:spec=>controller.begin({...spec,scope:'page',placement:'pane'})};
const errors=()=>controller.snapshot().filter(r=>r.severity==='error').map(r=>r.text);
const select={value:'new',disabled:false},button={disabled:false},name={value:'old'};
let install,calls=[],messages=[],loads=0,refreshes=0,failRequest=false,failRefresh=false;
const confirm=()=>{throw new Error('Confirmation must not be called');};
const context={confirm,window:{scryingAdminFeedback:feedback},renderCampaigns(){},latest:{active_setup:{name:'old',campaign_id:'campaign'}},campaignData:{active:'campaign'},
    document:{readyState:'interactive',getElementById(id){return {setupSelect:select,loadSetup:button,setupName:name}[id];},addEventListener(event,cb){install=cb;}},
    paneNotification(kind,message){messages.push(message);},
    async request(url,options){if(url==='/api/campaigns'){refreshes++;return {active:'campaign',moved:[]};}calls.push({url,options});if(failRequest)throw new Error('Denied');return {name:'new',campaign:'campaign'};},
    async load(){loads++;if(failRefresh)throw new Error('Refresh failed');observe('new');context.latest={active_setup:{name:'new',campaign_id:'campaign'}};},
    async setups(){throw new Error('Error-swallowing setups() must not be used');}};
vm.runInNewContext(source,context);
select.onchange=button.onclick=()=>{throw new Error('Old confirming handler must be replaced');};
install();
(async()=>{
    await select.onchange({preventDefault(){}});
    assert.equal(calls.length,1);assert.equal(calls[0].url,'/api/setups/load');
    assert.deepEqual(JSON.parse(calls[0].options.body),{name:'new',campaign:'campaign'});
    assert.equal(loads,1);assert.equal(refreshes,1);assert.equal(name.value,'new');assert.equal(select.disabled,false);
    await button.onclick();assert.equal(calls.length,1);
    context.latest={active_setup:{name:'old',campaign_id:'campaign'}};observe('old');select.value='new';
    await button.onclick();assert.equal(calls.length,2);
    context.latest={active_setup:{name:'old',campaign_id:'campaign'}};observe('old');select.value='new';failRequest=true;
    await select.onchange();assert.equal(select.value,'old');assert.deepEqual(errors(),['Denied']);assert.equal(button.disabled,false);
    failRequest=false;select.value='';await select.onchange();assert.equal(calls.length,3);
    assert(errors().includes('Choose a saved battle setup to load'));
    select.value='new';context.campaignData.active=null;await button.onclick();assert.equal(calls.length,3);
    assert(errors().includes('Choose an active campaign first'));
    context.campaignData.active='campaign';failRefresh=true;await select.onchange();
    assert.equal(select.value,'new');
    assert(errors().some(t=>t.includes('was loaded, but refreshing the view failed: Refresh failed')));
    assert.deepEqual(messages,[],'no legacy paneNotification calls for load feedback');
    assert.equal(context.confirm,confirm);
    console.log('Dropdown/button direct switching, payload, no-op, error/revert, empty selection and untouched global confirmation checks passed.');
})().catch(error=>{console.error(error);process.exitCode=1;});
