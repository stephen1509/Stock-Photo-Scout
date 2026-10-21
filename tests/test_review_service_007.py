import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.review_intelligence import ReviewIntelligenceRecord
from stock_photo_scout.stock_usefulness import StockUsefulnessReview
from stock_photo_scout.review_service import ReviewService
class ReviewService007Tests(unittest.TestCase):
 def test_default_load_is_fail_closed(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);source=root/"photos";source.mkdir();s=ReviewService(source,root/"reviews");x=s.load("a.jpg");self.assertEqual(x["assessment"]["stage"],"stage-1");self.assertFalse(x["assessment"]["can_shortlist"])
 def test_complete_human_review_round_trip(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);source=root/"photos";source.mkdir();s=ReviewService(source,root/"reviews");r=ReviewIntelligenceRecord("a.jpg",screen_decision="inspect",focus_state="looks-clean",composition_state="strong");u=StockUsefulnessReview("clear","clean","right","strong","distinct",False,True,"reviewed");x=s.save("a.jpg",r,u);self.assertTrue(x["assessment"]["can_shortlist"]);self.assertEqual(s.load("a.jpg")["review"]["screen_decision"],"inspect")
 def test_path_mismatch_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);source=root/"photos";source.mkdir();s=ReviewService(source,root/"reviews")
   with self.assertRaises(ValueError):s.save("a.jpg",ReviewIntelligenceRecord("b.jpg"),StockUsefulnessReview())
 def test_review_directory_inside_source_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);source=root/"photos";source.mkdir()
   with self.assertRaises(ValueError):ReviewService(source,source/"reviews")
if __name__=="__main__":unittest.main()
