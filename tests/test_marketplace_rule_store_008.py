import sys,tempfile,unittest
from datetime import date
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.marketplace_rules import MarketplaceRuleProfile
from stock_photo_scout.marketplace_rule_store import load_and_assess,load_profile,profile_from_json,profile_to_json,save_profile
class MarketplaceRuleStore008Tests(unittest.TestCase):
 def profile(self):return MarketplaceRuleProfile("Example","https://example.com/rules",date(2026,10,21),30,"Human verified")
 def test_round_trip(self):self.assertEqual(profile_from_json(profile_to_json(self.profile())),self.profile())
 def test_persist_and_assess(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"rules.json";save_profile(self.profile(),p);profile,a=load_and_assess(p,today=date(2026,10,21));self.assertEqual(profile,self.profile());self.assertTrue(a.usable)
 def test_stale_profile_remains_fail_closed_after_load(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"rules.json";save_profile(MarketplaceRuleProfile("Example","https://example.com/rules",date(2026,1,1),30),p);_,a=load_and_assess(p,today=date(2026,10,21));self.assertFalse(a.usable);self.assertTrue(a.stale)
 def test_unknown_fields_rejected(self):
  bad='{"schema_version":1,"profile":{"marketplace":"X","source_url":"https://example.com","surprise":true}}'
  with self.assertRaises(ValueError):profile_from_json(bad)
 def test_symlink_destination_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);real=root/"real.json";real.write_text("keep");link=root/"link.json"
   try:link.symlink_to(real)
   except (OSError,NotImplementedError):self.skipTest("symlinks unavailable")
   with self.assertRaises(ValueError):save_profile(self.profile(),link,overwrite=True)
   self.assertEqual(real.read_text(),"keep")
 def test_symlink_parent_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);real=root/"real";real.mkdir();link=root/"linked"
   try:link.symlink_to(real,target_is_directory=True)
   except (OSError,NotImplementedError):self.skipTest("symlinks unavailable")
   with self.assertRaises(ValueError):save_profile(self.profile(),link/"rules.json")
if __name__=="__main__":unittest.main()
