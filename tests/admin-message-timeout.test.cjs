const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');
const source = fs.readFileSync(path.join(__dirname, '../static/admin-message-timeout.js'), 'utf8');
function setup(initial = '', missing = false) {
    let now = 0, next = 1, notify;
    const timers = new Map();
    const area = {textContent: initial};
    const context = {document: {getElementById: () => missing ? null : area},
        MutationObserver: class {
            constructor(callback) {notify = callback;}
            observe(node, options) {assert.equal(node, area);assert(options.childList && options.characterData && options.subtree);}
        },
        setTimeout(callback, delay) {const id = next++;timers.set(id, {callback, due: now + delay});return id;},
        clearTimeout(id) {timers.delete(id);}};
    vm.createContext(context);vm.runInContext(source, context);
    function advance(ms) {
        const until = now + ms;
        while (true) {
            const ready = [...timers].filter(([, t]) => t.due <= until).sort((a, b) => a[1].due - b[1].due)[0];
            if (!ready) break;
            now = ready[1].due;timers.delete(ready[0]);ready[1].callback();notify();
        }
        now = until;
    }
    return {area, timers, advance, write(text) {area.textContent = text;notify();}};
}
test('clears at five seconds, not earlier', () => {
    const w = setup();w.write('Error');w.advance(4999);assert.equal(w.area.textContent, 'Error');
    w.advance(1);assert.equal(w.area.textContent, '');assert.equal(w.timers.size, 0);
});
test('replacement message gets its own full timeout', () => {
    const w = setup();w.write('First');w.advance(4000);w.write('Second');w.advance(1000);
    assert.equal(w.area.textContent, 'Second');w.advance(4000);assert.equal(w.area.textContent, '');
});
test('repeating the same text restarts the timer', () => {
    const w = setup();w.write('Error');w.advance(4000);w.write('Error');w.advance(1000);
    assert.equal(w.area.textContent, 'Error');w.advance(4000);assert.equal(w.area.textContent, '');
});
test('manual clearing cancels the timeout', () => {
    const w = setup();w.write('Error');w.advance(1000);w.write('');
    assert.equal(w.timers.size, 0);w.advance(5000);assert.equal(w.area.textContent, '');
});
test('pre-existing message gets a timeout on installation', () => {
    const w = setup('Already visible');w.advance(5000);assert.equal(w.area.textContent, '');
});
test('empty or missing message element creates no timeout', () => {
    assert.equal(setup().timers.size, 0);assert.equal(setup('', true).timers.size, 0);
});
