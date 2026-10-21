"""Explainable analysis of human-recorded marketplace outcomes.

This module summarizes factual history. It does not predict acceptance, rank
photos, or automatically change QC thresholds.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from .rejection_learning import MarketplaceOutcome
@dataclass(frozen=True)
class OutcomeSummary:
 marketplace:str
 total:int
 accepted:int
 rejected:int
 withdrawn:int
 pending:int
 rejection_reason_counts:tuple[tuple[str,int],...]
 observations:tuple[str,...]
def summarize_outcomes(records:tuple[MarketplaceOutcome,...],marketplace:str)->OutcomeSummary:
 if not isinstance(records,tuple):raise ValueError("records must be a tuple")
 if not isinstance(marketplace,str) or not marketplace.strip():raise ValueError("marketplace is required")
 selected=[]
 for r in records:
  if not isinstance(r,MarketplaceOutcome):raise ValueError("records must contain MarketplaceOutcome values")
  if r.marketplace.casefold()==marketplace.casefold():selected.append(r)
 counts=Counter(r.outcome for r in selected);reasons=Counter(code for r in selected if r.outcome=="rejected" for code in r.reason_codes);obs=[]
 if not selected:obs.append("No human-recorded outcomes exist for this marketplace yet.")
 if counts["pending"]:obs.append(f"{counts['pending']} outcome(s) are still pending; do not treat them as accepted or rejected.")
 if reasons:
  top=max(reasons.values());leaders=sorted(k for k,v in reasons.items() if v==top);obs.append("Most frequently recorded rejection reason(s): "+", ".join(leaders)+". This is historical evidence, not a prediction.")
 return OutcomeSummary(marketplace,len(selected),counts["accepted"],counts["rejected"],counts["withdrawn"],counts["pending"],tuple(sorted(reasons.items())),tuple(obs))
