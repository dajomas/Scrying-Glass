const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
let source=fs.readFileSync(path.join(__dirname,'../static/features.js'),'utf8');
source=source.replace("    editable.forEach(id=>$(id).addEventListener", "    globalThis.testApi={refresh}; return;\n    editable.forEach(id=>$(id).addEventListener");
const elements=new Map();
function element(id) {
    if(!elements.has(id))elements.set(id,{value:'',dataset:{},textContent:'',disabled:false,
        replaceChildren(...options){this.options=options;if(options.length&&options[0].value!==undefined)this.value=options[0].value;}});
    return elements.get(id);
}
let serverState;
const summary={checkpoints:[],displays:[],downed:[],undo:null};
const context={document:{getElementById:element,activeElement:null},FormData:class {},
    Option:class {constructor(name,value){this.name=name;this.value=value;}},
    fetch:async url=>({ok:true,json:async()=>url==='/api/state'?serverState:summary})};
vm.runInNewContext(source,context);
const refresh=context.testApi.refresh;
const actor=(id,in_turn=false,extra={})=>({id,name:id,active:true,in_turn,hp:10,max_hp:20,effects:[],...extra});
const state=(turn,scope='campaign')=>({active_campaign_id:scope,characters:[actor('a',turn==='a'),actor('b',turn==='b')],monsters:[actor('m',turn==='m')],lairs:turn==='lair'?[actor('lair',true)]:[]});
(async()=>{
    serverState=state('b');assert.equal(await refresh(),true);
    assert.equal(element('featureTarget').value,'b');
    element('featureTarget').value='a';element('featureTempHp').dataset.dirty='1';element('featureTempHp').value='99';
    assert.equal(await refresh(),true);assert.equal(element('featureTarget').value,'a');
    assert.equal(element('featureTempHp').value,'99');
    serverState=state('m');assert.equal(await refresh(),true);
    assert.equal(element('featureTarget').value,'m');assert.equal(element('featureTempHp').dataset.dirty,undefined);
    assert.equal(element('featureTempHp').value,0);
    serverState=state('a');serverState.characters[0]=actor('a',true,{hp:0,alive:false,life_state:'down'});
    assert.equal(await refresh(),true);assert.equal(element('featureTarget').value,'a');
    assert.equal(element('featureLifeState').value,'down');
    serverState=state('lair');assert.equal(await refresh(),true);assert.equal(element('featureTarget').value,'a');
    element('featureTarget').value='b';serverState=state('a');assert.equal(await refresh(),true);
    assert.equal(element('featureTarget').value,'a');
    element('featureTarget').value='b';serverState=state('a','different');assert.equal(await refresh(),true);
    assert.equal(element('featureTarget').value,'a');
    serverState=state(null);assert.equal(await refresh(),true);assert.equal(element('featureTarget').value,'a');
    console.log('Initial selection, manual override, monster/downed turns, dirty-field refresh, lair transition, scope change and no-turn checks passed.');
})().catch(error=>{console.error(error);process.exitCode=1;});
