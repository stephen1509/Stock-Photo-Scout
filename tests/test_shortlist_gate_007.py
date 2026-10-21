import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.review_service import ReviewService
from stock_photo_scout.review_intelligence import ReviewIntelligenceRecord
from stock_photo_scout.stock_usefulness import StockUsefulnessReview
from stock_photo_scout.shortlist_gate import assess_workspace_transition
class ShortlistGate007Tests(unittest.TestCase):
 def setup(self,td):
  root=Path(td);source=root/"photos";source.mkdir();return ReviewService(source,root/"reviews")
 def test_legacy_shortlist_selection_fails_closed_without_review(self):
  with tempfile.TemporaryDirectory() as td:self.assertFalse(assess_workspace_transition(self.setup(td),"a.jpg","shortlist").allowed)
 def test_review_qualified_candidate_can_shortlist(self):
  with tempfile.TemporaryDirectory() as td:
   s=self.setup(td);s.save("a.jpg",ReviewIntelligenceRecord("a.jpg",screen_decision="inspect",focus_state="looks-clean",composition_state="strong"),StockUsefulnessReview("clear","clean","right","strong","distinct",False,True,""));g=assess_workspace_transition(s,"a.jpg","shortlist");self.assertTrue(g.allowed);self.assertTrue(g.authoritative_review_complete)
 def test_non_shortlist_legacy_states_are_not_claimed_review_complete(self):
  with tempfile.TemporaryDirectory() as td:
   g=assess_workspace_transition(self.setup(td),"a.jpg","edit");self.assertTrue(g.allowed);self.assertFalse(g.authoritative_review_complete)
if __name__=="__main__":unittest.main()
