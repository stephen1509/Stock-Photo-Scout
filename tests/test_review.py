import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from stock_photo_scout.catalog import CATALOG_SCHEMA_VERSION, CatalogEntry, LocalCatalog, build_catalog
from stock_photo_scout.exif import ExifMetadata
from stock_photo_scout.review import ReviewPolicy, find_exact_duplicates, review_technical_metadata


class ReviewTechnicalMetadataTests(unittest.TestCase):
    def test_returns_explainable_opt_in_technical_flags(self) -> None:
        catalog = LocalCatalog(
            CATALOG_SCHEMA_VERSION,
            (
                CatalogEntry(
                    relative_path="small.jpg",
                    filename="small.jpg",
                    suffix=".jpg",
                    size_bytes=10,
                    modified_time_ns=1,
                    detected_format="JPEG",
                    width_pixels=800,
                    height_pixels=600,
                    metadata_status="extracted",
                    metadata_message=None,
                    exif=ExifMetadata(status="extracted", orientation=6),
                ),
                CatalogEntry(
                    relative_path="unknown.jpg",
                    filename="unknown.jpg",
                    suffix=".jpg",
                    size_bytes=10,
                    modified_time_ns=1,
                    detected_format=None,
                    width_pixels=None,
                    height_pixels=None,
                    metadata_status="invalid",
                    metadata_message="Synthetic fixture",
                    exif=ExifMetadata(status="invalid"),
                ),
            ),
            Path(tempfile.gettempdir()),
        )

        report = review_technical_metadata(catalog, ReviewPolicy(minimum_pixel_count=1_000_000))

        self.assertEqual(report.reviews[0].pixel_count, 480_000)
        self.assertEqual(
            [flag.code for flag in report.reviews[0].flags],
            ["below_configured_pixel_threshold", "orientation_transform_present"],
        )
        self.assertEqual(
            [flag.code for flag in report.reviews[1].flags],
            ["technical_metadata_unavailable", "dimensions_missing"],
        )

    def test_does_not_apply_pixel_threshold_without_configuration(self) -> None:
        catalog = LocalCatalog(
            CATALOG_SCHEMA_VERSION,
            (
                CatalogEntry(
                    relative_path="small.jpg",
                    filename="small.jpg",
                    suffix=".jpg",
                    size_bytes=10,
                    modified_time_ns=1,
                    detected_format="JPEG",
                    width_pixels=1,
                    height_pixels=1,
                    metadata_status="extracted",
                    metadata_message=None,
                    exif=ExifMetadata(status="not_found"),
                ),
            ),
            Path(tempfile.gettempdir()),
        )

        report = review_technical_metadata(catalog)

        self.assertEqual(report.reviews[0].flags, ())


class ExactDuplicateTests(unittest.TestCase):
    def test_finds_sha256_content_matches_without_changing_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory)
            nested = source / "nested"
            nested.mkdir()
            (source / "alpha.jpg").write_bytes(b"same source bytes")
            (nested / "beta.jpg").write_bytes(b"same source bytes")
            (source / "gamma.jpg").write_bytes(b"different source bytes")
            before = {
                path.relative_to(source).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns)
                for path in source.rglob("*")
                if path.is_file()
            }
            catalog = build_catalog(source)

            report = find_exact_duplicates(catalog, chunk_size=3)

            after = {
                path.relative_to(source).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns)
                for path in source.rglob("*")
                if path.is_file()
            }
            self.assertEqual(len(report.groups), 1)
            self.assertEqual(report.groups[0].relative_paths, ("alpha.jpg", "nested/beta.jpg"))
            self.assertEqual(report.issues, ())
            self.assertEqual(before, after)

    def test_rejects_non_positive_hash_chunk_size(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            catalog = LocalCatalog(CATALOG_SCHEMA_VERSION, (), Path(temporary_directory))

            with self.assertRaises(ValueError):
                find_exact_duplicates(catalog, chunk_size=0)

    def test_reports_a_file_changed_since_cataloging(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            source = Path(temporary_directory)
            changed = source / "changed.jpg"
            changed.write_bytes(b"cataloged source bytes")
            catalog = build_catalog(source)
            changed.write_bytes(b"source bytes changed after cataloging")

            report = find_exact_duplicates(catalog)

            self.assertEqual(report.groups, ())
            self.assertEqual(len(report.issues), 1)
            self.assertEqual(report.issues[0].relative_path, "changed.jpg")


if __name__ == "__main__":
    unittest.main()
