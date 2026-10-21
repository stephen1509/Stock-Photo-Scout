"""Marketplace-neutral, fail-closed rule-profile metadata.

This module stores *provenance about requirements*, not invented marketplace
requirements. A profile is usable only when a human has recorded an
Authoritative source URL, a verification date and an explicit review horizon.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from urllib.parse import urlparse

@dataclass(frozen=True)
class MarketplaceRuleProfile:
    marketplace: str
    source_url: str
    verified_on: date | None = None
    review_after_days: int | None = None
    notes: str = ""

@dataclass(frozen=True)
class MarketplaceRuleAssessment:
    usable: bool
    stale: bool
    blockers: tuple[str, ...]


def assess_rule_profile(profile: MarketplaceRuleProfile, *, today: date) -> MarketplaceRuleAssessment:
    if not isinstance(profile, MarketplaceRuleProfile):
        raise ValueError("profile must be MarketplaceRuleProfile")
    if not isinstance(today, date):
        raise ValueError("today must be a date")
    blockers=[]
    if not isinstance(profile.marketplace,str) or not profile.marketplace.strip(): blockers.append("Marketplace name is missing.")
    if not isinstance(profile.source_url,str) or not profile.source_url.strip(): blockers.append("Authoritative requirements source URL is missing.")
    else:
        parsed=urlparse(profile.source_url)
        if parsed.scheme!="https" or not parsed.netloc: blockers.append("Requirements source must be an HTTPS URL.")
    if profile.verified_on is None: blockers.append("Marketplace requirements have no human verification date.")
    elif not isinstance(profile.verified_on,date): blockers.append("Marketplace verification date is invalid.")
    elif profile.verified_on>today: blockers.append("Marketplace verification date cannot be in the future.")
    if not isinstance(profile.review_after_days,int) or isinstance(profile.review_after_days,bool) or profile.review_after_days<1:
        blockers.append("Marketplace requirements review horizon is missing or invalid.")
    if not isinstance(profile.notes,str): blockers.append("Marketplace rule-profile notes must be text.")
    stale=False
    if isinstance(profile.verified_on,date) and isinstance(profile.review_after_days,int) and not isinstance(profile.review_after_days,bool) and profile.review_after_days>0 and profile.verified_on<=today:
        stale=(today-profile.verified_on).days>profile.review_after_days
        if stale:blockers.append("Marketplace requirements are stale and must be re-verified against the authoritative source.")
    return MarketplaceRuleAssessment(not blockers,stale,tuple(blockers))
