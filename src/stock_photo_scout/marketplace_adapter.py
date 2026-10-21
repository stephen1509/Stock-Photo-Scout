"""0.08 marketplace adapter contract without invented marketplace rules.

Adapters translate a human-verified rule profile plus candidate facts into
explicit blockers/prompts. They never infer acceptance probability and never
submit anything to a marketplace.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from .marketplace_rules import MarketplaceRuleProfile, assess_rule_profile

@dataclass(frozen=True)
class MarketplaceCandidateFacts:
    route: str = "undecided"
    title_present: bool | None = None
    description_present: bool | None = None
    keywords_present: bool | None = None
    rights_review_complete: bool | None = None
    exact_export_qc_complete: bool | None = None

@dataclass(frozen=True)
class MarketplaceAdapterAssessment:
    marketplace: str
    usable_rule_profile: bool
    ready_for_human_marketplace_preflight: bool
    blockers: tuple[str,...]


def assess_marketplace_candidate(profile: MarketplaceRuleProfile, facts: MarketplaceCandidateFacts, *, today: date) -> MarketplaceAdapterAssessment:
    if not isinstance(facts,MarketplaceCandidateFacts):raise ValueError("facts must be MarketplaceCandidateFacts")
    rules=assess_rule_profile(profile,today=today);blockers=list(rules.blockers)
    if facts.route not in {"commercial","editorial"}:blockers.append("A concrete commercial/editorial route has not been selected.")
    for value,label in ((facts.title_present,"Title"),(facts.description_present,"Description"),(facts.keywords_present,"Keywords"),(facts.rights_review_complete,"Rights review"),(facts.exact_export_qc_complete,"Exact-export QC")):
        if value is not True:blockers.append(label+" is not explicitly complete.")
    return MarketplaceAdapterAssessment(profile.marketplace,rules.usable,not blockers,tuple(blockers))
