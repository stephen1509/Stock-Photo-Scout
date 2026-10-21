"""Independent human-review dimensions for stock-photo candidates."""
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath

REVIEW_DECISIONS=("unreviewed","rejected","hold","candidate")
TECHNICAL_STATES=("unchecked","pass","inspect","edit","fail")
STOCK_POTENTIAL=("unknown","low","promising","strong")
RIGHTS_STATES=("unchecked","clear-looking","questions","release-needed")
ROUTES=("undecided","commercial","editorial","both-possible")
PREPARATION_STATES=("not-started","editing","metadata","preflight","ready")

@dataclass(frozen=True)
class CandidateReviewRecord:
    relative_path:str
    review_decision:str="unreviewed"
    technical_state:str="unchecked"
    stock_potential:str="unknown"
    rights_state:str="unchecked"
    route:str="undecided"
    preparation_state:str="not-started"
    reviewer_notes:str=""
    skip_reason:str=""
    edit_needed:bool=False

def _validate_path(value:str)->None:
    if not isinstance(value,str) or not value: raise ValueError("relative_path must be non-empty")
    p,w=Path(value),PureWindowsPath(value)
    if p.is_absolute() or w.is_absolute() or w.drive or ".." in p.parts or ".." in w.parts: raise ValueError("relative_path must stay inside the selected root")

def validate_candidate_review(r:CandidateReviewRecord)->None:
    _validate_path(r.relative_path)
    for value,allowed,name in ((r.review_decision,REVIEW_DECISIONS,"review_decision"),(r.technical_state,TECHNICAL_STATES,"technical_state"),(r.stock_potential,STOCK_POTENTIAL,"stock_potential"),(r.rights_state,RIGHTS_STATES,"rights_state"),(r.route,ROUTES,"route"),(r.preparation_state,PREPARATION_STATES,"preparation_state")):
        if value not in allowed: raise ValueError(f"unsupported {name}: {value}")
    if not isinstance(r.edit_needed,bool): raise ValueError("edit_needed must be boolean")

def readiness_blockers(r:CandidateReviewRecord)->tuple[str,...]:
    validate_candidate_review(r); b=[]
    if r.review_decision!="candidate": b.append("Human review has not marked this image as a candidate.")
    if r.technical_state!="pass": b.append("Technical review is not explicitly passed.")
    if r.stock_potential not in {"promising","strong"}: b.append("Stock potential is not explicitly promising or strong.")
    if r.rights_state!="clear-looking": b.append("Rights review is unresolved or requires follow-up.")
    if r.route=="undecided": b.append("Commercial/editorial route is undecided.")
    if r.preparation_state!="ready": b.append("Preparation is not explicitly ready.")
    if r.edit_needed: b.append("An outstanding edit is still marked as needed.")
    return tuple(b)
