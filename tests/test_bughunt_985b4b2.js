/* Executes the actual production renderer and helpers with a minimal DOM.
 * Fault injection throws from a card's innerHTML setter after card insertion.
 * Timers and requestAnimationFrame are deterministic fixtures, not a browser.
 */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const source=fs.readFileSync(path.join(__dirname,'..','static','client.js'),'utf8');
const code=source.slice(0,source.indexOf('function connectDisplay()'));
function fixture() {
 const h={fault:null,timers:new Map()};let timerId=0;
 class Element {
  constructor(tag='div') {
   this.tag=tag;this.id='';this.className='';this.children=[];this.parent=null;this._html='';
   this.style={setProperty(name,value){this[name]=value;}};
   this.classList={contains:name=>this.className.split(/\s+/).includes(name),
    add:(...names)=>{this.className=[...new Set([...this.className.split(/\s+/).filter(Boolean),...names])].join(' ');},
    remove:(...names)=>{this.className=this.className.split(/\s+/).filter(name=>!names.includes(name)).join(' ');},
    toggle:(name,on)=>{if(on)this.classList.add(name);else this.classList.remove(name);}};
  }
  get innerHTML(){return this._html;}
  set innerHTML(value){
   if(this.id===h.fault){h.fault=null;throw Error('Injected card DOM failure');}
   this._html=value;for(const child of this.children)child.parent=null;this.children=[];
   if(value==='<div class="empty"></div>'){const empty=new Element();empty.className='empty';this.appendChild(empty);}
  }
  appendChild(child){child.parent=this;this.children.push(child);return child;}
  prepend(child){child.parent=this;this.children.unshift(child);}
  setAttribute(name,value){this[name]=value;}
  remove(){if(this.parent)this.parent.children=this.parent.children.filter(child=>child!==this);this.parent=null;}
  querySelectorAll(selector){const output=[];const visit=node=>{for(const child of node.children){if(selector.startsWith('.')&&child.classList.contains(selector.slice(1)))output.push(child);visit(child);}};visit(this);return output;}
  querySelector(selector){return this.querySelectorAll(selector)[0]||null;}
 }
 const stage=new Element(),initiative=new Element(),campaign=new Element();stage.id='stage';initiative.id='initiative';campaign.id='clientCampaign';
 const roots=[stage,initiative,campaign];
 const get=id=>{const walk=node=>node.id===id?node:node.children.map(walk).find(Boolean);return roots.map(walk).find(Boolean)||null;};
 const sandbox={document:{body:{style:{}},querySelector:selector=>get(selector.slice(1)),getElementById:get,createElement:tag=>new Element(tag)},
  applyBattleOrderFontSize(){},requestAnimationFrame:fn=>fn(),
  setTimeout:(fn,delay)=>{const id=++timerId;h.timers.set(id,{fn,delay});return id;},clearTimeout:id=>h.timers.delete(id)};
 vm.createContext(sandbox);vm.runInContext(code,sandbox);
 h.render=state=>sandbox.render(state);h.get=get;h.stage=stage;
 h.cards=()=>stage.querySelectorAll('.monster').map(card=>card.id).sort();
 h.finishExits=()=>{for(const [id,timer]of [...h.timers]){h.timers.delete(id);timer.fn();}};
 return h;
}
function snapshot(ids) {
 return {characters:[],lairs:[],battle_order:ids,battle_round:0,display:{entry_direction:'from_bottom',exit_direction:'to_bottom'},
  monsters:ids.map(id=>({id,name:id,monster_species:'Goblin',active:true,alive:true,visible:true,in_turn:false,hp:10,max_hp:10,color:'#842029',effects:[]}))};
}
function failNewCard(h,ids,id='b'){h.fault='m-'+id;assert.throws(()=>h.render(snapshot(ids)),/Injected card DOM failure/);assert(h.get('m-'+id));}
const cases=[
 ['card created during failed update is retired after old snapshot recovery',()=>{
  const h=fixture();h.render(snapshot(['a']));failNewCard(h,['a','b']);h.render(snapshot(['a']));h.finishExits();assert.deepEqual(h.cards(),['m-a']);
 }],
 ['failed initial render cards are retired on replacement snapshot',()=>{
  const h=fixture();failNewCard(h,['a','b']);h.render(snapshot(['c']));h.finishExits();assert.deepEqual(h.cards(),['m-c']);
 }],
 ['different recovery snapshot removes both tracked and untracked stale cards',()=>{
  const h=fixture();h.render(snapshot(['a']));failNewCard(h,['a','b']);h.render(snapshot(['c']));h.finishExits();assert.deepEqual(h.cards(),['m-c']);
 }],
 ['orphan exit uses one existing animation timer',()=>{
  const h=fixture();h.render(snapshot(['a']));failNewCard(h,['a','b']);h.render(snapshot(['a']));h.render(snapshot(['a']));
  assert.equal(h.timers.size,1);assert.equal([...h.timers.values()][0].delay,750);assert(h.get('m-b').classList.contains('exit-bottom'));
 }],
 ['normal removal retains exit animation and removes card',()=>{
  const h=fixture();h.render(snapshot(['a','b']));h.render(snapshot(['a']));assert.equal(h.timers.size,1);h.finishExits();assert.deepEqual(h.cards(),['m-a']);
 }],
 ['reappearing card cancels its pending removal and retains element identity',()=>{
  const h=fixture();h.render(snapshot(['a','b']));const b=h.get('m-b');h.render(snapshot(['a']));h.render(snapshot(['a','b']));
  assert.equal(h.timers.size,0);assert.equal(h.get('m-b'),b);assert(!b.classList.contains('exit-bottom'));
 }],
 ['partial card included by recovery snapshot is repaired rather than removed',()=>{
  const h=fixture();h.render(snapshot(['a']));failNewCard(h,['a','b']);const b=h.get('m-b');h.render(snapshot(['a','b']));
  assert.equal(h.get('m-b'),b);assert.equal(h.timers.size,0);assert(b.innerHTML.includes('<h1>b'));
 }],
 ['empty snapshot removes partial cards and pending timers',()=>{
  const h=fixture();h.render(snapshot(['a']));failNewCard(h,['a','b']);h.render(snapshot([]));assert.deepEqual(h.cards(),[]);assert.equal(h.timers.size,0);
 }]
];
let failures=0;for(const [name,test]of cases){try{test();console.log('PASS '+name);}catch(error){failures++;console.error('FAIL '+name+'\n'+error.stack);}}
console.log(`${cases.length} tests; ${cases.length-failures} passed; ${failures} failed`);process.exitCode=failures?1:0;
