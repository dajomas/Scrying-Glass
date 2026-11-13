// SG-TODO-009.7 / 4A.11 follow-up. Real feedback controller/bootstrap;
// mocked DOM and transport. Run through tools/run_split_tests.py in CI.
'use strict';
const assert = require('node:assert/strict');
const test = require('node:test');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {installFeedback} = require('./battle-action-feedback-fixture.cjs');
const read = file => fs.readFileSync(path.join(__dirname, '..', file), 'utf8');
const admin = read('static/admin/060-source.js') + read('static/admin/070-source.js');
const block = admin.slice(admin.indexOf('function activeBattleTargets()'),
    admin.indexOf('async function resetCombatantWithFeedback('));
const turn = read('static/battle-turn-actions.js');
const deferred = () => {let resolve; const promise = new Promise(r => {resolve = r;}); return {promise, resolve};};
function attach(ctx) {
    const timers = [];
    const api = installFeedback(ctx, {
        setTimeout(fn, delay) {const timer = {fn, delay}; timers.push(timer); return timer;},
        clearTimeout(timer) {timer.cancelled = true;},
    });
    return {...api, timers};
}
function core() {
    const ids = {}, requests = [], legacy = [];
    const rows = {children: [], appendChild(x) {this.children.push(x);},
        querySelectorAll() {return this.children;},
        set innerHTML(value) {this.children = [];}};
    function element() {
        const fields = {};
        const row = {dataset: {}, children: [], set innerHTML(html) {
            for (const key of ['target', 'kind', 'amount', 'critical', 'source', 'stat', 'remove-action-row']) {
                if (key === 'source' && !html.includes('data-action-source')) continue;
                fields[key] = {value: key === 'kind' ? (html.includes('value="reduce-stat"') ? 'reduce-stat' : 'damage') :
                    key === 'amount' ? '1' : key === 'stat' ? 'strength' : 'm',
                    checked: false, disabled: false, parentElement: {}, addEventListener() {}, closest() {return row;}};
            }
        }, querySelector(selector) {
            if (selector === '.amount-field') return {};
            return fields[selector === '[data-remove-action-row]' ? 'remove-action-row' : selector.slice(13, -1)] || null;
        }, querySelectorAll() {return Object.values(fields);}, appendChild(x) {this.children.push(x);},
        remove() {rows.children.splice(rows.children.indexOf(row), 1);}};
        return row;
    }
    const apply = {disabled: false, closest() {return null;}};
    const modal = {hidden: false, addEventListener() {}, setAttribute() {}, removeAttribute() {},
        querySelectorAll() {return [apply, ...rows.children.flatMap(row => row.querySelectorAll())];}};
    const form = {reportValidity() {return true;}, querySelector() {return apply;}};
    const ctx = {battleActionsApplying: false, battleActionActorId: 'm', battleStatisticsToken: 'token',
        battleActionRows: rows, battleActionModal: modal, battleActionForm: form,
        latest: {monsters: [], characters: [], lairs: [], statistics_token: 'token'},
        document: {createElement: element, querySelector: id => ids[id] ||= {}},
        message: text => legacy.push(text), esc: String,
        request: async (url, options) => {requests.push(JSON.parse(options.body)); return {applied: 1};},
        load: async () => {}, window: {}};
    const api = attach(ctx); vm.runInContext(block, ctx);
    const submit = () => form.onsubmit({preventDefault() {}});
    return {ctx, rows, ids, requests, legacy, submit, ...api};
}
const combatant = () => ({id: 'm', name: 'Mephit', active: true, alive: true, in_turn: true,
    hp: 8, max_hp: 10, temp_hp: 0});
function turnFixture() {
    const ids = {}, requests = [], legacy = [], observers = [];
    const control = (disabled = false) => ({disabled});
    const controls = [control(), control(true), control()];
    const form = {resets: 0, reset() {this.resets++;},
        addEventListener(type, fn) {this.submit = fn;}, querySelectorAll() {return controls.slice(0, 2);}};
    ids.battleActionModal = {hidden: false}; ids.battleActionRows = {querySelectorAll() {return [];}};
    ids.battleTurnEffectsForm = form; ids.battleActionForm = {querySelectorAll() {return controls.slice(2);}};
    for (const id of ['battleTurnDamage', 'battleTurnHealing', 'battleTurnNotice', 'battleTurnCombatant'])
        ids[id] = {value: '', textContent: ''};
    ids.battleTurnDamage.value = '2'; ids.battleTurnHealing.value = '1';
    let closeCount = 0, loadCount = 0;
    const refreshEntered = deferred();
    const ctx = {window: {}, battleActionActorId: 'm', latest: {monsters: [combatant()], characters: []},
        document: {readyState: 'complete', getElementById: id => ids[id]},
        MutationObserver: class {constructor(callback) {this.callback = callback; observers.push(this);} observe() {} disconnect() {}},
        request: async (url, options) => {requests.push({url, ...JSON.parse(options.body)}); if (ctx.requestWait) await ctx.requestWait;
            if (ctx.reject) throw new Error('Rejected');},
        load: async () => {loadCount++; refreshEntered.resolve(); if (ctx.refreshWait) await ctx.refreshWait;
            if (ctx.refreshReject) throw new Error('Offline'); if (ctx.afterLoad) ctx.afterLoad();},
        closeBattleActions() {closeCount++; ids.battleActionModal.hidden = true;},
        message: text => legacy.push(text)};
    const getter = ctx.document.getElementById;
    const api = attach(ctx); ctx.document.getElementById = getter;
    vm.runInContext(turn, ctx);
    return {ctx, ids, form, controls, requests, legacy, ...api, refreshEntered: refreshEntered.promise,
        submit: () => form.submit({preventDefault() {}}),
        sessionChange() {observers[1].callback();},
        get closeCount() {return closeCount;}, get loadCount() {return loadCount;}};
}
function unrelated(f) {
    const ticket = f.feedback.begin({region: 'global', operation: 'unrelated', target: 'other', label: 'Other operation'});
    f.feedback.publish(ticket, {severity: 'error', text: 'Keep this error'});
}

test('active-target failure is explicit persistent error, not legacy feedback', () => {
    const f = core(); f.ctx.addBattleActionRow();
    const record = f.feedback.snapshot()[0];
    assert.equal(record.operation, 'battle.actions.targets'); assert.equal(record.target, 'active');
    assert.equal(record.severity, 'error'); assert.match(record.text, /no active combatants/);
    assert.equal(f.timers.length, 0); assert.equal(f.rows.children.length, 0); assert.equal(f.legacy.length, 0);
});
test('living target failure is independent from active targets', () => {
    const f = core(); f.ctx.addBattleActionRow(); f.ctx.addStatisticsReductionRow();
    assert.deepEqual(f.feedback.snapshot().map(x => x.target).sort(), ['active', 'living']);
    f.ctx.latest.monsters = [{...combatant(), alive: false}]; f.ctx.addBattleActionRow();
    assert.equal(f.rows.children.length, 1); assert.equal(f.feedback.snapshot().length, 1);
    assert.equal(f.feedback.snapshot()[0].target, 'living');
    f.ctx.latest.monsters[0].alive = true; f.ctx.addStatisticsReductionRow();
    assert.equal(f.rows.children.length, 2); assert.equal(f.feedback.snapshot().length, 0);
});
test('repeated target failure replaces only its own record', () => {
    const f = core(); unrelated(f); f.ctx.addBattleActionRow(); f.ctx.addBattleActionRow();
    assert.equal(f.feedback.snapshot().length, 2);
    f.ctx.latest.monsters = [combatant()]; f.ctx.addBattleActionRow(true);
    assert.equal(f.feedback.snapshot().length, 1); assert.equal(f.feedback.snapshot()[0].operation, 'unrelated');
});
test('busy target handlers do not change feedback or rows', () => {
    const f = core(); f.ctx.addBattleActionRow(); const prior = f.feedback.snapshot();
    f.ctx.battleActionsApplying = true; f.ctx.latest.monsters = [combatant()];
    f.ctx.addBattleActionRow(); f.ctx.addStatisticsReductionRow();
    assert.deepEqual(f.feedback.snapshot(), prior); assert.equal(f.rows.children.length, 0);
});
test('no pending is scoped informational feedback and sends no mutation', async () => {
    const f = core(); await f.submit(); await f.submit();
    assert.equal(f.feedback.snapshot().length, 1); const record = f.feedback.snapshot()[0];
    assert.equal(record.severity, 'info'); assert.equal(record.operation, 'battle.actions.pending');
    assert.equal(record.target, 'm'); assert.equal(f.requests.length, 0); assert.equal(f.legacy.length, 0);
});
test('valid pending batch resolves matching info while preserving other errors and payload', async () => {
    const f = core(); unrelated(f); await f.submit(); f.ctx.latest.monsters = [combatant()];
    f.ctx.addBattleActionRow(); await f.submit();
    assert.equal(f.requests.length, 1); assert.equal(f.requests[0].actor_id, 'm');
    assert.equal(f.requests[0].actions[0].amount, 1); assert.equal(f.requests[0].actions[0].critical_hit, false);
    assert.equal(f.feedback.snapshot().length, 1); assert.equal(f.feedback.snapshot()[0].operation, 'unrelated');
});
test('ineligible completion publishes success for five seconds and preserves payload', async () => {
    const f = turnFixture(); f.ctx.afterLoad = () => {f.ctx.latest.monsters[0].in_turn = false;};
    await f.submit(); assert.equal(f.closeCount, 1); assert.equal(f.requests.length, 1);
    assert.deepEqual(f.requests[0], {url: '/api/battle/actions', actor_id: 'm', actions: [
        {target_id: 'm', action: 'damage', amount: 2, critical_hit: false},
        {target_id: 'm', action: 'heal', amount: 1, critical_hit: false}]});
    const record = f.feedback.snapshot()[0]; assert.equal(record.severity, 'success');
    assert.equal(record.operation, 'battle.actions.turn-completion'); assert.equal(record.target, 'm');
    assert.equal(f.timers[0].delay, 5000); assert.equal(f.legacy.length, 0);
    f.timers[0].fn(); assert.equal(f.feedback.snapshot().length, 0);
    assert.deepEqual(f.controls.map(x => x.disabled), [false, true, false]);
});
test('still eligible completion remains modal-local and preserves unrelated feedback', async () => {
    const f = turnFixture(); unrelated(f); await f.submit(); assert.equal(f.closeCount, 0);
    assert.equal(f.ids.battleTurnNotice.textContent, 'Start-of-turn changes applied.');
    assert.equal(f.feedback.snapshot().length, 1); assert.equal(f.feedback.snapshot()[0].operation, 'unrelated');
});
for (const mode of ['scope', 'session', 'actor']) {
    test(`stale ${mode} after request cannot refresh, close or publish completion`, async () => {
        const f = turnFixture(), pending = deferred(); f.ctx.requestWait = pending.promise;
        const result = f.submit();
        if (mode === 'scope') f.scope('other', 'encounter');
        if (mode === 'session') f.sessionChange();
        if (mode === 'actor') f.ctx.battleActionActorId = 'different';
        pending.resolve(); await result;
        assert.equal(f.loadCount, 0); assert.equal(f.closeCount, 0); assert.equal(f.feedback.snapshot().length, 0);
        assert.deepEqual(f.controls.map(x => x.disabled), [false, true, false]);
    });
}
test('scope changing during refresh suppresses completion and closing', async () => {
    const f = turnFixture(), pending = deferred(); f.ctx.refreshWait = pending.promise;
    const result = f.submit(); await f.refreshEntered; f.scope('new', 'scope'); pending.resolve(); await result;
    assert.equal(f.loadCount, 1); assert.equal(f.closeCount, 0); assert.equal(f.feedback.snapshot().length, 0);
});
test('request rejection remains local, restores controls and never replays automatically', async () => {
    const f = turnFixture(); f.ctx.reject = true; await f.submit();
    assert.equal(f.ids.battleTurnNotice.textContent, 'Rejected'); assert.equal(f.requests.length, 1);
    assert.equal(f.loadCount, 0); assert.equal(f.feedback.snapshot().length, 0);
    assert.deepEqual(f.controls.map(x => x.disabled), [false, true, false]);
});
test('applied mutation with refresh rejection remains distinct and is not replayed', async () => {
    const f = turnFixture(); f.ctx.refreshReject = true; await f.submit();
    assert.match(f.ids.battleTurnNotice.textContent, /were applied, but refresh failed: Offline/);
    assert.equal(f.requests.length, 1); assert.equal(f.closeCount, 0); assert.equal(f.feedback.snapshot().length, 0);
});
test('duplicate submit during mutation sends one request', async () => {
    const f = turnFixture(), pending = deferred(); f.ctx.requestWait = pending.promise;
    const result = f.submit(); await f.submit(); assert.equal(f.requests.length, 1);
    pending.resolve(); await result;
});
test('zero input and invalid actor remain local and send no request', async () => {
    const f = turnFixture(); f.ids.battleTurnDamage.value = ''; f.ids.battleTurnHealing.value = '0';
    await f.submit(); assert.match(f.ids.battleTurnNotice.textContent, /greater than zero/);
    f.ctx.latest.monsters[0].active = false; await f.submit();
    assert.match(f.ids.battleTurnNotice.textContent, /current active combatant/);
    assert.equal(f.requests.length, 0); assert.equal(f.feedback.snapshot().length, 0);
});
