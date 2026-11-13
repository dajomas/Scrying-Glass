// Production helper/open functions with real feedback/bootstrap; mocked UI and transport.
'use strict';
const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const {installFeedback} = require('./battle-action-feedback-fixture.cjs');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'static/admin/060-source.js'), 'utf8');
const helperStart = source.indexOf('function battleActionFeedback(');
const helperEnd = source.indexOf('function closeBattleActions()', helperStart);
const openStart = source.indexOf('function openBattleActions(');
assert.ok(helperStart >= 0 && helperEnd > helperStart && openStart > helperEnd);
const block = source.slice(helperStart, helperEnd) + source.slice(openStart);
const spec = {region:'global', operation:'battle.actions.eligibility', target:'m', label:'Battle actions: M'};
function fixture() {
    const nodes = new Map(), reactions = [], timers = new Map(); let serial = 0, lairs = 0;
    const ctx = {latest:{monsters:[{id:'m',name:'M',active:false,in_turn:true,alive:true}],characters:[],lairs:[],statistics_token:'new-token'},
        battleActionsApplying:false,battleActionActorId:'previous',battleStatisticsToken:'previous-token',
        battleActionRows:{innerHTML:'retained rows'},battleActionModal:{hidden:true},
        document:{querySelector(id){if(!nodes.has(id)) nodes.set(id,{textContent:'retained notice'});return nodes.get(id);}},
        addBattleActionRow(reaction){reactions.push(reaction);},
        message(){throw new Error('Eligibility must not use legacy feedback');},
        request(){throw new Error('Opening must not send a mutation');},
        load(){throw new Error('Opening must not refresh');}};
    const {feedback,scope} = installFeedback(ctx, {setTimeout(fn,ms){timers.set(++serial,{fn,ms});return serial;},clearTimeout(id){timers.delete(id);}});
    ctx.window.scryingOpenLairAction = () => {lairs++;};
    vm.runInContext(block,ctx);
    return {ctx,nodes,reactions,timers,feedback,scope,lairs:()=>lairs,snapshot:()=>feedback.snapshot(),
        open:id=>ctx.openBattleActions(id),
        ready(){ctx.latest.monsters[0].active=true;},
        seed(operation='fixture.other',target='x',text='unrelated'){
            feedback.publish(feedback.begin({...spec,operation,target}),{severity:'error',text});}};
}
test('missing actor yields explicit persistent ID-targeted error without opening or mutation',()=>{
    const f=fixture();f.open('missing');const n=f.snapshot()[0];
    assert.equal(n.operation,spec.operation);assert.equal(n.target,'missing');assert.equal(n.severity,'error');
    assert.equal(n.text,'Only the current active combatant can perform battle actions.');
    assert.equal(n.label,'Battle actions: missing');assert.equal(f.timers.size,0);assert.equal(f.ctx.battleActionModal.hidden,true);
    assert.equal(f.ctx.battleActionActorId,'previous');assert.equal(f.ctx.battleActionRows.innerHTML,'retained rows');
});
test('inactive actor retains existing eligibility gate and name label',()=>{
    const f=fixture();f.open('m');assert.equal(f.snapshot()[0].severity,'error');assert.equal(f.snapshot()[0].label,'Battle actions: M');assert.equal(f.reactions.length,0);
});
test('off-turn active actor remains rejected',()=>{
    const f=fixture();f.ready();f.ctx.latest.monsters[0].in_turn=false;f.open('m');assert.equal(f.snapshot()[0].severity,'error');assert.equal(f.reactions.length,0);
});
test('matching valid opening silently resolves its actual earlier eligibility failure',()=>{
    const f=fixture();f.open('m');f.ready();f.open('m');assert.equal(f.snapshot().length,0);assert.equal(f.timers.size,0);
    assert.equal(f.ctx.battleActionActorId,'m');assert.equal(f.ctx.battleStatisticsToken,'new-token');
    assert.equal(f.ctx.battleActionRows.innerHTML,'');assert.equal(f.ctx.battleActionModal.hidden,false);
    assert.equal(f.nodes.get('#battleActionNotice').textContent,'');assert.equal(f.nodes.get('#battleActionTitle').textContent,'Battle actions: M');
    assert.deepEqual(f.reactions,[false]);
});
test('opening another valid actor cannot clear the first actors error',()=>{
    const f=fixture();f.open('m');f.ctx.latest.characters=[{id:'c',name:'C',active:true,in_turn:true,alive:true}];f.open('c');
    assert.equal(f.snapshot().length,1);assert.equal(f.snapshot()[0].target,'m');
});
test('matching valid opening leaves unrelated operation error intact',()=>{
    const f=fixture();f.seed();f.open('m');f.ready();f.open('m');assert.equal(f.snapshot().length,1);assert.equal(f.snapshot()[0].text,'unrelated');
});
test('repeated same actor rejection replaces its error with no timer',()=>{
    const f=fixture();f.open('m');f.open('m');assert.equal(f.snapshot().length,1);assert.equal(f.timers.size,0);
});
test('actor rename does not change retry identity',()=>{
    const f=fixture();f.open('m');f.ctx.latest.monsters[0].name='Renamed';f.ready();f.open('m');assert.equal(f.snapshot().length,0);
});
test('busy opening does not create or resolve feedback or change modal state',()=>{
    const f=fixture();f.open('m');f.ready();const ticket=f.feedback.begin(spec);f.ctx.battleActionsApplying=true;f.open('m');
    assert.equal(f.snapshot().length,1);assert.equal(f.feedback.isCurrent(ticket),true);assert.equal(f.ctx.battleActionRows.innerHTML,'retained rows');
});
test('lair delegation precedes eligibility feedback and preserves pending identity',()=>{
    const f=fixture();f.ctx.latest.lairs=[{id:'l'}];const ticket=f.feedback.begin(spec);f.open('l');
    assert.equal(f.lairs(),1);assert.equal(f.snapshot().length,0);assert.equal(f.feedback.isCurrent(ticket),true);assert.equal(f.reactions.length,0);
});
test('missing optional lair opener retains no-op behavior',()=>{
    const f=fixture();f.ctx.latest.lairs=[{id:'l'}];delete f.ctx.window.scryingOpenLairAction;f.open('l');assert.equal(f.snapshot().length,0);assert.equal(f.reactions.length,0);
});
test('dead active current actor remains eligible and starts a reaction row',()=>{
    const f=fixture();f.ready();f.ctx.latest.monsters[0].alive=false;f.open('m');assert.deepEqual(f.reactions,[true]);assert.equal(f.ctx.battleActionModal.hidden,false);assert.equal(f.snapshot().length,0);
});
test('character rejection and matching retry use character ID',()=>{
    const f=fixture();f.ctx.latest.characters=[{id:'c',name:'C',active:true,in_turn:false,alive:true}];f.open('c');
    assert.equal(f.snapshot()[0].target,'c');f.ctx.latest.characters[0].in_turn=true;f.open('c');assert.equal(f.snapshot().length,0);
});
test('real bootstrap retires old-scope eligibility and prevents away-and-back revival',()=>{
    const f=fixture();f.open('m');const old=f.feedback.begin(spec);f.scope('other','setup');
    assert.equal(f.snapshot().length,0);assert.equal(f.feedback.publish(old,{severity:'error',text:'late'}),false);
    f.scope();assert.equal(f.snapshot().length,0);f.ready();f.open('m');assert.equal(f.snapshot().length,0);
});
test('unrelated success cannot resolve eligibility failure',()=>{
    const f=fixture();f.open('m');f.feedback.publish(f.feedback.begin({...spec,operation:'fixture.success'}),{severity:'success',text:'ok'});
    assert.equal(f.snapshot().find(x=>x.operation===spec.operation).severity,'error');
});
test('shared helper preserves explicit outcome severity and distinct targets',()=>{
    const f=fixture();f.ctx.battleActionFeedback('fixture','active','Targets',{severity:'error',text:'problem'});
    f.ctx.battleActionFeedback('fixture','living','Targets');assert.equal(f.snapshot().length,1);
    f.ctx.battleActionFeedback('fixture','active','Targets',{severity:'info',text:'observation'});
    assert.equal(f.snapshot().filter(x=>x.severity==='error').length,1);
    f.ctx.battleActionFeedback('fixture','active','Targets');assert.equal(f.snapshot().length,0);
});
