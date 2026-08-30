# Stock Photo Scout — Current Authority

Status: Checkpoint 0.01 (2026-08-31)

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

Checkpoint 0.01 establishes product rules, technical boundaries, and a local-only candidate-file inventory. It does not inspect pixels or EXIF, score photos, detect duplicates, create listings, or connect to Dreamstime.

## Change control

Read this file and `CURRENT_STATUS.md` before changing scope. Update both when a checkpoint changes. Make one GitHub checkpoint only after focused local verification passes.
