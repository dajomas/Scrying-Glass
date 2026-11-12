// Real 040 switch helpers + 080 owner and real controller; mocked DOM, transport and context.
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const {harness,flush}=require('./campaign-feedback-fixture.cjs');
const legacy=fs.readFileSync(path.join(__dirname,'../static/admin/040-source.js'),'utf8');
const source=fs.readFileSync(path.join(__dirname,'../static/admin/080-source.js'),'utf8');
const setup=legacy.slice(legacy.indexOf('async function applyOpenedSetup('),legacy.indexOf('const REPLACE_WARNING'));
const start=legacy.indexOf('async function switchCampaign()');
const oldSwitch=legacy.slice(start,legacy.indexOf('// The delete dialog',start));
function fixture(){
 const h=harness();h.legacy=[];h.context.campaignData={active:'old',campaigns:[{id:'old',name:'Old'},{id:'new',name:'New'}]};
 h.context.activeCampaign=()=>h.context.campaignData.campaigns.find(c=>c.id===h.context.campaignData.active);
 h.context.paneNotification=(region,text)=>h.legacy.push({region,text});
 vm.runInContext(setup+oldSwitch,h.context);vm.runInContext(source.slice(source.indexOf('// Stage 1 Step 1C.1')),h.context);
 h.select=h.node('#campaignSelect');h.button=h.node('#switchCampaign');
 h.change=id=>{h.select.value=id;return h.select.onchange();};h.click=()=>h.button.onclick();
 h.answer=(id='new',opened='default')=>({active:id,opened_setup:opened,campaigns:[{id:'old',name:'Old'},{id,name:'New'}]});
 return h;
}
async function applied(h,p,opened='default'){
 h.calls.at(-1).resolve(h.answer('new',opened));await flush();h.observe('new',opened);h.loads.at(-1).resolve();await p;
}
module.exports={fixture,applied,flush};
