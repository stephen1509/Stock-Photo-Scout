# Stock Photo Scout

Dreamstime-first, local Windows photo-selection assistant.

## Status
Checkpoint 0.04 is in progress. The project has a safe inventory, a deterministic local catalog, explicit non-overwriting JSON persistence outside photo sources, PNG/JPEG/TIFF dimensions, and a deliberately small privacy-conscious JPEG/TIFF EXIF subset. It adds explainable metadata prompts, opt-in SHA-256 exact-content grouping, and editable local preparation drafts; it does not claim visual similarity, rights clearance, or marketplace compliance. Dropbox is the primary working storage and project authority; GitHub receives deliberate stable checkpoints.

## Core safety rules
- Never modify original photographs.
- Preserve uncertainty; do not invent metadata, locations, people, or rights status.
- Do not upload photographs, credentials, or private project data without explicit approval.
- No paid AI services, automated agency submission, or deployment is part of this initial checkpoint.

## Planned first milestone
Establish project authority documents, a safe local folder scanner, a metadata catalogue, and focused tests before adding image analysis or agency integrations.

Checkpoint 0.01 established project authority and a safe inventory. Checkpoint 0.02 is adding local catalog and metadata foundations without inspecting personal photos. Start with [PROJECT_AUTHORITY_CURRENT.md](PROJECT_AUTHORITY_CURRENT.md), then [CURRENT_STATUS.md](CURRENT_STATUS.md).

The next user-directed research session is defined in [NEXT_CHATGPT_ACTION.md](NEXT_CHATGPT_ACTION.md).

## Local draft review

Review a local draft without opening its source photo:

```powershell
python stock_photo_scout.py review-draft local_drafts\img_0530.json
```

After you have confirmed a proper name or intentional spelling, save it to an explicit local dictionary and include that dictionary on later reviews:

```powershell
python stock_photo_scout.py accept-spelling local_drafts\accepted_spellings.json Todaiji
python stock_photo_scout.py review-draft local_drafts\img_0530.json --dictionary local_drafts\accepted_spellings.json
```

Create a new draft outside the selected photo folder, then explicitly update it as you review the photo:

```powershell
python stock_photo_scout.py create-draft "D:\Photos" IMG_0600.jpg local_drafts\img_0600.json --title "Temple at dawn" --keyword temple --keyword dawn
python stock_photo_scout.py edit-draft "D:\Photos" local_drafts\img_0600.json --logos unknown --notes "Check logos before any submission"
```

## Local visual dashboard

Start the browser dashboard for a selected source folder. It shows and updates only the local draft JSON files; it does not open or modify a photo.

```powershell
python stock_photo_scout.py dashboard "D:\Photos"
```

Open the displayed `http://127.0.0.1:8765` address. Press `Ctrl+C` in that PowerShell window when you are finished.
