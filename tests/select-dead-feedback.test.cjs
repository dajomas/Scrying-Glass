/* Effective selection asset with production controller and a scoped adapter; no native DOM. */
const {test}=require('node:test'), a=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const {createController}=require('../static/admin-feedback-controller.js');
const source=fs.readFileSync(path.join(__dirname,'../static/bulk-select-all.js'),'utf8');
function fixture(){
    let scope='a',now=0,serial=0;const timers=new Map(),history=[],sets={characters:new Set(['old']),monsters:new Set(['old'])};
    const c=createController({setTimeout(fn,delay){const id=++serial;timers.set(id,{at:now+delay,fn});history.push(fn);return id;},clearTimeout(id){timers.delete(id);}});
    c.setScope('encounter',scope);
    const feedback={...c,begin:spec=>c.begin({...spec,lane:'encounter',scope,placement:'pane'})};
    const latest={characters:[{id:'same',life_state:'dead'},{id:'alive',life_state:'standing'}],
        monsters:[{id:'same',alive:false},{id:'alive',alive:true}]};
    const boxes=Object.fromEntries(Object.entries(latest).map(([kind,items])=>[kind,items.map(item=>({dataset:{selectId:item.id},checked:false}))]));
    const delegated=[];const h={sets,boxes,history,delegated,onClear(){},records:()=>c.snapshot(),
        scope(value){scope=value;c.setScope('encounter',value);},
        advance(ms){now+=ms;for(const [id,t]of [...timers])if(t.at<=now){timers.delete(id);t.fn();}},
        error(kind,operation,text,target=kind){feedback.publish(feedback.begin({region:kind,operation,target,label:'Fixture'}),{severity:'error',text});}};
    const forbidden=()=>a.fail('select-dead must stay local, without transport/refresh/legacy feedback');
    const ctx=vm.createContext({latest,window:{scryingAdminFeedback:feedback},
        document:{getElementById(){return null;},querySelectorAll(s){if(s==='button[data-select-all-kind]')return [];return s.includes('"characters"')?boxes.characters:boxes.monsters;}},
        setAllSelected(kind,value){a.equal(value,false);sets[kind].clear();h.onClear();},
        updateRowSelection(kind,id,value){a.equal(value,true);sets[kind].add(id);},
        runBulkAction(...args){delegated.push({self:this,args});return 'original-result';},
        request:forbidden,fetch:forbidden,load:forbidden,paneNotification:forbidden});
    vm.runInContext(source,ctx);h.context=ctx;h.run=kind=>ctx.runBulkAction(kind,'select-dead');return h;
}
test('explicit pane success uses separate roster identities even with equal combatant IDs',async()=>{
    const h=fixture();await h.run('characters');await h.run('monsters');
    a.deepEqual(h.records().map(x=>[x.operation,x.target,x.region,x.severity,x.text]),[
        ['roster.select-dead','characters','characters','success','Selected 1 dead character.'],
        ['roster.select-dead','monsters','monsters','success','Selected 1 dead monster.']]);
});
test('selection and checkboxes stay local; encounter data and other roster are untouched',async()=>{
    const h=fixture(),before=JSON.stringify(h.context.latest);await h.run('monsters');
    a.deepEqual([...h.sets.monsters],['same']);a.deepEqual([...h.sets.characters],['old']);
    a.deepEqual(h.boxes.monsters.map(x=>x.checked),[true,false]);a.equal(JSON.stringify(h.context.latest),before);
});
test('success expires exactly at three seconds',async()=>{
    const h=fixture();await h.run('characters');h.advance(2999);a.equal(h.records().length,1);h.advance(1);a.equal(h.records().length,0);
});
test('selection success and expiry preserve unrelated actionable errors',async()=>{
    const h=fixture();for(const op of ['roster.join','monster.roll-all.request','monster.raw-roll.request','monster.edit'])h.error('monsters',op,op,'same');
    await h.run('monsters');h.advance(3000);a.equal(h.records().length,4);a.equal(h.records().every(x=>x.severity==='error'),true);
});
test('matching successful selection replaces only its own prior error',async()=>{
    const h=fixture();h.error('characters','roster.select-dead','old');h.error('monsters','roster.select-dead','other');await h.run('characters');
    a.deepEqual(h.records().map(x=>x.text),['other','Selected 1 dead character.']);
});
test('repeated selection replaces its own notice and obsolete timer cannot clear the replacement',async()=>{
    const h=fixture();await h.run('characters');const old=h.history[0];await h.run('characters');
    a.equal(h.records().length,1);old();a.equal(h.records().length,1);h.advance(3000);a.equal(h.records().length,0);
});
test('zero results still clear the selection and report the unchanged zero-count wording',async()=>{
    const h=fixture();h.context.latest.monsters=[];await h.run('monsters');a.equal(h.sets.monsters.size,0);
    a.equal(h.records()[0].text,'Selected 0 dead monsters.');a.equal(h.records()[0].severity,'success');
});
test('permanent-death and deduplication rules remain unchanged',async()=>{
    const h=fixture();h.context.latest.characters=[{id:'same',life_state:'dead'},{id:'same',death_failures:3},
        {id:'down',life_state:'down',alive:false},{id:'stable',life_state:'stable',alive:false}];
    await h.run('characters');a.deepEqual([...h.sets.characters],['same']);a.equal(h.records()[0].text,'Selected 1 dead character.');
});
test('invalid kind or unavailable roster remains a silent no-op',async()=>{
    const h=fixture();h.error('monsters','roster.join','keep');await h.run('invalid');h.context.latest=null;await h.run('monsters');
    h.context.latest={monsters:{}};await h.run('monsters');a.deepEqual([...h.sets.monsters],['old']);a.deepEqual(h.records().map(x=>x.text),['keep']);
});
test('non-selection actions preserve original receiver, arguments and return',async()=>{
    const h=fixture(),owner={};a.equal(await h.context.runBulkAction.call(owner,'monsters','remove','extra'),'original-result');
    a.equal(h.delegated[0].self,owner);a.deepEqual(h.delegated[0].args,['monsters','remove','extra']);a.equal(h.records().length,0);
});
test('scope invalidation before publishing cannot attach a stale notice to the new encounter',async()=>{
    const h=fixture();h.onClear=()=>{h.scope('b');h.error('monsters','fixture.current','keep');};await h.run('monsters');
    a.deepEqual(h.records().map(x=>x.text),['keep']);
});
test('versioned asset loads once after core and before roster presentation',()=>{
    const html=fs.readFileSync(path.join(__dirname,'../templates/admin/190_document_end.html'),'utf8');
    const marker='/static/bulk-select-all.js?v=2';a.equal(html.split(marker).length-1,1);
    a.ok(html.indexOf('/static/admin.js')<html.indexOf(marker));a.ok(html.indexOf(marker)<html.indexOf('/static/admin-rosters.js'));
});
