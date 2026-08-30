import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from stock_photo_scout.scanner import inventory_images


class InventoryImagesTests(unittest.TestCase):
    def test_finds_supported_images_without_changing_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory)
            nested = source / "nested"
            nested.mkdir()
            (source / "Zulu.JPG").write_bytes(b"first")
            (nested / "alpha.png").write_bytes(b"second")
            (source / "notes.txt").write_text("not an image", encoding="utf-8")
            before = {path.relative_to(source).as_posix(): (path.stat().st_size, path.stat().st_mtime_ns) for path in source.rglob("*") if path.is_file()}

            candidates = inventory_images(source)

            after = {path.relative_to(source).as_posix(): (path.stat().st_size, path.stat().st_mtime_ns) for path in source.rglob("*") if path.is_file()}
            self.assertEqual([candidate.relative_path.as_posix() for candidate in candidates], ["nested/alpha.png", "Zulu.JPG"])
            self.assertEqual(before, after)

    def test_rejects_a_file_as_the_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            file_source = Path(temporary_directory) / "image.jpg"
            file_source.write_bytes(b"not decoded")
            with self.assertRaises(NotADirectoryError):
                inventory_images(file_source)


if __name__ == "__main__":
    unittest.main()
