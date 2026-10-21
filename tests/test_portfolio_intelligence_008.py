import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.portfolio_intelligence import PortfolioCandidate,portfolio_observations
class PortfolioIntelligence008Tests(unittest.TestCase):
 def test_empty_portfolio_has_no_invented_advice(self):self.assertEqual(portfolio_observations(()),())
 def test_unknown_human_fields_are_prompted(self):
  x=portfolio_observations((PortfolioCandidate("a.jpg"),));codes={o.code for o in x};self.assertIn("route-undecided",codes);self.assertIn("copy-space-unknown",codes)
 def test_same_subject_is_explainable_cluster_not_score(self):
  x=portfolio_observations((PortfolioCandidate("b.jpg","temple","landscape","editorial","left"),PortfolioCandidate("a.jpg","Temple","landscape","editorial","right")));codes={o.code for o in x};self.assertIn("subject-cluster",codes);self.assertIn("orientation-concentration",codes);self.assertFalse(any("score" in o.code for o in x))
 def test_mixed_orientation_avoids_concentration_prompt(self):
  x=portfolio_observations((PortfolioCandidate("a.jpg","deer","landscape","editorial","left"),PortfolioCandidate("b.jpg","deer","portrait","editorial","right")));self.assertNotIn("orientation-concentration",{o.code for o in x})
 def test_duplicate_paths_rejected(self):
  with self.assertRaises(ValueError):portfolio_observations((PortfolioCandidate("a.jpg"),PortfolioCandidate("a.jpg")))
if __name__=="__main__":unittest.main()
