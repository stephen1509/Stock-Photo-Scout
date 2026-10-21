# Stock Photo Scout — Current Authority

Status: 0.06 Reliability & QC implementation substantially complete; executable qualification pending (2026-10-21)

## Purpose
Stock Photo Scout is a local-first Windows assistant for reviewing an existing photo collection and identifying promising stock-photo candidates. Dreamstime is the first marketplace target, but the core must remain marketplace-neutral and useful without an account connection or online service.

## Non-negotiable rules
- Original photos are read-only: never rename, move, edit, upload, delete, or overwrite them.
- Dropbox is the primary private working/source-of-truth area; GitHub contains only deliberate public-safe code/docs/tests.
- Never commit originals, previews, generated private catalogs/drafts/workspace/preparation state, credentials, or personal photo data.
- Pixel/byte reads beyond metadata require explicit selection/consent.
- Derived previews/working copies stay outside the source-photo tree and never overwrite originals.
- Unknown marketplace requirements remain unknown until confirmed.
- Visual metrics are observations/suggestions, never marketplace acceptance decisions.
- Human final control is mandatory.
- No paid/cloud AI APIs, submission automation, deployment, Netlify, or GitHub Actions unless explicitly necessary and authorized.
- Development is local-first / remote-last; batch remote calls and commits.

## Qualified historical baseline
The older 0.05 offline baseline was previously qualified on Python 3.12. Historical documents report 79/79 for that qualified baseline. That historical count MUST NOT be presented as verification of the expanded 0.06 branch.

## 0.06 Reliability & QC — implemented, awaiting executable qualification
Current development branch: `improve/reliability-qc-006-20261021`.

Implemented:
- fail-closed preflight semantics, including explicit preview-integrity confirmation;
- multidimensional candidate review: human decision, technical state, stock potential, rights state, route, preparation state and edit-needed flag;
- structured rights/IP review with route-sensitive reviewed decisions bound to the selected commercial/editorial route;
- restored source→export provenance using consent-gated SHA-256 fingerprints and external deterministic state;
- provenance invalidation when source/export bytes change; changed exports require final QC again;
- exact-export final QC bound to the current export SHA-256, explicit 100% inspection and human confirmation;
- consolidated fail-closed readiness across review, rights, provenance, exact-file QC and current marketplace-requirement confirmation;
- strict persisted analysis validation, finite numeric/range checks and malformed-record rejection;
- hardened cross-platform path/traversal/symlink/source-tree protections;
- candidate dashboard DOM/path/request/concurrency hardening;
- direct `submission-ready` mutation removed from the dashboard/API workflow; legacy values remain readable but non-authoritative;
- localhost Host/Origin checks and restrictive browser security headers;
- expanded adversarial/regression tests for the above contracts.

## Qualification boundary
The expanded 0.06 test suite has NOT yet been executed in a confirmed full local run. The current execution environment could not obtain a checkout because DNS resolution for GitHub failed. A single explicitly permitted checkout attempt was made; it failed at DNS and was not repeatedly retried. GitHub Actions were deliberately not used because Actions minutes are scarce.

Therefore:
- 0.06 is **implemented/staticly reviewed**, not fully qualified;
- do not claim a new pass count;
- do not merge 0.06 to `main` solely on static inspection;
- when an executable checkout becomes available, immediately run the full suite, repair failures in batches, rerun, then perform synthetic destructive qualification.

## 0.07 Review Intelligence — authorized next phase
0.07 may proceed on the 0.06 development line while the qualification boundary remains explicit. It must remain advisory and human-controlled.

Planned scope:
1. two-stage review: fast screening then exact-pixel technical inspection for shortlisted candidates;
2. subject-aware focus review rather than treating texture/noise proxies as universal quality scores;
3. composition and stock-usefulness prompts;
4. similar/burst grouping to reduce redundant review;
5. independent technical quality and stock-potential dimensions;
6. explicit human decisions with reasons; no hidden AI/marketplace score;
7. preparation for a larger deliberately varied human-labelled calibration set;
8. no cloud CV/generative AI dependency.

## Marketplace/account boundary
A prior separately authorized non-original working-copy upload reached Dreamstime's unfinished edit-information screen. No portal metadata was saved and no image was submitted, published or finalized. Do not interact with Dreamstime or another marketplace without explicit action-time authorization.
