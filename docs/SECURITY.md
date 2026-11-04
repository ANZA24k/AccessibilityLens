# Security model

## Trust boundaries

The application owner defines the scope and selects the auditor. Only that auditor submits evidence; owner and auditor can evaluate. Public viewers may read all stored data. There are no payments, token balances, privileged result overrides, policy edits or upgrade methods.

A policy or auditor can lie or select weak criteria. Hashes prove committed bytes, not truthful observation, auditor independence or legal compliance. The contract performs semantic review of documented tests, not actual browser testing, a site crawl or comprehensive WCAG certification.

## Consensus

All web and LLM work occurs under `gl.vm.run_nondet_unsafe`. Validators independently fetch the same pinned sources and independently assess without the proposed result in their prompt. They validate the leader's quotation grounding against their own verified documents and require exact cell-level state agreement. Different but valid quotations may be accepted. Decision counts and overall status are derived deterministically. A structurally valid JSON response is not sufficient for validator acceptance.

Two model attempts are permitted per node/evaluation. Invalid or unavailable model responses produce all UNKNOWN. Such an outcome closes only after the second audit attempt. Consensus exceptions propagate, so failed consensus cannot create an application receipt. Runtime out-of-gas/termination may revert instead of producing UNKNOWN. Retries use identical immutable evidence; revised evidence requires a new audit label. No challenge mechanism can overwrite a historical receipt; protocol appeals follow GenLayer's network rules.

## Defenses

- Fixed public HTTPS host, full Git commit, strict path syntax, exact byte and SHA-256 checks.
- Maximum 16 source records, 6,000 bytes per record, 32,000 declared total; 16 required cells and bounded prompts/retries.
- Exact record scope and application build matching, strict schemas, duplicate/extra field rejection and exact quotes.
- Failure/unknown reports never upgraded to PASS; missing coverage prevents CONFORMANT.
- All criteria, observations and procedures treated as untrusted data in prompts; no evidence-provided tools, code, links or instructions executed.
- Authorized writes and immutable per-policy labels; contract-address domain separation and append-only hash-linked receipts.

The remote fetch size bound is enforced after transport download. GenVM controls transport response buffering and redirect behavior. The contract accepts only status 200 and exact committed bytes; transport-level limits are not claimed. Broad exception handling is confined to evidence/model availability; the consensus operation itself is not caught.

## Remaining risks

AI providers can share biases or accept a deceptive report. Exact quotation grounding does not prove the quote entails the criterion. Validators can disagree and prevent completion. Sources can become unavailable; an unchanged URL can fail even though its commit exists. Synthetic fixtures and direct tests mock external I/O and do not establish model quality, live network finality or full multi-validator security. Build hashes are assertions about artifacts; this contract cannot prove the live website serves those artifacts. Text evidence does not authenticate screenshots, screen-reader audio, test tooling or human actions.

For a suspected vulnerability, avoid posting private user records or secrets. Use GitHub private vulnerability reporting if enabled, otherwise provide only a non-sensitive reproduction in a repository issue. No formal external security audit has been performed.
