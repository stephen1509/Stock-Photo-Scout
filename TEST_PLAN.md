# Test Plan

Run from the project root:

```powershell
python -m unittest discover -s tests -v
```

Checkpoint 0.01 tests prove that inventory recognizes supported suffixes case-insensitively, finds nested images, excludes unrelated files, returns stable ordering, and leaves source files unchanged.

Future tests must use non-sensitive fixtures. Real-photo samples remain outside Git.
