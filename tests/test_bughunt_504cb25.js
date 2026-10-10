/* Render-failure recovery checks for the production connectDisplay function.
 * Uses deterministic WebSocket/timer/render fixtures, not a browser or server.
 */
'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const source=fs.readFileSync(path.join(__dirname,'..','static','client.js'),'utf8');
const start=source.indexOf('function connectDisplay()'),end=source.indexOf('const websocket = connectDisplay();',start);
const code=source.slice(start,end);
function fixture() {
 const sockets=[],timers=new Map(),intervals=new Map(),label={},listeners={};let id=0,fail=false,view=null;
 const renders=[];
 class WS {
  constructor(){this.readyState=WS.CONNECTING;this.sent=[];sockets.push(this);}
  send(text){this.sent.push(JSON.parse(text));}
  close(){this.readyState=WS.CLOSED;}
 }
 WS.CONNECTING=0;WS.OPEN=1;WS.CLOSED=3;
 const context={WebSocket:WS,JSON,Date,Math,document:{hidden:false,querySelector:()=>label,
  addEventListener:(name,fn)=>listeners[name]=fn,removeEventListener:()=>{}},
  window:{addEventListener:()=>{},removeEventListener:()=>{}},
  location:{protocol:'https:',host:'table.example',assign:()=>{}},fetch:async()=>({status:200}),
  console:{warn:()=>{},error:()=>{},info:()=>{},debug:()=>{}},
  render:state=>{renders.push(state);view='partial';if(fail)throw Error('Injected render failure');view=state.x;},
  setTimeout:(fn,delay)=>{const n=++id;timers.set(n,{fn,delay});return n;},clearTimeout:n=>timers.delete(n),
  setInterval:fn=>{const n=++id;intervals.set(n,fn);return n;},clearInterval:n=>intervals.delete(n)};
 vm.createContext(context);vm.runInContext(code,context);const controller=context.connectDisplay();
 const h={sockets,timers,label,renders,controller,setFail:value=>{fail=value;},view:()=>view,
  open:()=>{const ws=sockets.at(-1);ws.readyState=WS.OPEN;ws.onopen();return ws;},
  message:message=>sockets.at(-1).onmessage({data:JSON.stringify(message)}),
  resyncCount:()=>sockets.flatMap(ws=>ws.sent).filter(m=>m.type==='resync').length,
  async reconnect(){const old=sockets.at(-1);old.readyState=WS.CLOSED;await old.onclose({code:1006,reason:'',wasClean:false});
    const [n,timer]=timers.entries().next().value;timers.delete(n);timer.fn();h.open();}};
 h.open();return h;
}
const state=(revision,x)=>({type:'state',revision,state:{x}});
const cases=[
 ['failed resync can be retried on next heartbeat',async()=>{
  const h=fixture();h.message(state(1,'A'));h.controller.resync();h.setFail(true);h.message(state(2,'B'));
  h.message({type:'heartbeat',revision:2});assert.equal(h.resyncCount(),2);
 }],
 ['manual resync can retry after render failure',async()=>{
  const h=fixture();h.message(state(1,'A'));h.controller.resync();h.setFail(true);h.message(state(2,'B'));
  h.controller.resync();assert.equal(h.resyncCount(),2);
 }],
 ['old valid snapshot is rerendered after partial failure',async()=>{
  const h=fixture();h.message(state(1,'A'));h.setFail(true);h.message(state(2,'B'));assert.equal(h.view(),'partial');
  h.setFail(false);h.message(state(3,'A'));assert.equal(h.renders.length,3);assert.equal(h.view(),'A');
 }],
 ['reconnect also repairs old snapshot after partial failure',async()=>{
  const h=fixture();h.message(state(1,'A'));h.setFail(true);h.message(state(2,'B'));await h.reconnect();
  h.setFail(false);h.message(state(3,'A'));assert.equal(h.view(),'A');assert.equal(h.renders.length,3);
 }],
 ['error status does not falsely promise a retained screen',async()=>{
  const h=fixture();h.setFail(true);h.message(state(1,'A'));assert.doesNotMatch(h.label.textContent,/retained last screen/);
 }],
 ['healthy unchanged snapshots still skip duplicate rendering',async()=>{
  const h=fixture();h.message(state(1,'A'));h.message(state(2,'A'));assert.equal(h.renders.length,1);
 }],
 ['failed state is not acknowledged',async()=>{
  const h=fixture();h.message(state(1,'A'));h.setFail(true);h.message(state(2,'B'));
  const acks=h.sockets[0].sent.filter(m=>m.type==='ack');assert.equal(acks.length,1);assert.equal(acks[0].revision,1);
 }],
 ['pending resync requests remain deduplicated',async()=>{
  const h=fixture();h.controller.resync();h.controller.resync();assert.equal(h.resyncCount(),1);
 }],
 ['successful repair is acknowledged at its revision',async()=>{
  const h=fixture();h.message(state(1,'A'));h.setFail(true);h.message(state(2,'B'));h.setFail(false);h.message(state(3,'C'));
  assert.equal(h.view(),'C');assert.equal(h.sockets[0].sent.at(-1).type,'ack');assert.equal(h.sockets[0].sent.at(-1).revision,3);
 }],
 ['healthy reconnect still preserves unchanged stage',async()=>{
  const h=fixture();h.message(state(1,'A'));await h.reconnect();h.message(state(1,'A'));assert.equal(h.renders.length,1);
 }]
];
(async()=>{let failures=0;for(const [name,test]of cases){try{await test();console.log('PASS '+name);}catch(error){failures++;console.error('FAIL '+name+'\n'+error.stack);}}
 console.log(`${cases.length} tests; ${cases.length-failures} passed; ${failures} failed`);process.exitCode=failures?1:0;})();
