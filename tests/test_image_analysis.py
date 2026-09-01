import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from stock_photo_scout.image_analysis import analyze_candidate, analysis_from_json, analysis_observations, analysis_to_json, save_analysis_json
from stock_photo_scout.visual_signals import VisualSignalPolicy


class FakeDecoder:
    def __init__(self) -> None:
        self.paths = []

    def decode_luminance(self, source_path: Path):
        self.paths.append(source_path)
        return [
            [0, 0, 0, 0, 0],
            [0, 100, 100, 100, 0],
            [0, 100, 255, 100, 0],
            [0, 100, 100, 100, 0],
            [0, 0, 0, 0, 0],
        ]


class CandidateAnalysisTests(unittest.TestCase):
    def test_requires_consent_before_decoder_is_called(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "photos"
            source.mkdir()
            (source / "photo.jpg").write_bytes(b"fake image")
            decoder = FakeDecoder()

            with self.assertRaises(PermissionError):
                analyze_candidate(source, "photo.jpg", decoder, consent=False)
            self.assertEqual(decoder.paths, [])

    def test_injected_decoder_runs_only_after_path_validation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "photos"
            source.mkdir()
            image = source / "photo.jpg"
            original = b"fake image"
            image.write_bytes(original)
            decoder = FakeDecoder()

            result = analyze_candidate(
                source,
                "photo.jpg",
                decoder,
                consent=True,
                policy=VisualSignalPolicy(max_dark_clip_ratio=0.10),
            )
            self.assertEqual(result.relative_path, "photo.jpg")
            self.assertEqual(result.decoder_name, "FakeDecoder")
            self.assertEqual(decoder.paths, [image.resolve()])
            self.assertGreater(result.report.sharpness_proxy, 0)
            self.assertEqual(image.read_bytes(), original)

    def test_rejects_unsafe_candidate_before_decoder(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            source = Path(td) / "photos"
            source.mkdir()
            decoder = FakeDecoder()
            with self.assertRaises(ValueError):
                analyze_candidate(source, "../outside.jpg", decoder, consent=True)
            with self.assertRaises(ValueError):
                analyze_candidate(source, "C:outside.jpg", decoder, consent=True)
            self.assertEqual(decoder.paths, [])

    def test_analysis_serialization_and_external_save(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "photos"
            source.mkdir()
            (source / "photo.jpg").write_bytes(b"fake image")
            result = analyze_candidate(source, "photo.jpg", FakeDecoder(), consent=True)
            destination = root / "local_analysis" / "photo.json"
            save_analysis_json(result, destination, source)
            serialized = destination.read_text(encoding="utf-8")
            self.assertEqual(json.loads(serialized)["schema_version"], 1)
            self.assertEqual(serialized, analysis_to_json(result))
            self.assertEqual(analysis_from_json(serialized), result)
            self.assertNotIn(str(source), serialized)
            with self.assertRaises(FileExistsError):
                save_analysis_json(result, destination, source)

    def test_observations_are_factual_and_explainable(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "photos"
            source.mkdir()
            (source / "photo.jpg").write_bytes(b"fake image")
            result = analyze_candidate(source, "photo.jpg", FakeDecoder(), consent=True)
            text = "\n".join(analysis_observations(result))
            self.assertIn("Mean luminance:", text)
            self.assertIn("Sharpness proxy:", text)
            self.assertNotIn("accepted", text.lower())
            self.assertNotIn("dreamstime-ready", text.lower())


if __name__ == "__main__":
    unittest.main()
