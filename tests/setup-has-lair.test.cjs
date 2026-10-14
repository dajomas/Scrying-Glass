const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'static/setup-has-lair.js'), 'utf8');
function setup(initial) {
    const nodes = new Map();
    for (const id of ['setupHasLair', 'lairTools', 'toggleLairPane']) {
        nodes.set(id, {dataset: {}, checked: false, disabled: false, hidden: false,
            addEventListener(type, fn) {this[type] = fn;}});
    }
    const calls = [], errors = [];
    const ctx = {document: {getElementById: id => nodes.get(id)}, window: {}, latest: initial,
        request: async (url, options) => {calls.push([url, options]);},
        paneNotification: (kind, text) => errors.push(text)};
    ctx.load = async () => ctx.window.scryingLairsRender(ctx.latest);
    vm.createContext(ctx); vm.runInContext(source, ctx);
    return {ctx, nodes, calls, errors, box: nodes.get('setupHasLair')};
}
const state = enabled => ({has_lair: enabled, active_campaign_id: '1', active_setup: {campaign_id: '1', name: 'test'}});
test('unchecked gates pane and toggle without overwriting existing hidden preferences', () => {
    const w = setup(state(false));
    for (const id of ['lairTools', 'toggleLairPane']) {
        assert.equal(w.nodes.get(id).dataset.setupHasLair, 'false');
        assert.equal(w.nodes.get(id).hidden, false);
    }
    w.nodes.get('lairTools').hidden = true;
    w.ctx.window.scryingLairsRender(state(true));
    assert(w.box.checked);
    assert.equal(w.nodes.get('lairTools').dataset.setupHasLair, 'true');
    assert(w.nodes.get('lairTools').hidden);
});
test('setup switches synchronize checkbox and gate', () => {
    const w = setup(state(true));
    w.ctx.window.scryingLairsRender(state(false));
    assert(!w.box.checked);
    assert.equal(w.nodes.get('lairTools').dataset.setupHasLair, 'false');
});
test('checkbox sends scoped update and disables duplicate requests while pending', async () => {
    const w = setup(state(false));
    let release;
    w.ctx.request = (url, options) => {
        w.calls.push([url, options]);
        return new Promise(resolve => {release = resolve;});
    };
    w.box.checked = true;
    const promise = w.box.change();
    assert(w.box.disabled);
    assert.equal(w.nodes.get('lairTools').dataset.setupHasLair, 'true');
    assert.equal(w.calls[0][0], '/api/setups/has-lair');
    assert.equal(w.calls[0][1].method, 'PATCH');
    assert.deepEqual(JSON.parse(w.calls[0][1].body), {has_lair: true, scope: {campaign_id: '1', setup: {campaign_id: '1', name: 'test'}}});
    w.ctx.latest = state(true); release(); await promise;
    assert(!w.box.disabled); assert(w.box.checked);
});
test('failed update restores server state and shows error', async () => {
    const w = setup(state(false));
    w.ctx.request = async () => {throw new Error('Denied');};
    w.box.checked = true; await w.box.change();
    assert(!w.box.checked); assert(!w.box.disabled);
    assert.deepEqual(w.errors, ['Denied']);
});
test('checkbox precedes imports and follows setup-name input', () => {
    const html = fs.readFileSync(path.join(root, 'templates/admin/050_setup_input.html'), 'utf8');
    assert(html.indexOf('id="setupName"') < html.indexOf('id="setupHasLair"'));
    assert(html.indexOf('id="setupHasLair"') < html.indexOf('id="openImport"'));
    const css = fs.readFileSync(path.join(root, 'static/lairs.css'), 'utf8');
    assert.match(css, /#lairTools\[data-setup-has-lair="false"\]/);
    assert.match(css, /#toggleLairPane\[data-setup-has-lair="false"\]/);
    assert.match(css, /display: none !important/);
});
