import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
PROJECT_ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(PROJECT_ROOT/"src"))
from stock_photo_scout.workspace import CandidateWorkspaceRecord,create_preview_copy,load_workspace,save_workspace,set_candidate_state

class WorkspaceHardening006Tests(unittest.TestCase):
    def test_windows_drive_and_unc_paths_rejected_cross_platform(self):
        for value in (r"C:\photo.jpg",r"C:photo.jpg",r"\\server\share\photo.jpg"):
            with self.subTest(value=value),self.assertRaises(ValueError): set_candidate_state({},value,"maybe")
    def test_non_string_persisted_path_is_rejected_not_coerced(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"w.json"; p.write_text(json.dumps({"schema_version":1,"candidates":[{"relative_path":123,"state":"maybe","preview_relative_path":""}]}),encoding="utf-8")
            with self.assertRaises(ValueError): load_workspace(p)
    def test_overwrite_refuses_directory_target(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source=root/"photos"; source.mkdir(); target=root/"state.json"; target.mkdir()
            with self.assertRaises(ValueError): save_workspace({"a.jpg":CandidateWorkspaceRecord("a.jpg")},target,source,overwrite=True)
    def test_failed_copy_removes_partial_preview(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source=root/"photos"; preview=root/"previews"; source.mkdir(); (source/"a.jpg").write_bytes(b"abcdef")
            def fail(src,dst,length): dst.write(b"partial"); raise OSError("simulated copy failure")
            with patch("stock_photo_scout.workspace.shutil.copyfileobj",side_effect=fail):
                with self.assertRaises(OSError): create_preview_copy(source,"a.jpg",preview,consent=True)
            self.assertFalse((preview/"a.jpg").exists())

if __name__=="__main__": unittest.main()
