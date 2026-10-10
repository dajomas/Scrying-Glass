/* Deterministic async-interleaving regressions for static/users.js.
 * Executes the complete production script in Node vm with DOM/fetch fixtures.
 * No real browser or HTTP server is exercised.
 */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '..', 'static', 'users.js'), 'utf8');
const tick = () => new Promise(resolve => setImmediate(resolve));
const users = [{id:1,username:'owner',role:'superadmin'}, {id:2,username:'alice',role:'client'}, {id:3,username:'bob',role:'admin'}];
async function harness() {
  class Element {
    constructor() { this.children=[]; this.value=''; this.required=false; this.textContent=''; }
    append(...items) { this.children.push(...items); }
    replaceChildren(...items) { this.children=[...items]; }
    focus() {}
  }
  const elements = Object.fromEntries(['userMessage','userForm','password','formTitle','userRows','username','role','cancelEdit'].map(id=>[id,new Element()]));
  elements.userForm.reset = () => { elements.username.value=''; elements.role.value='client'; elements.password.value=''; };
  const h = {elements,requests:[],redirects:[],gate:false,release:null,failWrite:false};
  const response = (data,status=200) => ({status,ok:status>=200&&status<300,json:async()=>data});
  const fetch = async (url,options) => {
    const method=options.method;
    h.requests.push({url,method,body:options.body?JSON.parse(options.body):undefined});
    if(url==='/api/me')return response({username:'owner',role:'superadmin'});
    if(url==='/api/users'&&method==='GET') {
      if(h.gate) {h.gate=false;await new Promise(resolve=>{h.release=resolve;});}
      return response(users);
    }
    if(h.failWrite)return response({detail:'Write rejected'},409);
    return response({id:Number(url.split('/').at(-1))||4});
  };
  const context=vm.createContext({document:{getElementById:id=>elements[id],createElement:()=>new Element()},
    fetch,location:{assign:url=>h.redirects.push(url)},confirm:()=>true});
  vm.runInContext(source,context,{filename:'static/users.js'});
  await tick();
  h.edit = id => {const row=elements.userRows.children.find(row=>row.children[0].textContent===users.find(u=>u.id===id).username);row.children[2].children[0].onclick();};
  h.cancel = () => elements.cancelEdit.onclick();
  h.submit = () => elements.userForm.onsubmit({preventDefault(){}});
  h.write = () => h.requests.find(request=>request.method==='PATCH'||request.method==='POST');
  return h;
}
async function pausedEdit(id=2) {
  const h=await harness();h.edit(id);h.elements.username.value='submitted';h.gate=true;
  h.pending=h.submit();assert.equal(typeof h.release,'function');return h;
}
const cases = [
  ['switching account cannot change PATCH target', async()=>{
    const h=await pausedEdit();h.edit(3);h.release();await h.pending;
    assert.equal(h.write().url,'/api/users/2');assert.equal(h.write().body.username,'submitted');
  }],
  ['cancel cannot turn PATCH into POST', async()=>{
    const h=await pausedEdit();h.cancel();h.release();await h.pending;
    assert.equal(h.write().method,'PATCH');assert.equal(h.write().url,'/api/users/2');
  }],
  ['switching to self cannot redirect a non-self save', async()=>{
    const h=await pausedEdit();h.edit(1);h.release();await h.pending;
    assert.equal(h.write().url,'/api/users/2');assert.deepEqual(h.redirects,[]);
  }],
  ['switching away from self still redirects after self save', async()=>{
    const h=await pausedEdit(1);h.edit(2);h.release();await h.pending;
    assert.equal(h.write().url,'/api/users/1');assert.deepEqual(h.redirects,['/login']);
  }],
  ['newly selected edit form is preserved', async()=>{
    const h=await pausedEdit();h.edit(3);h.elements.username.value='unsaved bob';h.release();await h.pending;
    assert.equal(h.elements.username.value,'unsaved bob');assert.equal(h.elements.formTitle.textContent,'Edit bob');
  }],
  ['new typing for same account is preserved', async()=>{
    const h=await pausedEdit();h.elements.username.value='next unsaved name';h.release();await h.pending;
    assert.equal(h.elements.username.value,'next unsaved name');assert.equal(h.write().body.username,'submitted');
  }],
  ['new password typing is preserved', async()=>{
    const h=await pausedEdit();h.elements.password.value='new unsaved password';h.release();await h.pending;
    assert.equal(h.elements.password.value,'new unsaved password');assert.equal(h.write().body.password,undefined);
  }],
  ['new role selection is preserved', async()=>{
    const h=await pausedEdit();h.elements.role.value='admin';h.release();await h.pending;
    assert.equal(h.elements.role.value,'admin');assert.equal(h.write().body.role,'client');
  }],
  ['unchanged successful edit resets form', async()=>{
    const h=await pausedEdit();h.release();await h.pending;
    assert.equal(h.write().url,'/api/users/2');assert.equal(h.elements.formTitle.textContent,'Create user');
    assert.equal(h.elements.username.value,'');assert.equal(h.elements.password.required,true);
  }],
  ['normal create remains POST with password', async()=>{
    const h=await harness();h.elements.username.value='new';h.elements.role.value='client';h.elements.password.value='password1';await h.submit();
    assert.equal(h.write().url,'/api/users');assert.equal(h.write().method,'POST');assert.equal(h.write().body.password,'password1');
  }],
  ['blank edit password stays omitted', async()=>{
    const h=await harness();h.edit(2);await h.submit();assert.equal(h.write().body.password,undefined);
  }],
  ['failed write preserves editing form', async()=>{
    const h=await harness();h.edit(2);h.elements.username.value='unsaved';h.failWrite=true;await h.submit();
    assert.equal(h.elements.username.value,'unsaved');assert.equal(h.elements.userMessage.textContent,'Write rejected');
  }]
];
(async()=>{
  let failed=0;
  for(const [name,test] of cases) {
    try {await test();console.log('PASS '+name);}
    catch(error) {failed++;console.error('FAIL '+name+'\n'+error.stack);}
  }
  console.log(`${cases.length} tests; ${cases.length-failed} passed; ${failed} failed`);
  process.exitCode=failed?1:0;
})();
