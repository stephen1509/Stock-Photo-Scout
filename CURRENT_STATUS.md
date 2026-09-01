# Current Status

## Checkpoints 0.01–0.04 — complete

The read-only scanner, deterministic catalog/metadata foundation, exact-duplicate grouping, explainable technical prompts, local title/keyword/notes/rights drafts, spelling support, CLI workflows, and localhost draft dashboard are complete.

## Research and operating plan — complete (2026-09-01)

Current Dreamstime contributor workflow and the Windows tool ecosystem were researched and recorded in `RESEARCH_BRIEF_2026-09-01.md`. The approved phased operating/build plan is `APP_OPERATING_PLAN.md`.

## 0.05A — Local candidate workspace

Offline implementation is complete.

Implemented:
- human-controlled states: `skip`, `maybe`, `shortlist`, `edit`, `metadata-ready`, `submission-ready`;
- deterministic local workspace JSON outside source folders;
- explicit consent before source image-byte reads;
- non-overwriting JPEG/PNG/TIFF preview copies outside the source tree;
- candidate gallery layered over the localhost dashboard;
- original images are never served directly;
- explicit preview integrity/staleness verification with SHA-256;
- cross-platform path validation, traversal rejection, symlink protection, and source-tree write refusal;
- no-install CLI and browser controls.

Still required before formally closing 0.05A:
1. a small explicitly selected real-photo-folder trial on the Windows PC;
2. post-trial verification that originals remain unchanged;
3. decide from the real trial whether full-size byte-for-byte preview copies are sufficient or resized thumbnails are worth introducing.

## 0.05B — Local technical/visual suggestions

Offline core implemented.

Implemented:
- a pure luminance-grid analysis engine independent of any decoder;
- mean luminance;
- dark/bright clipping ratios;
- explainable sharpness proxy;
- explainable noise proxy;
- optional caller-configured thresholds only;
- no Dreamstime acceptance thresholds or hidden quality score;
- synthetic tests.

Still required:
- select/approve a local image-decoding path;
- decode actual user-selected images;
- calibrate measurements on real photographs;
- only then consider additional signals such as horizon/composition/dust.

## 0.05C — Metadata and editor handoff

Offline foundation implemented.

Implemented:
- human-approved title, description, keywords, categories;
- commercial/editorial human choice;
- editor target: none/darktable/RawTherapee/GIMP/other;
- working-export relative path;
- notes;
- deterministic external JSON persistence;
- CLI create/edit/review commands;
- localhost Preparation page per candidate.

No editor is launched automatically and no original is modified.

## 0.05D — Manual Dreamstime preflight

Offline foundation implemented.

Implemented:
- local manual preflight packet;
- preparation-field completeness prompts;
- candidate-state check;
- unresolved people/property/logo/release prompt support;
- preview-integrity input;
- current-Dreamstime-requirements-reviewed gate;
- technical-observation collection;
- human-readable packet and deterministic JSON;
- CLI and localhost dashboard access.

`local_packet_complete` means only that this local checklist has no recorded blockers. It does not mean legal clearance, Dreamstime eligibility, acceptance, or upload success.

## 0.05E — Optional integrations

Not started. Cloud/AI services, paid APIs, account access, upload assistance, or automation remain outside current authorization and require a separate explicit decision.

## Verification

The final offline development state was verified on Python 3.12 with:

`python -m unittest discover -s tests -v`

Result:
- **63 tests run**
- **63 passed**
- **0 failures / 0 errors**
- temporary GitHub Actions verification workflows were removed after use.

## Current genuine blocker

Further meaningful visual-development validation now requires the Windows PC and an explicitly selected real photo folder. Until then, no source photographs need to be read or modified.
