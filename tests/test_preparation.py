import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from stock_photo_scout.preparation import (
    CategoryPair,
    PreparationRecord,
    category_pair_from_text,
    edit_preparation,
    evaluate_preparation,
    preparation_from_json,
    preparation_to_json,
    save_preparation_json,
)


class PreparationTests(unittest.TestCase):
    def test_reports_missing_human_fields_without_claiming_acceptance(self) -> None:
        report = evaluate_preparation(PreparationRecord("photo.jpg"))
        codes = {prompt.code for prompt in report.prompts}
        self.assertEqual(codes, {"title_missing", "description_missing", "keywords_missing", "route_undecided"})

    def test_editor_handoff_requires_recorded_working_export(self) -> None:
        record = PreparationRecord(
            "photo.jpg",
            title="Temple at dawn",
            description="Temple exterior at dawn",
            keywords=("temple", "dawn"),
            route="commercial",
            editor_target="darktable",
        )
        report = evaluate_preparation(record)
        self.assertEqual([prompt.code for prompt in report.prompts], ["working_export_missing"])

        updated = edit_preparation(record, working_export_relative_path="exports/photo-final.jpg")
        self.assertEqual(evaluate_preparation(updated).prompts, ())

    def test_serialization_is_deterministic_and_external(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "photos"
            source.mkdir()
            destination = root / "local_preparation" / "photo.json"
            record = PreparationRecord(
                "nested/photo.jpg",
                title="Temple",
                description="Historic temple exterior",
                keywords=("temple", "architecture"),
                categories=("architecture",),
                route="editorial",
                notes="Human review complete",
            )
            serialized = preparation_to_json(record)
            save_preparation_json(record, destination, source)
            self.assertEqual(preparation_from_json(serialized), record)
            self.assertEqual(preparation_from_json(destination.read_text(encoding="utf-8")), record)
            self.assertNotIn(str(source), serialized)
            with self.assertRaises(FileExistsError):
                save_preparation_json(record, destination, source)

    def test_rejects_unsafe_paths_and_source_tree_writes(self) -> None:
        with self.assertRaises(ValueError):
            PreparationRecord("../outside.jpg")
        with self.assertRaises(ValueError):
            PreparationRecord("C:outside.jpg")
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory) / "photos"
            source.mkdir()
            with self.assertRaises(ValueError):
                save_preparation_json(PreparationRecord("photo.jpg"), source / "prep.json", source)

    def test_duplicate_keywords_are_explainable_prompt(self) -> None:
        record = PreparationRecord(
            "photo.jpg",
            title="Temple",
            description="Temple",
            keywords=("Nara", "nara"),
            route="editorial",
        )
        self.assertIn("duplicate_keywords", {prompt.code for prompt in evaluate_preparation(record).prompts})

    def test_round_trips_up_to_three_category_pairs(self) -> None:
        record = PreparationRecord(
            "photo.jpg",
            category_pairs=(
                CategoryPair("Arts & Architecture", "Historic buildings"),
                CategoryPair("Travel", "Landmarks"),
                CategoryPair("Nature"),
            ),
        )
        self.assertEqual(preparation_from_json(preparation_to_json(record)), record)
        self.assertEqual(category_pair_from_text("Travel :: Landmarks"), CategoryPair("Travel", "Landmarks"))
        with self.assertRaises(ValueError):
            PreparationRecord("photo.jpg", category_pairs=(CategoryPair("A"),) * 4)


if __name__ == "__main__":
    unittest.main()
