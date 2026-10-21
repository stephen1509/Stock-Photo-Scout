import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.candidate_review import CandidateReviewRecord,readiness_blockers
from stock_photo_scout.final_qc import plan_100_percent_crops
from stock_photo_scout.readiness import assess_readiness
from stock_photo_scout.rights_review import RightsReview,rights_blockers
class ReliabilityQcTests(unittest.TestCase):
 def ready_review(self): return CandidateReviewRecord("photo.jpg","candidate","pass","strong","clear-looking","commercial","ready")
 def clear_rights(self): return RightsReview(*(["none-seen"]*9))
 def test_default_review_fails_closed(self): self.assertGreaterEqual(len(readiness_blockers(CandidateReviewRecord("photo.jpg"))),6)
 def test_default_rights_fails_closed(self): self.assertGreater(len(rights_blockers(RightsReview())),5)
 def test_all_explicit_gates_can_be_ready(self): self.assertTrue(assess_readiness(review=self.ready_review(),rights=self.clear_rights(),provenance_current=True,final_qc_confirmed=True,current_marketplace_requirements_reviewed=True).ready)
 def test_unknown_boolean_gates_fail_closed(self): self.assertFalse(assess_readiness(review=self.ready_review(),rights=self.clear_rights(),provenance_current=None,final_qc_confirmed=None,current_marketplace_requirements_reviewed=None).ready)
 def test_windows_and_unc_candidate_paths_rejected(self):
  for p in (r"C:\\photo.jpg",r"\\server\\share\\photo.jpg","../photo.jpg"):
   with self.subTest(p=p),self.assertRaises(ValueError): readiness_blockers(CandidateReviewRecord(p))
 def test_large_image_gets_five_actual_pixel_crops(self): self.assertEqual(len(plan_100_percent_crops(6000,4000)),5)
 def test_small_image_deduplicates_crop(self): self.assertEqual(len(plan_100_percent_crops(800,600)),1)
if __name__=="__main__": unittest.main()
