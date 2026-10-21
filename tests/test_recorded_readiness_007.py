import sys, unittest
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.candidate_review import CandidateReviewRecord
from stock_photo_scout.final_qc import FinalQcRecord
from stock_photo_scout.provenance import create_provenance
from stock_photo_scout.readiness import assess_recorded_readiness
from stock_photo_scout.rights_review import RightsReview

class RecordedReadinessTests(unittest.TestCase):
 def setUp(self):
  self.tmp=TemporaryDirectory();root=Path(self.tmp.name);self.source=root/"source";self.exports=root/"exports";self.source.mkdir();self.exports.mkdir();(self.source/"a.jpg").write_bytes(b"source");(self.exports/"a.jpg").write_bytes(b"export");self.provenance=create_provenance(self.source,"a.jpg",self.exports,"a.jpg",editor_target="GIMP",export_version=1,consent=True);self.review=CandidateReviewRecord("a.jpg","candidate","pass","strong","clear-looking","commercial","ready");self.rights=RightsReview(*(["none-seen"]*9));self.qc=FinalQcRecord(self.provenance.export.sha256,True,True,(),"Exact export inspected")
 def tearDown(self):self.tmp.cleanup()
 def assess(self,**changes):
  args=dict(review=self.review,rights=self.rights,provenance=self.provenance,source_root=self.source,export_root=self.exports,provenance_consent=True,current_marketplace_requirements_reviewed=True,final_qc=self.qc,review_intelligence_complete=True);args.update(changes);return assess_recorded_readiness(**args)
 def test_current_recorded_bytes_can_pass_all_gates(self):self.assertTrue(self.assess().ready)
 def test_consent_is_required(self):
  r=self.assess(provenance_consent=False);self.assertFalse(r.ready);self.assertTrue(any("Explicit byte-read consent" in x for x in r.blockers))
 def test_changed_export_fails_and_requires_new_qc(self):
  (self.exports/"a.jpg").write_bytes(b"changed export");r=self.assess();self.assertFalse(r.ready);self.assertTrue(any("Export bytes changed" in x for x in r.blockers))
 def test_changed_source_fails(self):
  (self.source/"a.jpg").write_bytes(b"changed source");r=self.assess();self.assertFalse(r.ready);self.assertTrue(any("Source bytes changed" in x for x in r.blockers))
 def test_missing_export_fails_closed(self):
  (self.exports/"a.jpg").unlink();r=self.assess();self.assertFalse(r.ready);self.assertTrue(any("Provenance verification failed" in x for x in r.blockers))
 def test_review_intelligence_still_cannot_be_bypassed(self):self.assertFalse(self.assess(review_intelligence_complete=None).ready)
if __name__=="__main__":unittest.main()
