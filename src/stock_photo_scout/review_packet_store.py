"""Atomic combined persistence for a candidate's 0.07 human review packet.

The combined packet prevents review/usefulness state from tearing across two
separate writes. Legacy split files remain readable through ReviewService.
"""
from __future__ import annotations
from dataclasses import asdict
import json,os,tempfile
from pathlib import Path
from .review_intelligence import ReviewIntelligenceRecord,validate_review_intelligence
from .stock_usefulness import StockUsefulnessReview,validate_stock_usefulness
SCHEMA_VERSION=1
def packet_to_json(review:ReviewIntelligenceRecord,usefulness:StockUsefulnessReview)->str:
 validate_review_intelligence(review);validate_stock_usefulness(usefulness);return json.dumps({"schema_version":SCHEMA_VERSION,"review":asdict(review),"usefulness":asdict(usefulness)},ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+"\n"
def packet_from_json(text:str)->tuple[ReviewIntelligenceRecord,StockUsefulnessReview]:
 p=json.loads(text)
 if not isinstance(p,dict) or set(p)!={"schema_version","review","usefulness"} or p.get("schema_version")!=SCHEMA_VERSION or not isinstance(p.get("review"),dict) or not isinstance(p.get("usefulness"),dict):raise ValueError("Review packet JSON does not match the supported schema.")
 rr=dict(p["review"]);ur=dict(p["usefulness"]);review_allowed={"relative_path","screen_decision","reason_codes","similar_group_id","preferred_in_group","focus_state","subject_note","composition_state","copy_space","alternate_crop_worth_reviewing","notes"};usefulness_allowed={"subject_clarity","background_clutter","copy_space","crop_flexibility","redundancy","alternate_orientation_worth_reviewing","human_confirmed","notes"}
 if set(rr)-review_allowed or set(ur)-usefulness_allowed:raise ValueError("Review packet contains unsupported fields.")
 if "relative_path" not in rr:raise ValueError("Review packet requires relative_path.")
 if "reason_codes" in rr:
  if not isinstance(rr["reason_codes"],list) or not all(isinstance(x,str) for x in rr["reason_codes"]):raise ValueError("reason_codes must be a list of strings.")
  rr["reason_codes"]=tuple(rr["reason_codes"])
 try:review=ReviewIntelligenceRecord(**rr);usefulness=StockUsefulnessReview(**ur)
 except TypeError as exc:raise ValueError("Review packet fields are invalid.") from exc
 validate_review_intelligence(review);validate_stock_usefulness(usefulness);return review,usefulness
def _reject_symlink_ancestors(target:Path)->None:
 current=target.parent
 while True:
  if current.exists() and current.is_symlink():raise ValueError("Refusing review packet path through a symlink directory.")
  if current==current.parent:break
  current=current.parent
def _fsync_directory(directory:Path)->None:
 try:
  fd=os.open(directory,os.O_RDONLY)
 except (AttributeError,OSError):return
 try:os.fsync(fd)
 except OSError:pass
 finally:os.close(fd)
def save_packet(review:ReviewIntelligenceRecord,usefulness:StockUsefulnessReview,destination:str|Path,source_root:str|Path,*,overwrite:bool=False)->Path:
 root=Path(source_root).expanduser().resolve(strict=True);raw=Path(destination).expanduser();_reject_symlink_ancestors(raw)
 if raw.is_symlink():raise ValueError("Refusing symlink review packet destination.")
 target=raw.resolve(strict=False)
 if target.is_relative_to(root):raise ValueError("Refusing to write review packet inside the source-photo folder.")
 if target.suffix.lower()!=".json":raise ValueError("Review packet must use a .json suffix.")
 text=packet_to_json(review,usefulness);target.parent.mkdir(parents=True,exist_ok=True);_reject_symlink_ancestors(target)
 if target.exists() and (target.is_symlink() or not target.is_file()):raise ValueError("Refusing non-regular or symlink review packet destination.")
 if target.exists() and not overwrite:raise FileExistsError(target)
 temp=None
 try:
  with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",newline="\n",dir=target.parent,prefix=f".{target.stem}.",suffix=".tmp",delete=False) as out:out.write(text);out.flush();os.fsync(out.fileno());temp=Path(out.name)
  os.replace(temp,target);_fsync_directory(target.parent)
 finally:
  if temp is not None and temp.exists():temp.unlink()
 return target
def load_packet(path:str|Path)->tuple[ReviewIntelligenceRecord,StockUsefulnessReview]:
 target=Path(path)
 if target.is_symlink() or not target.is_file():raise ValueError("Review packet must be a regular non-symlink file.")
 return packet_from_json(target.read_text(encoding="utf-8"))
