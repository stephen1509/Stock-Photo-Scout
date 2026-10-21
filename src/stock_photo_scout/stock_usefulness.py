"""Structured human composition/usefulness review for 0.07.

No field or helper predicts marketplace acceptance. The output is a checklist of
human observations and follow-up prompts, not a score.
"""
from dataclasses import dataclass

CLARITY=("unknown","weak","clear")
CLUTTER=("unknown","clean","some","distracting")
SPACE=("unknown","none","left","right","top","bottom","multiple")
FLEXIBILITY=("unknown","limited","some","strong")
UNIQUENESS=("unknown","redundant","distinct")

@dataclass(frozen=True)
class StockUsefulnessReview:
 subject_clarity:str="unknown"
 background_clutter:str="unknown"
 copy_space:str="unknown"
 crop_flexibility:str="unknown"
 redundancy:str="unknown"
 alternate_orientation_worth_reviewing:bool|None=None
 human_confirmed:bool|None=None
 notes:str=""

def validate_stock_usefulness(r:StockUsefulnessReview)->None:
 if not isinstance(r,StockUsefulnessReview):raise ValueError("review must be StockUsefulnessReview")
 for name,value,allowed in (("subject_clarity",r.subject_clarity,CLARITY),("background_clutter",r.background_clutter,CLUTTER),("copy_space",r.copy_space,SPACE),("crop_flexibility",r.crop_flexibility,FLEXIBILITY),("redundancy",r.redundancy,UNIQUENESS)):
  if value not in allowed:raise ValueError("unsupported "+name)
 if r.alternate_orientation_worth_reviewing is not None and not isinstance(r.alternate_orientation_worth_reviewing,bool):raise ValueError("alternate_orientation_worth_reviewing must be boolean or unknown")
 if r.human_confirmed is not None and not isinstance(r.human_confirmed,bool):raise ValueError("human_confirmed must be boolean or unknown")
 if not isinstance(r.notes,str):raise ValueError("notes must be a string")

def usefulness_prompts(r:StockUsefulnessReview)->tuple[str,...]:
 validate_stock_usefulness(r);out=[]
 if r.subject_clarity=="unknown":out.append("Decide whether the intended subject reads clearly.")
 if r.background_clutter=="unknown":out.append("Review the background for distracting clutter.")
 if r.copy_space=="unknown":out.append("Review whether useful copy/negative space exists.")
 if r.crop_flexibility=="unknown":out.append("Review whether alternate practical crops are available.")
 if r.redundancy=="unknown":out.append("Compare against similar images before deciding portfolio value.")
 if r.subject_clarity=="weak":out.append("Human review marked the subject as weak; compare with stronger alternatives.")
 if r.background_clutter=="distracting":out.append("Human review marked the background as distracting; consider edit/crop or another candidate.")
 if r.redundancy=="redundant":out.append("Human review marked this image redundant; identify the preferred similar candidate.")
 if r.human_confirmed is not True:out.append("Human composition/usefulness review is not explicitly confirmed.")
 return tuple(out)

def review_complete(r:StockUsefulnessReview)->bool:
 validate_stock_usefulness(r)
 return r.human_confirmed is True and all(v!="unknown" for v in (r.subject_clarity,r.background_clutter,r.copy_space,r.crop_flexibility,r.redundancy))
