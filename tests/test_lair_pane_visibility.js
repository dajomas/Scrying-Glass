/* Run with node tests/test_lair_pane_visibility.js. Executes the actual admin controller. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const source=fs.readFileSync(path.join(root,'static/admin.js'),'utf8');
const start=source.indexOf('const hideablePanes =');
const functionStart=source.indexOf('function updatePaneVisibilityForBattle()',start);
const end=source.indexOf('\n}',functionStart)+2;
assert(start>=0&&functionStart>=0&&end>functionStart);
function setup(){
 const nodes=new Map();
 const get=selector=>{
  if(!nodes.has(selector))nodes.set(selector,{hidden:false,textContent:'',attributes:{},setAttribute(k,v){this.attributes[k]=v;}});
  return nodes.get(selector);
 };
 const context={document:{querySelector:get},latest:{battle_order:[]}};vm.createContext(context);
 vm.runInContext(source.slice(start,end)+`
 globalThis.api={controls:paneControlByKey,parent:setParentPaneHidden,hide:setPaneHidden,
  all:setAllHideablePanesHidden,update:updatePaneVisibilityForBattle};`,context);
 context.api.all(false);
 return {context,api:context.api,get,control:key=>context.api.controls.get(key),
  battle(active){context.latest={battle_order:active?['actor']:[]};context.api.update();}};
}
let count=0;
function test(name,fn){fn();count++;console.log('PASS: '+name);}
test('lair toggles independently with synchronized label and aria',()=>{
 const w=setup(),l=w.control('lairInput');l.button.onclick();
 assert(l.pane.hidden);assert.equal(l.button.textContent,'Show lair input');assert.equal(l.button.attributes['aria-expanded'],'false');
 assert(!w.control('monsterInput').pane.hidden);l.button.onclick();assert(!l.pane.hidden);assert.equal(l.button.textContent,'Hide lair input');
});
test('hiding setup hides both children and their toggle buttons',()=>{
 const w=setup();w.control('battleSetup').button.onclick();
 for(const k of ['lairInput','monsterInput']){const c=w.control(k);assert(c.pane.hidden);assert(c.button.hidden);assert.equal(c.button.attributes['aria-expanded'],'false');}
});
for(const lairHidden of [false,true])for(const monsterHidden of [false,true]){
 test(`setup reopening restores independent preferences: lair=${lairHidden}, monster=${monsterHidden}`,()=>{
  const w=setup();w.api.hide(w.control('lairInput'),lairHidden);w.api.hide(w.control('monsterInput'),monsterHidden);
  w.api.parent('battleSetup',true);w.api.parent('battleSetup',true);w.api.parent('battleSetup',false);
  assert.equal(w.control('lairInput').pane.hidden,lairHidden);assert.equal(w.control('monsterInput').pane.hidden,monsterHidden);
  for(const k of ['lairInput','monsterInput'])assert(!w.control(k).button.hidden);
 });
}
test('parent restores previously hidden child buttons exactly',()=>{
 const w=setup();w.control('lairInput').button.hidden=true;w.api.parent('battleSetup',true);w.api.parent('battleSetup',false);
 assert(w.control('lairInput').button.hidden);assert(!w.control('monsterInput').button.hidden);
});
test('battle start collapses lair and monster equally, retaining toggle access',()=>{
 const w=setup();w.battle(true);
 for(const k of ['lairInput','monsterInput']){assert(w.control(k).pane.hidden);assert(!w.control(k).button.hidden);}
});
test('manual reopening during battle survives repeated updates',()=>{
 const w=setup();w.battle(true);w.control('lairInput').button.onclick();w.battle(true);w.battle(true);
 assert(!w.control('lairInput').pane.hidden);assert(w.control('monsterInput').pane.hidden);
});
test('battle end restores normal layout and clears parent snapshots',()=>{
 const w=setup();w.api.hide(w.control('lairInput'),true);w.api.parent('battleSetup',true);w.battle(true);w.battle(false);
 for(const k of ['battleSetup','lairInput','monsterInput']){assert(!w.control(k).pane.hidden);assert(!w.control(k).button.hidden);}
 w.api.parent('battleSetup',true);w.api.parent('battleSetup',false);assert(!w.control('lairInput').pane.hidden);
});
test('second battle repeats automatic collapse',()=>{
 const w=setup();w.battle(true);w.battle(false);w.battle(true);assert(w.control('lairInput').pane.hidden);
});
test('manual setup hide/show during battle preserves child choices',()=>{
 const w=setup();w.battle(true);w.control('lairInput').button.onclick();w.api.parent('battleSetup',false);
 w.api.parent('battleSetup',true);w.battle(true);assert(w.control('lairInput').button.hidden);
 w.api.parent('battleSetup',false);assert(!w.control('lairInput').pane.hidden);assert(w.control('monsterInput').pane.hidden);
});
test('campaign-character dependency remains unchanged',()=>{
 const w=setup();w.api.hide(w.control('characterInput'),true);w.api.parent('campaign',true);
 assert(w.control('characterInput').button.hidden);w.api.parent('campaign',false);
 assert(w.control('characterInput').pane.hidden);assert(!w.control('characterInput').button.hidden);assert(!w.control('lairInput').pane.hidden);
});
test('initial active encounter collapses; idle refresh preserves choices',()=>{
 const w=setup();w.battle(true);assert(w.control('lairInput').pane.hidden);w.battle(false);
 w.control('lairInput').button.onclick();w.battle(false);assert(w.control('lairInput').pane.hidden);
});
test('template and toggle order place lair between setup and monster',()=>{
 const assembly=fs.readFileSync(path.join(root,'web_html/admin_html.py'),'utf8');
 assert(assembly.indexOf("'050_setup_input.html'")<assembly.indexOf("'185_lair_tools.html'"));
 assert(assembly.indexOf("'185_lair_tools.html'")<assembly.indexOf("'060_monster_input.html'"));
 assert.equal((assembly.match(/'185_lair_tools.html'/g)||[]).length,1);
 const buttons=fs.readFileSync(path.join(root,'templates/admin/010_pane_controls.html'),'utf8');
 assert(buttons.indexOf('id="toggleBattleSetupPane"')<buttons.indexOf('id="toggleLairPane"'));
 assert(buttons.indexOf('id="toggleLairPane"')<buttons.indexOf('id="toggleMonsterPane"'));
 assert.match(buttons,/aria-controls="lairTools"/);
 const lair=fs.readFileSync(path.join(root,'templates/admin/185_lair_tools.html'),'utf8');
 assert.match(lair,/class="pane pane-battle-group lair-tools"/);
 const css=fs.readFileSync(path.join(root,'static/admin.css'),'utf8');
 assert.match(css,/#toggleBattleSetupPane,\s*#toggleLairPane,\s*#toggleMonsterPane\s*\{/);
 assert.match(css,/#toggleLairPane:hover,\s*#toggleLairPane:focus-visible,/);
 assert(!fs.readFileSync(path.join(root,'static/lairs.css'),'utf8').includes('border:1px solid #8064a2'));
});
console.log(`${count} lair-pane checks passed`);
