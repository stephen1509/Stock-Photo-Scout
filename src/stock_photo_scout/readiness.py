"""Combined fail-closed readiness for human-controlled review gates."""
from dataclasses import dataclass
from .candidate_review import CandidateReviewRecord, readiness_blockers
from .rights_review import RightsReview, rights_blockers
from .final_qc import FinalQcRecord, final_qc_blockers

@dataclass(frozen=True)
class ReadinessAssessment:
    ready: bool
    blockers: tuple[str,...]

def assess_readiness(*,review:CandidateReviewRecord,rights:RightsReview,provenance_current:bool,current_marketplace_requirements_reviewed:bool,final_qc:FinalQcRecord|None=None,current_export_sha256:str="",final_qc_confirmed:bool|None=None)->ReadinessAssessment:
    """Fail closed across independent review, rights, provenance, exact-file QC and current marketplace gates.

    ``final_qc_confirmed`` remains only for old caller compatibility and cannot
    make an image ready. Rights marked ``reviewed`` must be bound to the exact
    final commercial/editorial route selected by the candidate review.
    """
    blockers=list(readiness_blockers(review))
    required_route=review.route if review.route in {"commercial","editorial"} else None
    blockers.extend(rights_blockers(rights,required_route=required_route))
    if provenance_current is not True:blockers.append("Source/export provenance is not explicitly current.")
    if final_qc is None:blockers.append("Final export has no exact-file QC record.")
    else:blockers.extend(final_qc_blockers(final_qc,current_export_sha256=current_export_sha256))
    if current_marketplace_requirements_reviewed is not True:blockers.append("Current marketplace requirements have not been explicitly re-confirmed.")
    return ReadinessAssessment(not blockers,tuple(blockers))
