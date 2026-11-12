// Production Join gate and migrated core functions; scoped controller adapter and mock transport/DOM.
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');
const {createController} = require('../static/admin-feedback-controller.js');
const gate = fs.readFileSync(path.join(__dirname, '../static/initiative-join-gate.js'), 'utf8');
const core = fs.readFileSync(path.join(__dirname, '../static/admin/010-source.js'), 'utf8');
function slice(start, end) {
    const first = core.indexOf(start), last = core.indexOf(end, first);
    assert(first >= 0 && last > first, 'production function boundaries');
    return core.slice(first, last);
}
const functions = slice('async function request(', 'function esc(') +
    slice('const rosterPending =', 'async function removeCombatant(') +
    slice('async function patch(', 'function colorMarker(');
function setup({kind = 'characters', ids = ['a'], complete = false} = {}) {
    let clock = 0, timerId = 0;
    const timers = new Map(), loadFlags = [];
    const controller = createController({setTimeout(fn, delay) {
        assert.equal(delay, 3000); const id = ++timerId; timers.set(id, {at: clock + delay, fn}); return id;
    }, clearTimeout(id) {timers.delete(id);}});
    let scope = 'fixture', ready, clicks, loads = 0;
    controller.setScope('encounter', scope);
    const api = {begin: spec => controller.begin({...spec, lane: 'encounter', scope, placement: spec.region === 'global' ? 'global' : 'pane'}),
        publish: controller.publish, resolve: controller.resolve, isCurrent: controller.isCurrent};
    const calls = [], panes = [], selected = [...ids];
    let transport = async () => new Response('{}'), refresh = async () => {};
    const ctx = {URL, console, window: {scryingAdminFeedback: api,
        location: {origin: 'http://fixture', href: 'http://fixture/'},
        fetch: async (url, options) => {calls.push({url, options});return transport(url, options);}},
        document: {readyState: complete ? 'complete' : 'interactive', getElementById: () => null,
            querySelectorAll: () => [], addEventListener(type, fn, options) {
                if (type === 'click') {assert.equal(options, true);clicks = fn;}
                else {assert.equal(type, 'DOMContentLoaded');assert.equal(options.once, true);ready = fn;}
            }},
        latest: {characters: [], monsters: []},
        selectedIds: () => [...selected], selectionMessage: () => 'Select one or more first.',
        setAllSelected: () => {}, itemsFor: () => [], confirm: () => true,
        paneNotification: (region, text) => panes.push({region, text}),
        load: async flag => {loadFlags.push(flag);loads++;await refresh();}};
    ctx.fetch = (...args) => ctx.window.fetch(...args);
    ctx.bulkRequest = (k, action, list) => ctx.request(`/api/${k}/bulk`, {
        method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({action, ids: list})});
    vm.createContext(ctx);
    if (complete) vm.runInContext(functions, ctx);
    vm.runInContext(gate, ctx);
    if (!complete) {vm.runInContext(functions, ctx);ready();}
    return {ctx, calls, panes, selected, loadFlags, records: controller.snapshot,
        advance(ms) {clock += ms; for (const [id, timer] of [...timers]) {
            if (timer.at <= clock) {timers.delete(id); timer.fn();}
        }},
        get loads() {return loads;}, transport(fn) {transport = fn;}, refresh(fn) {refresh = fn;},
        scope(value) {scope = value;controller.setScope('encounter', value);},
        emit(text, target = 'other') {controller.publish(api.begin({region: 'global', operation: 'other', target, label: 'Other'}), {severity: 'error', text});},
        patch(id = 'a', data = {active: true}) {return ctx.patch(kind, id, data);},
        bulk(action = 'join-battle') {return ctx.runBulkAction(kind, action);},
        blocked(id = 'a') {
            ctx.latest[kind] = [{id, name: 'Alpha', active: false, initiative: null}];
            const button = {hasAttribute: name => name === (kind === 'characters' ? 'data-ca' : 'data-ma'), getAttribute: () => id};
            const event = {target: {closest: () => button}, preventDefault() {this.prevented = true;}, stopImmediatePropagation() {this.stopped = true;}};
            clicks(event);assert(event.prevented && event.stopped);
        }};
}
const rejected = (detail = 'Join rejected') => new Response(JSON.stringify({detail}), {status: 422});
for (const kind of ['characters', 'monsters']) {
    for (const method of ['patch', 'bulk']) {
        test(`${kind} ${method}: exactly one persistent rejection and no pane duplicate`, async () => {
            const w = setup({kind});w.transport(async () => rejected());
            await w[method]();
            assert.equal(w.calls.length, 1);assert.equal(w.loads, 0);assert.deepEqual(w.panes, []);
            assert.equal(w.records().length, 1);assert.equal(w.records()[0].severity, 'error');
            assert.equal(w.records()[0].operation, 'roster.join');assert.equal(w.records()[0].text, 'Join rejected');
        });
        test(`${kind} ${method}: network error is reported once without replay`, async () => {
            const w = setup({kind});w.transport(async () => {throw new Error('Offline');});
            await w[method]();assert.equal(w.calls.length, 1);assert.equal(w.records().length, 1);
            assert.equal(w.records()[0].text, 'Offline');assert.deepEqual(w.panes, []);
        });
    }
    test(`${kind}: blocked click then matching core retry preserves another target/error`, async () => {
        const w = setup({kind});w.blocked('a');w.blocked('b');w.emit('Unrelated');
        await w.patch('a');
        assert.deepEqual(w.records().map(r => r.text), ['Enter initiative before joining battle: Alpha', 'Unrelated']);
        assert.equal(w.records()[0].target, JSON.stringify([kind, 'b']));assert.equal(w.loads, 1);
    });
    test(`${kind}: bulk key canonicalizes order without changing payload order or single target`, async () => {
        const w = setup({kind, ids: ['b', 'a']});w.blocked();w.transport(async () => rejected());
        await w.bulk();w.selected.reverse();w.transport(async () => new Response('{"count":2}'));
        await w.bulk();
        const global = w.records().filter(r => r.region === 'global');
        assert.equal(global.length, 1);assert.equal(global[0].target, JSON.stringify([kind, 'a']));
        assert.deepEqual(JSON.parse(w.calls[0].options.body), {action: 'join-battle', ids: ['b', 'a']});
        assert.deepEqual(JSON.parse(w.calls[1].options.body), {action: 'join-battle', ids: ['a', 'b']});
        assert.deepEqual(w.panes, []);
        const success = w.records().filter(r => r.region === kind);
        assert.equal(success.length, 1);assert.equal(success[0].severity, 'success');
        assert.equal(success[0].text, '2 ' + kind + ' updated.');
    });
}
test('structured core request errors retain formatted field context', async () => {
    const w = setup();w.transport(async () => rejected([{loc: ['body', 'initiative'], msg: 'Required'}]));
    await w.patch();assert.equal(w.records()[0].text, 'initiative: Required');assert.deepEqual(w.panes, []);
});
test('non-JSON core failure retains HTTP request fallback', async () => {
    const w = setup();w.transport(async () => new Response('HTML', {status: 503, statusText: 'Unavailable'}));
    await w.patch();assert.equal(w.records()[0].text, '503 Unavailable');
});
for (const method of ['patch', 'bulk']) for (const ok of [false, true]) {
    test(`${method}: stale scope ${ok ? 'success' : 'failure'} cannot publish or refresh`, async () => {
        const w = setup();let release;w.transport(() => new Promise(resolve => {release = resolve;}));
        const pending = w[method]();w.scope('new');w.emit('New scope');
        release(ok ? new Response('{}') : rejected('Old scope'));await pending;
        assert.deepEqual(w.records().map(r => r.text), ['New scope']);assert.deepEqual(w.panes, []);assert.equal(w.loads, 0);
    });
}
for (const ok of [false, true]) test(`superseded ${ok ? 'success' : 'failure'} cannot replace current rejection`, async () => {
    const w = setup();let release;w.transport(() => new Promise(resolve => {release = resolve;}));
    const old = w.patch();w.transport(async () => rejected('New rejection'));await w.patch();
    release(ok ? new Response('{}') : rejected('Old rejection'));await old;
    assert.deepEqual(w.records().map(r => r.text), ['New rejection']);assert.equal(w.loads, 0);
});
for (const method of ['patch', 'bulk']) test(`${method}: refresh failure is not a Join rejection or mutation replay`, async () => {
    const w = setup();w.refresh(async () => {throw new Error('Refresh failed');});
    if (method === 'patch') {
        await assert.rejects(w.patch(), /Refresh failed/);assert.equal(w.records().length, 0);
    } else {
        await w.bulk();assert.deepEqual(w.records().map(r => r.severity), ['success', 'error']);
        assert.equal(w.records()[1].operation, 'roster.bulk.join-battle.refresh');
        assert.match(w.records()[1].text, /do not repeat the Join/);
        assert.equal(w.records().some(r => r.operation === 'roster.join'), false);
    }
    assert.equal(w.calls.length, 1);assert.equal(w.loads, 1);
});
test('non-Join patch, leave and bulk actions delegate to explicit local feedback', async () => {
    const w = setup();w.transport(async () => rejected('Other error'));
    await w.patch('a', {active: false});await w.patch('a', {initiative: 0});await w.bulk('leave-battle');
    assert.equal(w.calls.length, 3);assert.equal(w.records().length, 3);assert.deepEqual(w.panes, []);
    assert(w.records().every(r => r.region === 'characters' && r.placement === 'pane' && r.severity === 'error'));
    assert.deepEqual(w.records().map(r => r.text), ['Other error', 'Other error', 'Other error']);
    assert(w.records().every(r => r.operation !== 'roster.join'));
});
test('empty bulk selection keeps local validation explicit without a request', async () => {
    const w = setup({ids: []});await w.bulk();assert.equal(w.calls.length, 0);assert.deepEqual(w.panes, []);
    assert.equal(w.records().length, 1);assert.equal(w.records()[0].region, 'characters');
    assert.equal(w.records()[0].operation, 'roster.bulk.join-battle.selection');
    assert.equal(w.records()[0].severity, 'error');assert.equal(w.records()[0].text, 'Select one or more first.');
});
test('encoded single ID, method, headers and payload are preserved', async () => {
    const w = setup();await w.patch('a/b', {active: true});
    assert.equal(w.calls[0].url, '/api/characters/a%2Fb');assert.equal(w.calls[0].options.method, 'PATCH');
    assert.equal(w.calls[0].options.headers['Content-Type'], 'application/json');
    assert.deepEqual(JSON.parse(w.calls[0].options.body), {active: true});assert.equal(w.loads, 1);
});
test('late injection and repeated loading do not wrap/report twice', async () => {
    const w = setup({complete: true});const patch = w.ctx.patch, fetch = w.ctx.window.fetch;
    vm.runInContext(gate, w.ctx);assert.equal(w.ctx.patch, patch);assert.equal(w.ctx.window.fetch, fetch);
    w.transport(async () => rejected());await w.patch();assert.equal(w.records().length, 1);assert.equal(w.calls.length, 1);
});

const turn = () => new Promise(resolve => setImmediate(resolve));
for (const kind of ['characters', 'monsters']) test(`${kind}: pane success precedes strict refresh and expires at 3s`, async () => {
    const w = setup({kind});let release;w.refresh(() => new Promise(resolve => {release = resolve;}));
    const pending = w.bulk();await turn();
    assert.equal(w.records()[0].operation, 'roster.bulk.join-battle');
    assert.equal(w.records()[0].placement, 'pane');assert.deepEqual(w.loadFlags, [true]);
    assert.equal(w.records()[0].text, `1 ${kind === 'characters' ? 'character' : 'monster'} updated.`);
    w.advance(2999);assert.equal(w.records().length, 1);w.advance(1);assert.equal(w.records().length, 0);
    release();await pending;
});
test('matching selected retry clears selection validation and keeps independent errors', async () => {
    const w = setup({ids: []});await w.bulk();w.emit('Keep global');w.selected.push('a');await w.bulk();
    assert.equal(w.records().some(r => r.operation.endsWith('.selection')), false);
    assert.equal(w.records().some(r => r.text === 'Keep global'), true);assert.deepEqual(w.panes, []);
});
test('duplicate bulk Join is suppressed through mutation and refresh even with reordered selection', async () => {
    const w = setup({ids: ['b', 'a']});let send, reload;
    w.transport(() => new Promise(resolve => {send = resolve;}));w.refresh(() => new Promise(resolve => {reload = resolve;}));
    const pending = w.bulk();w.selected.reverse();await w.bulk();assert.equal(w.calls.length, 1);
    send(new Response('{"count":2}'));await turn();await w.bulk();assert.equal(w.calls.length, 1);assert.equal(w.loads, 1);
    reload();await pending;w.transport(async () => new Response('{}'));w.refresh(async () => {});await w.bulk();assert.equal(w.calls.length, 2);
});
test('equal selected IDs in different rosters do not share a pending lock or pane identity', async () => {
    const w = setup();const releases=[];w.transport(() => new Promise(resolve => releases.push(resolve)));
    const characters = w.bulk(), monsters = w.ctx.runBulkAction('monsters', 'join-battle');
    assert.equal(w.calls.length, 2);for (const release of releases) release(new Response('{}'));
    await Promise.all([characters, monsters]);assert.deepEqual(w.records().map(r => r.region), ['characters', 'monsters']);
});
for (const ok of [false, true]) test(`obsolete bulk refresh ${ok ? 'success' : 'failure'} preserves new-scope feedback`, async () => {
    const w = setup();let yes, no;w.refresh(() => new Promise((resolve, reject) => {yes = resolve;no = reject;}));
    const pending = w.bulk();await turn();w.scope('other');w.emit('New encounter');
    if (ok) yes();else no(new Error('Old reload'));await pending;
    assert.deepEqual(w.records().map(r => r.text), ['New encounter']);assert.equal(w.calls.length, 1);
});
test('refresh failure persists after success expiry and resolves on explicit matching retry', async () => {
    const w = setup();w.refresh(async () => {throw new Error('Offline');});await w.bulk();w.advance(60000);
    assert.equal(w.records().length, 1);assert.equal(w.records()[0].operation, 'roster.bulk.join-battle.refresh');
    assert.equal(w.calls.length, 1);w.refresh(async () => {});await w.bulk();
    assert.equal(w.records().some(r => r.severity === 'error'), false);assert.equal(w.calls.length, 2);
});
test('newer pane outcome suppresses obsolete bulk success and reload', async () => {
    const w = setup();let release;w.transport(() => new Promise(resolve => {release = resolve;}));const pending = w.bulk();
    const api = w.ctx.window.scryingAdminFeedback;
    api.publish(api.begin({region: 'characters', operation: 'roster.bulk.join-battle',
        target: JSON.stringify(['characters', ['a']]), label: 'New outcome'}), {severity: 'error', text: 'Keep newer'});
    release(new Response('{}'));await pending;assert.deepEqual(w.records().map(r => r.text), ['Keep newer']);assert.equal(w.loads, 0);
});
test('single Join remains silent and its transport ownership marker is preserved', async () => {
    const w = setup();await w.patch();assert.equal(w.records().length, 0);
    await w.bulk();assert.equal(Object.getOwnPropertySymbols(w.calls[1].options).length, 1);
    assert.equal(w.calls[1].options.method, 'POST');assert.equal(w.calls[1].options.headers['Content-Type'], 'application/json');
});
test('explicit zero count and missing-count fallback retain bulk wording', async () => {
    const w = setup({ids: ['b', 'a']});w.transport(async () => new Response('{"count":0}'));await w.bulk();
    assert.equal(w.records()[0].text, '0 characters updated.');w.transport(async () => new Response('{}'));await w.bulk();
    assert.equal(w.records().filter(r => r.severity === 'success')[0].text, '2 characters updated.');
});
