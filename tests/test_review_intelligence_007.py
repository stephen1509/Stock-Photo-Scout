import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.review_intelligence import ReviewIntelligenceRecord,can_enter_shortlist_review,review_prompts,validate_review_intelligence
class ReviewIntelligence007Tests(unittest.TestCase):
 def test_default_is_unknown_and_prompts_human(self):
  r=ReviewIntelligenceRecord("photo.jpg");self.assertFalse(can_enter_shortlist_review(r));self.assertTrue(any("fast-screen" in x for x in review_prompts(r)))
 def test_inspect_requires_human_focus_and_composition_review(self):
  p=review_prompts(ReviewIntelligenceRecord("photo.jpg",screen_decision="inspect"));self.assertTrue(any("focus" in x for x in p));self.assertTrue(any("composition" in x for x in p))
 def test_inspect_is_workflow_gate_not_quality_score(self):self.assertTrue(can_enter_shortlist_review(ReviewIntelligenceRecord("photo.jpg",screen_decision="inspect")))
 def test_similar_group_preference_requires_group(self):
  with self.assertRaises(ValueError):validate_review_intelligence(ReviewIntelligenceRecord("photo.jpg",preferred_in_group=True))
 def test_group_prompts_for_human_preference(self):self.assertTrue(any("similar/burst" in x for x in review_prompts(ReviewIntelligenceRecord("photo.jpg",similar_group_id="burst-1"))))
 def test_unknown_and_duplicate_reason_codes_fail_closed(self):
  for codes in (("magic-score",),("needs-edit","needs-edit")):
   with self.subTest(codes=codes),self.assertRaises(ValueError):validate_review_intelligence(ReviewIntelligenceRecord("photo.jpg",reason_codes=codes))
 def test_windows_unc_and_traversal_paths_rejected(self):
  for p in (r"C:\\photo.jpg",r"\\server\\share\\photo.jpg","../photo.jpg"):
   with self.subTest(p=p),self.assertRaises(ValueError):validate_review_intelligence(ReviewIntelligenceRecord(p))
 def test_focus_concern_requests_actual_pixel_review(self):self.assertTrue(any("actual pixels" in x for x in review_prompts(ReviewIntelligenceRecord("photo.jpg",screen_decision="inspect",focus_state="concern",composition_state="usable"))))
if __name__=="__main__":unittest.main()
