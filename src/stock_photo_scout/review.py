"""Explainable, local-only review signals for cataloged image candidates."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Literal

from .catalog import CatalogEntry, LocalCatalog


ReviewSeverity = Literal["info", "attention"]


@dataclass(frozen=True)
class ReviewPolicy:
    """Opt-in technical thresholds that never represent marketplace rules."""

    minimum_pixel_count: int | None = None

    def __post_init__(self) -> None:
        if self.minimum_pixel_count is not None and self.minimum_pixel_count < 1:
            raise ValueError("minimum_pixel_count must be positive when configured.")


@dataclass(frozen=True)
class TechnicalReviewFlag:
    """A factual prompt for human review, not a pass/fail assessment."""

    code: str
    severity: ReviewSeverity
    explanation: str


@dataclass(frozen=True)
class TechnicalReview:
    relative_path: str
    pixel_count: int | None
    flags: tuple[TechnicalReviewFlag, ...]


@dataclass(frozen=True)
class TechnicalReviewReport:
    reviews: tuple[TechnicalReview, ...]


@dataclass(frozen=True)
class ExactDuplicateGroup:
    """A SHA-256 content match group, ordered by relative path."""

    sha256_digest: str
    size_bytes: int
    relative_paths: tuple[str, ...]


@dataclass(frozen=True)
class HashingIssue:
    relative_path: str
    message: str


@dataclass(frozen=True)
class ExactDuplicateReport:
    groups: tuple[ExactDuplicateGroup, ...]
    issues: tuple[HashingIssue, ...]


def review_technical_metadata(catalog: LocalCatalog, policy: ReviewPolicy | None = None) -> TechnicalReviewReport:
    """Create non-destructive review prompts from already cataloged metadata."""

    active_policy = policy or ReviewPolicy()
    return TechnicalReviewReport(
        tuple(_review_entry(entry, active_policy) for entry in catalog.entries)
    )


def find_exact_duplicates(catalog: LocalCatalog, *, chunk_size: int = 1024 * 1024) -> ExactDuplicateReport:
    """Hash source files locally to find SHA-256 content matches.

    This intentionally performs a full read of each cataloged source file, so it
    is separate from metadata-only review and must be called explicitly.
    """

    if chunk_size < 1:
        raise ValueError("chunk_size must be positive.")

    source_root = catalog.source_root.resolve(strict=True)
    paths_by_digest: dict[tuple[str, int], list[str]] = {}
    issues: list[HashingIssue] = []
    for entry in catalog.entries:
        try:
            content_digest = _hash_catalog_entry(source_root, entry, chunk_size)
        except (OSError, ValueError) as error:
            issues.append(HashingIssue(entry.relative_path, f"File could not be hashed ({type(error).__name__})."))
            continue
        paths_by_digest.setdefault((content_digest, entry.size_bytes), []).append(entry.relative_path)

    groups = [
        ExactDuplicateGroup(digest, size_bytes, tuple(sorted(paths, key=str.casefold)))
        for (digest, size_bytes), paths in paths_by_digest.items()
        if len(paths) > 1
    ]
    return ExactDuplicateReport(
        groups=tuple(sorted(groups, key=lambda group: tuple(path.casefold() for path in group.relative_paths))),
        issues=tuple(issues),
    )


def _review_entry(entry: CatalogEntry, policy: ReviewPolicy) -> TechnicalReview:
    flags: list[TechnicalReviewFlag] = []
    pixel_count = _pixel_count(entry)
    if entry.metadata_status != "extracted":
        flags.append(
            TechnicalReviewFlag(
                "technical_metadata_unavailable",
                "attention",
                "The bounded header reader did not yield usable technical metadata; inspect this file manually.",
            )
        )
    if pixel_count is None:
        flags.append(
            TechnicalReviewFlag(
                "dimensions_missing",
                "attention",
                "Pixel dimensions are unavailable, so technical size cannot be reviewed automatically.",
            )
        )
    elif policy.minimum_pixel_count is not None and pixel_count < policy.minimum_pixel_count:
        flags.append(
            TechnicalReviewFlag(
                "below_configured_pixel_threshold",
                "attention",
                f"{pixel_count} pixels is below the caller-configured review threshold of {policy.minimum_pixel_count} pixels.",
            )
        )
    if entry.exif.orientation not in {None, 1}:
        flags.append(
            TechnicalReviewFlag(
                "orientation_transform_present",
                "info",
                f"EXIF orientation {entry.exif.orientation} indicates that a viewer may need a display transform.",
            )
        )
    return TechnicalReview(entry.relative_path, pixel_count, tuple(flags))


def _pixel_count(entry: CatalogEntry) -> int | None:
    if entry.width_pixels is None or entry.height_pixels is None:
        return None
    return entry.width_pixels * entry.height_pixels


def _hash_catalog_entry(source_root: Path, entry: CatalogEntry, chunk_size: int) -> str:
    candidate = source_root / Path(entry.relative_path)
    if candidate.is_symlink():
        raise ValueError("Refusing to hash a symlink.")
    resolved = candidate.resolve(strict=True)
    if not resolved.is_relative_to(source_root) or not resolved.is_file():
        raise ValueError("Catalog entry is not a regular file inside the source root.")
    current_stat = resolved.stat()
    if current_stat.st_size != entry.size_bytes or current_stat.st_mtime_ns != entry.modified_time_ns:
        raise ValueError("Catalog entry no longer matches the current source file.")

    digest = sha256()
    with resolved.open("rb") as source_file:
        while chunk := source_file.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()
