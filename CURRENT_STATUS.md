# Current Status

Date: 2026-10-21
Development branch: `improve/reliability-qc-006-20261021`

## Qualified historical baseline
Checkpoints 0.01–0.05 established the read-only scanner/catalog, duplicate grouping, local drafts, candidate workspace, bounded visual observations, preparation/editor handoff and manual marketplace preflight foundation.

The authoritative historical qualified baseline is **79/79 tests passed** on the older 0.05-era code. Older documentation that says 77/77 is superseded. This historical count MUST NOT be presented as verification of the expanded 0.06/0.07/0.08 branch.

## 0.06 Reliability & QC — implemented, qualification pending
Implemented on the development branch:
- fail-closed preview/preflight integrity;
- multidimensional candidate review foundation;
- structured route-sensitive rights review, with positional compatibility preserved for older callers;
- source→export provenance with SHA-256 and stale-QC detection;
- direct high-level provenance-bound readiness that re-fingerprints selected source/export files with explicit consent instead of trusting a naked Boolean;
- exact-export human final-QC record and 100% inspection planning;
- consolidated fail-closed readiness gates;
- strict persisted-analysis validation including finite numeric/range checks;
- cross-platform traversal/drive/UNC/symlink protections;
- safer atomic external persistence;
- localhost Host/Origin/CSP and mutation-lock hardening;
- direct `submission-ready` mutation prohibited;
- legacy `submission-ready` remains readable but non-authoritative;
- preview metadata updates independently of state transitions, preserving legacy compatibility without promotion/demotion.

## 0.07 Review Intelligence — substantially implemented, qualification pending
Implemented:
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
- standalone 0.07 review controller/page;
- localhost-only 0.07 HTTP server and runnable checkout launcher;
- review server security tests covering localhost restriction, non-serving of originals, traversal rejection and bounded JSON requests;
- consolidated submission readiness requires literal `review_intelligence_complete=True`; old 0.06 callers fail closed instead of bypassing 0.07 review.

Remaining UI consolidation:
- link/mount the 0.07 review surface directly from the main candidate dashboard;
- display authoritative review/shortlist status on candidate cards;
- prevent the legacy workspace `shortlist` label from visually implying completed 0.07 qualification.

## Preparation / metadata hardening
Preparation now has strict supported-schema parsing, typed keyword/category/category-pair validation, safe cross-platform relative paths, external-only persistence, fsync-backed creation/atomic overwrite, duplicate-keyword prompts and blank keyword/category prompts. Dreamstime category pairs remain a marketplace-specific preparation detail and should migrate behind the future adapter boundary rather than spread into the neutral core.

## 0.08 Stock Intelligence / marketplace engine — foundation started, qualification pending
Implemented initial marketplace-neutral components:
- `marketplace_rules.py`: requirement-profile provenance with marketplace name, authoritative HTTPS source, human verification date and explicit review horizon;
- stale, missing, future-dated or malformed requirement profiles fail closed rather than silently becoming current marketplace truth;
- no Dreamstime/Adobe/Shutterstock/Getty/Alamy requirements are invented or embedded by this framework;
- `portfolio_intelligence.py`: explainable human-data observations for subject clusters, route/copy-space incompleteness and orientation concentration;
- portfolio intelligence deliberately produces observations, not sales predictions, acceptance probabilities or hidden suitability scores;
- tests authored for current/stale rule profiles and explainable portfolio observations.

## Qualification truth
The expanded 0.06/0.07/0.08 test suite has **NOT** been executed in a confirmed full local run in the current environment. A previous attempt to obtain an executable checkout failed because GitHub DNS resolution was unavailable. GitHub Actions are intentionally not being consumed as a routine substitute because remote resources are scarce.

Therefore:
- do not claim a new passing-test count;
- do not merge to `main` solely from static inspection;
- when an executable checkout becomes available, run the complete suite and synthetic destructive qualification, repair in batches, then rerun.

## Product/account boundary
Original photographs remain read-only. Pixel/byte reads require the established explicit-consent pathways. No cloud CV/generative AI is required. No marketplace upload, submission, publication or deletion is authorized by this development work. The previously authorized non-original Dreamstime working-copy test remains unfinished and must not be continued without explicit action-time instruction.

## Next development order
1. Consolidate the 0.07 review surface with candidate-dashboard UX and authoritative shortlist status.
2. Continue 0.08 marketplace-neutral adapter contracts without embedding unverified marketplace requirements.
3. Expand explainable portfolio intelligence and metadata assistance while keeping human control/no hidden score.
4. Execute full local qualification when a checkout becomes available.
5. Perform a small explicitly selected real-photo end-to-end dry run after qualification.
6. Only after authoritative requirements research, populate individual marketplace adapters with sourced, dated, stale-aware rules.
