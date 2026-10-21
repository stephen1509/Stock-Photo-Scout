import sys,unittest
from datetime import date
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.marketplace_rules import MarketplaceRuleProfile
from stock_photo_scout.marketplace_adapter import MarketplaceCandidateFacts,assess_marketplace_candidate
class MarketplaceAdapter008Tests(unittest.TestCase):
 def profile(self,**changes):
  p={"marketplace":"Example Market","source_url":"https://example.invalid/requirements","verified_on":date(2026,10,20),"review_after_days":30};p.update(changes);return MarketplaceRuleProfile(**p)
 def complete(self,**changes):
  p={"route":"commercial","title_present":True,"description_present":True,"keywords_present":True,"rights_review_complete":True,"exact_export_qc_complete":True};p.update(changes);return MarketplaceCandidateFacts(**p)
 def test_complete_facts_with_current_profile_reach_human_preflight(self):
  a=assess_marketplace_candidate(self.profile(),self.complete(),today=date(2026,10,21));self.assertTrue(a.usable_rule_profile);self.assertTrue(a.ready_for_human_marketplace_preflight)
 def test_stale_profile_blocks(self):
  a=assess_marketplace_candidate(self.profile(verified_on=date(2026,1,1),review_after_days=30),self.complete(),today=date(2026,10,21));self.assertFalse(a.ready_for_human_marketplace_preflight)
 def test_unknown_boolean_like_values_fail_closed(self):
  for value in (None,False,1,"true"):
   with self.subTest(value=value):self.assertFalse(assess_marketplace_candidate(self.profile(),self.complete(rights_review_complete=value),today=date(2026,10,21)).ready_for_human_marketplace_preflight)
 def test_undecided_route_blocks(self):
  self.assertFalse(assess_marketplace_candidate(self.profile(),self.complete(route="undecided"),today=date(2026,10,21)).ready_for_human_marketplace_preflight)
if __name__=="__main__":unittest.main()
