# Stock Photo Scout

Dreamstime-first, local Windows photo-selection assistant.

## Current state

The research and operating plan are complete, and the offline-safe engineering foundation now extends through 0.05A–0.05D.

The project includes:
- read-only scanner and deterministic catalog;
- privacy-conscious metadata extraction;
- exact duplicate grouping;
- title/keyword/rights drafts and spelling support;
- consented local preview copies and candidate states;
- localhost candidate gallery;
- SHA-256 preview-integrity/staleness verification;
- decoder-independent luminance/clipping/sharpness/noise signal engine;
- consent-gated analysis orchestration and external analysis records;
- automatic same-candidate analysis → preflight handoff;
- optional bounded Pillow-compatible decoder adapter (not installed or required yet);
- local preparation records for title, description, keywords, categories, route, editor and working export;
- manual preflight packet generation;
- CLI and browser workflows.

**77/77 tests pass** on Python 3.12.

## Safety

- Originals are never modified.
- Originals are never served directly by the dashboard.
- Local derived data stays outside the source-photo tree.
- No photo, preview, catalog, draft, workspace/preparation state or credential belongs in Git.
- No cloud/AI/paid service, Dreamstime account access, upload or automated submission is authorized.
- “Local packet complete” is not a legal or Dreamstime acceptance decision.

## Dashboard

```powershell
python stock_photo_scout.py dashboard "D:\Photos"
```

The candidate gallery supports:
`skip`, `maybe`, `shortlist`, `edit`, `metadata-ready`, `submission-ready`.

Each candidate also has a **Preparation / preflight** page for local metadata/editor handoff and the manual Dreamstime checklist.

Defaults:
- drafts: `local_drafts`
- spellings: `local_drafts\accepted_spellings.json`
- previews: `local_previews`
- candidate workspace: `local_workspace\candidates.json`
- preparation: `local_preparation`
- analysis: `local_analysis`
- port: `8765`

## Preparation CLI

Create preparation:

```powershell
python stock_photo_scout.py create-preparation "D:\Photos" IMG_0600.jpg local_preparation\img_0600.json --title "Temple at dawn" --description "Historic temple exterior at dawn" --keyword temple --keyword dawn --route editorial
```

Review:

```powershell
python stock_photo_scout.py review-preparation local_preparation\img_0600.json
```

Manual preflight:

```powershell
python stock_photo_scout.py preflight local_preparation\img_0600.json --state submission-ready --preview-integrity match --current-requirements-reviewed
```

No command above uploads or submits anything.

## Current next gate

Further useful visual validation now requires:
1. the Windows PC;
2. an explicitly selected small real-photo folder;
3. a reviewed local decoding path;
4. a real-photo trial followed by original-file integrity verification.

See `PROJECT_AUTHORITY_CURRENT.md`, `CURRENT_STATUS.md`, `RESEARCH_BRIEF_2026-09-01.md`, and `APP_OPERATING_PLAN.md`.
