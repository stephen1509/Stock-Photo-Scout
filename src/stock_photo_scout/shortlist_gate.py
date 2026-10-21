"""Bridge legacy workspace labels to authoritative 0.07 review qualification."""
from dataclasses import dataclass
from .review_service import ReviewService

@dataclass(frozen=True)
class ShortlistGate:
 requested_state:str
 allowed:bool
 authoritative_review_complete:bool
 blockers:tuple[str,...]

def assess_workspace_transition(service:ReviewService,relative_path:str,requested_state:str)->ShortlistGate:
 if requested_state!="shortlist":return ShortlistGate(requested_state,True,False,())
 result=service.load(relative_path);assessment=result["assessment"]
 if assessment["can_shortlist"] is True:return ShortlistGate(requested_state,True,True,())
 blockers=tuple(assessment["blockers"]) or ("0.07 review has not qualified this candidate for shortlist.",)
 return ShortlistGate(requested_state,False,False,blockers)
