// Production delegated-removal prefix with real feedback, not a full Admin browser.
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const read = p => fs.readFileSync(path.join(root, p), 'utf8');
const {createController} = require(path.join(root, 'static/admin-feedback-controller.js'));
const core = read('static/admin/070-source.js');
const start = core.indexOf("document.addEventListener('click', async event => {");
const end = core.indexOf("\n    if (button.dataset.battleActor)", start);
assert.ok(start >= 0 && end > start);
const source = core.slice(start, end) + '\n});';
function fixture() {
    const calls = [], prompts = [], modern = [], timers = new Map();
    let listener, refreshes = 0, timerId = 0;
    const f = {calls, prompts, modern, timers, accept: true,
        onRequest: async () => ({name: 'Server name'}), onLoad: async () => {}};
    const controller = createController({setTimeout(fn, ms) {timers.set(++timerId, {fn, ms}); return timerId;},
        clearTimeout(id) {timers.delete(id);}});
    const context = vm.createContext({window: {}, ScryingFeedback: {createController: () => controller},
        document: {getElementById: () => null, addEventListener(type, fn) {listener = fn;}},
        confirm(text) {prompts.push(text); return f.accept;},
        request: async (...args) => {calls.push(args); return f.onRequest(...args);},
        load: async () => {refreshes++; return f.onLoad();},
        removeCombatant: async (...args) => modern.push(args),
        message() {throw new Error('Fallback must not use legacy feedback');}});
    vm.runInContext(read('static/admin-feedback-admin.js'), context);
    const feedback = context.window.scryingAdminFeedback;
    f.scope = (campaign = 'a', name = 'one') => assert.equal(feedback.observeState({active_campaign_id: campaign,
        active_setup: {campaign_id: campaign, name}}, feedback.stateRequest()), true);
    f.scope(); vm.runInContext(source, context);
    Object.assign(f, {feedback, context, snapshot: () => feedback.snapshot(), refreshes: () => refreshes,
        button(id = 'x', kind = 'monster', name = 'Ogre') {
            return {dataset: {remove: id, ...(kind === undefined ? {} : {removeKind: kind})}, disabled: false,
                closest: () => name === null ? null : {querySelector: () => ({textContent: name})}};
        },
        click(button) {return listener({target: {closest: () => button}});},
        seed(id = 'x', text = 'old', operation = 'combatant.remove.fallback', severity = 'error') {
            return feedback.publish(feedback.begin({region: 'global', operation, target: id, label: operation}), {severity, text});
        }});
    return f;
}
function deferred() {let resolve, reject;
    const promise = new Promise((yes, no) => {resolve = yes; reject = no;}); return {promise, resolve, reject};}
test('named confirmation is unchanged and cancellation preserves error, ticket and button', async () => {
    const f = fixture(), b = f.button(); f.seed();
    const ticket = f.feedback.begin({region:'global',operation:'combatant.remove.fallback',target:'x',label:'pending'});
    f.accept = false; await f.click(b);
    assert.equal(f.prompts[0], 'Remove monster “Ogre” from the current encounter?');
    assert.equal(f.calls.length, 0); assert.equal(b.disabled, false); assert.equal(f.snapshot()[0].text, 'old');
    assert.equal(f.feedback.isCurrent(ticket), true);
});
test('button disables before one encoded bodyless DELETE, then success precedes refresh', async () => {
    const f = fixture(), b = f.button('a/b ?');
    f.onRequest = async (url, options) => {
        assert.equal(b.disabled, true); assert.equal(url, '/api/combatants/a%2Fb%20%3F');
        assert.equal(options.method, 'DELETE'); assert.deepEqual(Object.keys(options), ['method']);
        return {name:'Server name'};
    };
    f.onLoad = async () => {assert.equal(b.disabled, true); assert.equal(f.snapshot()[0].severity, 'success');};
    await f.click(b); assert.equal(f.calls.length, 1); assert.equal(f.refreshes(), 1);
    assert.equal(f.snapshot()[0].text, 'Removed Server name.'); assert.equal(b.disabled, true);
});
test('current request failure persists, reenables the button and never refreshes or retries', async () => {
    const f = fixture(), b = f.button(); f.onRequest = async () => {throw new Error('denied');};
    await f.click(b); assert.equal(b.disabled, false); assert.equal(f.calls.length, 1); assert.equal(f.refreshes(), 0);
    assert.equal(f.snapshot()[0].operation, 'combatant.remove.fallback'); assert.equal(f.snapshot()[0].target, 'x');
    assert.equal(f.snapshot()[0].severity, 'error'); assert.equal(f.snapshot()[0].text, 'denied'); assert.equal(f.timers.size, 0);
});
test('actual failure followed by matching success replaces its error only', async () => {
    const f = fixture(), b = f.button(); f.seed('y', 'other entity'); f.seed('x', 'reset error', 'combatant.reset');
    f.onRequest = async () => {throw new Error('failed');}; await f.click(b);
    f.onRequest = async () => ({name:'Ogre'}); await f.click(b);
    assert.equal(f.snapshot().filter(x => x.operation === 'combatant.remove.fallback' && x.target === 'x').length, 1);
    assert.equal(f.snapshot().find(x => x.operation === 'combatant.remove.fallback' && x.target === 'x').severity, 'success');
    assert.equal(f.snapshot().find(x => x.target === 'y').text, 'other entity');
    assert.equal(f.snapshot().find(x => x.operation === 'combatant.reset').text, 'reset error'); assert.equal(f.calls.length, 2);
});
test('success expiry is five seconds and cannot remove unrelated persistent errors', async () => {
    const f = fixture(); f.seed('y'); await f.click(f.button());
    const timer = [...f.timers.values()][0]; assert.equal(timer.ms, 5000); timer.fn();
    assert.equal(f.snapshot().length, 1); assert.equal(f.snapshot()[0].target, 'y');
});
test('removing another entity does not clear the first entity failure', async () => {
    const f = fixture(); f.seed(); await f.click(f.button('y'));
    assert.equal(f.snapshot().find(x => x.target === 'x').severity, 'error');
});
test('kind is display metadata: same endpoint ID retry resolves earlier default-kind error', async () => {
    const f = fixture(); f.seed(); await f.click(f.button('x', 'character', 'Ada'));
    assert.equal(f.snapshot().length, 1); assert.equal(f.snapshot()[0].severity, 'success');
});
test('refresh alone cannot clear a removal error', async () => {
    const f = fixture(); f.seed(); await f.context.load(); assert.equal(f.snapshot()[0].severity, 'error');
});
test('unrelated success cannot clear a removal error', () => {
    const f = fixture(); f.seed(); f.seed('battle', 'Reset', 'battle.reset-all', 'success');
    assert.equal(f.snapshot().find(x => x.operation === 'combatant.remove.fallback').severity, 'error');
});
test('confirmed deletion and real loadState refresh failure coexist without a second DELETE', async () => {
    const f = fixture(); f.seed(); f.onLoad = () => f.feedback.loadState(() => {
        f.feedback.stateRequest(); return Promise.reject(new Error('refresh failed'));
    }, () => {throw new Error('failed fetch must not render');});
    const b = f.button(); await f.click(b); assert.equal(f.calls.length, 1); assert.equal(b.disabled, true);
    assert.equal(f.snapshot().find(x => x.operation === 'combatant.remove.fallback').severity, 'success');
    assert.equal(f.snapshot().find(x => x.operation === 'state.load').severity, 'error');
});
test('unexpected refresh rejection is not labelled as a failed DELETE or reenabled for replay', async () => {
    const f = fixture(), b = f.button(); f.onLoad = async () => {throw new Error('refresh');};
    await assert.rejects(f.click(b), /refresh/); assert.equal(b.disabled, true);
    assert.equal(f.snapshot()[0].severity, 'success'); assert.equal(f.calls.length, 1);
});
test('old-setup success cannot publish or refresh the new setup', async () => {
    const f = fixture(), p = deferred(), b = f.button(); f.onRequest = () => p.promise;
    const done = f.click(b); f.scope('a','two'); f.seed('x','new error'); p.resolve({name:'old'}); await done;
    assert.equal(f.snapshot().length, 1); assert.equal(f.snapshot()[0].text, 'new error'); assert.equal(f.refreshes(), 0);
});
test('old-campaign failure cannot publish or alter a new control', async () => {
    const f = fixture(), p = deferred(), b = f.button(), newButton = f.button(); f.onRequest = () => p.promise;
    const done = f.click(b); f.scope('b'); f.seed('x','new error'); p.reject(new Error('old')); await done;
    assert.equal(f.snapshot()[0].text, 'new error'); assert.equal(newButton.disabled, false); assert.equal(b.disabled, true);
});
test('away-and-back scope changes cannot revive the original deletion response', async () => {
    const f = fixture(), p = deferred(); f.onRequest = () => p.promise;
    const done = f.click(f.button()); f.scope('b'); f.scope(); p.resolve({}); await done;
    assert.equal(f.snapshot().length, 0); assert.equal(f.refreshes(), 0);
});
test('superseded success preserves newer same-target failure', async () => {
    const f = fixture(), p = deferred(), b = f.button(); let n = 0;
    f.onRequest = () => ++n === 1 ? p.promise : Promise.reject(new Error('new failure'));
    const old = f.click(b); await f.click(b); p.resolve({name:'old'}); await old;
    assert.equal(f.snapshot()[0].text, 'new failure'); assert.equal(b.disabled, false); assert.equal(f.refreshes(), 0);
});
test('superseded failure cannot reenable the same button during a newer pending attempt', async () => {
    const f = fixture(), a = deferred(), b = deferred(), button = f.button(); let n = 0;
    f.onRequest = () => ++n === 1 ? a.promise : b.promise;
    const first = f.click(button), second = f.click(button); a.reject(new Error('old')); await first;
    assert.equal(button.disabled, true); assert.equal(f.snapshot().length, 0);
    b.resolve({name:'Ogre'}); await second; assert.equal(button.disabled, true);
});
test('different-target concurrent outcomes do not supersede each other', async () => {
    const f = fixture(), p = deferred(); let n = 0;
    f.onRequest = () => ++n === 1 ? p.promise : Promise.reject(new Error('other failure'));
    const first = f.click(f.button('x')); await f.click(f.button('y')); p.resolve({name:'Ogre'}); await first;
    assert.equal(f.snapshot().find(x => x.target === 'x').severity, 'success');
    assert.equal(f.snapshot().find(x => x.target === 'y').severity, 'error'); assert.equal(f.refreshes(), 1);
});
test('modern pane-removal route keeps priority even if data-remove is also present', async () => {
    const f = fixture(), b = f.button(); b.dataset.removeKind = 'monsters'; b.dataset.removeId = 'x';
    await f.click(b); assert.equal(f.modern.length, 1); assert.deepEqual(Array.from(f.modern[0]), ['monsters','x']);
    assert.equal(f.prompts.length, 0); assert.equal(f.calls.length, 0); assert.equal(f.snapshot().length, 0); assert.equal(b.disabled, false);
});
test('missing row uses kind fallback and confirmed success tolerates empty response JSON', async () => {
    const f = fixture(), b = f.button('x', 'combatant', null); f.onRequest = async () => null;
    await f.click(b); assert.equal(f.prompts[0], 'Remove combatant “combatant” from the current encounter?');
    assert.equal(f.snapshot()[0].text, 'Removed combatant.'); assert.equal(b.disabled, true);
});
test('no matching button or removal attributes causes no request or notice', async () => {
    const f = fixture(); await f.click(null); await f.click({dataset:{}});
    assert.equal(f.calls.length, 0); assert.equal(f.prompts.length, 0); assert.equal(f.snapshot().length, 0);
});
