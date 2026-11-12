// SG-TODO-009.7 Deliverable 2: background-poll connection warning (persistent, deduplicated,
// recovery resolves only its own identity). Real controller/bootstrap; DOM, HTTP and timers mocked.
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');
const {createController} = require('../static/admin-feedback-controller.js');
const bootstrap = fs.readFileSync(path.join(__dirname, '../static/admin-feedback-admin.js'), 'utf8');
const code = fs.readFileSync(path.join(__dirname, '../static/features.js'), 'utf8');
const flush = async () => { for (let i = 0; i < 6; i++) await new Promise(resolve => setImmediate(resolve)); };

async function setup() {
    const elements = new Map(), timers = new Map();
    let now = 0, sequence = 0, poll = null;
    class Element {
        constructor() { this.dataset = {}; this.value = ''; this.files = []; this.listeners = {}; this.checked = false; }
        addEventListener(name, fn) { this.listeners[name] = fn; }
        replaceChildren(...children) { this.children = children; }
        append(...children) { this.children = children; }
    }
    const element = id => { if (!elements.has(id)) elements.set(id, new Element()); return elements.get(id); };
    const state = {active_campaign_id: 'fixture', active_setup: {campaign_id: 'fixture', name: 'setup'}, lairs: [], monsters: [],
        characters: [{id: 'c', name: 'Hero', hp: 10, max_hp: 10, active: true, temp_hp: 0}]};
    const summary = {checkpoints: [], displays: [], downed: [], undo: null};
    const h = {mode: 'ok', gets: 0};
    const context = {window: {scryingDamagePreview: () => 'Apply?'}, document: {createElement: () => new Element(), activeElement: null},
        FormData: class {}, Option: function(name, id) { this.text = name; this.value = String(id); },
        confirm: () => true, location: {},
        setInterval: (fn, delay) => { assert.equal(delay, 3000); poll = fn; return 1; },
        load: async () => {},
        fetch: async (url, request) => {
            if (request.method === 'GET') h.gets++;
            if (h.mode === 'network') throw new TypeError('Failed to fetch');
            if (h.mode === 'http') return {ok: false, status: 503, json: async () => ({detail: 'Service unavailable'})};
            if (h.mode === 'http2') return {ok: false, status: 500, json: async () => { throw new Error('not json'); }};
            return {ok: true, json: async () => url === '/api/state' ? state : summary};
        }};
    // Same bootstrap as battle-action-feedback-fixture.cjs, keeping the controller for dismissal
    // and notification counting.
    let controller, notifications = 0;
    context.document.getElementById = () => null;
    context.ScryingFeedback = {createController: () => (controller = createController({
        setTimeout(fn, delay) { const id = ++sequence; timers.set(id, {fn, deadline: now + delay}); return id; },
        clearTimeout(id) { timers.delete(id); },
    }))};
    vm.createContext(context);
    vm.runInContext(bootstrap, context);
    const feedback = context.window.scryingAdminFeedback;
    const scope = (campaign = 'fixture', name = 'setup') => assert(feedback.observeState(
        {active_campaign_id: campaign, active_setup: {campaign_id: campaign, name}}, feedback.stateRequest()));
    scope();
    controller.subscribe(() => { notifications++; });
    context.document.getElementById = element;
    element('featureTarget').value = 'c';
    vm.runInContext(code, context, {filename: 'static/features.js'});
    await flush();
    return Object.assign(h, {element, feedback, scope, state, controller, notified: () => notifications,
        records: () => feedback.snapshot().map(r => [r.lane, r.region, r.operation, r.severity, r.text]),
        connection: () => feedback.snapshot().filter(r => r.operation === 'connection.poll'),
        poll: async () => { poll(); await flush(); },
        tick(ms) { now += ms; for (const [id, item] of [...timers]) if (item.deadline <= now) { timers.delete(id); item.fn(); } }});
}
const lost = 'Connection to the server was lost. Retrying automatically.';

test('network loss shows one persistent global warning on the page lane', async () => {
    const h = await setup();
    assert.deepEqual(h.records(), []);
    h.mode = 'network'; await h.poll();
    assert.deepEqual(h.records(), [['page', 'global', 'connection.poll', 'warning', lost]]);
    assert.equal(h.element('featureNotice').textContent, undefined);
    h.tick(600000); assert.equal(h.connection().length, 1);
});

test('identical polling failures keep the same record without re-publishing', async () => {
    const h = await setup(); h.mode = 'network'; await h.poll();
    const first = h.connection()[0], before = h.notified();
    for (let i = 0; i < 5; i++) await h.poll();
    assert.equal(h.gets, 2 + 2 + 10, 'every poll still requests state and features');
    assert.equal(h.connection().length, 1);
    assert.equal(h.connection()[0], first, 'the identical failure keeps the existing frozen record');
    assert.equal(h.notified(), before, 'no controller notification, so no re-render or announcement');
});

test('a different failure replaces the warning in place (one record)', async () => {
    const h = await setup(); h.mode = 'network'; await h.poll();
    h.mode = 'http'; await h.poll();
    assert.deepEqual(h.records(), [['page', 'global', 'connection.poll', 'warning',
        'Background refresh failed: Service unavailable. Retrying automatically.']]);
    h.mode = 'http2'; await h.poll();
    assert.deepEqual(h.connection().map(r => r.text), ['Background refresh failed: Request failed (500). Retrying automatically.']);
});

test('recovery resolves only the connection identity and keeps unrelated errors', async () => {
    const h = await setup();
    const other = h.feedback.begin({region: 'global', operation: 'battle.next', target: 'battle', label: 'Next'});
    h.feedback.publish(other, {severity: 'error', text: 'Next rejected'});
    const page = h.feedback.begin({lane: 'page', region: 'campaign', operation: 'campaign.switch', target: 'x', label: 'Switch'});
    h.feedback.publish(page, {severity: 'error', text: 'Switch failed'});
    h.mode = 'network'; await h.poll();
    h.mode = 'ok'; await h.poll();
    assert.deepEqual(h.records(), [
        ['encounter', 'global', 'battle.next', 'error', 'Next rejected'],
        ['page', 'campaign', 'campaign.switch', 'error', 'Switch failed'],
        ['page', 'global', 'connection.poll', 'success', 'Connection to the server restored.'],
    ]);
    h.tick(4999); assert.equal(h.connection().length, 1);
    h.tick(1); assert.equal(h.connection().length, 0);
    assert.equal(h.records().length, 2);
});

test('successful polls without an outstanding warning publish nothing', async () => {
    const h = await setup();
    for (let i = 0; i < 3; i++) await h.poll();
    assert.deepEqual(h.records(), []);
});

test('a dismissed warning is not re-announced by identical failures; a new failure or recovery is', async () => {
    const h = await setup(); h.mode = 'network'; await h.poll();
    assert(h.controller.dismiss(h.connection()[0].id));
    for (let i = 0; i < 3; i++) await h.poll();
    assert.deepEqual(h.connection(), []);
    h.mode = 'http'; await h.poll();
    assert.deepEqual(h.connection().map(r => r.severity), ['warning']);
    h.controller.dismiss(h.connection()[0].id);
    h.mode = 'ok'; await h.poll();
    assert.deepEqual(h.connection().map(r => [r.severity, r.text]), [['success', 'Connection to the server restored.']]);
});

test('campaign/setup scope changes do not clear the connection warning', async () => {
    const h = await setup(); h.mode = 'network'; await h.poll();
    h.scope('other', 'second');
    assert.deepEqual(h.connection().map(r => r.severity), ['warning']);
});

test('manual Refresh failure stays a tools error and does not raise the connection warning', async () => {
    const h = await setup(); h.mode = 'network';
    await h.element('featureRefresh').onclick(); await flush();
    assert.deepEqual(h.records().map(r => r.slice(0, 4)), [['encounter', 'tools', 'tools.refresh', 'error']]);
    h.mode = 'ok'; await h.element('featureRefresh').onclick(); await flush();
    assert.deepEqual(h.records(), []);
});

test('manual success after a background loss also resolves the warning', async () => {
    const h = await setup(); h.mode = 'network'; await h.poll();
    h.mode = 'ok'; await h.element('featureRefresh').onclick(); await flush();
    assert.deepEqual(h.connection().map(r => r.severity), ['success']);
});
