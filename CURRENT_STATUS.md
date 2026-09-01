# Current Status

## Checkpoint 0.01 — Local foundation (complete)

- Project authority and safe operating rules recorded.
- Product, architecture, Dreamstime-rule, and test-plan documents established.
- Read-only image-file inventory implemented using only the Python standard library.
- Focused unit coverage verifies supported file recognition, nested discovery, non-image exclusion, and no source-file changes.

## Checkpoint 0.02 — Local catalog and metadata (complete)

Completed:

- Deterministic, in-memory catalog records with relative paths and a versioned schema.
- Read-only, bounded PNG and JPEG header parsing for pixel dimensions.
- Read-only TIFF dimension parsing and bounded JPEG/TIFF EXIF extraction.
- Catalog schema version 2 records orientation, original capture-time text, camera make/model, and lens model.
- Privacy-sensitive GPS, owner/serial identifiers, comments, thumbnails, and arbitrary EXIF fields are not collected.
- Explicit `unsupported`, `invalid`, and `error` outcomes instead of guessed metadata.
- Stable JSON serialization that does not embed the selected source-root path or write files implicitly.
- Explicit JSON persistence that refuses destinations inside the source tree and refuses overwrites.
- Project-local `local_catalogs/` output is excluded from Git.
- Focused tests proving dimension extraction, deterministic catalog ordering, and no source-file changes.
- An approved representative photo folder completed a read-only local trial; the saved catalog matched a fresh inventory and did not embed the source-root path.

Focused local verification has passed. A GitHub checkpoint remains a deliberate follow-up, not an automatic sync.

## Checkpoint 0.03 — Review signals (complete)

Completed:

- Metadata-only technical review prompts with no default size threshold.
- Explicit caller-configured pixel-count prompts that never claim marketplace compliance.
- SHA-256 exact-content grouping, deliberately separate from metadata-only review because it reads source bytes.
- Hashing issues are reported per relative path; no source file is changed.
- An approved representative photo folder completed a read-only duplicate trial: one exact-content group was found, with no hashing issues.
- A metadata-only review completed without a default size threshold; orientation-display prompts were reported separately from quality judgments.
- A fresh inventory matched the saved catalog after the review and duplicate pass.

Focused local verification has passed. A GitHub checkpoint remains a deliberate follow-up, not an automatic sync.

## Checkpoint 0.04 — Stock readiness (in progress)

Implemented with synthetic fixtures only:

- Editable local title, keyword, note, and user-supplied rights-observation drafts.
- Explainable prompts for missing drafts, duplicate keywords, unknown observations, and recorded follow-up context.
- Offline spelling prompts review every word in titles, keywords, and notes. They ask about unrecognized terms and suggest close local-vocabulary matches, but never silently replace text.
- Explicit local dictionaries can retain user-confirmed spellings (such as proper names) without adding them automatically or storing photo data.
- A project-local command-line review flow can display draft prompts and explicitly save a user-confirmed spelling for later reviews; it requires no Python package installation and does not open the source image.
- Project-local commands can create and explicitly update title, keyword, note, and structured rights-observation drafts outside the selected source folder.
- A localhost-only browser dashboard can show and update local drafts, prompts, and confirmed spellings without opening source images.
- No legal, release, or marketplace-acceptance determination.
- Explicit non-overwriting JSON persistence outside source folders; `local_drafts/` is excluded from Git.

One user-selected candidate now has a local draft and recorded rights observations. Its remaining prompts require manual review; no rights or marketplace conclusion has been made.

Not yet started: commercial-readiness checks; quality scoring beyond technical prompts; title/keyword/release workflows; Dreamstime connection or submission; paid services, cloud processing, CI, and deployment.
