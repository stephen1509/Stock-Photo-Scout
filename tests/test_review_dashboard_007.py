import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.review_dashboard import ReviewDashboardController,REVIEW_PAGE
class ReviewDashboard007Tests(unittest.TestCase):
 def service(self,td):
  root=Path(td);source=root/"photos";source.mkdir();return ReviewDashboardController(source,root/"reviews")
 def test_default_load_fails_closed(self):
  with tempfile.TemporaryDirectory() as td:
   c=self.service(td);x=c.load({"relative_path":"a.jpg"});self.assertFalse(x["assessment"]["can_shortlist"])
 def test_complete_human_payload_can_qualify_review(self):
  with tempfile.TemporaryDirectory() as td:
   c=self.service(td);x=c.save({"relative_path":"a.jpg","screen_decision":"inspect","focus_state":"looks-clean","composition_state":"strong","copy_space":True,"alternate_crop_worth_reviewing":False,"notes":"Human review","subject_clarity":"clear","background_clutter":"clean","usefulness_copy_space":"right","crop_flexibility":"strong","redundancy":"distinct","alternate_orientation_worth_reviewing":True,"human_confirmed":True,"usefulness_notes":"Reviewed"});self.assertTrue(x["assessment"]["can_shortlist"]);self.assertTrue(x["review"]["copy_space"]);self.assertTrue(x["usefulness"]["alternate_orientation_worth_reviewing"])
 def test_workspace_shortlist_alone_is_not_authoritative(self):
  with tempfile.TemporaryDirectory() as td:
   c=self.service(td);x=c.shortlist_status("a.jpg","shortlist");self.assertFalse(x["authoritative_shortlist"])
 def test_qualified_review_plus_shortlist_is_authoritative(self):
  with tempfile.TemporaryDirectory() as td:
   c=self.service(td);c.save({"relative_path":"a.jpg","screen_decision":"inspect","focus_state":"looks-clean","composition_state":"strong","subject_clarity":"clear","background_clutter":"clean","usefulness_copy_space":"right","crop_flexibility":"strong","redundancy":"distinct","human_confirmed":True});self.assertTrue(c.shortlist_status("a.jpg","shortlist")["authoritative_shortlist"])
 def test_page_exposes_full_human_review_surface_without_innerhtml(self):
  for field in ("copy_space","alternate_crop_worth_reviewing","notes","alternate_orientation_worth_reviewing","usefulness_notes"):self.assertIn("id="+field,REVIEW_PAGE)
  self.assertIn("assessment.textContent",REVIEW_PAGE);self.assertNotIn("innerHTML",REVIEW_PAGE);self.assertIn("No stock score or marketplace-acceptance prediction",REVIEW_PAGE)
if __name__=="__main__":unittest.main()
