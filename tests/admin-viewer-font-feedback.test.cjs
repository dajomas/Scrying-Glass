// Full 080 + production controls helper; real controller, scoped test adapter, mocked DOM/network.
'use strict';
const test=require('node:test'), assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const {createController}=require(path.join(root,'static/admin-feedback-controller.js'));
const core=read('static/admin/070-source.js');
const offset=core.indexOf('function updateBattleOrderFontControls(fontSize) {');
assert.ok(offset>=0);
const helper=core.slice(offset), source=read('static/admin/080-source.js');
const spec={region:'global',operation:'display.battle-order-font',target:'battle-order',label:'Change viewer font size'};
function deferred(){let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};}
function fixture(size=16){
    let scope='a/one';const nodes=new Map(),calls=[],timers=new Map(),previews=[];let serial=0,loads=0,setups=0;
    const controller=createController({setTimeout(fn,ms){timers.set(++serial,{fn,ms});return serial;},clearTimeout(id){timers.delete(id);}});
    controller.setScope('encounter',scope);
    const feedback={begin(s){return controller.begin({...s,lane:'encounter',scope,placement:'global'});},
        publish:controller.publish,resolve:controller.resolve,isCurrent:controller.isCurrent};
    const f={calls,timers,nodes,previews,onRequest:async()=>({battle_order_font_size:18}),feedback};
    const context=vm.createContext({Error,latest:{display:{battle_order_font_size:size}},battleOrderFontAdjustmentPending:false,
        window:{scryingAdminFeedback:feedback},document:{querySelector(id){if(!nodes.has(id))nodes.set(id,{disabled:false,textContent:'',listeners:{},addEventListener(type,fn){this.listeners[type]=fn;}});return nodes.get(id);}},
        request:async(...args)=>{calls.push(args);return f.onRequest(...args);},
        message(){throw new Error('Font must not use legacy feedback');},
        installColorPreview(...args){previews.push(args);},load(){loads++;},setups(){setups++;}});
    vm.runInContext(helper,context);vm.runInContext(source,context);
    Object.assign(f,{context,controller,snapshot:()=>controller.snapshot(),pending:()=>context.battleOrderFontAdjustmentPending,
        display:()=>context.latest?.display,
        control:id=>nodes.get('#battleOrderFont'+id),run:direction=>context.adjustBattleOrderFont(direction),
        render:()=>context.updateBattleOrderFontControls(context.latest?.display?.battle_order_font_size),
        scope(value='b/two',font=24){scope=value;controller.setScope('encounter',scope);context.latest={display:{battle_order_font_size:font}};},
        seed(text='old',operation=spec.operation,target=spec.target){controller.publish(feedback.begin({...spec,operation,target}),{severity:'error',text});},
        boot:()=>({loads,setups})});
    return f;
}
test('POST preserves endpoint, JSON direction and header; success is silent',async()=>{
    const f=fixture();await f.run('increase');const [url,options]=f.calls[0];
    assert.equal(url,'/api/display/battle-order-font');assert.equal(options.method,'POST');
    assert.equal(options.headers['Content-Type'],'application/json');assert.deepEqual(JSON.parse(options.body),{direction:'increase'});
    assert.equal(f.display().battle_order_font_size,18);assert.equal(f.control('Size').textContent,'18 px');
    assert.equal(f.snapshot().length,0);assert.equal(f.timers.size,0);assert.equal(f.calls.length,1);
});
test('pending blocks both directions and disables both controls until completion',async()=>{
    const f=fixture(),p=deferred();f.onRequest=()=>p.promise;const first=f.run('increase');
    assert.equal(f.pending(),true);assert.equal(f.control('Decrease').disabled,true);assert.equal(f.control('Increase').disabled,true);
    await f.run('decrease');assert.equal(f.calls.length,1);p.resolve({battle_order_font_size:18});await first;
    assert.equal(f.pending(),false);assert.equal(f.control('Decrease').disabled,false);assert.equal(f.control('Increase').disabled,false);
});
test('request failure persists with own identity and restores controls without replay',async()=>{
    const f=fixture();f.onRequest=async()=>{throw new Error('denied');};await f.run('increase');
    assert.equal(f.snapshot()[0].severity,'error');assert.equal(f.snapshot()[0].text,'denied');assert.equal(f.snapshot()[0].operation,spec.operation);
    assert.equal(f.snapshot()[0].target,spec.target);assert.equal(f.timers.size,0);assert.equal(f.pending(),false);
    assert.equal(f.control('Size').textContent,'16 px');assert.equal(f.control('Increase').disabled,false);assert.equal(f.calls.length,1);
});
test('non-Error rejection retains existing fallback wording',async()=>{
    const f=fixture();f.onRequest=async()=>{throw 'offline';};await f.run('increase');
    assert.equal(f.snapshot()[0].text,'Unable to change viewer font size.');assert.equal(f.snapshot()[0].severity,'error');
});
test('opposite-direction successful retry resolves only related error',async()=>{
    const f=fixture();f.seed('other','activity-log.clear','activity-log');f.onRequest=async()=>{throw new Error('denied');};await f.run('increase');
    f.onRequest=async()=>({battle_order_font_size:14});await f.run('decrease');
    assert.equal(f.snapshot().length,1);assert.equal(f.snapshot()[0].text,'other');assert.equal(f.display().battle_order_font_size,14);
    assert.equal(JSON.parse(f.calls[1][1].body).direction,'decrease');
});
test('unrelated success and control rerender do not resolve font failure',()=>{
    const f=fixture();f.seed();f.render();f.controller.publish(f.feedback.begin({...spec,operation:'activity-log.clear'}),{severity:'success',text:'ok'});
    assert.equal(f.snapshot().find(x=>x.operation===spec.operation).text,'old');
});
test('minimum and maximum retain boundary disabling after success',async()=>{
    const f=fixture();for(const value of [12,40]){f.onRequest=async()=>({battle_order_font_size:value});await f.run('increase');
        assert.equal(f.control('Decrease').disabled,value===12);assert.equal(f.control('Increase').disabled,value===40);
        assert.equal(f.control('Size').textContent,value+' px');assert.equal(f.pending(),false);}
});
test('boundary disabling is retained after request failure',async()=>{
    for(const size of [12,40]){const f=fixture(size);f.onRequest=async()=>{throw new Error('no');};await f.run('increase');
        assert.equal(f.control('Decrease').disabled,size===12);assert.equal(f.control('Increase').disabled,size===40);}
});
test('control helper retains clamp and invalid-value default',()=>{
    const f=fixture();for(const [value,want] of [[0,12],[100,40],[15.5,16],['bad',16]]){
        f.context.updateBattleOrderFontControls(value);assert.equal(f.control('Size').textContent,want+' px');}
});
test('old-scope success cannot alter latest display, resolve current error or render old value',async()=>{
    const f=fixture(),p=deferred();f.onRequest=()=>p.promise;const old=f.run('increase');f.scope();f.seed('new');
    p.resolve({battle_order_font_size:18});await old;assert.equal(f.display().battle_order_font_size,24);
    assert.equal(f.control('Size').textContent,'24 px');assert.equal(f.snapshot()[0].text,'new');assert.equal(f.pending(),false);
});
test('old-scope error cannot overwrite current feedback; pending cleanup still runs',async()=>{
    const f=fixture(),p=deferred();f.onRequest=()=>p.promise;const old=f.run('increase');f.scope();f.seed('new');
    p.reject(new Error('old'));await old;assert.equal(f.snapshot()[0].text,'new');assert.equal(f.control('Size').textContent,'24 px');assert.equal(f.pending(),false);
});
test('away-and-back scope cannot revive original response',async()=>{
    const f=fixture(),p=deferred();f.onRequest=()=>p.promise;const old=f.run('increase');f.scope();f.scope('a/one',30);
    p.resolve({battle_order_font_size:18});await old;assert.equal(f.display().battle_order_font_size,30);assert.equal(f.snapshot().length,0);
});
test('newer same-operation ticket suppresses older completion without bypassing lock',async()=>{
    const f=fixture(),p=deferred();f.onRequest=()=>p.promise;const old=f.run('increase');f.seed('new');
    await f.run('decrease');p.resolve({battle_order_font_size:18});await old;
    assert.equal(f.calls.length,1);assert.equal(f.snapshot()[0].text,'new');assert.equal(f.display().battle_order_font_size,16);
});
test('confirmed request resolves its error even if subsequent control update throws',async()=>{
    const f=fixture();f.seed();const real=f.context.updateBattleOrderFontControls;let calls=0;
    f.context.updateBattleOrderFontControls=value=>{if(++calls===2)throw new Error('UI failure');return real(value);};
    await assert.rejects(f.run('increase'),/UI failure/);assert.equal(f.snapshot().length,0);assert.equal(f.pending(),false);assert.equal(f.calls.length,1);
});
test('initial control rendering failure still releases pending and does not send POST',async()=>{
    const f=fixture();const real=f.context.updateBattleOrderFontControls;let calls=0;
    f.context.updateBattleOrderFontControls=value=>{if(++calls===1)throw new Error('render');return real(value);};
    await assert.rejects(f.run('increase'),/render/);assert.equal(f.pending(),false);assert.equal(f.calls.length,0);assert.equal(f.snapshot().length,0);
});
test('missing latest display retains no-assignment path and default final controls',async()=>{
    const f=fixture();f.context.latest={};await f.run('increase');assert.equal(f.display(),undefined);
    assert.equal(f.control('Size').textContent,'16 px');assert.equal(f.pending(),false);
});
test('both original click listeners retain directions',async()=>{
    const f=fixture();f.control('Decrease').listeners.click();await new Promise(resolve=>setImmediate(resolve));
    f.control('Increase').listeners.click();await new Promise(resolve=>setImmediate(resolve));
    assert.deepEqual(f.calls.map(x=>JSON.parse(x[1].body).direction),['decrease','increase']);
});
test('full fragment retains color-preview and startup wiring with no extra refresh',async()=>{
    const f=fixture();assert.equal(f.previews.length,4);assert.deepEqual(f.boot(),{loads:1,setups:1});
    await f.run('increase');assert.deepEqual(f.boot(),{loads:1,setups:1});
});
