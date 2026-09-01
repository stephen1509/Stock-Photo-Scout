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

Implemented:

- local candidate-workspace model;
- human-controlled states: `skip`, `maybe`, `shortlist`, `edit`, `metadata-ready`, `submission-ready`;
- deterministic workspace JSON outside the source tree;
- explicit consent required before preview byte reads;
- supported JPEG/PNG/TIFF preview copies outside the source tree;
- preview copies are exclusive/non-overwriting;
- traversal, source-tree destination, symlink, unsupported-type, and invalid-state safeguards;
- standalone no-install workspace CLI;
- candidate gallery layered over the existing localhost draft dashboard;
- the normal `dashboard` command now launches the candidate gallery;
- browser state controls persist to the local workspace manifest;
- the browser can serve only derived preview copies, never originals;
- preview creation requires an explicit browser confirmation and consent flag.

Verification:

- the original 0.05A workspace/CLI focused suite had **6 passing tests**;
- the candidate-dashboard integration has **4 additional focused passing tests** in an isolated compatibility harness;
- those integration tests cover source-byte preservation, consent enforcement, persisted state, external workspace paths, and traversal rejection.
- a complete repository-wide regression run is still required on the working PC before 0.05A is closed.

Still to do inside 0.05A:

- run the full repository test suite on the working copy;
- run an explicitly approved small real-photo-folder trial and verify originals remain unchanged;
- decide whether full-size preview copies are sufficient or whether to introduce a reviewed local thumbnail-decoding dependency.

## Later phases

- 0.05B — local technical/visual suggestions;
- 0.05C — metadata and editor handoff;
- 0.05D — Dreamstime preflight/manual submission packet;
- 0.05E — optional AI/cloud/service integrations only after separate approval.


## 0.05A repository-wide verification — 2026-09-01

A temporary GitHub Actions workflow ran the exact repository checkpoint on Python 3.12 with:

`python -m unittest discover -s tests -v`

The first run exposed one cross-platform safety regression: Windows drive-qualified candidate paths such as `C:outside.jpg` were not rejected when tests ran on POSIX. The validator was hardened with host-independent Windows-path detection.

Verification after the fix:
- **47 tests run**
- **47 passed**
- **0 failures / 0 errors**
- verified commit: `fa6ab2861ad6df7f061f4540767ccca012a3b974`
- temporary CI workflow removed immediately after verification

Remaining 0.05A gates:
1. small real-photo-folder trial on the user's Windows PC;
2. verify originals remain unchanged after that trial;
3. decide whether full-size local preview copies are acceptable or whether resized thumbnails should be added.
