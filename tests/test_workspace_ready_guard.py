import json, sys, tempfile, unittest
from pathlib import Path
PROJECT_ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT_ROOT/"src"))
from stock_photo_scout.workspace import CandidateWorkspaceRecord, load_workspace, set_candidate_state

class WorkspaceReadyGuardTests(unittest.TestCase):
    def test_direct_submission_ready_transition_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"cannot be set directly"):
            set_candidate_state({},"photo.jpg","submission-ready")

    def test_legacy_submission_ready_record_remains_readable_for_migration(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"workspace.json"
            path.write_text(json.dumps({"schema_version":1,"candidates":[{"relative_path":"photo.jpg","state":"submission-ready","preview_relative_path":""}]}),encoding="utf-8")
            self.assertEqual(load_workspace(path)["photo.jpg"].state,"submission-ready")

if __name__=="__main__": unittest.main()
