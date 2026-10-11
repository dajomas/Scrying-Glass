const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
let source = fs.readFileSync(path.join(__dirname, '../static/battle-turn-actions.js'), 'utf8');
source = source.replace("if (document.readyState === 'loading') {", "globalThis.testExports = {buildTurnActions, reorderCriticalFields}; if (document.readyState === 'loading') {");
const context = {document: {readyState: 'loading', addEventListener() {}}};
vm.runInNewContext(source, context);
const {buildTurnActions, reorderCriticalFields} = context.testExports;
const build = (...args) => JSON.parse(JSON.stringify(buildTurnActions(...args)));
assert.deepEqual(build('actor', '', ''), []);
assert.deepEqual(build('actor', '0', '0'), []);
assert.deepEqual(build('actor', '12', '7'), [
    {target_id: 'actor', action: 'damage', amount: 12, critical_hit: false},
    {target_id: 'actor', action: 'heal', amount: 7, critical_hit: false},
]);
assert.equal(build('actor', '', '99999')[0].action, 'heal');
for (const value of ['-1', '1.5', '100000', 'NaN', 'Infinity']) {
    assert.throws(() => build('actor', value, ''));
    assert.throws(() => build('actor', '', value));
}
const parent = {};
const field = {parentNode: parent, nextElementSibling: null};
let moves = 0;
const amount = {parentNode: parent, before(value) {assert.equal(value, field); moves++; field.nextElementSibling = amount;}};
const checkbox = {closest() {return field;}};
const row = {querySelector(selector) {return selector === '.amount-field' ? amount : checkbox;}};
const rows = {querySelectorAll() {return [row];}};
reorderCriticalFields(rows);
reorderCriticalFields(rows);
assert.equal(moves, 1);
reorderCriticalFields({querySelectorAll() {return [{querySelector() {return null;}}];}});
console.log('Payload validation and critical-field reorder tests passed.');
