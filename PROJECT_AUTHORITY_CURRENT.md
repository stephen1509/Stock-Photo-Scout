# Stock Photo Scout — Current Authority

Status: Checkpoint 0.04 (in progress, 2026-08-31)

## Purpose

Stock Photo Scout is a local Windows assistant for reviewing an existing photo collection and identifying promising stock-photo candidates. Dreamstime is the intended first marketplace, but the project must remain useful without an account connection or online service.

## Non-negotiable rules

- Original photos are read-only: never rename, move, edit, upload, delete, or overwrite them.
- Dropbox is the main working storage and source of truth for project material.
- GitHub is for deliberate stable checkpoints, not continuous syncing or personal-photo storage.
- Do not commit originals, private previews, credentials, or generated local catalogs.
- No paid APIs, AI/image services, marketplace submissions, cloud processing, CI, or deployment in the initial milestones.
- Unknown marketplace requirements must be confirmed, not guessed or hard-coded.

## Current scope

Checkpoint 0.04 adds editable local title/keyword drafts and user-supplied commercial-readiness observations. It may prompt manual follow-up but does not make legal, rights, release, or marketplace acceptance determinations; it does not create listings or connect to Dreamstime.

The catalog stores relative paths, file facts, dimensions, orientation, original capture-time text, camera make/model, and lens model. GPS, owner/serial identifiers, comments, thumbnails, and arbitrary EXIF fields remain out of scope.

Technical review thresholds are caller-configured prompts, not marketplace requirements or acceptance decisions. Human review remains decisive.

Title/keyword drafts and readiness observations are local, optional, and excluded from Git. They are not generated from images or sent to external services.

## Change control

Read this file and `CURRENT_STATUS.md` before changing scope. Update both when a checkpoint changes. Make one GitHub checkpoint only after focused local verification passes.
