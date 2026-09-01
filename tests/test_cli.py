import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from stock_photo_scout.cli import main
from stock_photo_scout.drafts import CandidateDraft, draft_to_json


class CommandLineReviewTests(unittest.TestCase):
    def test_review_uses_local_dictionary_without_reading_an_image(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            draft_path = root / "draft.json"
            dictionary_path = root / "accepted_spellings.json"
            draft_path.write_text(draft_to_json(CandidateDraft("photo.jpg", title="Todaiji temple")), encoding="utf-8")

            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(["accept-spelling", str(dictionary_path), "Todaiji"]), 0)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(["review-draft", str(draft_path), "--dictionary", str(dictionary_path)]), 0)

            self.assertIn("Candidate: photo.jpg", output.getvalue())
            self.assertNotIn("Todaiji", output.getvalue())

    def test_accept_spelling_creates_then_updates_a_local_dictionary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            dictionary_path = Path(temporary_directory) / "accepted_spellings.json"

            with contextlib.redirect_stdout(io.StringIO()):
                main(["accept-spelling", str(dictionary_path), "Todaiji"])
                main(["accept-spelling", str(dictionary_path), "Nara"])

            self.assertIn("Todaiji", dictionary_path.read_text(encoding="utf-8"))
            self.assertIn("Nara", dictionary_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
