/* Complete 040 plus production controller; controlled DOM/transport and scope adapter. */
const {test}=require('node:test'), a=require('node:assert/strict');
const fs=require('node:fs'), path=require('node:path'), vm=require('node:vm');
const {createController}=require('../static/admin-feedback-controller.js');
const source=fs.readFileSync(path.join(__dirname,'../static/admin/040-source.js'),'utf8');
const tick=()=>new Promise(resolve=>setImmediate(resolve));
function hold(){let resolve,reject;const promise=new Promise((yes,no)=>{resolve=yes;reject=no;});return{promise,resolve,reject};}
function fixture(){
    let scope='a',now=0,next=0;const timers=new Map(),nodes=new Map(),calls=[],loads=[],confirmations=[];
    const controller=createController({setTimeout(fn,delay){const id=++next;timers.set(id,{at:now+delay,fn});return id;},clearTimeout(id){timers.delete(id);}});
    controller.setScope('encounter',scope);
    const feedback={...controller,begin(spec){return controller.begin({...spec,lane:'encounter',scope,placement:'pane'});}};
    const node=()=>({disabled:false,hidden:true,value:'',addEventListener(){},focus(){}});
    const doc={querySelector(id){if(!nodes.has(id))nodes.set(id,node());return nodes.get(id);},addEventListener(){}};
    const h={calls,loads,confirmations,confirm:true,send:async()=>({count:2}),refresh:async()=>{},
        records:()=>controller.snapshot(),error(operation,text,target='all-monsters'){feedback.publish(feedback.begin({region:'monsters',operation,target,label:operation}),{severity:'error',text});},
        scope(value){scope=value;controller.setScope('encounter',scope);},
        advance(ms){now+=ms;for(const [id,timer]of [...timers])if(timer.at<=now){timers.delete(id);timer.fn();}}};
    const context=vm.createContext({window:{scryingAdminFeedback:feedback},document:doc,
        latest:{monsters:[{id:'m'},{id:'n'}],characters:[{id:'c',initiative:21}]},
        csvImportModal:node(),editModal:node(),importModal:node(),monsterFileHelpModal:node(),
        campaignModal:node(),campaignSetupModal:node(),campaignDeleteModal:node(),
        closeImport(){},renderImportSetups(){},
        confirm(text){confirmations.push(text);return h.confirm;},
        request(url,options){calls.push({url,options});return h.send();},load(flag){loads.push(flag);return h.refresh();},
        paneNotification(){a.fail('roll-all must not use compatibility feedback');}});
    vm.runInContext(source,context);h.context=context;h.button=doc.querySelector('#rollMonsterInitiative');
    h.run=()=>h.button.onclick();return h;
}
test('empty roster is deduplicated info; no confirmation, mutation or unrelated clearing',async()=>{
    const h=fixture();h.context.latest.monsters=[];h.error('monster.raw-roll.request','keep','m');
    await h.run();await h.run();a.equal(h.records().length,2);a.equal(h.records()[1].severity,'info');
    a.equal(h.confirmations.length,0);a.equal(h.calls.length,0);
});
test('cancellation preserves errors and does not mutate or refresh',async()=>{
    const h=fixture();h.confirm=false;h.error('monster.roll-all.request','keep');await h.run();
    a.equal(h.records()[0].text,'keep');a.equal(h.calls.length,0);a.equal(h.loads.length,0);
});
test('bodyless POST and original confirmation/count text; success precedes strict refresh',async()=>{
    const h=fixture(),d=hold();h.refresh=()=>d.promise;const before=JSON.stringify(h.context.latest);const pending=h.run();await tick();
    a.equal(h.confirmations[0],'Overwrite initiative for all 2 monster(s) with a random d20 roll?');
    a.equal(h.calls[0].url,'/api/monsters/roll-initiative');a.deepEqual(Object.keys(h.calls[0].options),['method']);a.equal(h.calls[0].options.method,'POST');
    a.deepEqual(h.loads,[true]);a.equal(h.records()[0].text,'Rolled d20 initiative for 2 monster(s)');
    a.equal(h.records()[0].severity,'success');a.equal(JSON.stringify(h.context.latest),before);
    d.resolve();await pending;h.advance(2999);a.equal(h.records().length,1);h.advance(1);a.equal(h.records().length,0);
});
test('request errors persist beyond success timeout and restore the button',async()=>{
    const h=fixture();h.send=async()=>{throw new Error('rejected');};await h.run();h.advance(60000);
    a.equal(h.records()[0].text,'rejected');a.equal(h.records()[0].severity,'error');a.equal(h.loads.length,0);a.equal(h.button.disabled,false);
});
test('matching retry preserves raw-roll, Edit, Join and other-target errors',async()=>{
    const h=fixture();h.error('monster.roll-all.request','old');
    for(const op of ['monster.raw-roll.request','monster.edit','roster.join'])h.error(op,op,'m');
    h.error('monster.roll-all.request','other','different-target');await h.run();
    a.equal(h.records().some(x=>x.text==='old'),false);a.equal(h.records().filter(x=>x.severity==='error').length,4);
});
test('duplicates stay blocked throughout mutation and refresh; explicit later attempt works',async()=>{
    const h=fixture(),m=hold(),r=hold();h.send=()=>m.promise;h.refresh=()=>r.promise;const pending=h.run();
    await h.run();a.equal(h.calls.length,1);a.equal(h.button.disabled,true);m.resolve({count:2});await tick();
    await h.run();a.equal(h.calls.length,1);a.equal(h.confirmations.length,1);a.equal(h.button.disabled,true);
    r.resolve();await pending;a.equal(h.button.disabled,false);h.send=async()=>({count:1});h.refresh=async()=>{};await h.run();a.equal(h.calls.length,2);
});
for(const reject of [false,true])for(const mode of ['scope','superseded'])test(`obsolete mutation ${mode} reject=${reject}`,async()=>{
    const h=fixture(),d=hold();h.send=()=>d.promise;const pending=h.run();
    if(mode==='scope'){h.scope('b');h.scope('a');}h.error('monster.roll-all.request','new');
    if(reject)d.reject(new Error('old'));else d.resolve({count:99});await pending;
    a.deepEqual(h.records().map(x=>x.text),['new']);a.equal(h.loads.length,0);a.equal(h.button.disabled,false);
});
test('refresh error is separate persistent no-replay guidance; later successful refresh resolves it',async()=>{
    const h=fixture();h.refresh=async()=>{throw new Error('offline');};await h.run();
    a.equal(h.calls.length,1);a.deepEqual(h.records().map(x=>x.severity),['success','error']);
    a.equal(h.records()[1].operation,'monster.roll-all.refresh');a.match(h.records()[1].text,/do not roll again/);
    h.advance(60000);a.equal(h.records().length,1);h.refresh=async()=>{};await h.run();a.equal(h.records().some(x=>x.severity==='error'),false);
});
for(const reject of [false,true])test(`scope change during refresh reject=${reject}`,async()=>{
    const h=fixture(),d=hold();h.refresh=()=>d.promise;const pending=h.run();await tick();h.scope('b');h.error('fixture.current','new');
    if(reject)d.reject(new Error('old'));else d.resolve();await pending;a.deepEqual(h.records().map(x=>x.text),['new']);a.equal(h.calls.length,1);
});
test('superseded refresh cannot resolve or replace the newer refresh error',async()=>{
    for(const reject of [false,true]){const h=fixture(),d=hold();h.refresh=()=>d.promise;const pending=h.run();await tick();
        h.error('monster.roll-all.refresh','new');if(reject)d.reject(new Error('old'));else d.resolve();await pending;
        a.equal(h.records().filter(x=>x.severity==='error')[0].text,'new');}
});
test('button restores its pre-existing disabled state',async()=>{
    const h=fixture();h.button.disabled=true;await h.run();a.equal(h.button.disabled,true);
});
