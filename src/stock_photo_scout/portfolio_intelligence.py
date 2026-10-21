"""0.08 explainable portfolio observations; never a sales/acceptance score."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class PortfolioCandidate:
    relative_path: str
    subject_key: str = ""
    orientation: str = "unknown"
    route: str = "undecided"
    copy_space: str = "unknown"
    human_priority: str = "unreviewed"

@dataclass(frozen=True)
class PortfolioObservation:
    code: str
    explanation: str
    related_paths: tuple[str,...] = ()

_ORIENTATIONS={"unknown","landscape","portrait","square"}
_ROUTES={"undecided","commercial","editorial"}
_COPY={"unknown","none","left","right","top","bottom","multiple"}
_PRIORITY={"unreviewed","low","normal","high"}

def portfolio_observations(candidates: tuple[PortfolioCandidate,...]) -> tuple[PortfolioObservation,...]:
    if not isinstance(candidates,tuple):raise ValueError("candidates must be a tuple")
    seen=set(); groups={}; observations=[]
    for c in candidates:
        if not isinstance(c,PortfolioCandidate):raise ValueError("candidate must be PortfolioCandidate")
        if not isinstance(c.relative_path,str) or not c.relative_path or c.relative_path in seen:raise ValueError("candidate paths must be unique non-empty text")
        seen.add(c.relative_path)
        if not isinstance(c.subject_key,str):raise ValueError("subject_key must be text")
        if c.orientation not in _ORIENTATIONS or c.route not in _ROUTES or c.copy_space not in _COPY or c.human_priority not in _PRIORITY:raise ValueError("unsupported portfolio observation value")
        if c.subject_key.strip():groups.setdefault(c.subject_key.strip().casefold(),[]).append(c)
        if c.route=="undecided":observations.append(PortfolioObservation("route-undecided","Human submission route is still undecided.",(c.relative_path,)))
        if c.copy_space=="unknown":observations.append(PortfolioObservation("copy-space-unknown","Copy-space usefulness has not been reviewed.",(c.relative_path,)))
    for key,items in sorted(groups.items()):
        if len(items)>1:
            paths=tuple(sorted(x.relative_path for x in items));observations.append(PortfolioObservation("subject-cluster","Multiple candidates share the same human subject key; compare them for redundancy and complementary uses.",paths))
            orientations={x.orientation for x in items if x.orientation!="unknown"}
            if len(orientations)==1:observations.append(PortfolioObservation("orientation-concentration","This subject cluster currently has only one reviewed orientation; consider whether another orientation would add genuine utility rather than a duplicate.",paths))
    return tuple(observations)
