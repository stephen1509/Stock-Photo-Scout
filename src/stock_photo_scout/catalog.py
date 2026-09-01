"""Deterministic, local-only catalog records for inventoried images."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path

from .exif import ExifMetadata
from .metadata import MetadataStatus, extract_technical_metadata
from .scanner import inventory_images


CATALOG_SCHEMA_VERSION = 2


@dataclass(frozen=True)
class CatalogEntry:
    """A relative-path catalog entry that does not embed its source root."""

    relative_path: str
    filename: str
    suffix: str
    size_bytes: int
    modified_time_ns: int
    detected_format: str | None
    width_pixels: int | None
    height_pixels: int | None
    metadata_status: MetadataStatus
    metadata_message: str | None
    exif: ExifMetadata


@dataclass(frozen=True)
class LocalCatalog:
    """A deterministic snapshot suitable for local serialization."""

    schema_version: int
    entries: tuple[CatalogEntry, ...]
    source_root: Path = field(repr=False, compare=False)


def build_catalog(source_folder: str | Path) -> LocalCatalog:
    """Build an in-memory catalog from one explicitly selected source folder."""

    source_root = Path(source_folder).expanduser().resolve(strict=True)
    entries: list[CatalogEntry] = []
    for candidate in inventory_images(source_root):
        metadata = extract_technical_metadata(candidate.path)
        entries.append(
            CatalogEntry(
                relative_path=candidate.relative_path.as_posix(),
                filename=candidate.path.name,
                suffix=candidate.path.suffix.lower(),
                size_bytes=candidate.size_bytes,
                modified_time_ns=candidate.modified_time_ns,
                detected_format=metadata.detected_format,
                width_pixels=metadata.width_pixels,
                height_pixels=metadata.height_pixels,
                metadata_status=metadata.status,
                metadata_message=metadata.message,
                exif=metadata.exif,
            )
        )
    return LocalCatalog(CATALOG_SCHEMA_VERSION, tuple(entries), source_root)


def catalog_to_json(catalog: LocalCatalog) -> str:
    """Return stable JSON without writing to the source folder or project."""

    payload = {
        "schema_version": catalog.schema_version,
        "entries": [asdict(entry) for entry in catalog.entries],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def save_catalog_json(catalog: LocalCatalog, destination: str | Path) -> Path:
    """Explicitly save a catalog outside its source tree without overwriting."""

    destination_path = Path(destination).expanduser().resolve(strict=False)
    if destination_path.suffix.lower() != ".json":
        raise ValueError(f"Catalog destination must use a .json suffix: {destination_path}")
    if destination_path.is_relative_to(catalog.source_root):
        raise ValueError(f"Refusing to write a catalog inside its source folder: {destination_path}")

    payload = catalog_to_json(catalog)
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    with destination_path.open("x", encoding="utf-8", newline="\n") as output:
        output.write(payload)
    return destination_path
