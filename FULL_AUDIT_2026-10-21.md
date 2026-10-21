# Stock Photo Scout — Full Pre-PC Qualification Audit

Date: 2026-10-21
Branch audited: `improve/reliability-qc-006-20261021`
Static audit baseline before this report: `c52c05bca53838b54f26a1bb3a6a0e71a4d2ce43`

## Executive conclusion
The project has a coherent safety-first architecture and is ready for executable qualification, not for merge or marketplace use. The largest risk is no longer missing architecture; it is the amount of 0.06–0.08 code that has been statically reviewed but not run together in a confirmed full local test pass. Tomorrow's PC session should therefore begin with qualification, not new feature work.

No original/private photographs were inspected during this audit. No marketplace action, deployment, GitHub Actions, Netlify, cloud AI or paid API was used.

## Authority and documentation audit
Strengths:
- Original-photo immutability, explicit pixel/byte consent, external derived state, human control and marketplace-action boundaries are consistently stated.
- `ROADMAP.md` and `TEST_PLAN.md` now reflect the 0.06–0.10 direction and correctly separate historical 79/79 qualification from the expanded branch.
- `CURRENT_STATUS.md` accurately refuses to claim an expanded passing count.

Drift found:
- `PROJECT_AUTHORITY_CURRENT.md` still describes 0.07 primarily as an authorized/planned next phase even though 0.07 is now substantially implemented and 0.08 has begun.
- `CURRENT_STATUS.md` predates the latest combined review packet, metadata assistant, marketplace rule store, marketplace preflight and outcome-analysis additions.
- package `__init__.py` exposes mostly the older foundation surface; newer modules are imported directly by tests/application code. This is not necessarily a defect, but the intended public package API should be decided after qualification.

Action: refresh authority/status after executable results so documentation records verified reality rather than another static estimate.

## Architecture audit
### Strong / coherent
- Core remains marketplace-neutral while Dreamstime-specific behavior is isolated enough to migrate behind an adapter.
- Readiness is fail-closed across human review, route-sensitive rights, provenance, exact-export QC and current marketplace requirements.
- `assess_recorded_readiness` re-verifies actual recorded source/export fingerprints instead of accepting a caller-invented provenance boolean.
- 0.07 separates observations, prompts and human decisions; no hidden acceptance/suitability score.
- authoritative shortlist requires completed 0.07 review rather than trusting a legacy workspace label.
- combined review packet fixes the earlier torn-state risk between review and usefulness files.
- 0.08 stores provenance ABOUT marketplace requirements rather than embedding invented marketplace facts.
- outcome learning remains factual/human-controlled and does not silently tune thresholds.

### Architecture debt
1. Dreamstime's maximum-three category-pair rule remains in generic preparation code. Do not remove it before qualification; migrate it behind the Dreamstime adapter in 0.09 with regression coverage.
2. There are both standalone review-dashboard and integrated candidate-dashboard surfaces. Keep both for qualification, then decide whether standalone review is a supported diagnostic surface or redundant maintenance burden.
3. Legacy split review/usefulness persistence remains readable. A future schema/migration policy should define how long this compatibility path remains.

## Persistence and filesystem audit
### Strong
`review_packet_store.py` has strict schema validation, source-tree refusal, regular-file checks, symlink-parent refusal, same-directory temp file, file fsync, atomic replace and parent-directory fsync.

### Findings requiring qualification/repair
**A1 — medium: marketplace rule store hardening is weaker than review packet store.**
`marketplace_rule_store.py` resolves the destination and rejects a symlink target, but it does not explicitly reject symlinked parent directories and does not fsync the parent directory after `os.replace`. Align it with the stronger packet-store persistence pattern after the first test run, or before real rule profiles are relied upon.

**A2 — medium: one-sided legacy review state needs explicit fail-closed tests.**
`ReviewService.load` will combine an existing legacy review with default usefulness, or existing usefulness with default review. The workflow should block this, but tests should prove neither one-sided state can qualify.

**A3 — medium: malformed combined packet precedence needs explicit proof.**
When a combined packet exists, `ReviewService` uses it rather than falling back to legacy split files. This is the correct fail-closed design. Add/execute a test proving a malformed combined packet cannot be bypassed by a valid stale legacy pair.

**A4 — low/medium: combined-packet-vs-legacy precedence needs explicit proof.**
A valid combined packet should remain authoritative even when contradictory legacy split files exist. Add/execute this regression test.

## Concurrency audit
**A5 — medium/high: standalone review server uses `ThreadingHTTPServer` but the visible save path has no mutation lock/version token.**
Atomic file replacement prevents partial JSON, but simultaneous saves can still be last-writer-wins and lose a human edit. The candidate dashboard already has mutation-lock infrastructure elsewhere. During PC qualification, create a concurrent-save test and either serialize ReviewService mutations or add optimistic revision checking. This is the most important newly identified runtime risk in the static audit.

## Readiness and safety audit
Strong:
- literal `True` gates are used for 0.07 completion and current marketplace review;
- provenance errors become blockers;
- exact export SHA binds final QC;
- changed export/source cannot silently retain provenance confidence;
- marketplace preflight is downstream of core readiness rather than a bypass;
- direct `submission-ready` mutation remains prohibited.

Qualification targets:
- changed export after QC;
- changed source after provenance;
- missing/false consent;
- unknown composition;
- unresolved rights route mismatch;
- stale marketplace profile;
- false core readiness with an otherwise-current profile;
- legacy shortlist/submission-ready records.

## HTTP/browser surface audit
Strong:
- localhost binding;
- Host/Origin checking;
- no-store, nosniff and restrictive CSP;
- request-size limit;
- no originals route in review server;
- textContent-based dynamic rendering in the reviewed 0.07 surface.

Qualification targets:
- hostile filenames and text;
- malformed Content-Length and JSON;
- non-local Host/Origin;
- traversal through relative_path;
- concurrent POST saves;
- ensure no route can serve source-photo bytes.

## Test-suite audit
The repository contains both historical foundation tests and dedicated 0.06/0.07/0.08 regression tests. This is good coverage breadth, but no static audit can replace execution. The full suite must run before any pass-count or merge claim.

Mandatory first PC command:

```powershell
python -m unittest discover -s tests -v
```

Capture output:

```powershell
python -m unittest discover -s tests -v *> qualification-results.txt
```

After the ordinary suite is green, run the destructive cases in `TEST_PLAN.md`.

## Product/workflow audit
The intended real workflow is now coherent:

candidate → 0.07 human review → authoritative shortlist → factual metadata → route/rights → separate working export → provenance → exact-export 100% QC → current sourced marketplace rules → human marketplace preflight.

The remaining gap is proof that this chain works end-to-end in one executable environment. Real-photo testing should wait until synthetic/local qualification is clean.

## Marketplace audit
Current design correctly avoids claiming current Dreamstime requirements from old/static knowledge. 0.09 must research authoritative current marketplace rules and persist source URL + verification date + staleness. Dreamstime first; other marketplaces later. Upload/submission is outside qualification and remains explicitly action-authorized.

## Calibration audit
The existing 16-image human-labelled pass is evidence that simple sharpness/noise proxies are not reliable universal quality classifiers. Keep them advisory. Expand toward roughly 100–200 deliberately varied human-reviewed images only after code qualification. Do not use private photos for cloud model analysis.

## Priority findings
- **P0:** execute the complete expanded suite; no merge/pass-count before this.
- **P0:** destructive qualification proving originals cannot be mutated and readiness cannot be bypassed.
- **P1:** investigate/fix concurrent review save lost-update risk.
- **P1:** add one-sided legacy and malformed/precedence packet tests.
- **P1:** align marketplace-rule persistence hardening with review-packet persistence.
- **P1:** batch-repair all runtime failures discovered tomorrow.
- **P2:** refresh authority/status docs after verified results.
- **P2:** move Dreamstime-specific category rules behind 0.09 adapter after qualification.
- **P2:** decide supported public API/export surface and standalone review-dashboard role.
- **P3:** larger human calibration and real-photo product trial.

## Go / no-go assessment
- Continue local development: **GO**.
- Run local full qualification tomorrow: **GO — immediate next step**.
- Use a small real-photo set before tests/destructive qualification: **NO-GO**.
- Merge development branch to main now: **NO-GO**.
- Marketplace upload/submission now: **NO-GO**.
- GitHub Actions/Netlify as routine qualification substitute: **NO-GO under current resource constraints**.

## Tomorrow's exact order
1. Verify Python and Git locally.
2. Checkout/update `improve/reliability-qc-006-20261021`.
3. Record branch HEAD and Python version.
4. Run complete unit suite and save output.
5. Classify every failure together.
6. Repair in a batch; rerun complete suite.
7. Add/fix concurrency and persistence-edge tests identified above.
8. Run destructive qualification.
9. Repair/rerun until clean.
10. Record actual test count and qualification checkpoint.
11. Only then plan the controlled real-photo dry run and 0.09 Dreamstime adapter.

This audit is static and deliberately conservative: unexecuted code is treated as unqualified even when inspection looks sound.
