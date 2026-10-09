const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(path.join(__dirname,'../static/encounter-visibility.js'),'utf8');
const window={};vm.runInNewContext(source,{window,document:{getElementById:()=>null}});
let count=0;
function test(fn){fn();count++;}
function setup(){const renders=[];return {c:window.createEncounterVisibility(value=>renders.push(value)),renders};}
test(()=>{const {c,renders}=setup();assert.equal(c.visible,false);assert.deepEqual(renders,[false]);});
test(()=>{const {c}=setup();c.toggle();assert.equal(c.visible,true);c.toggle();assert.equal(c.visible,false);});
test(()=>{const {c}=setup();c.update({battle_round:1});assert.equal(c.visible,true);c.update({battle_round:0});assert.equal(c.visible,false);});
test(()=>{const {c}=setup();c.toggle();c.update({battle_round:1});c.toggle();assert.equal(c.visible,false);c.update({battle_round:0});assert.equal(c.visible,true);});
test(()=>{const {c}=setup();c.update({battle_round:1});c.toggle();c.update({battle_round:2});assert.equal(c.visible,false);});
test(()=>{const {c}=setup();c.update({battle_round:1});c.update({battle_round:1});c.update({battle_round:0});assert.equal(c.visible,false);});
test(()=>{const {c}=setup();c.update({battle_round:1});c.update({battle_round:0});c.toggle();c.update({battle_round:1});c.update({battle_round:0});assert.equal(c.visible,true);});
test(()=>{const {c}=setup();c.update({battle_round:1,battle_order:[]});assert.equal(c.visible,true);c.update({battle_round:2,battle_order:[]});assert.equal(c.inBattle,true);});
test(()=>{const {c}=setup();c.update({});assert.equal(c.visible,false);});
test(()=>{const {c}=setup();c.update({battle_round:1});c.update({battle_round:0});assert.equal(c.inBattle,false);assert.equal(c.visible,false);});
console.log(count+' visibility state-machine tests passed');
