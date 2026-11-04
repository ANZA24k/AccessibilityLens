# Deployment

Offline validation is complete. Live network status is recorded below when available; no address or transaction is fabricated.

## Reproduce

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
genvm-lint check contracts/accessibility_lens.py
genvm-lint schema contracts/accessibility_lens.py --output docs/abi.json
npm ci
# Set a dedicated Studio test account in your shell; never put keys in the repository.
export GENLAYER_PRIVATE_KEY=YOUR_DEDICATED_TEST_ACCOUNT_KEY
npm run deploy
```

`scripts/network.mjs` selects official SDK `studionet` (chain ID 61999), disables leader-only mode and waits for FINALIZED. It saves receipts and requires execution SUCCESS. Studio uses test accounts; do not reuse an account holding real assets. Network signing secrets are never printed or included in receipts.

After successful deployment set `GENLAYER_CONTRACT` to the exact deployed address. Use the methods and JSON argument arrays described in README. `register_policy` requires the canonical policy JSON string and designated auditor address. `submit_audit` requires policy ID, unique label, evidence JSON string and canonical manifest SHA-256. `evaluate` requires audit ID.

```sh
npm run read -- get_policy '["POLICY_ID"]'
npm run write -- evaluate '["AUDIT_ID"]'
npm run read -- get_receipt '["AUDIT_ID",1]'
```

Use `python scripts/manifest.py FULL_COMMIT` to pin the synthetic PASS fixture sources. Inspect every finalized transaction's execution result and read back policy, audit and receipt state. A deployment success alone does not demonstrate an AI assessment. Direct SDK tests mock web/model I/O and manually run validator callbacks; they do not simulate full network finality, fees, validator rotation or appeals.
