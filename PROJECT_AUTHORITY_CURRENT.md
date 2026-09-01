# Stock Photo Scout — Current Authority

Status: Checkpoint 0.05A (implementation in progress, 2026-09-01)

## Purpose

Stock Photo Scout is a local Windows assistant for reviewing an existing photo collection and identifying promising stock-photo candidates. Dreamstime is the intended first marketplace, but the project must remain useful without an account connection or online service.

## Current authority

The Dreamstime/tool research phase is complete. The current research record is `RESEARCH_BRIEF_2026-09-01.md`, and `APP_OPERATING_PLAN.md` is the approved operating/build plan.

Implementation now follows phases 0.05A–0.05E. The immediate phase is 0.05A: an explicit local candidate workspace with read-only source handling, consented preview access, and human-controlled candidate states.

## Non-negotiable rules

- Original photos are read-only: never rename, move, edit, upload, delete, or overwrite them.
- Dropbox is the main working storage and source of truth for project material.
- GitHub is for deliberate stable checkpoints, not continuous syncing or personal-photo storage.
- Do not commit originals, private previews, credentials, generated local catalogs, local drafts, or local workspace state.
- No paid APIs, AI/image services, marketplace submissions, cloud processing, CI, or deployment unless separately approved.
- Unknown marketplace requirements must be confirmed, not guessed or hard-coded.
- Pixel/byte reads beyond metadata require an explicitly selected image/folder and consent.
- Derived previews/working copies must live outside the source-photo tree and must never overwrite existing files.

## Current scope

Checkpoint 0.05A adds the first candidate-workspace foundation:

- explicit candidate states: `skip`, `maybe`, `shortlist`, `edit`, `metadata-ready`, `submission-ready`;
- deterministic local workspace manifests outside the source tree;
- explicit consent before source image bytes are read for a preview;
- non-overwriting byte-for-byte preview copies outside the source tree;
- path traversal, source-tree destination, symlink, unsupported-type, and overwrite safeguards.

This first slice deliberately avoids adding a new image-decoding dependency. Browser/gallery integration and generated thumbnail resizing remain 0.05A follow-up work.

Human review remains decisive. Nothing in 0.05A makes legal, rights, release, marketability, or Dreamstime acceptance determinations.

## Change control

Read this file, `CURRENT_STATUS.md`, `RESEARCH_BRIEF_2026-09-01.md`, and `APP_OPERATING_PLAN.md` before changing scope. Update authority/status when a checkpoint changes. GitHub checkpoints must contain only reviewed code/docs safe for the public repository.
