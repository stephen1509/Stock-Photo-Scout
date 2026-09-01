# Architecture

Checkpoint 0.01 is a Python standard-library core:

```text
User-selected photo folder
        |
        v
read-only inventory (src/stock_photo_scout/scanner.py)
        |
        v
CandidateImage records returned to the caller
```

The inventory reads directory entries and file statistics only. It neither opens image contents nor writes anywhere.

Metadata extraction, local catalog, review UI, and marketplace-preflight rules are deliberately deferred, and must remain separate from immutable original-photo sources.

## Checkpoint 0.02 slice in progress

```text
User-selected photo folder
        |
        v
read-only inventory
        |
        v
bounded, read-only header extraction
        |
        v
deterministic in-memory LocalCatalog
        |
        v
JSON text returned to the caller
        |
        v
optional explicit save outside the photo source tree
```

The extractor reads PNG and JPEG headers plus selected TIFF image-file-directory entries for pixel dimensions. It does not decode pixels, follow symlinks, or infer missing facts. HEIC, HEIF, and WebP currently receive an explicit `unsupported` metadata status rather than using an unverified dependency.

JPEG APP1 EXIF and standalone TIFF metadata use a standard-library parser with strict entry-count, byte-read, value-size, and offset limits. The catalog schema is version 2 and includes only orientation, the original capture-time text, camera make/model, and lens model. GPS, owner names, serial identifiers, comments, thumbnails, and arbitrary EXIF fields are not collected. Capture-time text remains unnormalized because EXIF may not provide a timezone.

Catalog entries contain relative paths only; the selected source root is retained only for in-process safety checks and is excluded from object representations and serialized JSON. Persistence is opt-in: `save_catalog_json` requires a `.json` destination, rejects destinations inside the selected source tree, creates missing parent folders, and refuses to overwrite an existing file. The recommended project-local destination is `local_catalogs/`, which Git ignores.

Malformed or out-of-bounds EXIF receives an explicit status without discarding independently valid JPEG dimensions.

## Checkpoint 0.03 review signals

```text
LocalCatalog
   |                 \
   v                  v
metadata-only       explicit full-file SHA-256 read
technical prompts       |
   |                     v
   v                 exact-content groups
human review             |
                         v
                     human review
```

Technical prompts use only cataloged facts. A pixel-count threshold is optional and caller-configured; it is never a marketplace requirement. Exact-content grouping is separate because it reads bytes from each selected source file, uses bounded-memory chunks, and identifies SHA-256 content matches only—not visual similarity or quality.

## Checkpoint 0.04 slice in progress

```text
CandidateDraft (local, editable)
        |
        v
user-supplied rights observations + title/keywords
        |
        v
explainable manual-follow-up prompts
        |
        v
optional JSON save outside the source tree
```

Drafts record user input rather than infer it from images. They never declare that a release is required, that rights are cleared, or that a marketplace will accept a file.

Every word in titles, each keyword, and notes is checked against a small, extensible offline vocabulary. Unrecognized terms always prompt the user, with close alternatives when available; wording is never changed automatically. Confirmed proper names and intentional spellings can be added as accepted terms.

Confirmed spelling terms can optionally be kept in an explicit, local JSON dictionary. It is never populated automatically, contains no photo paths or metadata, and uses the same deliberate save/update pattern as drafts.
