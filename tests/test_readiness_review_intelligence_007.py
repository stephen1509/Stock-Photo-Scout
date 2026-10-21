import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.candidate_review import CandidateReviewRecord
from stock_photo_scout.rights_review import RightsReview
from stock_photo_scout.final_qc import FinalQcRecord
from stock_photo_scout.readiness import assess_readiness

SHA="a"*64
class ReadinessReviewIntelligence007Tests(unittest.TestCase):
 def base(self,**changes):
  args=dict(review=CandidateReviewRecord(technical_state="passed",stock_potential="promising",rights_state="reviewed",route="commercial",preparation_state="complete"),rights=RightsReview(*(["none-seen"]*9)),provenance_current=True,current_marketplace_requirements_reviewed=True,final_qc=FinalQcRecord(SHA,True,True,(),"checked"),current_export_sha256=SHA)
  args.update(changes);return assess_readiness(**args)
 def test_old_callers_fail_closed_without_007_review(self):
  r=self.base();self.assertFalse(r.ready);self.assertIn("0.07 human review intelligence is not explicitly complete.",r.blockers)
 def test_false_and_none_do_not_pass(self):
  for value in (False,None,1,"true"):
   with self.subTest(value=value):self.assertFalse(self.base(review_intelligence_complete=value).ready)
 def test_literal_true_allows_other_complete_gates(self):
  self.assertTrue(self.base(review_intelligence_complete=True).ready)
 def test_007_does_not_override_other_blockers(self):
  r=self.base(review_intelligence_complete=True,provenance_current=False);self.assertFalse(r.ready);self.assertIn("Source/export provenance is not explicitly current.",r.blockers)
if __name__=="__main__":unittest.main()
