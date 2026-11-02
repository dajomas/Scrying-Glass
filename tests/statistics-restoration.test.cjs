const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const nodes=new Map();
class Element {
 constructor(){this.children=[];this.dataset={};this.value='';this.hidden=true;this.listeners={};}
 append(...children){this.children.push(...children);}
 replaceChildren(...children){this.children=children;}
 addEventListener(n,fn){this.listeners[n]=fn;}
 querySelectorAll(selector){const all=this.children.flatMap(c=>[c,...c.querySelectorAll(selector)]);return selector==='[data-base-stat]'?all.filter(x=>x.dataset.baseStat):all;}
 reportValidity(){return true;}
}
const el=id=>{if(!nodes.has(id))nodes.set(id,new Element());return nodes.get(id);};
let click,allow=true,hold=null;const requests=[];
const state={active_campaign_id:'1',active_setup:{name:'test'},statistics_token:'token',monsters:[],characters:[{id:'c',name:'Cleric',hp:8,max_hp:10,base_max_hp:15,base_strength:12,strength:9,effects:[{mechanical:{stat:'strength',amount:3}}]}]};
const ctx={window:{},document:{getElementById:el,createElement:()=>new Element(),addEventListener:(n,fn)=>click=fn},confirm:()=>allow,alert:()=>{},
 fetch:async(url,opts={})=>{if(hold)await hold;if(opts.body)requests.push({url,body:JSON.parse(opts.body)});return {ok:true,json:async()=>opts.body?{}:JSON.parse(JSON.stringify(state))};}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../static/statistics.js'),'utf8'),ctx);
const flush=()=>new Promise(r=>setImmediate(r));
const open=()=>click({target:{closest:()=>({dataset:{statistics:'c'}})}});
(async()=>{
 open();await flush();assert.equal(el('statisticsModal').hidden,false);assert.match(el('statisticsTitle').textContent,/Cleric/);
 const inputs=el('statisticsFields').querySelectorAll('[data-base-stat]');assert.equal(inputs.length,7);
 el('statisticsRestoreStat').value='strength';allow=false;el('statisticsRestore').onclick();await flush();assert.equal(requests.length,0,'Cancel must not mutate');
 allow=true;el('statisticsRestore').onclick();await flush();assert.equal(requests.length,1);assert.equal(requests[0].body.stat,'strength');assert.equal(requests[0].body.token,'token');
 let input=el('statisticsFields').querySelectorAll('[data-base-stat]').find(x=>x.dataset.baseStat==='charisma');input.value='14';
 el('statisticsBasesForm').onsubmit({preventDefault(){}});await flush();assert.equal(requests[1].body.bases.charisma,14);
 ctx.window.scryingStatisticsState({...state,active_campaign_id:'2'});assert.equal(el('statisticsModal').hidden,true);el('statisticsRestore').onclick();await flush();assert.equal(requests.length,2,'Scope change invalidates target');
 console.log('PASS: restore next to reset workflow, seven base inputs, cancellation, selected restore, base editing and campaign isolation');
})().catch(e=>{console.error(e);process.exitCode=1;});
