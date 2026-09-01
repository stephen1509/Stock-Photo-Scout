import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from stock_photo_scout.spelling import find_possible_spelling_issues
from stock_photo_scout.spelling_dictionary import (
    AcceptedSpellings,
    save_spelling_dictionary,
    spelling_dictionary_from_json,
    spelling_dictionary_to_json,
    update_spelling_dictionary,
)
from stock_photo_scout import spelling_dictionary


class AcceptedSpellingsTests(unittest.TestCase):
    def test_confirmed_term_suppresses_future_prompt_without_changing_text(self) -> None:
        dictionary = AcceptedSpellings().add("Todaiji")

        self.assertEqual(find_possible_spelling_issues("Todaiji", dictionary.apply_to()), ())

    def test_serializes_and_explicitly_updates_local_dictionary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            destination = Path(temporary_directory) / "local_drafts" / "accepted_spellings.json"
            original = AcceptedSpellings(frozenset({"Todaiji"}))
            updated = original.add("Nara")

            self.assertEqual(save_spelling_dictionary(original, destination), destination.resolve())
            self.assertEqual(spelling_dictionary_from_json(spelling_dictionary_to_json(original)), original)
            self.assertEqual(update_spelling_dictionary(updated, destination), destination.resolve())
            self.assertEqual(
                spelling_dictionary_from_json(destination.read_text(encoding="utf-8")), updated
            )
            with self.assertRaises(FileExistsError):
                save_spelling_dictionary(updated, destination)

    def test_update_retries_a_brief_file_lock(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            destination = Path(temporary_directory) / "accepted_spellings.json"
            save_spelling_dictionary(AcceptedSpellings(frozenset({"Todaiji"})), destination)
            original_replace = spelling_dictionary.os.replace
            calls = 0

            def locked_once(source: Path, target: Path) -> None:
                nonlocal calls
                calls += 1
                if calls == 1:
                    raise PermissionError("temporary lock")
                original_replace(source, target)

            with patch.object(spelling_dictionary.os, "replace", side_effect=locked_once), patch.object(
                spelling_dictionary.time, "sleep"
            ):
                update_spelling_dictionary(AcceptedSpellings(frozenset({"Todaiji", "Nara"})), destination)

            self.assertEqual(calls, 2)
            self.assertIn("Nara", destination.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
