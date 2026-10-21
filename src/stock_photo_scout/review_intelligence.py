"""Human-controlled 0.07 review-intelligence records.

This module records review structure and prompts. It does not predict marketplace
acceptance and deliberately exposes no aggregate suitability score.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath

SCREEN_DECISIONS=("unreviewed","skip","hold","inspect")
FOCUS_STATES=("unknown","subject-confirmed","looks-clean","concern","needs-exact-pixel-review")
COMPOSITION_STATES=("unknown","weak","usable","strong")
REASON_CODES=frozenset((
 "duplicate-or-near-duplicate","weak-subject","weak-composition","distracting-background",
 "insufficient-copy-space","focus-concern","motion-blur-concern","noise-or-artifact-concern",
 "exposure-or-color-concern","rights-or-ip-concern","commercially-limited","editorial-interest",
 "stronger-similar-image-exists","promising-subject","strong-composition","useful-copy-space",
 "technically-clean-looking","needs-edit","other",
))

@dataclass(frozen=True)
class ReviewIntelligenceRecord:
 relative_path:str
 screen_decision:str="unreviewed"
 reason_codes:tuple[str,...]=()
 similar_group_id:str=""
 preferred_in_group:bool|None=None
 focus_state:str="unknown"
 subject_note:str=""
 composition_state:str="unknown"
 copy_space:bool|None=None
 alternate_crop_worth_reviewing:bool|None=None
 notes:str=""

def _relative(value:str)->None:
 if not isinstance(value,str) or not value:raise ValueError("relative_path must be non-empty")
 p,w=Path(value),PureWindowsPath(value)
 if p.is_absolute() or p.drive or w.is_absolute() or w.drive or ".." in p.parts or ".." in w.parts:raise ValueError("relative_path must be safe and relative")

def validate_review_intelligence(r:ReviewIntelligenceRecord)->None:
 if not isinstance(r,ReviewIntelligenceRecord):raise ValueError("record must be ReviewIntelligenceRecord")
 _relative(r.relative_path)
 if r.screen_decision not in SCREEN_DECISIONS:raise ValueError("unsupported screen_decision")
 if not isinstance(r.reason_codes,tuple):raise ValueError("reason_codes must be a tuple")
 if len(set(r.reason_codes))!=len(r.reason_codes):raise ValueError("reason_codes must not contain duplicates")
 unknown=set(r.reason_codes)-REASON_CODES
 if unknown:raise ValueError("unsupported reason code(s): "+", ".join(sorted(unknown)))
 if not isinstance(r.similar_group_id,str):raise ValueError("similar_group_id must be a string")
 for name,value in (("preferred_in_group",r.preferred_in_group),("copy_space",r.copy_space),("alternate_crop_worth_reviewing",r.alternate_crop_worth_reviewing)):
  if value is not None and not isinstance(value,bool):raise ValueError(name+" must be boolean or unknown")
 if r.focus_state not in FOCUS_STATES:raise ValueError("unsupported focus_state")
 if r.composition_state not in COMPOSITION_STATES:raise ValueError("unsupported composition_state")
 for name,value in (("subject_note",r.subject_note),("notes",r.notes)):
  if not isinstance(value,str):raise ValueError(name+" must be a string")
 if r.preferred_in_group is not None and not r.similar_group_id:raise ValueError("preferred_in_group requires a similar_group_id")

def review_prompts(r:ReviewIntelligenceRecord)->tuple[str,...]:
 """Return human review prompts; never an acceptance or suitability score."""
 validate_review_intelligence(r);p=[]
 if r.screen_decision=="unreviewed":p.append("Human fast-screen decision is still required.")
 if r.screen_decision=="inspect" and r.focus_state=="unknown":p.append("Confirm the intended subject/focus region before technical inspection.")
 if r.screen_decision=="inspect" and r.composition_state=="unknown":p.append("Review composition and practical stock usefulness.")
 if r.similar_group_id and r.preferred_in_group is None:p.append("Choose whether this is a preferred member of its similar/burst group.")
 if r.focus_state in {"concern","needs-exact-pixel-review"}:p.append("Inspect focus and motion at actual pixels before technical pass.")
 if r.composition_state=="weak":p.append("Composition is human-marked weak; compare against stronger similar images before proceeding.")
 return tuple(p)

def can_enter_shortlist_review(r:ReviewIntelligenceRecord)->bool:
 """A narrow workflow gate, not a stock-quality decision."""
 validate_review_intelligence(r)
 return r.screen_decision=="inspect"
