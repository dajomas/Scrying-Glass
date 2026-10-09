/* Focused DOM-contract tests; no browser rendering is claimed. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const code=fs.readFileSync(path.join(__dirname,'../static/campaign-backups.js'),'utf8');
let passed=0;
function fixture(options={}) {
    let moved=false,callback=null,appends=0;
    const classes=new Set();
    const panel={classList:{add:name=>classes.add(name)},querySelector:selector=>options.badControls?null:{id:selector.slice(1)}};
    const campaign={querySelector:()=>moved?panel:null,appendChild:node=>{assert.equal(node,panel);moved=true;appends++;}};
    const doc={readyState:options.loading?'loading':'interactive',getElementById:()=>options.noCampaign?null:campaign,querySelector:()=>options.noPanel||moved?null:panel,addEventListener:(name,fn,settings)=>{assert.equal(name,'DOMContentLoaded');assert.equal(settings.once,true);callback=fn;}};
    const sandbox={document:doc,console:{warn:()=>{}}};vm.createContext(sandbox);
    return {run:()=>vm.runInContext(code,sandbox),ready:()=>callback(),getMoved:()=>moved,getAppends:()=>appends,classes};
}
function test(fn){fn();passed++;}
test(()=>{const f=fixture();f.run();assert.equal(f.getMoved(),true);assert(f.classes.has('campaign-backups-panel'));});
test(()=>{const f=fixture();f.run();f.run();assert.equal(f.getAppends(),1);});
test(()=>{const f=fixture({loading:true});f.run();assert.equal(f.getMoved(),false);f.ready();assert.equal(f.getMoved(),true);});
test(()=>{const f=fixture({noCampaign:true});f.run();assert.equal(f.getMoved(),false);});
test(()=>{const f=fixture({noPanel:true});f.run();assert.equal(f.getMoved(),false);});
test(()=>{const f=fixture({badControls:true});f.run();assert.equal(f.getMoved(),false);});
console.log(passed+' DOM-contract tests passed');
