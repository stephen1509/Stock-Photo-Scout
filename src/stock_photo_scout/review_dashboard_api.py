"""Validated localhost-dashboard adapter for 0.07 review state.

Keeps HTTP/UI payload parsing separate from persistence and review semantics.
"""
from .review_intelligence import ReviewIntelligenceRecord,SCREEN_DECISIONS,FOCUS_STATES,COMPOSITION_STATES,REASON_CODES
from .stock_usefulness import StockUsefulnessReview,CLARITY,CLUTTER,SPACE,FLEXIBILITY,UNIQUENESS
from .review_service import ReviewService

def _optional_bool(value,name):
 if value is None or isinstance(value,bool):return value
 raise ValueError(name+" must be boolean or null.")
def _text(payload,name,default=""):
 value=payload.get(name,default)
 if not isinstance(value,str):raise ValueError(name+" must be text.")
 return value
def _choice(payload,name,allowed,default):
 value=_text(payload,name,default)
 if value not in allowed:raise ValueError("Unsupported "+name+".")
 return value

def load_review_payload(service:ReviewService,payload:dict):
 if not isinstance(payload,dict):raise ValueError("Review request must be an object.")
 relative_path=_text(payload,"relative_path")
 if not relative_path:raise ValueError("relative_path is required.")
 return service.load(relative_path)

def save_review_payload(service:ReviewService,payload:dict):
 if not isinstance(payload,dict):raise ValueError("Review request must be an object.")
 relative_path=_text(payload,"relative_path")
 if not relative_path:raise ValueError("relative_path is required.")
 reasons=payload.get("reason_codes",[])
 if not isinstance(reasons,list) or not all(isinstance(x,str) for x in reasons):raise ValueError("reason_codes must be a list of strings.")
 if len(set(reasons))!=len(reasons) or any(x not in REASON_CODES for x in reasons):raise ValueError("reason_codes contain unsupported or duplicate values.")
 review=ReviewIntelligenceRecord(relative_path=relative_path,screen_decision=_choice(payload,"screen_decision",SCREEN_DECISIONS,"unreviewed"),reason_codes=tuple(reasons),similar_group_id=_text(payload,"similar_group_id"),preferred_in_group=_optional_bool(payload.get("preferred_in_group"),"preferred_in_group"),focus_state=_choice(payload,"focus_state",FOCUS_STATES,"unknown"),subject_note=_text(payload,"subject_note"),composition_state=_choice(payload,"composition_state",COMPOSITION_STATES,"unknown"),copy_space=_optional_bool(payload.get("copy_space"),"copy_space"),alternate_crop_worth_reviewing=_optional_bool(payload.get("alternate_crop_worth_reviewing"),"alternate_crop_worth_reviewing"),notes=_text(payload,"notes"))
 usefulness=StockUsefulnessReview(subject_clarity=_choice(payload,"subject_clarity",CLARITY,"unknown"),background_clutter=_choice(payload,"background_clutter",CLUTTER,"unknown"),copy_space=_choice(payload,"usefulness_copy_space",SPACE,"unknown"),crop_flexibility=_choice(payload,"crop_flexibility",FLEXIBILITY,"unknown"),redundancy=_choice(payload,"redundancy",UNIQUENESS,"unknown"),alternate_orientation_worth_reviewing=_optional_bool(payload.get("alternate_orientation_worth_reviewing"),"alternate_orientation_worth_reviewing"),human_confirmed=_optional_bool(payload.get("human_confirmed"),"human_confirmed"),notes=_text(payload,"usefulness_notes"))
 return service.save(relative_path,review,usefulness)
