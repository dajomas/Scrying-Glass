// Production export/clear slice with real feedback; mocked DOM/network, not full Admin.
'use strict';
const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const read = p => fs.readFileSync(path.join(root,p),'utf8');
const {createController} = require(path.join(root,'static/admin-feedback-controller.js'));
const core = read('static/admin/040-source.js');
const start = core.indexOf("document.querySelector('#exportActivityLogCsv').onclick");
const end = core.indexOf("csvImportModal.addEventListener('click'",start);
assert.ok(start>=0 && end>start);
const source = core.slice(start,end);
const spec = {region:'global',operation:'activity-log.clear',target:'activity-log',label:'Clear activity log'};
function deferred() {let resolve,reject; const promise=new Promise((a,b)=>{resolve=a;reject=b;}); return {promise,resolve,reject};}
function fixture() {
    const controls = new Map(), calls=[], prompts=[], timers=new Map(); let serial=0, refreshes=0;
    const f={calls,prompts,timers,accept:true,onRequest:async()=>({cleared:3}),onLoad:async()=>{}};
    const controller=createController({setTimeout(fn,ms){timers.set(++serial,{fn,ms});return serial;},clearTimeout(id){timers.delete(id);}});
    const context=vm.createContext({latest:{activity_log:[{}, {}, {}]}, window:{location:{href:'unchanged'}},
        ScryingFeedback:{createController:()=>controller},
        document:{getElementById:()=>null,querySelector(selector){if(!controls.has(selector))controls.set(selector,{});return controls.get(selector);}},
        confirm(text){prompts.push(text);return f.accept;},
        request:async(...args)=>{calls.push(args);return f.onRequest(...args);},
        load:async()=>{refreshes++;return f.onLoad();},
        message(){throw new Error('Clear must not use compatibility feedback');}});
    vm.runInContext(read('static/admin-feedback-admin.js'),context);
    const feedback=context.window.scryingAdminFeedback;
    Object.assign(f,{feedback,context,refreshes:()=>refreshes,snapshot:()=>feedback.snapshot(),
        scope(campaign='a',name='one'){assert.equal(feedback.observeState({active_campaign_id:campaign,active_setup:{campaign_id:campaign,name}},feedback.stateRequest()),true);},
        setLog(value){context.latest={activity_log:value};},
        seed(text='old',operation=spec.operation,target=spec.target,severity='error'){
            return feedback.publish(feedback.begin({...spec,operation,target}),{severity,text});},
        click:()=>controls.get('#clearActivityLog').onclick(),
        export:format=>controls.get('#exportActivityLog'+format).onclick()});
    f.scope(); vm.runInContext(source,context); return f;
}
test('cancel retains count confirmation, existing error and pending identity',async()=>{
    const f=fixture();f.seed(); const ticket=f.feedback.begin(spec);f.accept=false;await f.click();
    assert.equal(f.prompts[0],'Clear all 3 activity log entries?');assert.equal(f.calls.length,0);
    assert.equal(f.refreshes(),0);assert.equal(f.snapshot()[0].text,'old');assert.equal(f.feedback.isCurrent(ticket),true);
});
test('empty emits explicit info without confirmation, request or refresh',async()=>{
    const f=fixture();f.setLog([]);await f.click();assert.equal(f.snapshot()[0].severity,'info');
    assert.equal(f.snapshot()[0].text,'The activity log is already empty.');assert.equal(f.prompts.length,0);
    assert.equal(f.calls.length,0);assert.equal(f.refreshes(),0);assert.equal(f.timers.size,0);
});
test('empty is not server success and cannot erase a matching clear failure',async()=>{
    const f=fixture();f.seed();f.setLog([]);await f.click();assert.equal(f.snapshot().length,2);
    assert.equal(f.snapshot().find(x=>x.severity==='error').text,'old');
});
test('repeated empty notices replace one info record without erasing errors',async()=>{
    const f=fixture();f.seed();f.setLog([]);await f.click();await f.click();
    assert.equal(f.snapshot().filter(x=>x.severity==='info').length,1);assert.equal(f.snapshot().filter(x=>x.severity==='error').length,1);
});
test('confirmed clear preserves one bodyless POST and publishes before refresh',async()=>{
    const f=fixture();f.onRequest=async(url,options)=>{assert.equal(url,'/api/activity-log/clear');
        assert.equal(options.method,'POST');assert.deepEqual(Object.keys(options),['method']);return {cleared:3};};
    f.onLoad=async()=>{assert.equal(f.snapshot()[0].severity,'success');};await f.click();
    assert.equal(f.calls.length,1);assert.equal(f.refreshes(),1);assert.equal(f.snapshot()[0].text,'Cleared 3 activity log entries.');
});
test('success reports server count with singular wording',async()=>{
    const f=fixture();f.onRequest=async()=>({cleared:1});await f.click();assert.equal(f.snapshot()[0].text,'Cleared 1 activity log entry.');
});
test('server-confirmed zero is success, distinct from the local empty shortcut',async()=>{
    const f=fixture();f.onRequest=async()=>({cleared:0});await f.click();
    assert.equal(f.snapshot()[0].severity,'success');assert.equal(f.snapshot()[0].text,'Cleared 0 activity log entries.');assert.equal(f.calls.length,1);
});
test('request failure is persistent and never refreshes or automatically retries',async()=>{
    const f=fixture();f.onRequest=async()=>{throw new Error('denied');};await f.click();
    assert.equal(f.snapshot()[0].severity,'error');assert.equal(f.snapshot()[0].text,'denied');
    assert.equal(f.timers.size,0);assert.equal(f.calls.length,1);assert.equal(f.refreshes(),0);
});
test('successful retry with changed count clears only related error and info',async()=>{
    const f=fixture();f.seed('other','combatant.reset','x');f.onRequest=async()=>{throw new Error('denied');};await f.click();
    f.setLog([]);await f.click();f.setLog([{}]);f.onRequest=async()=>({cleared:1});await f.click();
    assert.equal(f.snapshot().filter(x=>x.operation===spec.operation).length,1);
    assert.equal(f.snapshot().find(x=>x.operation===spec.operation).severity,'success');
    assert.equal(f.snapshot().find(x=>x.operation==='combatant.reset').text,'other');
});
test('success expires at five seconds without removing unrelated error',async()=>{
    const f=fixture();f.seed('other','combatant.reset','x');await f.click();const timer=[...f.timers.values()][0];
    assert.equal(timer.ms,5000);timer.fn();assert.equal(f.snapshot().length,1);assert.equal(f.snapshot()[0].text,'other');
});
test('ordinary refresh and unrelated success cannot clear a failed clear',async()=>{
    const f=fixture();f.seed();await f.context.load();f.seed('ok','battle.reset-all','battle','success');
    assert.equal(f.snapshot().find(x=>x.operation===spec.operation).severity,'error');
});
test('confirmed clear and real loadState refresh failure coexist with one POST',async()=>{
    const f=fixture();f.onLoad=()=>f.feedback.loadState(()=>{f.feedback.stateRequest();return Promise.reject(new Error('refresh failed'));},()=>{});
    await f.click();assert.equal(f.snapshot().find(x=>x.operation===spec.operation).severity,'success');
    assert.equal(f.snapshot().find(x=>x.operation==='state.load').text,'refresh failed');assert.equal(f.calls.length,1);
});
test('unexpected refresh rejection is not mislabeled a clear request failure',async()=>{
    const f=fixture();f.onLoad=async()=>{throw new Error('refresh');};await assert.rejects(f.click(),/refresh/);
    assert.equal(f.snapshot()[0].severity,'success');assert.equal(f.calls.length,1);
});
test('old-setup success cannot publish or refresh new setup',async()=>{
    const f=fixture(),p=deferred();f.onRequest=()=>p.promise;const done=f.click();f.scope('a','two');f.seed('new');
    p.resolve({cleared:3});await done;assert.equal(f.snapshot()[0].text,'new');assert.equal(f.refreshes(),0);
});
test('old-campaign failure cannot overwrite new campaign feedback',async()=>{
    const f=fixture(),p=deferred();f.onRequest=()=>p.promise;const done=f.click();f.scope('b');f.seed('new');
    p.reject(new Error('old'));await done;assert.equal(f.snapshot()[0].text,'new');
});
test('away-and-back scope changes cannot revive old clear response',async()=>{
    const f=fixture(),p=deferred();f.onRequest=()=>p.promise;const done=f.click();f.scope('b');f.scope();
    p.resolve({cleared:3});await done;assert.equal(f.snapshot().length,0);assert.equal(f.refreshes(),0);
});
test('newer same-operation failure supersedes old success without adding concurrency policy',async()=>{
    const f=fixture(),p=deferred();let n=0;f.onRequest=()=>++n===1?p.promise:Promise.reject(new Error('new'));
    const old=f.click();await f.click();assert.equal(f.calls.length,2);p.resolve({cleared:3});await old;
    assert.equal(f.snapshot()[0].text,'new');assert.equal(f.refreshes(),0);
});
test('newer success supersedes old failure',async()=>{
    const f=fixture(),p=deferred();let n=0;f.onRequest=()=>++n===1?p.promise:Promise.resolve({cleared:0});
    const old=f.click();await f.click();p.reject(new Error('old'));await old;
    assert.equal(f.snapshot()[0].severity,'success');assert.equal(f.refreshes(),1);
});
test('newer empty observation supersedes pending clear but does not clear a prior error',async()=>{
    const f=fixture(),p=deferred();f.seed();f.onRequest=()=>p.promise;const old=f.click();f.setLog([]);await f.click();
    p.resolve({cleared:3});await old;assert.equal(f.snapshot().filter(x=>x.severity==='info').length,1);
    assert.equal(f.snapshot().find(x=>x.severity==='error').text,'old');assert.equal(f.refreshes(),0);assert.equal(f.calls.length,1);
});
test('CSV and JSON export navigation remains unchanged with no feedback or clear request',()=>{
    const f=fixture();f.seed();f.export('Csv');assert.equal(f.context.window.location.href,'/api/activity-log.csv');
    f.export('Json');assert.equal(f.context.window.location.href,'/api/activity-log.json');
    assert.equal(f.snapshot().length,1);assert.equal(f.snapshot()[0].text,'old');assert.equal(f.calls.length,0);assert.equal(f.prompts.length,0);
});
test('non-array activity data retains existing empty fallback',async()=>{
    const f=fixture();for(const value of [null,undefined,{},'bad']){f.setLog(value);await f.click();}
    assert.equal(f.snapshot().length,1);assert.equal(f.snapshot()[0].severity,'info');assert.equal(f.calls.length,0);
});
