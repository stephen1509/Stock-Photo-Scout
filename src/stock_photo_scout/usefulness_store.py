"""Safe external persistence for human composition/usefulness reviews."""
from dataclasses import asdict
import json,os,tempfile
from pathlib import Path
from .stock_usefulness import StockUsefulnessReview,validate_stock_usefulness
SCHEMA_VERSION=1

def usefulness_to_json(record:StockUsefulnessReview)->str:
 validate_stock_usefulness(record);return json.dumps({"schema_version":SCHEMA_VERSION,"usefulness":asdict(record)},ensure_ascii=False,indent=2,sort_keys=True)+"\n"
def usefulness_from_json(text:str)->StockUsefulnessReview:
 p=json.loads(text)
 if not isinstance(p,dict) or set(p)!={"schema_version","usefulness"} or p.get("schema_version")!=SCHEMA_VERSION or not isinstance(p.get("usefulness"),dict):raise ValueError("Usefulness JSON does not match the supported schema.")
 raw=p["usefulness"];allowed={"subject_clarity","background_clutter","copy_space","crop_flexibility","redundancy","alternate_orientation_worth_reviewing","human_confirmed","notes"}
 if set(raw)-allowed:raise ValueError("Usefulness JSON contains unsupported fields.")
 try:r=StockUsefulnessReview(**raw)
 except TypeError as exc:raise ValueError("Usefulness JSON fields are invalid.") from exc
 validate_stock_usefulness(r);return r
def save_usefulness(record:StockUsefulnessReview,destination:str|Path,source_root:str|Path,*,overwrite:bool=False)->Path:
 root=Path(source_root).expanduser().resolve(strict=True);target=Path(destination).expanduser().resolve(strict=False)
 if target.is_relative_to(root):raise ValueError("Refusing to write usefulness state inside the source-photo folder.")
 if target.suffix.lower()!=".json":raise ValueError("Usefulness state must use a .json suffix.")
 text=usefulness_to_json(record);target.parent.mkdir(parents=True,exist_ok=True)
 if not overwrite:
  with target.open("x",encoding="utf-8",newline="\n") as out:out.write(text);out.flush();os.fsync(out.fileno())
  return target
 if target.is_symlink() or not target.is_file():raise ValueError("Refusing to replace a non-regular or symlink usefulness file.")
 temp=None
 try:
  with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",newline="\n",dir=target.parent,prefix=f".{target.stem}.",suffix=".tmp",delete=False) as out:out.write(text);out.flush();os.fsync(out.fileno());temp=Path(out.name)
  os.replace(temp,target)
 finally:
  if temp is not None and temp.exists():temp.unlink()
 return target
def load_usefulness(path:str|Path)->StockUsefulnessReview:
 p=Path(path)
 if p.is_symlink() or not p.is_file():raise ValueError("Usefulness state must be a regular non-symlink file.")
 return usefulness_from_json(p.read_text(encoding="utf-8"))
