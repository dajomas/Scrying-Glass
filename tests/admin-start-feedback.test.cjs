'use strict';
const assert = require('node:assert/strict');
const {test} = require('node:test');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {createController} = require('../static/admin-feedback-controller.js');
const source = fs.readFileSync(path.join(__dirname, '../static/admin-initial-visibility.js'), 'utf8');
const deferred = () => {
    let resolve, reject;
    const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
    return {promise, resolve, reject};
};
function fixture() {
    const timers = [], calls = [], pending = [], events = [];
    const controller = createController({setTimeout: (fn, ms) => { timers.push({fn, ms}); return timers.length; }, clearTimeout() {}});
    let scope = 'encounter-a';
    controller.setScope('encounter', scope);
    // Only the bootstrap's destination/default adapter is mocked, not the controller.
    const feedback = {...controller, begin(spec) {
        return controller.begin({...spec, lane:'encounter', scope, placement:'global'});
    }};
    const context = {document:{getElementById: () => null}, startBattle: async () => {},
        scryingAdminFeedback:feedback,
        request(url, options) { events.push('request'); calls.push({url, options});
            const task = deferred(); pending.push(task); return task.promise; },
        setAllHideablePanesHidden(value) { events.push('collapse'); assert.equal(value, true); },
        load: async () => { events.push('load'); },
        message() { throw new Error('Legacy feedback must not be used'); }};
    context.window = context;
    vm.createContext(context); vm.runInContext(source, context);
    return {context, controller, feedback, calls, pending, events, timers,
        switchScope(value) { scope = value; controller.setScope('encounter', scope); },
        emit(operation, text) { const ticket = feedback.begin({region:'global', operation, target:'battle', label:operation});
            controller.publish(ticket, {severity:'error', text}); },
        records: () => controller.snapshot().map(r => ({operation:r.operation,text:r.text,severity:r.severity})),
        reinstall() { vm.runInContext(source, context); }};
}
test('Start keeps URL, method, JSON payload and undefined result; success collapses then refreshes', async () => {
    const f = fixture(); const order = ['one','two'];
    const result = f.context.startBattle(order);
    assert.equal(f.calls.length, 1);
    assert.equal(f.calls[0].url, '/api/battle/start');
    assert.equal(f.calls[0].options.method, 'POST');
    assert.equal(f.calls[0].options.headers['Content-Type'], 'application/json');
    assert.deepEqual(JSON.parse(f.calls[0].options.body), {order});
    assert.deepEqual(f.events, ['request']);
    f.pending[0].resolve({}); assert.equal(await result, undefined);
    assert.deepEqual(f.events, ['request','collapse','load']); assert.deepEqual(f.records(), []);
});
test('request failure is persistent, explicit and leaves panes/refresh untouched', async () => {
    const f = fixture(); const task = f.context.startBattle([]);
    f.pending[0].reject(new Error('Rejected start'));
    assert.equal(await task, undefined);
    assert.deepEqual(f.events, ['request']); assert.equal(f.calls.length, 1);
    assert.deepEqual(f.records(), [{operation:'battle.start',text:'Rejected start',severity:'error'}]);
    assert.equal(f.timers.length, 0);
});
test('matching successful retry resolves only Start error, before refreshing', async () => {
    const f = fixture(); let task = f.context.startBattle([]);
    f.pending[0].reject(new Error('Start failure')); await task;
    f.emit('other.operation', 'Keep this');
    f.context.load = async () => { assert.deepEqual(f.records().map(r=>r.operation), ['other.operation']); };
    task = f.context.startBattle(['x']); f.pending[1].resolve({}); await task;
    assert.deepEqual(f.records().map(r=>r.text), ['Keep this']); assert.equal(f.calls.length, 2);
});
test('an unrelated success does not resolve a Start error', async () => {
    const f = fixture(); const task = f.context.startBattle([]);
    f.pending[0].reject(new Error('Keep Start error')); await task;
    const ticket = f.feedback.begin({region:'global',operation:'other',target:'battle',label:'Other'});
    f.controller.resolve(ticket);
    assert.deepEqual(f.records().map(r=>r.operation), ['battle.start']);
});
test('repeated failure replaces the related notice rather than duplicating it', async () => {
    const f = fixture();
    for (let i=0;i<2;i++) { const task=f.context.startBattle([]); f.pending[i].reject(new Error('Failure '+i)); await task; }
    assert.deepEqual(f.records(), [{operation:'battle.start',text:'Failure 1',severity:'error'}]);
});
test('older failure cannot overwrite a newer request failure', async () => {
    const f=fixture(); const older=f.context.startBattle([]), newer=f.context.startBattle([]);
    f.pending[1].reject(new Error('New failure')); await newer;
    f.pending[0].reject(new Error('Old failure')); await older;
    assert.deepEqual(f.records().map(r=>r.text), ['New failure']);
});
test('older success cannot clear a newer failure or collapse/refresh its view', async () => {
    const f=fixture(); const older=f.context.startBattle([]), newer=f.context.startBattle([]);
    f.pending[1].reject(new Error('New failure')); await newer;
    f.pending[0].resolve({}); await older;
    assert.deepEqual(f.records().map(r=>r.text), ['New failure']);
    assert.deepEqual(f.events, ['request','request']);
});
test('old-scope failure cannot publish in the new encounter', async () => {
    const f=fixture(); const task=f.context.startBattle([]); f.switchScope('encounter-b');
    f.pending[0].reject(new Error('Old encounter')); await task;
    assert.deepEqual(f.records(), []); assert.deepEqual(f.events, ['request']);
});
test('old-scope success cannot collapse or refresh the new encounter', async () => {
    const f=fixture(); const task=f.context.startBattle([]); f.switchScope('encounter-b');
    f.pending[0].resolve({}); await task;
    assert.deepEqual(f.records(), []); assert.deepEqual(f.events, ['request']);
});
test('scope A-B-A still rejects the old request via epoch', async () => {
    const f=fixture(); const task=f.context.startBattle([]);
    f.switchScope('encounter-b'); f.switchScope('encounter-a');
    f.pending[0].reject(new Error('Old epoch')); await task;
    assert.deepEqual(f.records(), []);
});
test('successful Start followed by handled refresh failure retains only state.load error, no retry', async () => {
    const f=fixture(); let task=f.context.startBattle([]);
    f.pending[0].reject(new Error('Earlier Start failure')); await task;
    f.context.load=async () => { f.events.push('load'); f.emit('state.load', 'Refresh failed'); };
    task=f.context.startBattle([]); f.pending[1].resolve({}); await task;
    assert.deepEqual(f.records(), [{operation:'state.load',text:'Refresh failed',severity:'error'}]);
    assert.equal(f.calls.length, 2); assert.deepEqual(f.events, ['request','request','collapse','load']);
});
test('duplicate asset installation preserves the installed wrapper', async () => {
    const f=fixture(), handler=f.context.startBattle; f.reinstall(); assert.equal(f.context.startBattle, handler);
    const task=f.context.startBattle([]); f.pending[0].resolve({}); await task; assert.equal(f.calls.length, 1);
});
