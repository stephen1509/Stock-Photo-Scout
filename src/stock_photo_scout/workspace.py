"""Safe local candidate workspace for explicitly selected Stock Photo Scout images."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Final

WORKSPACE_SCHEMA_VERSION: Final[int] = 1
SUPPORTED_PREVIEW_SUFFIXES: Final[tuple[str, ...]] = (".jpg", ".jpeg", ".png", ".tif", ".tiff")
CANDIDATE_STATES: Final[tuple[str, ...]] = (
    "skip",
    "maybe",
    "shortlist",
    "edit",
    "metadata-ready",
    "submission-ready",
)


@dataclass(frozen=True)
class CandidateWorkspaceRecord:
    """Local review state for one source-relative candidate."""

    relative_path: str
    state: str = "maybe"
    preview_relative_path: str = ""


def create_preview_copy(
    source_root: str | Path,
    relative_path: str,
    preview_root: str | Path,
    *,
    consent: bool,
) -> Path:
    """Create one non-overwriting byte-for-byte local preview copy outside the source tree."""

    if consent is not True:
        raise PermissionError("Explicit preview consent is required before reading source image bytes.")

    source_root_path = Path(source_root).expanduser().resolve(strict=True)
    preview_root_path = Path(preview_root).expanduser().resolve(strict=False)
    if preview_root_path.is_relative_to(source_root_path):
        raise ValueError("Preview workspace must be outside the selected source-photo folder.")

    relative = _validated_relative_path(relative_path)
    source_path = (source_root_path / relative).resolve(strict=True)
    if not source_path.is_relative_to(source_root_path):
        raise ValueError("Candidate path escapes the selected source-photo folder.")
    if source_path.is_symlink() or not source_path.is_file():
        raise ValueError("Candidate must be a regular non-symlink file.")
    if source_path.suffix.lower() not in SUPPORTED_PREVIEW_SUFFIXES:
        raise ValueError(f"Unsupported preview image type: {source_path.suffix or '(none)'}")

    destination = (preview_root_path / relative).resolve(strict=False)
    if not destination.is_relative_to(preview_root_path):
        raise ValueError("Preview destination escapes the preview workspace.")
    destination.parent.mkdir(parents=True, exist_ok=True)

    with source_path.open("rb") as source, destination.open("xb") as output:
        shutil.copyfileobj(source, output, length=1024 * 1024)
        output.flush()
        os.fsync(output.fileno())
    return destination


def load_workspace(path: str | Path) -> dict[str, CandidateWorkspaceRecord]:
    """Load and validate a local candidate workspace manifest."""

    manifest_path = Path(path)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != WORKSPACE_SCHEMA_VERSION or not isinstance(payload.get("candidates"), list):
        raise ValueError("Workspace JSON does not match the supported schema.")

    records: dict[str, CandidateWorkspaceRecord] = {}
    for item in payload["candidates"]:
        if not isinstance(item, dict):
            raise ValueError("Workspace candidate must be an object.")
        record = CandidateWorkspaceRecord(
            relative_path=str(item.get("relative_path", "")),
            state=str(item.get("state", "")),
            preview_relative_path=str(item.get("preview_relative_path", "")),
        )
        _validate_record(record)
        if record.relative_path in records:
            raise ValueError(f"Duplicate workspace candidate: {record.relative_path}")
        records[record.relative_path] = record
    return records


def save_workspace(
    records: dict[str, CandidateWorkspaceRecord],
    destination: str | Path,
    source_root: str | Path,
    *,
    overwrite: bool = False,
) -> Path:
    """Persist a deterministic workspace manifest outside the source tree."""

    source_root_path = Path(source_root).expanduser().resolve(strict=True)
    destination_path = Path(destination).expanduser().resolve(strict=False)
    if destination_path.is_relative_to(source_root_path):
        raise ValueError("Refusing to write workspace state inside the selected source-photo folder.")
    if destination_path.suffix.lower() != ".json":
        raise ValueError("Workspace manifest must use a .json suffix.")

    for record in records.values():
        _validate_record(record)

    payload = {
        "schema_version": WORKSPACE_SCHEMA_VERSION,
        "candidates": [asdict(records[key]) for key in sorted(records)],
    }
    serialized = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    destination_path.parent.mkdir(parents=True, exist_ok=True)

    if not overwrite:
        with destination_path.open("x", encoding="utf-8", newline="\n") as output:
            output.write(serialized)
        return destination_path

    if destination_path.is_symlink():
        raise ValueError("Refusing to replace a symlink workspace manifest.")
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=destination_path.parent,
            prefix=f".{destination_path.stem}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary.write(serialized)
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, destination_path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    return destination_path


def set_candidate_state(
    records: dict[str, CandidateWorkspaceRecord],
    relative_path: str,
    state: str,
    *,
    preview_relative_path: str | None = None,
) -> dict[str, CandidateWorkspaceRecord]:
    """Return a new workspace mapping with one explicitly selected state change."""

    if state not in CANDIDATE_STATES:
        raise ValueError(f"Unsupported candidate state: {state}")
    normalized = _validated_relative_path(relative_path).as_posix()
    existing = records.get(normalized, CandidateWorkspaceRecord(normalized))
    updated = CandidateWorkspaceRecord(
        relative_path=normalized,
        state=state,
        preview_relative_path=existing.preview_relative_path if preview_relative_path is None else preview_relative_path,
    )
    _validate_record(updated)
    result = dict(records)
    result[normalized] = updated
    return result


def _validated_relative_path(relative_path: str) -> Path:
    candidate = Path(relative_path)
    if not relative_path or candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError("Candidate path must be a non-empty relative path without parent traversal.")
    return candidate


def _validate_record(record: CandidateWorkspaceRecord) -> None:
    _validated_relative_path(record.relative_path)
    if record.state not in CANDIDATE_STATES:
        raise ValueError(f"Unsupported candidate state: {record.state}")
    if record.preview_relative_path:
        _validated_relative_path(record.preview_relative_path)
