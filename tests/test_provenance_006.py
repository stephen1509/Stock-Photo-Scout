import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from stock_photo_scout.provenance import create_provenance, fingerprint_file, provenance_from_json, provenance_to_json, save_provenance, verify_provenance

class ProvenanceTests(unittest.TestCase):
    def fixture(self, root):
        source=root/"photos"; export=root/"exports"; source.mkdir(); export.mkdir()
        (source/"日本 photo.jpg").write_bytes(b"source-v1")
        (export/"日本 final.jpg").write_bytes(b"export-v1")
        return source,export

    def test_requires_explicit_byte_read_consent(self):
        with tempfile.TemporaryDirectory() as td:
            source, _ = self.fixture(Path(td))
            with self.assertRaises(PermissionError): fingerprint_file(source,"日本 photo.jpg",consent=False)

    def test_round_trip_and_current_verification(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source,export=self.fixture(root)
            record=create_provenance(source,"日本 photo.jpg",export,"日本 final.jpg",editor_target="darktable",export_version=1,consent=True)
            restored=provenance_from_json(provenance_to_json(record)); self.assertEqual(restored,record)
            current,blockers=verify_provenance(record,source,export,consent=True); self.assertTrue(current); self.assertEqual(blockers,())
            save_provenance(record,root/"state"/"provenance.json",source); self.assertTrue((root/"state"/"provenance.json").is_file())

    def test_changed_export_invalidates_and_requires_final_qc_repeat(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source,export=self.fixture(root)
            record=create_provenance(source,"日本 photo.jpg",export,"日本 final.jpg",editor_target="darktable",export_version=1,consent=True)
            (export/"日本 final.jpg").write_bytes(b"export-v2")
            current,blockers=verify_provenance(record,source,export,consent=True)
            self.assertFalse(current); self.assertTrue(any("final QC" in b for b in blockers))

    def test_changed_source_invalidates(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source,export=self.fixture(root)
            record=create_provenance(source,"日本 photo.jpg",export,"日本 final.jpg",editor_target="darktable",export_version=1,consent=True)
            (source/"日本 photo.jpg").write_bytes(b"source-v2")
            self.assertFalse(verify_provenance(record,source,export,consent=True)[0])

    def test_overlapping_roots_and_windows_paths_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source=root/"photos"; source.mkdir(); (source/"x.jpg").write_bytes(b"x")
            with self.assertRaises(ValueError): create_provenance(source,"x.jpg",source/"exports","x.jpg",editor_target="other",export_version=1,consent=True)
            for value in (r"C:\\x.jpg", r"\\server\\share\\x.jpg", "../x.jpg"):
                with self.subTest(value=value), self.assertRaises(ValueError): fingerprint_file(source,value,consent=True)

    def test_malformed_json_fails_closed(self):
        malformed=([], {"schema_version":1}, {"schema_version":1,"record":[]}, {"schema_version":1,"record":{"source":{},"export":{},"editor_target":"x","export_version":1,"notes":""}})
        for value in malformed:
            with self.subTest(value=value), self.assertRaises(ValueError): provenance_from_json(json.dumps(value))

    def test_state_cannot_be_saved_inside_source_tree(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source,export=self.fixture(root)
            record=create_provenance(source,"日本 photo.jpg",export,"日本 final.jpg",editor_target="darktable",export_version=1,consent=True)
            with self.assertRaises(ValueError): save_provenance(record,source/"provenance.json",source)

if __name__=="__main__": unittest.main()
