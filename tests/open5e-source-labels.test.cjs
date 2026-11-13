'use strict';
// Open5e candidate labels and popup ordering (SG-TODO-017 Stage 2).
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../static/admin/010-source.js'), 'utf8');
const label = source.slice(0, source.indexOf('\nlet latest;'));
const context = vm.createContext({});
vm.runInContext(label, context);

test('Open5e labels use the provider / book [/ legacy] layout', () => {
    const candidate = Object.freeze({provider: 'Open5e', source: '5e 2014 Rules', game_system: '5th Edition 2014', legacy: true});
    assert.equal(context.monsterSourceLabel(candidate, true), 'Open5e / 5e 2014 Rules / legacy');
    assert.equal(context.monsterSourceLabel(candidate), 'Open5e (5e 2014 Rules)');
    assert.equal(context.monsterSourceLabel({provider: 'Open5e', source: 'Tome of Beasts'}, true), 'Open5e / Tome of Beasts');
    assert.equal(context.monsterSourceLabel({provider: 'Open5e'}, true), 'Open5e / Source unavailable');
});

test('existing provider labels are unchanged', () => {
    assert.equal(context.monsterSourceLabel({provider: '5e.tools', source: 'MM'}, true), '5e.tools / Monster Manuals 2014');
    assert.equal(context.monsterSourceLabel({provider: 'D&D Beyond', source: 'Basic Rules', legacy: true}, true),
        'D&D Beyond / Basic Rules / legacy');
});

test('candidate popup renders attribution as text only', () => {
    const script = fs.readFileSync(path.join(__dirname, '../static/monster-candidate-selection.js'), 'utf8');
    assert.match(script, /credit\.textContent = ` \$\{candidate\.attribution\}`/);
    assert.doesNotMatch(script, /innerHTML/);
});

test('candidate popup keeps provider order and sorts rows by book within a provider', () => {
    const script = fs.readFileSync(path.join(__dirname, '../static/monster-candidate-selection.js'), 'utf8');
    const start = script.indexOf('const providerRank');
    const end = script.indexOf('rows.map(row => row.candidate)');
    assert.ok(start > 0 && end > start);
    const sorter = new Function('candidates', 'monsterSourceLabel',
        script.slice(start, end) + 'return rows.map(row => row.candidate.id);');
    const candidates = [
        {id: 1, provider: 'D&D Beyond', source: 'Monster Manual', legacy: false},
        {id: 2, provider: 'D&D Beyond', source: 'Basic Rules', legacy: true},
        {id: 3, provider: '5e.tools', source: 'XMM'},
        {id: 4, provider: '5e.tools', source: 'MM'},
        {id: 5, provider: 'Open5e', source: 'Tome of Beasts'},
        {id: 6, provider: 'Open5e', source: 'Black Flag SRD'},
        {id: 7, provider: 'Open5e', source: '5e 2014 Rules', legacy: true},
    ];
    assert.deepEqual(sorter(candidates, context.monsterSourceLabel), [2, 1, 4, 3, 7, 6, 5]);
});
