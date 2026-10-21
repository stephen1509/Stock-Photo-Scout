"""Privacy-preserving source-to-export provenance for local stock-photo preparation."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib, json, os
from pathlib import Path, PureWindowsPath

SCHEMA_VERSION = 1

@dataclass(frozen=True)
class FileFingerprint:
    relative_path: str
    sha256: str
    size_bytes: int
    mtime_ns: int

@dataclass(frozen=True)
class ProvenanceRecord:
    source: FileFingerprint
    export: FileFingerprint
    editor_target: str
    export_version: int
    notes: str = ""


def _relative(value: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError("relative_path must be a non-empty string")
    native, windows = Path(value), PureWindowsPath(value)
    if native.is_absolute() or native.drive or windows.is_absolute() or windows.drive or ".." in native.parts or ".." in windows.parts:
        raise ValueError("relative_path must be safe and relative")
    return native


def _external_roots(source_root: Path, export_root: Path) -> tuple[Path, Path]:
    source = Path(source_root).expanduser().resolve(strict=False)
    export = Path(export_root).expanduser().resolve(strict=False)
    if source == export or source.is_relative_to(export) or export.is_relative_to(source):
        raise ValueError("Source and export roots must be separate and non-overlapping.")
    return source, export


def fingerprint_file(root: Path, relative_path: str, *, consent: bool) -> FileFingerprint:
    if consent is not True:
        raise PermissionError("Explicit byte-read consent is required for provenance fingerprinting.")
    rel = _relative(relative_path)
    root = Path(root).expanduser().resolve(strict=False)
    unresolved = root / rel
    if unresolved.is_symlink():
        raise ValueError("Symlink files are not accepted for provenance fingerprinting.")
    target = unresolved.resolve(strict=True)
    if not target.is_relative_to(root) or not target.is_file():
        raise ValueError("Fingerprint target must be a regular file inside its declared root.")
    digest = hashlib.sha256()
    with target.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
        stat = os.fstat(handle.fileno())
    return FileFingerprint(rel.as_posix(), digest.hexdigest(), stat.st_size, stat.st_mtime_ns)


def create_provenance(source_root: Path, source_relative_path: str, export_root: Path, export_relative_path: str, *, editor_target: str, export_version: int, notes: str = "", consent: bool) -> ProvenanceRecord:
    source_root, export_root = _external_roots(source_root, export_root)
    if not isinstance(editor_target, str) or not editor_target.strip():
        raise ValueError("editor_target is required")
    if not isinstance(export_version, int) or isinstance(export_version, bool) or export_version < 1:
        raise ValueError("export_version must be a positive integer")
    if not isinstance(notes, str):
        raise ValueError("notes must be a string")
    return ProvenanceRecord(
        fingerprint_file(source_root, source_relative_path, consent=consent),
        fingerprint_file(export_root, export_relative_path, consent=consent),
        editor_target.strip(), export_version, notes,
    )


def _valid_fingerprint(value) -> FileFingerprint:
    if not isinstance(value, dict) or set(value) != {"relative_path", "sha256", "size_bytes", "mtime_ns"}:
        raise ValueError("Malformed provenance fingerprint")
    _relative(value["relative_path"])
    sha = value["sha256"]
    if not isinstance(sha, str) or len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha.lower()):
        raise ValueError("Malformed provenance SHA-256")
    for key in ("size_bytes", "mtime_ns"):
        if not isinstance(value[key], int) or isinstance(value[key], bool) or value[key] < 0:
            raise ValueError(f"Malformed provenance {key}")
    return FileFingerprint(value["relative_path"], sha.lower(), value["size_bytes"], value["mtime_ns"])


def provenance_to_json(record: ProvenanceRecord) -> str:
    if not isinstance(record, ProvenanceRecord):
        raise ValueError("record must be ProvenanceRecord")
    _valid_fingerprint(asdict(record.source)); _valid_fingerprint(asdict(record.export))
    if not isinstance(record.editor_target, str) or not record.editor_target.strip(): raise ValueError("editor_target is required")
    if not isinstance(record.export_version, int) or isinstance(record.export_version, bool) or record.export_version < 1: raise ValueError("export_version must be positive")
    if not isinstance(record.notes, str): raise ValueError("notes must be a string")
    return json.dumps({"schema_version": SCHEMA_VERSION, "record": asdict(record)}, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"


def provenance_from_json(text: str) -> ProvenanceRecord:
    value = json.loads(text)
    if not isinstance(value, dict) or set(value) != {"schema_version", "record"} or value["schema_version"] != SCHEMA_VERSION or not isinstance(value["record"], dict):
        raise ValueError("Unsupported or malformed provenance document")
    raw = value["record"]
    if set(raw) != {"source", "export", "editor_target", "export_version", "notes"}: raise ValueError("Malformed provenance record")
    source, export = _valid_fingerprint(raw["source"]), _valid_fingerprint(raw["export"])
    if not isinstance(raw["editor_target"], str) or not raw["editor_target"].strip(): raise ValueError("Malformed editor_target")
    if not isinstance(raw["export_version"], int) or isinstance(raw["export_version"], bool) or raw["export_version"] < 1: raise ValueError("Malformed export_version")
    if not isinstance(raw["notes"], str): raise ValueError("Malformed notes")
    return ProvenanceRecord(source, export, raw["editor_target"], raw["export_version"], raw["notes"])


def save_provenance(record: ProvenanceRecord, destination: Path, source_root: Path, *, overwrite: bool = False) -> None:
    destination = Path(destination).expanduser().resolve(strict=False)
    source_root = Path(source_root).expanduser().resolve(strict=False)
    if destination.is_relative_to(source_root): raise ValueError("Provenance state must remain outside the source-photo tree.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    data = provenance_to_json(record)
    if destination.exists() and not overwrite: raise FileExistsError(destination)
    if destination.exists() and (destination.is_symlink() or not destination.is_file()): raise ValueError("Refusing to overwrite non-regular provenance state.")
    tmp = destination.with_name(destination.name + ".tmp")
    try:
        with tmp.open("x", encoding="utf-8") as handle:
            handle.write(data); handle.flush(); os.fsync(handle.fileno())
        os.replace(tmp, destination)
    finally:
        if tmp.exists(): tmp.unlink()


def verify_provenance(record: ProvenanceRecord, source_root: Path, export_root: Path, *, consent: bool) -> tuple[bool, tuple[str, ...]]:
    source_root, export_root = _external_roots(source_root, export_root)
    blockers = []
    current_source = fingerprint_file(source_root, record.source.relative_path, consent=consent)
    current_export = fingerprint_file(export_root, record.export.relative_path, consent=consent)
    if current_source.sha256 != record.source.sha256 or current_source.size_bytes != record.source.size_bytes:
        blockers.append("Source bytes changed after provenance was recorded.")
    if current_export.sha256 != record.export.sha256 or current_export.size_bytes != record.export.size_bytes:
        blockers.append("Export bytes changed after provenance was recorded; final QC must be repeated.")
    return not blockers, tuple(blockers)
