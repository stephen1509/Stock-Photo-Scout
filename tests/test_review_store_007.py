import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.review_intelligence import ReviewIntelligenceRecord
from stock_photo_scout.review_store import load_review,review_from_json,review_to_json,save_review
class ReviewStore007Tests(unittest.TestCase):
 def test_round_trip(self):
  r=ReviewIntelligenceRecord("奈良/photo.jpg","inspect",("promising-subject",),"g1",True,"looks-clean","deer","strong",True,False,"human note")
  self.assertEqual(review_from_json(review_to_json(r)),r)
 def test_unknown_fields_fail_closed(self):
  p=json.loads(review_to_json(ReviewIntelligenceRecord("a.jpg")));p["review"]["magic_score"]=99
  with self.assertRaises(ValueError):review_from_json(json.dumps(p))
 def test_bad_schema_fails_closed(self):
  with self.assertRaises(ValueError):review_from_json(json.dumps({"schema_version":999,"review":{"relative_path":"a.jpg"}}))
 def test_save_outside_source_and_overwrite(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);source=root/"photos";source.mkdir();dest=root/"state"/"review.json";r=ReviewIntelligenceRecord("a.jpg");save_review(r,dest,source);self.assertEqual(load_review(dest),r);r2=ReviewIntelligenceRecord("a.jpg",screen_decision="hold");save_review(r2,dest,source,overwrite=True);self.assertEqual(load_review(dest),r2)
 def test_source_tree_write_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);source=root/"photos";source.mkdir()
   with self.assertRaises(ValueError):save_review(ReviewIntelligenceRecord("a.jpg"),source/"review.json",source)
 def test_non_json_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);source=root/"photos";source.mkdir()
   with self.assertRaises(ValueError):save_review(ReviewIntelligenceRecord("a.jpg"),root/"review.txt",source)
if __name__=="__main__":unittest.main()
