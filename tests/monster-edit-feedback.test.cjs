/* Production controller with the complete effective handler; controlled DOM/transport. */
const {test}=require('node:test');
const a=require('node:assert/strict'), fs=require('node:fs'), vm=require('node:vm'), path=require('node:path');
const {createController}=require('../static/admin-feedback-controller.js');
const source=fs.readFileSync(path.join(__dirname,'../static/monster-initiative-edit.js'),'utf8');
const target=id=>JSON.stringify(['monsters',id]);
const tick=()=>new Promise(r=>setImmediate(r));
function hold(){let yes,no;const promise=new Promise((y,n)=>{yes=y;no=n;});return{promise,yes,no};}
function fixture(){
    const c=createController(),sent=[],loads=[],attrs=new Map();let scope='a';
    c.setScope('encounter',scope);
    const begin=(operation,id='m')=>c.begin({lane:'encounter',scope,operation,target:target(id),region:'monsters',placement:'pane',label:operation});
    const element=value=>({value,disabled:false,dataset:{assignedBonus:'12'}});
    const form={valid:true,elements:{name:element(' Dragon '),monster_species:element(' dragon '),initiative_bonus:element('10'),initiative:element('28')},
        controls:[{disabled:false},{disabled:true}],reportValidity(){return this.valid;},querySelectorAll(){return this.controls;},
        setAttribute(k,v){attrs.set(k,v);},removeAttribute(k){attrs.delete(k);},onsubmit:async()=>{f.delegated++;}};
    class File{constructor(name){this.name=name;}}
    class Data extends Map{constructor(){super(Object.entries(form.elements).map(([k,v])=>[k,v.value]));this.set('image',f.image);}}
    const f={delegated:0,closes:0,sent,loads,attrs,form,image:new File(''),request:async()=>({}),refresh:async()=>{},records:()=>c.snapshot(),
        scope(){scope='b';c.setScope('encounter',scope);},error(operation,id,text){c.publish(begin(operation,id),{severity:'error',text});},
        submit(){return form.onsubmit({preventDefault(){}});},open(id='m',kind='monsters'){ctx.openEdit(kind,id);},close(){ctx.closeEdit();}};
    const ctx=vm.createContext({document:{querySelector:()=>form},window:{scryingAdminFeedback:{...c,begin:s=>begin(s.operation,JSON.parse(s.target)[1])}},
        FormData:Data,File,monsterEdit(){return '';},editing:{kind:'monsters',id:'m'},editModal:{hidden:false},
        openEdit(kind,id){ctx.editing={kind,id};ctx.editModal.hidden=false;form.controls=[{disabled:false},{disabled:true}];},
        closeEdit(){f.closes++;ctx.editing=null;ctx.editModal.hidden=true;},
        request(url,options){sent.push({url,options});return f.request();},load(x){loads.push(x);return f.refresh();},
        paneNotification(){a.fail('legacy feedback');}});
    vm.runInContext(source,ctx);return f;
}
test('native invalidity has persistent matching validation recovery',async()=>{
    const f=fixture();f.form.valid=false;await f.submit();a.equal(f.sent.length,0);a.equal(f.records()[0].operation,'monster.edit.validation');
    f.form.valid=true;await f.submit();a.equal(f.records().length,0);
});
test('transport trims names, preserves bonus omission and image upload, and encodes IDs',async()=>{
    const f=fixture();f.open('a/b ?#');await f.submit();let s=f.sent.at(-1);
    a.equal(s.url,'/api/monsters/a%2Fb%20%3F%23/edit');a.equal(s.options.method,'POST');
    a.equal(s.options.body.get('name'),'Dragon');a.equal(s.options.body.get('monster_species'),'dragon');
    a.equal(s.options.body.get('initiative'),'28');a.equal(s.options.body.get('initiative_bonus'),'10');a.equal(s.options.body.has('image'),false);
    for(const value of ['','12']){f.open();f.form.elements.initiative_bonus.value=value;await f.submit();a.equal(f.sent.at(-1).options.body.has('initiative_bonus'),false);}
    f.open();f.image={};await f.submit();a.equal(f.sent.at(-1).options.body.has('image'),false);
});
test('request error persists, keeps draft/modal and restores prior disabled states',async()=>{
    const f=fixture();const controls=f.form.controls;f.request=async()=>{throw new Error('rejected');};await f.submit();
    a.equal(f.closes,0);a.equal(f.loads.length,0);a.equal(f.records()[0].text,'rejected');
    a.deepEqual(controls.map(x=>x.disabled),[false,true]);a.equal(f.attrs.has('aria-busy'),false);a.equal(f.form.elements.initiative_bonus.value,'10');
});
test('matching recovery preserves other targets and raw-roll errors; no success notice',async()=>{
    const f=fixture();f.error('monster.edit','m','old');f.error('monster.edit','n','other');f.error('monster.raw-roll.request','m','raw');
    await f.submit();a.deepEqual(f.records().map(r=>r.text),['other','raw']);a.equal(f.closes,1);a.deepEqual(f.loads,[true]);
});
test('duplicate prevention spans mutation and refresh even after reopening same target',async()=>{
    const f=fixture(),m=hold(),r=hold();f.request=()=>m.promise;f.refresh=()=>r.promise;const x=f.submit();
    await f.submit();a.equal(f.sent.length,1);m.yes();await tick();a.equal(f.loads.length,1);f.open();await f.submit();a.equal(f.sent.length,1);r.yes();await x;
});
for(const reject of [false,true])for(const mode of ['scope','session','superseded'])test(`obsolete mutation ${mode} reject=${reject}`,async()=>{
    const f=fixture(),d=hold();f.request=()=>d.promise;const x=f.submit();
    if(mode==='scope')f.scope();else if(mode==='session'){f.close();f.open();}else f.error('monster.edit','m','new');
    const closes=f.closes;if(reject)d.no(new Error('old'));else d.yes();await x;
    a.equal(f.closes,closes);a.equal(f.loads.length,0);a.equal(f.records().some(r=>r.text==='old'),false);
    if(mode==='superseded')a.deepEqual(f.records().map(r=>r.text),['new']);
});
test('saved mutation/failed refresh owns separate error and does not replay',async()=>{
    const f=fixture();f.error('monster.edit','m','old');f.refresh=async()=>{throw new Error('offline');};await f.submit();
    a.equal(f.sent.length,1);a.equal(f.records().length,1);a.equal(f.records()[0].operation,'monster.edit.refresh');
    a.match(f.records()[0].text,/Monster saved, but refresh failed: offline.*Reload before continuing/);
    f.open();f.refresh=async()=>{};await f.submit();a.equal(f.records().length,0);
});
test('reopen then close during refresh cannot receive old completion',async()=>{
    const f=fixture(),d=hold();f.refresh=()=>d.promise;const x=f.submit();await tick();f.open();f.close();
    d.no(new Error('old'));await x;a.equal(f.records().length,0);
});
test('old cleanup cannot clear newer busy state for an independent target',async()=>{
    const f=fixture(),old=hold(),next=hold();f.request=()=>old.promise;const x=f.submit();
    f.open('n');f.request=()=>next.promise;const y=f.submit();a.equal(f.sent.length,2);old.yes();await x;
    a.equal(f.attrs.get('aria-busy'),'true');next.yes();await y;a.equal(f.attrs.has('aria-busy'),false);
});
test('characters and absent sessions delegate unchanged',async()=>{
    const f=fixture();f.open('c','characters');await f.submit();f.close();await f.submit();a.equal(f.delegated,2);a.equal(f.sent.length,0);
});

test('scope and supersession during refresh cannot replace current feedback',async()=>{
    for(const change of ['scope','supersede']){
        const f=fixture(),d=hold();f.refresh=()=>d.promise;const x=f.submit();await tick();
        if(change==='scope')f.scope();f.error('monster.edit.refresh','m','new');d.no(new Error('old'));await x;
        a.deepEqual(f.records().map(r=>r.text),['new']);
    }
});
