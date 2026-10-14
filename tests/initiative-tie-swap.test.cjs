const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');
const source = fs.readFileSync(path.join(__dirname, '../static/admin.js'), 'utf8');
const start = source.indexOf('function swapTiePosition(');
const end = source.indexOf("document.querySelector('#tieGroups').addEventListener", start);
const sandbox = {};
vm.createContext(sandbox);
vm.runInContext(source.slice(start, end), sandbox);
function item(id, position, bucket = '0') {
    return {id, value: String(position), dataset: {tiePosition: String(position), tieBucket: bucket, tieMember: id}, matches: () => true};
}
function change(items, target, chosen) {
    target.value = String(chosen);
    sandbox.swapTiePosition({target, currentTarget: {querySelectorAll: () => items}});
}
function positions(items) { return items.map(x => Number(x.value)); }

test('M2 choosing 2 gives C2 its previous position 4', () => {
    const items = ['C1', 'C2', 'M1', 'M2', 'M3'].map((id, i) => item(id, i + 1));
    change(items, items[3], 2);
    assert.deepEqual(positions(items), [1, 4, 3, 2, 5]);
    assert.equal(items[1].dataset.tiePosition, '4');
    assert.equal(items[3].dataset.tiePosition, '2');
});
test('repeated swaps use updated previous positions', () => {
    const items = [item('C1', 1), item('C2', 2), item('M1', 3), item('M2', 4)];
    change(items, items[3], 2);
    change(items, items[1], 1);
    change(items, items[3], 4);
    assert.deepEqual(positions(items), [2, 1, 3, 4]);
    assert.equal(new Set(positions(items)).size, items.length);
});
test('swaps stay in the same initiative bucket', () => {
    const items = [item('A', 1), item('B', 2), item('X', 1, '1'), item('Y', 2, '1')];
    change(items, items[1], 1);
    assert.deepEqual(positions(items), [2, 1, 1, 2]);
});
test('unchanged value does not change another combatant', () => {
    const items = [item('A', 1), item('B', 2)];
    change(items, items[0], 1);
    assert.deepEqual(positions(items), [1, 2]);
});
test('unrelated change events are ignored', () => {
    sandbox.swapTiePosition({target: {matches: () => false}});
});
test('rendered selects initialize their tracked position', () => {
    const fn = source.slice(source.indexOf('function tieUI()'), start);
    const context = {latest: {characters: [{id: 'C'}]}, esc: String,
        tiedBuckets: () => [{initiative: 10, members: [{id: 'M', name: 'M'}, {id: 'C', name: 'C'}]}]};
    vm.createContext(context);
    vm.runInContext(fn + '; result = tieUI();', context);
    assert.match(context.result, /data-tie-member="C" data-tie-position="1"/);
    assert.match(context.result, /data-tie-member="M" data-tie-position="2"/);
});
