'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../static/admin-notification-layout.js'), 'utf8');
const ids = ['campaignNotification', 'characterAddNotification',
             'battleSetupNotification', 'monsterAddNotification'];

function fixture(values = {}, missing = []) {
    const notices = Object.fromEntries(ids.filter(id => !missing.includes(id)).map(id =>
        [id, {textContent: values[id] ?? ' ', hidden: false}]));
    const observers = [];
    const context = vm.createContext({window: {}, document: {
        getElementById: id => notices[id] || null,
    }, MutationObserver: class {
        constructor(callback) { this.callback = callback; }
        observe(target, options) { observers.push({target, options, callback: this.callback}); }
    }});
    vm.runInContext(source, context);
    return {notices, observers, context};
}

test('initial whitespace is hidden and meaningful messages are preserved', () => {
    const text = '  Save failed: enter initiative.  ';
    const {notices} = fixture({campaignNotification: text,
        characterAddNotification: '\t\n', battleSetupNotification: '\u00a0'});
    assert.equal(notices.campaignNotification.hidden, false);
    assert.equal(notices.campaignNotification.textContent, text);
    for (const id of ids.slice(1)) assert.equal(notices[id].hidden, true);
});

test('each notice reappears for content and collapses after text is cleared', () => {
    const {observers} = fixture();
    assert.equal(observers.length, 4);
    for (const {target, options, callback} of observers) {
        assert.deepEqual({...options}, {childList: true, characterData: true, subtree: true});
        target.textContent = 'Saved successfully';
        callback();
        assert.equal(target.hidden, false);
        target.textContent = ' ';
        callback();
        assert.equal(target.hidden, true);
        assert.equal(target.textContent, ' ');
        target.textContent = '';
        callback();
        assert.equal(target.hidden, true);
    }
});

test('duplicate installation does not add observers', () => {
    const {context, observers} = fixture();
    vm.runInContext(source, context);
    assert.equal(observers.length, 4);
});

test('missing elements are tolerated', () => {
    assert.equal(fixture({}, ids).observers.length, 0);
});
