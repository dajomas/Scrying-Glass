const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');
const source = fs.readFileSync(path.join(__dirname, '../static/admin.js'), 'utf8');

function rendererSource(text) {
    const start = text.indexOf('function tieUI()');
    const end = text.indexOf('function swapTiePosition(', start);
    assert.ok(start >= 0 && end > start, 'Cannot isolate tieUI(): renderer boundaries changed');
    // Exclude swapTiePosition and the browser-only listener registration.
    return text.slice(start, end);
}
const fn = rendererSource(source);

function selections(html) {
    return [...html.matchAll(/<select\b[^>]*\bdata-tie-member="([^"]+)"[^>]*>([\s\S]*?)<\/select>/g)]
        .map(match => {
            const selected = [...match[2].matchAll(/<option\b([^>]*)>/g)]
                .filter(option => /\bselected(?:\s|=|$)/.test(option[1]));
            assert.equal(selected.length, 1, `Expected one selected position for ${match[1]}`);
            const value = selected[0][1].match(/\bvalue="(\d+)"/);
            assert.ok(value, `Missing numeric selected position for ${match[1]}`);
            return [match[1], Number(value[1])];
        });
}

function render(buckets, characterIds) {
    const before = JSON.stringify(buckets);
    const sandbox = {latest: {characters: characterIds.map(id => ({id}))},
        tiedBuckets: () => buckets, esc: String};
    vm.createContext(sandbox);
    vm.runInContext(fn + '; result = tieUI();', sandbox);
    assert.equal(JSON.stringify(buckets), before, 'Rendering must not mutate source buckets');
    return sandbox.result;
}
function defaults(ids, characterIds) {
    const members = ids.map(id => ({id, name: id}));
    const positions = selections(render([{initiative: 12, members}], characterIds));
    assert.equal(positions.length, ids.length, 'Every combatant must have a rendered selection');
    return positions;
}
test('mixed ties default to characters first with stable within-kind order', () => {
    assert.deepEqual(defaults(['m2', 'c2', 'm1', 'c1'], ['c1', 'c2']),
        [['c2', 1], ['c1', 2], ['m2', 3], ['m1', 4]]);
});
test('monster-only ties retain order', () => {
    assert.deepEqual(defaults(['m2', 'm1'], []), [['m2', 1], ['m1', 2]]);
});
test('character-only ties retain order', () => {
    assert.deepEqual(defaults(['c2', 'c1'], ['c1', 'c2']), [['c2', 1], ['c1', 2]]);
});
test('empty ties render no controls', () => {
    assert.equal(render([], []), '');
    assert.deepEqual(selections(render([], [])), []);
});
test('each initiative bucket receives independent one-based positions', () => {
    const html = render([
        {initiative: 18, members: [{id:'m1', name:'M1'}, {id:'c1', name:'C1'}]},
        {initiative: 7, members: [{id:'m2', name:'M2'}, {id:'c2', name:'C2'}]},
    ], ['c2', 'c1']);
    assert.deepEqual(selections(html), [['c1',1], ['m1',2], ['c2',1], ['m2',2]]);
    assert.match(html, /data-tie-bucket="0" data-tie-member="c1" data-tie-position="1"/);
    assert.match(html, /data-tie-bucket="1" data-tie-member="c2" data-tie-position="1"/);
});
test('rendering accepts frozen input without reordering source members', () => {
    const members = Object.freeze([Object.freeze({id:'m',name:'M'}), Object.freeze({id:'c',name:'C'})]);
    const buckets = Object.freeze([Object.freeze({initiative:10, members})]);
    assert.deepEqual(selections(render(buckets, ['c'])), [['c',1], ['m',2]]);
    assert.deepEqual(members.map(x => x.id), ['m','c']);
});
test('position parser tolerates attributes after the combatant ID', () => {
    assert.deepEqual(selections('<select data-tie-member="c" data-tie-position="2" aria-label="Position"><option value="1">1</option><option value="2" selected>2</option></select>'), [['c',2]]);
});
test('position parser rejects missing or ambiguous selected positions', () => {
    assert.throws(() => selections('<select data-tie-member="c"><option value="1">1</option></select>'), /one selected position/);
    assert.throws(() => selections('<select data-tie-member="c"><option value="1" selected>1</option><option value="2" selected>2</option></select>'), /one selected position/);
});
test('isolated renderer excludes swap handler and browser event registration', () => {
    assert.doesNotMatch(fn, /function swapTiePosition|document\./);
    assert.deepEqual(defaults(['m','c'], ['c']), [['c',1], ['m',2]]);
});
test('changed source boundaries produce an explicit fixture failure', () => {
    assert.throws(() => rendererSource('function tieUI() {}'), /renderer boundaries changed/);
    assert.throws(() => rendererSource('function swapTiePosition() {}'), /renderer boundaries changed/);
});
