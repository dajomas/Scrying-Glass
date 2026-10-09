const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(path.join(__dirname,'../static/client.js'),'utf8');
const a=source.indexOf('function connectDisplay()'),b=source.indexOf('const websocket = connectDisplay();',a);const code=source.slice(a,b);
let passed=0;
function fixture(){
    let now=0,renders=0;const timeouts=new Map(),intervals=new Map(),instances=[],label={},docListeners={},winListeners={};let id=0;
    class WS {
        constructor(){this.readyState=WS.CONNECTING;this.sent=[];this.closed=0;instances.push(this);}
        send(text){this.sent.push(JSON.parse(text));}
        close(){this.closed++;this.readyState=WS.CLOSED;}
    }
    WS.CONNECTING=0;WS.OPEN=1;WS.CLOSED=3;
    class Clock extends Date {static now(){return now;}}
    const document={hidden:false,querySelector:()=>label,addEventListener:(k,f)=>docListeners[k]=f,removeEventListener:()=>{}};
    const window={addEventListener:(k,f)=>winListeners[k]=f,removeEventListener:()=>{}};
    const sandbox={document,window,WebSocket:WS,Date:Clock,Math:{random:()=>0,min:Math.min,floor:Math.floor},JSON,console:{info:()=>{},warn:()=>{},error:()=>{},debug:()=>{}},location:{protocol:'http:',host:'testserver',assign:()=>{throw Error('unexpected navigation');}},fetch:async()=>({status:200}),render:()=>renders++,setTimeout:(fn,delay)=>{const key=++id;timeouts.set(key,{fn,delay});return key;},clearTimeout:key=>timeouts.delete(key),setInterval:fn=>{const key=++id;intervals.set(key,fn);return key;},clearInterval:key=>intervals.delete(key)};
    vm.createContext(sandbox);vm.runInContext(code,sandbox);const controller=sandbox.connectDisplay();
    return {instances,label,document,docListeners,winListeners,controller,timeouts,intervals,renderCount:()=>renders,advance:t=>now+=t,open:()=>{const s=instances.at(-1);s.readyState=WS.OPEN;s.onopen();return s;},message:obj=>instances.at(-1).onmessage({data:JSON.stringify(obj)}),retry:()=>{const [key,value]=timeouts.entries().next().value;timeouts.delete(key);value.fn();},async disconnect(){const s=instances.at(-1);s.readyState=WS.CLOSED;await s.onclose({code:1006,reason:'',wasClean:false});}};
}
async function test(fn){await fn();passed++;}
(async()=>{
    await test(async()=>{const f=fixture();f.open();f.message({type:'state',revision:1,state:{x:1}});assert.equal(f.renderCount(),1);await f.disconnect();assert.equal(f.timeouts.size,1);f.retry();f.open();f.message({type:'state',revision:1,state:{x:1}});assert.equal(f.renderCount(),1);assert.equal(f.instances.length,2);});
    await test(async()=>{const f=fixture();f.open();f.message({type:'state',revision:1,state:{x:1}});f.message({type:'state',revision:2,state:{x:2}});assert.equal(f.renderCount(),2);});
    await test(async()=>{const f=fixture();f.open();f.message({type:'state',revision:1,state:{x:1}});f.message({type:'heartbeat',revision:1});assert.equal(f.instances[0].sent.at(-1).type,'pong');});
    await test(async()=>{const f=fixture();f.open();f.advance(60000);for(const fn of f.intervals.values())fn();assert.equal(f.instances[0].closed,0);assert.equal(f.instances.length,1);});
    await test(async()=>{const f=fixture();f.open();f.message({type:'state',revision:1,state:{x:1}});f.message({type:'heartbeat',revision:2});assert.equal(f.instances[0].sent.at(-1).type,'resync');});
    await test(async()=>{const f=fixture();f.open();await f.disconnect();await f.disconnect();assert.equal(f.timeouts.size,1);});
    await test(async()=>{const f=fixture();f.open();f.document.hidden=true;f.docListeners.visibilitychange();assert.equal(f.instances[0].sent.length,0);f.document.hidden=false;f.docListeners.visibilitychange();assert.equal(f.instances[0].sent.at(-1).type,'resync');});
    await test(async()=>{const f=fixture();f.open();await f.disconnect();f.retry();assert.equal(f.instances.length,2);f.controller.close();assert.equal(f.intervals.size,0);});
    console.log(passed+' in-place reconnection tests passed');
})().catch(error=>{console.error(error);process.exit(1);});
