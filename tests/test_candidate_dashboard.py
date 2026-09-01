import sys, tempfile, unittest
from pathlib import Path
PROJECT_ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT_ROOT/"src"))
from stock_photo_scout.candidate_dashboard import CandidateDashboard, CandidateDashboardSettings
from stock_photo_scout.drafts import CandidateDraft, save_draft_json

class CandidateDashboardTests(unittest.TestCase):
    def test_draft_candidate_does_not_read_source(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source=root/"photos"; source.mkdir()
            image=source/"photo.jpg"; original=b"source-image-bytes"; image.write_bytes(original)
            drafts=root/"local_drafts"; save_draft_json(CandidateDraft("photo.jpg",title="Temple"),drafts/"photo.json",source)
            d=CandidateDashboard(CandidateDashboardSettings.create(source,drafts,drafts/"accepted_spellings.json",root/"local_previews",root/"local_workspace"/"candidates.json"))
            c=d.list_candidates()[0]
            self.assertEqual((c["relative_path"],c["state"],c["preview_available"]),("photo.jpg","maybe",False))
            self.assertEqual(image.read_bytes(),original)

    def test_preview_requires_consent_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source=root/"photos"; source.mkdir(); drafts=root/"local_drafts"; drafts.mkdir()
            image=source/"photo.jpg"; original=b"source"; image.write_bytes(original)
            d=CandidateDashboard(CandidateDashboardSettings.create(source,drafts,drafts/"accepted_spellings.json",root/"local_previews",root/"local_workspace"/"candidates.json"))
            with self.assertRaises(PermissionError): d.create_preview({"relative_path":"photo.jpg","consent":False})
            r=d.create_preview({"relative_path":"photo.jpg","consent":True}); p=d.preview_path(r["preview_relative_path"])
            self.assertEqual(p.read_bytes(),original); self.assertFalse(p.is_relative_to(source)); self.assertEqual(image.read_bytes(),original)

    def test_state_persists_and_preview_traversal_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source=root/"photos"; source.mkdir(); drafts=root/"local_drafts"; drafts.mkdir()
            d=CandidateDashboard(CandidateDashboardSettings.create(source,drafts,drafts/"accepted_spellings.json",root/"local_previews",root/"local_workspace"/"candidates.json"))
            d.set_state({"relative_path":"photo.jpg","state":"shortlist"})
            self.assertEqual(d.list_candidates()[0]["state"],"shortlist")
            with self.assertRaises((FileNotFoundError,ValueError)): d.preview_path("../secret.jpg")

    def test_workspace_paths_cannot_be_inside_source(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source=root/"photos"; source.mkdir()
            with self.assertRaises(ValueError):
                CandidateDashboardSettings.create(source,root/"drafts",root/"drafts"/"accepted_spellings.json",source/"previews",root/"workspace.json")

if __name__=="__main__": unittest.main()
