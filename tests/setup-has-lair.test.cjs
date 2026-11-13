const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');
const {installFeedback} = require('./battle-action-feedback-fixture.cjs');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'static/setup-has-lair.js'), 'utf8');
function setup(initial) {
    const nodes = new Map();
    for (const id of ['setupHasLair', 'lairTools', 'toggleLairPane']) {
        nodes.set(id, {dataset: {}, checked: false, disabled: false, hidden: false,
            addEventListener(type, fn) {this[type] = fn;}});
    }
    const calls = [], legacy = [];
    const ctx = {document: {}, window: {}, latest: initial,
        request: async (url, options) => {calls.push([url, options]);},
        // Stage 3 retires this caller's untyped pane notification; any call is a regression.
        paneNotification: (kind, text) => legacy.push([kind, text])};
    ctx.load = async () => ctx.window.scryingLairsRender(ctx.latest);
    const {feedback, scope} = installFeedback(ctx);
    ctx.document.getElementById = id => nodes.get(id);
    vm.runInContext(source, ctx);
    const records = () => feedback.snapshot().filter(r => r.operation === 'setup.has-lair');
    return {ctx, nodes, calls, legacy, feedback, scope, records, box: nodes.get('setupHasLair')};
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
    assert.deepEqual(w.records().map(r => [r.region, r.severity, r.text, r.target]),
        [['battleSetup', 'error', 'Denied', JSON.stringify(['1', {campaign_id: '1', name: 'test'}])]]);
    assert.deepEqual(w.legacy, []);
});
test('error persists until the next successful update for the setup resolves it', async () => {
    const w = setup(state(false));
    w.ctx.request = async () => {throw new Error('Denied');};
    w.box.checked = true; await w.box.change();
    assert.equal(w.records().length, 1);
    w.ctx.request = async () => {}; w.ctx.latest = state(true);
    w.box.checked = true; await w.box.change();
    assert.equal(w.records().length, 0); assert(w.box.checked); assert.deepEqual(w.legacy, []);
});
test('success publishes no message and a declined duplicate starts no feedback', async () => {
    const w = setup(state(false));
    let release;
    w.ctx.request = () => new Promise(resolve => {release = resolve;});
    w.box.checked = true; const pending = w.box.change(); await w.box.change();
    w.ctx.latest = state(true); release(); await pending;
    assert.equal(w.feedback.snapshot().length, 0);
});
test('setup switch clears the encounter-lane error and stale completion cannot publish', async () => {
    const w = setup(state(false));
    let reject;
    w.ctx.request = () => new Promise((resolve, fail) => {reject = fail;});
    w.box.checked = true; const pending = w.box.change();
    w.scope('1', 'other'); reject(new Error('Late denial')); await pending;
    assert.equal(w.records().length, 0);
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
