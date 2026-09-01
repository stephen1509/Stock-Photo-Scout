import json
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from stock_photo_scout.preflight import build_preflight_packet, preflight_to_json, preflight_to_text
from stock_photo_scout.preparation import PreparationRecord


class PreflightPacketTests(unittest.TestCase):
    def test_incomplete_packet_explains_every_local_blocker(self) -> None:
        packet = build_preflight_packet(
            PreparationRecord("photo.jpg"),
            candidate_state="shortlist",
            unresolved_rights_prompts=("Review recognizable people.",),
            preview_integrity_confirmed=False,
            current_requirements_reviewed=False,
        )
        self.assertFalse(packet.local_packet_complete)
        text = preflight_to_text(packet)
        self.assertIn("Candidate state is 'shortlist'", text)
        self.assertIn("Unresolved people/property/logo/release observations", text)
        self.assertIn("integrity check does not match", text)
        self.assertIn("requirements have not been re-confirmed", text)
        self.assertIn("does not upload, submit", text)

    def test_complete_local_packet_still_does_not_claim_marketplace_acceptance(self) -> None:
        preparation = PreparationRecord(
            "photo.jpg",
            title="Temple at dawn",
            description="Historic temple exterior at dawn",
            keywords=("temple", "dawn", "Japan"),
            categories=("architecture",),
            route="editorial",
            editor_target="darktable",
            working_export_relative_path="exports/photo-final.jpg",
        )
        packet = build_preflight_packet(
            preparation,
            candidate_state="submission-ready",
            preview_integrity_confirmed=True,
            current_requirements_reviewed=True,
        )
        self.assertTrue(packet.local_packet_complete)
        self.assertEqual(packet.blockers, ())
        self.assertIn("does not upload, submit", preflight_to_text(packet))

    def test_json_is_deterministic_and_contains_no_absolute_source_root(self) -> None:
        packet = build_preflight_packet(
            PreparationRecord(
                "nested/photo.jpg",
                title="Temple",
                description="Temple exterior",
                keywords=("temple",),
                route="commercial",
            ),
            candidate_state="submission-ready",
            current_requirements_reviewed=True,
        )
        serialized = preflight_to_json(packet)
        payload = json.loads(serialized)
        self.assertEqual(payload["schema_version"], 1)
        self.assertEqual(payload["preflight"]["relative_path"], "nested/photo.jpg")
        self.assertNotIn("C:\\", serialized)
        self.assertNotIn("/home/", serialized)


if __name__ == "__main__":
    unittest.main()
