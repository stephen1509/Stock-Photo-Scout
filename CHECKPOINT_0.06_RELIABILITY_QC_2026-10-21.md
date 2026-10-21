# 0.06 Reliability & QC durable checkpoint — 2026-10-21

Branch: `improve/reliability-qc-006-20261021`

This checkpoint preserves the reliability work in a single durable branch commit without using GitHub Actions, deployment, Remote Desktop Commander, marketplace actions, or private-photo reads.

Implemented foundation:
- existing preflight now fails closed when preview integrity is unknown;
- source/export provenance work exists earlier in this branch;
- independent human candidate dimensions: review decision, technical state, stock potential, rights state, route, preparation state, notes/skip/edit-needed;
- structured human rights/IP checklist that flags questions and does not claim legal clearance;
- actual-pixel/100%-inspection crop planning for final-export QC, keeping downsampled analysis as screening only;
- combined readiness requires explicit positive provenance, final-QC and current-marketplace-rule review gates;
- focused regression tests cover fail-closed defaults, explicit-ready state, Windows/UNC/traversal path rejection, and final-QC crop planning.

Qualification truth: this commit is **implemented, awaiting local full-suite qualification**. Historical 79/79 applies to older main-line code and must not be reported as the current branch result. Do not use GitHub Actions merely to obtain a test count.

Next milestone: obtain a non-scarce local checkout, run the complete suite, repair failures in batches, then audit/integrate dashboard and CLI surfaces. Originals remain immutable; private photo bytes/pixels require explicit selected-image/folder consent; marketplace actions require explicit action-time authorization.
