# AccessibilityLens

A standalone GenLayer Intelligent Contract for evidence-backed, build-specific digital accessibility assessments. It combines immutable test requirements, independently executed AI review, exact evidence quotations and deterministic coverage rules.

**Status:** deployed successfully on Studionet (chain 61999). 53 SDK tests, GenVM lint, semantic validation and type checking pass. Live assessment results and receipts are recorded in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md). This is an assessment of submitted test evidence, not certification of a site's complete accessibility or legal compliance.

## What it does

1. A policy owner fixes an application target, SHA-256 build identity, pages, criteria, required methods and designated auditor.
2. The auditor registers an immutable manifest of public, full-commit-pinned JSON test records, each bound by SHA-256 and exact byte length. Missing test cells are allowed but cannot pass.
3. The owner or auditor requests evaluation. GenLayer's leader retrieves and checks the evidence, then uses an LLM to assess test adequacy and documented barriers.
4. Validators independently retrieve and hash-check sources, rerun the assessment without seeing the leader answer, ground the leader's quotations and require agreement on every cell's result.
5. Deterministic code derives an outcome and appends a hash-linked receipt. Consensus rejection propagates; it cannot be caught and relabeled as success.

## Outcomes

| Outcome | Deterministic rule |
|---|---|
| CONFORMANT | Every required page/criterion/method cell has supported PASS evidence. |
| NONCONFORMANT | At least one cell has a supported FAIL. This takes priority over unknown cells. |
| PARTIAL | Some PASS cells, at least one UNKNOWN, and no supported FAIL. |
| INCONCLUSIVE | All cells UNKNOWN. |

CONFORMANT always means **conformant to the registered scope and submitted evidence**. The policy can omit requirements; the contract does not enforce a full WCAG standard or inspect a running browser. A report's FAIL or UNKNOWN can never become PASS. Semantically inadequate or contradictory records become UNKNOWN.

## Quick start

Python 3.12+; pinned GenVM SDK direct-test dependencies are downloaded/cached by the tools. Node 22+ is needed only for network scripts.

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
genvm-lint check contracts/accessibility_lens.py
genvm-lint schema contracts/accessibility_lens.py --output docs/abi.json
npm ci
```

Tests execute the actual pinned GenLayer SDK and storage with mocked web and model I/O. They explicitly invoke captured validator functions, including disagreement cases. They do not prove live multi-validator consensus or model resistance to injection.

## Public API

| Method | Caller / purpose |
|---|---|
| `register_policy(policy_json, auditor)` | Any creator; returns immutable policy ID. |
| `submit_audit(policy_id, label, evidence_json, evidence_hash)` | Designated auditor only; returns audit ID. Label cannot be reused under that policy. |
| `evaluate(audit_id)` | Owner or auditor; returns receipt hash. |
| `get_policy(policy_id)` | Read canonical policy envelope. |
| `get_audit(audit_id)` | Read immutable package and progress. |
| `get_receipt(audit_id, attempt)` | Read append-only attempt receipt. |

Only all-UNKNOWN assessments may retry, at most twice on the same immutable package. Other results close the audit immediately. Corrected evidence needs a fresh label and audit; changed criteria or build needs a fresh policy. Old assessments remain visible.

Limits: 4 requirements, 4 pages, 4 supported method types, at most 16 required cells and 16 evidence records; 6,000 bytes each and 32,000 total declared source bytes; at most two model attempts per node per evaluation. Test methods: AUTOMATED, KEYBOARD, SCREEN_READER, MANUAL.

## Evidence and verification

- [Evidence format, hashing and fixtures](docs/EVIDENCE.md)
- [Security assumptions and threat model](docs/SECURITY.md)
- [Deployment and interaction](docs/DEPLOYMENT.md)
- [Review/submission notes](docs/SUBMISSION.md)
- [Generated ABI](docs/abi.json)

Synthetic fixtures model checkout keyboard navigation, screen reader names and accessibility-tree inspection. They are text records, not independently authenticated audit findings. Images and screen-reader audio must be transcribed into scoped records; this version does not process binary screenshots or audio.

## Official references

Implementation follows the current [Equivalence Principle](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle), [storage reference](https://docs.genlayer.com/developers/intelligent-contracts/features/storage), [web access](https://docs.genlayer.com/developers/intelligent-contracts/features/web-access), and [official linter](https://github.com/genlayerlabs/genvm-linter). The runner hash in the contract is pinned for reproducibility; the linter may report a newer optional runner.

MIT license. No token, payments, escrow, admin override or external AI service is included.
