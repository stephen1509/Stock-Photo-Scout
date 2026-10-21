"""Combined fail-closed readiness for human-controlled review gates."""
from dataclasses import dataclass
from .candidate_review import CandidateReviewRecord, readiness_blockers
from .rights_review import RightsReview, rights_blockers
from .final_qc import FinalQcRecord, final_qc_blockers


@dataclass(frozen=True)
class ReadinessAssessment:
    ready: bool
    blockers: tuple[str, ...]


def assess_readiness(
    *,
    review: CandidateReviewRecord,
    rights: RightsReview,
    provenance_current: bool,
    current_marketplace_requirements_reviewed: bool,
    final_qc: FinalQcRecord | None = None,
    current_export_sha256: str = "",
    final_qc_confirmed: bool | None = None,
) -> ReadinessAssessment:
    """Assess readiness without allowing unknown gates to become truthy.

    `final_qc_confirmed` is retained temporarily for compatibility with older
    callers, but it cannot make a candidate ready. New readiness requires a
    FinalQcRecord bound to the exact current export SHA-256.
    """
    blockers = list(readiness_blockers(review))
    blockers.extend(rights_blockers(rights))
    if provenance_current is not True:
        blockers.append("Source/export provenance is not explicitly current.")
    if final_qc is None:
        blockers.append("Final export has no exact-file QC record.")
    else:
        blockers.extend(final_qc_blockers(final_qc, current_export_sha256=current_export_sha256))
    if current_marketplace_requirements_reviewed is not True:
        blockers.append("Current marketplace requirements have not been explicitly re-confirmed.")
    return ReadinessAssessment(not blockers, tuple(blockers))
