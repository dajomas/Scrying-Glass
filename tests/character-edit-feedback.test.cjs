const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'static/character-edit-feedback.js'), 'utf8');
const {createController} = require(path.join(root, 'static/admin-feedback-controller.js'));
const deferred = () => {
    let resolve, reject;
    const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
    return {promise, resolve, reject};
};
function harness() {
    const timers = new Map();
    let nextTimer = 0, scope = 'encounter-a';
    const controller = createController({
        setTimeout(fn, delay) { const id = ++nextTimer; timers.set(id, {fn, delay}); return id; },
        clearTimeout(id) { timers.delete(id); },
    });
    controller.setScope('encounter', scope);
    const feedback = {...controller, begin(spec) {
        return controller.begin({...spec, lane: 'encounter', scope, placement: 'pane'});
    }};
    const calls = [], loads = [], delegated = [];
    const modal = {hidden: false};
    const form = {onsubmit(event) { delegated.push({self: this, event}); },
        reportValidity() { return this.valid !== false; },
        querySelectorAll() { return this.controls; },
    };
    const context = vm.createContext({window: {scryingAdminFeedback: feedback},
        document: {querySelector() { return form; }}, editModal: modal,
        editing: null, monsterEdit: () => '',
        numberValue(f, key, fallback) { return f.elements[key].value === '' ? fallback : +f.elements[key].value; },
        request(url, options) {
            const pending = deferred(); calls.push({url, options, ...pending}); return pending.promise;
        },
        closeEdit() { context.editing = null; modal.hidden = true; form.elements = {}; form.controls = []; },
        load(flag) { const pending = deferred(); loads.push({flag, ...pending}); return pending.promise; },
    });
    function open(id = 'a/b ?', kind = 'characters') {
        context.editing = {kind, id}; modal.hidden = false;
        form.elements = Object.fromEntries(Object.entries({name: '  Hero  ', color: '#112233',
            hp: '0', max_hp: '12', initiative: ''}).map(([key, value]) => [key,
            {value, disabled: false, tagName: 'INPUT'}]));
        const submit = {tagName: 'BUTTON', type: 'submit', disabled: false};
        const cancel = {tagName: 'BUTTON', type: 'button', disabled: false};
        form.controls = [...Object.values(form.elements), submit, cancel];
        return {session: context.editing, controls: form.controls, submit, cancel};
    }
    // Production openEdit uses (kind, id); this fixture helper uses (id, kind).
    context.openEdit = (kind, id) => { open(id, kind); };
    open(); vm.runInContext(source, context);
    const submit = () => form.onsubmit.call(form, {preventDefault() {}});
    return {form, context, modal, open, submit, calls, loads, timers, controller, feedback, delegated,
        scope(value) { scope = value; controller.setScope('encounter', value); },
        records: () => controller.snapshot(),
    };
}
const flush = async () => { await Promise.resolve(); await Promise.resolve(); };
async function complete(h, pending) {
    h.calls.at(-1).resolve({}); await flush();
    if (h.loads.length) h.loads.at(-1).resolve();
    await pending;
}
test('preserves JSON endpoint and blank, zero and negative initiative', async () => {
    for (const [input, expected] of [['', null], ['0', 0], ['-3', -3]]) {
        const h = harness(); h.form.elements.initiative.value = input;
        const pending = h.submit();
        assert.equal(h.calls[0].url, '/api/characters/a%2Fb%20%3F');
        assert.equal(h.calls[0].options.method, 'PATCH');
        assert.equal(h.calls[0].options.headers['Content-Type'], 'application/json');
        assert.deepEqual(JSON.parse(h.calls[0].options.body),
            {name: 'Hero', color: '#112233', hp: 0, max_hp: 12, initiative: expected});
        await complete(h, pending);
    }
});
test('request errors persist and preserve draft, dialog and disabled states', async () => {
    const h = harness(); const controls = h.form.controls;
    controls[1].disabled = true;
    const pending = h.submit();
    assert.equal(controls.at(-1).disabled, false);
    h.calls[0].reject(new Error('Save failed')); await pending;
    assert.equal(h.modal.hidden, false); assert.equal(h.form.elements.name.value, '  Hero  ');
    assert.equal(controls[0].disabled, false); assert.equal(controls[1].disabled, true);
    assert.equal(h.records()[0].severity, 'error'); assert.equal(h.timers.size, 0);
});
test('matching recovery preserves unrelated target and operation errors', async () => {
    const h = harness();
    for (const [operation, target] of [['character.create', 'characters'], ['character.edit', '["characters","b"]']]) {
        h.feedback.publish(h.feedback.begin({region: 'characters', operation, target, label: 'Other'}),
            {severity: 'error', text: operation + target});
    }
    let pending = h.submit(); h.calls[0].reject(new Error('Old save error')); await pending;
    pending = h.submit(); await complete(h, pending);
    assert.equal(h.records().filter(r => r.severity === 'error').length, 2);
    assert.equal(h.records().some(r => r.text === 'Old save error'), false);
});
test('one mutation through request and refresh; success precedes refresh and expires at 3s', async () => {
    const h = harness(); const pending = h.submit(); const duplicate = h.submit();
    assert.equal(h.calls.length, 1); await duplicate;
    h.calls[0].resolve({}); await flush();
    assert.equal(h.records()[0].severity, 'success'); assert.equal(h.modal.hidden, true);
    assert.equal(h.loads[0].flag, true);
    h.open(); await h.submit(); assert.equal(h.calls.length, 1);
    h.loads[0].resolve(); await pending;
    assert.equal([...h.timers.values()][0].delay, 3000);
    [...h.timers.values()][0].fn(); assert.equal(h.records().length, 0);
});
test('refresh failure is separate persistent no-replay guidance', async () => {
    const h = harness(); const pending = h.submit(); h.calls[0].resolve({}); await flush();
    h.loads[0].reject(new Error('Offline')); await pending;
    assert.equal(h.calls.length, 1);
    assert.deepEqual(h.records().map(r => r.severity), ['success', 'error']);
    assert.match(h.records()[1].text, /do not repeat the save/);
    assert.equal(h.records()[1].operation, 'character.edit.refresh');
    [...h.timers.values()][0].fn(); assert.equal(h.records().length, 1);
});
test('reopening same ID suppresses old close, notice and refresh; restores only old controls', async () => {
    const h = harness(); const old = h.form.controls; const pending = h.submit();
    h.context.closeEdit(); const newer = h.open();
    h.calls[0].resolve({}); await flush();
    assert.equal(h.loads.length, 0); await pending;
    assert.equal(h.context.editing, newer.session); assert.equal(h.modal.hidden, false);
    assert.equal(h.loads.length, 0); assert.equal(h.records().length, 0);
    assert.equal(old[0].disabled, false); assert.equal(newer.controls[0].disabled, false);
});
test('different target can save while old completion cannot change its dialog', async () => {
    const h = harness(); const old = h.submit(); const newer = h.open('b'); const pending = h.submit();
    h.calls[0].reject(new Error('Obsolete')); await old;
    assert.equal(h.context.editing, newer.session); assert.equal(newer.controls[0].disabled, true);
    assert.equal(h.records().length, 0);
    await complete(h, pending); assert.equal(h.calls.length, 2);
});
test('scope transition suppresses old result and allows new-scope save', async () => {
    const h = harness(); const old = h.submit(); h.scope('encounter-b');
    h.open(); const pending = h.submit(); h.calls[0].resolve({}); await old;
    assert.equal(h.loads.length, 0); assert.equal(h.records().length, 0);
    await complete(h, pending); assert.equal(h.calls.length, 2);
});
test('reopened dialog does not receive old refresh failure', async () => {
    const h = harness(); const pending = h.submit(); h.calls[0].resolve({}); await flush();
    const newer = h.open('b'); h.loads[0].reject(new Error('Offline')); await pending;
    assert.equal(h.context.editing, newer.session);
    assert.equal(h.records().filter(r => r.severity === 'error').length, 0);
});
test('native validity and non-character delegation remain; installation is idempotent', async () => {
    const h = harness(); h.form.valid = false; await h.submit(); assert.equal(h.calls.length, 0);
    const installed = h.form.onsubmit; vm.runInContext(source, h.context);
    assert.equal(h.form.onsubmit, installed);
    h.open('m', 'monsters'); await h.submit();
    assert.equal(h.delegated.length, 1); assert.equal(h.delegated[0].self, h.form);
    assert.equal(h.calls.length, 0);
});
test('document-end loads character owner once before monster wrapper', () => {
    const html = fs.readFileSync(path.join(root, 'templates/admin/190_document_end.html'), 'utf8');
    assert.equal((html.match(/src="\/static\/character-edit-feedback\.js\?v=1"/g) || []).length, 1);
    assert.ok(html.indexOf('/static/admin.js') < html.indexOf('/static/character-edit-feedback.js'));
    assert.ok(html.indexOf('/static/character-edit-feedback.js') < html.indexOf('/static/monster-initiative-edit.js'));
});

test('actual late monster wrapper delegates character submission to new owner', async () => {
    const h = harness();
    vm.runInContext(fs.readFileSync(path.join(root, 'static/monster-initiative-edit.js'), 'utf8'), h.context);
    const pending = h.submit(); await complete(h, pending);
    assert.equal(h.calls.length, 1); assert.match(h.calls[0].url, /^\/api\/characters\//);
    assert.equal(h.records()[0].operation, 'character.edit');
    assert.equal(h.delegated.length, 0);
});
test('actual late monster wrapper retains its own FormData request and no character notice', async () => {
    const h = harness(); h.open('monster/id', 'monsters');
    h.form.elements.monster_species = {value: '  Goblin  '};
    h.form.elements.initiative_bonus = {value: '+2', dataset: {assignedBonus: '1'}};
    h.context.FormData = class extends Map {
        constructor(form) { super(Object.entries(form.elements).map(([k, v]) => [k, v.value])); }
    };
    h.context.File = class {};
    h.form.setAttribute = () => {}; h.form.removeAttribute = () => {};
    h.context.paneNotification = () => assert.fail('Unexpected monster error');
    vm.runInContext(fs.readFileSync(path.join(root, 'static/monster-initiative-edit.js'), 'utf8'), h.context);
    const pending = h.submit();
    assert.equal(h.calls[0].url, '/api/monsters/monster%2Fid/edit');
    assert.equal(h.calls[0].options.method, 'POST');
    assert.equal(h.calls[0].options.body.get('monster_species'), 'Goblin');
    assert.equal(h.calls[0].options.body.get('initiative_bonus'), '+2');
    await complete(h, pending); assert.equal(h.records().length, 0);
});

test('scope invalidation alone suppresses completion even if Edit session object remains', async () => {
    const h = harness(); const session = h.context.editing; const pending = h.submit();
    h.scope('encounter-b'); h.calls[0].resolve({}); await flush();
    assert.equal(h.loads.length, 0); assert.equal(h.context.editing, session);
    assert.equal(h.modal.hidden, false); assert.equal(h.records().length, 0);
    await pending;
});

test('scope change does not enable overlapping submissions on the same dialog controls', async () => {
    const h = harness(); const controls = h.form.controls; const pending = h.submit();
    h.scope('encounter-b'); const duplicate = h.submit();
    assert.equal(h.calls.length, 1); assert.equal(controls[0].disabled, true);
    await duplicate; h.calls[0].resolve({}); await pending;
    assert.equal(controls[0].disabled, false); assert.equal(h.loads.length, 0);
    const retry = h.submit(); assert.equal(h.calls.length, 2); await complete(h, retry);
});
