# Stock Photo Scout — Research Brief

**Research date:** 1 September 2026 (Pacific/Auckland)
**Purpose:** choose the next safe, practical development slice for a Windows, local-first photo-preparation assistant.
**Scope:** research only. No account access, installation, image upload, pixel analysis, or automated submission was performed.

## Recommendation

Keep Stock Photo Scout as the local candidate, metadata, and human-review layer. For the next practical workflow, pair it with **darktable** for non-destructive RAW review and export, plus **ExifTool** only as a later, opt-in sidecar/metadata handoff utility. Keep Dreamstime upload and final submission manual.

This is the lowest-cost and lowest-privacy-risk route: the core workflow stays on the Windows PC and Dropbox-backed project folder; only the photographer deliberately uploads a finished working copy to Dreamstime. Do not add cloud captioning, AI image analysis, account automation, or automatic metadata writes in the next build phase.

## 1. Dreamstime contributor workflow

### Confirmed from Dreamstime’s public material

| Area | Current finding | Practical implication for Stock Photo Scout |
| --- | --- | --- |
| Upload | Dreamstime describes browser upload and FTP upload for contributors. Files are held unfinished while details are completed, then submitted for review. | Prepare a local submission packet, but leave upload and the final submit click to the photographer. |
| Technical baseline | Contributor FAQ states JPG, RGB/sRGB, 3–70 MP, and no noise or artifacts. The upload page may have additional instructions. | A future preflight may check factual properties and present an explicit “verify current requirements” notice; it must not claim acceptance. |
| Metadata | Dreamstime’s upload guidance describes title, description, category, keywords, and license type as per-file fields. Commercial self-keywording is described as English-only. | Store suggestions and human-approved values locally; map fields only after confirming the logged-in upload UI. |
| Commercial vs editorial | Dreamstime distinguishes RF commercial, RF no-keywords, and Editorial paths. Its terms say editorial media may contain logos/identifiable people without a model release, but must not be used commercially; editorial alteration must not distort reality. | Keep the existing observations as prompts, not legal conclusions. Make “commercial or editorial?” a human decision with an evidence checklist. |
| Releases | Dreamstime states a release is needed for recognizable people in commercial media and describes attaching releases at submission. | A future workflow should track whether the photographer has evidence, never infer whether a release is legally required. |
| Keyword help | Dreamstime’s upload article mentions PhotoEye AI/ML keyword insertion. The article is older and its availability/behavior needs confirmation in the logged-in portal. | Do not depend on it or send photos to it without a separate, explicit approval. |

### Important caveats

- The public FAQ is authoritative but parts of it are older. Treat submission-screen details, quotas, supported formats, and any AI feature as **confirm-at-use** facts.
- I found public references to browser and FTP upload, but no public contributor API documentation supporting automated upload or submission. That is **absence of public evidence**, not proof that no private integration exists. Do not automate it without written confirmation from Dreamstime.
- Dreamstime’s terms place rights responsibility on the contributor. The app can surface observations and missing evidence; it should not make legal or marketplace-acceptance decisions.

## 2. Candidate tool comparison

| Tool | Best role | Windows / data path | Cost and maturity | Fit and cautions |
| --- | --- | --- | --- | --- |
| **Stock Photo Scout** | Inventory, technical facts, exact duplicates, local draft/review prompts | Windows; local files and project-local JSON only | Existing project; standard-library implementation | Keep it as the orchestration and audit trail, not an editor or rights engine. |
| **darktable** | RAW/DAM review, ratings/tags, non-destructive adjustments and export | Windows supported; database plus XMP sidecars | Free/open source; mature photo workflow application | Best first editor handoff. It writes XMP sidecars by default, so use copies or a separately approved sidecar location if adjacent files are unacceptable. |
| **RawTherapee** | Focused RAW development and technical adjustment workflows | Windows builds; sidecar processing profiles can be stored beside inputs or centrally | Free/open source; mature RAW processor | Strong alternative if a lighter RAW-development workflow is preferred. Configure central profiles when source folders must remain pristine. |
| **digiKam** | DAM, metadata review and batch metadata operations | Windows supported; local catalog and metadata tools | Free/open source; mature, broad feature set | Consider only if darktable’s DAM is insufficient. Its batch metadata tools can alter metadata, so treat it as a later, carefully scoped tool. |
| **GIMP** | Pixel-level retouching of a working copy | Windows download available; local | Free/open source; mature raster editor | Useful after a human decides an edit is appropriate. Never point it at originals for destructive saves. |
| **ExifTool** | Scriptable metadata inspection or producing XMP sidecars | Windows compatible; local command line | Free/open source; long-standing metadata utility | Good later integration boundary because it can create sidecars in another destination. It is powerful enough to modify originals, so never expose write commands without a deliberate working-copy/sidecar mode. |
| Cloud captioning/keywording | Optional suggestion generation | Sends selected image or metadata to a provider | Variable / often paid | Deferred. Requires separate provider selection, privacy review, cost approval, and explicit per-batch upload consent. |

## 3. Recommended stack and cost

**Start with:** Stock Photo Scout + darktable + manual Dreamstime browser upload.

- **Cost:** no new paid service required; all recommended local tools are free/open source.
- **Why this combination:** it retains the project’s strongest property—original-photo safety—while adding a proven non-destructive editor and a human-controlled submission step.
- **Alternative:** RawTherapee instead of darktable if the priority is focused RAW processing rather than a larger DAM workflow.
- **Later optional addition:** ExifTool for reviewed XMP-sidecar export/import. This should be designed as an explicit, previewable action rather than a background feature.

Do **not** select a cloud AI service until the photographer chooses a provider and accepts its data handling and cost. Dreamstime’s own optional keywording, if still present, should be evaluated only inside the contributor portal and only with an approved test image.

## 4. Privacy and data flow

```text
Original photo folder (read-only)
        |
        | local file facts / explicitly approved pixel reads
        v
Stock Photo Scout local catalog + drafts  ----> Dropbox project storage (synced project data)
        |                                           |
        | human-approved candidate and metadata     | no originals, previews, or credentials in Git
        v                                           v
darktable / RawTherapee sidecars or working copies   GitHub stable code checkpoints
        |
        | explicit export of a selected working copy
        v
Manual Dreamstime browser/FTP upload  ----> Dreamstime
```

| Step | Leaves the device? | Consent gate |
| --- | --- | --- |
| Inventory, catalog, technical review, local drafts | No | User selects the source folder. |
| Exact duplicate hashing or preview/pixel analysis | No, but reads source content | Explicit selected-folder or selected-image permission. |
| darktable/RawTherapee edits | No, but may create sidecars/exports | Choose working-copy or sidecar location first. |
| Dropbox synchronization | Project data syncs under the user’s existing Dropbox configuration | Keep photos, previews, catalogs, drafts, and credentials excluded unless explicitly chosen. |
| GitHub checkpoint | Remote code/docs only | Review staged files; never include private research exports, photos, drafts, or credentials. |
| Dreamstime upload / any cloud AI | Yes | Separate explicit approval for the specific provider and selected files. |

## 5. Phased build plan

### Phase 0.05A — local candidate workspace

1. Add an explicit, opt-in **preview/workspace mode** for one selected folder.
2. Keep originals read-only; thumbnails or previews must live outside the source folder and be excluded from Git.
3. Add clear consent copy before any pixel decoding.

### Phase 0.05B — local visual and technical suggestions

1. Add factual checks first: dimensions, aspect ratio, orientation, duplicate groups, and unreadable/unsupported formats.
2. Evaluate local visual-quality libraries/tools only after a separate design decision. Label all quality and composition outputs as suggestions.
3. Do not turn current Dreamstime limits into hard-coded acceptance claims; retain versioned, source-linked rules.

### Phase 0.05C — metadata and editor handoff

1. Extend drafts with title, description, keyword, category, and commercial/editorial **human-choice** fields.
2. Export a reviewed handoff file or XMP sidecar to a non-source workspace; show an exact diff before writing.
3. Offer darktable or RawTherapee handoff instructions, never an automatic edit.

### Phase 0.05D — Dreamstime preflight packet

1. Build a local checklist showing detected facts, user observations, unresolved prompts, and sources for current requirements.
2. Produce a manual-upload packet: selected export path, approved title/keywords, license choice, and release-evidence reminder.
3. Require the photographer to confirm the current Dreamstime upload UI and make the final submission.

### Phase 0.05E — optional service integrations

Only after a new approval: select any cloud/AI captioning provider, document its data flow/cost, run a small consented test, and review the resulting suggestions. Do not build automated submission until Dreamstime compatibility is confirmed.

## 6. Decisions required before implementation

1. May the app decode pixels and create local previews for a specifically selected photo folder? If yes, where should previews live?
2. Which editor should be the first handoff target: darktable, RawTherapee, GIMP, or an editor already in use?
3. Are adjacent sidecar files acceptable, or must all derived data live in a separate workspace?
4. Should Dropbox sync local drafts/catalogs, or should those remain local-only outside Dropbox?
5. Do you want a no-cost local-first stack only, or should the next research pass compare specific cloud/AI services after approving image-data sharing?
6. When ready, may we inspect the Dreamstime contributor portal manually with your account, without uploading or changing anything, to verify the current UI?

## Sources

Accessed 1 September 2026. Links are retained so requirements can be rechecked before implementation.

1. [Dreamstime contributor FAQ](https://www.dreamstime.com/faqs-detail-2) — technical baseline, upload routes, commercial/editorial paths, releases, review and keyword guidance.
2. [Dreamstime terms and participation guidelines](https://www.dreamstime.com/terms) — editorial alteration and contributor rights responsibilities.
3. [Dreamstime upload and submission guide](https://www.dreamstime.com/blog/how-to-upload-submit-images-dreamstime-31514) — browser workflow, file-detail fields, and historical PhotoEye mention.
4. [Dreamstime sell-stock overview](https://www.dreamstime.com/sell-stock-photos-images) — release and filename guidance; verify in the current portal before use.
5. [darktable: non-destructive editing and sidecars](https://docs.darktable.org/usermanual/4.8/en/darktable_user_manual.pdf) and [export/metadata controls](https://docs.darktable.org/usermanual/4.2/en/module-reference/utility-modules/shared/export/).
6. [RawTherapee preferences and processing-profile storage](https://rawpedia.rawtherapee.com/Color_Management_Tab) and [editor sidecar behavior](https://rawpedia.rawtherapee.com/Editor).
7. [digiKam metadata tools](https://docs.digikam.org/en/batch_queue/metadata_tools.html).
8. [GIMP Windows downloads](https://www.gimp.org/downloads/).
9. [ExifTool metadata sidecars](https://exiftool.org/metafiles.html).
