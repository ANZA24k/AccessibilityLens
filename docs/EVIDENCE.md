# Evidence format and commitments

Every policy fixes `target` and `version` (64 lowercase hex SHA-256 of application build bytes), `pages`, and requirements with IDs, natural-language criteria and required test methods. A policy does not automatically include all WCAG requirements. Register a complete, reviewed scope if that is your goal.

A required cell is the Cartesian product of each requirement's methods and every page. At most 16 cells may be registered. No `NOT_APPLICABLE` or discretionary waiver exists.

The auditor supplies `evidence_json`, a JSON array of descriptors:

```json
{"requirement":"focus","page":"/checkout","method":"KEYBOARD","url":"https://raw.githubusercontent.com/OWNER/REPO/FULL_40_HEX_COMMIT/fixtures/record.json","sha256":"64_lowercase_hex","bytes":500}
```

The URL above illustrates the format, not a real valid descriptor. Use `python scripts/manifest.py FULL_COMMIT` to generate real fixture descriptors and the manifest hash. Exact source bytes include whitespace and final newlines; never hash parsed/reformatted JSON as a substitute.

Each retrieved JSON record must have exactly these keys:

```json
{
  "target":"demo-checkout",
  "version":"64_lowercase_hex_build_sha256",
  "requirement":"focus",
  "page":"/checkout",
  "method":"KEYBOARD",
  "environment":"Browser, OS, assistive technology and version",
  "procedure":"Specific steps actually performed on this build and page",
  "observed":"Specific observed behavior or barrier, not an unsupported compliance claim",
  "reported":"PASS"
}
```

`reported` is PASS, FAIL or UNKNOWN. The model checks whether the procedure is appropriate for the criterion and method and whether observations support the report. A supported PASS/FAIL needs exact substrings from both procedure and observed fields. A model cannot promote a reported failure or uncertainty to PASS. UNKNOWN has no quotations. No source, malformed source, hash mismatch, unrelated target/build/cell and retrieval failure all contribute UNKNOWN rather than successful coverage.

The contract does not fetch arbitrary URLs or follow links embedded in records. Only HTTPS raw.githubusercontent.com URLs with full 40-character lowercase Git commits and restricted `.json` paths are accepted. Response status must be 200. The SDK HTTP stack may follow redirects internally; the contract has no redirect-control API. Exact byte/hash verification remains mandatory even after any transport redirect. Response sizes are checked after download; transport buffering/timeouts are controlled by GenVM, not the contract. Sources must therefore remain small and public.

## Canonical hashing

Manifest and receipt JSON uses Python `json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)`, UTF-8 encoded, then SHA-256. Arrays preserve order. Raw source files are hashed directly as bytes. Duplicate JSON keys and non-finite numeric constants are rejected. Policy and audit IDs also commit the contract address, creator/auditor identity and immutable content. Chain finality is supplied by GenLayer, not by the receipt hash alone.

A receipt envelope contains `hash` and `body`. The body binds contract, version, policy ID, audit ID, manifest hash, attempt, previous hash, assessment and deterministic decision. Run `python scripts/verify_receipt.py RECEIPT.json` to verify its internal hash, then independently read the same receipt and audit head from the deployed contract. Save successful finalized transaction receipts separately. A correctly hashed file alone does not prove chain inclusion or validator agreement.

## Fixtures

`policy.json` and `pass_0.json`–`pass_2.json` describe synthetic checkout tests. `fail.json` demonstrates a keyboard trap. `injection.json` and `contradiction.json` exercise conservative semantic UNKNOWN responses in mocked tests. These are educational fixtures, not a real application's audit or proof that a live model rejects all malicious instructions.

Immutable evidence does not prove observations are truthful. Review auditor identity, scope quality and evidence provenance separately. Public audit data must not contain credentials, personal data or private screen captures.
