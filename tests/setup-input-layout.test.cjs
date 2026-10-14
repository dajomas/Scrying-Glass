const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const html = fs.readFileSync(path.join(__dirname, '../templates/admin/050_setup_input.html'), 'utf8');
const controls = ['setupName', 'newSetup', 'saveSetup', 'setupSelect', 'loadSetup', 'renameSetup', 'deleteSetup'];
test('original controls remain in their original order before Has lair', () => {
    const positions = controls.map(id => html.indexOf(`id="${id}"`));
    assert(positions.every(p => p >= 0));
    for (let i = 1; i < positions.length; i++) assert(positions[i] > positions[i - 1]);
    assert(html.indexOf('id="setupHasLair"') > positions.at(-1));
});
test('no block row splits the setup-name input from the original controls', () => {
    const originalControls = html.slice(html.indexOf('id="setupName"'), html.indexOf('id="deleteSetup"'));
    assert(!originalControls.includes('<div'));
    assert(!originalControls.includes('setupHasLair'));
});
test('checkbox occupies the next row before both import buttons', () => {
    const checkbox = html.indexOf('id="setupHasLair"');
    assert(checkbox < html.indexOf('id="openImport"'));
    assert(checkbox < html.indexOf('id="openMonsterCsvImport"'));
    assert.match(html, /<div class="row">\s*<label for="setupHasLair">/);
    assert.equal((html.match(/id="setupHasLair"/g) || []).length, 1);
});
