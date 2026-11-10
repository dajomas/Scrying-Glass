'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const {createController} = require(path.join(root, 'static/admin-feedback-controller.js'));
const source = fs.readFileSync(path.join(root, 'static/admin-reset-all-feedback.js'), 'utf8');
const bootstrap = fs.readFileSync(path.join(root, 'static/admin-feedback-admin.js'), 'utf8');
function fixture() {
    const timers = new Map(), calls = [], confirmations = [], button = {};
    const end = {onclick() {}}, individual = {onclick() {}};
    let timerId = 0, refreshes = 0;
    const f = {calls, confirmations, timers, button, end, individual, accept: true,
        onRequest: async () => ({}), onLoad: async () => {}};
    const controller = createController({setTimeout(fn, ms) {
        timers.set(++timerId, {fn, ms}); return timerId;
    }, clearTimeout(id) { timers.delete(id); }});
    const context = vm.createContext({window: {},
        document: {getElementById: id => ({resetAll: button, endBattle: end, individualReset: individual}[id] || null)},
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
    const endHandler = end.onclick, individualHandler = individual.onclick;
    vm.runInContext(source, context);
    assert.equal(end.onclick, endHandler); assert.equal(individual.onclick, individualHandler);
    Object.assign(f, {context, feedback, controller,
        click: () => button.onclick(), snapshot: () => feedback.snapshot(),
        seed(operation, text = operation, severity = 'error') {
            return feedback.publish(feedback.begin({region: 'global', operation,
                target: 'battle', label: operation}), {severity, text});
        }, refreshes: () => refreshes});
    return f;
}
function deferred() {
    let resolve, reject;
    const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
    return {promise, resolve, reject};
}
test('asset loads once, deferred after core and End feedback', () => {
    const html = fs.readFileSync(path.join(root, 'templates/admin/190_document_end.html'), 'utf8');
    const tag = '<script src="/static/admin-reset-all-feedback.js?v=1" defer></script>';
    assert.equal(html.split(tag).length, 2);
    assert.ok(html.indexOf(tag) > html.indexOf('/static/admin-end-feedback.js'));
    assert.ok(html.indexOf('/static/admin-end-feedback.js') > html.indexOf('/static/admin.js'));
});
test('cancellation preserves the error and does not begin or supersede a request', async () => {
    const f = fixture(); f.seed('battle.reset-all'); const before = f.snapshot();
    const guard = f.feedback.begin({region: 'global', operation: 'battle.reset-all', target: 'battle', label: 'pending'});
    f.accept = false; await f.click();
    assert.deepEqual(f.snapshot(), before); assert.equal(f.feedback.isCurrent(guard), true);
    assert.equal(f.calls.length, 0); assert.equal(f.refreshes(), 0);
    assert.equal(f.confirmations[0], 'Reset every monster and character?');
});
test('one unchanged POST and refresh, without direct client state mutation', async () => {
    const f = fixture(), before = JSON.stringify(f.context.latest);
    await f.click(); assert.equal(f.calls.length, 1);
    assert.equal(f.calls[0][0], '/api/battle/reset-all');
    assert.equal(f.calls[0][1].method, 'POST');
    assert.deepEqual(Object.keys(f.calls[0][1]), ['method']);
    assert.equal(JSON.stringify(f.context.latest), before); assert.equal(f.refreshes(), 1);
    assert.equal(f.snapshot().length, 0); assert.equal(f.timers.size, 0);
});
test('failure publishes persistent explicit error and neither refreshes nor retries', async () => {
    const f = fixture(); f.onRequest = async () => { throw new Error('denied'); };
    await f.click(); assert.equal(f.calls.length, 1); assert.equal(f.refreshes(), 0);
    assert.equal(f.snapshot()[0].operation, 'battle.reset-all');
    assert.equal(f.snapshot()[0].severity, 'error'); assert.equal(f.snapshot()[0].text, 'denied');
    assert.equal(f.timers.size, 0);
});
test('actual failed attempt followed by success silently resolves only Reset All', async () => {
    const f = fixture(); f.seed('battle.end');
    f.onRequest = async () => { throw new Error('failed reset'); }; await f.click();
    assert.equal(f.snapshot().length, 2);
    f.onRequest = async () => ({}); await f.click();
    assert.equal(f.snapshot().length, 1); assert.equal(f.snapshot()[0].operation, 'battle.end');
    assert.equal(f.calls.length, 2); assert.equal(f.refreshes(), 1); assert.equal(f.timers.size, 0);
});
test('refresh alone cannot clear a Reset All error', async () => {
    const f = fixture(); f.seed('battle.reset-all'); await f.context.load();
    assert.equal(f.snapshot().length, 1); assert.equal(f.snapshot()[0].severity, 'error');
});
test('unrelated success cannot clear Reset All errors or use the legacy route', async () => {
    const f = fixture(); f.seed('battle.reset-all'); f.seed('battle.end', 'Ended', 'success');
    assert.equal(f.snapshot().find(x => x.operation === 'battle.reset-all').severity, 'error');
    assert.deepEqual(Array.from(f.feedback.legacyRegions()), []);
});
test('successful mutation resolves before real loadState publishes its own refresh failure', async () => {
    const f = fixture(); f.seed('battle.reset-all'); f.seed('battle.end');
    f.onLoad = () => {
        assert.equal(f.snapshot().some(x => x.operation === 'battle.reset-all'), false);
        return f.feedback.loadState(() => {
            f.feedback.stateRequest(); return Promise.reject(new Error('refresh failed'));
        }, () => { throw new Error('failed fetch must not render'); });
    };
    await f.click(); assert.equal(f.calls.length, 1);
    assert.equal(f.snapshot().find(x => x.operation === 'state.load').text, 'refresh failed');
    assert.equal(f.snapshot().some(x => x.operation === 'battle.reset-all'), false);
    assert.equal(f.snapshot().find(x => x.operation === 'battle.end').severity, 'error');
});
test('old-setup success cannot resolve or refresh a newer setup', async () => {
    const f = fixture(), pending = deferred(); f.onRequest = () => pending.promise;
    const done = f.click(); f.scope('a', 'two'); f.seed('battle.reset-all', 'new error');
    pending.resolve({}); await done;
    assert.equal(f.refreshes(), 0); assert.equal(f.snapshot()[0].text, 'new error');
});
test('old-campaign failure cannot publish into the new campaign', async () => {
    const f = fixture(), pending = deferred(); f.onRequest = () => pending.promise;
    const done = f.click(); f.scope('b'); f.seed('battle.reset-all', 'new error');
    pending.reject(new Error('old failure')); await done;
    assert.equal(f.snapshot().length, 1); assert.equal(f.snapshot()[0].text, 'new error');
});
test('away-and-back scope changes do not revive an old response', async () => {
    const f = fixture(), pending = deferred(); f.onRequest = () => pending.promise;
    const done = f.click(); f.scope('b'); f.scope(); pending.resolve({}); await done;
    assert.equal(f.snapshot().length, 0); assert.equal(f.refreshes(), 0);
});
test('superseded success cannot clear a newer same-scope failure', async () => {
    const f = fixture(), pending = deferred(); let n = 0;
    f.onRequest = () => ++n === 1 ? pending.promise : Promise.reject(new Error('new failure'));
    const old = f.click(); await f.click(); pending.resolve({}); await old;
    assert.equal(f.snapshot()[0].text, 'new failure'); assert.equal(f.refreshes(), 0);
    assert.equal(f.calls.length, 2);
});
test('superseded failure cannot reinstate an error after the newer success', async () => {
    const f = fixture(), pending = deferred(); let n = 0;
    f.onRequest = () => ++n === 1 ? pending.promise : Promise.resolve({});
    const old = f.click(); await f.click(); pending.reject(new Error('old failure')); await old;
    assert.equal(f.snapshot().length, 0); assert.equal(f.refreshes(), 1);
});
test('unexpected refresh rejection is not published as a Reset All request failure', async () => {
    const f = fixture(); f.seed('battle.reset-all');
    f.onLoad = async () => { throw new Error('unexpected refresh'); };
    await assert.rejects(f.click(), /unexpected refresh/);
    assert.equal(f.snapshot().length, 0); assert.equal(f.calls.length, 1);
});
test('absence of the Reset All button does not affect other handlers', () => {
    assert.doesNotThrow(() => vm.runInNewContext(source, {document: {getElementById: () => null}}));
});
test('Reset All remains available with an empty battle order', async () => {
    const f = fixture(); f.context.latest.battle_order = [];
    await f.click(); assert.equal(f.calls.length, 1); assert.equal(f.confirmations.length, 1);
});
