const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
class Element {
 constructor(tag='div'){this.tagName=tag;this.children=[];this.dataset={};this.value='';this.hidden=false;this.disabled=false;this.listeners={};this.attributes={};}
 append(...children){this.children.push(...children);}
 replaceChildren(...children){this.children=children;}
 addEventListener(n,fn){this.listeners[n]=fn;}
 setAttribute(k,v){this.attributes[k]=v;}
 focus(){this.focused=true;}
 querySelectorAll(selector){
  const all=this.children.flatMap(c=>[c,...c.querySelectorAll('*')]);
  if(selector==='[data-base-stat]')return all.filter(x=>x.dataset.baseStat);
  if(selector==='[data-stat]')return all.filter(x=>x.dataset.stat);
  if(selector==='input,select,button')return all.filter(x=>['input','select','button'].includes(x.tagName));
  return all;
 }
 querySelector(selector){return selector==='[role="dialog"]'?this.children.find(x=>x.attributes.role==='dialog'):null;}
 reportValidity(){return true;}
}
function harness(effects=[{mechanical:{version:1,stat:'max_hp',amount:9}}]) {
 const nodes=new Map(),listeners={},requests=[];
 const el=id=>{if(!nodes.has(id))nodes.set(id,new Element());return nodes.get(id);};
 const modal=el('statisticsModal'),dialog=new Element();dialog.setAttribute('role','dialog');modal.append(dialog);
 for(const id of ['statisticsRestore','statisticsClose','statisticsEditBases','statisticsBack','statisticsSaveBases']){const x=el(id);x.tagName='button';dialog.append(x);}
 el('statisticsRestoreStat').tagName='select';dialog.append(el('statisticsRestoreStat'));
 const state={active_campaign_id:'1',active_setup:{name:'test'},statistics_token:'token',monsters:[],characters:[{id:'c',name:'Johan',hp:0,max_hp:0,base_max_hp:1,effects}]};
 let allow=true,fail=false,hold=null;
 const context={window:{},document:{getElementById:el,createElement:tag=>new Element(tag),addEventListener:(n,f)=>listeners[n]=f},confirm:()=>allow,alert:()=>{},
 fetch:async(url,opts={})=>{
  if(hold)await hold;
  const body=opts.body&&JSON.parse(opts.body);if(body)requests.push({url,body});
  if(body&&!fail&&body.operation==='restore')state.characters[0].effects=state.characters[0].effects.filter(e=>body.stat!=='all'&&e.mechanical.stat!==body.stat);
  return {ok:!fail,json:async()=>fail?{detail:'Encounter changed; reopen Restore statistics'}:body?{}:JSON.parse(JSON.stringify(state))};
 }};
 vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../static/statistics.js'),'utf8'),context);
 const button=new Element();button.dataset.statistics='c';
 return {el,state,requests,context,listeners,button,open:()=>listeners.click({target:{closest:()=>button}}),setAllow:x=>allow=x,setFail:x=>fail=x,setHold:x=>hold=x};
}
const flush=()=>new Promise(r=>setImmediate(r));
const shown=h=>h.el('statisticsFields').querySelectorAll('[data-stat]').map(x=>x.dataset.stat);
(async()=>{
 let h=harness();h.open();await flush();
 assert.deepEqual(shown(h),['max_hp'],'Only affected Max HP appears, even with zero effective value');
 assert.equal(h.el('statisticsFields').querySelectorAll('[data-base-stat]').length,0,'Restore is not the original-score editor');
 assert.equal(h.el('statisticsRestoreStat').children.length,1);assert.equal(h.el('statisticsRestoreStat').value,'max_hp');
 h.setAllow(false);h.el('statisticsRestore').onclick();await flush();assert.equal(h.requests.length,0);
 h.setAllow(true);h.el('statisticsRestore').onclick();await flush();assert.equal(h.requests[0].body.stat,'max_hp');assert.equal(h.requests[0].body.token,'token');
 assert.deepEqual(shown(h),[]);assert.equal(h.el('statisticsRestore').disabled,true);assert.equal(h.el('statisticsRestoreStat').disabled,true);
 assert.match(h.el('statisticsFields').children[0].textContent,/No statistic reductions/);
 h.el('statisticsRestore').onclick();await flush();assert.equal(h.requests.length,1);
 h=harness([{mechanical:{version:1,stat:'strength',amount:3}},{mechanical:{version:1,stat:'dexterity',amount:2}}]);h.open();await flush();
 assert.deepEqual(shown(h),['strength','dexterity']);assert.equal(h.el('statisticsRestoreStat').children.length,3);assert.equal(h.el('statisticsRestoreStat').value,'all');
 h.el('statisticsRestoreStat').value='strength';h.el('statisticsRestore').onclick();await flush();assert.deepEqual(shown(h),['dexterity']);assert.equal(h.el('statisticsRestoreStat').value,'dexterity');
 h.el('statisticsEditBases').onclick();assert.equal(h.el('statisticsFields').querySelectorAll('[data-base-stat]').length,7);assert.equal(h.el('statisticsRestoreControls').hidden,true);assert.match(h.el('statisticsTitle').textContent,/Original\/base/);
 const charisma=h.el('statisticsFields').querySelectorAll('[data-base-stat]').find(x=>x.dataset.baseStat==='charisma');charisma.value='14';h.el('statisticsBasesForm').onsubmit({preventDefault(){}});await flush();assert.equal(h.requests[1].body.bases.charisma,14);
 h.el('statisticsBack').onclick();assert.deepEqual(shown(h),['dexterity']);
 h.context.window.scryingStatisticsState({...h.state,active_campaign_id:'other'});assert.equal(h.el('statisticsModal').hidden,true);h.el('statisticsRestore').onclick();await flush();assert.equal(h.requests.length,2);
 h=harness();h.open();await flush();h.setFail(true);h.el('statisticsRestore').onclick();await flush();assert.match(h.el('statisticsNotice').textContent,/Encounter changed/);assert.equal(h.el('statisticsRestore').disabled,false);
 h=harness([]);h.open();await flush();assert.equal(h.el('statisticsRestore').disabled,true);h.el('statisticsEditBases').onclick();assert.equal(shown(h).length,7,'Missing bases can still be set explicitly');
 h.el('statisticsClose').onclick();assert.equal(h.button.focused,true);
 console.log('PASS: affected-only rows/choices, Max HP zero, selected/all restore, empty disabling, independent base editor, cancel, stale errors, scope and focus');
})().catch(e=>{console.error(e);process.exitCode=1;});
