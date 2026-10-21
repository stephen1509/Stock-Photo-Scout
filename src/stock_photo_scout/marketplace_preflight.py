"""High-level marketplace preflight binding readiness to sourced rule provenance."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from .marketplace_rules import MarketplaceRuleProfile,assess_rule_profile
from .readiness import ReadinessAssessment
@dataclass(frozen=True)
class MarketplacePreflightAssessment:
 marketplace:str
 ready_for_human_preflight:bool
 blockers:tuple[str,...]
def assess_marketplace_preflight(readiness:ReadinessAssessment,profile:MarketplaceRuleProfile,*,today:date)->MarketplacePreflightAssessment:
 if not isinstance(readiness,ReadinessAssessment):raise ValueError("readiness must be ReadinessAssessment")
 rules=assess_rule_profile(profile,today=today);blockers=list(readiness.blockers)
 if readiness.ready is not True and not blockers:blockers.append("Core candidate readiness is not explicitly complete.")
 for b in rules.blockers:
  if b not in blockers:blockers.append(b)
 return MarketplacePreflightAssessment(profile.marketplace,readiness.ready is True and rules.usable and not blockers,tuple(blockers))
