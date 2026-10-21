import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.review_intelligence import ReviewIntelligenceRecord
from stock_photo_scout.review_workflow import assess_review_workflow
from stock_photo_scout.stock_usefulness import StockUsefulnessReview,review_complete,usefulness_prompts

def complete_usefulness():return StockUsefulnessReview("clear","clean","right","strong","distinct",False,True,"Human reviewed")
class ReviewWorkflow007Tests(unittest.TestCase):
 def test_unreviewed_stays_stage_one(self):
  a=assess_review_workflow(ReviewIntelligenceRecord("a.jpg"));self.assertEqual(a.stage,"stage-1");self.assertFalse(a.can_shortlist)
 def test_skip_cannot_shortlist(self):self.assertFalse(assess_review_workflow(ReviewIntelligenceRecord("a.jpg",screen_decision="skip")).can_shortlist)
 def test_inspect_fails_closed_without_stage_two_reviews(self):
  a=assess_review_workflow(ReviewIntelligenceRecord("a.jpg",screen_decision="inspect"));self.assertFalse(a.can_shortlist);self.assertGreaterEqual(len(a.blockers),2)
 def test_complete_human_stage_two_can_shortlist(self):
  r=ReviewIntelligenceRecord("a.jpg",screen_decision="inspect",focus_state="looks-clean",composition_state="strong");a=assess_review_workflow(r,complete_usefulness());self.assertTrue(a.can_shortlist);self.assertEqual(a.blockers,())
 def test_focus_concern_blocks_even_with_usefulness_complete(self):
  r=ReviewIntelligenceRecord("a.jpg",screen_decision="inspect",focus_state="concern",composition_state="strong");self.assertFalse(assess_review_workflow(r,complete_usefulness()).can_shortlist)
 def test_grouped_image_must_be_preferred(self):
  r=ReviewIntelligenceRecord("a.jpg",screen_decision="inspect",similar_group_id="g1",preferred_in_group=False,focus_state="looks-clean",composition_state="strong");self.assertFalse(assess_review_workflow(r,complete_usefulness()).can_shortlist)
 def test_grouped_preferred_image_can_continue(self):
  r=ReviewIntelligenceRecord("a.jpg",screen_decision="inspect",similar_group_id="g1",preferred_in_group=True,focus_state="looks-clean",composition_state="strong");self.assertTrue(assess_review_workflow(r,complete_usefulness()).can_shortlist)
 def test_usefulness_unknowns_are_not_silently_complete(self):
  u=StockUsefulnessReview(human_confirmed=True);self.assertFalse(review_complete(u));self.assertTrue(usefulness_prompts(u))
 def test_boolean_confirmation_must_be_literal_bool(self):
  with self.assertRaises(ValueError):review_complete(StockUsefulnessReview(human_confirmed=1))
if __name__=="__main__":unittest.main()
