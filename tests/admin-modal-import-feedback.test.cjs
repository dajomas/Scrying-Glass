const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'static/admin/040-source.js'), 'utf8');
const {createController} = require(path.join(root, 'static/admin-feedback-controller.js'));
function deferred() {
    let resolve, reject;
    const promise = new Promise((a,b) => {resolve=a; reject=b;});
    return {promise, resolve, reject};
}
const flush = async () => {await Promise.resolve(); await Promise.resolve();};
function harness() {
    let scope='a', timer=0;
    const timers=new Map(), calls=[], loads=[], confirmations=[];
    const controller=createController({setTimeout(fn,delay){const id=++timer; timers.set(id,{fn,delay}); return id;}, clearTimeout(id){timers.delete(id);}});
    controller.setScope('encounter',scope);
    const api={...controller, begin(spec){return controller.begin({...spec,lane:'encounter',scope,placement:'pane'});}};
    function form(values) {
        const events={};
        return {values,valid:true,resets:0,built:0,button:{disabled:false},
            addEventListener(name,fn){(events[name] ||= []).push(fn);},
            edit(name,value){this.values[name]=value; for(const fn of events.change || []) fn();},
            reportValidity(){return this.valid;}, querySelectorAll(){return [this.button];},
            reset(){this.resets++; this.values.csv_file=null; for(const fn of events.reset || []) fn();},
        };
    }
    const file={name:'original.csv'}, csv=form({csv_file:file});
    const setup=form({name:'Source',kind:'monsters',campaign:'',life_filter:'alive'});
    const passive={hidden:true,addEventListener(){}};
    const nodes={'#csvImportForm':csv,'#importForm':setup};
    const node=id => nodes[id] ||= {value:'',addEventListener(){}};
    const csvModal={hidden:true,addEventListener(){}}, modal={hidden:true,addEventListener(){}};
    const state={allow:true,hold:false,pending:[]};
    class FormData extends Map {constructor(f){super(Object.entries(f.values)); f.built++;}}
    const context=vm.createContext({window:{scryingAdminFeedback:api},FormData,
        document:{querySelector:node,addEventListener(){}},csvImportKind:null,
        csvImportModal:csvModal,importModal:modal,campaignData:{active:'campaign-a'},
        editModal:passive,monsterFileHelpModal:passive,campaignModal:passive,
        campaignSetupModal:passive,campaignDeleteModal:passive,
        closeImport(){modal.hidden=true;},closeCsvImport(){throw new Error('Obsolete CSV closer');},
        closeEdit(){},renderImportSetups(){},
        setups(){if(!state.hold)return Promise.resolve(); const p=deferred(); state.pending.push(p); return p.promise;},
        confirm(text){confirmations.push(text);return state.allow;},
        request(url,options){const p=deferred(); calls.push({url,options,...p}); return p.promise;},
        load(flag){const p=deferred(); loads.push({flag,...p}); return p.promise;},
    });
    vm.runInContext(source,context);
    const event=f => ({target:f,currentTarget:f,preventDefault(){}});
    return {csv,setup,file,csvModal,modal,calls,loads,state,timers,confirmations,
        openCsv(kind='characters'){node(kind==='characters'?'#openCharacterCsvImport':'#openMonsterCsvImport').onclick();},
        cancelCsv(){node('#cancelCsvImport').onclick();},
        openSetup(){return node('#openImport').onclick();}, cancelSetup(){node('#cancelImport').onclick();},
        submitCsv(){return csv.onsubmit(event(csv));}, submitSetup(){return setup.onsubmit(event(setup));},
        scope(){scope+='b';controller.setScope('encounter',scope);}, records:()=>controller.snapshot(),
    };
}
async function complete(h,p,result) {h.calls.at(-1).resolve(result); await flush(); h.loads.at(-1)?.resolve(); await p;}
test('CSV endpoints, file and dual success identities', async () => {
    for(const kind of ['characters','monsters']) {
        const h=harness(); h.openCsv(kind); const p=h.submitCsv();
        assert.equal(h.calls[0].url,`/api/${kind}/import-csv`);
        assert.equal(h.calls[0].options.body.get('csv_file'),h.file);
        await complete(h,p,{count:2});
        assert.deepEqual(h.records().map(r=>r.region),[kind==='characters'?'campaign':'battleSetup',kind]);
        assert.equal(h.records().every(r=>r.severity==='success'),true); assert.equal(h.csv.resets,1);
    }
});
test('setup payload, default filters and exact confirmation', async () => {
    for(const value of ['alive','dead','all','']) {
        const h=harness(); await h.openSetup(); h.setup.values.life_filter=value; const p=h.submitSetup();
        const filter=value || 'alive', label={alive:'Alive',dead:'Dead',all:'Alive and Dead'}[filter];
        assert.equal(h.confirmations[0],`Import ${label} monsters from Source into the current setup?`);
        assert.deepEqual(JSON.parse(h.calls[0].options.body),{name:'Source',kind:'monsters',campaign:'campaign-a',life_filter:filter});
        assert.equal(h.calls[0].url,'/api/setups/import'); await complete(h,p,{monsters:1,name:'Source'});
    }
});
test('validation and cancelled confirmation do not import', async () => {
    const h=harness(); await h.openSetup(); h.setup.values.life_filter='bad'; await h.submitSetup();
    assert.match(h.records()[0].text,/valid monster state/);
    h.setup.values.life_filter='alive'; h.setup.values.name=''; await h.submitSetup();
    assert.match(h.records()[0].text,/saved setup/); h.setup.values.name='Source'; h.state.allow=false;
    await h.submitSetup(); assert.equal(h.calls.length,0); assert.equal(h.modal.hidden,false);
    h.openCsv(); h.csv.valid=false; await h.submitCsv(); assert.equal(h.calls.length,0);
});
test('request failures preserve files and matching recovery preserves other kind error', async () => {
    const h=harness(); h.openCsv(); let p=h.submitCsv(); h.calls[0].reject(new Error('Characters failed')); await p;
    assert.equal(h.csv.values.csv_file,h.file); assert.equal(h.csv.resets,0); assert.equal(h.csvModal.hidden,false);
    h.openCsv('monsters'); p=h.submitCsv(); h.calls[1].reject(new Error('Monsters failed')); await p;
    assert.equal(h.records().length,2); h.openCsv(); p=h.submitCsv(); await complete(h,p,{count:1});
    assert.deepEqual(h.records().filter(r=>r.severity==='error').map(r=>r.text),['Monsters failed']);
});
test('duplicates blocked through refresh; disabled states restored', async () => {
    const h=harness(); h.openCsv(); const p=h.submitCsv(), duplicate=h.submitCsv();
    assert.equal(h.calls.length,1); await duplicate; assert.equal(h.csv.built,1);
    h.calls[0].resolve({count:1}); await flush(); h.openCsv();
    const during=h.submitCsv(); assert.equal(h.calls.length,1); await during; h.loads[0].resolve(); await p;
    assert.equal(h.csv.button.disabled,false); h.csv.button.disabled=true;
    const failure=h.submitCsv(); h.calls[1].reject(new Error('Rejected')); await failure;
    assert.equal(h.csv.button.disabled,true);
});
test('same-kind reopen suppresses old close/reset and refresh', async () => {
    const h=harness(); h.openCsv(); const p=h.submitCsv(); h.cancelCsv(); h.openCsv();
    const next={name:'next.csv'}; h.csv.edit('csv_file',next); const resets=h.csv.resets;
    h.calls[0].resolve({count:1}); await flush(); assert.equal(h.loads.length,0); await p;
    assert.equal(h.csvModal.hidden,false); assert.equal(h.csv.resets,resets); assert.equal(h.csv.values.csv_file,next);
});
test('setup reopen and encounter changes suppress obsolete results', async () => {
    const h=harness(); await h.openSetup(); let p=h.submitSetup(); h.cancelSetup(); await h.openSetup();
    h.calls[0].reject(new Error('Old rejection')); await p; assert.equal(h.records().length,0);
    p=h.submitSetup(); h.scope(); h.calls[1].resolve({monsters:1,name:'Old'}); await flush();
    assert.equal(h.loads.length,0); await p; assert.equal(h.modal.hidden,false);
});
test('new file selected during request is never discarded on success', async () => {
    const h=harness(); h.openCsv(); const p=h.submitCsv(), next={name:'next.csv'}; h.csv.edit('csv_file',next);
    await complete(h,p,{count:1}); assert.equal(h.csv.values.csv_file,next);
    assert.equal(h.csv.resets,0); assert.equal(h.csvModal.hidden,false); assert.equal(h.records().length,2);
});
test('refresh error persists after three-second successes without replay', async () => {
    const h=harness(); h.openCsv(); const p=h.submitCsv(); h.calls[0].resolve({count:1}); await flush();
    h.loads[0].reject(new Error('Offline')); await p; assert.equal(h.calls.length,1); assert.equal(h.loads[0].flag,true);
    assert.deepEqual(h.records().map(r=>r.severity),['success','success','error']);
    assert.match(h.records()[2].text,/do not import again/);
    for(const timer of [...h.timers.values()]) {assert.equal(timer.delay,3000); timer.fn();}
    assert.equal(h.records().length,1);
});
test('cancel or scope change during setup-list loading prevents obsolete open', async () => {
    for(const cancel of [true,false]) {
        const h=harness(); h.state.hold=true; const p=h.openSetup(); if(cancel) h.cancelSetup(); else h.scope();
        h.state.pending[0].resolve(); await p; assert.equal(h.modal.hidden,true);
    }
});
