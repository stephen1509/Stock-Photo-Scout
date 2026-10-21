"""Structured human rights/IP review prompts; not legal advice."""
from dataclasses import dataclass,fields

@dataclass(frozen=True)
class RightsReview:
    recognizable_people:str="unchecked"; minors:str="unchecked"; private_property:str="unchecked"; artwork_or_sculpture:str="unchecked"; logos_or_trademarks:str="unchecked"; branded_products:str="unchecked"; copyrighted_characters:str="unchecked"; signs_screens_documents:str="unchecked"; identifiable_interiors:str="unchecked"; model_release:str="not-applicable"; property_release:str="not-applicable"; notes:str=""
_ALLOWED={"unchecked","none-seen","present","question"}; _RELEASE={"not-applicable","unavailable","available","question"}
def rights_blockers(r:RightsReview)->tuple[str,...]:
    b=[]
    for f in fields(r):
        if f.name in {"notes","model_release","property_release"}: continue
        v=getattr(r,f.name)
        if v not in _ALLOWED: raise ValueError(f"invalid rights value for {f.name}: {v}")
        if v=="unchecked": b.append(f"{f.name} has not been reviewed")
        elif v in {"present","question"}: b.append(f"{f.name} requires human rights/route review")
    for name in ("model_release","property_release"):
        v=getattr(r,name)
        if v not in _RELEASE: raise ValueError(f"invalid release value for {name}: {v}")
        if v=="question": b.append(f"{name} status is unresolved")
    return tuple(b)
