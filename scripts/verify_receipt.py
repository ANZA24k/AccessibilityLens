"""Verify a downloaded contract receipt envelope (not a chain finality proof)."""
import hashlib,json,sys
r=json.load(open(sys.argv[1])); b=json.dumps(r['body'],sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
assert hashlib.sha256(b).hexdigest()==r['hash'], 'Receipt hash mismatch'
print(r['hash'],r['body']['decision']['outcome'])
