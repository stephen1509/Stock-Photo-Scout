import json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.preparation import PreparationRecord,evaluate_preparation,preparation_from_json,preparation_to_json,save_preparation_json
class PreparationHardening007Tests(unittest.TestCase):
 def test_round_trip_strict_schema(self):
  r=PreparationRecord("a.jpg",title="Nara deer",description="Deer in Nara",keywords=("deer","Nara"),route="editorial");self.assertEqual(preparation_from_json(preparation_to_json(r)),r)
 def test_unknown_top_level_and_record_fields_fail_closed(self):
  base=json.loads(preparation_to_json(PreparationRecord("a.jpg")))
  p=dict(base);p["future"]=1
  with self.assertRaises(ValueError):preparation_from_json(json.dumps(p))
  p=json.loads(json.dumps(base));p["preparation"]["magic_score"]=99
  with self.assertRaises(ValueError):preparation_from_json(json.dumps(p))
 def test_keyword_types_fail_closed(self):
  p=json.loads(preparation_to_json(PreparationRecord("a.jpg")));p["preparation"]["keywords"]=["deer",3]
  with self.assertRaises(ValueError):preparation_from_json(json.dumps(p))
 def test_category_pair_unknown_field_fails_closed(self):
  p=json.loads(preparation_to_json(PreparationRecord("a.jpg")));p["preparation"]["category_pairs"]=[{"category":"Animals","future":1}]
  with self.assertRaises(ValueError):preparation_from_json(json.dumps(p))
 def test_blank_and_duplicate_metadata_prompted(self):
  report=evaluate_preparation(PreparationRecord("a.jpg",title="x",description="y",keywords=("deer"," Deer ",""),categories=("Animals"," "),route="editorial"));codes={x.code for x in report.prompts};self.assertTrue({"duplicate_keywords","blank_keywords","blank_categories"}.issubset(codes))
 def test_durable_external_save_and_overwrite(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);source=root/"photos";source.mkdir();dest=root/"state"/"prep.json";save_preparation_json(PreparationRecord("a.jpg"),dest,source);save_preparation_json(PreparationRecord("a.jpg",title="updated"),dest,source,overwrite=True);self.assertEqual(preparation_from_json(dest.read_text()).title,"updated")
 def test_source_tree_write_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   source=Path(td)/"photos";source.mkdir()
   with self.assertRaises(ValueError):save_preparation_json(PreparationRecord("a.jpg"),source/"prep.json",source)
if __name__=="__main__":unittest.main()
