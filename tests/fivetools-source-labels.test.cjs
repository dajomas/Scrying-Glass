'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {createController} = require('../static/admin-feedback-controller.js');
const bootstrap = fs.readFileSync(path.join(__dirname,'../static/admin-feedback-admin.js'),'utf8');
const prefix = fs.readFileSync(path.join(__dirname,'../static/admin/010-source.js'),'utf8').split('function setColorPreview')[0];
const names = {MM:'Monster Manuals 2014',XMM:'Monster Manuals 2024',PHB:'Player Handbook 2014',XPHB:'Player Handbook 2024',DMG:'Dungeon Master Guide 2014',XDMG:'Dungeon Master Guide 2024'};
function fixture() {
    const fields = {monsterSpecies:{value:'Goblin'},monsterAc:{value:''},monsterHpRangeStart:{value:''},monsterHpRangeEnd:{value:''},monsterSpeciesLookupOverwrite:{checked:false},monsterAddNotification:{textContent:''}};
    const messages = [], timers = new Map();
    let now = 0, timerId = 0;
    const controller = createController({
        setTimeout(fn, delay) {const id = ++timerId;timers.set(id, {fn, at:now + delay});return id;},
        clearTimeout(id) {timers.delete(id);},
    });
    // This VM exercises feedback records, not DOM rendering; no view roots are mounted.
    const context = vm.createContext({document:{querySelector:s=>fields[s.slice(1)],getElementById:()=>null},
        ScryingFeedback:{createController:()=>controller},clearTimeout,setTimeout,console,messages});
    context.window = context;
    vm.runInContext(bootstrap, context);
    vm.runInContext(prefix + '\n' + `const paneNotification=(kind,text,options)=>{
        const accepted=window.scryingAdminFeedback.deliver(kind,text,options);
        if(accepted) messages.push(text);
        return accepted;
    };`, context);
    return {fields,messages,context,advance(milliseconds) {
        now += milliseconds;
        for(const [id,timer] of [...timers]) if(timer.at <= now) {timers.delete(id);timer.fn();}
    }};
}

test('six exact labels retain immutable raw source identity',()=>{
    const {context:c}=fixture();
    for(const [source,name] of Object.entries(names)) {
        const value=Object.freeze({provider:'5e.tools',source,selection_token:'keep',source_url:'https://example.test/'+source});
        assert.equal(c.monsterSourceLabel(value),'5e.tools ('+name+')');
        assert.equal(c.monsterSourceLabel(value,true),'5e.tools / '+name);
        assert.equal(value.source,source);assert.equal(value.selection_token,'keep');
        assert.equal(value.source_url,'https://example.test/'+source);
    }
});
test('custom codes and D&D Beyond wording remain intact',()=>{
    const {context:c}=fixture();
    for(const source of ['CUSTOM','mm','XPBH','__proto__','constructor','<img src=x>']) {
        assert.equal(c.monsterSourceLabel({provider:'5e.tools',source,legacy:true}),'5e.tools ('+source+')');
    }
    assert.equal(c.monsterSourceLabel({provider:'5e.tools'}),'5e.tools (unknown source)');
    for(const legacy of [true,false]) assert.equal(c.monsterSourceLabel({provider:'D&D Beyond',legacy}),(legacy?'legacy':'current')+' D&D Beyond');
});
test('actual lookup notifications and overwrite/edit guards',async()=>{
    for(const [source,name] of Object.entries(names)) {
        const {fields:f,messages:m,context:c}=fixture();
        c.request=async()=>Object.freeze({found:true,provider:'5e.tools',source,ac:12,hp:'7'});
        await c.lookupMonsterSpeciesStats();
        assert.equal(f.monsterAc.value,'12');assert.equal(f.monsterHpRangeStart.value,'7');
        assert.ok(m.at(-1).includes(name));
        f.monsterAc.value='19';f.monsterHpRangeStart.value='20';
        await c.lookupMonsterSpeciesStats();
        assert.equal(f.monsterAc.value,'19');assert.equal(f.monsterHpRangeStart.value,'20');
        f.monsterSpeciesLookupOverwrite.checked=true;
        c.request=async()=>{f.monsterAc.value='99';return {found:true,provider:'5e.tools',source,ac:12,hp:'7'};};
        await c.lookupMonsterSpeciesStats();
        assert.equal(f.monsterAc.value,'99');assert.equal(f.monsterHpRangeStart.value,'7');
    }
});
test('lookup success metadata and clearing preserve unrelated feedback',async()=>{
    const {context:c}=fixture(), a=c.scryingAdminFeedback;
    const ticket=a.begin({region:'monsters',operation:'fixture.edit',target:'other',label:'Edit'});
    a.deliver('monsters','Unrelated edit failed',{ticket,severity:'error'});
    c.request=async()=>({found:true,provider:'5e.tools',source:'MM',ac:12,hp:'7'});
    await c.lookupMonsterSpeciesStats();
    const lookup=a.snapshot().find(record=>record.operation==='monster.lookup');
    assert.equal(lookup.severity,'success');assert.equal(lookup.region,'monsters');
    assert.ok(lookup.text.includes(names.MM));
    c.setMonsterSpeciesLookupStatus('');
    assert.deepEqual(a.snapshot().map(record=>record.operation),['fixture.edit']);
});
test('lookup request failure uses persistent error feedback',async()=>{
    const {fields:f,context:c,advance}=fixture();
    c.request=async()=>{throw new Error('Fixture provider unavailable');};
    await c.lookupMonsterSpeciesStats();advance(10000);
    const records=c.scryingAdminFeedback.snapshot();
    assert.equal(records.length,1);assert.equal(records[0].operation,'monster.lookup');
    assert.equal(records[0].severity,'error');assert.ok(records[0].text.includes('unavailable'));
    assert.equal(f.monsterAc.value,'');assert.equal(f.monsterHpRangeStart.value,'');
});
test('old lookup result cannot overwrite the newer inputs or feedback',async()=>{
    const {fields:f,messages:m,context:c}=fixture();let release;
    c.request=()=>new Promise(resolve=>{release=resolve;});
    const first=c.lookupMonsterSpeciesStats();
    c.request=async()=>({found:true,provider:'5e.tools',source:'PHB',ac:16,hp:'9'});
    await c.lookupMonsterSpeciesStats();
    release({found:true,provider:'5e.tools',source:'MM',ac:99,hp:'99'});await first;
    assert.equal(f.monsterAc.value,'16');assert.equal(f.monsterHpRangeStart.value,'9');
    assert.ok(m.at(-1).includes(names.PHB));
    const records=c.scryingAdminFeedback.snapshot();
    assert.equal(records.length,1);assert.equal(records[0].severity,'success');
    assert.ok(records[0].text.includes(names.PHB));
});
