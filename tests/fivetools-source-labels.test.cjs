'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const prefix = fs.readFileSync(path.join(__dirname,'../static/admin/010-source.js'),'utf8').split('function setColorPreview')[0];
const names = {MM:'Monster Manuals 2014',XMM:'Monster Manuals 2024',PHB:'Player Handbook 2014',XPHB:'Player Handbook 2024',DMG:'Dungeon Master Guide 2014',XDMG:'Dungeon Master Guide 2024'};
function fixture() {
    const fields = {monsterSpecies:{value:'Goblin'},monsterAc:{value:''},monsterHpRangeStart:{value:''},monsterHpRangeEnd:{value:''},monsterSpeciesLookupOverwrite:{checked:false},monsterAddNotification:{textContent:''}};
    const messages = [];
    const context = vm.createContext({document:{querySelector:s=>fields[s.slice(1)]},clearTimeout,setTimeout,console,messages});
    vm.runInContext(prefix+'\nconst paneNotificationTimeouts={monsters:null};const paneNotification=(kind,text)=>messages.push(text);',context);
    return {fields,messages,context};
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
