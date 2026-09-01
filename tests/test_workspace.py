import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from stock_photo_scout.workspace import (
    CandidateWorkspaceRecord,
    create_preview_copy,
    load_workspace,
    save_workspace,
    set_candidate_state,
)


class CandidateWorkspaceTests(unittest.TestCase):
    def test_preview_requires_explicit_consent_and_preserves_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "photos"
            previews = root / "previews"
            source.mkdir()
            image = source / "nested" / "photo.jpg"
            image.parent.mkdir()
            original = b"synthetic-jpeg-bytes"
            image.write_bytes(original)

            with self.assertRaises(PermissionError):
                create_preview_copy(source, "nested/photo.jpg", previews, consent=False)

            preview = create_preview_copy(source, "nested/photo.jpg", previews, consent=True)
            self.assertEqual(preview.read_bytes(), original)
            self.assertEqual(image.read_bytes(), original)
            self.assertFalse(preview.is_relative_to(source))

            with self.assertRaises(FileExistsError):
                create_preview_copy(source, "nested/photo.jpg", previews, consent=True)

    def test_preview_refuses_source_tree_destination_and_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "photos"
            source.mkdir()
            (source / "photo.jpg").write_bytes(b"image")

            with self.assertRaises(ValueError):
                create_preview_copy(source, "photo.jpg", source / "previews", consent=True)
            with self.assertRaises(ValueError):
                create_preview_copy(source, "../photo.jpg", root / "previews", consent=True)

    def test_candidate_state_round_trip_is_deterministic_and_local(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "photos"
            source.mkdir()
            manifest = root / "workspace" / "candidates.json"

            records = {}
            records = set_candidate_state(records, "b.jpg", "shortlist", preview_relative_path="b.jpg")
            records = set_candidate_state(records, "a.jpg", "skip")
            save_workspace(records, manifest, source)

            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual([item["relative_path"] for item in payload["candidates"]], ["a.jpg", "b.jpg"])
            loaded = load_workspace(manifest)
            self.assertEqual(loaded["b.jpg"], CandidateWorkspaceRecord("b.jpg", "shortlist", "b.jpg"))
            self.assertFalse(manifest.is_relative_to(source))

            updated = set_candidate_state(loaded, "b.jpg", "edit")
            save_workspace(updated, manifest, source, overwrite=True)
            self.assertEqual(load_workspace(manifest)["b.jpg"].state, "edit")

    def test_invalid_state_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            set_candidate_state({}, "photo.jpg", "excellent")


if __name__ == "__main__":
    unittest.main()
