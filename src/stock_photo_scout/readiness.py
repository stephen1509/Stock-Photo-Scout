"""Combined fail-closed readiness for human-controlled review gates."""
from dataclasses import dataclass
from pathlib import Path
from .candidate_review import CandidateReviewRecord, readiness_blockers
from .rights_review import RightsReview, rights_blockers
from .final_qc import FinalQcRecord, final_qc_blockers
from .provenance import ProvenanceRecord, verify_provenance

@dataclass(frozen=True)
class ReadinessAssessment:
    ready: bool
    blockers: tuple[str,...]

def assess_readiness(*,review:CandidateReviewRecord,rights:RightsReview,provenance_current:bool,current_marketplace_requirements_reviewed:bool,final_qc:FinalQcRecord|None=None,current_export_sha256:str="",final_qc_confirmed:bool|None=None,review_intelligence_complete:bool|None=None)->ReadinessAssessment:
    """Compose already-evaluated fail-closed readiness gates.

    ``review_intelligence_complete`` must be literal True. ``final_qc_confirmed``
    remains only for old caller compatibility and cannot make an image ready.
    Prefer :func:`assess_recorded_readiness` when a provenance record and roots
    are available so callers cannot accidentally invent a provenance boolean.
    """
    blockers=list(readiness_blockers(review))
    if review_intelligence_complete is not True:blockers.append("0.07 human review intelligence is not explicitly complete.")
    required_route=review.route if review.route in {"commercial","editorial"} else None
    blockers.extend(rights_blockers(rights,required_route=required_route))
    if provenance_current is not True:blockers.append("Source/export provenance is not explicitly current.")
    if final_qc is None:blockers.append("Final export has no exact-file QC record.")
    else:blockers.extend(final_qc_blockers(final_qc,current_export_sha256=current_export_sha256))
    if current_marketplace_requirements_reviewed is not True:blockers.append("Current marketplace requirements have not been explicitly re-confirmed.")
    return ReadinessAssessment(not blockers,tuple(blockers))

def assess_recorded_readiness(*,review:CandidateReviewRecord,rights:RightsReview,provenance:ProvenanceRecord,source_root:Path,export_root:Path,provenance_consent:bool,current_marketplace_requirements_reviewed:bool,final_qc:FinalQcRecord|None=None,review_intelligence_complete:bool|None=None)->ReadinessAssessment:
    """Verify the recorded source/export bytes, then assess the exact recorded export.

    Provenance verification reads the two explicitly selected files and therefore
    requires literal byte-read consent. Verification errors fail closed and are
    returned as blockers rather than being converted into a readiness success.
    """
    provenance_blockers=[]
    try:
        if not isinstance(provenance,ProvenanceRecord):raise ValueError("provenance must be ProvenanceRecord")
        current,provenance_blockers_raw=verify_provenance(provenance,source_root,export_root,consent=provenance_consent)
        provenance_blockers.extend(provenance_blockers_raw)
    except (ValueError,PermissionError,FileNotFoundError,OSError) as exc:
        current=False; provenance_blockers.append("Provenance verification failed: "+str(exc))
    base=assess_readiness(review=review,rights=rights,provenance_current=current,final_qc=final_qc,current_export_sha256=provenance.export.sha256 if isinstance(provenance,ProvenanceRecord) else "",current_marketplace_requirements_reviewed=current_marketplace_requirements_reviewed,review_intelligence_complete=review_intelligence_complete)
    blockers=list(provenance_blockers)
    for blocker in base.blockers:
        if blocker not in blockers:blockers.append(blocker)
    return ReadinessAssessment(not blockers,tuple(blockers))
