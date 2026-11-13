// 4A.11 commit 1: reuse the real-controller legacy Apply fixture without its test IIFE.
'use strict';
const assert = require('node:assert/strict');
const test = require('node:test');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const fixtureSource = fs.readFileSync(path.join(__dirname, 'battle-action-apply.test.cjs'), 'utf8');
const boundary = fixtureSource.indexOf('(async () => {');
assert.ok(boundary > 0, 'Legacy fixture boundary is required');
const fixtureContext = {require, __dirname, console};
vm.runInNewContext(fixtureSource.slice(0, boundary), fixtureContext);
const make = () => fixtureContext.fixture();
const feedback = f => f.ctx.window.scryingAdminFeedback;
const noTargets = f => {f.ctx.latest.monsters = []; f.ctx.latest.characters = [];};
function unrelated(f) {
    const api = feedback(f);
    api.publish(api.begin({region: 'global', operation: 'unrelated', target: 'other', label: 'Other'}),
        {severity: 'error', text: 'Keep this error'});
}
test('active targets publish persistent explicit error without legacy feedback', () => {
    const f = make(); noTargets(f); f.ctx.addBattleActionRow();
    const records = feedback(f).snapshot();
    assert.equal(records.length, 1); assert.equal(records[0].operation, 'battle.actions.targets');
    assert.equal(records[0].target, 'active'); assert.equal(records[0].severity, 'error');
    assert.match(records[0].text, /no active combatants/);
    assert.equal(f.rows.children.length, 0); assert.equal(f.messages.length, 0);
});
test('active and living conditions resolve independently', () => {
    const f = make(); noTargets(f); f.ctx.addBattleActionRow(); f.ctx.addStatisticsReductionRow();
    assert.deepEqual(feedback(f).snapshot().map(x => x.target).sort(), ['active', 'living']);
    f.ctx.latest.monsters = [{id: 'm', name: 'Monster', active: true, alive: false}];
    f.ctx.addBattleActionRow(); assert.equal(f.rows.children.length, 1);
    assert.equal(feedback(f).snapshot().length, 1); assert.equal(feedback(f).snapshot()[0].target, 'living');
    f.ctx.latest.monsters[0].alive = true; f.ctx.addStatisticsReductionRow();
    assert.equal(f.rows.children.length, 2); assert.equal(feedback(f).snapshot().length, 0);
});
test('repeated failures replace only the matching target record', () => {
    const f = make(); noTargets(f); unrelated(f); f.ctx.addBattleActionRow(); f.ctx.addBattleActionRow();
    assert.equal(feedback(f).snapshot().length, 2);
    f.ctx.latest.characters = [{id: 'c', name: 'Character', active: true, alive: true}];
    f.ctx.addBattleActionRow(true); assert.equal(feedback(f).snapshot().length, 1);
    assert.equal(feedback(f).snapshot()[0].operation, 'unrelated');
});
test('busy target handlers leave records and rows unchanged', () => {
    const f = make(); noTargets(f); f.ctx.addBattleActionRow(); const prior = feedback(f).snapshot();
    f.ctx.battleActionsApplying = true;
    f.ctx.addBattleActionRow(); f.ctx.addStatisticsReductionRow();
    assert.deepEqual(feedback(f).snapshot(), prior); assert.equal(f.rows.children.length, 0);
});
test('no pending uses actor-specific info without requests or legacy messages', async () => {
    const f = make(); await f.submit(); await f.submit(); const records = feedback(f).snapshot();
    assert.equal(records.length, 1); assert.equal(records[0].operation, 'battle.actions.pending');
    assert.equal(records[0].target, 'm'); assert.equal(records[0].severity, 'info');
    assert.equal(f.requests.length, 0); assert.equal(f.messages.length, 0);
});
test('pending batch resolves matching info and preserves unrelated errors and payload', async () => {
    const f = make(); unrelated(f); await f.submit(); f.add(); await f.submit();
    assert.equal(f.requests.length, 1); assert.equal(f.requests[0].actor_id, 'm');
    assert.equal(f.requests[0].actions[0].amount, 3); assert.equal(f.requests[0].actions[0].critical_hit, false);
    assert.equal(feedback(f).snapshot().length, 1); assert.equal(feedback(f).snapshot()[0].operation, 'unrelated');
});
