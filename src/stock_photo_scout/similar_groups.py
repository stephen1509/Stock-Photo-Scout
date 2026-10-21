"""Deterministic, explainable grouping hints for human review.

These helpers do not inspect image pixels, create embeddings, or reject images.
They only expose conservative grouping facts/hints for a human reviewer.
"""
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
import re

@dataclass(frozen=True)
class GroupCandidate:
 relative_path:str
 sha256:str=""
 captured_at_seconds:int|None=None

@dataclass(frozen=True)
class GroupHint:
 left:str
 right:str
 reasons:tuple[str,...]

def _path(v:str)->None:
 if not isinstance(v,str) or not v:raise ValueError("relative_path must be non-empty")
 p,w=Path(v),PureWindowsPath(v)
 if p.is_absolute() or p.drive or w.is_absolute() or w.drive or ".." in p.parts or ".." in w.parts:raise ValueError("relative_path must be safe and relative")

def _validate(c:GroupCandidate)->None:
 _path(c.relative_path)
 if not isinstance(c.sha256,str):raise ValueError("sha256 must be a string")
 if c.sha256 and (len(c.sha256)!=64 or any(x not in "0123456789abcdefABCDEF" for x in c.sha256)):raise ValueError("sha256 must be blank or a 64-character hex digest")
 if c.captured_at_seconds is not None and (isinstance(c.captured_at_seconds,bool) or not isinstance(c.captured_at_seconds,int) or c.captured_at_seconds<0):raise ValueError("captured_at_seconds must be a non-negative integer or unknown")

def _sequence(name:str)->tuple[str,int]|None:
 stem=Path(name).stem
 m=re.match(r"^(.*?)(\d+)$",stem)
 if not m:return None
 return m.group(1).casefold(),int(m.group(2))

def grouping_hint(a:GroupCandidate,b:GroupCandidate,*,capture_window_seconds:int=3,filename_sequence_gap:int=2)->GroupHint|None:
 _validate(a);_validate(b)
 if a.relative_path==b.relative_path:raise ValueError("grouping requires two different candidates")
 if isinstance(capture_window_seconds,bool) or not isinstance(capture_window_seconds,int) or capture_window_seconds<0:raise ValueError("capture_window_seconds must be non-negative")
 if isinstance(filename_sequence_gap,bool) or not isinstance(filename_sequence_gap,int) or filename_sequence_gap<1:raise ValueError("filename_sequence_gap must be positive")
 reasons=[]
 if a.sha256 and b.sha256 and a.sha256.casefold()==b.sha256.casefold():reasons.append("exact-content-hash")
 if a.captured_at_seconds is not None and b.captured_at_seconds is not None and abs(a.captured_at_seconds-b.captured_at_seconds)<=capture_window_seconds:reasons.append("capture-time-proximity")
 sa,sb=_sequence(a.relative_path),_sequence(b.relative_path)
 if sa and sb and sa[0]==sb[0] and 0<abs(sa[1]-sb[1])<=filename_sequence_gap:reasons.append("filename-sequence-proximity")
 if not reasons:return None
 return GroupHint(a.relative_path,b.relative_path,tuple(reasons))

def build_group_hints(candidates:tuple[GroupCandidate,...],*,capture_window_seconds:int=3,filename_sequence_gap:int=2)->tuple[GroupHint,...]:
 if not isinstance(candidates,tuple):raise ValueError("candidates must be a tuple")
 seen=set()
 for c in candidates:
  _validate(c)
  if c.relative_path in seen:raise ValueError("candidate paths must be unique")
  seen.add(c.relative_path)
 hints=[]
 for i,a in enumerate(candidates):
  for b in candidates[i+1:]:
   h=grouping_hint(a,b,capture_window_seconds=capture_window_seconds,filename_sequence_gap=filename_sequence_gap)
   if h:hints.append(h)
 return tuple(hints)
