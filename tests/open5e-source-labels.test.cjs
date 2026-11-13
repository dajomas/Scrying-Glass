'use strict';
// Open5e candidate labels show document and game system (SG-TODO-017 Stage 2).
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../static/admin/010-source.js'), 'utf8');
const label = source.slice(0, source.indexOf('\nlet latest;'));
const context = vm.createContext({});
vm.runInContext(label, context);

test('Open5e labels name the document, game system and provider', () => {
    const candidate = Object.freeze({provider: 'Open5e', source: '5e 2014 Rules', game_system: '5th Edition 2014'});
    assert.equal(context.monsterSourceLabel(candidate, true), '5e 2014 Rules, 5th Edition 2014 (Open5e)');
    assert.equal(context.monsterSourceLabel(candidate), 'Open5e (5e 2014 Rules, 5th Edition 2014)');
    assert.equal(context.monsterSourceLabel({provider: 'Open5e', source: 'Tome of Beasts'}, true), 'Tome of Beasts (Open5e)');
    assert.equal(context.monsterSourceLabel({provider: 'Open5e'}, true), 'Source unavailable (Open5e)');
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
