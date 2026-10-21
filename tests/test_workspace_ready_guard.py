import json, sys, tempfile, unittest
from pathlib import Path
PROJECT_ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT_ROOT/"src"))
from stock_photo_scout.workspace import CandidateWorkspaceRecord, load_workspace, set_candidate_preview, set_candidate_state

class WorkspaceReadyGuardTests(unittest.TestCase):
    def test_direct_submission_ready_transition_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"cannot be set directly"):
            set_candidate_state({},"photo.jpg","submission-ready")

    def test_legacy_submission_ready_record_remains_readable_for_migration(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"workspace.json"
            path.write_text(json.dumps({"schema_version":1,"candidates":[{"relative_path":"photo.jpg","state":"submission-ready","preview_relative_path":""}]}),encoding="utf-8")
            self.assertEqual(load_workspace(path)["photo.jpg"].state,"submission-ready")

    def test_preview_metadata_update_preserves_legacy_ready_state(self):
        records={"photo.jpg":CandidateWorkspaceRecord("photo.jpg","submission-ready","")}
        updated=set_candidate_preview(records,"photo.jpg","photo.jpg")
        self.assertEqual(updated["photo.jpg"].state,"submission-ready")
        self.assertEqual(updated["photo.jpg"].preview_relative_path,"photo.jpg")
        self.assertEqual(records["photo.jpg"].preview_relative_path,"")

    def test_preview_metadata_for_new_candidate_defaults_to_maybe(self):
        updated=set_candidate_preview({},"photo.jpg","previews/photo.jpg")
        self.assertEqual(updated["photo.jpg"].state,"maybe")

    def test_preview_metadata_paths_fail_closed(self):
        for path in ("../photo.jpg",r"C:\\photo.jpg",r"\\server\\share\\photo.jpg"):
            with self.subTest(path=path),self.assertRaises(ValueError):
                set_candidate_preview({},"photo.jpg",path)

if __name__=="__main__": unittest.main()
