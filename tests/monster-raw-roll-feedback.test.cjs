const {test} = require('node:test');
const a = require('node:assert/strict'), fs = require('node:fs'), vm = require('node:vm'), path = require('node:path');
const {createController} = require('../static/admin-feedback-controller.js');
const source = fs.readFileSync(path.join(__dirname, '../static/monster-initiative-roll.js'), 'utf8');
const op = x => 'monster.raw-roll.' + x;
const tick = () => new Promise(r => setImmediate(r));
function wait() {let yes, no; const promise = new Promise((y, n) => {yes=y; no=n;}); return {promise, yes, no};}
function fixture() {
    const timers=[], c=createController({setTimeout: f => {timers.push(f); return f;}, clearTimeout() {}});
    let scope='a', handler;
    c.setScope('encounter',scope);
    const begin=(operation,target='m') => c.begin({lane:'encounter',scope,operation,target,region:'monsters',placement:'pane',label:operation});
    class Input {constructor(id,value,valid=true,match=true) {Object.assign(this,{dataset:{mi:id},value,valid,match});} matches() {return this.match;} checkValidity() {return this.valid;}}
    const f={sent:[],loads:[],timers,request:async()=>({}),refresh:async()=>{},records:()=>c.snapshot(),
        error(operation,target,text) {c.publish(begin(operation,target),{severity:'error',text});},
        switch() {scope='b'; c.setScope('encounter',scope);},
        change(id='m',value='16',valid=true) {let stopped=false; const p=handler({target:new Input(id,value,valid),stopPropagation(){stopped=true;}}); a.equal(stopped,true); return p;},
        character() {return handler({target:new Input('c','21',true,false),stopPropagation(){a.fail('character intercepted');}})}
    };
    vm.runInNewContext(source,{window:{scryingAdminFeedback:{...c,begin:s=>begin(s.operation,s.target)}},
        document:{getElementById:()=>({querySelectorAll:()=>[],addEventListener:(_,fn)=>{handler=fn;}})},
        HTMLInputElement:Input,latest:null,monsterRow(){},paneNotification(){a.fail('legacy feedback');},
        request:(url,options)=>{f.sent.push({url,...options});return f.request();},load:x=>{f.loads.push(x);return f.refresh();}});
    return f;
}
test('persistent validation, independent targets and matching recovery',async()=>{
    const f=fixture(); f.error('monster.edit','m','edit'); f.error('monster.roll-all','m','all');
    await f.change('m','1.5'); await f.change('n','bad'); a.equal(f.sent.length,0); a.equal(f.records().length,4);
    await f.change('m','+16'); a.deepEqual(f.records().map(r=>r.target),['m','m','n']); a.equal(f.timers.length,0);
});
test('syntax, safe integer and native validity',async()=>{
    const f=fixture(); for(const v of ['1.5','1e2','0x10','NaN','Infinity','9007199254740992','+','--1']) await f.change('m',v);
    await f.change('m','16',false); a.equal(f.sent.length,0); a.equal(f.records().length,1); a.match(f.records()[0].text,/whole-number raw roll/);
});
test('null, signed values, encoded ID and raw-only PATCH',async()=>{
    const f=fixture(); for(const [v,n] of [['',null],['  ',null],['+16',16],['-50',-50],['0',0],['9007199254740991',9007199254740991],['-9007199254740991',-9007199254740991]]) {
        await f.change('a/b ?#',v); const s=f.sent.at(-1); a.equal(s.url,'/api/monsters/a%2Fb%20%3F%23/initiative-roll'); a.equal(s.method,'PATCH'); a.equal(s.headers['Content-Type'],'application/json'); a.deepEqual(JSON.parse(s.body),{initiative_roll:n});
    } a.deepEqual(f.loads,Array(7).fill(true)); a.equal(f.records().length,0);
});
test('persistent rejection and matching request recovery',async()=>{
    const f=fixture(); f.request=async()=>{throw new Error('rejected');}; await f.change('m'); await f.change('n');
    a.equal(f.loads.length,0); a.equal(f.records().length,2); a.equal(f.timers.length,0);
    f.request=async()=>({}); await f.change('m'); a.deepEqual(f.records().map(r=>[r.target,r.text]),[['n','rejected']]);
});
test('duplicate guard covers mutation and refresh, including replacement inputs',async()=>{
    const f=fixture(),m=wait(),r=wait(); f.request=()=>m.promise; f.refresh=()=>r.promise; const x=f.change();
    await f.change('m','17'); a.equal(f.sent.length,1); m.yes(); await tick(); a.equal(f.loads.length,1);
    await f.change('m','18'); a.equal(f.sent.length,1); r.yes(); await x;
    f.refresh=async()=>{}; await f.change(); a.equal(f.sent.length,2);
});
test('independent targets can submit concurrently',async()=>{
    const f=fixture(),d=wait(); f.request=()=>d.promise; const x=f.change('m'),y=f.change('n'); a.equal(f.sent.length,2);
    d.yes(); await Promise.all([x,y]); a.equal(f.loads.length,2);
});
for(const reject of [false,true]) for(const mode of ['encounter','request','refresh']) test(`${mode} stale completion reject=${reject}`,async()=>{
    const f=fixture(),d=wait(); if(mode==='refresh') f.refresh=()=>d.promise; else f.request=()=>d.promise;
    const x=f.change(); if(mode==='refresh') {await tick(); a.equal(f.loads.length,1);}
    if(mode!=='request') f.switch(); f.error(op(mode==='request'?'request':'refresh'),'m','new');
    if(reject) d.no(new Error('old')); else d.yes(); await x;
    a.equal(f.loads.length,mode==='refresh'?1:0); a.deepEqual(f.records().map(r=>r.text),['new']);
});
test('mutation success/refresh failure are separate, with no replay or success notice',async()=>{
    const f=fixture(); f.error(op('request'),'m','old'); f.refresh=async()=>{throw new Error('offline');}; await f.change();
    a.equal(f.sent.length,1); a.equal(f.records().length,1); a.equal(f.records()[0].operation,op('refresh'));
    a.match(f.records()[0].text,/Roll saved, but refresh failed: offline.*Reload before continuing/); a.equal(f.timers.length,0);
    f.refresh=async()=>{}; await f.change(); a.equal(f.sent.length,2); a.equal(f.records().length,0);
});
test('superseded refresh preserves newer error',async()=>{
    const f=fixture(),d=wait(); f.refresh=()=>d.promise; const x=f.change(); await tick(); a.equal(f.loads.length,1);
    f.error(op('refresh'),'m','new'); d.yes(); await x; a.deepEqual(f.records().map(r=>r.text),['new']);
});
test('old finally cannot unlock newer attempt',async()=>{
    const f=fixture(),old=wait(),next=wait(); f.request=()=>old.promise; const x=f.change(); f.switch(); f.request=()=>next.promise;
    const y=f.change(); old.yes(); await x; await f.change(); a.equal(f.sent.length,2); next.yes(); await y;
});
test('character events are untouched',async()=>{const f=fixture(); await f.character(); a.equal(f.sent.length,0); a.equal(f.records().length,0);});
