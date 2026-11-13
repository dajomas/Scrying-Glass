'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {test} = require('node:test');
const {createController} = require('../static/admin-feedback-controller.js');
const source = fs.readFileSync(path.join(__dirname,'../static/battle-actions-next.js'),'utf8');
const clone = value => JSON.parse(JSON.stringify(value));
const deferred = () => {let resolve;const promise=new Promise(yes=>{resolve=yes;});return {promise,resolve};};
const tick = () => new Promise(resolve=>setImmediate(resolve));
function fixture() {
    const config={}, timers=[], calls=[], opens=[], closes=[];
    const controller=createController({setTimeout(fn,ms){timers.push(ms);return timers.length;},clearTimeout(){}});
    let activeScope;
    const observe=state=>{activeScope=JSON.stringify([state.active_campaign_id,state.active_setup.campaign_id,state.active_setup.name]);
        controller.setScope('encounter',activeScope);return state;};
    const begin=spec=>controller.begin({...spec,lane:'encounter',scope:activeScope,placement:'global'});
    const feedback={...controller,begin};
    const main={disabled:false},button={disabled:false},submit={disabled:false},input={disabled:true};
    const notice={textContent:''}, modal={hidden:false,querySelectorAll:selector=>selector==='button[type="submit"]'?[submit]:[submit,input,button],
        addEventListener(type,handler){if(type==='submit')this.submit=handler;}};
    const nodes={nextBattle:main,nextBattleActions:button,battleActionModal:modal,battleActionNotice:notice};
    const server={active_campaign_id:'c',active_setup:{campaign_id:'c',name:'s'},battle_round:1,statistics_token:'old',
        characters:[{id:'a',active:true,in_turn:true},{id:'b',active:true,in_turn:false}],monsters:[],lairs:[]};
    observe(server);
    const emit=(operation,text=operation,target='battle')=>{const t=begin({region:'global',operation,target,label:operation});controller.publish(t,{severity:'error',text});};
    let reads=0,loads=0;
    const context={document:{readyState:'complete',getElementById:id=>nodes[id]},latest:clone(server),battleActionActorId:'a',battleActionsApplying:false,
        scryingAdminFeedback:feedback,message(){throw Error('Legacy message route');},
        async request(url,options={}) {
            calls.push({url,options});
            if(url==='/api/state') {
                reads++;if(config.failPreflight && reads===1)throw Error('Preflight offline');
                if(config.onRead)await config.onRead(reads);
                return observe(clone(server));
            }
            if(url==='/api/battle/next') {
                assert.equal(options.method,'POST');if(config.hold)await config.hold.promise;
                server.characters.forEach(c=>{c.in_turn=c.id===(config.noActor?null:'b');});server.statistics_token='next';
                if(config.failNext)throw Error('Response lost');
                return {current:server.characters.find(c=>c.in_turn)||null};
            }
            if(url==='/api/battle/actions') {if(config.holdApply)await config.holdApply.promise;return {applied:1};}
            throw Error('Unexpected request '+url);
        },
        async load(strict) {
            assert.equal(strict,true);loads++;
            if(config.failLoads===Infinity || loads<=(config.failLoads||0)) {
                if(config.loadNotice)emit('state.load','State refresh failed','state');
                throw Error('Refresh offline');
            }
            context.latest=observe(clone(server));
        },
        closeBattleActions(){closes.push(context.battleActionActorId);modal.hidden=true;context.battleActionActorId=null;},
        openBattleActions(id){opens.push(id);context.battleActionActorId=id;modal.hidden=false;}};
    context.window=context;vm.createContext(context);vm.runInContext(source,context);
    return {context,config,server,main,button,submit,input,modal,notice,feedback,emit,timers,calls,opens,closes,
        next:fromModal=>(fromModal?button:main).onclick(),
        posts:()=>calls.filter(c=>c.url==='/api/battle/next'),
        records:()=>controller.snapshot().map(r=>({operation:r.operation,severity:r.severity,text:r.text})),
        changeScope(name){server.active_setup.name=name;context.latest=observe(clone(server));},
        counts:()=>({reads,loads})};
}
test('modal success posts once, closes and reopens the authoritative actor',async()=>{
    const f=fixture();assert.equal(await f.next(true),undefined);assert.equal(f.posts().length,1);
    assert.deepEqual(f.opens,['b']);assert.equal(f.closes.length,1);assert.deepEqual(f.records(),[]);
    assert.equal(f.main.disabled,false);assert.equal(f.button.disabled,false);assert.equal(f.input.disabled,true);
});
test('main success leaves the modal closed without opening an actor',async()=>{
    const f=fixture();f.modal.hidden=true;await f.next(false);assert.equal(f.posts().length,1);assert.deepEqual(f.opens,[]);assert.equal(f.modal.hidden,true);
});
test('preflight failure is persistent, makes no POST and retains drafts/modal',async()=>{
    const f=fixture();f.config.failPreflight=true;await f.next(true);assert.equal(f.posts().length,0);assert.equal(f.closes.length,0);assert.equal(f.modal.hidden,false);
    assert.match(f.records()[0].text,/Unable to prepare turn advancement/);assert.equal(f.records()[0].severity,'error');assert.equal(f.timers.length,0);
});
test('lost response reports uncertainty and reconciles without POST retry or reopening',async()=>{
    const f=fixture();f.config.failNext=true;await f.next(true);assert.equal(f.posts().length,1);assert.deepEqual(f.opens,[]);assert.equal(f.modal.hidden,true);
    assert.match(f.records()[0].text,/outcome is uncertain/);assert.match(f.records()[0].text,/State refreshed/);assert.match(f.records()[0].text,/No automatic retry/);
    assert.equal(f.context.latest.characters.find(c=>c.in_turn).id,'b');assert.equal(f.timers.length,0);
});
test('confirmed mutation with failed refresh is not reported as an unconfirmed POST',async()=>{
    const f=fixture();f.config.failLoads=Infinity;f.config.loadNotice=true;await f.next(true);
    const next=f.records().find(r=>r.operation==='battle.next');assert.match(next.text,/Turn advanced, but refresh\/reconciliation failed/);
    assert.match(next.text,/Refresh before continuing/);assert.doesNotMatch(next.text,/outcome is uncertain/);assert.equal(f.posts().length,1);
    assert.ok(f.records().some(r=>r.operation==='state.load'));assert.deepEqual(f.opens,[]);
});
test('successful manual Next resolves only its related error',async()=>{
    const f=fixture();f.config.failNext=true;await f.next(true);f.emit('battle.start');f.emit('state.load');
    f.config.failNext=false;await f.next(false);assert.deepEqual(f.records().map(r=>r.operation),['battle.start','state.load']);assert.equal(f.posts().length,2);
});
test('successful refresh alone does not erase uncertain Next feedback',async()=>{
    const f=fixture();f.config.failNext=true;await f.next(false);await f.context.load(true);
    assert.deepEqual(f.records().map(r=>r.operation),['battle.next']);
});
test('repeated failed manual attempts replace one related error',async()=>{
    const f=fixture();f.config.failNext=true;await f.next(false);await f.next(false);
    assert.equal(f.records().filter(r=>r.operation==='battle.next').length,1);assert.equal(f.posts().length,2);
});
test('settled preparation report can be replaced after failed reconciliation',async()=>{
    const f=fixture();f.server.characters.forEach(c=>{c.in_turn=c.id==='b';});f.config.failLoads=1;
    await f.next(true);assert.equal(f.posts().length,0);assert.equal(f.counts().loads,2);
    assert.equal(f.records().length,1);assert.match(f.records()[0].text,/Unable to prepare turn advancement/);assert.match(f.records()[0].text,/Refresh offline/);
});
test('old-scope failure does not overwrite new-scope global or modal feedback',async()=>{
    const f=fixture();f.config.hold=deferred();f.config.failNext=true;const operation=f.next(true);await tick();
    f.changeScope('other');f.emit('other.operation','Current encounter error');f.notice.textContent='Current modal notice';
    f.config.hold.resolve();await operation;assert.deepEqual(f.records().map(r=>r.text),['Current encounter error']);assert.equal(f.notice.textContent,'Current modal notice');
});
test('scope A-B-A rejects feedback from the old encounter epoch',async()=>{
    const f=fixture();f.config.hold=deferred();f.config.failNext=true;const operation=f.next(false);await tick();
    f.changeScope('other');f.changeScope('s');f.notice.textContent='New epoch';f.config.hold.resolve();await operation;
    assert.deepEqual(f.records(),[]);assert.equal(f.notice.textContent,'New epoch');
});
test('old-scope success cannot resolve a new encounter Next error',async()=>{
    const f=fixture();f.config.hold=deferred();const operation=f.next(false);await tick();
    f.changeScope('other');f.emit('battle.next','New encounter Next error');f.config.hold.resolve();await operation;
    assert.deepEqual(f.records().map(r=>r.text),['New encounter Next error']);
});
test('no active participant is explicit info and resolves the prior Next error',async()=>{
    const f=fixture();f.emit('battle.next','Earlier error');f.emit('other.operation');f.config.noActor=true;await f.next(true);
    const next=f.records().filter(r=>r.operation==='battle.next');assert.deepEqual(next,[{operation:'battle.next',severity:'info',text:'No active participant remains.'}]);
    assert.ok(f.records().some(r=>r.operation==='other.operation'));assert.equal(f.modal.hidden,true);assert.deepEqual(f.opens,[]);
});
test('double modal click and main Next share one in-flight guard',async()=>{
    const f=fixture();f.config.hold=deferred();const operation=f.next(true);await tick();await f.next(true);await f.next(false);
    assert.equal(f.posts().length,1);f.config.hold.resolve();await operation;assert.equal(f.posts().length,1);
});
test('action write in flight blocks Next without changing feedback',async()=>{
    const f=fixture();f.emit('battle.next','Keep error');f.config.holdApply=deferred();
    const apply=f.context.request('/api/battle/actions',{method:'POST'});await tick();await f.next(true);assert.equal(f.posts().length,0);
    assert.deepEqual(f.records().map(r=>r.text),['Keep error']);f.config.holdApply.resolve();await apply;
});
test('Next blocks a new action POST and captures form submission',async()=>{
    const f=fixture();f.config.hold=deferred();const operation=f.next(true);await tick();
    await assert.rejects(f.context.request('/api/battle/actions',{method:'POST'}),/Turn advancement is in progress/);
    let prevented=0;f.modal.submit({preventDefault(){prevented++;},stopImmediatePropagation(){prevented++;}});assert.equal(prevented,2);
    f.config.hold.resolve();await operation;
});
test('disabled submit controls block Next without issuing a request',async()=>{
    const f=fixture();f.submit.disabled=true;await f.next(true);assert.equal(f.calls.length,0);
});
test('actor changed before POST retains the modal and requests review',async()=>{
    const f=fixture();f.server.characters.forEach(c=>{c.in_turn=c.id==='b';});await f.next(true);
    assert.equal(f.posts().length,0);assert.equal(f.closes.length,0);assert.match(f.records()[0].text,/Encounter or turn changed/);
});
test('unrelated success cannot clear a Next error',async()=>{
    const f=fixture();f.config.failNext=true;await f.next(false);
    const ticket=f.feedback.begin({region:'global',operation:'other',target:'battle',label:'Other'});f.feedback.resolve(ticket);
    assert.deepEqual(f.records().map(r=>r.operation),['battle.next']);
});
test('lifetime guard creates no visible notice and is retired on completion',async()=>{
    const f=fixture();await f.next(false);assert.deepEqual(f.records(),[]);assert.equal(f.timers.length,0);
    f.config.failNext=true;await f.next(false);assert.equal(f.records().length,1);assert.equal(f.records()[0].operation,'battle.next');
});
