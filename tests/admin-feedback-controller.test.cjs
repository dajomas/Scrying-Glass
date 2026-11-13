const {test} = require('node:test');
const assert = require('node:assert/strict');
const {createController} = require('../static/admin-feedback-controller.js');
function fixture() {
    let now = 0, id = 0;
    const timers = new Map(), callbacks = [];
    const c = createController({
        setTimeout(fn, delay) { const key = ++id; timers.set(key, {fn, at: now + delay}); callbacks.push(fn); return key; },
        clearTimeout(key) { timers.delete(key); }
    });
    c.setScope('encounter', 'campaign-a/setup-a');
    const spec = {lane: 'encounter', scope: 'campaign-a/setup-a', operation: 'monster.edit', target: 'm1',
        region: 'monsters', placement: 'pane', label: 'Save monster'};
    function advance(ms) {
        const until = now + ms;
        while (true) {
            const next = [...timers].filter(([, t]) => t.at <= until).sort((a, b) => a[1].at - b[1].at)[0];
            if (!next) break;
            now = next[1].at; timers.delete(next[0]); next[1].fn();
        }
        now = until;
    }
    return {c, spec, timers, callbacks, advance, begin: extra => c.begin({...spec, ...extra})};
}
test('pane success expires at exactly three seconds', () => {
    const f = fixture(); f.c.publish(f.begin(), {severity: 'success', text: 'Saved'});
    f.advance(2999); assert.equal(f.c.snapshot().length, 1);
    f.advance(1); assert.equal(f.c.snapshot().length, 0); assert.equal(f.timers.size, 0);
});
test('global success expires at exactly five seconds', () => {
    const f = fixture(); f.c.publish(f.begin({placement: 'global', region: 'message'}), {severity: 'success', text: 'Ended'});
    f.advance(4999); assert.equal(f.c.snapshot().length, 1);
    f.advance(1); assert.equal(f.c.snapshot().length, 0);
});
test('actionable errors have no automatic expiry', () => {
    const f = fixture(); f.c.publish(f.begin(), {severity: 'error', text: 'Choose a valid value'});
    f.advance(60000); assert.equal(f.c.snapshot()[0].severity, 'error'); assert.equal(f.timers.size, 0);
});
test('severity is explicit and never inferred from wording', () => {
    const f = fixture();
    f.c.publish(f.begin(), {severity: 'success', text: 'Error is merely quoted here'});
    f.advance(3000); assert.equal(f.c.snapshot().length, 0);
    f.c.publish(f.begin(), {severity: 'error', text: 'Saved is merely quoted here'});
    f.advance(3000); assert.equal(f.c.snapshot()[0].severity, 'error');
});
test('missing or invalid metadata fails before changing state', () => {
    const f = fixture();
    for (const field of ['lane','scope','operation','target','region','label','placement'])
        assert.throws(() => f.begin({[field]: ''}));
    const ticket = f.begin();
    assert.throws(() => f.c.publish(ticket, {text: 'No severity'}));
    assert.throws(() => f.c.publish(ticket, {severity: 'notice', text: 'Not a supported category'}));
    assert.throws(() => f.begin({field: ' '}));
    assert.throws(() => f.c.publish(ticket, {severity: 'error', text: ' '}));
    assert.equal(f.c.snapshot().length, 0);
    assert(f.c.publish(ticket, {severity: 'error', text: 'Still usable'}));
});
test('scope must be activated explicitly', () => {
    const f = fixture(); assert.throws(() => f.begin({scope: 'other'}));
    assert.throws(() => f.begin({lane: 'unknown'}));
});
test('beginning retry preserves old error until a relevant outcome', () => {
    const f = fixture(); const id = f.c.publish(f.begin(), {severity: 'error', text: 'Failed'});
    const retry = f.begin(); assert.equal(f.c.snapshot()[0].id, id);
    f.c.publish(retry, {severity: 'info', text: 'Retrying'});
    assert.deepEqual(f.c.snapshot().map(x => x.severity), ['error','info']);
    f.c.publish(retry, {severity: 'success', text: 'Saved'});
    assert.deepEqual(f.c.snapshot().map(x => x.severity), ['success']);
});
test('unrelated success does not remove error in same pane', () => {
    const f = fixture(); const id = f.c.publish(f.begin(), {severity: 'error', text: 'Edit failed'});
    f.c.publish(f.begin({operation: 'monster.create'}), {severity: 'success', text: 'Added'});
    assert.equal(f.c.snapshot().length, 2); f.advance(3000);
    assert.equal(f.c.snapshot()[0].id, id);
});
test('targets and operations remain distinct even for identical text', () => {
    const f = fixture();
    for (const target of ['m1','m2']) f.c.publish(f.begin({target}), {severity: 'error', text: 'Failure'});
    f.c.resolve(f.begin({target: 'm1'}));
    assert.equal(f.c.snapshot().length, 1); assert.equal(f.c.snapshot()[0].target, 'm2');
});
test('silent successful retry resolves only its related error', () => {
    const f = fixture();
    f.c.publish(f.begin(), {severity: 'error', text: 'Edit failed'});
    const other = f.c.publish(f.begin({operation: 'monster.create'}), {severity: 'error', text: 'Create failed'});
    assert.equal(f.c.resolve(f.begin()), true);
    assert.equal(f.c.snapshot().length, 1); assert.equal(f.c.snapshot()[0].id, other);
});
test('new failed retry replaces only the related old result', () => {
    const f = fixture(); const first = f.c.publish(f.begin(), {severity: 'error', text: 'First'});
    f.c.publish(f.begin(), {severity: 'error', text: 'Second'});
    assert.equal(f.c.snapshot().length, 1); assert.notEqual(f.c.snapshot()[0].id, first);
});
test('older response cannot overwrite a newer attempt', () => {
    const f = fixture(); const first = f.begin(), second = f.begin();
    assert.equal(f.c.publish(first, {severity: 'error', text: 'Stale'}), false);
    const id = f.c.publish(second, {severity: 'error', text: 'Current'});
    assert.equal(f.c.resolve(first), false); assert.equal(f.c.snapshot()[0].id, id);
});
test('terminal tickets cannot publish twice or later resolve newer feedback', () => {
    const f = fixture(), ticket = f.begin();
    f.c.publish(ticket, {severity: 'success', text: 'Saved'});
    assert.equal(f.c.publish(ticket, {severity: 'error', text: 'Late duplicate'}), false);
    assert.equal(f.c.resolve(ticket), false);
});
test('cancelled old timer callback cannot clear replacement error', () => {
    const f = fixture(); f.c.publish(f.begin(), {severity: 'success', text: 'Saved'});
    const callback = f.callbacks[0];
    const id = f.c.publish(f.begin(), {severity: 'error', text: 'New failure'});
    callback(); assert.equal(f.c.snapshot()[0].id, id);
});
test('scope change invalidates old timers and old responses', () => {
    const f = fixture(); f.c.publish(f.begin(), {severity: 'success', text: 'Old success'});
    const stale = f.begin(), oldTimer = f.callbacks[0];
    f.c.setScope('encounter', 'campaign-b/setup-b');
    assert.equal(f.c.snapshot().length, 0); assert.equal(f.timers.size, 0);
    const id = f.c.publish(f.begin({scope: 'campaign-b/setup-b'}), {severity: 'error', text: 'New scope'});
    oldTimer(); assert.equal(f.c.publish(stale, {severity: 'error', text: 'Stale'}), false);
    assert.equal(f.c.resolve(stale), false); assert.equal(f.c.snapshot()[0].id, id);
});
test('A to B to A does not revive a ticket from the first A', () => {
    const f = fixture(), stale = f.begin();
    f.c.setScope('encounter', 'b'); f.c.setScope('encounter', f.spec.scope);
    assert.equal(f.c.publish(stale, {severity: 'error', text: 'Old A'}), false);
});
test('same-scope refresh does not invalidate tickets or clear feedback', () => {
    const f = fixture(), ticket = f.begin();
    assert.equal(f.c.setScope('encounter', f.spec.scope), false);
    assert(f.c.publish(ticket, {severity: 'error', text: 'Still current'}));
    assert.equal(f.c.setScope('encounter', f.spec.scope), false); assert.equal(f.c.snapshot().length, 1);
});
test('viewer lane remains separate from encounter scope changes', () => {
    const f = fixture(); f.c.setScope('viewer-grants', 'selected-campaign-z');
    const viewer = f.begin({lane: 'viewer-grants', scope: 'selected-campaign-z', region: 'viewer', operation: 'grants.save'});
    const id = f.c.publish(viewer, {severity: 'error', text: 'Viewer save failed'});
    f.c.setScope('encounter', 'another-encounter'); assert.equal(f.c.snapshot()[0].id, id);
});
test('operation may resolve an old related destination after intentional routing change', () => {
    const f = fixture(); f.c.publish(f.begin({region: 'old-region'}), {severity: 'error', text: 'Failed'});
    f.c.publish(f.begin({region: 'new-region'}), {severity: 'success', text: 'Saved'});
    assert.deepEqual(f.c.snapshot().map(x => x.region), ['new-region']);
});
test('progress updates replace progress only, not existing error', () => {
    const f = fixture(); const id = f.c.publish(f.begin(), {severity: 'error', text: 'Failure'});
    const retry = f.begin();
    f.c.publish(retry, {severity: 'info', text: 'Step one'}); f.c.publish(retry, {severity: 'info', text: 'Step two'});
    assert.equal(f.c.snapshot().length, 2); assert.equal(f.c.snapshot()[0].id, id);
});
test('dismissal is record-specific and cancels only its timer', () => {
    const f = fixture(); const error = f.c.publish(f.begin(), {severity: 'error', text: 'Failure'});
    const success = f.c.publish(f.begin({target: 'm2'}), {severity: 'success', text: 'Saved'});
    assert.equal(f.c.dismiss(success), true); assert.equal(f.timers.size, 0);
    assert.equal(f.c.snapshot()[0].id, error); assert.equal(f.c.dismiss(success), false);
});
test('snapshots and records are immutable and ticket forgery fails', () => {
    const f = fixture(), ticket = f.begin();
    assert.equal(f.c.publish({...ticket}, {severity: 'error', text: 'Forged'}), false);
    f.c.publish(ticket, {severity: 'error', text: 'Real'});
    assert(Object.isFrozen(f.c.snapshot())); assert(Object.isFrozen(f.c.snapshot()[0]));
});
test('subscription and unsubscription expose current state without later callbacks', () => {
    const f = fixture(), seen = [], unsubscribe = f.c.subscribe(items => seen.push(items.length));
    f.c.publish(f.begin(), {severity: 'error', text: 'Failure'}); unsubscribe(); f.c.resolve(f.begin());
    assert.deepEqual(seen, [0,1]);
});
test('reentrant mutation does not send an older snapshot after a newer one', () => {
    const f = fixture(), seen = [];
    f.c.subscribe(items => { if (items.some(x => x.text === 'Remove me')) f.c.dismiss(items[0].id); });
    f.c.subscribe(items => seen.push(items.map(x => x.text)));
    f.c.publish(f.begin(), {severity: 'error', text: 'Remove me'});
    assert.deepEqual(seen, [[],[]]);
});
test('dispose clears timers and views, and stale timer callbacks are harmless', () => {
    const f = fixture(); f.c.publish(f.begin(), {severity: 'success', text: 'Saved'});
    const timer = f.callbacks[0], seen = []; f.c.subscribe(items => seen.push(items.length));
    f.c.dispose(); timer(); f.c.dispose();
    assert.deepEqual(seen, [1,0]); assert.equal(f.timers.size, 0); assert.equal(f.c.snapshot().length, 0);
    assert.throws(() => f.begin());
});
// SG-TODO-009.7 Deliverable 2: warning severity and explicit field association.
test('warning persists without a timer and is replaced or resolved by its own identity', () => {
    const f = fixture();
    f.c.publish(f.begin(), {severity: 'warning', text: 'Connection lost'});
    assert.equal(f.timers.size, 0); f.advance(600000);
    assert.deepEqual(f.c.snapshot().map(x => [x.severity, x.text]), [['warning', 'Connection lost']]);
    const other = f.begin({operation: 'other'}); f.c.publish(other, {severity: 'success', text: 'Unrelated'});
    f.c.resolve(f.begin({operation: 'other'}));
    assert.deepEqual(f.c.snapshot().map(x => x.severity), ['warning']);
    f.c.publish(f.begin(), {severity: 'warning', text: 'Still lost'});
    assert.deepEqual(f.c.snapshot().map(x => x.text), ['Still lost']);
    f.c.resolve(f.begin()); assert.equal(f.c.snapshot().length, 0);
});
test('an explicit field selector is carried on the ticket and record; omitted otherwise', () => {
    const f = fixture();
    const plain = f.begin(); assert.equal(Object.hasOwn(plain, 'field'), false);
    assert.equal(Object.hasOwn(f.begin({field: null}), 'field'), false);
    const ticket = f.begin({field: '#name'});
    assert.equal(ticket.field, '#name');
    f.c.publish(ticket, {severity: 'error', text: 'Enter a name'});
    assert.equal(f.c.snapshot()[0].field, '#name');
    assert.throws(() => f.begin({field: 3}));
});
