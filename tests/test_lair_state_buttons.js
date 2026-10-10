/* DOM-mock tests: run with node tests/test_lair_state_buttons.js. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),source=fs.readFileSync(path.join(root,'static/lair-state-buttons.js'),'utf8');
function setup(lairs=[{id:'l',active:false,visible:false,in_turn:false}]) {
 const nodes=new Map();const get=id=>{if(!nodes.has(id)){const classes=new Set();nodes.set(id,{textContent:'',disabled:false,checked:false,attributes:{},classList:{toggle(k,v){v?classes.add(k):classes.delete(k);},contains:k=>classes.has(k)},setAttribute(k,v){this.attributes[k]=v;}});}return nodes.get(id);};
 let state={lairs:structuredClone(lairs)},requests=[],fail=false,hold=null,loads=0;
 const sandbox={latest:state,document:{getElementById:get},window:{scryingLairsRender(snapshot){get('lairActive').checked=snapshot.lairs[0]?.active;return 'rendered';}},
 load:async()=>{loads++;sandbox.window.scryingLairsRender(state);},
 fetch:async(url,options)=>{
  requests.push({url,options,body:JSON.parse(options.body)});if(hold)await hold;
  if(fail)return {ok:false,status:400,json:async()=>({detail:'Rejected'})};
  Object.assign(state.lairs[0],JSON.parse(options.body));if(!state.lairs[0].active)state.lairs[0].in_turn=false;
  if(state.lairs[0].in_turn)state.lairs[0].visible=true;
  return {ok:true,json:async()=>structuredClone(state.lairs[0])};
 }};
 vm.createContext(sandbox);vm.runInContext(source,sandbox);
 return {get,sandbox,requests,state,fail(value){fail=value;},hold(value){hold=value;},loads:()=>loads};
}
let count=0;
async function test(name,fn){await fn();count++;console.log('PASS: '+name);}
(async()=>{
 await test('inactive lair shows Join Battle; neutral Visible/Turn buttons',()=>{const w=setup();assert.equal(w.get('lairJoinBattle').textContent,'Join Battle');assert(!w.get('lairJoinBattle').classList.contains('on'));assert(w.get('lairToggleTurn').disabled);});
 await test('join patches active immediately and updates In Battle styling',async()=>{const w=setup();await w.get('lairJoinBattle').onclick();assert.deepEqual(w.requests[0].body,{active:true});assert.equal(w.get('lairJoinBattle').textContent,'In Battle');assert(w.get('lairJoinBattle').classList.contains('on'));assert(w.get('lairActive').checked);assert.equal(w.loads(),1);});
 await test('leave patches active false',async()=>{const w=setup([{id:'l',active:true,visible:true,in_turn:true}]);await w.get('lairJoinBattle').onclick();assert.deepEqual(w.requests[0].body,{active:false});assert(!w.get('lairToggleTurn').classList.contains('on'));});
 await test('visible toggle patches only visibility',async()=>{const w=setup();await w.get('lairToggleVisible').onclick();assert.deepEqual(w.requests[0].body,{visible:true});assert(w.get('lairVisible').checked);assert(w.get('lairToggleVisible').classList.contains('on'));assert.equal(w.get('lairToggleVisible').attributes['aria-pressed'],'true');});
 await test('turn toggle patches in_turn and reflects automatic visibility',async()=>{const w=setup([{id:'l',active:true,visible:false,in_turn:false}]);await w.get('lairToggleTurn').onclick();assert.deepEqual(w.requests[0].body,{in_turn:true});assert(w.get('lairToggleTurn').classList.contains('on'));assert(w.get('lairVisible').checked);await w.get('lairToggleTurn').onclick();assert.deepEqual(w.requests[1].body,{in_turn:false});});
 await test('inactive turn cannot submit',async()=>{const w=setup();await w.get('lairToggleTurn').onclick();assert.equal(w.requests.length,0);});
 await test('no lair disables state controls but preserves create defaults',()=>{const w=setup([]);for(const id of ['lairJoinBattle','lairToggleVisible','lairToggleTurn'])assert(w.get(id).disabled);assert(w.get('lairActive').checked);assert(w.get('lairVisible').checked);});
 await test('server errors preserve old styling and show notice',async()=>{const w=setup();w.fail(true);await w.get('lairJoinBattle').onclick();assert.equal(w.get('lairNotice').textContent,'Rejected');assert(!w.get('lairJoinBattle').classList.contains('on'));assert(!w.get('lairJoinBattle').disabled);});
 await test('busy guard suppresses duplicate requests',async()=>{const w=setup();let release;w.hold(new Promise(resolve=>release=resolve));const first=w.get('lairJoinBattle').onclick();await w.get('lairJoinBattle').onclick();assert.equal(w.requests.length,1);assert(w.get('lairJoinBattle').disabled);release();await first;});
 await test('renderer return value is preserved and hidden bridges reflect current state',()=>{const w=setup();const result=w.sandbox.window.scryingLairsRender({lairs:[{id:'l',active:true,visible:true,in_turn:true}]});assert.equal(result,'rendered');assert(w.get('lairActive').checked);assert(w.get('lairVisible').checked);assert(w.get('lairToggleTurn').classList.contains('on'));});
 await test('template replaces configuration checkboxes with non-submit buttons',()=>{const html=fs.readFileSync(path.join(root,'templates/admin/185_lair_tools.html'),'utf8');const pane=html.slice(0,html.indexOf('</section>'));assert(!pane.includes('type="checkbox"'));for(const id of ['lairJoinBattle','lairToggleVisible','lairToggleTurn'])assert(pane.includes(`id="${id}" type="button"`));assert(pane.includes('id="lairColorPreview"'));});
 console.log(`${count} lair-button frontend checks passed`);
})().catch(error=>{console.error(error);process.exitCode=1;});
