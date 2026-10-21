# Current Status

Date: 2026-10-21
Development branch: `improve/reliability-qc-006-20261021`

## Qualified historical baseline
Checkpoints 0.01–0.05 established the read-only scanner/catalog, duplicate grouping, local drafts, candidate workspace, bounded visual observations, preparation/editor handoff and manual marketplace preflight foundation.

The authoritative historical qualified baseline is **79/79 tests passed** on the older 0.05-era code. Older documentation that says 77/77 is superseded. This historical count MUST NOT be presented as verification of the expanded 0.06/0.07 branch.

## 0.06 Reliability & QC — implemented, qualification pending
Implemented on the development branch:
- fail-closed preview/preflight integrity;
- multidimensional candidate review foundation;
- structured route-sensitive rights review;
- source→export provenance with SHA-256 and stale-QC detection;
- exact-export human final-QC record and 100% inspection planning;
- consolidated fail-closed readiness gates;
- strict persisted-analysis validation including finite numeric/range checks;
- cross-platform traversal/drive/UNC/symlink protections;
- safer atomic external persistence;
- localhost Host/Origin/CSP and mutation-lock hardening;
- direct `submission-ready` mutation prohibited;
- legacy `submission-ready` remains readable but non-authoritative;
- preview metadata now updates independently of state transitions, preserving legacy compatibility without promotion/demotion.

## 0.07 Review Intelligence — implementation in progress
Implemented foundations:
- human fast-screen states: unreviewed / skip / hold / inspect;
- explicit human reason codes with no aggregate stock/acceptance score;
- deterministic similar/burst hints from exact hash, capture-time proximity and weak filename-sequence proximity;
- explicit human preferred-member decision for grouped candidates;
- human-specified subject region → safe actual-pixel inspection-region planning;
- structured composition/usefulness review: subject clarity, background clutter, copy space, crop flexibility, redundancy and alternate-orientation review;
- fail-closed Stage-1 → Stage-2 workflow assessment;
- deterministic external review/usefulness persistence with source-tree write refusal and atomic overwrite;
- ReviewService composing persisted review state and workflow assessment;
- validated localhost-dashboard payload adapter;
- authoritative shortlist gate: the legacy workspace `shortlist` label alone is not proof of completed 0.07 review;
- standalone 0.07 localhost review controller/page and regression tests authored.

Still to integrate:
- mount the 0.07 review page/API routes into the main candidate dashboard;
- add candidate-card navigation/status for review qualification;
- ensure UI shortlist actions use the authoritative 0.07 gate rather than implying qualification from the legacy workspace label;
- connect completed 0.07 review into consolidated readiness without weakening provenance, rights, exact-export QC or current-marketplace-requirements gates.

## Preparation / metadata hardening still required
Existing preparation already supports factual title/description/keywords, duplicate-keyword prompting, commercial/editorial route, editor handoff, safe relative export paths and Dreamstime category pairs. Remaining work includes stricter persisted-schema validation, blank/duplicate normalization policy, durable fsync on preparation writes, and clearer marketplace-neutral core vs marketplace-adapter constraints.

## Qualification truth
The expanded 0.06/0.07 test suite has **NOT** been executed in a confirmed full local run in the current environment. A previous attempt to obtain an executable checkout failed because GitHub DNS resolution was unavailable. GitHub Actions are intentionally not being consumed as a routine substitute because remote resources are scarce.

Therefore:
- do not claim a new passing-test count;
- do not merge to `main` solely from static inspection;
- when an executable checkout becomes available, run the complete suite and synthetic destructive qualification, repair in batches, then rerun.

## Product/account boundary
Original photographs remain read-only. Pixel/byte reads require the established explicit-consent pathways. No cloud CV/generative AI is required. No marketplace upload, submission, publication or deletion is authorized by this development work. The previously authorized non-original Dreamstime working-copy test remains unfinished and must not be continued without explicit action-time instruction.

## Next development order
1. Integrate the 0.07 review controller/page into the localhost candidate dashboard.
2. Reconcile shortlist UI/state with authoritative 0.07 qualification.
3. Harden preparation persistence/metadata semantics.
4. Bind 0.07 review completion into consolidated readiness.
5. Execute full local qualification when a checkout becomes available.
6. Perform a small explicitly selected real-photo end-to-end dry run after qualification.
7. Continue into 0.08 Stock Intelligence and marketplace-neutral adapters.
