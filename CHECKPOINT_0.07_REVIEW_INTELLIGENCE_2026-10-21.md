# Checkpoint 0.07 — Review Intelligence

Date: 2026-10-21
Branch: `improve/reliability-qc-006-20261021`

## Implemented
- Human-controlled fast-screen model: unreviewed / skip / hold / inspect.
- Explicit human reason codes; no aggregate stock/acceptance score.
- Deterministic similar/burst hints from exact hash, capture-time proximity and weak filename-sequence proximity.
- Human preferred-member decision for grouped candidates.
- Subject-aware actual-pixel inspection-region planning from a human-confirmed normalized subject region.
- Structured composition/stock-usefulness review: subject clarity, clutter, copy space, crop flexibility, redundancy and alternate orientation.
- Fail-closed Stage-1 → Stage-2 workflow assessment.
- External deterministic versioned persistence for review and usefulness state.
- Atomic overwrite, fsync, symlink/non-regular protection and source-tree write prohibition.
- Local ReviewService composing review, usefulness and workflow assessment.
- Legacy 0.06 preview compatibility fixed: preview metadata updates no longer masquerade as state transitions, so readable legacy `submission-ready` records can receive a preview without promotion/demotion.

## Safety/product boundaries
- Originals remain read-only.
- No automatic deletion or rejection from similar-group hints.
- No inferred marketplace acceptance.
- No cloud CV/generative AI dependency.
- No marketplace action.
- Pixel reads remain separately consent-gated by existing image/preview pathways.
- `submission-ready` remains governed by consolidated 0.06 readiness, not 0.07 review controls.

## Qualification truth
The expanded 0.06/0.07 suite has NOT been executed in a confirmed full local run in the current environment. Tests have been authored but no new passing count is claimed. Historical 79/79 applies only to the older qualified baseline.

## Next implementation batch
1. Expose ReviewService through localhost dashboard API/UI.
2. Keep DOM rendering safe with textContent/DOM construction; no candidate-controlled innerHTML.
3. Add dashboard tests for review load/save, malformed values, grouped preferred-member behavior and fail-closed shortlist assessment.
4. Reconcile candidate workspace `shortlist` state with 0.07 assessment so UI cannot imply review completion merely by selecting a legacy workspace state.
5. Later bind review completion into consolidated readiness without weakening the exact-export/provenance/final-QC gates.
