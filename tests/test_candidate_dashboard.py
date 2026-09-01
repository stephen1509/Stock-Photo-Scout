import sys, tempfile, unittest
from pathlib import Path
PROJECT_ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT_ROOT/"src"))
from stock_photo_scout.candidate_dashboard import CandidateDashboard, CandidateDashboardSettings
from stock_photo_scout.drafts import CandidateDraft, save_draft_json
from stock_photo_scout.image_analysis import CandidateAnalysis, save_analysis_json
from stock_photo_scout.visual_signals import VisualSignalReport

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

    def test_preparation_and_preflight_are_local_only(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source=root/"photos"; source.mkdir(); drafts=root/"local_drafts"; drafts.mkdir()
            d=CandidateDashboard(CandidateDashboardSettings.create(
                source,drafts,drafts/"accepted_spellings.json",
                root/"local_previews",root/"local_workspace"/"candidates.json",
                root/"local_preparation",root/"local_analysis"
            ))
            d.set_state({"relative_path":"photo.jpg","state":"submission-ready"})
            loaded=d.load_preparation({"relative_path":"photo.jpg"})
            self.assertEqual(loaded["preparation"]["route"],"undecided")
            saved=d.save_preparation({
                "relative_path":"photo.jpg",
                "title":"Temple",
                "description":"Temple exterior",
                "keywords":["temple","Japan"],
                "categories":["architecture"],
                "route":"editorial",
                "editor_target":"darktable",
                "working_export_relative_path":"exports/photo-final.jpg",
                "notes":"Reviewed locally",
            })
            self.assertEqual(saved["prompts"],[])
            analysis=CandidateAnalysis(
                "photo.jpg","SyntheticDecoder",
                VisualSignalReport(10,10,121.0,0.0,0.0,6.0,2.0,())
            )
            save_analysis_json(analysis,root/"local_analysis"/"photo.json",source)
            packet=d.build_preflight({
                "relative_path":"photo.jpg",
                "preview_integrity":"match",
                "current_requirements_reviewed":True,
            })
            self.assertTrue(packet["local_packet_complete"])
            self.assertIn("does not upload, submit",packet["text"])
            self.assertIn("Mean luminance: 121.0000.",packet["text"])
            self.assertTrue((root/"local_preparation").exists())
            self.assertFalse((root/"local_preparation").is_relative_to(source))

    def test_preparation_directory_cannot_be_inside_source(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source=root/"photos"; source.mkdir()
            with self.assertRaises(ValueError):
                CandidateDashboardSettings.create(
                    source,root/"drafts",root/"drafts"/"accepted_spellings.json",
                    root/"previews",root/"workspace.json",source/"preparation"
                )

    def test_analysis_directory_cannot_be_inside_source(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source=root/"photos"; source.mkdir()
            with self.assertRaises(ValueError):
                CandidateDashboardSettings.create(
                    source,root/"drafts",root/"drafts"/"accepted_spellings.json",
                    root/"previews",root/"workspace.json",root/"preparation",source/"analysis"
                )

    def test_workspace_paths_cannot_be_inside_source(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source=root/"photos"; source.mkdir()
            with self.assertRaises(ValueError):
                CandidateDashboardSettings.create(source,root/"drafts",root/"drafts"/"accepted_spellings.json",source/"previews",root/"workspace.json")

if __name__=="__main__": unittest.main()
