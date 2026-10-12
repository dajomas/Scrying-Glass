const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../static/admin.js'),'utf8');
const start=source.indexOf("document.querySelector('#openImport').onclick");
const end=source.indexOf('function closeCsvImport()',start);
const html=fs.readFileSync(path.join(__dirname,'../templates/admin/120_setup_import_modal.html'),'utf8');
assert.match(html,/<option value="alive" selected>Alive<\/option>/);
assert.match(html,/<option value="dead">Dead<\/option>/);
assert.match(html,/<option value="all">Alive and Dead<\/option>/);
const controls={};const calls=[];const prompts=[];
const ctx={document:{querySelector:id=>controls[id] ||= {value:''}},
    setups:async()=>{},campaignData:{active:'campaign'},renderImportSetups(){},
    importModal:{hidden:true},closeImport(){},load:async()=>{},paneNotification(){},
    confirm:text=>{prompts.push(text);return true;},
    FormData:class {constructor(data){this.data=data;} get(key){return this.data[key]??null;}},
    request:async(url,options)=>{calls.push(JSON.parse(options.body));return {monsters:1,name:'source'};}};
vm.runInNewContext(source.slice(start,end),ctx);
(async()=>{
    controls['#importLifeFilter']={value:'dead'};
    await controls['#openImport'].onclick();
    assert.equal(controls['#importLifeFilter'].value,'alive');
    for(const filter of ['alive','dead','all']){
        await controls['#importForm'].onsubmit({preventDefault(){},target:{name:'source',kind:'monsters',life_filter:filter}});
        assert.equal(calls.at(-1).life_filter,filter);
    }
    assert.match(prompts.at(-1),/Alive and Dead/);
    await controls['#importForm'].onsubmit({preventDefault(){},target:{name:'source',kind:'monsters'}});
    assert.equal(calls.at(-1).life_filter,'alive');
    console.log('Setup import filter UI tests passed.');
})().catch(error=>{console.error(error);process.exitCode=1;});
