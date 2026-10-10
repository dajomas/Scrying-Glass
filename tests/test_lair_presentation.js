/* DOM-mock regression checks for lair color preview and viewer name-only rendering. */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.resolve(__dirname,'..');
const previewSource=fs.readFileSync(path.join(root,'static/lair-color-preview.js'),'utf8');
let count=0;
function test(name,fn){fn();count++;console.log('PASS: '+name);}
function picker(){
 const input={value:'#8064a2',listeners:{},addEventListener(k,fn){(this.listeners[k]??=[]).push(fn);}};
 const preview={style:{},dataset:{}};let dirty=false,received=null;
 const original=function(...args){received={receiver:this,args};if(!dirty)input.value=args[0].color;return 'rendered';};
 const sandbox={document:{getElementById:id=>id==='lairColor'?input:id==='lairColorPreview'?preview:null},window:{scryingLairsRender:original}};
 vm.createContext(sandbox);vm.runInContext(previewSource,sandbox);
 return {input,preview,sandbox,dirty(value){dirty=value;},received(){return received;},emit(name){input.listeners[name].forEach(fn=>fn());}};
}
test('initial marker matches picker',()=>{const p=picker();assert.equal(p.preview.style.backgroundColor,'#8064a2');});
test('input edits update marker immediately',()=>{const p=picker();p.input.value='#112233';p.emit('input');assert.equal(p.preview.style.backgroundColor,'#112233');});
test('change events update marker',()=>{const p=picker();p.input.value='#aabbcc';p.emit('change');assert.equal(p.preview.style.backgroundColor,'#aabbcc');});
test('programmatic setup refresh updates marker and preserves renderer contract',()=>{
 const p=picker(),state={color:'#123456'},receiver={};
 const result=p.sandbox.window.scryingLairsRender.call(receiver,state,'extra');
 assert.equal(result,'rendered');assert.equal(p.preview.style.backgroundColor,'#123456');
 assert.equal(p.received().receiver,receiver);assert.equal(p.received().args[0],state);assert.equal(p.received().args[1],'extra');
});
test('refresh respects unsaved picker color',()=>{const p=picker();p.input.value='#ff0000';p.dirty(true);p.sandbox.window.scryingLairsRender({color:'#00ff00'});assert.equal(p.preview.style.backgroundColor,'#ff0000');});
test('duplicate script evaluation does not duplicate listeners',()=>{const p=picker();vm.runInContext(previewSource,p.sandbox);assert.equal(p.input.listeners.input.length,1);});
test('missing preview elements are harmless',()=>{const s={window:{},document:{getElementById:()=>null}};vm.runInNewContext(previewSource,s);});
const clientSource=fs.readFileSync(path.join(root,'static/client.js'),'utf8');
function viewer(){
 const initiative={innerHTML:'',hidden:false,querySelector:()=>null,prepend(){}};
 const stage={innerHTML:'',style:{}},campaign={};
 const sandbox={document:{body:{style:{}},querySelector:selector=>({'#initiative':initiative,'#stage':stage,'#clientCampaign':campaign}[selector])},applyBattleOrderFontSize(){},clearTimeout(){}};
 vm.createContext(sandbox);vm.runInContext(clientSource.slice(0,clientSource.indexOf('function connectDisplay()')),sandbox);
 return {sandbox,initiative};
}
const lair={id:'l',kind:'lair',name:'Volcano',active:true,visible:true,in_turn:true,color:'#8064a2',initiative:20,effects:[{name:'Should not appear'}]};
test('lair content is exactly its escaped name',()=>{const v=viewer();assert.equal(v.sandbox.initiativeTokenContent(lair),'Volcano');});
test('lair names are escaped',()=>{const v=viewer();assert.equal(v.sandbox.initiativeTokenContent({...lair,name:'<Lair & "fire">'}),'&lt;Lair &amp; &quot;fire&quot;&gt;');});
test('actual viewer token contains only lair name while retaining turn/color',()=>{
 const v=viewer();v.sandbox.render({characters:[],monsters:[],lairs:[lair],battle_order:['l'],battle_round:0,display:{}});
 const token=v.initiative.innerHTML;assert.equal(token.replace(/<[^>]*>/g,'').trim(),'Volcano');
 assert(!token.includes('Lair action'));assert(!token.includes('Initiative'));assert(!token.includes('Should not appear'));assert(!token.includes('(down)'));
 assert.match(token,/class="token lair turn"/);assert(token.includes('background:#8064a2'));
});
test('hidden lair is omitted',()=>{const v=viewer();v.sandbox.render({characters:[],monsters:[],lairs:[{...lair,visible:false}],battle_order:['l'],battle_round:0,display:{}});assert.equal(v.initiative.innerHTML,'');});
test('character status and effects remain unchanged',()=>{const v=viewer();const text=v.sandbox.initiativeTokenContent({name:'Hero',alive:false,life_state:'down',effects:[{name:'Prone'}]});assert(text.includes('(down)'));assert(text.includes('effect-badge'));assert(text.includes('Prone'));});
test('ally monster label remains unchanged',()=>{const v=viewer();assert(v.sandbox.initiativeTokenContent({name:'Goblin',monster_species:'Goblin',ally:true,alive:true}).includes('Goblin - Ally'));});
test('template uses shared marker styles and preview script follows lair script',()=>{
 const template=fs.readFileSync(path.join(root,'templates/admin/185_lair_tools.html'),'utf8');
 assert.match(template,/class="color-picker-control"/);assert.match(template,/id="lairColorPreview" class="turn-marker color-picker-preview"/);
 assert.match(template,/aria-hidden="true"/);assert.equal((template.match(/id="lairColorPreview"/g)||[]).length,1);
 const scripts=fs.readFileSync(path.join(root,'templates/admin/190_document_end.html'),'utf8');
 assert(scripts.indexOf('/static/lairs.js')<scripts.indexOf('/static/lair-color-preview.js'));
});
console.log(`${count} lair-presentation checks passed`);
