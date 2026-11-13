const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'static/admin/060-source.js'), 'utf8');
const {createController} = require(path.join(root, 'static/admin-feedback-controller.js'));
const deferred = () => {
    let resolve, reject;
    const promise = new Promise((a, b) => {resolve = a; reject = b;});
    return {promise, resolve, reject};
};
const flush = async () => {await Promise.resolve(); await Promise.resolve();};
function harness() {
    let scope = 'encounter-a', timerId = 0;
    const timers = new Map(), calls = [], loads = [], validations = [];
    const controller = createController({
        setTimeout(fn, delay) {const id = ++timerId; timers.set(id, {fn, delay}); return id;},
        clearTimeout(id) {timers.delete(id);},
    });
    controller.setScope('encounter', scope);
    const feedback = {...controller, begin(spec) {
        return controller.begin({...spec, lane: 'encounter', scope, placement: 'pane'});
    }};
    class File {constructor(name) {this.name = name;}}
    class FormData extends Map {
        constructor(form) {
            super(Object.entries(form.values).filter(([key]) => !form.fields[key].disabled));
            form.constructed++; form.formDataHook?.(this);
        }
    }
    const form = (id, values) => ({id, values, constructed: 0, resets: 0, valid: true,
        fields: Object.fromEntries(Object.keys(values).map(key => [key,
            {disabled: false, focused: 0, focus() {this.focused++;}}])),
        reportValidity() {return this.valid;}, querySelectorAll() {return Object.values(this.fields);},
        reset() {this.resets++;}, get elements() {return this.fields;},
    });
    const forms = {
        '#characterForm': form('characterForm', {name: ' Hero ', color: '#123456', hp: '0', initiative: ''}),
        '#monsterForm': form('monsterForm', {name: ' Goblin ', hprangestart: ' 3d8+9 ', hprangeend: '', initiative_bonus: '-2'}),
        '#monsterUpload': form('monsterUpload', {monster_file: new File('goblin.monster'), quantity: '02', image: new File('token.png')}),
    };
    const state = {hpError: null};
    const passive = {addEventListener() {}};
    const context = vm.createContext({window: {scryingAdminFeedback: feedback}, File, FormData, Error,
        document: {querySelector: selector => forms[selector] || passive},
        characterBulkAction: passive, monsterBulkAction: passive,
        validateMonsterHpRange(start, end) {validations.push([start, end]); return state.hpError;},
        isDiceHpExpression: () => true, parseNonNegativeInteger: () => 0,
        request(url, options) {
            const pending = deferred(); calls.push({url, options, ...pending}); return pending.promise;
        },
        load(flag) {const pending = deferred(); loads.push({flag, ...pending}); return pending.promise;},
    });
    vm.runInContext(source, context);
    return {forms, calls, loads, validations, state, timers,
        scope() {scope = 'encounter-b'; controller.setScope('encounter', scope);},
        submit(selector, targetOnly = false) {
            const f = forms[selector];
            return f.onsubmit({currentTarget: targetOnly ? null : f, target: f, preventDefault() {}});
        },
        notices: () => controller.snapshot(),
    };
}
async function succeed(h, pending, result = {}) {
    h.calls.at(-1).resolve(result); await flush(); h.loads.at(-1)?.resolve(); await pending;
}
test('character JSON preserves names, zero HP and blank/zero/negative initiative', async () => {
    for (const [value, expected] of [['', null], ['0', 0], ['-2', -2]]) {
        const h = harness(); h.forms['#characterForm'].values.initiative = value;
        const pending = h.submit('#characterForm', true);
        assert.equal(h.calls[0].url, '/api/characters');
        assert.equal(h.calls[0].options.headers['Content-Type'], 'application/json');
        assert.deepEqual(JSON.parse(h.calls[0].options.body),
            {name: ' Hero ', color: '#123456', hp: 0, initiative: expected});
        await succeed(h, pending);
    }
});
test('request failure preserves files, draft and prior disabled states', async () => {
    const h = harness(), f = h.forms['#monsterUpload']; f.fields.image.disabled = true;
    const file = f.values.monster_file; const pending = h.submit('#monsterUpload');
    h.calls[0].reject(new Error('Rejected')); await pending;
    assert.equal(f.resets, 0); assert.equal(f.values.monster_file, file);
    assert.equal(f.fields.monster_file.disabled, false); assert.equal(f.fields.image.disabled, true);
    assert.equal(h.loads.length, 0); assert.equal(h.notices()[0].severity, 'error');
    assert.equal(h.timers.size, 0);
});
test('success precedes separate persistent refresh failure without replay', async () => {
    const h = harness(); const pending = h.submit('#characterForm'); h.calls[0].resolve({}); await flush();
    assert.equal(h.notices()[0].severity, 'success'); assert.equal(h.forms['#characterForm'].resets, 1);
    assert.equal(h.loads[0].flag, true); h.loads[0].reject(new Error('Offline')); await pending;
    assert.deepEqual(h.notices().map(n => n.severity), ['success', 'error']);
    assert.match(h.notices()[1].operation, /\.refresh$/); assert.match(h.notices()[1].text, /do not repeat/);
    assert.equal(h.calls.length, 1);
});
test('duplicate guard includes refresh and avoids rebuilding FormData', async () => {
    const h = harness(), f = h.forms['#characterForm']; const pending = h.submit('#characterForm');
    const duplicate = h.submit('#characterForm'); assert.equal(h.calls.length, 1); await duplicate;
    assert.equal(f.constructed, 1); h.calls[0].resolve({}); await flush();
    const duringRefresh = h.submit('#characterForm'); assert.equal(h.calls.length, 1); await duringRefresh;
    h.loads[0].resolve(); await pending; assert.equal(f.fields.name.disabled, false);
});
test('stale completion never resets the form or starts a new-encounter refresh', async () => {
    const h = harness(), f = h.forms['#characterForm']; const pending = h.submit('#characterForm');
    h.scope(); h.calls[0].resolve({}); await flush();
    assert.equal(f.resets, 0); assert.equal(h.loads.length, 0); assert.equal(h.notices().length, 0);
    await pending; assert.equal(f.fields.name.disabled, false);
});
test('native validation error resolves on matching valid preparation', async () => {
    const h = harness(), f = h.forms['#characterForm']; f.valid = false; await h.submit('#characterForm');
    assert.equal(h.calls.length, 0); assert.equal(h.notices()[0].operation, 'character.create.validation');
    f.valid = true; const pending = h.submit('#characterForm'); assert.equal(h.notices().length, 0);
    await succeed(h, pending);
});
test('HP validation preserves focus; retry retains dice strings and formdata tokens', async () => {
    const h = harness(), f = h.forms['#monsterForm']; h.state.hpError = 'HP range invalid';
    await h.submit('#monsterForm'); assert.equal(h.calls.length, 0); assert.equal(f.fields.hprangeend.focused, 1);
    h.state.hpError = null;
    f.formDataHook = payload => {payload.set('selection_token', 'signed-selection'); payload.set('initiative_bonus_offer_token', 'signed-offer');};
    const pending = h.submit('#monsterForm'); const payload = h.calls[0].options.body;
    assert.equal(payload.get('hprangestart'), '3d8+9'); assert.equal(payload.get('hprangeend'), '');
    assert.equal(payload.get('initiative_bonus'), '-2'); assert.equal(payload.get('selection_token'), 'signed-selection');
    assert.equal(payload.get('initiative_bonus_offer_token'), 'signed-offer'); assert.equal(h.calls[0].options.headers, undefined);
    assert.deepEqual(h.validations.at(-1), ['3d8+9', '']); await succeed(h, pending, [{}]);
});
test('file quantity validation retains uploads and valid original FormData values', async () => {
    const h = harness(), f = h.forms['#monsterUpload']; const file = f.values.monster_file, image = f.values.image;
    for (const text of ['0', '51', '1.5', '-1', 'abc']) {f.values.quantity = text; await h.submit('#monsterUpload');}
    assert.equal(h.calls.length, 0); assert.equal(f.resets, 0); f.values.quantity = '02';
    const pending = h.submit('#monsterUpload'); const body = h.calls[0].options.body;
    assert.equal(h.calls[0].url, '/api/monsters/import'); assert.equal(body.get('quantity'), '02');
    assert.equal(body.get('monster_file'), file); assert.equal(body.get('image'), image);
    await succeed(h, pending, null); assert.match(h.notices()[0].text, /2 monsters imported/);
});
test('matching request recovery preserves the other form error', async () => {
    const h = harness(); let a = h.submit('#characterForm'), b = h.submit('#monsterForm');
    h.calls[0].reject(new Error('Character failed')); h.calls[1].reject(new Error('Monster failed'));
    await Promise.all([a, b]); assert.equal(h.notices().length, 2);
    a = h.submit('#characterForm'); await succeed(h, a);
    assert.equal(h.notices().filter(n => n.severity === 'error').length, 1);
    assert.equal(h.notices().find(n => n.severity === 'error').text, 'Monster failed');
});
test('FormData is captured before controls are disabled', async () => {
    const h = harness(), f = h.forms['#characterForm']; const pending = h.submit('#characterForm');
    assert.equal(Object.values(f.fields).every(x => x.disabled), true);
    assert.deepEqual(Object.keys(JSON.parse(h.calls[0].options.body)), ['name', 'color', 'hp', 'initiative']);
    await succeed(h, pending);
});
test('production controller gives pane success 3s and preserves refresh error afterward', async () => {
    const h = harness(); const pending = h.submit('#characterForm'); h.calls[0].resolve({}); await flush();
    h.loads[0].reject(new Error('Offline')); await pending;
    const timer = [...h.timers.values()][0]; assert.equal(timer.delay, 3000); timer.fn();
    assert.equal(h.notices().length, 1); assert.equal(h.notices()[0].severity, 'error');
});
test('successful explicit resubmission and refresh resolve only their own refresh error', async () => {
    const h = harness(); let pending = h.submit('#characterForm'); h.calls[0].resolve({}); await flush();
    h.loads[0].reject(new Error('Offline')); await pending;
    const other = h.submit('#monsterForm'); h.calls[1].reject(new Error('Other error')); await other;
    pending = h.submit('#characterForm'); await succeed(h, pending);
    assert.deepEqual(h.notices().filter(n => n.severity === 'error').map(n => n.text), ['Other error']);
});
