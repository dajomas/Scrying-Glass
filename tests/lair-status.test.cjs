const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../static/lair-status.js'),'utf8');
const classes=new Set();let install,writes=0,text='Checking lair status…',calls=0;
const note={get textContent(){return text;},set textContent(value){writes++;text=value;},
    classList:{toggle(name,on){if(on)classes.add(name);else classes.delete(name);}}};
const context={window:{},document:{readyState:'interactive',getElementById(){return note;},
    addEventListener(event,callback){assert.equal(event,'DOMContentLoaded');install=callback;}}};
vm.runInNewContext(source,context);
context.window.scryingLairsRender=function(snapshot,extra){calls++;assert.equal(extra,'extra');return 42;};
install();
const render=snapshot=>{assert.equal(context.window.scryingLairsRender(snapshot,'extra'),42);};
render({lairs:[]});assert.equal(text,'No Lair');assert(classes.has('no-active-lair'));
render({lairs:[{name:'Dragon cave',active:false}]});assert.equal(text,'Lair: Dragon cave');assert(!classes.has('has-active-lair'));
render({lairs:[{name:'Dragon cave',active:true,visible:false,in_turn:false}]});assert.equal(text,'Active Lair: Dragon cave');assert(classes.has('has-active-lair'));
const before=writes;render({lairs:[{name:'Dragon cave',active:true}]});assert.equal(writes,before);
render({lairs:[{name:'Dragon cave',active:false,in_turn:true}]});assert.equal(text,'Lair: Dragon cave');
render({lairs:[]});assert.equal(text,'No Lair');
render({lairs:[{name:'<b>Untrusted</b>',active:true}]});assert.equal(text,'Active Lair: <b>Untrusted</b>');
render({});assert.equal(text,'No Lair');assert.equal(calls,8);
console.log('Exact three-state wording, status transitions, hook preservation, text safety and unchanged-render checks passed.');
