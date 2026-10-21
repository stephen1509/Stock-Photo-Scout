import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.review_intelligence import ReviewIntelligenceRecord
from stock_photo_scout.stock_usefulness import StockUsefulnessReview
from stock_photo_scout.review_packet_store import packet_from_json,packet_to_json,save_packet
from stock_photo_scout.review_service import ReviewService
from stock_photo_scout.review_store import save_review
from stock_photo_scout.usefulness_store import save_usefulness
class ReviewPacketStore007Tests(unittest.TestCase):
 def records(self,rel="a.jpg"):return ReviewIntelligenceRecord(rel,screen_decision="inspect",focus_state="looks-clean",composition_state="strong"),StockUsefulnessReview("clear","clean","right","strong","distinct",False,True,"Human reviewed")
 def test_packet_round_trip(self):
  r,u=self.records();self.assertEqual(packet_from_json(packet_to_json(r,u)),(r,u))
 def test_packet_cannot_be_inside_source_tree(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);source=root/"photos";source.mkdir();r,u=self.records()
   with self.assertRaises(ValueError):save_packet(r,u,source/"state.json",source)
 def test_service_writes_one_combined_packet(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);source=root/"photos";source.mkdir();reviews=root/"reviews";s=ReviewService(source,reviews);r,u=self.records();s.save("a.jpg",r,u);files=list(reviews.iterdir());self.assertEqual(len(files),1);self.assertTrue(files[0].name.endswith(".review-packet.json"));self.assertTrue(s.load("a.jpg")["assessment"]["can_shortlist"])
 def test_legacy_split_pair_is_read_but_next_save_migrates_to_packet(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);source=root/"photos";source.mkdir();reviews=root/"reviews";s=ReviewService(source,reviews);r,u=self.records();packet,rp,up=s._paths("a.jpg");save_review(r,rp,source);save_usefulness(u,up,source);self.assertTrue(s.load("a.jpg")["assessment"]["can_shortlist"]);s.save("a.jpg",r,u);self.assertTrue(packet.exists())
 def test_packet_path_mismatch_fails_closed(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);source=root/"photos";source.mkdir();reviews=root/"reviews";s=ReviewService(source,reviews);packet,_,_=s._paths("a.jpg");r,u=self.records("b.jpg");save_packet(r,u,packet,source)
   with self.assertRaises(ValueError):s.load("a.jpg")
 def test_symlink_destination_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);source=root/"photos";source.mkdir();outside=root/"outside.json";outside.write_text("keep");link=root/"packet.json"
   try:link.symlink_to(outside)
   except (OSError,NotImplementedError):self.skipTest("symlinks unavailable")
   r,u=self.records()
   with self.assertRaises(ValueError):save_packet(r,u,link,source,overwrite=True)
   self.assertEqual(outside.read_text(),"keep")
 def test_symlink_parent_is_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);source=root/"photos";source.mkdir();real=root/"real";real.mkdir();link=root/"linked"
   try:link.symlink_to(real,target_is_directory=True)
   except (OSError,NotImplementedError):self.skipTest("symlinks unavailable")
   r,u=self.records()
   with self.assertRaises(ValueError):save_packet(r,u,link/"packet.json",source)
if __name__=="__main__":unittest.main()
