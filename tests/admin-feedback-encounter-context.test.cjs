const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const {createController} = require(path.join(root, 'static/admin-feedback-controller.js'));
const source = fs.readFileSync(path.join(root, 'static/admin-feedback-admin.js'), 'utf8');
function harness() {
    const controller = createController();
    const context = vm.createContext({window: {}, ScryingFeedback: {createController: () => controller},
        document: {getElementById: () => null}});
    vm.runInContext(source, context);
    const api = context.window.scryingAdminFeedback;
    const observe = (campaign, setup) => api.observeState({active_campaign_id: campaign,
        active_setup: setup ? {campaign_id: campaign, name: setup} : null}, api.stateRequest());
    return {api, context, observe};
}
test('encounter context starts with the existing uninitialized scope', () => {
    const {api} = harness();
    assert.equal(api.encounterContext().scope, JSON.stringify(['uninitialized']));
    assert.equal(api.encounterContext().epoch, 1);
});
test('context is a fresh immutable snapshot and cannot mutate feedback scope', () => {
    const {api, observe} = harness();
    const before = api.encounterContext();
    assert.ok(Object.isFrozen(before));
    assert.notEqual(api.encounterContext(), before);
    assert.equal(Reflect.set(before, 'scope', 'forged'), false);
    observe('campaign-a', 'setup-a');
    assert.equal(before.scope, JSON.stringify(['uninitialized']));
    assert.equal(api.encounterContext().scope, JSON.stringify(['campaign-a', 'campaign-a', 'setup-a']));
    assert.equal(api.encounterContext().epoch, before.epoch + 1);
});
test('same accepted scope does not advance its epoch', () => {
    const {api, observe} = harness();
    observe('a', 'one'); const before = api.encounterContext();
    assert.equal(observe('a', 'one'), true);
    assert.equal(api.encounterContext().epoch, before.epoch);
});
test('leaving and returning to the same identity advances the epoch twice', () => {
    const {api, observe} = harness();
    observe('a', 'one'); const before = api.encounterContext();
    observe('b', 'two'); observe('a', 'one');
    assert.equal(api.encounterContext().scope, before.scope);
    assert.equal(api.encounterContext().epoch, before.epoch + 2);
});
test('obsolete and invalid state observations cannot change context', () => {
    const {api, observe} = harness();
    observe('a', 'one'); const before = api.encounterContext();
    const old = api.stateRequest(); api.stateRequest();
    assert.equal(api.observeState({active_campaign_id: 'b', active_setup: null}, old), false);
    assert.equal(api.observeState({active_campaign_id: '', active_setup: null}, api.stateRequest()), false);
    assert.equal(api.encounterContext().scope, before.scope);
    assert.equal(api.encounterContext().epoch, before.epoch);
});
test('reading context preserves tickets, errors and page-lane feedback', () => {
    const {api, observe} = harness(); observe('a', 'one');
    const spec = {region: 'campaign', operation: 'fixture.read', target: 'one', label: 'Read'};
    const ticket = api.begin(spec);
    const page = api.begin({...spec, lane: 'page', operation: 'fixture.page'});
    api.publish(page, {severity: 'error', text: 'Keep independent error'});
    const before = api.snapshot()[0];
    for (let i = 0; i < 5; i++) api.encounterContext();
    assert.equal(api.isCurrent(ticket), true);
    assert.equal(api.snapshot()[0], before);
    observe('b', 'two');
    assert.equal(api.isCurrent(ticket), false);
    assert.equal(api.snapshot()[0], before);
});
test('lookup invalidation does not advance encounter context', () => {
    const {api, observe} = harness(); observe('a', 'one');
    const before = api.encounterContext(); api.invalidateLookup();
    assert.equal(api.encounterContext().scope, before.scope);
    assert.equal(api.encounterContext().epoch, before.epoch);
});
test('reloading the bootstrap retains the original API and context', () => {
    const {api, context, observe} = harness(); observe('a', 'one');
    const before = api.encounterContext(); vm.runInContext(source, context);
    assert.equal(context.window.scryingAdminFeedback, api);
    assert.equal(api.encounterContext().scope, before.scope);
    assert.equal(api.encounterContext().epoch, before.epoch);
});
test('header versions only the changed bootstrap and retains asset order', () => {
    const html = fs.readFileSync(path.join(root, 'templates/admin/010_pane_controls.html'), 'utf8');
    assert.equal((html.match(/admin-feedback-admin\.js\?v=2/g) || []).length, 1);
    assert.ok(!html.includes('admin-feedback-admin.js?v=1'));
    const order = ['admin-feedback-controller.js?v=1', 'admin-feedback-view.js?v=1',
        'admin-feedback-admin.js?v=2', 'initiative-join-gate.js'];
    for (let i = 1; i < order.length; i++) assert.ok(html.indexOf(order[i - 1]) < html.indexOf(order[i]));
});
