"""Combined fail-closed readiness for human-controlled review gates."""
from dataclasses import dataclass
from .candidate_review import CandidateReviewRecord,readiness_blockers
from .rights_review import RightsReview,rights_blockers
@dataclass(frozen=True)
class ReadinessAssessment: ready:bool; blockers:tuple[str,...]
def assess_readiness(*,review:CandidateReviewRecord,rights:RightsReview,provenance_current:bool,final_qc_confirmed:bool,current_marketplace_requirements_reviewed:bool)->ReadinessAssessment:
    b=list(readiness_blockers(review)); b.extend(rights_blockers(rights))
    if provenance_current is not True: b.append("Source/export provenance is not explicitly current.")
    if final_qc_confirmed is not True: b.append("Final export has not been explicitly rechecked at final-QC stage.")
    if current_marketplace_requirements_reviewed is not True: b.append("Current marketplace requirements have not been explicitly re-confirmed.")
    return ReadinessAssessment(not b,tuple(b))
