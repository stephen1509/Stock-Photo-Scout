import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.review_service import ReviewService
from stock_photo_scout.review_dashboard_api import load_review_payload,save_review_payload
class ReviewDashboardApi007Tests(unittest.TestCase):
 def service(self,td):
  root=Path(td);source=root/"photos";source.mkdir();return ReviewService(source,root/"reviews")
 def test_load_requires_candidate(self):
  with tempfile.TemporaryDirectory() as td:
   with self.assertRaises(ValueError):load_review_payload(self.service(td),{})
 def test_complete_payload_can_qualify_stage_two(self):
  with tempfile.TemporaryDirectory() as td:
   s=self.service(td);x=save_review_payload(s,{"relative_path":"a.jpg","screen_decision":"inspect","focus_state":"looks-clean","composition_state":"strong","subject_clarity":"clear","background_clutter":"clean","usefulness_copy_space":"right","crop_flexibility":"strong","redundancy":"distinct","human_confirmed":True});self.assertTrue(x["assessment"]["can_shortlist"])
 def test_malformed_boolean_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   with self.assertRaises(ValueError):save_review_payload(self.service(td),{"relative_path":"a.jpg","human_confirmed":1})
 def test_duplicate_and_unknown_reason_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   s=self.service(td)
   for reasons in (["needs-edit","needs-edit"],["magic-score"]):
    with self.subTest(reasons=reasons),self.assertRaises(ValueError):save_review_payload(s,{"relative_path":"a.jpg","reason_codes":reasons})
 def test_group_preference_without_group_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   with self.assertRaises(ValueError):save_review_payload(self.service(td),{"relative_path":"a.jpg","preferred_in_group":True})
 def test_hostile_path_rejected_by_service_model(self):
  with tempfile.TemporaryDirectory() as td:
   with self.assertRaises(ValueError):save_review_payload(self.service(td),{"relative_path":"../secret.jpg"})
if __name__=="__main__":unittest.main()
