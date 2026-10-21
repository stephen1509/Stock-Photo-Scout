"""Local service layer composing persistent 0.07 human review state."""
from dataclasses import asdict
import hashlib
from pathlib import Path
from .review_intelligence import ReviewIntelligenceRecord,validate_review_intelligence
from .review_store import load_review
from .stock_usefulness import StockUsefulnessReview,validate_stock_usefulness
from .usefulness_store import load_usefulness
from .review_packet_store import load_packet,save_packet
from .review_workflow import assess_review_workflow
class ReviewService:
 def __init__(self,source_root:str|Path,review_directory:str|Path):
  self.source_root=Path(source_root).expanduser().resolve(strict=True);self.review_directory=Path(review_directory).expanduser().resolve(strict=False)
  if self.review_directory.is_relative_to(self.source_root):raise ValueError("Review directory must be outside the source-photo folder.")
 def _stem(self,relative_path:str)->str:return hashlib.sha256(relative_path.encode("utf-8")).hexdigest()[:24]
 def _paths(self,relative_path:str):
  validate_review_intelligence(ReviewIntelligenceRecord(relative_path));s=self._stem(relative_path);return self.review_directory/(s+".review-packet.json"),self.review_directory/(s+".review.json"),self.review_directory/(s+".usefulness.json")
 def load(self,relative_path:str):
  packet,rp,up=self._paths(relative_path)
  if packet.exists():review,usefulness=load_packet(packet)
  else:review=load_review(rp) if rp.exists() else ReviewIntelligenceRecord(relative_path);usefulness=load_usefulness(up) if up.exists() else StockUsefulnessReview()
  if review.relative_path!=relative_path:raise ValueError("Persisted review candidate path mismatch.")
  assessment=assess_review_workflow(review,usefulness)
  return {"review":asdict(review),"usefulness":asdict(usefulness),"assessment":{"stage":assessment.stage,"can_shortlist":assessment.can_shortlist,"blockers":list(assessment.blockers),"prompts":list(assessment.prompts)}}
 def save(self,relative_path:str,review:ReviewIntelligenceRecord,usefulness:StockUsefulnessReview):
  if review.relative_path!=relative_path:raise ValueError("Review candidate path mismatch.")
  validate_review_intelligence(review);validate_stock_usefulness(usefulness);packet,_,_=self._paths(relative_path);save_packet(review,usefulness,packet,self.source_root,overwrite=packet.exists());return self.load(relative_path)
