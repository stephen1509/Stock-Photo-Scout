# Stock Photo Scout — Current Authority

Status: Offline 0.05A–0.05D foundation implemented; first approved real-photo validation complete (2026-09-03)

## Purpose

Stock Photo Scout is a local Windows assistant for reviewing an existing photo collection and identifying promising stock-photo candidates. Dreamstime is the intended first marketplace, but the project must remain useful without an account connection or online service.

## Current authority

The Dreamstime/tool research is complete. `RESEARCH_BRIEF_2026-09-01.md` and `APP_OPERATING_PLAN.md` remain the research and operating authorities.

Offline-safe development has advanced through the local foundations of phases 0.05A–0.05D. The first explicitly approved image trial completed with an external preview and bounded local decoding; original-file integrity was confirmed afterward.

## Non-negotiable rules

- Original photos are read-only: never rename, move, edit, upload, delete, or overwrite them.
- Dropbox is the main working storage/source of truth; GitHub is for deliberate public-safe checkpoints.
- Never commit originals, previews, generated private catalogs/drafts/workspace/preparation state, credentials, or personal photo data.
- Pixel/byte reads beyond metadata require an explicitly selected image/folder and consent.
- Derived previews/working copies must live outside the source-photo tree and never overwrite existing files.
- Unknown marketplace requirements remain unknown until confirmed.
- Visual metrics are observations/suggestions, never acceptance decisions.
- No paid APIs, cloud AI/image services, Dreamstime account access, uploads, submission automation, CI, or deployment unless separately approved.

## Implemented offline scope

### 0.05A
Candidate states, consented external previews, gallery/dashboard, preview integrity verification, and path/source-write safeguards.

### 0.05B core
Decoder-independent luminance, clipping, sharpness-proxy, and noise-proxy measurements using caller-configured thresholds only. The consent-gated decoder orchestration, external analysis-record persistence, same-candidate analysis→preflight handoff, and an optional bounded Pillow-compatible adapter are also implemented. A 16-image human-labelled local pass has a descriptive `calibration-report` command; it never trains a model or decides suitability. Pillow is not installed or authorized as a required dependency yet.

### 0.05C foundation
Human metadata, commercial/editorial route, editor target, working-export tracking, local persistence, CLI and dashboard preparation workflow.

### 0.05D foundation
Manual preflight packet combining local preparation completeness, candidate state, technical observations, unresolved rights prompts, preview-integrity state, and a current-requirements-reviewed flag.

## Verification

Final offline state: **79/79 tests passed** on Python 3.12. Temporary verification workflows were removed after completion.

## Current stop condition

0.05A is locally validated, and 0.05B has completed a 16-image human-labelled descriptive pass with source integrity confirmed. Do not claim 0.05B is calibrated until a broader, deliberately selected human-labelled set supports reliable review guidance. The logged-in Dreamstime contributor UI was inspected read-only; uploads and submissions remain unperformed.

0.05E remains outside current authorization.
