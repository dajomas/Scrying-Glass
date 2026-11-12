// Full features script with real feedback controller/bootstrap; DOM and HTTP are mocked.
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const test=require('node:test');
const vm=require('node:vm');
const {installFeedback}=require('./battle-action-feedback-fixture.cjs');
const code=fs.readFileSync(path.join(__dirname,'../static/features.js'),'utf8');
const flush=()=>new Promise(resolve=>setImmediate(resolve));
async function setup(options={}) {
    const elements=new Map(),timers=new Map();let now=0,sequence=0;
    class Element {
        constructor(){this.dataset={};this.value='';this.files=[];this.listeners={};}
        addEventListener(name,fn){this.listeners[name]=fn;}
        replaceChildren(...children){this.children=children;}
        append(...children){this.children=children;}
    }
    const element=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id);};
    class FormData {constructor(){this.entries=[];}append(...entry){this.entries.push(entry);}}
    const state={active_campaign_id:'fixture',active_setup:{campaign_id:'fixture',name:'setup'},characters:[],monsters:[],lairs:[]};
    const summary={checkpoints:[],displays:[],downed:[],undo:null};
    const h={calls:[],alerts:[],allow:true,hold:false,failPost:false,failSetups:false,failLoad:false,failRefresh:false,name:'Imported campaign',setups:0,loads:0};
    let poll;
    const context={window:{},document:{getElementById:element,createElement:()=>new Element(),activeElement:null},
        FormData,Option:function(name,id){this.text=name;this.value=String(id);},
        confirm:()=>h.allow,alert:text=>h.alerts.push(text),location:{},
        setInterval:fn=>{poll=fn;},
        setups:async()=>{h.setups++;if(h.failSetups)throw new Error('Setup list failed');},
        load:async()=>{h.loads++;if(h.failLoad)throw new Error('Core refresh failed');},
        fetch:async(url,request)=>{
            h.calls.push({url,request});
            if(request.method==='POST') {
                if(h.hold)await new Promise(resolve=>{h.release=resolve;});
                if(h.failPost)return {ok:false,status:422,json:async()=>({detail:'Import rejected'})};
                return {ok:true,json:async()=>({name:h.name})};
            }
            if(h.failRefresh)throw new Error('Feature refresh failed');
            return {ok:true,json:async()=>url==='/api/state'?state:summary};
        }};
    const {feedback,scope}=installFeedback(context,{
        setTimeout(fn,delay){const id=++sequence;timers.set(id,{fn,deadline:now+delay});return id;},
        clearTimeout(id){timers.delete(id);},
    });
    context.document.getElementById=element;
    vm.runInContext(code,context,{filename:'static/features.js'});await flush();
    Object.assign(h,options);
    const file={name:'campaign.zip'};element('importBundle').files=[file];element('importBundle').value='selected';
    return Object.assign(h,{element,file,feedback,scope,
        run:()=>element('importBundle').onchange(),
        writes:()=>h.calls.filter(call=>call.request.method==='POST'),
        records:()=>feedback.snapshot().filter(record=>record.operation==='campaign-bundle.import'),
        tick(ms){now+=ms;for(const [id,item]of [...timers])if(item.deadline<=now){timers.delete(id);item.fn();}},
        poll:async()=>{poll();await flush();},
    });
}
const guidance=name=>`Imported ${name}. Switch campaigns, then restore the "Imported encounter" checkpoint to resume its runtime state.`;
test('confirmed import keeps file POST and full recovery wording, without alert',async()=>{
    const h=await setup({name:'<Campaign & name>'});await h.run();
    assert.equal(h.writes().length,1);const {url,request}=h.writes()[0];
    assert.equal(url,'/api/campaign-bundle');assert.equal(request.cache,'no-store');
    assert.equal(request.headers,undefined);assert.equal(request.body.entries.length,1);
    assert.equal(request.body.entries[0][0],'file');assert.equal(request.body.entries[0][1],h.file);
    assert.equal(h.records().length,1);assert.equal(h.records()[0].severity,'success');
    assert.equal(h.records()[0].text,guidance(h.name));assert.deepEqual(h.alerts,[]);
    assert.equal(h.setups,1);assert.equal(h.loads,1);assert.equal(h.element('importBundle').value,'');
    assert.deepEqual(Array.from(h.feedback.legacyRegions()),[]);
});
test('success expires at five seconds without clearing unrelated persistent error',async()=>{
    const h=await setup();const ticket=h.feedback.begin({region:'global',operation:'battle.end',target:'battle',label:'End'});
    h.feedback.publish(ticket,{severity:'error',text:'Independent error'});await h.run();
    h.tick(4999);assert.equal(h.records().length,1);h.tick(1);assert.equal(h.records().length,0);
    assert.deepEqual(h.feedback.snapshot().map(record=>record.text),['Independent error']);
});
for(const missing of [false,true])test(missing?'missing file does not start import feedback':'cancellation does not start import feedback',async()=>{
    const h=await setup();if(missing)h.element('importBundle').files=[];else h.allow=false;
    await h.run();assert.equal(h.writes().length,0);assert.equal(h.records().length,0);
    // Stage 3: cancellation is silent; the legacy 'Cancelled.' notice is retired.
    assert.equal(h.element('importBundle').value,'selected');assert.equal(h.element('featureNotice').textContent,undefined);
    assert.equal(h.feedback.snapshot().length,0);
});
test('busy duplicate is suppressed and release permits only an explicit later import',async()=>{
    const h=await setup({hold:true});const pending=h.run();await flush();await h.run();
    assert.equal(h.writes().length,1);assert.equal(h.records().length,0);
    h.release();await pending;h.hold=false;await h.run();assert.equal(h.writes().length,2);
    assert.equal(h.records().length,1);assert.equal(h.records()[0].text,guidance(h.name));
});
test('rejected POST remains local and is not retried or announced as success',async()=>{
    const h=await setup({failPost:true});await h.run();await h.poll();
    assert.equal(h.writes().length,1);assert.equal(h.setups,0);
    // Stage 3: the rejection is a persistent tools-region error keyed like the import, never a success.
    assert.deepEqual(h.records().map(r=>[r.region,r.severity,r.text]),[['tools','error','Import rejected']]);
    h.tick(60000);assert.equal(h.records().length,1);
    assert.equal(h.element('featureNotice').textContent,undefined);assert.equal(h.element('importBundle').value,'selected');
});
for(const awayBack of [false,true])test(awayBack?'away-and-back epoch suppresses stale import success':'scope transition suppresses stale import success',async()=>{
    const h=await setup({hold:true});const pending=h.run();await flush();h.scope('other','elsewhere');
    if(awayBack)h.scope();h.release();await pending;
    assert.equal(h.records().length,0);assert.equal(h.writes().length,1);assert.deepEqual(h.alerts,[]);
});
for(const [flag,message]of [['failSetups','Setup list failed'],['failLoad','Core refresh failed'],['failRefresh','Feature refresh failed']])test(flag+' does not recast confirmed import or replay POST',async()=>{
    const h=await setup({[flag]:true});await h.run();
    assert.equal(h.writes().length,1);assert.equal(h.records().length,1);
    assert.equal(h.records()[0].severity,'success');assert.equal(h.records()[0].text,guidance(h.name));
    const again=h.feedback.snapshot().filter(r=>r.operation==='campaign-bundle.import.refresh');
    assert.equal(again.length,1);assert.equal(again[0].region,'tools');assert.equal(again[0].severity,'error');
    assert.match(again[0].text,new RegExp(`^Import campaign bundle completed, but refreshing the view failed: ${message}\\. Reload the page`));
    h.tick(60000);assert.equal(h.feedback.snapshot().filter(r=>r.operation==='campaign-bundle.import.refresh').length,1);
});
test('a later successful import resolves the earlier rejection',async()=>{
    const h=await setup({failPost:true});await h.run();h.failPost=false;await h.run();
    assert.deepEqual(h.records().map(r=>[r.region,r.severity]),[['global','success']]);
});
test('same-scope feature refresh preserves an unsaved field during import',async()=>{
    const h=await setup({hold:true});const pending=h.run();await flush();
    const input=h.element('featureTempHp');input.value='new draft';input.listeners.input();h.release();await pending;
    assert.equal(input.value,'new draft');assert.equal(input.dataset.dirty,'1');assert.equal(h.writes().length,1);
});
