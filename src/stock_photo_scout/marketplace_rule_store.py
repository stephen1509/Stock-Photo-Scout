"""External persistence for human-verified marketplace rule provenance."""
from __future__ import annotations
from dataclasses import asdict
from datetime import date
import json,os,tempfile
from pathlib import Path
from .marketplace_rules import MarketplaceRuleProfile,assess_rule_profile
SCHEMA_VERSION=1
def profile_to_json(profile:MarketplaceRuleProfile)->str:
 if not isinstance(profile,MarketplaceRuleProfile):raise ValueError("profile must be MarketplaceRuleProfile")
 p=asdict(profile);p["verified_on"]=profile.verified_on.isoformat() if isinstance(profile.verified_on,date) else None
 return json.dumps({"schema_version":SCHEMA_VERSION,"profile":p},ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+"\n"
def profile_from_json(text:str)->MarketplaceRuleProfile:
 p=json.loads(text)
 if not isinstance(p,dict) or set(p)!={"schema_version","profile"} or p.get("schema_version")!=SCHEMA_VERSION or not isinstance(p.get("profile"),dict):raise ValueError("Marketplace rule JSON does not match the supported schema.")
 item=p["profile"];allowed={"marketplace","source_url","verified_on","review_after_days","notes"}
 if set(item)-allowed or not {"marketplace","source_url"}.issubset(item):raise ValueError("Marketplace rule profile has unsupported or missing fields.")
 raw=item.get("verified_on")
 try:verified=date.fromisoformat(raw) if raw is not None else None
 except (TypeError,ValueError) as exc:raise ValueError("Marketplace verification date is invalid.") from exc
 try:return MarketplaceRuleProfile(item["marketplace"],item["source_url"],verified,item.get("review_after_days"),item.get("notes",""))
 except TypeError as exc:raise ValueError("Marketplace rule profile fields are invalid.") from exc
def _reject_symlink_ancestors(target:Path)->None:
 current=target.parent
 while True:
  if current.exists() and current.is_symlink():raise ValueError("Refusing marketplace rule path through a symlink directory.")
  if current==current.parent:break
  current=current.parent
def _fsync_directory(directory:Path)->None:
 try:
  fd=os.open(directory,os.O_RDONLY)
 except (AttributeError,OSError):return
 try:os.fsync(fd)
 except OSError:pass
 finally:os.close(fd)
def save_profile(profile:MarketplaceRuleProfile,destination:str|Path,*,overwrite:bool=False)->Path:
 raw=Path(destination).expanduser();_reject_symlink_ancestors(raw)
 if raw.is_symlink():raise ValueError("Refusing symlink marketplace rule destination.")
 target=raw.resolve(strict=False)
 if target.suffix.lower()!=".json":raise ValueError("Marketplace rule profile must use a .json suffix.")
 target.parent.mkdir(parents=True,exist_ok=True);_reject_symlink_ancestors(target)
 if target.exists() and (target.is_symlink() or not target.is_file()):raise ValueError("Refusing non-regular marketplace rule destination.")
 if target.exists() and not overwrite:raise FileExistsError(target)
 text=profile_to_json(profile);temp=None
 try:
  with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",newline="\n",dir=target.parent,prefix=f".{target.stem}.",suffix=".tmp",delete=False) as out:out.write(text);out.flush();os.fsync(out.fileno());temp=Path(out.name)
  os.replace(temp,target);_fsync_directory(target.parent)
 finally:
  if temp is not None and temp.exists():temp.unlink()
 return target
def load_profile(path:str|Path)->MarketplaceRuleProfile:
 target=Path(path)
 if target.is_symlink() or not target.is_file():raise ValueError("Marketplace rule profile must be a regular non-symlink file.")
 return profile_from_json(target.read_text(encoding="utf-8"))
def load_and_assess(path:str|Path,*,today:date):
 profile=load_profile(path);return profile,assess_rule_profile(profile,today=today)
