"""Build the synthetic PASS manifest at a verified 40-character repository commit."""
import hashlib, json, re, sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
commit = sys.argv[1]
if not re.fullmatch('[0-9a-f]{40}', commit): raise SystemExit('Provide a full commit SHA')
items=[]
for i in range(3):
    path=root/f'fixtures/pass_{i}.json'; raw=path.read_bytes(); d=json.loads(raw)
    items.append(dict({k:d[k] for k in ('requirement','page','method')},
        url=f'https://raw.githubusercontent.com/ANZA24k/AccessibilityLens/{commit}/fixtures/pass_{i}.json',
        sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)))
canonical=json.dumps(items,sort_keys=True,separators=(',',':'),ensure_ascii=True)
print(json.dumps({'manifest':items,'evidence_json':canonical,'evidence_hash':hashlib.sha256(canonical.encode()).hexdigest()},indent=2))
