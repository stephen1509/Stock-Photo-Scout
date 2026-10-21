"""Structured human rights/IP review prompts; not legal advice.

``reviewed`` means a human has seen an issue and explicitly resolved how it is
treated for a particular submission route. It is never a legal-clearance claim.
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
    reviewed_route: str = "undecided"
    notes: str = ""

_ALLOWED={"unchecked","none-seen","present","question","reviewed"}
_RELEASE={"not-applicable","unavailable","available","question","reviewed"}
_ROUTES={"undecided","commercial","editorial"}

def rights_blockers(review: RightsReview, *, required_route: str | None = None) -> tuple[str,...]:
    if not isinstance(review, RightsReview): raise ValueError("review must be RightsReview")
    if review.reviewed_route not in _ROUTES: raise ValueError(f"invalid reviewed_route: {review.reviewed_route}")
    if not isinstance(review.notes,str): raise ValueError("rights notes must be a string")
    blockers=[]; route_sensitive=False
    for field in fields(review):
        if field.name in {"notes","model_release","property_release","reviewed_route"}: continue
        value=getattr(review,field.name)
        if value not in _ALLOWED: raise ValueError(f"invalid rights value for {field.name}: {value}")
        if value=="unchecked": blockers.append(f"{field.name} has not been reviewed")
        elif value in {"present","question"}: blockers.append(f"{field.name} requires human rights/route review")
        elif value=="reviewed": route_sensitive=True
    for name in ("model_release","property_release"):
        value=getattr(review,name)
        if value not in _RELEASE: raise ValueError(f"invalid release value for {name}: {value}")
        if value=="question": blockers.append(f"{name} status is unresolved")
        elif value=="reviewed": route_sensitive=True
    if required_route is not None:
        if required_route not in {"commercial","editorial"}: raise ValueError("required_route must be commercial or editorial")
        if route_sensitive and review.reviewed_route!=required_route:
            blockers.append("Rights handling was not explicitly reviewed for the selected submission route.")
    elif route_sensitive and review.reviewed_route not in {"commercial","editorial"}:
        blockers.append("Route-sensitive rights handling has not been bound to a concrete submission route.")
    return tuple(blockers)
