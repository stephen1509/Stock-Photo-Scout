# Stock Photo Scout

Dreamstime-first, local Windows photo-selection assistant.

## Status

Research and operating-plan work are complete. Implementation is now in **Checkpoint 0.05A — local candidate workspace**.

The project already has a read-only scanner, deterministic local catalog, safe metadata extraction, duplicate grouping, local readiness drafts, spelling support, CLI tools, and a localhost draft dashboard. The first 0.05A workspace layer now adds explicit preview consent, non-overwriting local preview copies outside the source-photo tree, and human-controlled candidate states.

Dropbox remains the working source of truth. GitHub receives deliberate public-safe checkpoints only.

## Core safety rules

- Never modify original photographs.
- Preserve uncertainty; do not invent metadata, locations, people, rights status, or marketplace acceptance.
- Never put photos, private previews, local catalogs/drafts/workspace state, or credentials in Git.
- Derived previews and working copies must live outside the selected source folder.
- Do not upload photographs or use cloud/paid services without explicit approval.
- Keep Dreamstime submission manual unless separately authorized and confirmed compatible with current policy.

## 0.05A candidate states

The workspace model supports:

- `skip`
- `maybe`
- `shortlist`
- `edit`
- `metadata-ready`
- `submission-ready`

The first implementation stores deterministic local workspace JSON and can create a byte-for-byte preview copy of an explicitly selected JPEG/PNG/TIFF only after consent. It refuses source-tree destinations, traversal, symlinks, unsupported types, and overwrites.

Browser/gallery integration is the next 0.05A substep.

## Project authority

Start with:

1. `PROJECT_AUTHORITY_CURRENT.md`
2. `CURRENT_STATUS.md`
3. `RESEARCH_BRIEF_2026-09-01.md`
4. `APP_OPERATING_PLAN.md`

The older `NEXT_CHATGPT_ACTION.md` describes the research task that has now been completed and should be treated as historical context rather than the active next action.
