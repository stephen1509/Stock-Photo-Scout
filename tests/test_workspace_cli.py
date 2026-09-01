import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from stock_photo_scout.workspace_cli import workspace_main
from stock_photo_scout.workspace import load_workspace


class WorkspaceCliTests(unittest.TestCase):
    def test_preview_command_requires_consent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "photos"
            source.mkdir()
            (source / "photo.jpg").write_bytes(b"source")
            with self.assertRaises(PermissionError):
                workspace_main(["preview", str(source), "photo.jpg", str(root / "previews")])

    def test_preview_and_state_commands_preserve_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "photos"
            source.mkdir()
            image = source / "photo.jpg"
            original = b"source image bytes"
            image.write_bytes(original)
            previews = root / "local_previews"
            manifest = root / "local_workspace" / "candidates.json"

            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(
                    workspace_main(["preview", str(source), "photo.jpg", str(previews), "--consent"]),
                    0,
                )
                self.assertEqual(
                    workspace_main(
                        [
                            "set-state",
                            str(source),
                            str(manifest),
                            "photo.jpg",
                            "shortlist",
                            "--preview-relative-path",
                            "photo.jpg",
                        ]
                    ),
                    0,
                )

            self.assertEqual(image.read_bytes(), original)
            self.assertEqual((previews / "photo.jpg").read_bytes(), original)
            self.assertEqual(load_workspace(manifest)["photo.jpg"].state, "shortlist")

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(workspace_main(["show", str(manifest)]), 0)
            self.assertIn("photo.jpg: shortlist preview=photo.jpg", output.getvalue())


if __name__ == "__main__":
    unittest.main()
