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
