"""0.08 human-controlled marketplace outcome ledger.

Stores factual outcomes/reasons for later review. It does not learn a model,
change thresholds automatically, or infer future acceptance probability.
"""
from __future__ import annotations
from dataclasses import asdict,dataclass
from datetime import date
import json,os,tempfile
from pathlib import Path,PureWindowsPath
SCHEMA_VERSION=1
OUTCOMES=frozenset({"accepted","rejected","withdrawn","pending"})
@dataclass(frozen=True)
class MarketplaceOutcome:
 relative_path:str;marketplace:str;outcome:str;recorded_on:date;reason_codes:tuple[str,...]=();notes:str=""
 def __post_init__(self):
  _relative(self.relative_path)
  if not isinstance(self.marketplace,str) or not self.marketplace.strip():raise ValueError("marketplace is required")
  if self.outcome not in OUTCOMES:raise ValueError("unsupported outcome")
  if not isinstance(self.recorded_on,date):raise ValueError("recorded_on must be a date")
  if not isinstance(self.reason_codes,tuple) or any(not isinstance(x,str) or not x.strip() for x in self.reason_codes):raise ValueError("reason_codes must be non-empty text values")
  if len(set(x.casefold() for x in self.reason_codes))!=len(self.reason_codes):raise ValueError("reason_codes must be unique")
  if not isinstance(self.notes,str):raise ValueError("notes must be text")
def _relative(v):
 if not isinstance(v,str) or not v:raise ValueError("relative_path is required")
 n,w=Path(v),PureWindowsPath(v)
 if n.is_absolute() or n.drive or w.is_absolute() or w.drive or ".." in n.parts or ".." in w.parts:raise ValueError("relative_path must be safe and relative")
def outcome_to_json(r):
 if not isinstance(r,MarketplaceOutcome):raise ValueError("record must be MarketplaceOutcome")
 d=asdict(r);d["recorded_on"]=r.recorded_on.isoformat();return json.dumps({"schema_version":SCHEMA_VERSION,"outcome":d},ensure_ascii=False,sort_keys=True,indent=2)+"\n"
def outcome_from_json(text):
 p=json.loads(text)
 if not isinstance(p,dict) or set(p)!={"schema_version","outcome"} or p["schema_version"]!=SCHEMA_VERSION or not isinstance(p["outcome"],dict):raise ValueError("unsupported outcome document")
 d=p["outcome"];expected={"relative_path","marketplace","outcome","recorded_on","reason_codes","notes"}
 if set(d)!=expected or not isinstance(d["reason_codes"],list):raise ValueError("malformed outcome record")
 try:when=date.fromisoformat(d["recorded_on"])
 except (TypeError,ValueError) as e:raise ValueError("invalid recorded_on") from e
 return MarketplaceOutcome(d["relative_path"],d["marketplace"],d["outcome"],when,tuple(d["reason_codes"]),d["notes"])
def save_outcome(record,destination,source_root,*,overwrite=False):
 target=Path(destination).expanduser().resolve(strict=False);root=Path(source_root).expanduser().resolve(strict=False)
 if target.is_relative_to(root):raise ValueError("Outcome state must remain outside source-photo tree")
 target.parent.mkdir(parents=True,exist_ok=True);data=outcome_to_json(record)
 if target.exists() and not overwrite:raise FileExistsError(target)
 if target.exists() and (target.is_symlink() or not target.is_file()):raise ValueError("Refusing non-regular outcome destination")
 temp=None
 try:
  with tempfile.NamedTemporaryFile("w",encoding="utf-8",dir=target.parent,prefix=".outcome-",suffix=".tmp",delete=False) as f:f.write(data);f.flush();os.fsync(f.fileno());temp=Path(f.name)
  os.replace(temp,target)
 finally:
  if temp and temp.exists():temp.unlink()
 return target
