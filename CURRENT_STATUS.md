# Current Status

## Checkpoints 0.01–0.03 — complete

The local scanner, deterministic catalog/metadata foundation, metadata-only review prompts, and opt-in SHA-256 exact-duplicate grouping are complete and locally verified. Originals remain read-only.

## Checkpoint 0.04 — Stock readiness foundation (complete)

Implemented and verified:

- editable local title, keyword, note, and rights-observation drafts;
- explainable readiness prompts;
- offline spelling review and explicit accepted-spelling dictionary;
- CLI create/edit/review flows;
- localhost-only draft dashboard;
- non-overwriting local persistence outside source folders.

One user-selected candidate has a local draft and recorded observations. Remaining prompts require human review; no legal or marketplace conclusion is made.

## Research and operating plan — complete (2026-09-01)

The requested current Dreamstime/tool-ecosystem research was completed and recorded in `RESEARCH_BRIEF_2026-09-01.md`.

The resulting end-to-end implementation plan is recorded in `APP_OPERATING_PLAN.md`. Research is no longer the next action.

## Checkpoint 0.05A — Local candidate workspace (in progress)

Implemented and focused-tested:

- local candidate-workspace model;
- human-controlled states: `skip`, `maybe`, `shortlist`, `edit`, `metadata-ready`, `submission-ready`;
- deterministic workspace JSON outside the source tree;
- explicit consent required before preview byte reads;
- supported JPEG/PNG/TIFF preview copies outside the source tree;
- preview copies are exclusive/non-overwriting;
- traversal, source-tree destination, symlink, unsupported-type, and invalid-state safeguards;
- standalone no-install workspace CLI for preview creation, candidate-state updates, and manifest display.

Focused 0.05A tests: **6 passed**.

Still to do inside 0.05A:

- integrate the workspace into the main localhost dashboard/gallery;
- decide whether full-size preview copies are sufficient or whether to introduce a reviewed local thumbnail-decoding dependency;
- run an explicitly approved small real-photo-folder trial and verify originals remain unchanged.

## Later phases

- 0.05B — local technical/visual suggestions;
- 0.05C — metadata and editor handoff;
- 0.05D — Dreamstime preflight/manual submission packet;
- 0.05E — optional AI/cloud/service integrations only after separate approval.
