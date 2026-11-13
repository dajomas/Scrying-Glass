const {test} = require('node:test');
const assert = require('node:assert/strict');
const {createRefreshSelection} = require('../static/monster-refresh-selection.js');
const fixture = () => createRefreshSelection([
    {id:'a',offer:{initiative_bonus:12,ac:18,max_hp:'2d8+4',hp:'2d8+4'}},
    {id:'b',offer:{initiative_bonus:0,ac:null,max_hp:20,hp:20}},
    {id:'c',offer:{}}
]);
test('initially unchecked including current HP',()=>{
    const s=fixture();assert.deepEqual(s.payload(),{});
    assert.deepEqual(s.state('column','hp'),{disabled:false,checked:false,indeterminate:false});
});
test('column toggle skips unavailable cells',()=>{
    const s=fixture();s.toggle('column','ac');assert.deepEqual(s.payload(),{a:['ac']});
    s.toggle('column','ac');assert.deepEqual(s.payload(),{});
});
test('row toggle selects current HP explicitly and skips disabled',()=>{
    const s=fixture();s.toggle('row','b');
    assert.deepEqual(s.payload(),{b:['initiative_bonus','max_hp','hp']});
    s.toggle('row','b');assert.deepEqual(s.payload(),{});
});
test('individual deselection creates partial column and header fills remainder',()=>{
    const s=fixture();s.toggle('column','hp');s.set('a','hp',false);
    assert.equal(s.state('column','hp').indeterminate,true);
    s.toggle('column','hp');assert.equal(s.state('column','hp').checked,true);
});
test('partial row selects remainder then clears whole row',()=>{
    const s=fixture();s.set('a','ac',true);assert.equal(s.state('row','a').indeterminate,true);
    s.toggle('row','a');assert.equal(s.state('row','a').checked,true);
    s.toggle('row','a');assert.equal(s.state('row','a').checked,false);
});
test('empty row is disabled',()=>{
    const s=fixture();assert.equal(s.state('row','c').disabled,true);
    s.toggle('row','c');assert.deepEqual(s.payload(),{});
});
test('unavailable and unknown cells cannot be selected',()=>{
    const s=fixture();assert.throws(()=>s.set('b','ac',true));
    assert.throws(()=>s.set('other','hp',true));assert.throws(()=>s.set('a','hp','yes'));
    assert.throws(()=>s.toggle('column','name'));assert.throws(()=>s.toggle('row','other'));
});
test('payload is detached',()=>{
    const s=fixture();s.set('a','ac',true);const p=s.payload();p.a.push('hp');
    assert.deepEqual(s.payload(),{a:['ac']});
});
test('no mutation of supplied rows',()=>{
    const rows=[{id:'a',offer:{ac:0,hp:0}}], before=JSON.stringify(rows);
    const s=createRefreshSelection(rows);s.toggle('row','a');assert.equal(JSON.stringify(rows),before);
});
test('duplicate IDs rejected',()=>{
    assert.throws(()=>createRefreshSelection([{id:'a'},{id:'a'}]));
});
