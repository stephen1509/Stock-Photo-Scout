"""Read-only candidate image inventory."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


SUPPORTED_IMAGE_SUFFIXES = frozenset({".heic", ".heif", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"})


@dataclass(frozen=True)
class CandidateImage:
    """A minimal, non-invasive record for an image candidate."""

    path: Path
    relative_path: Path
    size_bytes: int
    modified_time_ns: int


def inventory_images(source_folder: str | Path) -> list[CandidateImage]:
    """Return supported image files below *source_folder* without altering it."""

    source = Path(source_folder).expanduser().resolve(strict=True)
    if not source.is_dir():
        raise NotADirectoryError(f"Source is not a folder: {source}")

    candidates: list[CandidateImage] = []
    for path in source.rglob("*"):
        if path.is_symlink() or not path.is_file() or path.suffix.lower() not in SUPPORTED_IMAGE_SUFFIXES:
            continue
        stat = path.stat()
        candidates.append(CandidateImage(path, path.relative_to(source), stat.st_size, stat.st_mtime_ns))

    return sorted(candidates, key=lambda candidate: candidate.relative_path.as_posix().casefold())
