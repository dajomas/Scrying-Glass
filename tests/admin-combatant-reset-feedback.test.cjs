// Production helper/delegated-click slices with real feedback; not a full Admin browser.
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
const start = core.indexOf('async function resetCombatantWithFeedback(');
const end = core.indexOf("document.addEventListener('change'", start);
assert.ok(start >= 0 && end > start);
const source = core.slice(start, end);
function fixture() {
    const listeners = {}, calls = [], patches = [], other = [], timers = new Map();
    let timerId = 0, refreshes = 0;
    const f = {calls, patches, other, timers, onRequest: async () => ({}), onLoad: async () => {}};
    const controller = createController({setTimeout(fn, ms) {timers.set(++timerId, {fn, ms}); return timerId;},
        clearTimeout(id) {timers.delete(id);}});
    const context = vm.createContext({window: {}, ScryingFeedback: {createController: () => controller},
        document: {getElementById: () => null, addEventListener(type, handler) {listeners[type] = handler;}},
        latest: {monsters: [{id: 'm1', name: 'Ogre'}, {id: 'm2', name: 'Wolf'}],
            characters: [{id: 'c1', name: 'Ada'}]},
        request: async (...args) => {calls.push(args); return f.onRequest(...args);},
        load: async () => {refreshes++; return f.onLoad();},
        patch: (...args) => patches.push(args),
        removeCombatant: (...args) => other.push(['remove', ...args]),
        openBattleActions: id => other.push(['actions', id]), openEdit: (...args) => other.push(['edit', ...args]),
        confirm() {throw new Error('Individual reset must not add a confirmation');},
        message() {throw new Error('Reset must not use legacy feedback');}});
    vm.runInContext(read('static/admin-feedback-admin.js'), context);
    const feedback = context.window.scryingAdminFeedback;
    f.scope = (campaign = 'a', name = 'one') => {
        assert.equal(feedback.observeState({active_campaign_id: campaign,
            active_setup: {campaign_id: campaign, name}}, feedback.stateRequest()), true);
    };
    f.scope(); vm.runInContext(source, context);
    Object.assign(f, {context, feedback, snapshot: () => feedback.snapshot(), refreshes: () => refreshes,
        click(dataset) {const button = {dataset, classList: {contains: () => false}};
            return listeners.click({target: {closest: () => button}});},
        seed(operation, kind = 'monsters', id = 'm1', text = 'earlier error') {
            const ticket = feedback.begin({region: 'global', operation,
                target: operation === 'combatant.reset' ? JSON.stringify([kind, id]) : 'battle', label: operation});
            feedback.publish(ticket, {severity: 'error', text});
        }});
    return f;
}
function deferred() {let resolve, reject;
    const promise = new Promise((yes, no) => {resolve = yes; reject = no;});
    return {promise, resolve, reject};}
for (const [key, kind, id, name] of [['r', 'monsters', 'm1', 'Ogre'], ['cr', 'characters', 'c1', 'Ada']]) {
    test(`${kind}: explicit persistent failure uses target identity and unchanged request`, async () => {
        const f = fixture(); f.onRequest = async () => {throw new Error('denied');};
        await f.click({[key]: id});
        assert.equal(f.calls.length, 1); assert.equal(f.calls[0][0], `/api/combatants/${id}/reset`);
        assert.equal(f.calls[0][1].method, 'POST'); assert.deepEqual(Object.keys(f.calls[0][1]), ['method']);
        assert.equal(f.snapshot()[0].operation, 'combatant.reset');
        assert.equal(f.snapshot()[0].target, JSON.stringify([kind, id]));
        assert.ok(f.snapshot()[0].label.includes(name)); assert.equal(f.snapshot()[0].severity, 'error');
        assert.equal(f.timers.size, 0); assert.equal(f.refreshes(), 0);
    });
    test(`${kind}: actual failed request then matching retry resolves silently`, async () => {
        const f = fixture(); f.onRequest = async () => {throw new Error('failed');};
        await f.click({[key]: id}); f.onRequest = async () => ({}); await f.click({[key]: id});
        assert.equal(f.snapshot().length, 0); assert.equal(f.calls.length, 2);
        assert.equal(f.refreshes(), 1); assert.equal(f.timers.size, 0);
    });
}
test('resetting another monster or a character does not clear the first monster error', async () => {
    const f = fixture(); f.seed('combatant.reset'); await f.click({r: 'm2'}); await f.click({cr: 'c1'});
    assert.equal(f.snapshot().length, 1); assert.equal(f.snapshot()[0].target, JSON.stringify(['monsters','m1']));
});
test('same identifier in different kind has a distinct feedback target', async () => {
    const f = fixture(); f.seed('combatant.reset', 'monsters', 'same'); await f.click({cr: 'same'});
    assert.equal(f.snapshot().length, 1); assert.equal(f.snapshot()[0].target, JSON.stringify(['monsters','same']));
});
test('individual reset does not clear Reset All, End or state-load errors', async () => {
    const f = fixture(); for (const operation of ['battle.reset-all','battle.end','state.load']) f.seed(operation);
    await f.click({r: 'm1'}); assert.equal(f.snapshot().length, 3);
});
test('refresh alone does not clear an individual reset error', async () => {
    const f = fixture(); f.seed('combatant.reset'); await f.context.load(); assert.equal(f.snapshot().length, 1);
});
test('success resolves before actual loadState handles a refresh failure without retry', async () => {
    const f = fixture(); f.seed('combatant.reset'); f.onLoad = () => {
        assert.equal(f.snapshot().length, 0);
        return f.feedback.loadState(() => {f.feedback.stateRequest(); return Promise.reject(new Error('refresh'));}, () => {});
    }; await f.click({r: 'm1'});
    assert.equal(f.calls.length, 1); assert.equal(f.snapshot().length, 1);
    assert.equal(f.snapshot()[0].operation, 'state.load');
});
test('old-setup success does not clear a new error or refresh the new setup', async () => {
    const f = fixture(), p = deferred(); f.onRequest = () => p.promise;
    const done = f.click({r:'m1'}); f.scope('a','two'); f.seed('combatant.reset'); p.resolve({}); await done;
    assert.equal(f.snapshot().length, 1); assert.equal(f.refreshes(), 0);
});
test('old-campaign failure cannot publish into the new campaign', async () => {
    const f = fixture(), p = deferred(); f.onRequest = () => p.promise;
    const done = f.click({cr:'c1'}); f.scope('b'); p.reject(new Error('old')); await done;
    assert.equal(f.snapshot().length, 0); assert.equal(f.refreshes(), 0);
});
test('switching away and back does not revive an old reset attempt', async () => {
    const f = fixture(), p = deferred(); f.onRequest = () => p.promise;
    const done = f.click({r:'m1'}); f.scope('b'); f.scope(); p.resolve({}); await done;
    assert.equal(f.snapshot().length, 0); assert.equal(f.refreshes(), 0);
});
test('superseded success cannot clear a newer failure for the same target', async () => {
    const f = fixture(), p = deferred(); let n = 0;
    f.onRequest = () => ++n === 1 ? p.promise : Promise.reject(new Error('new'));
    const old = f.click({r:'m1'}); await f.click({r:'m1'}); p.resolve({}); await old;
    assert.equal(f.snapshot()[0].text, 'new'); assert.equal(f.refreshes(), 0);
});
test('concurrent different-target resets remain independent', async () => {
    const f = fixture(), p = deferred(); let n = 0;
    f.onRequest = () => ++n === 1 ? p.promise : Promise.reject(new Error('second target'));
    const first = f.click({r:'m1'}); await f.click({r:'m2'}); p.resolve({}); await first;
    assert.equal(f.snapshot().length, 1); assert.equal(f.snapshot()[0].text, 'second target'); assert.equal(f.refreshes(), 1);
});
test('URI encoding and submitted name are captured before a response', async () => {
    const f = fixture(); f.context.latest.monsters.push({id:'a/b ?',name:'Old name'});
    f.onRequest = async () => {f.context.latest.monsters.at(-1).name = 'New name'; throw new Error('failed');};
    await f.click({r:'a/b ?'}); assert.equal(f.calls[0][0], '/api/combatants/a%2Fb%20%3F/reset');
    assert.equal(f.snapshot()[0].label, 'Reset monster: Old name');
});
test('existing remove/edit/action and earlier patch branches keep their precedence', async () => {
    const f = fixture(); await f.click({removeKind:'monsters',removeId:'m1',r:'m1'});
    await f.click({battleActor:'m1',r:'m1'}); await f.click({edit:'m1',kind:'monsters',r:'m1'});
    await f.click({ma:'m1',r:'m1'});
    assert.equal(f.calls.length, 0); assert.equal(f.other.length, 3); assert.equal(f.patches.length, 1);
});
test('unexpected load rejection is not recast as an individual reset request failure', async () => {
    const f = fixture(); f.seed('combatant.reset'); f.onLoad = async () => {throw new Error('refresh');};
    await assert.rejects(f.click({r:'m1'}), /refresh/); assert.equal(f.snapshot().length, 0); assert.equal(f.calls.length, 1);
});
