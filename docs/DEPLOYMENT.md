# Deployment

## Live deployment

Current contract: `0xa23E85B5F3c0141748e8957Cd5FaA2A6d17FF573` on Studionet (chain ID 61999).

[Open contract in the official Studio Explorer](https://explorer-studio.genlayer.com/contracts/0xa23E85B5F3c0141748e8957Cd5FaA2A6d17FF573)

Deployment transaction: `0x9354821ec5604623863e90ad9dd5fb4bb1d45f255c0c91326b251c652a67c423`, FINALIZED with execution SUCCESS and leader-only disabled. `evidence/source-verification.json` independently compares deployed code bytes against repository source. Both SHA-256 values are `8623d7800307e8f8714b2e97747e7ebd71b1d55f87f6e6098db36df7906e2efb`.

53 SDK direct tests, GenVM AST lint, semantic validation and type checking pass. Live workflow receipts are in `evidence/live-demo.json` and individual transaction files.

The earlier `0xF1167141b130dDd16DDF3A65974343f108fE7bec` deployment is superseded. Its evidence is preserved as `live-initial.json` and `source-verification-initial.json`. That run returned INCONCLUSIVE after the top-level array response did not match the SDK JSON object interface. Version 1.1 uses an exact `{"checks": [...]}` model response envelope. New integrations should use the current address above.

Studionet is a hosted development network and may reset. This is not a production-mainnet deployment. The smoke test uses a disposable dedicated account; users should register policies with their own wallets and auditors.

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

## Live smoke test

Generate a fixture manifest from the fixture-bearing commit, set your dedicated test account and deployed address, then run:

```sh
python scripts/manifest.py 87eded275881ab691c59f4f9e5b27456c27bed83 > fixtures/manifest.json
node scripts/live_demo.mjs
python scripts/verify_source.py "$GENLAYER_CONTRACT"
```

The smoke test creates one synthetic policy and audit. It is intended for a fresh test account: repeating with the same account and contract hits the immutable policy/label guards. It verifies finalization, execution success, read-back state and receipt hashing. Account keys are excluded from committed evidence.

## Verified final assessment

The synthetic checkout assessment finalized successfully with **CONFORMANT**, three PASS cells, zero FAIL and zero UNKNOWN. All committed sources were retrieved and SHA-256/byte-verified. This outcome applies only to the synthetic registered scope; it is not an assessment of a real site or complete WCAG compliance.

| Step | Transaction | Result |
|---|---|---|
| Deploy | `0x9354821ec5604623863e90ad9dd5fb4bb1d45f255c0c91326b251c652a67c423` | FINALIZED / SUCCESS |
| register_policy | `0x98bc4ae7d4811fd3c9da766cd6f606c1293915d5f181f25af917aed17c988869` | FINALIZED / SUCCESS |
| submit_audit | `0x87a3bbb27aabf4a5c46de08ff06844648211e82e95c2ccdf0dc06e9bbdaaf423` | FINALIZED / SUCCESS |
| evaluate | `0xa68248e5d6c8519a0285a65c08c02ee1ded7230c116c0b0dbd855b967bc4b9b1` | FINALIZED / SUCCESS |

Policy ID: `6236c61c7b55754d09e06b9c15ffa5a898603ac50a92b938f3a89962e83477a8`.

Audit ID: `69c4ea127d7d6f3a8b522b137bed11e1497dd179e6942be15b31d26206bb8eef`.

Receipt hash: `fe31631fced01b62f5f368072cf4c42e7291546bbef7a78b5458dc4c0e122fcb`.

`evidence/assessment-receipt.json` is the read-back contract receipt. Its internal hash was independently recomputed; `evidence/live-demo.json` also records the read-back policy and closed audit. Transaction files retain network votes and execution outcomes.
