const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../static/lair-status.js'), 'utf8');
function setup(readyState='interactive', latest=null) {
    const classes = new Set();
    let writes = 0, text = 'Checking lair status…', install;
    const note = {classList: {toggle(name, enabled) {if(enabled)classes.add(name);else classes.delete(name);}},
        get textContent() {return text;}, set textContent(value) {writes++;text=value;}};
    const context = {latest, window: {}, document: {readyState,
        getElementById() {return note;}, addEventListener(event, callback) {assert.equal(event,'DOMContentLoaded');install=callback;}}};
    vm.runInNewContext(source,context);
    return {context,note,classes,install:()=>install(),writes:()=>writes};
}
const env=setup();
assert.equal(env.context.window.scryingLairsRender,undefined);
let calls=0, receiver, passed;
env.context.window.scryingLairsRender=function(snapshot, extra) {calls++;receiver=this;passed=extra;return 'original-result';};
env.install();
const render=env.context.window.scryingLairsRender;
const owner={};
assert.equal(render.call(owner,{lairs:[]},'extra'),'original-result');
assert.equal(receiver,owner);assert.equal(passed,'extra');assert.equal(calls,1);
assert.equal(env.note.textContent,'No active lair.');assert(env.classes.has('no-active-lair'));
render({lairs:[{name:'Dragon cave',active:true,visible:false,in_turn:false}]});
assert.equal(env.note.textContent,'Active lair: Dragon cave');assert(env.classes.has('has-active-lair'));assert(!env.classes.has('no-active-lair'));
const writes=env.writes();render({lairs:[{name:'Dragon cave',active:true}]});assert.equal(env.writes(),writes);
render({lairs:[{name:'Dragon cave',active:false,in_turn:true}]});assert.equal(env.note.textContent,'No active lair.');
render({lairs:[]});assert.equal(env.note.textContent,'No active lair.');
render({lairs:[{name:'<b>Unsafe name</b>',active:true}]});assert.equal(env.note.textContent,'Active lair: <b>Unsafe name</b>');
render({lairs:[{active:true}]});assert.equal(env.note.textContent,'Active lair: Lair');
render({lairs:[{name:'A',active:true},{name:'B',active:true}]});assert.equal(env.note.textContent,'Active lairs: A, B');
const initial=setup('interactive',{lairs:[{name:'Initial',active:true}]});initial.install();assert.equal(initial.note.textContent,'Active lair: Initial');
const loaded=setup('complete',{lairs:[]});assert.equal(loaded.note.textContent,'No active lair.');
console.log('Deferred installation, hook preservation, active/inactive/removal, visibility independence, initial render, text safety and duplicate-announcement checks passed.');
