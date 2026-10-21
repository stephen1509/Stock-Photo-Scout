import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.stock_usefulness import StockUsefulnessReview,review_complete,usefulness_prompts,validate_stock_usefulness
class StockUsefulness007Tests(unittest.TestCase):
 def test_default_is_incomplete_and_prompted(self):
  r=StockUsefulnessReview();self.assertFalse(review_complete(r));self.assertGreaterEqual(len(usefulness_prompts(r)),5)
 def test_complete_review_has_no_required_prompts(self):
  r=StockUsefulnessReview("clear","clean","left","some","distinct",False,True,"");self.assertTrue(review_complete(r));self.assertEqual(usefulness_prompts(r),())
 def test_weak_human_observations_generate_explainable_prompts(self):
  r=StockUsefulnessReview("weak","distracting","none","limited","redundant",False,True,"");p=usefulness_prompts(r);self.assertTrue(any("subject" in x for x in p));self.assertTrue(any("background" in x for x in p));self.assertTrue(any("redundant" in x for x in p))
 def test_no_aggregate_score_exists(self):self.assertFalse(hasattr(StockUsefulnessReview(),"score"))
 def test_invalid_values_fail_closed(self):
  with self.assertRaises(ValueError):validate_stock_usefulness(StockUsefulnessReview(subject_clarity="excellent-97-percent"))
if __name__=="__main__":unittest.main()
