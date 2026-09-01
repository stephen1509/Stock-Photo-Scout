# Test Plan

Run from the project root:

```powershell
python -m unittest discover -s tests -v
```

Checkpoint 0.01 tests prove that inventory recognizes supported suffixes case-insensitively, finds nested images, excludes unrelated files, returns stable ordering, and leaves source files unchanged.

Checkpoint 0.02 tests use synthetic PNG, JPEG, TIFF, and unsupported-format fixtures. They verify bounded header and EXIF extraction in both TIFF byte orders, privacy-conscious field selection, safe handling of out-of-bounds EXIF, explicit non-success outcomes, deterministic relative-path catalog serialization, safe output outside the source tree, overwrite refusal, and no source-file changes.

Checkpoint 0.03 tests use synthetic source files. They verify explainable technical prompts, opt-in thresholds, deterministic SHA-256 exact-content groups, bounded-memory chunking, invalid-option rejection, and no source-file changes.

Checkpoint 0.04 tests use synthetic local drafts. They verify editable title/keyword/observation data, explainable manual prompts, deterministic JSON round-tripping, source-boundary protection, overwrite refusal, and no source-file changes.

Spelling tests verify that every word in title, keyword, and note text is reviewed; close local-vocabulary alternatives are suggested without changing text; unrecognized terms still prompt for confirmation; and accepted terms suppress unwanted prompts.

Local-dictionary tests verify that only explicitly confirmed terms suppress later prompts, and that local JSON persistence is deterministic and does not overwrite without an explicit update.

Command-line tests verify that drafts can be created and explicitly updated outside their source folder while source-image bytes remain unchanged.

Tests must use non-sensitive fixtures. Real-photo samples remain outside Git.
