# Stock Photo Scout — Operating Plan

**Objective:** help Stephen turn a large local photo collection into a small, high-quality, human-approved set of Dreamstime-ready submissions—while preserving originals, privacy, and final human control.

**Decision principle:** the app does not decide that an image is marketable, legally cleared, or accepted by Dreamstime. It assembles evidence, catches avoidable issues, coordinates the right local tools, and produces a clear manual submission packet.

## 1. The product in one view

```text
Read-only original photo folder
        |
        v
Stock Photo Scout: inventory, technical facts, duplicate grouping, review queue
        |
        +--> human shortlist and observations
        |          |
        |          +--> darktable / RawTherapee: non-destructive development
        |          +--> GIMP: deliberate pixel retouching on a working copy
        |          +--> digiKam: optional DAM/tagging management
        |          +--> ExifTool: explicit sidecar/metadata handoff only
        v
Stock Photo Scout: evidence-based preflight + approved submission packet
        |
        v
Photographer manually uploads and submits in Dreamstime
```

The first meaningful outcome is not “upload everything.” It is a ranked, explainable shortlist of images that have passed technical review, human visual review, metadata preparation, and rights/context checks.

## 2. Roles and boundaries

| Component | Owns | Must never do by default |
| --- | --- | --- |
| **Stock Photo Scout** | Local inventory; dimensions/EXIF subset; exact duplicates; review queues; drafts; checklists; export packet | Modify original photos, claim legal clearance/acceptance, upload or submit files |
| **darktable** | Non-destructive RAW review/development, ratings/tags, export of selected working copies | Be launched against source folders until the user chooses sidecar/storage behaviour |
| **RawTherapee** | Alternative RAW development and processing profiles | Write profiles alongside originals unless that has been explicitly accepted |
| **GIMP** | Manual retouching of an exported working copy | Overwrite an original or perform automatic “improvement” |
| **digiKam** | Optional asset management, tags and batch workflow | Perform metadata writes without a preview and explicit user confirmation |
| **ExifTool** | Read metadata; later generate externally stored XMP sidecars or verified metadata packets | Run a broad metadata-writing command against a source folder |
| **Dreamstime** | Receives a photographer-selected final export; review and acceptance | Receive photos, metadata, or credentials automatically from this app |

## 3. The end-to-end operating workflow

### A. Select and inventory a folder

1. Stephen explicitly chooses one photo folder.
2. Stock Photo Scout inventories supported files without opening pixel data or changing the folder.
3. It records only local, minimally necessary facts: relative path, size, modified time, supported format, dimensions, orientation, limited camera/lens/capture-time text, and metadata-read status.
4. The catalogue and drafts are saved outside the photo folder, with path-safe, non-overwriting saves.

**Output:** a deterministic local catalogue and a repeatable starting point.

### B. Create a focused candidate queue

1. Remove exact duplicates from the first pass using opt-in SHA-256 grouping.
2. Group by clear technical follow-ups: unreadable file, unsupported format, missing dimensions, orientation transform, or a user-set pixel threshold.
3. Let Stephen mark candidates as `skip`, `maybe`, `shortlist`, `edit`, `metadata-ready`, or `submission-ready`.
4. Never use a numerical “quality score” as a submission decision. If a visual signal is later introduced, show the reason and confidence as a suggestion only.

**Output:** a manageable shortlist, with all exclusions traceable to a human decision or a factual flag.

### C. Human visual review

For a selected, consented candidate only, the app may create or open a local preview workspace in a location outside the source folder. The reviewer checks:

- strong, clear commercial concept or credible editorial value;
- composition and distractions;
- focus, motion blur, noise, artefacts, dust/spots, and unwanted text/watermarks;
- exposure, colour, white balance, horizon, and crop;
- whether an edit could improve the image without misrepresenting it;
- recognisable people, private/restricted places, logos/trademarks, and third-party content.

The app records observations and follow-up questions, not legal or marketplace conclusions.

**Output:** a visible record of why an image moves forward, needs an edit, is better suited to editorial review, or should be skipped.

### D. Non-destructive editing and working-copy control

1. If no edit is needed, retain the original as the factual source and proceed to metadata preparation.
2. If RAW development is needed, hand off the selected image to darktable (preferred) or RawTherapee. Configure their database/sidecar location before use.
3. If pixel retouching is warranted, export a TIFF or high-quality working copy and use GIMP on that copy only.
4. Save final exports into a named, versioned workspace such as `working_copies/<candidate-id>/exports/`, never in the original-photo folder.
5. Return the export path, tool used, edit version, and reviewer note to the Stock Photo Scout draft.

**Quality rule:** commercial edits can improve presentation, but editorial work must preserve the camera-recorded reality. The final choice remains the photographer’s.

### E. Metadata, keywords, and descriptive quality

1. Start with a photographer-written title/description that accurately states visible content and concept.
2. Build a concise keyword list from observable facts plus genuinely relevant concepts—no unrelated high-traffic keywords.
3. Run the existing offline spelling prompts; accepted spellings remain local and explicit.
4. Track a human-selected category and proposed commercial/editorial route.
5. Allow external metadata exchange only by explicit action, first as a previewable XMP sidecar or a field-mapping export. Never silently embed metadata in a source image.

**Output:** approved metadata with its author/reviewer, outstanding prompts, and the exact exported image it refers to.

### F. Dreamstime preflight packet

For each selected final export, Stock Photo Scout creates a local, readable packet containing:

- source and working-copy provenance;
- dimensions, pixel count, format and colour-space facts where detected;
- title, description, keywords, category and intended licence route;
- human visual-review notes and remaining technical prompts;
- rights observations and release-evidence status;
- warning if the candidate has not been rechecked after a material edit;
- links to the current Dreamstime rules used for the check and the date they were verified;
- a final checklist for the photographer to complete in the current Dreamstime upload UI.

The packet may say **“ready for your manual review”**. It must never say **“Dreamstime-compliant”** or **“will be accepted.”**

### G. Manual upload and learning loop

1. Stephen selects the final export and uploads it through Dreamstime’s current browser/FTP route.
2. Stephen completes and verifies the fields and selects the licence/submission route in the portal.
3. The app records only a local, user-entered outcome: submitted date, pending, accepted, rejected, or withdrawn; no account automation or credential storage.
4. If rejected, record the exact Dreamstime reason and associate it with the image and review notes.
5. Build a personal, local “rejection learning” library so future review prompts reflect real feedback without pretending it is a universal rule.

## 4. How we use each tool to improve quality

| Need | Tool and method | Human checkpoint |
| --- | --- | --- |
| Find candidates | Stock Photo Scout inventory, metadata facts, duplicate groups | Confirm that a folder is in scope |
| Judge visual merit | Local preview workspace + human checklist | Move image into/out of shortlist |
| RAW correction | darktable, or RawTherapee alternative, using non-destructive edit state | Approve edit and export settings |
| Pixel retouching | GIMP on a working copy only | Verify the final image at 100% and preserve editorial integrity |
| Manage a very large library | Optional digiKam catalogue/rating workflow | Approve any metadata-writing mode before enabling it |
| Sidecar metadata | ExifTool invoked only for a single previewed destination | Review field diff and output path |
| Dreamstime upload | Current Dreamstime web/FTP interface | Photographer handles login, upload, and submit |

## 5. Dreamstime-aware, but not Dreamstime-hard-coded

The current public material describes JPG RGB/sRGB uploads in the 3–70 MP range, reviews of quality/artifacts, title/description/category/keyword preparation, commercial and editorial paths, and release handling for recognisable people in commercial content. These are useful preflight reminders, not permanent rules.

Implementation requirements:

- Store any marketplace rule as a source link, verification date, and text/version note.
- Show when a rule has become stale and ask to refresh it before a submission batch.
- Separate **detected facts** (for example “JPEG, 24 MP”) from **user observations** (for example “logo visible”) and **marketplace claims** (which stay unmade).
- Present editorial warnings whenever a proposed edit may affect the truthfulness of an editorial image.
- Keep all uploads manual until there is current, documented permission and a separate user approval to integrate.

## 6. Product development sequence

### Release 0.05 — Candidate workspace and review ledger

- Add explicit selected-folder consent and a separate preview/workspace directory.
- Add candidate status, rating, reviewer notes, skip reason, and edit-needed fields.
- Display technical flags and exact duplicates alongside a manual visual checklist.
- Keep the dashboard local-only and do not make pixel reads implicit.

**Success:** Stephen can turn a selected folder into a traceable shortlist without changing photos.

### Release 0.06 — Editor handoff and versioned exports

- Add a working-copy record with source-relative path, destination, tool, edit state, and export version.
- Generate darktable/RawTherapee handoff instructions and a safe output-directory convention.
- Add a final-export recheck and a side-by-side preflight view of source versus export facts.

**Success:** an edited candidate has a clear lineage and no original is overwritten.

### Release 0.07 — Metadata and local submission packet

- Expand drafts to title, description, category, route and optional release/reference notes.
- Add reviewed XMP/CSV/JSON export as a separate, previewable action.
- Create a printable/shareable local preflight packet with unresolved prompts prominently shown.

**Success:** Stephen can manually submit one well-documented final export without retyping from scattered notes.

### Release 0.08 — Feedback and personalised quality learning

- Add local submission outcomes and structured rejection reasons.
- Surface personal trends (for example repeated technical issues) without turning them into universal or legal rules.
- Add a local batch-planning screen that selects only individually approved candidates.

**Success:** actual Dreamstime feedback improves the next review cycle.

### Later, only with separate approval

- Local visual-analysis models, after a privacy/performance design review.
- Cloud captioning or keyword suggestions, after provider, cost, and data-sharing approval.
- digiKam or ExifTool write integrations, after a detailed output/diff/rollback design.
- Dreamstime account or upload integration, after current permissions and allowed automation are verified.

## 7. Non-negotiable safeguards

1. Originals are never renamed, moved, overwritten, deleted, embedded with metadata, or uploaded by Stock Photo Scout.
2. Every action that reads pixels, creates previews, generates exports, writes sidecars, uses an external service, or accesses an account is opt-in and clearly named.
3. Derived data stays outside source folders and is excluded from Git by default.
4. A consented local action is not blanket consent for cloud analysis or upload.
5. Human review is decisive for image quality, descriptions, keywords, edit approval, editorial/commercial route, rights questions, and submission.
6. Dreamstime acceptance, legal clearance, and revenue potential are never represented as guaranteed.

## 8. First implementation decision

The best next build is **Release 0.05: the local candidate workspace and review ledger**. It creates the foundation that every later editor, metadata, and Dreamstime step needs, while keeping the current no-upload and no-original-change guarantees intact.

Before starting that build, decide:

1. Which single photo folder should be the first approved test folder?
2. Where should derived previews/workspaces live: project-local Dropbox storage or a separate local-only directory?
3. Is darktable the chosen first editor handoff, or do you prefer RawTherapee/GIMP/an existing editor?
