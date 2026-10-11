const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../static/bulk-select-all.js'),'utf8');
function select() {
    const s={options:[]};
    for(const value of ['','select-all','unselect-all','remove']) {
        const option={value,after(newOption){s.options.splice(s.options.indexOf(this)+1,0,newOption);}};
        s.options.push(option);
    }
    return s;
}
const menus={characterBulkAction:select(),monsterBulkAction:select()};
const sets={characters:new Set(['standing','stale']),monsters:new Set(['living'])};
const characters=[{id:'standing',alive:true,life_state:'standing'},{id:'down',alive:false,life_state:'down'},
    {id:'stable',alive:false,life_state:'stable'},{id:'dead',alive:false,life_state:'dead'},
    {id:'failed',alive:false,life_state:'down',death_failures:3}];
const monsters=[{id:'living',alive:true},{id:'dead-monster',alive:false},{id:'explicit-dead',alive:true,life_state:'dead'}];
const boxes={characters:characters.map(x=>({dataset:{selectId:x.id},checked:true})),
    monsters:monsters.map(x=>({dataset:{selectId:x.id},checked:true}))};
let buttonHandler,delegated=[],notices=[];
const context={latest:{characters,monsters},
    Option:class {constructor(text,value){this.text=text;this.value=value;}},
    document:{getElementById:id=>menus[id],querySelectorAll(selector){
        if(selector==='button[data-select-all-kind]')return [{dataset:{selectAllKind:'characters'},addEventListener(event,handler){buttonHandler=handler;}}];
        return selector.includes('"characters"')?boxes.characters:boxes.monsters;
    }},
    setAllSelected(kind,value){sets[kind].clear();if(value)context.latest[kind].forEach(x=>sets[kind].add(x.id));boxes[kind].forEach(x=>{x.checked=value;});},
    updateRowSelection(kind,id,checked){if(checked)sets[kind].add(id);else sets[kind].delete(id);},
    async runBulkAction(kind,action){delegated.push([kind,action]);return 'original';},
    paneNotification(kind,text){notices.push([kind,text]);}};
vm.runInNewContext(source,context);
(async()=>{
    for(const menu of Object.values(menus))assert.deepEqual(menu.options.map(x=>x.value),['','select-all','select-dead','unselect-all','remove']);
    await context.runBulkAction('characters','select-dead');
    assert.deepEqual([...sets.characters],['dead','failed']);
    assert.deepEqual(boxes.characters.filter(x=>x.checked).map(x=>x.dataset.selectId),['dead','failed']);
    assert.deepEqual([...sets.monsters],['living']);
    await context.runBulkAction('monsters','select-dead');
    assert.deepEqual([...sets.monsters],['dead-monster','explicit-dead']);
    assert.equal(await context.runBulkAction('characters','remove'),'original');assert.deepEqual(delegated,[['characters','remove']]);
    buttonHandler();assert.equal(sets.characters.size,characters.length);
    context.latest.characters=[{id:'standing',life_state:'standing',alive:true}];
    await context.runBulkAction('characters','select-dead');assert.equal(sets.characters.size,0);assert(notices.at(-1)[1].includes('0 dead'));
    context.latest=null;await context.runBulkAction('monsters','select-dead');
    console.log('Menu position, permanent-death character rules, monster death, selection sets/checkboxes, pane isolation, empty results and original actions passed.');
})().catch(error=>{console.error(error);process.exitCode=1;});
