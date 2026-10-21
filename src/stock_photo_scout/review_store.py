"""Deterministic external persistence for 0.07 human review records."""
from __future__ import annotations
from dataclasses import asdict
import json, os, tempfile
from pathlib import Path
from .review_intelligence import ReviewIntelligenceRecord, validate_review_intelligence

REVIEW_SCHEMA_VERSION=1

def review_to_json(record:ReviewIntelligenceRecord)->str:
 validate_review_intelligence(record)
 return json.dumps({"schema_version":REVIEW_SCHEMA_VERSION,"review":asdict(record)},ensure_ascii=False,indent=2,sort_keys=True)+"\n"

def review_from_json(text:str)->ReviewIntelligenceRecord:
 payload=json.loads(text)
 if not isinstance(payload,dict) or set(payload)!={"schema_version","review"} or payload.get("schema_version")!=REVIEW_SCHEMA_VERSION or not isinstance(payload.get("review"),dict):raise ValueError("Review JSON does not match the supported schema.")
 raw=payload["review"]
 allowed={"relative_path","screen_decision","reason_codes","similar_group_id","preferred_in_group","focus_state","subject_note","composition_state","copy_space","alternate_crop_worth_reviewing","notes"}
 if set(raw)-allowed:raise ValueError("Review JSON contains unsupported fields.")
 if "relative_path" not in raw:raise ValueError("Review JSON requires relative_path.")
 if "reason_codes" in raw:
  if not isinstance(raw["reason_codes"],list) or not all(isinstance(x,str) for x in raw["reason_codes"]):raise ValueError("reason_codes must be a list of strings.")
  raw=dict(raw);raw["reason_codes"]=tuple(raw["reason_codes"])
 try:record=ReviewIntelligenceRecord(**raw)
 except TypeError as exc:raise ValueError("Review JSON fields are invalid.") from exc
 validate_review_intelligence(record);return record

def save_review(record:ReviewIntelligenceRecord,destination:str|Path,source_root:str|Path,*,overwrite:bool=False)->Path:
 root=Path(source_root).expanduser().resolve(strict=True);target=Path(destination).expanduser().resolve(strict=False)
 if target.is_relative_to(root):raise ValueError("Refusing to write review state inside the source-photo folder.")
 if target.suffix.lower()!=".json":raise ValueError("Review state must use a .json suffix.")
 serialized=review_to_json(record);target.parent.mkdir(parents=True,exist_ok=True)
 if not overwrite:
  with target.open("x",encoding="utf-8",newline="\n") as out:out.write(serialized);out.flush();os.fsync(out.fileno())
  return target
 if target.is_symlink() or not target.is_file():raise ValueError("Refusing to replace a non-regular or symlink review file.")
 temporary_path=None
 try:
  with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",newline="\n",dir=target.parent,prefix=f".{target.stem}.",suffix=".tmp",delete=False) as temporary:
   temporary.write(serialized);temporary.flush();os.fsync(temporary.fileno());temporary_path=Path(temporary.name)
  os.replace(temporary_path,target)
 finally:
  if temporary_path is not None and temporary_path.exists():temporary_path.unlink()
 return target

def load_review(path:str|Path)->ReviewIntelligenceRecord:
 target=Path(path)
 if target.is_symlink() or not target.is_file():raise ValueError("Review state must be a regular non-symlink file.")
 return review_from_json(target.read_text(encoding="utf-8"))
