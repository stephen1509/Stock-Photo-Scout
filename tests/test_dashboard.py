import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from stock_photo_scout.dashboard import DashboardSettings, LocalDashboard
from stock_photo_scout.drafts import CandidateDraft, save_draft_json


class LocalDashboardTests(unittest.TestCase):
    def test_lists_reads_and_updates_only_local_drafts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "photos"
            source.mkdir()
            image = source / "photo.jpg"
            image.write_bytes(b"source image")
            drafts = root / "local_drafts"
            draft_path = drafts / "photo.json"
            save_draft_json(CandidateDraft("photo.jpg", title="Temple"), draft_path, source)
            dashboard = LocalDashboard(DashboardSettings.create(source, drafts, drafts / "accepted_spellings.json"))

            self.assertEqual(dashboard.list_drafts(), ["photo.json"])
            self.assertEqual(dashboard.load_draft("photo.json")["draft"]["title"], "Temple")
            response = dashboard.update_draft(
                "photo.json",
                {
                    "title": "Temple at dawn",
                    "keywords": ["temple", "dawn"],
                    "notes": "Review later",
                    "rights": {"visible_logos_or_trademarks": "unknown"},
                },
            )

            self.assertEqual(response["draft"]["keywords"], ["temple", "dawn"])
            self.assertEqual(response["draft"]["notes"], "Review later")
            self.assertEqual(image.read_bytes(), b"source image")

    def test_confirmed_spelling_is_written_to_local_dictionary_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "photos"
            source.mkdir()
            drafts = root / "local_drafts"
            dictionary = drafts / "accepted_spellings.json"
            dashboard = LocalDashboard(DashboardSettings.create(source, drafts, dictionary))

            self.assertEqual(dashboard.accept_spelling({"term": "Todaiji"}), {"term": "Todaiji"})
            self.assertIn("Todaiji", dictionary.read_text(encoding="utf-8"))

    def test_refuses_a_drafts_directory_inside_the_photo_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory) / "photos"
            source.mkdir()

            with self.assertRaises(ValueError):
                DashboardSettings.create(source, source / "local_drafts", source / "local_drafts" / "accepted_spellings.json")


if __name__ == "__main__":
    unittest.main()
