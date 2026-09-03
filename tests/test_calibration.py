import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from stock_photo_scout.calibration import (
    calibration_records_from_json,
    calibration_to_text,
    summarize_calibration,
)


class CalibrationTests(unittest.TestCase):
    def test_parses_and_summarizes_human_labels(self):
        records = calibration_records_from_json('''{
          "records": [
            {"filename":"a.jpg","technical_suitability_label":"good","mean_luminance":100,"dark_clip_ratio":0.1,"bright_clip_ratio":0.2,"sharpness_proxy":10,"noise_proxy":2},
            {"filename":"b.jpg","technical_suitability_label":"good","mean_luminance":120,"dark_clip_ratio":0.3,"bright_clip_ratio":0.4,"sharpness_proxy":14,"noise_proxy":4},
            {"filename":"c.jpg","technical_suitability_label":"needs_editing","mean_luminance":90,"dark_clip_ratio":0,"bright_clip_ratio":0.1,"sharpness_proxy":8,"noise_proxy":1}
          ]
        }''')
        summaries = summarize_calibration(records)
        self.assertEqual([item.label for item in summaries], ["good", "needs_editing"])
        self.assertEqual(summaries[0].count, 2)
        self.assertEqual(summaries[0].mean_luminance, 110)
        self.assertEqual(summaries[0].sharpness_proxy, 12)
        self.assertIn("advisory only", calibration_to_text(summaries))

    def test_rejects_missing_metric(self):
        with self.assertRaises(ValueError):
            calibration_records_from_json('{"records":[{"filename":"a.jpg","technical_suitability_label":"good"}]}')


if __name__ == "__main__":
    unittest.main()
