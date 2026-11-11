// 4A.13 bootstrap/producer isolation guard, not a full caller inventory or browser test.
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');
const {installFeedback} = require('./battle-action-feedback-fixture.cjs');
const read = name => fs.readFileSync(path.join(__dirname, '../static', name), 'utf8');
const operations = ['state.load', 'battle.start', 'battle.start.eligibility',
    'battle.start.tie-order', 'battle.next', 'battle.end', 'battle.end.validation',
    'battle.reset-all', 'combatant.reset', 'combatant.remove.fallback',
    'activity-log.clear', 'display.battle-order-font', 'battle.actions.eligibility',
    'battle.actions.targets', 'battle.actions.pending', 'battle.actions.turn-completion', 'roster.join',
    'statistics.open', 'campaign-bundle.import'];
function setup() {
    let now = 0, sequence = 0;
    const timers = new Map();
    const context = {document: {}};
    const {feedback, scope} = installFeedback(context, {
        setTimeout(fn, delay) {const id = ++sequence;timers.set(id, {fn, deadline: now + delay});return id;},
        clearTimeout(id) {timers.delete(id);},
    });
    const begin = (operation, target = 'same-target', region = 'global') =>
        feedback.begin({region, operation, target, label: operation});
    const error = (operation, target = 'same-target', region = 'global') =>
        feedback.publish(begin(operation, target, region), {severity: 'error', text: operation + ':' + target});
    return {context, feedback, scope, begin, error,
        tick(ms) {now += ms;for (const [id, item] of [...timers]) if (item.deadline <= now) {timers.delete(id);item.fn();}},
        texts: () => feedback.snapshot().map(record => record.text)};
}
test('every distinct operation pair isolates matching resolution through the real bootstrap', () => {
    let pairs = 0;
    for (let i = 0; i < operations.length; i++) for (let j = i + 1; j < operations.length; j++) {
        const w = setup(), a = operations[i], b = operations[j];
        w.error(a);w.error(b);w.tick(10000);
        assert.equal(w.feedback.snapshot().length, 2, `${a} / ${b}: persistent errors`);
        assert.equal(w.feedback.resolve(w.begin(a)), true);
        assert.deepEqual(w.texts(), [b + ':same-target'], `${a} must not clear ${b}`);
        assert.deepEqual(Array.from(w.feedback.legacyRegions()), []);pairs++;
    }
    assert.equal(pairs, 171);
});
test('same operation retains independent target failures', () => {
    const w = setup();w.error('roster.join', 'character-a');w.error('roster.join', 'character-b');
    w.feedback.resolve(w.begin('roster.join', 'character-a'));
    assert.deepEqual(w.texts(), ['roster.join:character-b']);
});
test('one success expires at five seconds without erasing another operation error', () => {
    const w = setup();w.error('combatant.reset');
    w.feedback.publish(w.begin('battle.end'), {severity: 'success', text: 'Ended'});
    w.tick(4999);assert.equal(w.feedback.snapshot().length, 2);
    w.tick(1);assert.deepEqual(w.texts(), ['combatant.reset:same-target']);
});
test('superseded tickets cannot overwrite or clear current failures', () => {
    const w = setup(), old = w.begin('battle.start');
    w.error('battle.start');w.error('battle.next');
    assert.equal(w.feedback.publish(old, {severity: 'success', text: 'Old'}), false);
    assert.equal(w.feedback.resolve(old), false);assert.equal(w.feedback.snapshot().length, 2);
});
test('away-and-back scope transitions cannot revive an old operation ticket', () => {
    const w = setup(), old = w.begin('battle.start');
    w.scope('elsewhere', 'other');w.scope();w.error('battle.end');
    assert.equal(w.feedback.publish(old, {severity: 'error', text: 'Old scope'}), false);
    assert.equal(w.feedback.resolve(old), false);assert.deepEqual(w.texts(), ['battle.end:same-target']);
});
test('retained pane compatibility cannot clear explicit pane or global errors', () => {
    const w = setup();w.error('roster.join');w.error('monster.edit', 'one', 'monsters');
    w.feedback.deliver('monsters', 'Legacy pane notice');w.feedback.deliver('monsters', '');
    assert.deepEqual(w.texts(), ['roster.join:same-target', 'monster.edit:one']);
    assert.deepEqual(Array.from(w.feedback.legacyRegions()), ['monsters']);
});
test('untyped global publish and clear reject without changing explicit feedback', () => {
    const w = setup();w.error('battle.start');
    for (const text of ['Unmigrated', '', '   ']) {
        assert.throws(() => w.feedback.deliver('global', text), /Global feedback requires an explicit ticket and severity/);
        assert.deepEqual(w.texts(), ['battle.start:same-target']);
        assert.deepEqual(Array.from(w.feedback.legacyRegions()), []);
    }
    const ticket = w.begin('battle.end');
    assert.equal(w.feedback.deliver('global', 'Explicit error', {ticket, severity: 'error'}), true);
    assert.deepEqual(w.texts(), ['battle.start:same-target', 'Explicit error']);
    assert.equal(w.feedback.resolve(ticket), true);
    assert.deepEqual(w.texts(), ['battle.start:same-target']);
});
test('actual End and Reset All producers preserve independent errors across explicit retry', async () => {
    const w = setup(), buttons = {endBattle: {}, resetAll: {}};
    const calls = [];let endFails = true;
    w.context.document.getElementById = id => buttons[id] || null;
    w.context.latest = {battle_order: ['actor']};w.context.confirm = () => true;
    w.context.request = async (url, options) => {
        calls.push({url, options});
        if (url.endsWith('/reset-all') || endFails) throw new Error(url.endsWith('/reset-all') ? 'Reset failed' : 'End failed');
        return {};
    };
    w.context.load = async () => {
        const snapshot = {active_campaign_id: 'fixture', active_setup: {campaign_id: 'fixture', name: 'setup'}};
        await w.feedback.loadState(() => {
            w.feedback.observeState(snapshot, w.feedback.stateRequest());return Promise.resolve(snapshot);
        }, () => {});
    };
    vm.runInContext(read('admin-end-feedback.js'), w.context);
    vm.runInContext(read('admin-reset-all-feedback.js'), w.context);
    await buttons.endBattle.onclick();await buttons.resetAll.onclick();
    assert.deepEqual(w.texts(), ['End failed', 'Reset failed']);
    endFails = false;await buttons.endBattle.onclick();
    assert.deepEqual(w.texts(), ['Reset failed', 'Battle ended. Combatants were not reset.']);
    w.tick(5000);assert.deepEqual(w.texts(), ['Reset failed']);
    assert.deepEqual(calls.map(call => call.url), ['/api/battle/end', '/api/battle/reset-all', '/api/battle/end']);
    assert(calls.every(call => call.options.method === 'POST'));
    assert.deepEqual(Array.from(w.feedback.legacyRegions()), []);
});
