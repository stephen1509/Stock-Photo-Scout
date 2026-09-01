import sys
import tempfile
import unittest
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from stock_photo_scout.drafts import (
    CandidateDraft,
    RightsObservations,
    draft_from_json,
    draft_to_json,
    edit_draft,
    evaluate_readiness,
    save_draft_json,
    update_draft_json,
)


class CandidateDraftTests(unittest.TestCase):
    def test_returns_manual_prompts_without_claiming_readiness(self) -> None:
        draft = CandidateDraft("temple.jpg")

        report = evaluate_readiness(draft)

        self.assertEqual(
            [prompt.code for prompt in report.prompts],
            [
                "title_missing",
                "keywords_missing",
                "recognizable_people_unknown",
                "private_property_or_restricted_location_unknown",
                "visible_logos_or_trademarks_unknown",
                "third_party_copyrighted_content_unknown",
                "release_evidence_not_reviewed",
            ],
        )
        self.assertTrue(all("ready" not in prompt.code for prompt in report.prompts))

    def test_edits_draft_and_reports_specific_follow_up(self) -> None:
        draft = CandidateDraft("temple.jpg")
        edited = edit_draft(
            draft,
            title="Temple market at dawn",
            keywords=("Japan", "market", "Japan "),
            rights=RightsObservations(
                recognizable_people="yes",
                private_property_or_restricted_location="no",
                visible_logos_or_trademarks="no",
                third_party_copyrighted_content="no",
                release_evidence="not_available",
            ),
            notes="Confirm rights context before any submission.",
        )

        report = evaluate_readiness(edited)

        self.assertEqual(edited.title, "Temple market at dawn")
        self.assertEqual(
            [prompt.code for prompt in report.prompts if prompt.code != "possible_spelling"],
            ["duplicate_keywords", "recognizable_people_present", "release_evidence_not_available"],
        )

    def test_serializes_and_saves_outside_source_without_overwriting(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source"
            source.mkdir()
            image = source / "temple.jpg"
            image.write_bytes(b"synthetic source")
            draft = CandidateDraft("temple.jpg", title="Temple market", keywords=("Japan", "market"))
            serialized = draft_to_json(draft)
            destination = root / "local_drafts" / "temple.json"

            saved_path = save_draft_json(draft, destination, source)

            self.assertEqual(saved_path, destination.resolve())
            self.assertEqual(draft_from_json(serialized), draft)
            self.assertEqual(draft_from_json(destination.read_text(encoding="utf-8")), draft)
            self.assertNotIn(str(source), serialized)
            self.assertEqual(image.read_bytes(), b"synthetic source")
            with self.assertRaises(FileExistsError):
                save_draft_json(draft, destination, source)

    def test_refuses_source_path_traversal_and_writes_inside_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source"
            source.mkdir()
            with self.assertRaises(ValueError):
                CandidateDraft("../outside.jpg")
            with self.assertRaises(ValueError):
                CandidateDraft("C:outside.jpg")

            draft = CandidateDraft("inside.jpg")
            with self.assertRaises(ValueError):
                save_draft_json(draft, source / "inside.json", source)

    def test_rejects_malformed_keyword_json(self) -> None:
        serialized = json.dumps(
            {
                "schema_version": 1,
                "draft": {
                    "relative_path": "temple.jpg",
                    "title": "Temple market",
                    "keywords": "not a keyword list",
                    "rights": {},
                    "notes": "",
                },
            }
        )

        with self.assertRaises(ValueError):
            draft_from_json(serialized)

    def test_explicitly_replaces_an_existing_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source"
            source.mkdir()
            destination = root / "local_drafts" / "temple.json"
            original = CandidateDraft("temple.jpg", title="First title")
            updated = edit_draft(original, title="Updated title", keywords=("Japan", "temple"))
            save_draft_json(original, destination, source)

            updated_path = update_draft_json(updated, destination, source)

            self.assertEqual(updated_path, destination.resolve())
            self.assertEqual(draft_from_json(destination.read_text(encoding="utf-8")), updated)

    def test_refuses_to_replace_a_missing_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source"
            source.mkdir()

            with self.assertRaises(FileNotFoundError):
                update_draft_json(CandidateDraft("temple.jpg"), root / "local_drafts" / "missing.json", source)


if __name__ == "__main__":
    unittest.main()
