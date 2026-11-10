'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const {createController} = require(path.join(root, 'static/admin-feedback-controller.js'));
const source = fs.readFileSync(path.join(root, 'static/admin-end-feedback.js'), 'utf8');
const bootstrap = fs.readFileSync(path.join(root, 'static/admin-feedback-admin.js'), 'utf8');
function fixture() {
    const timers = new Map(), calls = [], confirmations = [], button = {};
    let timerId = 0, refreshes = 0;
    const f = {calls, confirmations, timers, button, accept: true,
        onRequest: async () => ({}), onLoad: async () => {}};
    const controller = createController({setTimeout(fn, ms) {
        timers.set(++timerId, {fn, ms}); return timerId;
    }, clearTimeout(id) { timers.delete(id); }});
    const context = vm.createContext({window: {},
        document: {getElementById: id => id === 'endBattle' ? button : null},
        ScryingFeedback: {createController: () => controller},
        latest: {battle_order: ['m'], monsters: [{id: 'm', hp: 3}], characters: [{id: 'c', hp: 7}]},
        confirm(text) { confirmations.push(text); return f.accept; },
        request: async (...args) => { calls.push(args); return f.onRequest(...args); },
        load: async () => { refreshes++; return f.onLoad(); },
        message() { throw new Error('Legacy feedback must not be used'); }});
    vm.runInContext(bootstrap, context);
    const feedback = context.window.scryingAdminFeedback;
    f.scope = (campaign = 'a', name = 'one') => {
        const seq = feedback.stateRequest();
        assert.equal(feedback.observeState({active_campaign_id: campaign,
            active_setup: {campaign_id: campaign, name}}, seq), true);
    };
    f.scope();
    vm.runInContext(source, context);
    Object.assign(f, {context, feedback, controller,
        click: () => button.onclick(), snapshot: () => feedback.snapshot(),
        seed(operation, text = operation, severity = 'error') {
            const ticket = feedback.begin({region: 'global', operation, target: 'battle', label: operation});
            return feedback.publish(ticket, {severity, text});
        }, refreshes: () => refreshes});
    return f;
}
function deferred() {
    let resolve, reject;
    const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
    return {promise, resolve, reject};
}
test('End asset is deferred after core and Start validation, exactly once', () => {
    const html = fs.readFileSync(path.join(root, 'templates/admin/190_document_end.html'), 'utf8');
    const tag = '<script src="/static/admin-end-feedback.js?v=1" defer></script>';
    assert.equal(html.split(tag).length, 2);
    assert.ok(html.indexOf(tag) > html.indexOf('/static/admin-start-validation.js'));
    assert.ok(html.indexOf('/static/admin-start-validation.js') > html.indexOf('/static/admin.js'));
});
test('empty battle produces a persistent validation error without confirmation or POST', async () => {
    const f = fixture(); f.context.latest.battle_order = [];
    await f.click();
    assert.equal(f.calls.length, 0); assert.equal(f.confirmations.length, 0);
    assert.equal(f.snapshot()[0].operation, 'battle.end.validation');
    assert.equal(f.snapshot()[0].severity, 'error'); assert.equal(f.timers.size, 0);
});
test('cancelling confirmation leaves existing End errors intact', async () => {
    const f = fixture(); f.seed('battle.end.validation'); f.seed('battle.end');
    const before = f.snapshot(); f.accept = false; await f.click();
    assert.deepEqual(f.snapshot(), before); assert.equal(f.calls.length, 0);
    assert.equal(f.confirmations[0], 'End the battle without resetting combatants?');
});
test('confirmed valid attempt resolves validation before sending the unchanged POST', async () => {
    const f = fixture(); f.seed('battle.end.validation');
    f.onRequest = async (url, options) => {
        assert.equal(f.snapshot().some(x => x.operation === 'battle.end.validation'), false);
        assert.equal(url, '/api/battle/end'); assert.equal(options.method, 'POST');
        assert.deepEqual(Object.keys(options), ['method']);
    };
    const before = JSON.stringify(f.context.latest); await f.click();
    assert.equal(f.calls.length, 1); assert.equal(JSON.stringify(f.context.latest), before);
    assert.equal(f.refreshes(), 1);
});
test('request failure stays persistent and does not refresh or retry', async () => {
    const f = fixture(); f.onRequest = async () => { throw new Error('denied'); };
    await f.click();
    assert.equal(f.snapshot()[0].text, 'denied'); assert.equal(f.snapshot()[0].severity, 'error');
    assert.equal(f.snapshot()[0].operation, 'battle.end'); assert.equal(f.timers.size, 0);
    assert.equal(f.calls.length, 1); assert.equal(f.refreshes(), 0);
});
test('successful retry replaces only its request error and uses the global five-second deadline', async () => {
    const f = fixture(); f.seed('battle.end'); f.seed('battle.next');
    await f.click();
    assert.equal(f.snapshot().filter(x => x.operation === 'battle.end').length, 1);
    assert.equal(f.snapshot().find(x => x.operation === 'battle.end').severity, 'success');
    assert.equal(f.snapshot().find(x => x.operation === 'battle.next').severity, 'error');
    const timer = [...f.timers.values()][0]; assert.equal(timer.ms, 5000); timer.fn();
    assert.equal(f.snapshot().length, 1); assert.equal(f.snapshot()[0].operation, 'battle.next');
});
test('refresh alone does not resolve an End request error', async () => {
    const f = fixture(); f.seed('battle.end'); await f.context.load();
    assert.equal(f.snapshot()[0].operation, 'battle.end'); assert.equal(f.snapshot()[0].severity, 'error');
});
test('validation rejection does not resolve an existing End request error', async () => {
    const f = fixture(); f.seed('battle.end'); f.context.latest.battle_order = [];
    await f.click(); assert.equal(f.snapshot().length, 2); assert.equal(f.calls.length, 0);
});
test('End success is published before refresh and coexists with load-owned refresh error', async () => {
    const f = fixture(); f.seed('battle.end');
    f.onLoad = async () => {
        assert.equal(f.snapshot().find(x => x.operation === 'battle.end').severity, 'success');
        f.seed('state.load', 'Refresh failed');
    };
    await f.click();
    assert.equal(f.calls.length, 1); assert.equal(f.refreshes(), 1);
    assert.equal(f.snapshot().find(x => x.operation === 'state.load').severity, 'error');
    assert.equal(f.snapshot().find(x => x.operation === 'battle.end').text, 'Battle ended. Combatants were not reset.');
});
test('unexpected refresh rejection is not recast as a failed End request', async () => {
    const f = fixture(); f.onLoad = async () => { throw new Error('refresh'); };
    await assert.rejects(f.click(), /refresh/);
    assert.equal(f.snapshot()[0].severity, 'success'); assert.equal(f.calls.length, 1);
});
test('old-setup successful response cannot announce or refresh the new setup', async () => {
    const f = fixture(), pending = deferred(); f.onRequest = () => pending.promise;
    const done = f.click(); f.scope('a', 'two'); f.seed('battle.end', 'new setup error');
    pending.resolve({}); await done;
    assert.equal(f.refreshes(), 0); assert.equal(f.snapshot()[0].text, 'new setup error');
});
test('old-campaign failed response cannot publish into the new campaign', async () => {
    const f = fixture(), pending = deferred(); f.onRequest = () => pending.promise;
    const done = f.click(); f.scope('b'); f.seed('battle.end', 'new campaign error');
    pending.reject(new Error('old failure')); await done;
    assert.equal(f.snapshot().length, 1); assert.equal(f.snapshot()[0].text, 'new campaign error');
});
test('switching away and back does not revive an old request', async () => {
    const f = fixture(), pending = deferred(); f.onRequest = () => pending.promise;
    const done = f.click(); f.scope('b'); f.scope(); pending.resolve({}); await done;
    assert.equal(f.snapshot().length, 0); assert.equal(f.refreshes(), 0);
});
test('superseded success does not erase a newer same-operation failure', async () => {
    const f = fixture(), pending = deferred(); let n = 0;
    f.onRequest = () => ++n === 1 ? pending.promise : Promise.reject(new Error('new failure'));
    const old = f.click(); await f.click(); pending.resolve({}); await old;
    assert.equal(f.snapshot()[0].text, 'new failure'); assert.equal(f.refreshes(), 0);
    assert.equal(f.calls.length, 2);
});
test('unrelated success cannot clear an End error and no legacy route is used', async () => {
    const f = fixture(); f.onRequest = async () => { throw new Error('End failed'); };
    await f.click(); f.seed('battle.start', 'Started', 'success');
    assert.equal(f.snapshot().find(x => x.operation === 'battle.end').severity, 'error');
    assert.deepEqual(Array.from(f.feedback.legacyRegions()), []);
});
