# Reviewer notes

Category: standalone Intelligent Contract. This repository has no frontend and does not claim to be a full product.

AccessibilityLens assesses build-pinned accessibility test evidence against immutable, scoped criteria. It requires independent GenLayer validator retrieval and AI assessment, exact evidence quotations, deterministic mandatory coverage rules, authorized submissions and append-only hash-linked receipts. Outcomes are CONFORMANT, PARTIAL, NONCONFORMANT and INCONCLUSIVE. It does not certify complete accessibility or legal compliance.

Review source in `contracts/accessibility_lens.py`, schemas and bounds in `docs/EVIDENCE.md`, threat model in `docs/SECURITY.md`, and reproducible commands/live status in `docs/DEPLOYMENT.md`.

Offline evidence: 53 SDK direct tests covering all outcomes, source integrity, authorization, immutable labels, bounded retries, malformed AI responses, missing test coverage and explicit validator disagreement. Web and model responses are mocked. Injection fixtures test contract handling of scripted conservative responses, not real model attack resistance. GenVM AST lint, semantic validation and generated ABI are included under `evidence/` and `docs/`.

Only provide an Explorer contract URL as submission evidence once it points to an actual successful deployment. Receipt hashes alone are not deployment evidence. See the live status file before making network claims.

## Verified deployment evidence

Current contract: https://explorer-studio.genlayer.com/contracts/0xa23E85B5F3c0141748e8957Cd5FaA2A6d17FF573

Four final-version transactions (deployment, policy registration, evidence submission and evaluation) finalized with execution SUCCESS and leader-only disabled. The synthetic checkout assessment returned CONFORMANT with three supported PASS results. Deployed source bytes match repository SHA-256. See `deployments/studionet.json`, `evidence/live-demo.json`, `evidence/source-verification.json` and the individual transaction receipts.

Suggested title: AccessibilityLens — GenLayer accessibility evidence assessment

Suggested description:

AccessibilityLens is a standalone GenLayer Intelligent Contract for build-specific accessibility evidence assessment. Immutable criteria define required page and test-method coverage. Commit-pinned JSON reports are verified by SHA-256 and exact byte length. GenLayer validators independently retrieve sources, assess test adequacy and require agreement on requirement-level results with grounded quotations. Deterministic rules produce CONFORMANT, PARTIAL, NONCONFORMANT or INCONCLUSIVE, with authorized submissions, bounded retries and append-only hash-linked receipts. Includes 53 passing SDK direct tests and passing GenVM lint, semantic validation and type checking. Deployed on Studionet; the synthetic checkout flow finalized successfully with CONFORMANT (3/3 PASS). Scope is limited to submitted evidence, not complete WCAG or legal certification.
