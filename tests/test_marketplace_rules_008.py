import sys,unittest
from datetime import date
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.marketplace_rules import MarketplaceRuleProfile,assess_rule_profile
class MarketplaceRules008Tests(unittest.TestCase):
 def test_blank_profile_fails_closed(self):
  a=assess_rule_profile(MarketplaceRuleProfile("",""),today=date(2026,10,21));self.assertFalse(a.usable);self.assertFalse(a.stale)
 def test_verified_current_profile_is_usable(self):
  p=MarketplaceRuleProfile("Example","https://example.com/requirements",date(2026,10,1),30);a=assess_rule_profile(p,today=date(2026,10,21));self.assertTrue(a.usable);self.assertFalse(a.stale)
 def test_stale_profile_fails_closed(self):
  p=MarketplaceRuleProfile("Example","https://example.com/requirements",date(2026,8,1),30);a=assess_rule_profile(p,today=date(2026,10,21));self.assertFalse(a.usable);self.assertTrue(a.stale)
 def test_http_source_is_not_accepted(self):
  p=MarketplaceRuleProfile("Example","http://example.com/requirements",date(2026,10,1),30);self.assertFalse(assess_rule_profile(p,today=date(2026,10,21)).usable)
 def test_future_verification_date_fails_closed(self):
  p=MarketplaceRuleProfile("Example","https://example.com/requirements",date(2026,10,22),30);self.assertFalse(assess_rule_profile(p,today=date(2026,10,21)).usable)
 def test_boolean_horizon_is_rejected(self):
  p=MarketplaceRuleProfile("Example","https://example.com/requirements",date(2026,10,1),True);self.assertFalse(assess_rule_profile(p,today=date(2026,10,21)).usable)
if __name__=="__main__":unittest.main()
