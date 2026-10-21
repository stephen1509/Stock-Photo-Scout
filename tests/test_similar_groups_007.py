import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.similar_groups import GroupCandidate,build_group_hints,grouping_hint
class SimilarGroups007Tests(unittest.TestCase):
 def test_exact_hash_is_explainable_fact(self):
  h=grouping_hint(GroupCandidate("a.jpg","a"*64),GroupCandidate("b.jpg","a"*64));self.assertEqual(h.reasons,("exact-content-hash",))
 def test_capture_time_is_conservative_hint(self):
  h=grouping_hint(GroupCandidate("a.jpg",captured_at_seconds=100),GroupCandidate("b.jpg",captured_at_seconds=102));self.assertIn("capture-time-proximity",h.reasons)
 def test_filename_sequence_is_weak_explicit_hint(self):
  h=grouping_hint(GroupCandidate("IMG_1001.jpg"),GroupCandidate("IMG_1002.jpg"));self.assertEqual(h.reasons,("filename-sequence-proximity",))
 def test_unrelated_candidates_have_no_hint(self):self.assertIsNone(grouping_hint(GroupCandidate("cat.jpg"),GroupCandidate("tree.jpg")))
 def test_multiple_reasons_are_preserved_not_scored(self):
  h=grouping_hint(GroupCandidate("IMG_1.jpg","b"*64,10),GroupCandidate("IMG_2.jpg","b"*64,11));self.assertEqual(set(h.reasons),{"exact-content-hash","capture-time-proximity","filename-sequence-proximity"})
 def test_no_self_pair(self):
  with self.assertRaises(ValueError):grouping_hint(GroupCandidate("a.jpg"),GroupCandidate("a.jpg"))
 def test_bad_hash_and_paths_fail_closed(self):
  for c in (GroupCandidate("../a.jpg"),GroupCandidate(r"C:\\a.jpg"),GroupCandidate("a.jpg","not-a-hash")):
   with self.subTest(c=c),self.assertRaises(ValueError):build_group_hints((c,))
 def test_duplicate_paths_rejected(self):
  with self.assertRaises(ValueError):build_group_hints((GroupCandidate("a.jpg"),GroupCandidate("a.jpg")))
if __name__=="__main__":unittest.main()
