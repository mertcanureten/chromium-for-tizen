// Read and exercise the dedicated V8 probe via its developer inspector.
import {WebSocket} from 'ws';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {dirname} from 'node:path';
const port=process.env.TV_DEBUG_PORT;
if(!port)throw new Error('Set TV_DEBUG_PORT to the V8Probe inspector port');
const reportPath=process.argv[2];
if(!reportPath)throw new Error('Provide a report output path');
const expected=JSON.parse(await readFile(new URL('./expected.json',import.meta.url),'utf8'));
const pages=await(await fetch(`http://127.0.0.1:${port}/json`,{signal:AbortSignal.timeout(8000)})).json();
if(pages.length!==1)throw new Error('Expected exactly one dedicated probe inspector target');
const ws=new WebSocket(pages[0].webSocketDebuggerUrl);
await new Promise((resolve,reject)=>{ws.once('open',resolve);ws.once('error',reject);});
let id=0;const pending=new Map();
ws.on('message',raw=>{const msg=JSON.parse(raw);const p=pending.get(msg.id);if(p){pending.delete(msg.id);clearTimeout(p.timer);msg.error?p.reject(new Error(JSON.stringify(msg.error))):p.resolve(msg.result);}});
ws.on('error',error=>{for(const p of pending.values()){clearTimeout(p.timer);p.reject(error);}pending.clear();});
async function evaluate(expression){const n=++id;const result=await new Promise((resolve,reject)=>{const timer=setTimeout(()=>{pending.delete(n);reject(new Error('TV inspector timed out'));},10000);pending.set(n,{resolve,reject,timer});ws.send(JSON.stringify({id:n,method:'Runtime.evaluate',params:{expression,returnByValue:true}}));});if(result.wasThrown||result.exceptionDetails)throw new Error(JSON.stringify(result));return result.result.value;}
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
let lastState;
async function waitForMessage(start){const deadline=Date.now()+120000;while(Date.now()<deadline){const state=await evaluate('({title:document.title,log:window.v8ProbeLog,result:window.v8ProbeResult,status:document.getElementById("status").textContent,elapsed:Date.now()-window.v8ProbeStarted,userAgent:navigator.userAgent})');lastState=state;if(!Array.isArray(state.log))throw new Error('This is not the dedicated V8 probe');if(state.result?.error)throw new Error(JSON.stringify(state));const message=state.log.slice(start).find(x=>/^(RESULT: |ERROR: )/.test(x));if(message)return {message,state};await sleep(1000);}throw new Error('Native V8 did not return within 120 seconds');}
const report={capturedAt:new Date().toISOString(),tests:[],passed:false};
try{
 const initial=await waitForMessage(0);report.initial=initial.state;
 const actual=JSON.parse(initial.message.replace(/^RESULT: /,''));
 const compare=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
 const mismatches=Object.keys(expected).filter(key=>!compare(actual[key],expected[key]));
 report.tests.push({name:'modern-language-baseline',passed:!mismatches.length,mismatches,actual});
 if(mismatches.length)throw new Error('Baseline mismatch: '+mismatches.join(', '));
 const cases=[
  {name:'runtime-exception',source:'throw new Error("probe-controlled-error")',prefix:'ERROR: Error: probe-controlled-error'},
  {name:'syntax-exception',source:'const = ;',prefix:'ERROR: SyntaxError:'},
  {name:'recovery-math-memory',source:'globalThis.probeMarker=42;JSON.stringify({recovery:6*7,math:Math.abs(Math.sin(Math.PI/6)-0.5)<1e-12&&Math.abs(Math.log(Math.E)-1)<1e-12&&Math.abs(Math.exp(1)-Math.E)<1e-12&&Object.is(Math.round(-0.1),-0),memory:Array.from({length:10000},(_,i)=>({i:i})).reduce((s,x)=>s+x.i,0),map:new Map([["a",42]]).get("a"),set:new Set([1,1,2]).size})',value:{recovery:42,math:true,memory:49995000,map:42,set:2}},
  {name:'fresh-isolate',source:'JSON.stringify({value:6*7,clean:typeof globalThis.probeMarker})',value:{value:42,clean:'undefined'}}
 ];
 for(const c of cases){const count=await evaluate('window.v8ProbeLog.length');const started=Date.now();await evaluate('window.runV8Probe('+JSON.stringify(c.source)+');true');const result=await waitForMessage(count);const passed=c.prefix?result.message.startsWith(c.prefix):result.message.startsWith('RESULT: ')&&compare(JSON.parse(result.message.slice(8)),c.value);report.tests.push({name:c.name,passed,roundTripMs:Date.now()-started,message:result.message});if(!passed)throw new Error('Test failed: '+c.name);}
 report.passed=true;
}catch(error){report.error=String(error);report.lastState=lastState;process.exitCode=1;}
finally{ws.close();await mkdir(dirname(reportPath),{recursive:true});await writeFile(reportPath,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));}
