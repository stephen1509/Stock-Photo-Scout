import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.candidate_review import CandidateReviewRecord,readiness_blockers
from stock_photo_scout.final_qc import FinalQcRecord,final_qc_blockers,plan_100_percent_crops
from stock_photo_scout.readiness import assess_readiness
from stock_photo_scout.rights_review import RightsReview,rights_blockers
SHA_A="a"*64;SHA_B="b"*64
class ReliabilityQcTests(unittest.TestCase):
 def ready_review(self):return CandidateReviewRecord("photo.jpg","candidate","pass","strong","clear-looking","commercial","ready")
 def clear_rights(self):return RightsReview(*(["none-seen"]*9))
 def clear_final_qc(self):return FinalQcRecord(SHA_A,True,True,(),"Inspected exact final export locally")
 def ready(self,**changes):
  args=dict(review=self.ready_review(),rights=self.clear_rights(),provenance_current=True,final_qc=self.clear_final_qc(),current_export_sha256=SHA_A,current_marketplace_requirements_reviewed=True,review_intelligence_complete=True);args.update(changes);return assess_readiness(**args)
 def test_default_review_fails_closed(self):self.assertGreaterEqual(len(readiness_blockers(CandidateReviewRecord("photo.jpg"))),6)
 def test_default_rights_fails_closed(self):self.assertGreater(len(rights_blockers(RightsReview())),5)
 def test_all_explicit_gates_can_be_ready(self):self.assertTrue(self.ready().ready)
 def test_route_review_cannot_be_reused_for_different_final_route(self):
  values=["none-seen"]*9;values[4]="reviewed";rights=RightsReview(*values,reviewed_route="editorial");result=self.ready(rights=rights);self.assertFalse(result.ready);self.assertTrue(any("selected submission route" in x for x in result.blockers))
 def test_old_boolean_final_qc_cannot_make_candidate_ready(self):
  result=assess_readiness(review=self.ready_review(),rights=self.clear_rights(),provenance_current=True,final_qc_confirmed=True,current_marketplace_requirements_reviewed=True,review_intelligence_complete=True);self.assertFalse(result.ready);self.assertTrue(any("exact-file QC" in x for x in result.blockers))
 def test_unknown_boolean_gates_fail_closed(self):self.assertFalse(assess_readiness(review=self.ready_review(),rights=self.clear_rights(),provenance_current=None,final_qc=None,current_marketplace_requirements_reviewed=None,review_intelligence_complete=None).ready)
 def test_changed_export_invalidates_qc(self):self.assertTrue(any("changed" in x for x in final_qc_blockers(self.clear_final_qc(),current_export_sha256=SHA_B)))
 def test_unresolved_defect_blocks_readiness(self):self.assertTrue(any("unresolved defect" in x for x in final_qc_blockers(FinalQcRecord(SHA_A,True,True,("focus",),"Needs another look"),current_export_sha256=SHA_A)))
 def test_unknown_defect_code_fails_closed(self):self.assertTrue(any("unsupported" in x for x in final_qc_blockers(FinalQcRecord(SHA_A,True,True,("magic-ai-score",),""),current_export_sha256=SHA_A)))
 def test_windows_and_unc_candidate_paths_rejected(self):
  for p in (r"C:\\photo.jpg",r"\\server\\share\\photo.jpg","../photo.jpg"):
   with self.subTest(p=p),self.assertRaises(ValueError):readiness_blockers(CandidateReviewRecord(p))
 def test_large_image_gets_five_actual_pixel_crops(self):self.assertEqual(len(plan_100_percent_crops(6000,4000)),5)
 def test_small_image_deduplicates_crop(self):self.assertEqual(len(plan_100_percent_crops(800,600)),1)
if __name__=="__main__":unittest.main()
