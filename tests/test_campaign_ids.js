// Node-only checks of the actual campaign UI helper functions (not a browser test).
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../static/admin.js'), 'utf8');
const names = ['campaignById', 'activeCampaign', 'campaignOptions', 'syncActiveBattleSetupControls', 'renderActiveBattleSetup'];
const functions = names.map(name => {
  const match = source.match(new RegExp('function ' + name + '\\([^]*?\\n\\}', 'm'));
  assert.ok(match, 'Missing helper ' + name);
  return match[0];
}).join('\n');
const controls = {
  '#setupName': {value: ''},
  '#setupSelect': {value: '', options: [{value: 'fight'}]},
  '#activeBattleSetupInfo': {textContent: '', innerHTML: ''},
};
const context = {
  campaignData: {active: '12', campaigns: [{id: '12', name: 'Original', setups: ['fight']}, {id: '13', name: 'Second', setups: []}]},
  latest: {active_setup: {campaign_id: '12', name: 'fight'}},
  document: {querySelector: key => controls[key]},
  esc: value => String(value),
};
vm.createContext(context);
vm.runInContext(functions, context);
assert.equal(context.campaignById('12').name, 'Original');
assert.equal(context.campaignById('Original'), null);
assert.equal(context.activeCampaign().id, '12');
assert.ok(context.campaignOptions('12').includes('value="12" selected'));
context.syncActiveBattleSetupControls();
assert.equal(controls['#setupName'].value, 'fight');
context.renderActiveBattleSetup();
assert.ok(controls['#activeBattleSetupInfo'].innerHTML.includes('fight'));
context.campaignData.campaigns[0].name = 'Renamed';
assert.equal(context.activeCampaign().id, '12');
assert.ok(context.campaignOptions('12').includes('Renamed'));
assert.ok(context.campaignOptions('12').includes('value="12" selected'));
assert.ok(!source.includes('.slug'));
assert.ok(!source.includes('activeSetup.campaign !=='));
console.log('PASS: campaign UI ID lookup, selection, active setup and rename checks');
