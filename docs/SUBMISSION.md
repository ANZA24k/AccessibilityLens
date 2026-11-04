# Reviewer notes

Category: standalone Intelligent Contract. This repository has no frontend and does not claim to be a full product.

AccessibilityLens assesses build-pinned accessibility test evidence against immutable, scoped criteria. It requires independent GenLayer validator retrieval and AI assessment, exact evidence quotations, deterministic mandatory coverage rules, authorized submissions and append-only hash-linked receipts. Outcomes are CONFORMANT, PARTIAL, NONCONFORMANT and INCONCLUSIVE. It does not certify complete accessibility or legal compliance.

Review source in `contracts/accessibility_lens.py`, schemas and bounds in `docs/EVIDENCE.md`, threat model in `docs/SECURITY.md`, and reproducible commands/live status in `docs/DEPLOYMENT.md`.

Offline evidence: 53 SDK direct tests covering all outcomes, source integrity, authorization, immutable labels, bounded retries, malformed AI responses, missing test coverage and explicit validator disagreement. Web and model responses are mocked. Injection fixtures test contract handling of scripted conservative responses, not real model attack resistance. GenVM AST lint, semantic validation and generated ABI are included under `evidence/` and `docs/`.

Only provide an Explorer contract URL as submission evidence once it points to an actual successful deployment. Receipt hashes alone are not deployment evidence. See the live status file before making network claims.
