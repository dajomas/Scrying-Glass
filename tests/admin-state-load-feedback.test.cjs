// Production request/load slices with real feedback control; not a full Admin browser.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ROOT = path.resolve(__dirname, '..');
const read = p => fs.readFileSync(path.join(ROOT, p), 'utf8');
const requestSource = read('static/admin/010-source.js').split('async function request(')[1].split('\nfunction esc(')[0];
const core = read('static/admin/030-source.js').split('\nconst hideablePanes =')[0];
const {createController} = require(path.join(ROOT, 'static/admin-feedback-controller.js'));
function state(campaign = 'a', battle = false) {
    return {active_campaign_id: campaign, active_setup: {campaign_id: campaign, name: 'setup'},
        monsters: [], characters: [], battle_order: battle ? ['c1'] : [], activity_log: []};
}
function fixture() {
    const pending = [], rendered = [], nodes = new Map(), timers = new Map();
    let timerId = 0, now = 0;
    const context = vm.createContext({console,
        ScryingFeedback: {createController: () => createController({
            setTimeout: (fn, delay) => {const id = ++timerId; timers.set(id, {fn, at: now + delay}); return id;},
            clearTimeout: id => timers.delete(id),
        })},
        document: {getElementById: () => null, querySelector: selector => {
            if (!nodes.has(selector)) nodes.set(selector, {});
            return nodes.get(selector);
        }},
        fetch: (url, options) => new Promise((resolve, reject) => pending.push({url, options, resolve, reject})),
        scryingStatisticsState: snapshot => rendered.push(snapshot),
        updateBattleOrderFontControls() {}, updateBattleRound() {}, syncActiveBattleSetupControls() {},
        renderActiveBattleSetup() {}, setBackgroundInputs() {}, renderActivityLog() {},
        updateBattleState() {}, updatePaneVisibilityForBattle() {},
        monsterRow: () => '', characterRow: () => '', all: () => [],
    });
    context.window = context;
    vm.runInContext(read('static/admin-feedback-admin.js'), context);
    vm.runInContext('let latest;\nasync function request(' + requestSource + '\n' + core, context);
    const api = context.scryingAdminFeedback;
    api.observeState(state(), api.stateRequest());
    return {context, api, pending, rendered, nodes,
        load: flag => context.load(flag),
        latest: () => vm.runInContext('latest', context),
        respond(index, snapshot = state(), status = 200) {
            pending[index].resolve({ok: status < 400, status, statusText: '', json: async () => snapshot});
        },
        notice(operation, text = operation, severity = 'error') {
            api.publish(api.begin({region: 'global', operation, target: 'one', label: operation}), {severity, text});
        },
        advance(milliseconds) {
            now += milliseconds;
            for (const [id, timer] of [...timers]) if (timer.at <= now) {timers.delete(id); timer.fn();}
        },
    };
}
test('load error has explicit identity, persists and never uses the legacy route', async () => {
    const f = fixture(), p = f.load();
    f.respond(0, {detail: 'State unavailable'}, 503);
    assert.equal(await p, undefined);
    f.advance(10000);
    assert.equal(f.api.snapshot().length, 1);
    const notice = f.api.snapshot()[0];
    assert.equal(notice.operation, 'state.load');
    assert.equal(notice.severity, 'error');
    assert.equal(notice.text, 'State unavailable');
    assert.equal(f.api.snapshot().filter(r=>String(r.operation).startsWith('legacy.')).map(r=>r.region).length, 0);
});
test('matching retry clears only load error, including the no-battle early return', async () => {
    const f = fixture();
    let p = f.load(); f.respond(0, {detail: 'Load failed'}, 503); await p;
    f.notice('independent.edit');
    p = f.load(); f.respond(1); assert.equal(await p, undefined);
    assert.deepEqual(f.api.snapshot().map(n => n.operation), ['independent.edit']);
    assert.equal(f.nodes.get('#battleInfo').textContent, 'No battle order set');
});
test('unrelated success does not clear the load error', async () => {
    const f = fixture(), p = f.load(); f.respond(0, {detail: 'Load failed'}, 503); await p;
    f.notice('independent.save', 'Saved', 'success'); f.advance(5000);
    assert.deepEqual(f.api.snapshot().map(n => n.operation), ['state.load']);
});
test('retry failure replaces the related error instead of duplicating it', async () => {
    const f = fixture();
    for (const text of ['First failure', 'Second failure']) {
        const p = f.load(); f.respond(f.pending.length - 1, {detail: text}, 503); await p;
    }
    assert.equal(f.api.snapshot().length, 1);
    assert.equal(f.api.snapshot()[0].text, 'Second failure');
});
test('out-of-order success cannot restore latest, scope or feedback', async () => {
    const f = fixture(), first = f.load(), second = f.load();
    f.respond(1, state('new')); await second; f.notice('new.scope.error');
    f.respond(0, state('old')); await first;
    assert.equal(f.latest().active_campaign_id, 'new');
    assert.equal(f.rendered.length, 1);
    assert.equal(JSON.parse(f.api.snapshot()[0].scope)[0], 'new');
});
test('old success cannot clear a newer failed load', async () => {
    const f = fixture(), first = f.load(), second = f.load();
    f.respond(1, {detail: 'New failure'}, 503); await second;
    f.respond(0); await first;
    assert.equal(f.api.snapshot()[0].text, 'New failure');
    assert.equal(f.rendered.length, 0);
});
test('old failure cannot replace feedback after newer success', async () => {
    const f = fixture(), first = f.load(), second = f.load();
    f.respond(1); await second; f.notice('independent.error');
    f.respond(0, {detail: 'Old failure'}, 503); await first;
    assert.deepEqual(f.api.snapshot().map(n => n.operation), ['independent.error']);
});
test('a direct state request also supersedes a pending load', async () => {
    const f = fixture(), first = f.load(), direct = f.context.request('/api/state');
    f.respond(1, state('new')); await direct; f.notice('new.scope.error');
    f.respond(0, state('old')); await first;
    assert.equal(f.rendered.length, 0);
    assert.equal(JSON.parse(f.api.snapshot()[0].scope)[0], 'new');
});
test('scope change without another request rejects the pending old state', async () => {
    const f = fixture(), p = f.load();
    f.api.setScope('encounter', JSON.stringify(['new', null, null])); f.notice('new.scope.error');
    f.respond(0, state('old')); await p;
    assert.equal(f.rendered.length, 0);
    assert.equal(JSON.parse(f.api.snapshot()[0].scope)[0], 'new');
});
test('accepted transition rebinds render errors to the new scope', async () => {
    const f = fixture();
    const original = new Error('Render failed');
    f.context.updateBattleState = () => {throw original;};
    const p = f.load(true); f.respond(0, state('new'));
    await assert.rejects(p, error => error === original);
    assert.equal(JSON.parse(f.api.snapshot()[0].scope)[0], 'new');
    assert.equal(f.api.snapshot()[0].text, 'Render failed');
});
test('load(true) rethrows the original network error; default load swallows it', async () => {
    const f = fixture(), error = new Error('Network down');
    let p = f.load(true); f.pending[0].reject(error);
    await assert.rejects(p, caught => caught === error);
    p = f.load(); f.pending[1].reject(error); assert.equal(await p, undefined);
});
test('stale load(true) still rethrows while suppressing its feedback', async () => {
    const f = fixture(), error = new Error('Old network failure');
    const first = f.load(true), second = f.load();
    f.respond(1); await second;
    f.pending[0].reject(error);
    await assert.rejects(first, caught => caught === error);
    assert.equal(f.api.snapshot().length, 0);
});
test('only literal true enables rethrowing', async () => {
    const f = fixture(), p = f.load('true');
    f.pending[0].reject(new Error('Failure'));
    assert.equal(await p, undefined);
});
test('active-battle success also resolves a related load failure', async () => {
    const f = fixture();
    let p = f.load(); f.respond(0, {detail: 'Load failed'}, 503); await p;
    p = f.load(); f.respond(1, state('a', true)); await p;
    assert.equal(f.api.snapshot().length, 0);
    assert.equal(f.rendered.length, 1);
});
test('invalid scope data cannot overwrite latest or silently resolve the error', async () => {
    const f = fixture(), p = f.load(); f.respond(0, {characters: [], monsters: []}); await p;
    assert.equal(f.rendered.length, 0);
    assert.equal(f.api.snapshot()[0].severity, 'error');
});
