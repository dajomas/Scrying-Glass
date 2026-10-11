const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
let source=fs.readFileSync(path.join(__dirname,'../static/battle-turn-actions.js'),'utf8');
source=source.replace("if (document.readyState === 'loading')", "globalThis.testExports={buildTurnActions,reorderCriticalFields}; if (document.readyState === 'loading')");
const context={document:{readyState:'loading',addEventListener(){}}};
vm.runInNewContext(source,context);
const {buildTurnActions,reorderCriticalFields}=context.testExports;
const build=(...args)=>JSON.parse(JSON.stringify(buildTurnActions(...args)));
assert.deepEqual(build('actor','','0'),[]);
assert.deepEqual(build('actor','5','3').map(x=>x.action),['damage','heal']);
for(const value of ['-1','1.5','100000','NaN','Infinity'])assert.throws(()=>build('actor',value,''));
class Element {
    constructor(kind){this.kind=kind;this.children=[];this.parentNode=null;this.attributes={};this.hidden=false;this.checked=false;this.moves=0;}
    append(child){if(child.parentNode)child.parentNode.children.splice(child.parentNode.children.indexOf(child),1);this.children.push(child);child.parentNode=this;}
    contains(other){return this===other||this.children.some(x=>x.contains(other));}
    closest(selector){const kind=selector.slice(1);for(let x=this;x;x=x.parentNode)if(x.kind===kind)return x;return null;}
    get parentElement(){return this.parentNode;}
    get nextElementSibling(){const siblings=this.parentNode?.children||[];return siblings[siblings.indexOf(this)+1]||null;}
    before(child){child.moves++;if(child.parentNode)child.parentNode.children.splice(child.parentNode.children.indexOf(child),1);const siblings=this.parentNode.children;siblings.splice(siblings.indexOf(this),0,child);child.parentNode=this.parentNode;}
    hasAttribute(key){return key in this.attributes;}
    setAttribute(key,value){this.attributes[key]=value;}
    querySelector(selector){const kind=selector==='.amount-field'?'amount-field':selector==='[data-action-critical]'?'checkbox':null;let found=null;const visit=x=>{if(found)return;if(x.kind===kind)found=x;else x.children.forEach(visit);};this.children.forEach(visit);return found;}
    querySelectorAll(selector){return this.children.filter(x=>x.kind===selector.slice(1));}
}
const rows=new Element('rows'),row=new Element('battle-action-row');rows.append(row);
const target=new Element('target'),action=new Element('action'),amount=new Element('amount-field'),remove=new Element('remove');
[target,action,amount,remove].forEach(x=>row.append(x));
const input=new Element('amount-input'),critical=new Element('critical-option'),checkbox=new Element('checkbox');
amount.append(input);amount.append(critical);critical.append(checkbox);checkbox.checked=true;
reorderCriticalFields(rows);
assert.deepEqual(row.children.map(x=>x.kind),['target','action','critical-option','amount-field','remove']);
assert.equal(checkbox.parentElement,critical);assert.equal(checkbox.checked,true);
assert.deepEqual(amount.children,[input]);assert.equal(checkbox.attributes['aria-label'],'Critical hit');
reorderCriticalFields(rows);assert.equal(critical.moves,1);
// Same visibility/reset logic used by admin.js, after relocation.
for(const kind of ['heal','buff','debuff','damage']) {
    checkbox.parentElement.hidden=kind!=='damage';
    if(kind!=='damage')checkbox.checked=false;
    assert.equal(critical.hidden,kind!=='damage');
    assert.equal(checkbox.checked,false);
    reorderCriticalFields(rows);assert.equal(critical.moves,1);
}
const newRow=new Element('battle-action-row');rows.append(newRow);
const newAmount=new Element('amount-field'),newCritical=new Element('critical-option'),newCheck=new Element('checkbox');
newRow.append(newAmount);newAmount.append(newCritical);newCritical.append(newCheck);
reorderCriticalFields(rows);assert.equal(newCritical.nextElementSibling,newAmount);
const empty=new Element('battle-action-row');rows.append(empty);reorderCriticalFields(rows);
assert.match(source,/rowObserver\.disconnect\(\);[\s\S]*finally \{ rowObserver\.observe\(rows, options\); \}/);
assert.equal(source.includes('confirm('),false);
console.log('Nested span relocation, DOM order, idempotence, checkbox identity/state, action visibility, new rows, payload validation and observer guards passed.');
