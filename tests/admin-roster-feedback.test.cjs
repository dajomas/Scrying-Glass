// Complete 010 fragment and production feedback bootstrap; mocked DOM/transport, not full Admin acceptance.
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');
const {createController} = require('../static/admin-feedback-controller.js');
const read = name => fs.readFileSync(path.join(__dirname, '../static', name), 'utf8');
const source = read('admin/010-source.js');
const bootstrap = read('admin-feedback-admin.js');
const gate = read('initiative-join-gate.js');
const clean = value => JSON.parse(JSON.stringify(value));
const ok = () => new Response('{"count":2}');
function deferred() {
    let resolve, reject;
    const promise = new Promise((a, b) => {resolve = a; reject = b;});
    return {promise, resolve, reject};
}
function setup(withJoin = false) {
    let sequence = 0, controller;
    const timers = new Map();
    const h = {calls: [], loads: [], prompts: [], accepted: true,
        send: async () => ok(), refresh: async () => {}};
    const ctx = {URL, console, window: {location: {origin: 'http://fixture', href: 'http://fixture/'}},
        document: {readyState: 'complete', getElementById: () => null, querySelector: () => null,
            querySelectorAll: () => [], addEventListener() {}},
        fixtureState: Object.fromEntries(['characters', 'monsters'].map(kind => [kind,
            [{id: 'a', name: 'Alpha'}, {id: 'b', name: 'Beta'}]])),
        ScryingFeedback: {createController() {
            controller = createController({setTimeout(fn, ms) {timers.set(++sequence, {fn, ms});return sequence;},
                clearTimeout(id) {timers.delete(id);}});
            return controller;
        }},
        confirm(text) {h.prompts.push(text);return h.accepted;},
        load: async rethrow => {h.loads.push(rethrow);return h.refresh();}};
    ctx.window.fetch = async (url, options) => {
        h.calls.push({url, options, body: JSON.parse(options.body)});
        return h.send(url, options);
    };
    ctx.fetch = (...args) => ctx.window.fetch(...args);
    vm.createContext(ctx);
    vm.runInContext(bootstrap, ctx);
    vm.runInContext(source, ctx);
    vm.runInContext('latest = fixtureState;', ctx);
    h.ctx = ctx; h.feedback = ctx.window.scryingAdminFeedback; h.timers = timers;
    h.records = () => h.feedback.snapshot();
    h.ids = ids => {
        for (const kind of ['characters', 'monsters']) {
            ctx.setAllSelected(kind, false);
            for (const id of ids) ctx.updateRowSelection(kind, id, true);
        }
    };
    h.ids(['b', 'a']);
    h.scope = value => h.feedback.setScope('encounter', value);
    if (withJoin) vm.runInContext(gate, ctx);
    return h;
}

test('persistent independent patch errors do not acquire expiry', async () => {
    const h = setup();h.send = async () => {throw Error('Rejected');};
    await h.ctx.patch('characters', 'a', {hp: 1});await h.ctx.patch('characters', 'b', {hp: 2});
    assert.equal(h.records().length, 2);assert.equal(h.timers.size, 0);
    assert(h.records().every(r => r.severity === 'error' && r.placement === 'pane'));
    assert.equal(h.loads.length, 0);assert.deepEqual(clean(h.feedback.legacyRegions()), []);
});
test('matching retry preserves its error until success and retains another target', async () => {
    const h = setup();h.send = async () => {throw Error('Rejected');};
    await h.ctx.patch('characters', 'a', {hp: 1});await h.ctx.patch('characters', 'b', {hp: 2});
    const hold = deferred();h.send = () => hold.promise;
    const pending = h.ctx.patch('characters', 'a', {hp: 3});assert.equal(h.records().length, 2);
    hold.resolve(ok());await pending;
    assert.equal(h.records().length, 1);assert.match(h.records()[0].target, /b/);assert.deepEqual(h.loads, [true]);
});
test('empty selection publishes persistent local validation without a request', async () => {
    const h = setup();h.ids([]);await h.ctx.runBulkAction('monsters', 'remove');
    assert.equal(h.calls.length, 0);assert.equal(h.prompts.length, 0);
    assert.equal(h.records()[0].operation, 'roster.bulk.remove.selection');
    assert.equal(h.records()[0].severity, 'error');assert.equal(h.records()[0].text, 'Select one or more monsters first.');
});
test('selection-only actions preserve real selection sets without new feedback', async () => {
    const h = setup();h.ids([]);await h.ctx.runBulkAction('monsters', 'select-all');
    assert.deepEqual(clean(h.ctx.selectedIds('monsters')), ['a', 'b']);
    await h.ctx.runBulkAction('monsters', 'unselect-all');assert.deepEqual(clean(h.ctx.selectedIds('monsters')), []);
    assert.equal(h.records().length, 0);assert.equal(h.calls.length, 0);
});
test('cancelled bulk removal preserves feedback and named confirmation', async () => {
    const h = setup();h.ids([]);await h.ctx.runBulkAction('monsters', 'remove');
    const record = h.records()[0];h.ids(['a', 'b']);h.accepted = false;
    await h.ctx.runBulkAction('monsters', 'remove');
    assert.equal(h.records()[0], record);assert.equal(h.calls.length, 0);
    assert.equal(h.prompts[0], 'Remove 2 selected monsters from the current battle setup?\n\nAlpha, Beta');
});
test('bulk payload keeps selection order while feedback uses canonical targets', async () => {
    const h = setup();await h.ctx.runBulkAction('monsters', 'remove');
    assert.deepEqual(h.calls[0].body, {action: 'remove', ids: ['b', 'a']});
    assert.equal(JSON.parse(h.records()[0].target)[1], '["a","b"]');
    assert.equal(h.records()[0].text, '2 monsters updated.');
    assert([...h.timers.values()].every(t => t.ms === 3000));
});
test('individual removal preserves payload, destination, name and success', async () => {
    const h = setup();await h.ctx.removeCombatant('characters', 'a');
    assert.deepEqual(h.calls[0].body, {action: 'remove', ids: ['a']});
    assert.equal(h.prompts[0], 'Remove character “Alpha” from the active campaign?');
    assert.equal(h.records()[0].text, 'Character “Alpha” removed.');
});
test('stale success cannot refresh a new encounter', async () => {
    const h = setup(), hold = deferred();h.send = () => hold.promise;
    const pending = h.ctx.patch('characters', 'a', {hp: 1});h.scope('new');hold.resolve(ok());await pending;
    assert.equal(h.loads.length, 0);assert.equal(h.records().length, 0);
});
test('stale failure cannot publish to a new encounter', async () => {
    const h = setup(), hold = deferred();h.send = () => hold.promise;
    const pending = h.ctx.patch('characters', 'a', {hp: 1});h.scope('new');hold.reject(Error('Old'));await pending;
    assert.equal(h.loads.length, 0);assert.equal(h.records().length, 0);
});
test('bulk refresh failure stays separate from success and does not replay', async () => {
    const h = setup();h.refresh = async () => {throw Error('Refresh failed');};
    await h.ctx.runBulkAction('monsters', 'heal');assert.equal(h.calls.length, 1);
    assert.deepEqual(h.records().map(r => r.severity), ['success', 'error']);
    assert.equal(h.records()[1].operation, 'roster.bulk.heal.refresh');assert.match(h.records()[1].text, /do not repeat/);
    for (const timer of [...h.timers.values()]) timer.fn();
    assert.equal(h.records().length, 1);assert.equal(h.records()[0].severity, 'error');
});
test('patch retains encoded URL, method, headers and exact JSON values', async () => {
    const h = setup(), data = {initiative: null, active: false, ac: 0};
    await h.ctx.patch('monsters', 'a/b', data);
    assert.equal(h.calls[0].url, '/api/monsters/a%2Fb');assert.equal(h.calls[0].options.method, 'PATCH');
    assert.equal(h.calls[0].options.headers['Content-Type'], 'application/json');assert.deepEqual(h.calls[0].body, data);
    assert.equal(h.records().length, 0);
});
test('duplicate same-field patch stays guarded through refresh', async () => {
    const h = setup(), hold = deferred();h.refresh = () => hold.promise;
    const pending = h.ctx.patch('characters', 'a', {hp: 1});await new Promise(setImmediate);
    await h.ctx.patch('characters', 'a', {hp: 1});assert.equal(h.calls.length, 1);hold.resolve();await pending;
});
test('old-scope cleanup cannot remove a newer pending guard', async () => {
    const h = setup(), old = deferred(), fresh = deferred();h.send = () => old.promise;
    const first = h.ctx.patch('characters', 'a', {hp: 1});h.scope('new');h.send = () => fresh.promise;
    const second = h.ctx.patch('characters', 'a', {hp: 2});old.resolve(ok());await first;
    await h.ctx.patch('characters', 'a', {hp: 2});assert.equal(h.calls.length, 2);
    fresh.resolve(ok());await second;assert.deepEqual(h.loads, [true]);
});
test('different field patches have independent pending identities', async () => {
    const h = setup(), hold = deferred();h.send = () => hold.promise;
    const a = h.ctx.patch('characters', 'a', {hp: 1}), b = h.ctx.patch('characters', 'a', {ac: 2});
    assert.equal(h.calls.length, 2);hold.resolve(ok());await Promise.all([a, b]);assert.equal(h.loads.length, 2);
});
test('successful refresh settles only its matching refresh error', async () => {
    const h = setup();h.refresh = async () => {throw Error('Refresh failed');};
    await h.ctx.patch('characters', 'a', {hp: 1});await h.ctx.patch('characters', 'b', {hp: 1});
    assert.equal(h.records().length, 2);h.refresh = async () => {};
    await h.ctx.patch('characters', 'a', {hp: 2});assert.equal(h.records().length, 1);assert.match(h.records()[0].target, /b/);
});
test('same IDs in different rosters do not replace each other', async () => {
    const h = setup();h.send = async () => {throw Error('Rejected');};
    await h.ctx.patch('characters', 'a', {hp: 1});await h.ctx.patch('monsters', 'a', {hp: 1});
    assert.equal(h.records().length, 2);assert.deepEqual(h.records().map(r => r.region).sort(), ['characters', 'monsters']);
});
for (const kind of ['characters', 'monsters']) for (const method of ['patch', 'bulk']) {
    test(`${kind} ${method}: loaded Join owner still reports one global rejection`, async () => {
        const h = setup(true);h.send = async () => new Response('{"detail":"Join rejected"}', {status: 422});
        if (method === 'patch') await h.ctx.patch(kind, 'a', {active: true});
        else await h.ctx.runBulkAction(kind, 'join-battle');
        assert.equal(h.calls.length, 1);assert.equal(h.loads.length, 0);assert.equal(h.records().length, 1);
        assert.equal(h.records()[0].operation, 'roster.join');assert.equal(h.records()[0].region, 'global');
        assert.equal(h.records()[0].text, 'Join rejected');assert.deepEqual(clean(h.feedback.legacyRegions()), []);
    });
}
