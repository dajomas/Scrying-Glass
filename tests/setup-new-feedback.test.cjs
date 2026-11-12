// SG-TODO-009.7 Stage 1 Step 2A: complete 060 with the production controller.
// DOM, transport, encounter context and legacy owners are mocked; not live-server evidence.
const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const {createController} = require(path.join(root, 'static/admin-feedback-controller.js'));
const source = fs.readFileSync(path.join(root, 'static/admin/060-source.js'), 'utf8');
const deferred = () => {let resolve, reject; const promise = new Promise((a, b) => {resolve = a; reject = b;}); return {promise, resolve, reject};};
const flush = async () => {for (let i = 0; i < 8; i++) await Promise.resolve();};
const LIST = {active: 'camp', moved: [], campaigns: [{id: 'camp', name: 'Camp', setups: ['default', 'Fresh']}]};

function harness() {
    const nodes = new Map(), calls = [], loads = [], timers = new Map(), confirmations = [], legacy = [], panes = [];
    let epoch = 1, scope = JSON.stringify(['camp', 'camp', 'default']), timer = 0;
    const node = id => {
        if (!nodes.has(id)) nodes.set(id, {value: '', disabled: false, focused: 0, listeners: {},
            addEventListener(type, fn) {(this.listeners[type] ||= []).push(fn);}, focus() {this.focused++;}});
        return nodes.get(id);
    };
    const passive = {addEventListener() {}};
    const ids = new Set(['#newSetup', '#setupName', '#setupSelect']);
    const controller = createController({setTimeout(fn, delay) {const id = ++timer; timers.set(id, {fn, delay}); return id;},
        clearTimeout(id) {timers.delete(id);}});
    controller.setScope('page', 'page');
    controller.setScope('encounter', scope);
    const api = {...controller, encounterContext: () => Object.freeze({scope, epoch}), begin(spec) {
        const lane = spec.lane || 'encounter';
        return controller.begin({...spec, lane, scope: lane === 'page' ? 'page' : scope, placement: 'pane'});
    }};
    node('#newSetup').onclick = () => legacy.push('legacy');
    const context = vm.createContext({window: {scryingAdminFeedback: api}, Error, JSON,
        document: {querySelector: selector => ids.has(selector) ? node(selector) : passive},
        characterBulkAction: passive, monsterBulkAction: passive,
        campaignData: {active: 'camp', campaigns: [{id: 'camp', name: 'Camp', setups: ['default']}]},
        activeCampaign() {return context.campaignData.campaigns.find(item => item.id === context.campaignData.active);},
        request(url, options) {const p = deferred(); calls.push({url, options, ...p}); return p.promise;},
        load(flag, current) {const p = deferred(); loads.push({flag, current, ...p}); return p.promise;},
        renderCampaigns() {}, renderActiveBattleSetup() {}, syncActiveBattleSetupControls() {},
        paneNotification(region, text) {panes.push([region, text]);},
        confirm(text) {confirmations.push(text); return context.confirmed;}, confirmed: true});
    vm.runInContext(source, context);
    const input = node('#setupName'), button = node('#newSetup');
    const type = value => {input.value = value; for (const fn of input.listeners.input || []) fn();};
    const observe = (campaign = 'camp', setup = 'Fresh') => {
        const next = JSON.stringify([campaign, setup ? campaign : null, setup]);
        if (next !== scope) {scope = next; epoch++; controller.setScope('encounter', scope);}
    };
    type(' Fresh ');
    return {context, api, node, input, button, calls, loads, timers, confirmations, legacy, panes, type, observe,
        click: () => button.onclick(), records: () => controller.snapshot()};
}
async function created(h, result = {name: 'Fresh', campaign: 'camp'}) {h.calls.at(-1).resolve(result); await flush();}
async function listed(h, list = LIST) {h.calls.at(-1).resolve(structuredClone(list)); await flush();}
async function loaded(h, pending, observe = true) {if (observe) h.observe(); h.loads.at(-1).resolve(); await pending;}
function other(h, spec = {}) {
    h.api.publish(h.api.begin({lane: 'page', region: 'battleSetup', operation: 'other', target: 'other', label: 'Other', ...spec}),
        {severity: 'error', text: 'Keep newer error'});
}

test('migrated owner replaces the legacy handler; passive readers keep loading', () => {
    const h = harness();
    assert.equal(h.button.onclick.constructor.name, 'AsyncFunction');
    h.context.confirmed = false; h.click();
    assert.deepEqual(h.legacy, []);
    const context = vm.createContext({window: {}, document: {querySelector: () => ({addEventListener() {}})},
        characterBulkAction: {addEventListener() {}}, monsterBulkAction: {addEventListener() {}}});
    assert.doesNotThrow(() => vm.runInContext(source, context));
});

test('blank and case-insensitive duplicate names persist validation errors without POST', async () => {
    const h = harness();
    h.type('   '); await h.click();
    let record = h.records().at(-1);
    assert.equal(record.operation, 'setup.new.validation'); assert.equal(record.severity, 'error');
    assert.equal(record.text, 'Enter a unique battle setup name before creating it.');
    assert.equal(record.target, JSON.stringify(['setup-new', 'camp'])); assert.equal(record.region, 'battleSetup');
    h.type(' DEFAULT '); await h.click();
    record = h.records().at(-1);
    assert.equal(record.text, 'A battle setup named “DEFAULT” already exists in Camp.');
    assert.equal(h.records().length, 1, 'replacement keeps one matching validation error');
    assert.equal(h.input.focused, 2); assert.equal(h.calls.length, 0); assert.equal(h.confirmations.length, 0);
    assert.equal(h.timers.size, 0, 'actionable validation errors do not expire');
    assert.equal(h.input.value, ' DEFAULT ');
});

test('valid input resolves validation; cancelled confirmation sends nothing', async () => {
    const h = harness(); other(h);
    h.type(''); await h.click(); assert.equal(h.records().length, 2);
    h.type(' Fresh '); h.context.confirmed = false; await h.click();
    assert.match(h.confirmations[0], /Discard the current battle setup and create a new empty setup named “Fresh”\?/);
    assert.deepEqual(h.records().map(r => r.text), ['Keep newer error']);
    assert.equal(h.calls.length, 0); assert.equal(h.input.value, ' Fresh ');
});

test('exact POST, early pane success, guarded refresh and three-second expiry', async () => {
    const h = harness(), p = h.click();
    assert.equal(h.calls[0].url, '/api/setups/new'); assert.equal(h.calls[0].options.method, 'POST');
    assert.equal(h.calls[0].options.headers['Content-Type'], 'application/json');
    assert.deepEqual(JSON.parse(h.calls[0].options.body), {name: 'Fresh', campaign: 'camp'});
    assert.equal(h.button.disabled, true);
    await created(h);
    assert.equal(h.records()[0].operation, 'setup.new'); assert.equal(h.records()[0].severity, 'success');
    assert.equal(h.records()[0].text, 'Created and saved empty battle setup “Fresh”.');
    assert.equal(h.input.value, 'Fresh'); assert.equal(h.calls[1].url, '/api/campaigns');
    await listed(h);
    assert.equal(h.node('#setupSelect').value, 'Fresh'); assert.equal(h.loads[0].flag, true);
    assert.equal(typeof h.loads[0].current, 'function'); assert.equal(h.button.disabled, true, 'busy through refresh');
    await loaded(h, p);
    assert.equal(h.button.disabled, false); assert.equal(h.records().length, 1);
    const timers = [...h.timers.values()]; assert.equal(timers.length, 1); assert.equal(timers[0].delay, 3000);
    timers[0].fn(); assert.equal(h.records().length, 0); assert.equal(h.calls.length, 2);
});

test('request rejection persists; matching retry resolves it and keeps unrelated errors', async () => {
    const h = harness(); other(h);
    let p = h.click(); h.calls[0].reject(new Error('A battle setup with this name already exists')); await p;
    assert.equal(h.records().at(-1).operation, 'setup.new'); assert.equal(h.records().at(-1).severity, 'error');
    assert.equal(h.loads.length, 0); assert.equal(h.input.value, ' Fresh '); assert.equal(h.button.disabled, false);
    assert.equal(h.timers.size, 0);
    p = h.click(); await created(h); await listed(h); await loaded(h, p);
    assert.deepEqual(h.records().filter(r => r.severity === 'error').map(r => r.text), ['Keep newer error']);
});

test('completed creation followed by failed refresh persists no-replay guidance', async () => {
    for (const stage of ['list', 'load', 'unapplied']) {
        const h = harness(), p = h.click(); await created(h);
        if (stage === 'list') {h.calls[1].reject(new Error('Offline')); await p;}
        else {await listed(h); if (stage === 'load') {h.loads[0].reject(new Error('Offline')); await p;} else await loaded(h, p, false);}
        const error = h.records().find(r => r.operation === 'setup.new.refresh');
        assert.ok(error, stage); assert.equal(error.severity, 'error');
        assert.match(error.text, /“Fresh” was created and saved, but refreshing the view failed/);
        assert.match(error.text, stage === 'unapplied' ? /state was not applied/ : /Offline/);
        assert.match(error.text, /do not create the setup again/);
        for (const t of [...h.timers.values()]) t.fn();
        assert.ok(h.records().some(r => r.operation === 'setup.new.refresh'), 'refresh error does not expire');
        assert.equal(h.calls.filter(c => c.url === '/api/setups/new').length, 1, 'never replays the POST');
        assert.equal(h.button.disabled, false);
    }
});

test('duplicate clicks are ignored through POST and refresh; prior disabled state is restored', async () => {
    const h = harness(); h.button.disabled = true;
    const p = h.click(); await h.click(); assert.equal(h.calls.length, 1);
    await created(h); await h.click(); await listed(h); await h.click();
    assert.equal(h.calls.length, 2); await loaded(h, p);
    assert.equal(h.button.disabled, true); assert.equal(h.confirmations.length, 1);
});

test('newer typing is preserved while the created setup is still reported', async () => {
    const h = harness(), p = h.click(); h.type('Next draft'); await created(h); await listed(h); await loaded(h, p);
    assert.equal(h.input.value, 'Next draft'); assert.equal(h.records()[0].severity, 'success');
});

test('campaign switch or unrelated scope change suppresses obsolete completion', async () => {
    for (const action of ['campaign', 'scope', 'refresh-scope']) {
        const h = harness(), p = h.click();
        if (action === 'campaign') h.context.campaignData = {active: 'other', campaigns: []};
        if (action === 'scope') h.observe('camp', 'elsewhere');
        if (action === 'refresh-scope') {await created(h); h.observe('camp', 'elsewhere'); await listed(h); await p;}
        else {await created(h); await p;}
        assert.equal(h.loads.length, 0, action);
        assert.equal(h.records().filter(r => r.operation === 'setup.new.refresh').length, 0);
        if (action !== 'refresh-scope') assert.equal(h.records().length, 0);
        assert.equal(h.calls.length, action === 'refresh-scope' ? 2 : 1);
        assert.equal(h.button.disabled, false);
    }
});

test('obsolete request rejection after a scope change is suppressed', async () => {
    const h = harness(), p = h.click(); h.observe('other', 'x'); h.calls[0].reject(new Error('Obsolete')); await p;
    assert.equal(h.records().length, 0);
});

test('expected transition may arrive before the POST response', async () => {
    const h = harness(), p = h.click(); h.observe(); await created(h); await listed(h);
    assert.equal(h.loads[0].current(), true); await loaded(h, p);
    assert.deepEqual(h.records().map(r => r.severity), ['success']);
});

test('older success timer cannot clear a newer same-identity error', async () => {
    const h = harness(), p = h.click(); await created(h); await listed(h); await loaded(h, p);
    const record = h.records()[0], timer = [...h.timers.values()][0];
    other(h, {operation: record.operation, target: record.target}); timer.fn();
    assert.equal(h.records()[0].text, 'Keep newer error');
});

test('server-moved setups keep the existing campaign notice', async () => {
    const h = harness(), p = h.click(); await created(h); await listed(h, {...LIST, moved: ['a', 'b']}); await loaded(h, p);
    assert.deepEqual(h.panes, [['campaign', 'Moved 2 unassigned setup(s) into campaign Default: a, b']]);
});
