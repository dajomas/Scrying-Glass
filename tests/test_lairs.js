/* DOM-mock integration checks; no real browser is required. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
class Element {
    constructor(tag='div'){this.tag=tag;this.children=[];this.dataset={};this.value='';this.checked=false;this.disabled=false;this.hidden=false;this.textContent='';this.listeners={};}
    append(...children){this.children.push(...children);}
    replaceChildren(...children){this.children=children;}
    setAttribute(name,value){this[name]=value;}
    addEventListener(name,fn){this.listeners[name]=fn;}
    get rows(){return this.children;}
    querySelectorAll(selector){
        const key=selector.slice(6,-1).replace(/-([a-z])/g,(_,c)=>c.toUpperCase());
        const output=[];
        const visit=node=>{if(node.dataset&&key in node.dataset)output.push(node);(node.children||[]).forEach(visit);};
        this.children.forEach(visit);return output;
    }
    querySelector(selector){return this.querySelectorAll(selector)[0]||null;}
}
const html=fs.readFileSync(path.join(root,'templates/admin/185_lair_tools.html'),'utf8');
const nodes=new Map([...html.matchAll(/id="([^"]+)"/g)].map(m=>[m[1],new Element()]));
const $=id=>{assert(nodes.has(id),`Missing HTML element ${id}`);return nodes.get(id);};
$('lairDefaultDamage').value='0';$('lairDefaultConditions').value='';$('lairActionName').value='Tremor';$('lairConditionTiming').value='manual';
const snapshot={lairs:[{id:'l',kind:'lair',name:'Lair',active:true,visible:true,in_turn:true,notes:'Private',color:'#8064a2'}],
 characters:[{id:'c',name:'<Hero>',hp:20,max_hp:20,active:true,life_state:'standing'}],
 monsters:[{id:'m',name:'Ally',hp:12,max_hp:12,active:true,life_state:'standing',monster_species:'Goblin',ally:true},
 {id:'dead',name:'Dead',hp:0,max_hp:10,active:true,life_state:'dead',monster_species:'Goblin'}]};
let revision=10,calls=[],loads=0,confirmations=0;
const context={document:{getElementById:$,createElement:tag=>new Element(tag)},window:{},
 confirm:()=>{confirmations++;return true;},load:async()=>{loads++;},
 fetch:async(url,options)=>{
  const body=options.body?JSON.parse(options.body):null;calls.push({url,method:options.method,body});
  const data=url==='/api/state'?structuredClone(snapshot):url==='/api/features'?{revision}:url.endsWith('/actions')?{applied:body.targets.length}:{};
  return {ok:true,json:async()=>data};
 },console};
vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(root,'static/lairs.js'),'utf8'),context);
const settle=async()=>{for(let i=0;i<12;i++)await new Promise(resolve=>setImmediate(resolve));};
(async()=>{
 context.window.scryingLairsRender(snapshot);
 assert.equal($('saveLair').textContent,'Save lair');assert.equal($('resolveLair').disabled,false);
 $('lairName').value='Unsaved';$('lairName').listeners.input();context.window.scryingLairsRender(snapshot);
 assert.equal($('lairName').value,'Unsaved','Polling must preserve unsaved edits');
 await context.window.scryingOpenLairAction('l');
 assert.equal($('lairActionModal').hidden,false);assert.equal($('lairTargets').rows.length,2,'Lair and dead creature excluded');
 const rows=$('lairTargets').rows;
 assert(rows.some(r=>r.children[1].textContent.includes('<Hero>')),'Names use textContent rather than injected HTML');
 $('lairSelectAll').onclick();assert(rows.every(r=>r.querySelector('[data-lair-select]').checked));
 $('lairDefaultDamage').value='8';$('lairDefaultConditions').value='Prone';$('lairFillSelected').onclick();
 assert(rows.every(r=>r.querySelector('[data-lair-damage]').value==='8'));
 rows.find(r=>r.dataset.target==='m').querySelector('[data-lair-damage]').value='4';
 $('lairConditionsPublic').checked=true;$('lairConditionTiming').value='lair-start';
 $('lairActionForm').onsubmit({preventDefault(){}});await settle();
 const action=calls.find(c=>c.url==='/api/lairs/l/actions');assert(action);
 assert.equal(action.body.revision,10);assert.equal(action.body.targets.length,2);
 assert.equal(action.body.targets.find(x=>x.id==='m').damage,4);
 assert.equal(action.body.targets[0].effects[0].anchor_id,'l');
 assert.equal(action.body.targets[0].effects[0].timing,'start');assert.equal(action.body.targets[0].effects[0].public,true);
 assert.equal($('lairActionModal').hidden,true);assert.equal(loads,1);assert.equal(confirmations,1);
 await context.window.scryingOpenLairAction('l');$('lairSelectNone').onclick();
 $('lairActionForm').onsubmit({preventDefault(){}});await settle();
 assert.equal(calls.filter(c=>c.url.endsWith('/actions')).length,1,'Empty selection sends no write');
 assert.equal($('lairActionNotice').textContent,'Select at least one target.');
 snapshot.lairs[0].in_turn=false;context.window.scryingLairsRender(snapshot);assert.equal($('resolveLair').disabled,true);
 await context.window.scryingOpenLairAction('l');assert.match($('lairNotice').textContent,/not currently/);
 console.log('Lair DOM-mock integration checks passed');
})().catch(error=>{console.error(error);process.exitCode=1;});
