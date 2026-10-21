import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.candidate_dashboard import CandidateDashboard,CandidateDashboardSettings
from stock_photo_scout.review_intelligence import ReviewIntelligenceRecord
from stock_photo_scout.stock_usefulness import StockUsefulnessReview
class CandidateDashboardIntegration007Tests(unittest.TestCase):
 def dashboard(self,root):
  source=root/"photos";source.mkdir();drafts=root/"drafts";drafts.mkdir();return CandidateDashboard(CandidateDashboardSettings.create(source,drafts,drafts/"dict.json",root/"previews",root/"workspace.json",root/"prep",root/"analysis",root/"reviews"))
 def complete_review(self,rel):return ReviewIntelligenceRecord(relative_path=rel,screen_decision="inspect",focus_state="looks-clean",composition_state="strong")
 def complete_usefulness(self):return StockUsefulnessReview(subject_clarity="clear",background_clutter="clean",copy_space="left",crop_flexibility="strong",redundancy="distinct",human_confirmed=True)
 def test_shortlist_fails_closed_until_review_qualifies(self):
  with tempfile.TemporaryDirectory() as td:
   d=self.dashboard(Path(td))
   with self.assertRaises(ValueError):d.set_state({"relative_path":"a.jpg","state":"shortlist"})
   d.reviews.save("a.jpg",self.complete_review("a.jpg"),self.complete_usefulness());r=d.set_state({"relative_path":"a.jpg","state":"shortlist"});self.assertTrue(r["authoritative_review_complete"]);self.assertTrue(d.list_candidates()[0]["authoritative_shortlist"])
 def test_review_directory_cannot_be_inside_source(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);source=root/"photos";source.mkdir();drafts=root/"drafts"
   with self.assertRaises(ValueError):CandidateDashboardSettings.create(source,drafts,drafts/"dict.json",root/"p",root/"w.json",root/"prep",root/"analysis",source/"reviews")
 def test_category_pairs_round_trip_without_field_shift(self):
  with tempfile.TemporaryDirectory() as td:
   d=self.dashboard(Path(td));saved=d.save_preparation({"relative_path":"a.jpg","title":"T","description":"D","keywords":["one"],"categories":["travel"],"category_pairs":[{"category":"Travel","subcategory":"Asia"}],"route":"editorial","editor_target":"gimp","working_export_relative_path":"exports/a.jpg","notes":"N"});p=saved["preparation"];self.assertEqual(p["category_pairs"],[{"category":"Travel","subcategory":"Asia"}]);self.assertEqual((p["route"],p["editor_target"]),("editorial","gimp"))
if __name__=="__main__":unittest.main()
