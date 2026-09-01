import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from stock_photo_scout.visual_signals import VisualSignalPolicy, analyze_luminance_grid


class VisualSignalTests(unittest.TestCase):
    def test_uniform_grid_has_zero_detail_proxies(self) -> None:
        report = analyze_luminance_grid([[128] * 5 for _ in range(5)])
        self.assertEqual(report.mean_luminance, 128)
        self.assertEqual(report.dark_clip_ratio, 0)
        self.assertEqual(report.bright_clip_ratio, 0)
        self.assertEqual(report.sharpness_proxy, 0)
        self.assertEqual(report.noise_proxy, 0)
        self.assertEqual(report.prompts, ())

    def test_checker_pattern_produces_nonzero_detail_signals(self) -> None:
        grid = [[0 if (x + y) % 2 == 0 else 255 for x in range(5)] for y in range(5)]
        report = analyze_luminance_grid(grid)
        self.assertGreater(report.sharpness_proxy, 0)
        self.assertGreater(report.noise_proxy, 0)
        self.assertGreater(report.dark_clip_ratio, 0)
        self.assertGreater(report.bright_clip_ratio, 0)

    def test_prompts_exist_only_when_caller_configures_thresholds(self) -> None:
        grid = [[0] * 5 for _ in range(5)]
        no_thresholds = analyze_luminance_grid(grid)
        self.assertEqual(no_thresholds.prompts, ())

        configured = analyze_luminance_grid(
            grid,
            VisualSignalPolicy(max_dark_clip_ratio=0.10, min_sharpness_proxy=1),
        )
        codes = {prompt.code for prompt in configured.prompts}
        self.assertIn("dark_clipping_above_configured_limit", codes)
        self.assertIn("sharpness_proxy_below_configured_limit", codes)

    def test_rejects_invalid_grid_and_policy(self) -> None:
        with self.assertRaises(ValueError):
            analyze_luminance_grid([])
        with self.assertRaises(ValueError):
            analyze_luminance_grid([[1, 2], [3]])
        with self.assertRaises(ValueError):
            analyze_luminance_grid([[256]])
        with self.assertRaises(ValueError):
            VisualSignalPolicy(dark_clip_level=254, bright_clip_level=253)


if __name__ == "__main__":
    unittest.main()
