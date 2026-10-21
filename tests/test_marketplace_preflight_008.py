import sys,unittest
from datetime import date
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.marketplace_rules import MarketplaceRuleProfile
from stock_photo_scout.marketplace_preflight import assess_marketplace_preflight
from stock_photo_scout.readiness import ReadinessAssessment
class MarketplacePreflight008Tests(unittest.TestCase):
 def profile(self,verified=date(2026,10,21)):return MarketplaceRuleProfile("Example","https://example.com/rules",verified,30)
 def test_ready_core_and_current_rules_can_reach_human_preflight(self):self.assertTrue(assess_marketplace_preflight(ReadinessAssessment(True,()),self.profile(),today=date(2026,10,21)).ready_for_human_preflight)
 def test_stale_rules_block_ready_core(self):
  a=assess_marketplace_preflight(ReadinessAssessment(True,()),self.profile(date(2026,1,1)),today=date(2026,10,21));self.assertFalse(a.ready_for_human_preflight);self.assertTrue(any("stale" in x for x in a.blockers))
 def test_core_blockers_are_preserved(self):
  a=assess_marketplace_preflight(ReadinessAssessment(False,("Rights unresolved.",)),self.profile(),today=date(2026,10,21));self.assertFalse(a.ready_for_human_preflight);self.assertIn("Rights unresolved.",a.blockers)
 def test_false_core_without_blocker_still_fails_closed(self):
  a=assess_marketplace_preflight(ReadinessAssessment(False,()),self.profile(),today=date(2026,10,21));self.assertFalse(a.ready_for_human_preflight);self.assertIn("Core candidate readiness is not explicitly complete.",a.blockers)
if __name__=="__main__":unittest.main()
