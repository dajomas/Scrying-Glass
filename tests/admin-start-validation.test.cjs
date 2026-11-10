'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {test} = require('node:test');
const {createController} = require('../static/admin-feedback-controller.js');
const read = file => fs.readFileSync(path.join(__dirname, '..', file), 'utf8');
const asset = read('static/admin-start-validation.js');
const core = read('static/admin/070-source.js');
const from = core.indexOf('function characterPermanentlyDead(');
const to = core.indexOf('async function startBattle(', from);
assert.ok(from >= 0 && to > from, 'Cannot isolate production ordering/validation helpers');
function fixture() {
    let scope = 'a';
    const timers = [], orders = [], c = createController({setTimeout(fn, ms) {timers.push(ms); return timers.length;}, clearTimeout() {}});
    c.setScope('encounter', scope);
    const feedback = {...c, begin: spec => c.begin({...spec,lane:'encounter',scope,placement:'global'})};
    const nodes = Object.fromEntries(['startBattle','confirmOrder','cancelOrder','tieGroups','tieModal'].map(id=>[id,{hidden:true,innerHTML:'',addEventListener(){}}]));
    const context = {latest:{characters:[],monsters:[],lairs:[]}, document:{querySelector:s=>nodes[s.slice(1)],
        querySelectorAll: selector => context.selections.filter(s=>selector.includes('"'+s.dataset.tieBucket+'"'))},
        selections:[],esc:String,scryingAdminFeedback:feedback,
        all:()=>[...context.latest.monsters,...context.latest.characters],
        startBattle:order=>orders.push(Array.from(order)),message(){throw Error('Legacy message route');}};
    context.window=context;
    vm.createContext(context); vm.runInContext(core.slice(from,to),context);
    const cancelFrom=core.indexOf("document.querySelector('#cancelOrder').onclick");
    const cancelTo=core.indexOf("document.querySelector('#nextBattle').onclick",cancelFrom);
    assert.ok(cancelFrom>=0 && cancelTo>cancelFrom);
    vm.runInContext(core.slice(cancelFrom,cancelTo),context);
    const start=context.startBattle, cancel=nodes.cancelOrder.onclick;
    vm.runInContext(asset,context);
    assert.equal(context.startBattle,start); assert.equal(nodes.cancelOrder.onclick,cancel);
    return {context,nodes,orders,timers,feedback,
        errors:()=>c.snapshot().map(r=>({operation:r.operation,text:r.text,severity:r.severity})),
        emit(operation){const t=feedback.begin({region:'global',operation,target:'battle',label:operation}); c.publish(t,{severity:'error',text:operation});},
        scope(value){scope=value;c.setScope('encounter',scope);},
        install(){vm.runInContext(asset,context);}};
}
const actor=(id,initiative=10,extra={})=>({id,name:id,initiative,active:true,alive:true,life_state:'standing',...extra});
function ties(f) {
    f.context.latest.characters=[actor('a'),actor('b')];
    f.nodes.startBattle.onclick();
    f.context.selections=['a','b'].map((id,i)=>({value:String(i+1),dataset:{tieMember:id,tieBucket:'0'}}));
}
test('asset loads once after core and the 4A.2 override',()=>{
    const html=read('templates/admin/190_document_end.html');
    const url='/static/admin-start-validation.js?v=1';
    assert.equal(html.split(url).length-1,1);
    assert.ok(html.indexOf('/static/admin.js')<html.indexOf(url));
    assert.ok(html.indexOf('/static/admin-initial-visibility.js')<html.indexOf(url));
    assert.ok(html.includes('<script src="'+url+'" defer></script>'));
    const f=fixture(), handler=f.nodes.startBattle.onclick;f.install();assert.equal(f.nodes.startBattle.onclick,handler);
});
test('empty eligibility rejection is persistent and makes no Start call',()=>{
    const f=fixture();f.nodes.startBattle.onclick();f.nodes.startBattle.onclick();
    assert.deepEqual(f.orders,[]);assert.equal(f.timers.length,0);
    assert.deepEqual(f.errors(),[{operation:'battle.start.eligibility',text:'Activate at least one turn-eligible participant first',severity:'error'}]);
});
test('eligible retry resolves only eligibility, preserving request and refresh errors',()=>{
    const f=fixture();f.nodes.startBattle.onclick();f.emit('battle.start');f.emit('state.load');
    f.context.latest.characters=[actor('c',12)];f.nodes.startBattle.onclick();
    assert.deepEqual(f.orders,[['c']]);assert.deepEqual(f.errors().map(r=>r.operation),['battle.start','state.load']);
});
test('active lair permits empty order, inactive lair does not',()=>{
    const f=fixture();f.context.latest.lairs=[{active:false}];f.nodes.startBattle.onclick();assert.equal(f.orders.length,0);
    f.context.latest.lairs[0].active=true;f.nodes.startBattle.onclick();assert.deepEqual(f.orders,[[]]);assert.deepEqual(f.errors(),[]);
});
test('dead/inactive participants do not bypass the existing eligibility gate',()=>{
    const f=fixture();f.context.latest.characters=[actor('dead',12,{death_failures:3}),actor('inactive',10,{active:false})];
    f.context.latest.monsters=[actor('monster',8,{monster_species:'x',alive:false})];
    f.nodes.startBattle.onclick();assert.equal(f.orders.length,0);assert.equal(f.errors()[0].operation,'battle.start.eligibility');
});
test('opening and cancelling ties preserve their error and selections',()=>{
    const f=fixture();f.emit('battle.start.tie-order');ties(f);assert.equal(f.nodes.tieModal.hidden,false);
    const selections=JSON.stringify(f.context.selections);f.nodes.cancelOrder.onclick();
    assert.equal(f.nodes.tieModal.hidden,true);assert.equal(JSON.stringify(f.context.selections),selections);
    assert.deepEqual(f.errors().map(r=>r.operation),['battle.start.tie-order']);assert.deepEqual(f.orders,[]);
});
test('duplicate tie positions retain modal and emit one persistent validation error',()=>{
    const f=fixture();ties(f);f.context.selections[1].value='1';f.nodes.confirmOrder.onclick();f.nodes.confirmOrder.onclick();
    assert.equal(f.nodes.tieModal.hidden,false);assert.deepEqual(f.orders,[]);assert.equal(f.timers.length,0);
    assert.deepEqual(f.errors(),[{operation:'battle.start.tie-order',text:'Each combatant in an initiative tie must have a unique position',severity:'error'}]);
});
test('incomplete tie controls retain the original rejection',()=>{
    const f=fixture();ties(f);f.context.selections.pop();f.nodes.confirmOrder.onclick();
    assert.equal(f.errors()[0].text,'Tie selection data is incomplete');assert.deepEqual(f.orders,[]);
});
test('corrected tie confirmation resolves only tie error and preserves chosen order',()=>{
    const f=fixture();ties(f);f.context.selections[1].value='1';f.nodes.confirmOrder.onclick();f.emit('battle.start');f.emit('state.load');
    f.context.selections[0].value='2';f.nodes.confirmOrder.onclick();
    assert.deepEqual(f.orders,[['b','a']]);assert.equal(f.nodes.tieModal.hidden,true);
    assert.deepEqual(f.errors().map(r=>r.operation),['battle.start','state.load']);
});
test('a subsequent valid no-tie Start resolves obsolete tie error',()=>{
    const f=fixture();f.emit('battle.start.tie-order');f.context.latest.characters=[actor('c')];f.nodes.startBattle.onclick();
    assert.deepEqual(f.errors(),[]);assert.deepEqual(f.orders,[['c']]);
});
test('passing eligibility and opening ties does not resolve tie rejection',()=>{
    const f=fixture();f.nodes.startBattle.onclick();f.emit('battle.start.tie-order');ties(f);
    assert.deepEqual(f.errors().map(r=>r.operation),['battle.start.tie-order']);assert.equal(f.orders.length,0);
});
test('normal order and mixed tie defaults remain character-first without mutating state',()=>{
    const f=fixture();f.context.latest.characters=[actor('c',10),actor('high',20)];f.context.latest.monsters=[actor('m',10,{monster_species:'x'})];
    const before=JSON.stringify(f.context.latest);f.nodes.startBattle.onclick();
    assert.ok(f.nodes.tieGroups.innerHTML.indexOf('data-tie-member="c"')<f.nodes.tieGroups.innerHTML.indexOf('data-tie-member="m"'));
    f.context.selections=[{value:'2',dataset:{tieMember:'c',tieBucket:'0'}},{value:'1',dataset:{tieMember:'m',tieBucket:'0'}}];
    f.nodes.confirmOrder.onclick();assert.deepEqual(f.orders,[['high','m','c']]);assert.equal(JSON.stringify(f.context.latest),before);
});
test('scope transition retires validation notices without restoring them',()=>{
    const f=fixture();f.nodes.startBattle.onclick();f.scope('b');assert.deepEqual(f.errors(),[]);f.scope('a');assert.deepEqual(f.errors(),[]);
});
