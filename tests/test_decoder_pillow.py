import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from stock_photo_scout.decoder_pillow import ImageTooLargeError, PillowLuminanceDecoder, _bounded_dimensions


class FakeImage:
    def __init__(self, size, data):
        self.size = size
        self._data = tuple(data)
        self.resize_calls = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def convert(self, mode):
        if mode != "L":
            raise AssertionError("expected luminance conversion")
        return self

    def resize(self, size, resample=None):
        self.resize_calls.append((size, resample))
        # Synthetic tests use constant luminance, so resizing can safely synthesize
        # the expected output length without relying on a real image library.
        value = int(self._data[0]) if self._data else 0
        return FakeImage(size, [value] * (size[0] * size[1]))

    def getdata(self):
        return self._data


class FakeModule:
    BILINEAR = 2

    def __init__(self, image):
        self.image = image
        self.opened = []

    def open(self, path):
        self.opened.append(path)
        return self.image


class PillowAdapterTests(unittest.TestCase):
    def test_decodes_injected_backend_without_real_dependency(self):
        image = FakeImage((3, 2), [0, 10, 20, 30, 40, 50])
        module = FakeModule(image)
        decoder = PillowLuminanceDecoder(image_module=module)

        rows = decoder.decode_luminance(Path("synthetic.jpg"))

        self.assertEqual(rows, ((0, 10, 20), (30, 40, 50)))
        self.assertEqual(module.opened, [Path("synthetic.jpg")])

    def test_downsamples_large_dimensions_to_configured_bound(self):
        image = FakeImage((4000, 2000), [100] * (4000 * 2000))
        module = FakeModule(image)
        decoder = PillowLuminanceDecoder(max_analysis_dimension=1000, image_module=module)

        rows = decoder.decode_luminance(Path("synthetic.jpg"))

        self.assertEqual((len(rows[0]), len(rows)), (1000, 500))
        self.assertEqual(image.resize_calls[0][0], (1000, 500))

    def test_rejects_source_above_configured_pixel_limit_before_extracting_grid(self):
        image = FakeImage((100, 100), [1] * 10000)
        decoder = PillowLuminanceDecoder(max_source_pixels=9999, image_module=FakeModule(image))
        with self.assertRaises(ImageTooLargeError):
            decoder.decode_luminance(Path("synthetic.jpg"))

    def test_bounded_dimensions_preserves_aspect_ratio(self):
        self.assertEqual(_bounded_dimensions(4000, 2000, 1000), (1000, 500))
        self.assertEqual(_bounded_dimensions(800, 600, 1000), (800, 600))

    def test_rejects_invalid_safety_configuration(self):
        with self.assertRaises(ValueError):
            PillowLuminanceDecoder(max_source_pixels=0)
        with self.assertRaises(ValueError):
            PillowLuminanceDecoder(max_analysis_dimension=0)


if __name__ == "__main__":
    unittest.main()
