const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../static/admin.js'), 'utf8');
const block = source.slice(source.indexOf('function activeBattleTargets()'), source.indexOf("document.addEventListener('click', async event => {", source.indexOf('function activeBattleTargets()')));
const controls = {};
const rows = {children: [], appendChild(row) {this.children.push(row);}};
function row() {
    const fields = {};
    const get = selector => fields[selector] ||= {value: selector==='[data-action-kind]'?'damage':'1', required:false, hidden:false, addEventListener(){}, parentElement:{hidden:false}};
    return {className:'', innerHTML:'', querySelector:get, remove(){}};
}
const ctx = {latest:{monsters:[{id:'m',name:'Dead Mephit',active:true,alive:false,in_turn:true}],characters:[{id:'c',name:'Paladin',active:true,alive:true}]},
    battleActionRows:rows,battleActionForm:{},battleActionModal:{addEventListener(){}},battleActionsApplying:false, battleActionActorId:null,
    document:{createElement:row,querySelector:id=>controls[id] ||= {}},esc:x=>String(x),message(){}};
vm.runInNewContext(block,ctx);
ctx.addBattleActionRow(true);
assert.match(rows.children[0].className,/battle-reaction-row/);
assert.match(rows.children[0].innerHTML,/data-action-source/);
assert.match(rows.children[0].innerHTML,/Dead Mephit/);
assert.doesNotMatch(rows.children[0].innerHTML,/value="buff"/);
ctx.addBattleActionRow();
assert.doesNotMatch(rows.children[1].innerHTML,/data-action-source/);
assert.match(rows.children[1].innerHTML,/value="buff"/);
ctx.openBattleActions('m');
assert.equal(ctx.battleActionActorId,'m');
assert.equal(ctx.battleActionModal.hidden,false);
console.log('Reaction row and dead turn owner popup tests passed.');
