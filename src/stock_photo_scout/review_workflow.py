"""Fail-closed workflow composition for 0.07 review intelligence."""
from dataclasses import dataclass
from .review_intelligence import ReviewIntelligenceRecord,review_prompts,validate_review_intelligence
from .stock_usefulness import StockUsefulnessReview,usefulness_prompts,review_complete
@dataclass(frozen=True)
class ReviewWorkflowAssessment:
 stage:str
 can_shortlist:bool
 blockers:tuple[str,...]
 prompts:tuple[str,...]
def assess_review_workflow(review:ReviewIntelligenceRecord,usefulness:StockUsefulnessReview|None=None)->ReviewWorkflowAssessment:
 validate_review_intelligence(review);prompts=list(review_prompts(review));blockers=[]
 if review.screen_decision=="unreviewed":return ReviewWorkflowAssessment("stage-1",False,("Fast-screen decision is required.",),tuple(prompts))
 if review.screen_decision in {"skip","hold"}:return ReviewWorkflowAssessment("stage-1",False,("Candidate has not been selected for Stage-2 inspection.",),tuple(prompts))
 if review.focus_state=="unknown":blockers.append("Intended subject/focus review is incomplete.")
 elif review.focus_state in {"concern","needs-exact-pixel-review"}:blockers.append("Focus requires actual-pixel technical resolution before shortlist completion.")
 if review.composition_state=="unknown":blockers.append("Human composition review is incomplete.")
 if usefulness is None:blockers.append("Composition/stock-usefulness review is missing.")
 else:
  prompts.extend(usefulness_prompts(usefulness))
  if not review_complete(usefulness):blockers.append("Composition/stock-usefulness review is incomplete.")
 if review.similar_group_id and review.preferred_in_group is not True:blockers.append("A grouped candidate must be explicitly chosen as a preferred member before shortlist completion.")
 return ReviewWorkflowAssessment("stage-2",not blockers,tuple(blockers),tuple(dict.fromkeys(prompts)))
