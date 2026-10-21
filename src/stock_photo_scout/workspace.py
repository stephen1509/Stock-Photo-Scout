"""Safe local candidate workspace for explicitly selected Stock Photo Scout images."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib, json, os, shutil, tempfile
from pathlib import Path, PureWindowsPath
from typing import Final
WORKSPACE_SCHEMA_VERSION:Final[int]=1
SUPPORTED_PREVIEW_SUFFIXES:Final[tuple[str,...]]=(".jpg",".jpeg",".png",".tif",".tiff")
CANDIDATE_STATES:Final[tuple[str,...]]=("skip","maybe","shortlist","edit","metadata-ready","submission-ready")
DIRECT_MUTABLE_STATES:Final[tuple[str,...]]=("skip","maybe","shortlist","edit","metadata-ready")
@dataclass(frozen=True)
class CandidateWorkspaceRecord:
    relative_path:str; state:str="maybe"; preview_relative_path:str=""
def create_preview_copy(source_root:str|Path,relative_path:str,preview_root:str|Path,*,consent:bool)->Path:
    if consent is not True: raise PermissionError("Explicit preview consent is required before reading source image bytes.")
    source_root_path=Path(source_root).expanduser().resolve(strict=True); preview_root_path=Path(preview_root).expanduser().resolve(strict=False)
    if preview_root_path.is_relative_to(source_root_path): raise ValueError("Preview workspace must be outside the selected source-photo folder.")
    relative=_validated_relative_path(relative_path); unresolved=source_root_path/relative
    if unresolved.is_symlink(): raise ValueError("Candidate must be a regular non-symlink file.")
    source_path=unresolved.resolve(strict=True)
    if not source_path.is_relative_to(source_root_path) or not source_path.is_file(): raise ValueError("Candidate must stay inside the selected source-photo folder and be a regular file.")
    if source_path.suffix.lower() not in SUPPORTED_PREVIEW_SUFFIXES: raise ValueError(f"Unsupported preview image type: {source_path.suffix or '(none)'}")
    destination=(preview_root_path/relative).resolve(strict=False)
    if not destination.is_relative_to(preview_root_path): raise ValueError("Preview destination escapes the preview workspace.")
    destination.parent.mkdir(parents=True,exist_ok=True); created=False
    try:
        with source_path.open("rb") as source,destination.open("xb") as output:
            created=True; shutil.copyfileobj(source,output,length=1024*1024); output.flush(); os.fsync(output.fileno())
        return destination
    except Exception:
        if created:
            try:
                if destination.exists() and not destination.is_symlink() and destination.is_file(): destination.unlink()
            except OSError: pass
        raise
@dataclass(frozen=True)
class PreviewVerification:
    relative_path:str; matches_source:bool; source_sha256:str; preview_sha256:str
def verify_preview_copy(source_root:str|Path,relative_path:str,preview_root:str|Path,*,consent:bool)->PreviewVerification:
    if consent is not True: raise PermissionError("Explicit preview verification consent is required before reading source image bytes.")
    source_root_path=Path(source_root).expanduser().resolve(strict=True); preview_root_path=Path(preview_root).expanduser().resolve(strict=True)
    if preview_root_path.is_relative_to(source_root_path): raise ValueError("Preview workspace must be outside the selected source-photo folder.")
    relative=_validated_relative_path(relative_path); us=source_root_path/relative; up=preview_root_path/relative
    if us.is_symlink() or up.is_symlink(): raise ValueError("Source and preview must be regular non-symlink files.")
    source_path=us.resolve(strict=True); preview_path=up.resolve(strict=True)
    if not source_path.is_relative_to(source_root_path) or not preview_path.is_relative_to(preview_root_path): raise ValueError("Verification path escapes its configured root.")
    for path,label in ((source_path,"source"),(preview_path,"preview")):
        if not path.is_file(): raise ValueError(f"{label.capitalize()} must be a regular non-symlink file.")
    sh=_sha256_file(source_path); ph=_sha256_file(preview_path); return PreviewVerification(relative.as_posix(),sh==ph,sh,ph)
def _sha256_file(path:Path)->str:
    digest=hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b""): digest.update(chunk)
    return digest.hexdigest()
def load_workspace(path:str|Path)->dict[str,CandidateWorkspaceRecord]:
    payload=json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload,dict) or payload.get("schema_version")!=WORKSPACE_SCHEMA_VERSION or not isinstance(payload.get("candidates"),list): raise ValueError("Workspace JSON does not match the supported schema.")
    records={}
    for item in payload["candidates"]:
        if not isinstance(item,dict): raise ValueError("Workspace candidate must be an object.")
        for name in ("relative_path","state","preview_relative_path"):
            if name in item and not isinstance(item[name],str): raise ValueError(f"Workspace candidate {name} must be a string.")
        record=CandidateWorkspaceRecord(item.get("relative_path",""),item.get("state",""),item.get("preview_relative_path","")); _validate_record(record)
        if record.relative_path in records: raise ValueError(f"Duplicate workspace candidate: {record.relative_path}")
        records[record.relative_path]=record
    return records
def save_workspace(records:dict[str,CandidateWorkspaceRecord],destination:str|Path,source_root:str|Path,*,overwrite:bool=False)->Path:
    root=Path(source_root).expanduser().resolve(strict=True); target=Path(destination).expanduser().resolve(strict=False)
    if target.is_relative_to(root): raise ValueError("Refusing to write workspace state inside the selected source-photo folder.")
    if target.suffix.lower()!=".json": raise ValueError("Workspace manifest must use a .json suffix.")
    for record in records.values(): _validate_record(record)
    serialized=json.dumps({"schema_version":WORKSPACE_SCHEMA_VERSION,"candidates":[asdict(records[k]) for k in sorted(records)]},ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    target.parent.mkdir(parents=True,exist_ok=True)
    if not overwrite:
        with target.open("x",encoding="utf-8",newline="\n") as output: output.write(serialized); output.flush(); os.fsync(output.fileno())
        return target
    if target.is_symlink() or not target.is_file(): raise ValueError("Refusing to replace a non-regular or symlink workspace manifest.")
    temporary_path=None
    try:
        with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",newline="\n",dir=target.parent,prefix=f".{target.stem}.",suffix=".tmp",delete=False) as temporary:
            temporary.write(serialized); temporary.flush(); os.fsync(temporary.fileno()); temporary_path=Path(temporary.name)
        os.replace(temporary_path,target)
    finally:
        if temporary_path is not None and temporary_path.exists(): temporary_path.unlink()
    return target
def set_candidate_state(records:dict[str,CandidateWorkspaceRecord],relative_path:str,state:str,*,preview_relative_path:str|None=None)->dict[str,CandidateWorkspaceRecord]:
    if state not in CANDIDATE_STATES: raise ValueError(f"Unsupported candidate state: {state}")
    if state=="submission-ready": raise ValueError("submission-ready cannot be set directly; use the consolidated 0.06 readiness workflow.")
    normalized=_validated_relative_path(relative_path).as_posix(); existing=records.get(normalized,CandidateWorkspaceRecord(normalized)); updated=CandidateWorkspaceRecord(normalized,state,existing.preview_relative_path if preview_relative_path is None else preview_relative_path); _validate_record(updated); result=dict(records); result[normalized]=updated; return result
def _validated_relative_path(relative_path:str)->Path:
    if not isinstance(relative_path,str) or not relative_path: raise ValueError("Candidate path must be a non-empty safe relative path.")
    candidate=Path(relative_path); windows=PureWindowsPath(relative_path)
    if candidate.is_absolute() or candidate.drive or windows.is_absolute() or windows.drive or ".." in candidate.parts or ".." in windows.parts: raise ValueError("Candidate path must be a non-empty safe relative path without parent traversal.")
    return candidate
def _validate_record(record:CandidateWorkspaceRecord)->None:
    _validated_relative_path(record.relative_path)
    if record.state not in CANDIDATE_STATES: raise ValueError(f"Unsupported candidate state: {record.state}")
    if record.preview_relative_path: _validated_relative_path(record.preview_relative_path)
