const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../static/admin.js'), 'utf8');
const start = source.indexOf('function activeBattleTargets()');
const block = source.slice(start, source.indexOf("document.addEventListener('click', async event => {", start));
function fixture() {
    const ids = {}, requests = [], messages = [];
    const rows = {children: [], appendChild(x) {this.children.push(x);},
        querySelectorAll() {return this.children;},
        set innerHTML(value) {this.children = [];}};
    function element() {
        const fields = {};
        const row = {dataset: {}, children: [],
            set innerHTML(html) {
                for (const key of ['target', 'kind', 'amount', 'critical', 'source', 'remove-action-row']) {
                    if (key === 'source' && !html.includes('data-action-source')) continue;
                    fields[key] = {value: key === 'kind' ? 'damage' : key === 'amount' ? '1' : '',
                        checked: false, disabled: false, required: ['target', 'source'].includes(key),
                        parentElement: {}, addEventListener() {}, closest() {return row;}};
                }
            },
            querySelector(selector) {
                if (selector === '.amount-field') return {};
                const key = selector === '[data-remove-action-row]' ? 'remove-action-row'
                    : selector.slice('[data-action-'.length, -1);
                return fields[key] || null;
            },
            querySelectorAll() {return Object.values(fields);},
            appendChild(x) {this.children.push(x);},
            remove() {rows.children.splice(rows.children.indexOf(row), 1);}};
        return row;
    }
    const button = () => ({disabled: false, closest() {return null;}});
    ids['#closeBattleActions'] = button();
    ids['#addBattleActionTarget'] = button(); ids['#addBattleReaction'] = button();
    const apply = button(), turn = button();
    const modal = {hidden: false, attributes: {}, addEventListener(type, fn) {this.click = fn;},
        querySelectorAll() {return [apply, turn, ...Object.values(ids).filter(x => 'disabled' in x),
            ...rows.children.flatMap(row => row.querySelectorAll())];},
        setAttribute(key, value) {this.attributes[key] = value;},
        removeAttribute(key) {delete this.attributes[key];}};
    const form = {querySelector() {return apply;}, reportValidity() {
        return rows.children.every(row => row.querySelectorAll().every(x =>
            x.disabled || !x.required || Boolean(x.value)));
    }};
    const ctx = {battleActionsApplying: false, battleActionActorId: 'm',
        battleActionRows: rows, battleActionForm: form, battleActionModal: modal,
        latest: {lairs: [], monsters: [{id:'m', name:'Monster', active:true, alive:true, in_turn:true}],
            characters:[{id:'c', name:'Character', active:true, alive:true}]},
        document: {createElement: element, querySelector: id => ids[id] ||= {}},
        message: x => messages.push(x), esc: String,
        request: async (url, options) => {
            const payload = JSON.parse(options.body); requests.push(payload);
            if (ctx.fail) throw new Error('Rejected');
            if (ctx.wait) await ctx.wait;
            return {applied: payload.actions.length};
        }, load: async () => {if (ctx.refreshFail) throw new Error('Offline');},
    };
    vm.runInNewContext(block, ctx);
    const add = (reaction = false, amount = 3) => {
        ctx.addBattleActionRow(reaction);
        const row = rows.children.at(-1);
        row.querySelector('[data-action-target]').value = 'c';
        row.querySelector('[data-action-amount]').value = String(amount);
        if (reaction) row.querySelector('[data-action-source]').value = 'm';
        return row;
    };
    return {ctx, rows, modal, form, ids, requests, messages, add, apply, turn,
        submit: () => form.onsubmit({preventDefault() {}})};
}
(async () => {
    const f = fixture(), a = f.add(), r = f.add(true, 7);
    a.querySelector('[data-action-critical]').checked = true;
    await f.submit();
    assert.equal(f.modal.hidden, false);
    assert.equal(f.requests.length, 1);
    assert.deepEqual(f.requests[0].actions.map(x => [x.source_id, x.amount, x.critical_hit]),
        [[null, 3, true], ['m', 7, false]]);
    for (const row of [a, r]) {
        assert.equal(row.dataset.applied, 'true');
        assert.equal(row.children[0].textContent, 'Applied');
        assert.ok(row.querySelectorAll().every(x => x.disabled));
    }
    assert.equal(f.apply.disabled, false);
    await f.submit(); assert.equal(f.requests.length, 1);
    f.add(true, 11); f.add(false, 5);
    await f.submit();
    assert.equal(f.requests.length, 2);
    assert.deepEqual(f.requests[1].actions.map(x => x.amount), [11, 5]);
    f.add(); f.ids['#closeBattleActions'].onclick();
    assert.equal(f.modal.hidden, true); assert.equal(f.rows.children.length, 0);
    assert.equal(f.requests.length, 2);
    f.ctx.openBattleActions('m');
    assert.equal(f.modal.hidden, false); assert.equal(f.rows.children.length, 1);
    assert.equal(f.rows.children[0].dataset.applied, undefined);
    assert.equal(f.ids['#battleActionNotice'].textContent, '');

    const kinds = fixture();
    const heal = kinds.add(true); heal.querySelector('[data-action-kind]').value = 'heal';
    heal.querySelector('[data-action-critical]').checked = true;
    const buff = kinds.add(); buff.querySelector('[data-action-kind]').value = 'buff';
    await kinds.submit();
    assert.equal(kinds.requests[0].actions[0].critical_hit, false);
    assert.equal(kinds.requests[0].actions[1].amount, null);
    kinds.ctx.latest.monsters[0].alive = false;
    kinds.add(true, 8); kinds.ctx.fail = true; await kinds.submit();
    kinds.ctx.fail = false; await kinds.submit();
    assert.equal(kinds.requests[2].actions.length, 1);
    assert.equal(kinds.requests[2].actions[0].amount, 8);

    const failed = fixture(), pending = failed.add(true);
    failed.ctx.fail = true; await failed.submit();
    assert.equal(pending.dataset.applied, undefined);
    assert.ok(pending.querySelectorAll().every(x => !x.disabled));
    failed.ctx.fail = false; await failed.submit();
    assert.equal(failed.requests.length, 2); assert.equal(pending.dataset.applied, 'true');

    const refresh = fixture(), resolved = refresh.add();
    refresh.ctx.refreshFail = true; await refresh.submit(); await refresh.submit();
    assert.equal(refresh.requests.length, 1); assert.equal(resolved.dataset.applied, 'true');
    assert.match(refresh.ids['#battleActionNotice'].textContent, /were applied, but refresh failed/);

    const busy = fixture(); busy.add(); let release;
    busy.ctx.wait = new Promise(resolve => {release = resolve;});
    const first = busy.submit(); await busy.submit();
    assert.equal(busy.requests.length, 1); assert.equal(busy.turn.disabled, true);
    assert.equal(busy.ids['#closeBattleActions'].disabled, true);
    busy.ctx.closeBattleActions(); busy.ctx.openBattleActions('m'); busy.ctx.addBattleActionRow();
    busy.modal.click({target: busy.modal});
    assert.equal(busy.modal.hidden, false); assert.equal(busy.rows.children.length, 1);
    release(); await first;
    assert.equal(busy.ctx.battleActionsApplying, false); assert.equal(busy.turn.disabled, false);
    assert.equal(busy.modal.attributes['aria-busy'], undefined);

    const validation = fixture(); validation.ctx.addBattleActionRow(true);
    await validation.submit(); assert.equal(validation.requests.length, 0);
    const empty = fixture(); await empty.submit(); assert.equal(empty.requests.length, 0);
    assert.match(empty.messages[0], /No pending/);
    const markup = fs.readFileSync(path.join(__dirname, '../templates/admin/180_battle_action_modal.html'), 'utf8');
    assert.match(markup, /type="button" id="closeBattleActions">Close/);
    assert.match(markup, /id="battleActionNotice" role="status" aria-live="polite"/);
    assert.doesNotMatch(markup, /cancelBattleActions/);
    console.log('Persistent modal tests passed: mixed ordered batches, skipped history, locking, close/reopen, rejection/retry, refresh failure, duplicate submissions, busy guards, validation and markup.');
})().catch(error => {console.error(error); process.exitCode = 1;});
