// Synthetic smoke test; use only a dedicated Studio test account.
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {createClient,createAccount} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';
import {TransactionStatus} from 'genlayer-js/types';
import {getAddress} from 'viem';
const address=getAddress(process.env.GENLAYER_CONTRACT);
if (!process.env.GENLAYER_PRIVATE_KEY) throw Error('Set dedicated test private key');
const account=createAccount(process.env.GENLAYER_PRIVATE_KEY);
const client=createClient({chain:studionet,account});
function canonical(x) {if(Array.isArray(x))return '['+x.map(canonical).join(',')+']';if(x&&typeof x==='object')return '{'+Object.keys(x).sort().map(k=>JSON.stringify(k)+':'+canonical(x[k])).join(',')+'}';return JSON.stringify(x);}
function digest(x){return createHash('sha256').update(canonical(x)).digest('hex');}
const safe=(k,v)=>/private.?key|secret|authorization|api.?key/i.test(k)?'[REDACTED]':typeof v==='bigint'?v.toString():v;
const state={network:'studionet',chain_id:61999,contract:address,leader_only:false,transactions:[]};
async function checkpoint(){await writeFile('evidence/live-demo.json',JSON.stringify(state,safe,2)+'\n');}
async function write(name,args){
 const hash=await client.writeContract({address,functionName:name,args,value:0n,leaderOnly:false});
 state.transactions.push({method:name,hash});await checkpoint();console.log(name,hash);
 const r=await client.waitForTransactionReceipt({hash,status:TransactionStatus.FINALIZED,interval:5000,retries:120});
 await writeFile(`evidence/${hash}.json`,JSON.stringify(r,safe,2)+'\n');
 const execution=r.txExecutionResultName||r.consensus_data?.leader_receipt?.[0]?.execution_result;
 state.transactions.at(-1).status=r.status_name||r.status;
 state.transactions.at(-1).execution=execution;await checkpoint();
 if(execution!=='SUCCESS')throw Error(name+' execution '+execution);
 console.log(name,'FINALIZED SUCCESS');return r;
}
const p=JSON.parse(await readFile('fixtures/policy.json','utf8'));
const mf=JSON.parse(await readFile('fixtures/manifest.json','utf8'));
state.policy_id=digest({domain:'AccessibilityLens/1.1',contract:address,owner:getAddress(account.address),auditor:getAddress(account.address),policy:p});
await checkpoint();
await write('register_policy',[canonical(p),getAddress(account.address)]);
state.policy=JSON.parse(await client.readContract({address,functionName:'get_policy',args:[state.policy_id]}));await checkpoint();
const label='synthetic-checkout-v1';
state.audit_id=digest({domain:'AccessibilityLens/1.1',contract:address,policy_id:state.policy_id,label,evidence:mf.manifest,evidence_hash:mf.evidence_hash});
await write('submit_audit',[state.policy_id,label,mf.evidence_json,mf.evidence_hash]);
state.audit=JSON.parse(await client.readContract({address,functionName:'get_audit',args:[state.audit_id]}));await checkpoint();
await write('evaluate',[state.audit_id]);
state.receipt=JSON.parse(await client.readContract({address,functionName:'get_receipt',args:[state.audit_id,1]}));
if(digest(state.receipt.body)!==state.receipt.hash)throw Error('Receipt hash mismatch');
state.audit=JSON.parse(await client.readContract({address,functionName:'get_audit',args:[state.audit_id]}));
await checkpoint();console.log('Outcome:',state.receipt.body.decision.outcome);
