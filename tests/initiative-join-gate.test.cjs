const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../static/initiative-join-gate.js'), 'utf8');
function setup(item) {
    const button = {disabled: false, title: '', dataset: {}, getAttribute: () => item.id,
        removeAttribute(name) {delete this[name];}};
    let refresh;
    const ctx = {latest: {characters: [item], monsters: []}, document: {
        getElementById: () => ({}), querySelectorAll: selector => selector.includes('data-ca') ? [button] : []},
        MutationObserver: class {constructor(fn) {refresh = fn;} observe() {}}};
    vm.createContext(ctx);vm.runInContext(source, ctx);
    return {button, refresh, ctx};
}
test('missing initiative disables Join Battle with explanatory tooltip', () => {
    const w = setup({id: 'a', active: false, initiative: null});
    assert(w.button.disabled);assert.match(w.button.title, /Enter initiative/);
});
test('zero and negative initiatives enable joining', () => {
    for (const initiative of [0, -2, 12]) assert(!setup({id: 'a', active: false, initiative}).button.disabled);
});
test('active combatants can still leave when initiative is missing', () => {
    assert(!setup({id: 'a', active: true, initiative: null}).button.disabled);
});
test('server refresh reenables the button after initiative is entered', () => {
    const item = {id: 'a', active: false, initiative: null};const w = setup(item);
    item.initiative = 10;w.refresh();assert(!w.button.disabled);assert(!w.button.dataset.initiativeBlocked);
});
