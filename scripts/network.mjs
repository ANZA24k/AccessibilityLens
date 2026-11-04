import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createClient, createAccount } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';
import { TransactionStatus } from 'genlayer-js/types';
const mode = process.argv[2];
const account = process.env.GENLAYER_PRIVATE_KEY ? createAccount(process.env.GENLAYER_PRIVATE_KEY) : undefined;
const client = createClient({ chain: studionet, ...(account ? {account} : {}) });
const address = process.env.GENLAYER_CONTRACT;
const safe = (k,v) => /private.?key|secret|authorization|api.?key/i.test(k) ? '[REDACTED]' : typeof v==='bigint' ? v.toString() : v;
await mkdir('evidence', { recursive: true });
if (mode === 'read') {
  if (!address) throw Error('Set GENLAYER_CONTRACT');
  console.log(await client.readContract({ address, functionName: process.argv[3], args: JSON.parse(process.argv[4] || '[]') }));
} else {
  if (!account) throw Error('Set GENLAYER_PRIVATE_KEY to a dedicated Studio test account');
  let hash;
  if (mode === 'deploy') hash = await client.deployContract({ code: await readFile('contracts/accessibility_lens.py'), args: [], leaderOnly: false });
  else if (mode === 'write' && address) hash = await client.writeContract({ address, functionName: process.argv[3], args: JSON.parse(process.argv[4] || '[]'), value: 0n, leaderOnly: false });
  else throw Error('Usage: network.mjs deploy | read METHOD JSON_ARGS | write METHOD JSON_ARGS');
  console.log('Transaction:',hash);
  const receipt = await client.waitForTransactionReceipt({ hash, status: TransactionStatus.FINALIZED, interval:5000, retries:120 });
  await writeFile(`evidence/${hash}.json`, JSON.stringify(receipt,safe,2)+'\n');
  const execution = receipt.txExecutionResultName || receipt.consensus_data?.leader_receipt?.[0]?.execution_result;
  if (execution !== 'SUCCESS') throw Error('Finalized transaction did not execute successfully; inspect saved receipt');
  console.log('Finalized SUCCESS; receipt saved. Contract:', receipt.data?.contract_address || receipt.to_address || '(inspect receipt)');
}
