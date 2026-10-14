const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');
const source = fs.readFileSync(path.join(__dirname, '../static/admin.js'), 'utf8');
const fn = source.slice(source.indexOf('function tieUI()'), source.indexOf('function readTieOrder()'));
function defaults(ids, characterIds) {
    const members = ids.map(id => ({id, name: id}));
    const sandbox = {latest: {characters: characterIds.map(id => ({id}))},
        tiedBuckets: () => [{initiative: 12, members}], esc: String};
    vm.createContext(sandbox);
    vm.runInContext(fn + '; result = tieUI();', sandbox);
    assert.deepEqual(members.map(m => m.id), ids);
    return [...sandbox.result.matchAll(/data-tie-member="([^"]+)">([\s\S]*?)<\/select>/g)]
        .map(m => [m[1], Number(m[2].match(/value="(\d+)" selected/)[1])]);
}
test('mixed ties default to characters first with stable within-kind order', () => {
    assert.deepEqual(defaults(['m2', 'c2', 'm1', 'c1'], ['c1', 'c2']),
        [['c2', 1], ['c1', 2], ['m2', 3], ['m1', 4]]);
});
test('monster-only ties retain order', () => {
    assert.deepEqual(defaults(['m2', 'm1'], []), [['m2', 1], ['m1', 2]]);
});
test('character-only ties retain order', () => {
    assert.deepEqual(defaults(['c2', 'c1'], ['c1', 'c2']), [['c2', 1], ['c1', 2]]);
});
