# Test Plan

Run from the project root:

```powershell
python -m unittest discover -s tests -v
```

Do not report a new passing-test count until this complete expanded suite has actually run in an executable checkout. The historical 79/79 count belongs only to the older qualified baseline.

## 0.01–0.04 historical foundation
Inventory tests prove supported-suffix recognition, nested discovery, stable ordering and source immutability. Metadata/catalog tests use synthetic PNG/JPEG/TIFF fixtures to verify bounded parsing, privacy-conscious EXIF selection, deterministic relative paths, safe external output and no source mutation. Technical/duplicate tests cover explainable opt-in observations, deterministic SHA-256 groups and bounded-memory processing. Draft/spelling/dictionary/CLI/dashboard tests cover deterministic external local state, explicit human edits and source-boundary protection.

## 0.05 candidate/preparation foundation
Verify candidate workspace states, explicit preview byte-read consent, preview copies outside the source tree, SHA-256 preview integrity/staleness, path/traversal/symlink refusal, preparation/editor handoff, manual preflight, and legacy-state compatibility. Direct `submission-ready` mutation must remain prohibited.

## 0.06 Reliability & QC
Verify:
- fail-closed preview integrity (`None`, false and mismatch cannot become complete);
- multidimensional candidate/route review;
- route-sensitive rights review;
- provenance fingerprints for exact source/export bytes;
- changed source or export invalidates provenance/QC;
- literal byte-read consent for provenance verification;
- exact-export 100% human QC and known defect codes;
- persisted analysis rejects malformed/non-finite/out-of-range values;
- Windows drive, UNC, traversal and symlink attacks fail closed;
- external persistence uses safe atomic replacement;
- localhost Host/Origin restrictions and mutation locking;
- legacy ready records remain readable but non-authoritative.

## 0.07 Review Intelligence
Verify:
- unreviewed/skip/hold cannot shortlist;
- Stage-2 inspect requires explicit focus and composition review;
- `composition_state=unknown` blocks even with complete usefulness data;
- grouped candidates require an explicit preferred member;
- usefulness unknowns and non-literal confirmations fail closed;
- review directory cannot be inside the source tree;
- main dashboard cannot set `shortlist` until ReviewService says `can_shortlist is True`;
- legacy shortlist label alone is not authoritative;
- complete review can become an authoritative shortlist only after the workspace transition;
- review dashboard exposes/persists all review/usefulness fields without unsafe `innerHTML`;
- localhost review server rejects non-local Host/Origin, traversal and oversized requests and never serves originals;
- combined `*.review-packet.json` persistence stores review+usefulness atomically;
- packet destination/source-tree/symlink/path-mismatch attacks fail closed;
- legacy split `.review.json` + `.usefulness.json` remains readable and migrates on next save.

## Preparation regression qualification
Verify Dreamstime category pairs round-trip without shifting route/editor/export/notes fields. Named construction must be retained. Unsupported preparation fields, blank/duplicate values and unsafe paths must produce explicit errors/prompts rather than silent coercion.

## 0.08 Stock Intelligence / marketplace-neutral engine
Verify:
- marketplace rule profiles require marketplace name, authoritative HTTPS source, human verification date and positive review horizon;
- future/stale/malformed profiles fail closed;
- persisted rule provenance round-trips through strict JSON and retains stale assessment after reload;
- marketplace candidate adapter requires concrete route, factual metadata presence, rights review and exact-export QC;
- marketplace preflight requires both core readiness and a current sourced rule profile;
- stale marketplace rules cannot be overridden by otherwise-ready candidate state;
- portfolio intelligence emits explainable observations only, never acceptance/sales scores;
- metadata assistant normalizes/deduplicates only human-entered terms and never invents missing facts/keywords;
- marketplace outcome ledger accepts only explicit factual outcomes and safe external paths;
- outcome analysis keeps pending separate and labels rejection-frequency observations as historical evidence, not predictions.

## Synthetic destructive qualification after unit tests
After the full unit suite passes, deliberately attempt:
1. source-photo mutation through every preview/analysis/review/preparation/provenance path;
2. writes through `..`, absolute paths, Windows drives, UNC paths, file symlinks and symlinked parent directories;
3. interrupted/partial external writes and stale temp-file conditions;
4. malformed JSON, unsupported fields, wrong candidate paths and stale schema versions;
5. concurrent candidate/review mutations;
6. direct shortlist and submission-ready bypass attempts;
7. changed export after final QC and changed source after provenance recording;
8. stale marketplace requirements after otherwise-complete readiness;
9. hostile filenames/metadata rendered in localhost dashboards;
10. legacy records from pre-0.07 state.

Expected result: fail closed, originals unchanged, no marketplace/network mutation, and no silent promotion to authoritative shortlist/readiness.

## Real-photo product qualification
Only after code qualification, use a small set of photographs explicitly selected by the user. Pixel/byte reads require the established explicit-consent pathway. Exercise the complete local chain: candidate → human review → authoritative shortlist → factual preparation/route/rights → separate working export → provenance → exact-export QC → current sourced marketplace rules → human preflight. No marketplace submission is part of this test.

All automated tests use non-sensitive synthetic fixtures. Real photos, previews, analysis, review packets, preparation state and marketplace credentials remain outside Git.
