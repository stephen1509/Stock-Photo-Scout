"""Structured human rights/IP review prompts; not legal advice.

A visible issue does not automatically mean a photograph is unusable. ``reviewed``
means a human has seen the issue and explicitly resolved its handling for the
chosen route (for example editorial treatment). It is not a legal-clearance
claim.
"""
from dataclasses import dataclass, fields

@dataclass(frozen=True)
class RightsReview:
    recognizable_people: str = "unchecked"
    minors: str = "unchecked"
    private_property: str = "unchecked"
    artwork_or_sculpture: str = "unchecked"
    logos_or_trademarks: str = "unchecked"
    branded_products: str = "unchecked"
    copyrighted_characters: str = "unchecked"
    signs_screens_documents: str = "unchecked"
    identifiable_interiors: str = "unchecked"
    model_release: str = "not-applicable"
    property_release: str = "not-applicable"
    notes: str = ""

_ALLOWED = {"unchecked", "none-seen", "present", "question", "reviewed"}
_RELEASE = {"not-applicable", "unavailable", "available", "question", "reviewed"}


def rights_blockers(review: RightsReview) -> tuple[str, ...]:
    blockers = []
    for field in fields(review):
        if field.name in {"notes", "model_release", "property_release"}:
            continue
        value = getattr(review, field.name)
        if value not in _ALLOWED:
            raise ValueError(f"invalid rights value for {field.name}: {value}")
        if value == "unchecked":
            blockers.append(f"{field.name} has not been reviewed")
        elif value in {"present", "question"}:
            blockers.append(f"{field.name} requires human rights/route review")
    for name in ("model_release", "property_release"):
        value = getattr(review, name)
        if value not in _RELEASE:
            raise ValueError(f"invalid release value for {name}: {value}")
        if value == "question":
            blockers.append(f"{name} status is unresolved")
    return tuple(blockers)
