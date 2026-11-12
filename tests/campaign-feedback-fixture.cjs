// Complete 080 with production controller; DOM, transport, context and legacy owners are mocked.
const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const {createController} = require(path.join(root, 'static/admin-feedback-controller.js'));
const source = fs.readFileSync(path.join(root, 'static/admin/080-source.js'), 'utf8');
const deferred = () => {let resolve, reject; const promise = new Promise((a,b) => {resolve=a;reject=b;}); return {promise,resolve,reject};};
const flush = async () => {for(let i=0;i<6;i++) await Promise.resolve();};
function harness() {
    const nodes = new Map(), calls = [], loads = [], timers = new Map(), edits = [], confirmations = [];
    let epoch=1, scope=JSON.stringify(['old','old','before']), boot=true, timer=0;
    const node = id => {if(!nodes.has(id)) nodes.set(id,{value:'',hidden:true,disabled:false,listeners:{},
        addEventListener(t,fn){(this.listeners[t] ||= []).push(fn);}});return nodes.get(id);};
    const form=node('#campaignForm');form.elements={name:node('name'),description:node('description')};
    form.valid=true;form.reportValidity=()=>form.valid;
    const controller=createController({setTimeout(fn,delay){const id=++timer;timers.set(id,{fn,delay});return id;},clearTimeout(id){timers.delete(id);}});
    controller.setScope('page','page');controller.setScope('encounter',scope);
    const api={...controller,encounterContext:()=>Object.freeze({scope,epoch}),begin(spec){const lane=spec.lane||'encounter';
        return controller.begin({...spec,lane,scope:lane==='page'?'page':scope,placement:'pane'});}};
    const context=vm.createContext({window:{scryingAdminFeedback:api},document:{querySelector:node},
        campaignEditing:null,campaignModal:node('#campaignModal'),campaignData:{active:'old',campaigns:[{id:'edit',name:'Edit',description:''}]},
        campaignById(id){return context.campaignData.campaigns?.find(c=>c.id===id);},
        REPLACE_WARNING:"The current battle will be replaced by the campaign's most recently used battle setup. Unsaved changes will be lost.",
        openCampaignModal(campaign=null){context.campaignEditing=campaign?.id||null;form.elements.name.value=campaign?.name||'';
            form.elements.description.value='';context.campaignModal.hidden=false;},
        closeCampaignModal(){context.campaignModal.hidden=true;context.campaignEditing=null;},
        request(url,options){const p=deferred();calls.push({url,options,...p});return p.promise;},
        load(flag){if(boot)return;const p=deferred();loads.push({flag,...p});return p.promise;},
        renderCampaigns(){},renderActiveBattleSetup(){},syncActiveBattleSetupControls(){},setups(){},installColorPreview(){},
        confirm(text){confirmations.push(text);return context.confirmed;},confirmed:true});
    form.onsubmit=function(event){edits.push({owner:this,event});};
    node('#cancelCampaign').onclick=context.closeCampaignModal;
    vm.runInContext(source,context);boot=false;
    const open=edit=>context.openCampaignModal(edit?{id:'edit',name:'Edit'}:null);
    const values=(name=' New ',description=' Desc ')=>{form.elements.name.value=name;form.elements.description.value=description;
        for(const fn of form.listeners.input)fn();};
    const submit=()=>form.onsubmit({target:form,currentTarget:form,preventDefault(){}});
    const observe=(campaign='new',setup='default')=>{const next=JSON.stringify([campaign,setup?campaign:null,setup]);
        if(next!==scope){scope=next;epoch++;controller.setScope('encounter',scope);}};
    open();values();
    return {context,api,node,form,calls,loads,timers,edits,confirmations,open,values,submit,observe,
        records:()=>controller.snapshot(),result:{active:'new',opened_setup:'default',campaigns:[]}};
}
async function applied(h){h.calls.at(-1).resolve(h.result);await flush();}
async function finish(h,p){h.observe();h.loads.at(-1).resolve();await p;}
function other(h,spec={}){h.api.publish(h.api.begin({lane:'page',region:'campaign',operation:'other',target:'other',label:'Other',...spec}),{severity:'error',text:'Keep newer error'});}

module.exports = {harness, deferred, flush, applied, finish, other};
