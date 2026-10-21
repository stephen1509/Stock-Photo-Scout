import sys,tempfile,unittest
from datetime import date
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.rejection_learning import MarketplaceOutcome,outcome_from_json,outcome_to_json,save_outcome
class RejectionLearning008Tests(unittest.TestCase):
 def record(self,**changes):
  p={"relative_path":"trip/a.jpg","marketplace":"Example Market","outcome":"rejected","recorded_on":date(2026,10,21),"reason_codes":("focus",),"notes":"Human-recorded marketplace response."};p.update(changes);return MarketplaceOutcome(**p)
 def test_round_trip(self):self.assertEqual(outcome_from_json(outcome_to_json(self.record())),self.record())
 def test_unknown_outcome_rejected(self):
  with self.assertRaises(ValueError):self.record(outcome="probably-accepted")
 def test_duplicate_reason_codes_rejected(self):
  with self.assertRaises(ValueError):self.record(reason_codes=("focus","FOCUS"))
 def test_windows_traversal_rejected(self):
  for p in ("../x.jpg","C:\\x.jpg","\\\\server\\x.jpg"):
   with self.subTest(p=p),self.assertRaises(ValueError):self.record(relative_path=p)
 def test_state_cannot_be_saved_inside_source_tree(self):
  with tempfile.TemporaryDirectory() as td:
   source=Path(td)/"photos";source.mkdir()
   with self.assertRaises(ValueError):save_outcome(self.record(),source/"outcome.json",source)
 def test_external_save_is_durable_and_parseable(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);source=root/"photos";source.mkdir();dest=root/"state"/"outcome.json";save_outcome(self.record(),dest,source);self.assertEqual(outcome_from_json(dest.read_text(encoding="utf-8")),self.record())
if __name__=="__main__":unittest.main()
