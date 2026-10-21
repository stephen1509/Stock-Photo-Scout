import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.preparation import PreparationRecord
from stock_photo_scout.metadata_assistant import review_metadata
class MetadataAssistant008Tests(unittest.TestCase):
 def test_deduplicates_without_inventing_keywords(self):
  r=PreparationRecord("a.jpg",title="Nara Temple",description="Temple exterior in Nara",keywords=("Nara"," temple ","NARA"),route="editorial");x=review_metadata(r);self.assertEqual(x.normalized_keyword_suggestions,("Nara","temple"));self.assertTrue(any(o.code=="keyword-duplicates" for o in x.observations))
 def test_identical_title_description_is_flagged(self):
  x=review_metadata(PreparationRecord("a.jpg",title="Temple exterior",description="Temple exterior",keywords=("temple",),route="editorial"));self.assertTrue(any(o.code=="title-description-identical" for o in x.observations))
 def test_missing_title_terms_are_prompts_not_auto_added(self):
  x=review_metadata(PreparationRecord("a.jpg",title="Autumn Temple Garden",description="Factual description",keywords=("temple",),route="editorial"));self.assertEqual(x.normalized_keyword_suggestions,("temple",));self.assertTrue(any(o.code=="title-terms-not-keywords" for o in x.observations))
 def test_undecided_route_is_explicit(self):
  x=review_metadata(PreparationRecord("a.jpg",title="Temple",description="Exterior",keywords=("temple",)));self.assertTrue(any(o.code=="route-undecided" for o in x.observations))
 def test_empty_facts_are_not_fabricated(self):
  x=review_metadata(PreparationRecord("a.jpg"));self.assertEqual(x.normalized_keyword_suggestions,());self.assertTrue(any(o.code=="facts-missing" for o in x.observations))
if __name__=="__main__":unittest.main()
