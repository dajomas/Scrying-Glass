const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
let source = fs.readFileSync(path.join(__dirname, '../static/battle-turn-actions.js'), 'utf8');
source = source.replace("if (document.readyState === 'loading')", "globalThis.exportsForTest = {buildTurnActions, reorderCriticalFields}; if (document.readyState === 'loading')");
const context = {document: {readyState: 'loading', addEventListener() {}}};
vm.runInNewContext(source, context);
const {buildTurnActions, reorderCriticalFields} = context.exportsForTest;
const build = (...args) => JSON.parse(JSON.stringify(buildTurnActions(...args)));
assert.deepEqual(build('a', '', '0'), []);
assert.deepEqual(build('a', '5', '3').map(x => x.action), ['damage', 'heal']);
for (const value of ['-1', '1.5', '100000', 'NaN', 'Infinity'])
    assert.throws(() => build('a', value, ''));
const parent = {};
let moves = 0;
const amount = {parentNode: parent, contains() {return false;},
    before(f) { moves++; f.nextElementSibling = amount; }};
const field = {parentNode: parent, contains() {return false;}, nextElementSibling: null};
const rowsFor = (a, f) => ({querySelectorAll() {return [{querySelector(s) {
    return s === '.amount-field' ? a : {closest() {return f;}};
}}];}});
reorderCriticalFields(rowsFor(amount, field));
reorderCriticalFields(rowsFor(amount, field));
assert.equal(moves, 1);
reorderCriticalFields(rowsFor(amount, amount));
assert.equal(moves, 1);
field.contains = () => true;
reorderCriticalFields(rowsFor(amount, field));
assert.equal(moves, 1);
assert.match(source, /rowObserver\.disconnect\(\);[\s\S]*try \{ reorderCriticalFields\(rows\); \}[\s\S]*finally \{ rowObserver\.observe\(rows, options\); \}/);
console.log('Validation, ordering, self/nested-move guards and observer isolation checks passed.');
