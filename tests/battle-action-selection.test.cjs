const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../static/admin.js'), 'utf8');
const start = source.indexOf('function activeBattleTargets()');
const end = source.indexOf("document.addEventListener('click', async event => {", start);

function setup() {
    const controls = {};
    const rows = {
        children: [],
        appendChild(row) { this.children.push(row); },
        querySelectorAll() { return this.children; },
    };
    function makeRow() {
        const fields = {};
        return {
            className: '',
            set innerHTML(html) {
                this.html = html;
                for (const key of ['source', 'target']) {
                    const match = html.match(new RegExp(`<select data-action-${key} required>([^]*?)</select>`));
                    if (!match) continue;
                    const options = [...match[1].matchAll(/<option value="([^"]*)"([^>]*)>/g)];
                    const selected = options.find(x => /selected/.test(x[2])) || options[0];
                    fields[`[data-action-${key}]`] = {
                        value: selected[1], required: true,
                        disabledPlaceholder: /disabled/.test(selected[2]),
                    };
                }
            },
            get innerHTML() { return this.html; },
            querySelector(selector) {
                if (selector === '[data-action-source]') return fields[selector] || null;
                return fields[selector] ||= {
                    value: selector === '[data-action-kind]' ? 'damage' : '1',
                    hidden: false, checked: false, addEventListener() {},
                    parentElement: {hidden: false},
                };
            },
            remove() {},
        };
    }
    const requests = [];
    const button = {disabled: false};
    const form = {
        reportValidity() {
            return rows.children.every(row => ['target', 'source'].every(key => {
                const field = row.querySelector(`[data-action-${key}]`);
                return !field || Boolean(field.value);
            }));
        },
        querySelector() { return button; },
    };
    const ctx = {
        latest: {
            monsters: [{id:'m', name:'Mephit', active:true, alive:true, in_turn:true}],
            characters: [{id:'c', name:'Paladin', active:true, alive:true}],
        },
        battleActionRows: rows, battleActionForm: form,
        battleActionModal: {addEventListener() {}}, battleActionActorId: 'm',
        document: {createElement:makeRow, querySelector:id => controls[id] ||= {}},
        esc:x => String(x), message() {}, load:async () => {},
        request:async (url, options) => {
            requests.push(JSON.parse(options.body));
            return {applied:1};
        },
    };
    vm.runInNewContext(source.slice(start, end), ctx);
    return {ctx, rows, form, requests};
}

async function submit(fixture) {
    await fixture.form.onsubmit({preventDefault() {}});
}

(async () => {
    const ordinary = setup();
    ordinary.ctx.addBattleActionRow();
    const action = ordinary.rows.children[0];
    assert.equal(action.querySelector('[data-action-target]').value, '');
    assert.equal(action.querySelector('[data-action-target]').required, true);
    assert.equal(action.querySelector('[data-action-target]').disabledPlaceholder, true);
    assert.equal(action.querySelector('[data-action-source]'), null);
    await submit(ordinary);
    assert.equal(ordinary.requests.length, 0);
    action.querySelector('[data-action-target]').value = 'c';
    await submit(ordinary);
    assert.equal(ordinary.requests.length, 1);
    assert.equal(ordinary.requests[0].actions[0].source_id, null);
    assert.equal(ordinary.requests[0].actions[0].target_id, 'c');

    const reaction = setup();
    reaction.ctx.addBattleActionRow(true);
    const row = reaction.rows.children[0];
    const target = row.querySelector('[data-action-target]');
    const actor = row.querySelector('[data-action-source]');
    assert.equal(target.value, '');
    assert.equal(actor.value, '');
    assert.equal(actor.required, true);
    assert.equal(actor.disabledPlaceholder, true);
    await submit(reaction);
    assert.equal(reaction.requests.length, 0);
    target.value = 'm';
    await submit(reaction);
    assert.equal(reaction.requests.length, 0);
    target.value = ''; actor.value = 'c';
    await submit(reaction);
    assert.equal(reaction.requests.length, 0);
    target.value = 'm';
    await submit(reaction);
    assert.equal(reaction.requests.length, 1);
    assert.equal(reaction.requests[0].actions[0].source_id, 'c');

    const multiple = setup();
    multiple.ctx.addBattleActionRow();
    multiple.rows.children[0].querySelector('[data-action-target]').value = 'c';
    multiple.ctx.addBattleActionRow(true);
    await submit(multiple);
    assert.equal(multiple.requests.length, 0);
    assert.equal(multiple.rows.children[1].querySelector('[data-action-source]').value, '');
    assert.equal(multiple.rows.children[1].querySelector('[data-action-target]').value, '');
    console.log('Explicit target/source selection regression tests passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
