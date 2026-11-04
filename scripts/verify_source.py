"""Compare deployed Studio source to repository bytes using the public RPC."""
import base64
import hashlib
import json
import sys
import urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[1]
address=sys.argv[1]
request=urllib.request.Request('https://studio.genlayer.com/api',data=json.dumps({
    'jsonrpc':'2.0','method':'gen_getContractCode','params':[address],'id':1}).encode(),
    headers={'Content-Type':'application/json','User-Agent':'python-requests/2.32.3'})
with urllib.request.urlopen(request,timeout=30) as response: result=json.load(response)
if 'error' in result: raise SystemExit(result['error'])
deployed=base64.b64decode(result['result'],validate=True)
local=(root/'contracts/accessibility_lens.py').read_bytes()
out={'network':'studionet','chain_id':61999,'contract':address,
     'local_sha256':hashlib.sha256(local).hexdigest(),
     'deployed_sha256':hashlib.sha256(deployed).hexdigest(),'matches':local==deployed}
(root/'evidence/source-verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
if not out['matches']: raise SystemExit('Deployed source differs from repository')
