// SG-TODO-009.7 Stage 1 Steps 2B-2E: save/load/rename/delete feedback in static/setup-switch.js
// with the production controller. DOM, transport and encounter context are mocked.
const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const {createController} = require(path.join(root, 'static/admin-feedback-controller.js'));
const source = fs.readFileSync(path.join(root, 'static/setup-switch.js'), 'utf8');
const deferred = () => {let resolve, reject; const promise = new Promise((a, b) => {resolve = a; reject = b;}); return {promise, resolve, reject};};
const flush = async () => {for (let i = 0; i < 10; i++) await Promise.resolve();};
const LIST = {active: 'camp', moved: [], campaigns: [{id: 'camp', name: 'Camp', setups: ['default', 'Two']}]};

function harness() {
    const nodes = new Map(), calls = [], loads = [], timers = new Map(), confirmations = [], prompts = [], panes = [];
    let epoch = 1, scope = JSON.stringify(['camp', 'camp', 'default']), timer = 0, install;
    const node = id => {
        if (!nodes.has(id)) nodes.set(id, {value: '', disabled: false, focused: 0, listeners: {},
            addEventListener(type, fn) {(this.listeners[type] ||= []).push(fn);}, focus() {this.focused++;}});
        return nodes.get(id);
    };
    const controller = createController({setTimeout(fn, delay) {const id = ++timer; timers.set(id, {fn, delay}); return id;},
        clearTimeout(id) {timers.delete(id);}});
    controller.setScope('page', 'page');
    const api = {...controller, encounterContext: () => Object.freeze({scope, epoch}),
        begin: spec => controller.begin({...spec, scope: 'page', placement: 'pane'})};
    for (const id of ['saveSetup', 'loadSetup', 'renameSetup', 'deleteSetup']) node(id).onclick = () => {throw new Error('legacy ' + id);};
    const context = vm.createContext({window: {scryingAdminFeedback: api}, Error, JSON,
        document: {readyState: 'interactive', getElementById: node, addEventListener(type, fn) {install = fn;}},
        latest: {active_setup: {name: 'default', campaign_id: 'camp'}},
        campaignData: {active: 'camp', campaigns: [{id: 'camp', name: 'Camp', setups: ['default', 'Two']}]},
        activeCampaign() {return context.campaignData.campaigns.find(item => item.id === context.campaignData.active);},
        campaignById(id) {return context.campaignData.campaigns.find(item => item.id === id);},
        request(url, options) {const p = deferred(); calls.push({url, options, ...p}); return p.promise;},
        load(flag, current) {const p = deferred(); loads.push({flag, current, ...p}); return p.promise;},
        setups() {throw new Error('error-swallowing setups() must not be used');},
        renderCampaigns() {}, renderActiveBattleSetup() {}, syncActiveBattleSetupControls() {},
        paneNotification(region, text) {panes.push([region, text]);},
        confirm(text) {confirmations.push(text); return context.confirmed;}, confirmed: true,
        prompt(text, value) {prompts.push([text, value]); return context.answer;}, answer: 'Renamed'});
    vm.runInContext(source, context);
    install();
    const input = node('setupName'), select = node('setupSelect');
    const type = value => {input.value = value; for (const fn of input.listeners.input || []) fn();};
    const observe = (setup, campaign = 'camp') => {
        const next = JSON.stringify([campaign, campaign, setup]);
        if (next !== scope) {scope = next; epoch++; controller.setScope('encounter', scope);}
    };
    select.value = 'Two'; type(' Fresh ');
    return {context, api, node, input, select, calls, loads, timers, confirmations, prompts, panes, type, observe,
        click: id => node(id).onclick(), records: () => controller.snapshot()};
}
const answer = async (h, result) => {h.calls.at(-1).resolve(structuredClone(result)); await flush();};
const loaded = async (h, setup) => {if (setup) h.observe(setup); h.loads.at(-1).resolve(); await flush();};
const ops = h => h.records().map(r => [r.operation, r.severity]);

test('legacy handlers are replaced; validation errors persist without requests', async () => {
    const h = harness();
    h.type('  '); await h.click('saveSetup');
    h.select.value = ''; await h.click('loadSetup'); await h.click('renameSetup'); await h.click('deleteSetup');
    assert.deepEqual(h.records().map(r => [r.operation, r.target, r.text]), [
        ['setup.save.validation', JSON.stringify(['setup-save', 'camp']), 'Enter a battle setup name before saving'],
        ['setup.load.validation', JSON.stringify(['setup-load', 'camp']), 'Choose a saved battle setup to load'],
        ['setup.rename.validation', JSON.stringify(['setup-rename', 'camp']), 'Choose a saved setup to rename'],
        ['setup.delete.validation', JSON.stringify(['setup-delete', 'camp']), 'Choose a saved setup to delete']]);
    assert.ok(h.records().every(r => r.region === 'battleSetup' && r.severity === 'error'));
    assert.equal(h.timers.size, 0); assert.equal(h.calls.length, 0);
    assert.equal(h.prompts.length + h.confirmations.length, 0); assert.equal(h.input.focused, 1);
});

test('2B save: exact POST, early success, ordered guarded refresh, 3 s expiry', async () => {
    const h = harness(), p = h.click('saveSetup');
    assert.equal(h.calls[0].url, '/api/setups/save');
    assert.deepEqual(JSON.parse(h.calls[0].options.body), {name: 'Fresh', campaign: 'camp'});
    assert.equal(h.node('saveSetup').disabled, true);
    await answer(h, {name: 'Fresh', campaign: 'camp'});
    assert.deepEqual(h.records().map(r => r.text), ['Saved setup: Fresh (campaign: Camp)']);
    assert.equal(h.input.value, 'Fresh'); assert.equal(h.loads[0].flag, true);
    await loaded(h, 'Fresh'); assert.equal(h.calls[1].url, '/api/campaigns');
    await answer(h, LIST); await p;
    assert.equal(h.select.value, 'Fresh'); assert.equal(h.node('saveSetup').disabled, false);
    assert.deepEqual(ops(h), [['setup.save', 'success']]);
    const timers = [...h.timers.values()]; assert.equal(timers.length, 1); assert.equal(timers[0].delay, 3000);
    timers[0].fn(); assert.equal(h.records().length, 0);
});

test('2B save over the current setup keeps scope; newer typing is preserved', async () => {
    const h = harness(); h.type('default'); const p = h.click('saveSetup'); h.type('Draft');
    await answer(h, {name: 'default', campaign: 'camp'}); await loaded(h); await answer(h, LIST); await p;
    assert.equal(h.input.value, 'Draft'); assert.deepEqual(ops(h), [['setup.save', 'success']]);
});

test('request failures persist and matching retry resolves them; refresh never replays', async () => {
    const h = harness(); let p = h.click('saveSetup');
    h.calls[0].reject(new Error('Disk full')); await p;
    assert.deepEqual(ops(h), [['setup.save', 'error']]); assert.equal(h.timers.size, 0); assert.equal(h.loads.length, 0);
    p = h.click('saveSetup'); await answer(h, {name: 'Fresh', campaign: 'camp'});
    h.loads[0].reject(new Error('Offline')); await p;
    const refresh = h.records().find(r => r.operation === 'setup.save.refresh');
    assert.match(refresh.text, /Fresh was saved, but refreshing the view failed: Offline\. Reload the page; do not repeat the save/);
    assert.equal(h.records().find(r => r.operation === 'setup.save').severity, 'success');
    for (const t of [...h.timers.values()]) t.fn();
    assert.deepEqual(ops(h), [['setup.save.refresh', 'error']]);
    assert.equal(h.calls.filter(c => c.url === '/api/setups/save').length, 2);
});

test('unapplied resulting scope reports a persistent refresh error', async () => {
    const h = harness(), p = h.click('saveSetup');
    await answer(h, {name: 'Fresh', campaign: 'camp'}); await loaded(h); await answer(h, LIST); await p;
    assert.match(h.records().find(r => r.operation === 'setup.save.refresh').text, /state was not applied/);
});

test('2C load: no confirmation, guarded refresh, already-loaded no-op, failure restores selection', async () => {
    const h = harness(); let p = h.select.onchange({preventDefault() {}});
    assert.equal(h.calls[0].url, '/api/setups/load');
    assert.deepEqual(JSON.parse(h.calls[0].options.body), {name: 'Two', campaign: 'camp'});
    assert.equal(h.select.disabled, true); assert.equal(h.node('loadSetup').disabled, true);
    await answer(h, {name: 'Two', campaign: 'camp'});
    assert.deepEqual(h.records().map(r => r.text), ['Loaded battle setup: Two']); assert.equal(h.input.value, 'Two');
    await loaded(h, 'Two'); await answer(h, LIST); await p;
    assert.equal(h.select.value, 'Two'); assert.equal(h.select.disabled, false); assert.deepEqual(ops(h), [['setup.load', 'success']]);
    assert.equal(h.confirmations.length, 0);
    h.context.latest = {active_setup: {name: 'Two', campaign_id: 'camp'}};
    await h.click('loadSetup'); assert.equal(h.calls.length, 2, 'already loaded is a no-op');
    h.select.value = 'default'; p = h.click('loadSetup'); h.calls.at(-1).reject(new Error('Denied')); await p;
    assert.equal(h.select.value, 'Two'); assert.equal(h.records().at(-1).text, 'Denied');
});

test('2C load failure keeps a newer selection; missing campaign is reported', async () => {
    const h = harness(), p = h.click('loadSetup'); h.select.value = 'Other'; h.calls[0].reject(new Error('Denied')); await p;
    assert.equal(h.select.value, 'Other');
    h.context.campaignData = {active: null, campaigns: []}; await h.click('loadSetup');
    assert.equal(h.records().at(-1).text, 'Choose an active campaign first');
});

test('2D rename: prompt no-ops, exact POST, active setup reload and success text', async () => {
    const h = harness();
    for (const value of [null, '  ', 'Two']) {h.context.answer = value; await h.click('renameSetup');}
    assert.equal(h.calls.length, 0); assert.deepEqual(h.prompts[0], ['Rename battle setup Two to:', 'Two']);
    h.select.value = 'default'; h.type('default'); h.context.answer = ' Main ';
    const p = h.click('renameSetup');
    assert.deepEqual(JSON.parse(h.calls[0].options.body), {name: 'default', new_name: 'Main', campaign: 'camp'});
    await answer(h, {old_name: 'default', name: 'Main', campaign: 'camp'});
    assert.deepEqual(h.records().map(r => r.text), ['Renamed battle setup default to Main']);
    assert.equal(h.input.value, 'Main'); await answer(h, LIST);
    assert.equal(h.select.value, 'Main'); assert.equal(h.loads.length, 1);
    await loaded(h, 'Main'); await p; assert.deepEqual(ops(h), [['setup.rename', 'success']]);
});

test('2D rename of an inactive setup leaves the editor and loaded setup alone', async () => {
    const h = harness(), p = h.click('renameSetup');
    await answer(h, {old_name: 'Two', name: 'Renamed', campaign: 'camp'}); await answer(h, LIST); await p;
    assert.equal(h.input.value, ' Fresh '); assert.equal(h.loads.length, 0); assert.deepEqual(ops(h), [['setup.rename', 'success']]);
});

test('2E delete: preserved confirmation, exact DELETE, opened setup and guarded refresh', async () => {
    const h = harness(); h.context.confirmed = false; await h.click('deleteSetup');
    assert.equal(h.calls.length, 0);
    assert.equal(h.confirmations[0], 'Delete battle setup Two from campaign Camp?\n\nThe next battle setup is opened afterwards ' +
        '(an empty "default" setup is created if this was the last one). Unsaved changes to the current battle will be lost.');
    h.context.confirmed = true; const p = h.click('deleteSetup');
    assert.equal(h.calls[0].url, '/api/setups/Two?campaign=camp'); assert.equal(h.calls[0].options.method, 'DELETE');
    await answer(h, {deleted: 'Two', opened_setup: 'default', created_default: true, campaign: 'camp'});
    assert.deepEqual(h.records().map(r => r.text), ['Deleted battle setup Two; opened new empty setup default']);
    await answer(h, LIST); assert.equal(h.select.value, 'default'); assert.equal(h.input.value, 'default');
    assert.equal(h.loads[0].flag, true); await loaded(h); await p; // same-named replacement keeps scope
    assert.deepEqual(ops(h), [['setup.delete', 'success']]); assert.equal(h.node('deleteSetup').disabled, false);
});

test('2E delete opening another setup completes with success only', async () => {
    const h = harness(), p = h.click('deleteSetup');
    await answer(h, {deleted: 'Two', opened_setup: 'Three', created_default: false, campaign: 'camp'});
    await answer(h, LIST); await loaded(h, 'Three'); await p;
    assert.deepEqual(h.records().map(r => r.text), ['Deleted battle setup Two; opened Three']);
});

test('campaign switch or unrelated scope change suppresses obsolete outcomes', async () => {
    for (const action of ['campaign', 'scope', 'reject']) {
        const h = harness(), p = h.click('saveSetup');
        if (action === 'campaign') h.context.campaignData = {active: 'other', campaigns: []};
        else h.observe('elsewhere');
        if (action === 'reject') h.calls[0].reject(new Error('Obsolete')); else await answer(h, {name: 'Fresh', campaign: 'camp'});
        await p;
        assert.equal(h.records().length, 0, action); assert.equal(h.loads.length, 0); assert.equal(h.node('saveSetup').disabled, false);
    }
});

test('expected transition may arrive before the response', async () => {
    const h = harness(), p = h.click('loadSetup'); h.observe('Two');
    await answer(h, {name: 'Two', campaign: 'camp'}); assert.equal(h.loads[0].current(), true);
    await loaded(h); await answer(h, LIST); await p; assert.deepEqual(ops(h), [['setup.load', 'success']]);
});

test('duplicate clicks are ignored and prior disabled state is restored', async () => {
    const h = harness(); h.node('deleteSetup').disabled = true;
    const p = h.click('deleteSetup'); await h.click('deleteSetup'); assert.equal(h.calls.length, 1);
    await answer(h, {deleted: 'Two', opened_setup: 'Three', campaign: 'camp'}); await h.click('deleteSetup');
    await answer(h, LIST); await loaded(h, 'Three'); await p;
    assert.equal(h.confirmations.length, 1); assert.equal(h.node('deleteSetup').disabled, true);
});

test('server-moved setups keep the campaign notice; unrelated errors survive', async () => {
    const h = harness();
    h.api.publish(h.api.begin({lane: 'page', region: 'battleSetup', operation: 'other', target: 'x', label: 'x'}),
        {severity: 'error', text: 'Keep newer error'});
    const p = h.click('renameSetup');
    await answer(h, {old_name: 'Two', name: 'Renamed', campaign: 'camp'}); await answer(h, {...LIST, moved: ['a', 'b']}); await p;
    assert.deepEqual(h.panes, [['campaign', 'Moved 2 unassigned setup(s) into campaign Default: a, b']]);
    assert.deepEqual(h.records().filter(r => r.severity === 'error').map(r => r.text), ['Keep newer error']);
});
