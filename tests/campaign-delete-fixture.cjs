const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const {createController}=require('../static/admin-feedback-controller.js');
const source=fs.readFileSync(path.join(__dirname,'../static/admin/050-source.js'),'utf8');
const deletion=source.slice(0,source.indexOf("document.querySelector('#openCampaignSetup')"));
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};};
const flush=async()=>{for(let i=0;i<8;i++)await Promise.resolve();};
function fixture(setups=['one']){
 const nodes=new Map(),calls=[],legacy=[],confirms=[],timers=new Map(),follow=[];let serial=0,epoch=1;
 let scope=JSON.stringify(['a','a','before']);
 function node(id){if(!nodes.has(id))nodes.set(id,{value:'',hidden:false,disabled:false,listeners:{},
  addEventListener(type,fn){(this.listeners[type]||=[]).push(fn);},
  set innerHTML(html){this.html=html;const opts=[...html.matchAll(/<option value="([^"]*)"([^>]*)>/g)];
   this.value=(opts.find(o=>o[2].includes('selected'))||opts[0]||[])[1]||'';},get innerHTML(){return this.html||'';}});return nodes.get(id);}
 const modal=node('#campaignDeleteModal');modal.hidden=true;node('#cancelCampaignDelete').onclick=()=>{modal.hidden=true;};
 const controller=createController({setTimeout(fn,ms){const id=++serial;timers.set(id,{fn,ms});return id;},clearTimeout(id){timers.delete(id);}});
 controller.setScope('page','page');controller.setScope('encounter',scope);
 const api={...controller,encounterContext:()=>({scope,epoch}),begin(spec){return controller.begin({...spec,scope:spec.lane==='page'?'page':scope,placement:'pane'});}};
 const context=vm.createContext({document:{querySelector:node},window:{scryingAdminFeedback:api},campaignDeleteModal:modal,
  campaignData:{active:'a',campaigns:[{id:'a',name:'Active',setups:['active']},{id:'b',name:'Victim',setups:[...setups]},{id:'c',name:'Destination',setups:[]}]},
  campaignById(id){return context.campaignData.campaigns.find(c=>c.id===id);},esc:s=>String(s),
  REPLACE_WARNING:"The current battle will be replaced by the campaign's most recently used battle setup. Unsaved changes will be lost.",
  confirm(text){confirms.push(text);return context.confirmed;},confirmed:true,
  request(url,options){const d=deferred();calls.push({url,options,...d});return d.promise;},
  async applyOpenedSetup(result){follow.push(result);return result.opened_setup?'; opened battle setup '+result.opened_setup:'';},
  paneNotification(region,text){legacy.push({region,text});}});
 vm.runInContext(deletion,context);
 const h={context,node,api,controller,calls,legacy,confirms,timers,follow,modal,
  records:()=>controller.snapshot(),open:()=>node('#deleteCampaign').onclick(),
  submit:()=>node('#campaignDeleteForm').onsubmit({preventDefault(){}}),
  change(id,value){const n=node(id);n.value=value;return n.onchange?.();},
  observe(campaign='a',setup='before'){const next=JSON.stringify([campaign,setup?campaign:null,setup]);if(next!==scope){scope=next;epoch++;controller.setScope('encounter',scope);}},
  result:{active:'a',opened_setup:'before',campaigns:[{id:'a',name:'Active',setups:['active']},{id:'c',name:'Destination',setups:[]}],moved:['one']}};
 h.open();return h;
}
function seed(h,operation='other',target='other'){h.api.publish(h.api.begin({lane:'page',region:'campaign',operation,target,label:'Keep newer'}),{severity:'error',text:'Keep newer error'});}
module.exports={fixture,seed,deferred,flush};
