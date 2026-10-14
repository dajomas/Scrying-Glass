const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../static/initiative-join-gate.js'), 'utf8');
function setup(item = {id: 'a', name: 'Alpha', active: false, initiative: null}, kind = 'characters', response) {
    const attribute = kind === 'characters' ? 'data-ca' : 'data-ma';
    const button = {disabled: false, title: '', dataset: {}, attributes: {},
        hasAttribute: name => name === attribute, getAttribute: () => item.id,
        setAttribute(name, value) {this.attributes[name] = value;},
        removeAttribute(name) {delete this.attributes[name];if (name === 'title') delete this.title;}};
    const message = {textContent: ''};let refresh, click;
    const nativeFetch = async () => response || new Response('{}', {status: 200});
    const ctx = {URL, latest: {characters: [], monsters: []}, window: {
        fetch: nativeFetch, location: {href: 'http://localhost/', origin: 'http://localhost'}}, document: {
        getElementById: id => id === 'message' ? message : {}, querySelectorAll: () => [button],
        addEventListener(type, fn, capture) {assert.equal(type, 'click');assert.equal(capture, true);click = fn;}},
        MutationObserver: class {constructor(fn) {refresh = fn;} observe() {}}};
    ctx.latest[kind] = [item];vm.createContext(ctx);vm.runInContext(source, ctx);
    return {button, message, refresh, ctx, click() {
        const event = {target: {closest: () => button}, prevented: false, stopped: false,
            preventDefault() {this.prevented = true;}, stopImmediatePropagation() {this.stopped = true;}};
        click(event);return event;
    }};
}
for (const kind of ['characters', 'monsters']) test(`${kind}: blocked click reports the name and prevents join handler`, () => {
    const w = setup(undefined, kind);assert(!w.button.disabled);
    assert.equal(w.button.attributes['aria-disabled'], 'true');
    const event = w.click();assert(event.prevented && event.stopped);
    assert.equal(w.message.textContent, 'Enter initiative before joining battle: Alpha');
});
test('numeric initiative permits joining, including zero and negatives', () => {
    for (const initiative of [0, -2, 12]) {
        const w = setup({id: 'a', active: false, initiative});
        assert(!w.click().stopped);assert.equal(w.message.textContent, '');
    }
});
test('leaving remains allowed without initiative', () => {
    assert(!setup({id: 'a', active: true, initiative: null}).click().stopped);
});
test('saved-state refresh removes blocked metadata', () => {
    const item = {id: 'a', active: false, initiative: null};const w = setup(item);
    item.initiative = 10;w.refresh();assert(!w.button.dataset.initiativeBlocked);
    assert(!w.button.attributes['aria-disabled']);
});
test('bulk server rejection reaches message without consuming response', async () => {
    const detail = 'Enter initiative before joining battle: Beta';
    const w = setup(undefined, 'characters', new Response(JSON.stringify({detail}), {status: 400}));
    const result = await w.ctx.window.fetch('/api/characters/bulk', {method: 'POST', body: JSON.stringify({action: 'join-battle', ids: ['a']})});
    assert.equal(w.message.textContent, detail);assert.deepEqual(await result.json(), {detail});
});
test('single join server rejection also reaches message', async () => {
    const w = setup(undefined, 'monsters', new Response(JSON.stringify({detail: 'Not authorized'}), {status: 403}));
    await w.ctx.window.fetch('/api/monsters/a', {method: 'PATCH', body: JSON.stringify({active: true})});
    assert.equal(w.message.textContent, 'Not authorized');
});
test('non-JSON rejection uses HTTP fallback', async () => {
    const w = setup(undefined, 'monsters', new Response('Oops', {status: 500}));
    await w.ctx.window.fetch('/api/monsters/bulk', {method: 'POST', body: JSON.stringify({action: 'join-battle'})});
    assert.equal(w.message.textContent, 'Join Battle rejected (HTTP 500).');
});
test('unrelated rejection does not change global message', async () => {
    const w = setup(undefined, 'characters', new Response('{}', {status: 400}));
    await w.ctx.window.fetch('/api/characters/a', {method: 'PATCH', body: JSON.stringify({hp: 2})});
    assert.equal(w.message.textContent, '');
});
test('successful join does not create rejection message', async () => {
    const w = setup();await w.ctx.window.fetch('/api/characters/a', {method: 'PATCH', body: JSON.stringify({active: true})});
    assert.equal(w.message.textContent, '');
});
