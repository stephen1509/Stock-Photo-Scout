import json
import math
import sys
import unittest
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
from stock_photo_scout.image_analysis import analysis_from_json


def payload():
    return {"schema_version": 1, "analysis": {"relative_path": "photo.jpg", "decoder_name": "FakeDecoder", "report": {"width": 1600, "height": 1200, "mean_luminance": 120.0, "dark_clip_ratio": .01, "bright_clip_ratio": .02, "sharpness_proxy": 5.0, "noise_proxy": 2.0, "prompts": []}}}

class AnalysisValidation006Tests(unittest.TestCase):
    def test_non_finite_metric_rejected(self):
        data = payload(); data["analysis"]["report"]["noise_proxy"] = math.nan
        with self.assertRaises(ValueError): analysis_from_json(json.dumps(data))
    def test_ratio_out_of_range_rejected(self):
        data = payload(); data["analysis"]["report"]["bright_clip_ratio"] = 1.01
        with self.assertRaises(ValueError): analysis_from_json(json.dumps(data))
    def test_zero_dimension_rejected(self):
        data = payload(); data["analysis"]["report"]["width"] = 0
        with self.assertRaises(ValueError): analysis_from_json(json.dumps(data))
    def test_boolean_dimension_rejected(self):
        data = payload(); data["analysis"]["report"]["width"] = True
        with self.assertRaises(ValueError): analysis_from_json(json.dumps(data))
    def test_malformed_prompt_rejected_instead_of_silently_dropped(self):
        data = payload(); data["analysis"]["report"]["prompts"] = ["bad"]
        with self.assertRaises(ValueError): analysis_from_json(json.dumps(data))
    def test_blank_decoder_rejected(self):
        data = payload(); data["analysis"]["decoder_name"] = ""
        with self.assertRaises(ValueError): analysis_from_json(json.dumps(data))

if __name__ == "__main__": unittest.main()
