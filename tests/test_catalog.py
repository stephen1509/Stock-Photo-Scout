import json
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from stock_photo_scout.catalog import CATALOG_SCHEMA_VERSION, build_catalog, catalog_to_json, save_catalog_json
from test_metadata import minimal_png, synthetic_exif_tiff


class BuildCatalogTests(unittest.TestCase):
    def test_builds_relative_deterministic_catalog_without_changing_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory)
            nested = source / "nested"
            nested.mkdir()
            (source / "Zulu.heic").write_bytes(b"synthetic unsupported fixture")
            (nested / "alpha.tiff").write_bytes(synthetic_exif_tiff(1200, 800))
            before = {path.relative_to(source).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns) for path in source.rglob("*") if path.is_file()}

            catalog = build_catalog(source)
            serialized = catalog_to_json(catalog)

            after = {path.relative_to(source).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns) for path in source.rglob("*") if path.is_file()}
            self.assertEqual(catalog.schema_version, CATALOG_SCHEMA_VERSION)
            self.assertEqual([entry.relative_path for entry in catalog.entries], ["nested/alpha.tiff", "Zulu.heic"])
            self.assertEqual(catalog.entries[0].metadata_status, "extracted")
            self.assertEqual((catalog.entries[0].width_pixels, catalog.entries[0].height_pixels), (1200, 800))
            self.assertEqual(catalog.entries[0].exif.camera_model, "Synthetic 1")
            self.assertEqual(catalog.entries[1].metadata_status, "unsupported")
            self.assertEqual(before, after)
            self.assertNotIn(str(source), serialized)
            self.assertNotIn(str(source), repr(catalog))
            payload = json.loads(serialized)
            self.assertEqual(payload["schema_version"], CATALOG_SCHEMA_VERSION)
            self.assertEqual(payload["entries"][0]["exif"]["orientation"], 6)
            self.assertNotIn("gps", serialized.casefold())

    def test_saves_json_outside_source_without_overwriting(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "source"
            source.mkdir()
            image = source / "sample.png"
            image.write_bytes(minimal_png(1200, 800))
            before = (image.read_bytes(), image.stat().st_mtime_ns)
            catalog = build_catalog(source)
            destination = root / "local_catalogs" / "sample.json"

            saved_path = save_catalog_json(catalog, destination)

            self.assertEqual(saved_path, destination.resolve())
            self.assertEqual(json.loads(destination.read_text(encoding="utf-8"))["entries"][0]["width_pixels"], 1200)
            self.assertEqual(before, (image.read_bytes(), image.stat().st_mtime_ns))

            destination.write_text("do not replace", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                save_catalog_json(catalog, destination)
            self.assertEqual(destination.read_text(encoding="utf-8"), "do not replace")

    def test_refuses_to_save_catalog_inside_source_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory)
            (source / "sample.png").write_bytes(minimal_png(1200, 800))
            catalog = build_catalog(source)
            destination = source / "catalog.json"

            with self.assertRaises(ValueError):
                save_catalog_json(catalog, destination)

            self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
