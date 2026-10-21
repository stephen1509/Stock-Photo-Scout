# Next ChatGPT Action — Resume Stock Photo Scout

## Start here
Read, in order:
1. `PROJECT_AUTHORITY_CURRENT.md`
2. `CURRENT_STATUS.md`
3. `APP_OPERATING_PLAN.md`
4. `REVIEW_INTELLIGENCE_0.07_PLAN.md`
5. `ROADMAP.md`

## Current durable development state
Development branch: `improve/reliability-qc-006-20261021`.

0.06 Reliability/QC is implemented but awaits a confirmed full executable qualification run. 0.07 Review Intelligence is substantially implemented: human fast screen, Stage-2 review, similar-group preference, composition/usefulness, main-dashboard review integration, authoritative shortlist gating, complete review UI fields, and combined atomic review-packet persistence with legacy split-file fallback. 0.08 has marketplace-rule provenance, a neutral adapter gate, portfolio observations, a human-controlled marketplace outcome ledger, and explainable outcome summaries.

The historical **79/79** result belongs only to the older qualified baseline. Do not report it as verification of the expanded branch and do not invent a new passing-test count.

## First next action
Obtain a usable local checkout when possible and run:
`python -m unittest discover -s tests -v`

Then repair failures in batches and rerun. Do not consume GitHub Actions merely as a routine substitute for the missing local run.

After unit qualification, perform synthetic destructive qualification covering source immutability, external-only writes, partial-write cleanup, symlink/traversal/Windows path rejection, review-packet corruption/path mismatch, stale provenance, changed export invalidating QC, localhost dashboard safety, concurrent mutations, legacy ready records, and attempts to bypass authoritative shortlist/readiness gates.

## Safe implementation that can continue before executable qualification
1. Audit combined review-packet migration/failure semantics and remaining concurrency edges.
2. Continue marketplace-neutral 0.08 metadata/outcome analysis without embedding unverified marketplace requirements or acceptance predictions.
3. Keep Dreamstime-specific category behavior behind or moving toward the marketplace-adapter boundary.
4. Update status/test documentation as implementation changes, but never claim tests passed without execution.

## First real-photo product qualification — only after code qualification
Use a small set of photographs explicitly selected by the user. Pixel/byte reads still require the established explicit-consent pathway. Run the complete local chain: candidate → human 0.07 review → qualified shortlist → factual preparation/route/rights review → separate working export → provenance → exact-export 100% QC → current sourced marketplace rules → local human preflight. Do not submit anything.

## Non-negotiable boundaries
- Original photographs are read-only: never rename, move, edit, overwrite, delete, embed metadata into, or upload them.
- Keep derived previews, analysis, drafts, catalogues, review packets, preparation records and working copies outside source-photo folders and out of Git.
- No Work mode, Netlify, routine GitHub Actions, Remote Desktop Commander, cloud CV/generative AI, paid APIs, or marketplace mutation is required for current development.
- No marketplace upload, submission, publication, deletion, account-setting change or credential exposure without separate explicit action-time authorization.
- The previously authorized non-original Dreamstime working-copy test remains unfinished; do not continue it without explicit instruction.
- Local preflight completeness is not legal clearance, marketplace eligibility, acceptance probability, or sales prediction.
