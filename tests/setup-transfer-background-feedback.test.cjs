// SG-TODO-009.7 Stage 1 Step 3: setup copy/move and View screen background feedback in
// static/setup-switch.js with the production controller. DOM, transport and context are mocked.
const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const {createController} = require(path.join(root, 'static/admin-feedback-controller.js'));
const source = fs.readFileSync(path.join(root, 'static/setup-switch.js'), 'utf8');
const deferred = () => {let resolve, reject; const promise = new Promise((a, b) => {resolve = a; reject = b;}); return {promise, resolve, reject};};
const flush = async () => {for (let i = 0; i < 10; i++) await Promise.resolve();};
const CAMPAIGNS = [{id: 'camp', name: 'Camp', setups: ['default']}, {id: 'other', name: 'Other', setups: ['Ambush']}];
const RESULT = (extra = {}) => ({active: 'camp', moved: [], campaigns: structuredClone(CAMPAIGNS), setup: 'Ambush', campaign: 'camp', mode: 'move', ...extra});

function harness({active = {name: 'default', campaign_id: 'camp'}} = {}) {
    const nodes = new Map(), calls = [], loads = [], timers = new Map(), panes = [], renders = [];
    let epoch = 1, scope = JSON.stringify(['camp', active ? active.campaign_id : null, active?.name || null]), timer = 0, install;
    const node = id => {
        if (!nodes.has(id)) nodes.set(id, {id, value: '', disabled: false, hidden: true, focused: 0, files: [],
            innerHTML: '', focus() {this.focused++;}, querySelector: () => node('submitTransfer')});
        return nodes.get(id);
    };
    const controller = createController({setTimeout(fn, delay) {const id = ++timer; timers.set(id, {fn, delay}); return id;},
        clearTimeout(id) {timers.delete(id);}});
    controller.setScope('page', 'page');
    const api = {...controller, encounterContext: () => Object.freeze({scope, epoch}),
        begin: spec => controller.begin({...spec, scope: 'page', placement: 'pane'})};
    const legacy = id => () => {throw new Error('legacy ' + id);};
    for (const id of ['openCampaignSetup', 'applyBackground', 'clearBackgroundImage']) node(id).onclick = legacy(id);
    node('campaignSetupForm').onsubmit = legacy('submit');
    node('backgroundImage').onchange = legacy('upload');
    let closed = 0;
    node('cancelCampaignSetup').onclick = () => {closed++; node('campaignSetupModal').hidden = true;};
    node('campaignSelect').value = 'camp';
    node('backgroundColor').value = '#112233';
    const form = {from_campaign: 'other', setup: 'Ambush', to_campaign: 'camp', mode: 'move'};
    class FormData {
        constructor(target) {this.entries = target ? {...form} : {};}
        get(key) {return this.entries[key] ?? null;}
        append(key, value) {this.entries[key] = value;}
    }
    const context = vm.createContext({window: {scryingAdminFeedback: api}, Error, JSON, FormData, encodeURIComponent,
        document: {readyState: 'interactive', getElementById: node, addEventListener(type, fn) {install = fn;}},
        latest: {active_setup: active},
        campaignData: {active: 'camp', campaigns: structuredClone(CAMPAIGNS)},
        campaignById(id) {return context.campaignData.campaigns.find(item => item.id === id);},
        campaignOptions(selected) {return `<${selected}>`;},
        request(url, options) {const p = deferred(); calls.push({url, options, ...p}); return p.promise;},
        load(flag, current) {const p = deferred(); loads.push({flag, current, ...p}); return p.promise;},
        setups() {throw new Error('error-swallowing setups() must not be used');},
        renderCampaigns() {renders.push('campaigns');}, renderCampaignSetupNames() {renders.push('names');},
        renderActiveBattleSetup() {}, syncActiveBattleSetupControls() {},
        paneNotification(region, text) {panes.push([region, text]);}});
    vm.runInContext(source, context);
    install();
    const observe = next => {next = JSON.stringify(next); if (next !== scope) {scope = next; epoch++; controller.setScope('encounter', scope);}};
    return {context, node, form, calls, loads, timers, panes, renders, observe, closed: () => closed,
        submit: () => node('campaignSetupForm').onsubmit({preventDefault() {}, target: node('campaignSetupForm')}),
        click: id => node(id).onclick(), records: () => controller.snapshot()};
}
const answer = async (h, result) => {h.calls.at(-1).resolve(structuredClone(result)); await flush();};
const ops = h => h.records().map(r => [r.operation, r.severity]);

test('open: direct campaign refresh, fills the modal; failures and a single campaign persist', async () => {
    const h = harness(); let p = h.click('openCampaignSetup');
    assert.equal(h.calls[0].url, '/api/campaigns');
    await answer(h, {active: 'camp', moved: [], campaigns: CAMPAIGNS}); await p;
    assert.equal(h.node('campaignSetupModal').hidden, false);
    assert.equal(h.node('campaignSetupFrom').innerHTML, '<other>'); assert.equal(h.node('campaignSetupTo').innerHTML, '<camp>');
    assert.deepEqual(h.renders, ['campaigns', 'names']); assert.equal(h.records().length, 0);
    h.node('campaignSetupModal').hidden = true;
    p = h.click('openCampaignSetup'); h.calls.at(-1).reject(new Error('Offline')); await p;
    assert.equal(h.node('campaignSetupModal').hidden, true);
    p = h.click('openCampaignSetup'); await answer(h, {active: 'camp', moved: [], campaigns: [CAMPAIGNS[0]]}); await p;
    assert.deepEqual(h.records().map(r => [r.operation, r.region, r.severity, r.text]), [['setup.transfer.open.validation',
        'campaign', 'error', 'Create a second campaign first; setups can only be added from another campaign']]);
    assert.equal(h.timers.size, 0);
    p = h.click('openCampaignSetup'); await answer(h, {active: 'camp', moved: [], campaigns: CAMPAIGNS}); await p;
    assert.equal(h.records().length, 0);
});

test('submit validation persists in the campaign pane without requests', async () => {
    const h = harness(); h.form.setup = ''; await h.submit();
    h.form.setup = 'Ambush'; h.form.to_campaign = 'other'; await h.submit();
    assert.deepEqual(h.records().map(r => [r.operation, r.region, r.text]), [
        ['setup.transfer.validation', 'campaign', 'Source and target campaign are the same']]);
    assert.equal(h.calls.length, 0); assert.equal(h.timers.size, 0);
    h.form.to_campaign = 'camp'; const p = h.submit(); assert.equal(h.records().length, 0);
    await answer(h, RESULT()); await p;
});

test('copy: exact POST, busy guard, modal closes, success expires without a load', async () => {
    const h = harness(); h.form.mode = 'copy'; h.node('campaignSetupModal').hidden = false;
    const p = h.submit(); h.submit();
    assert.equal(h.calls.length, 1); assert.equal(h.calls[0].url, '/api/campaigns/camp/setups');
    assert.deepEqual(JSON.parse(h.calls[0].options.body), {setup: 'Ambush', from_campaign: 'other', mode: 'copy'});
    assert.equal(h.node('submitTransfer').disabled, true);
    await answer(h, RESULT({mode: 'copy', setup: 'Ambush 2'})); await p;
    assert.deepEqual(h.records().map(r => [r.operation, r.region, r.text]), [
        ['setup.transfer', 'campaign', 'Copied setup Ambush to campaign Camp as Ambush 2']]);
    assert.equal(h.node('campaignSetupModal').hidden, true); assert.equal(h.loads.length, 0);
    assert.equal(h.context.campaignData.campaigns.length, 2); assert.equal(h.node('submitTransfer').disabled, false);
    const timers = [...h.timers.values()]; assert.equal(timers.length, 1); assert.equal(timers[0].delay, 3000);
});

test('moving the loaded setup expects the unloaded scope and refreshes; failures never replay', async () => {
    const h = harness(); h.form.from_campaign = 'camp'; h.form.setup = 'default'; h.form.to_campaign = 'other';
    let p = h.submit(); await answer(h, RESULT({campaign: 'other', setup: 'default'}));
    assert.equal(h.records()[0].text, 'Moved setup default to campaign Other'); assert.equal(h.loads[0].flag, true);
    h.observe(['camp', null, null]); h.loads[0].resolve(); await flush(); await p;
    assert.deepEqual(ops(h), [['setup.transfer', 'success']]);
    p = h.submit(); await answer(h, RESULT({campaign: 'other', setup: 'default'}));
    h.loads[1].reject(new Error('Offline')); await p;
    assert.match(h.records().find(r => r.operation === 'setup.transfer.refresh').text,
        /default was moved to Other, but refreshing the view failed: Offline\. Reload the page; do not repeat the move/);
    assert.equal(h.calls.length, 2);
});

test('request failure persists; cancel during the request keeps the reopened modal open', async () => {
    const h = harness(); let p = h.submit(); h.calls[0].reject(new Error('Setup is already in this campaign')); await p;
    assert.deepEqual(h.records().map(r => [r.operation, r.severity, r.text]), [['setup.transfer', 'error', 'Setup is already in this campaign']]);
    assert.equal(h.timers.size, 0);
    p = h.submit(); h.click('cancelCampaignSetup'); h.node('campaignSetupModal').hidden = false;
    await answer(h, RESULT()); await p;
    assert.equal(h.closed(), 1); assert.equal(h.node('campaignSetupModal').hidden, false);
    assert.deepEqual(ops(h), [['setup.transfer', 'success']]);
});

test('background apply/clear: exact PATCH, shared busy key, guarded refresh', async () => {
    const h = harness(); h.node('backgroundValue').value = '  ';
    let p = h.click('applyBackground'); h.click('clearBackgroundImage'); h.click('applyBackground');
    assert.equal(h.calls.length, 1); assert.equal(h.calls[0].options.method, 'PATCH');
    assert.equal(h.calls[0].url, '/api/display/background'); assert.deepEqual(JSON.parse(h.calls[0].options.body), {background: '#080b14'});
    assert.ok(['applyBackground', 'clearBackgroundImage', 'backgroundImage'].every(id => h.node(id).disabled));
    await answer(h, {}); assert.deepEqual(h.records().map(r => [r.operation, r.region, r.text]), [
        ['background.apply', 'battleSetup', 'View screen background updated. Save the setup to keep it.']]);
    h.loads[0].resolve(); await flush(); await p;
    assert.ok(!h.node('applyBackground').disabled);
    p = h.click('clearBackgroundImage'); assert.deepEqual(JSON.parse(h.calls[1].options.body), {background: '#112233'});
    await answer(h, {}); h.loads[1].reject(new Error('Offline')); await p;
    assert.match(h.records().find(r => r.operation === 'background.clear.refresh').text,
        /background was updated, but refreshing the view failed: Offline\. Reload the page; do not repeat the background change/);
    h.node('backgroundColor').oninput({target: {value: '#abcdef'}}); assert.equal(h.node('backgroundValue').value, '#abcdef');
});

test('background upload: FormData POST, value update, input reset, silent without a file', async () => {
    const h = harness(), input = h.node('backgroundImage');
    await input.onchange({target: input}); assert.equal(h.calls.length, 0);
    input.files = ['file']; input.value = 'C:\\fakepath\\map.png';
    let p = input.onchange({target: input});
    assert.equal(h.calls[0].url, '/api/display/background-image'); assert.equal(h.calls[0].options.body.get('image'), 'file');
    await answer(h, {background: '/uploads/map.png'});
    assert.equal(h.node('backgroundValue').value, '/uploads/map.png');
    assert.equal(h.records()[0].text, 'Background image uploaded. Save the setup to keep it.');
    h.loads[0].resolve(); await flush(); await p; assert.equal(input.value, '');
    input.files = ['file']; input.value = 'x'; p = input.onchange({target: input});
    h.calls[1].reject(new Error('Unsupported image')); await p;
    assert.equal(input.value, ''); assert.deepEqual(ops(h).at(-1), ['background.upload', 'error']);
});

test('stale background results are suppressed after a setup switch', async () => {
    const h = harness(), p = h.click('applyBackground');
    h.observe(['camp', 'camp', 'Two']); await answer(h, {}); await p;
    assert.equal(h.records().length, 0); assert.equal(h.loads.length, 0);
});
