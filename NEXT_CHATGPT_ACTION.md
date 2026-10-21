# Next ChatGPT Action — Resume Stock Photo Scout on PC

Date saved: 2026-10-21

## Start here
Read, in order:
1. `FULL_AUDIT_2026-10-21.md`
2. `PROJECT_AUTHORITY_CURRENT.md`
3. `CURRENT_STATUS.md`
4. `TEST_PLAN.md`
5. `ROADMAP.md`
6. `APP_OPERATING_PLAN.md`
7. `REVIEW_INTELLIGENCE_0.07_PLAN.md`

## Current durable development state
Development branch: `improve/reliability-qc-006-20261021`.

The pre-PC full static audit is complete and saved. The latest audit checkpoint before this handoff was `af0019bbd2247d1b8cd1eadf8e38f7852e0c6795`; this handoff commit supersedes it as branch HEAD.

0.06 Reliability/QC is implemented but awaits a confirmed full executable qualification run. 0.07 Review Intelligence is substantially implemented, including human fast screen, Stage-2 focus/composition/usefulness review, similar-group preference, authoritative shortlist gating, integrated review UI and combined atomic review-packet persistence with legacy split-file fallback. 0.08 includes marketplace-rule provenance/persistence, marketplace-neutral adapter/preflight foundations, portfolio observations, deterministic human-controlled metadata assistance, factual marketplace outcome persistence and explainable historical outcome summaries.

The historical **79/79** result belongs only to the older qualified baseline. Never present it as verification of the expanded 0.06/0.07/0.08 branch and never invent a new passing-test count.

## Tomorrow's first action — PC local qualification
Use a local checkout of this branch. Record branch HEAD and Python version, then run:

`python -m unittest discover -s tests -v`

Prefer also capturing the complete output to a local text file. Collect all failures before changing code, classify them, repair in a substantial batch, then rerun the entire suite. Do not use GitHub Actions as a routine substitute.

## P1 audit targets to prove during qualification
1. Review-server concurrent saves: prove that simultaneous mutations cannot silently lose a human edit. Atomic replacement prevents torn JSON but does not by itself prove conflict-free concurrent editing.
2. Combined review-packet precedence/failure semantics:
   - only legacy review exists;
   - only legacy usefulness exists;
   - malformed combined packet exists alongside a valid legacy pair;
   - valid combined packet contradicts stale legacy split files;
   - persisted candidate path mismatch.
   New combined state must be authoritative; malformed authoritative state must fail closed rather than silently falling back.
3. Marketplace rule persistence: align parent-symlink and post-replace directory-durability hardening with the stronger review-packet store where appropriate, and test it.
4. Run all preparation/category-pair regression tests to prove route/editor/export/notes fields cannot shift.
5. Verify exact-export QC invalidation, provenance staleness, localhost Host/Origin/CSP behavior, path/traversal/UNC/Windows-drive/symlink refusal, and direct shortlist/submission-ready bypass refusal.

## After unit qualification
Perform the synthetic destructive qualification in `TEST_PLAN.md`: source immutability, external-only writes, interrupted/partial persistence, malicious paths/symlinks, malformed JSON/schema, concurrent mutations, stale provenance, changed export after QC, hostile filenames/metadata, stale marketplace rules, legacy-state compatibility and attempts to bypass authoritative shortlist/readiness gates.

Repair findings in batches and rerun until clean. Only then record the verified expanded-suite test count and qualification checkpoint.

## Documentation reconciliation after actual results
`PROJECT_AUTHORITY_CURRENT.md` still describes 0.07 largely as planned/next even though it is substantially implemented. `CURRENT_STATUS.md` predates some newest 0.08 work. Update both only after the local run so the documents can include factual qualification results rather than another static-only status rewrite.

## First real-photo product qualification — only after code qualification
Use a small set of photographs explicitly selected by the user. Pixel/byte reads require the established explicit-consent pathway. Run the complete local chain:

candidate → human 0.07 review → authoritative shortlist → factual preparation/route/rights → separate working export → provenance → exact-export 100% QC → current sourced marketplace rules → human marketplace preflight.

No marketplace submission is part of this dry run.

## Marketplace direction after qualification
Continue the marketplace-neutral 0.08 core, then 0.09 marketplace adapters beginning with Dreamstime. Marketplace-specific behavior such as Dreamstime category pairs should migrate behind the adapter boundary. Requirements must come from current authoritative sources with source URL, human verification date and staleness/review policy; unknown requirements remain unknown.

## Non-negotiable boundaries
- Original photographs are read-only: never rename, move, edit, overwrite, delete, embed metadata into, or upload them.
- Keep derived previews, analysis, drafts, catalogues, review packets, preparation records and working copies outside source-photo folders and out of Git.
- Pixel/byte reads beyond metadata require explicit selection/consent.
- Human final control is mandatory; visual metrics are observations/suggestions, never acceptance decisions.
- Local-first / remote-last. Batch remote calls and commits.
- No Work mode, Netlify, routine GitHub Actions, Remote Desktop Commander, cloud CV/generative AI, paid APIs or marketplace mutation for current qualification.
- No marketplace upload, submission, publication, deletion, account-setting change or credential exposure without separate explicit action-time authorization.
- The previously authorized non-original Dreamstime working-copy test remains unfinished; do not continue it without explicit instruction.
- Local preflight completeness is not legal clearance, marketplace eligibility, acceptance probability or sales prediction.
