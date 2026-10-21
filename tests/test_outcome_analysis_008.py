import sys,unittest
from datetime import date
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.rejection_learning import MarketplaceOutcome
from stock_photo_scout.outcome_analysis import summarize_outcomes
class OutcomeAnalysis008Tests(unittest.TestCase):
 def r(self,path,outcome,reasons=(),market="Dreamstime"):return MarketplaceOutcome(path,market,outcome,date(2026,10,21),reasons,"")
 def test_empty_history_is_explicit(self):
  s=summarize_outcomes((),"Dreamstime");self.assertEqual(s.total,0);self.assertIn("No human-recorded outcomes",s.observations[0])
 def test_counts_only_selected_marketplace(self):
  s=summarize_outcomes((self.r("a.jpg","accepted"),self.r("b.jpg","rejected",("focus",)),self.r("c.jpg","accepted",market="Other")),"dreamstime");self.assertEqual((s.total,s.accepted,s.rejected),(2,1,1));self.assertEqual(s.rejection_reason_counts,(("focus",1),))
 def test_pending_is_not_folded_into_decision(self):
  s=summarize_outcomes((self.r("a.jpg","pending"),),"Dreamstime");self.assertEqual((s.accepted,s.rejected,s.pending),(0,0,1));self.assertTrue(any("still pending" in x for x in s.observations))
 def test_reason_observation_disclaims_prediction(self):
  s=summarize_outcomes((self.r("a.jpg","rejected",("focus",)),self.r("b.jpg","rejected",("focus","noise"))),"Dreamstime");self.assertTrue(any("not a prediction" in x for x in s.observations))
if __name__=="__main__":unittest.main()
