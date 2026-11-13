// Stage 4: the superseded 030 setup-import handlers were removed; this check now
// drives the 040 owner (openSetupImport/submitSetupImport) that the Admin binds.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../static/admin/040-source.js'),'utf8');
const start=source.indexOf('async function openSetupImport()');
const end=source.indexOf("document.querySelector('#exportActivityLogCsv').onclick",start);
assert.ok(start>=0&&end>start,'Cannot isolate the setup-import owner');
assert.ok(!fs.readFileSync(path.join(__dirname,'../static/admin/030-source.js'),'utf8').includes("querySelector('#importForm').onsubmit ="),
    'The superseded 030 setup-import submit handler must not return');
const html=fs.readFileSync(path.join(__dirname,'../templates/admin/120_setup_import_modal.html'),'utf8');
assert.match(html,/<option value="alive" selected>Alive<\/option>/);
assert.match(html,/<option value="dead">Dead<\/option>/);
assert.match(html,/<option value="all">Alive and Dead<\/option>/);
const controls={};const calls=[];const prompts=[];
const ticket={region:'battleSetup'};
const ctx={document:{querySelector:id=>controls[id] ||= {value:''}},
    window:{scryingAdminFeedback:{begin:()=>ticket,publish(){},resolve(){},isCurrent:()=>true}},
    setupImportSession:null,
    setups:async()=>{},campaignData:{active:'campaign'},renderImportSetups(){},
    importModal:{hidden:true},closeImport(){},load:async()=>{},
    confirm:text=>{prompts.push(text);return true;},
    FormData:class {constructor(data){this.data=data;} get(key){return this.data[key]??null;}},
    // Minimal stand-in for the shared lifecycle: validate, confirm, send.
    async runModalImport(form,spec,session,getSession,modal,prepare){
        const prepared=prepare();if(prepared.error)throw new Error(prepared.error);
        if(prepared.confirmation&&!ctx.confirm(prepared.confirmation))return;return prepared.send();},
    request:async(url,options)=>{calls.push(JSON.parse(options.body));return {monsters:1,name:'source'};}};
vm.createContext(ctx);
vm.runInContext('let setupImportSession=null;'+source.slice(start,end),ctx);
(async()=>{
    controls['#importLifeFilter']={value:'dead'};
    await controls['#openImport'].onclick();
    assert.equal(controls['#importLifeFilter'].value,'alive');
    for(const filter of ['alive','dead','all']){
        const target={name:'source',kind:'monsters',life_filter:filter};
        await controls['#importForm'].onsubmit({preventDefault(){},target,currentTarget:target});
        assert.equal(calls.at(-1).life_filter,filter);
    }
    assert.match(prompts.at(-1),/Alive and Dead/);
    const target={name:'source',kind:'monsters'};
    await controls['#importForm'].onsubmit({preventDefault(){},target,currentTarget:target});
    assert.equal(calls.at(-1).life_filter,'alive');
    console.log('Setup import filter UI tests passed.');
})().catch(error=>{console.error(error);process.exitCode=1;});
