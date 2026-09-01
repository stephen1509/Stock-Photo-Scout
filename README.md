# Stock Photo Scout

Dreamstime-first, local Windows photo-selection assistant.

## Status

Research and the operating plan are complete. Implementation is now in **Checkpoint 0.05A — local candidate workspace**.

The project has a read-only scanner, deterministic local catalog, safe metadata extraction, duplicate grouping, local readiness drafts, spelling support, CLI tools, and a localhost draft dashboard. 0.05A now adds explicit preview consent, non-overwriting preview copies outside the source tree, human-controlled candidate states, and a standalone no-install workspace CLI.

Dropbox remains the working source of truth. GitHub receives deliberate public-safe checkpoints only.

## Core safety rules

- Never modify original photographs.
- Preserve uncertainty; do not invent metadata, locations, people, rights status, or marketplace acceptance.
- Never put photos, private previews, local catalogs/drafts/workspace state, or credentials in Git.
- Derived previews and working copies must live outside the selected source folder.
- Do not upload photographs or use cloud/paid services without explicit approval.
- Keep Dreamstime submission manual unless separately authorized and confirmed compatible with current policy.

## 0.05A workspace CLI

Create one preview copy only after explicitly consenting to read the selected image:

```powershell
python stock_photo_workspace.py preview "D:\Photos" IMG_0600.jpg local_previews --consent
```

Set a human review state in a local workspace manifest:

```powershell
python stock_photo_workspace.py set-state "D:\Photos" local_workspace\candidates.json IMG_0600.jpg shortlist --preview-relative-path IMG_0600.jpg
```

Show the workspace:

```powershell
python stock_photo_workspace.py show local_workspace\candidates.json
```

Supported states are `skip`, `maybe`, `shortlist`, `edit`, `metadata-ready`, and `submission-ready`.

The current preview implementation makes a byte-for-byte local copy rather than resizing/decoding the image. That avoids adding an unapproved dependency. Dashboard/gallery integration is the next 0.05A substep.

## Project authority

Read:

1. `PROJECT_AUTHORITY_CURRENT.md`
2. `CURRENT_STATUS.md`
3. `RESEARCH_BRIEF_2026-09-01.md`
4. `APP_OPERATING_PLAN.md`

`NEXT_CHATGPT_ACTION.md` is historical context for the now-completed research phase.
