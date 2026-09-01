# Stock Photo Scout

Dreamstime-first, local Windows photo-selection assistant.

## Status

Research and the operating plan are complete. Implementation is in **Checkpoint 0.05A — local candidate workspace**.

The project now has a read-only scanner, deterministic local catalog, safe metadata extraction, duplicate grouping, local readiness drafts, spelling support, CLI tools, explicit local preview consent, human-controlled candidate states, and a localhost candidate gallery.

Dropbox remains the working source of truth. GitHub receives deliberate public-safe checkpoints only.

## Core safety rules

- Never modify original photographs.
- Preserve uncertainty; do not invent metadata, locations, people, rights status, or marketplace acceptance.
- Never put photos, private previews, local catalogs/drafts/workspace state, or credentials in Git.
- Derived previews and working copies must live outside the selected source folder.
- Do not upload photographs or use cloud/paid services without explicit approval.
- Keep Dreamstime submission manual unless separately authorized and confirmed compatible with current policy.

## Candidate gallery

Start the enhanced local dashboard:

```powershell
python stock_photo_scout.py dashboard "D:\Photos"
```

Defaults:

- local drafts: `local_drafts`
- accepted spellings: `local_drafts\accepted_spellings.json`
- local previews: `local_previews`
- candidate state: `local_workspace\candidates.json`
- localhost port: `8765`

Optional overrides:

```powershell
python stock_photo_scout.py dashboard "D:\Photos" --previews-dir local_previews --workspace local_workspace\candidates.json --port 8765
```

The browser lists candidates from the local draft/workspace data, displays only derived preview copies, and lets the photographer choose:

`skip`, `maybe`, `shortlist`, `edit`, `metadata-ready`, or `submission-ready`.

If a candidate has no preview, the browser asks for explicit confirmation before reading that selected image to create a local preview copy. Originals are never served directly to the browser and are not modified.

## Workspace CLI

The standalone workspace commands remain available.

Create one preview after explicit consent:

```powershell
python stock_photo_workspace.py preview "D:\Photos" IMG_0600.jpg local_previews --consent
```

Set state:

```powershell
python stock_photo_workspace.py set-state "D:\Photos" local_workspace\candidates.json IMG_0600.jpg shortlist --preview-relative-path IMG_0600.jpg
```

Show workspace:

```powershell
python stock_photo_workspace.py show local_workspace\candidates.json
```

The current preview implementation makes a byte-for-byte local copy rather than resizing/decoding the image. This avoids adding an unapproved dependency.

## Verification state

The original 0.05A workspace/CLI focused tests passed (6 tests). Four additional focused candidate-dashboard tests also passed in an isolated compatibility harness. A full repository-wide regression run and a user-approved small real-photo trial are still required before closing 0.05A.

## Project authority

Read:

1. `PROJECT_AUTHORITY_CURRENT.md`
2. `CURRENT_STATUS.md`
3. `RESEARCH_BRIEF_2026-09-01.md`
4. `APP_OPERATING_PLAN.md`

`NEXT_CHATGPT_ACTION.md` is historical context for the completed research phase.
