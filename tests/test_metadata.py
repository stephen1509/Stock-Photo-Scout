import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from stock_photo_scout.metadata import extract_technical_metadata


def minimal_png(width: int, height: int) -> bytes:
    return b"\x89PNG\r\n\x1a\n" + (13).to_bytes(4, "big") + b"IHDR" + width.to_bytes(4, "big") + height.to_bytes(4, "big")


def minimal_jpeg(width: int, height: int) -> bytes:
    frame_payload = b"\x08" + height.to_bytes(2, "big") + width.to_bytes(2, "big") + b"\x01\x01\x11\x00"
    return b"\xff\xd8\xff\xc0" + (len(frame_payload) + 2).to_bytes(2, "big") + frame_payload + b"\xff\xd9"


def synthetic_exif_tiff(width: int, height: int, byte_order: str = "little") -> bytes:
    byte_order_marker = b"II" if byte_order == "little" else b"MM"
    make = b"OpenAI Camera Co\x00"
    model = b"Synthetic 1\x00"
    captured_at = b"2026:08:31 12:34:56\x00"
    lens = b"Test Lens 50mm\x00"

    ifd0_offset = 8
    ifd0_entry_count = 6
    ifd0_size = 2 + (12 * ifd0_entry_count) + 4
    make_offset = ifd0_offset + ifd0_size
    model_offset = make_offset + len(make)
    exif_ifd_offset = model_offset + len(model)
    exif_ifd_entry_count = 2
    exif_ifd_size = 2 + (12 * exif_ifd_entry_count) + 4
    captured_at_offset = exif_ifd_offset + exif_ifd_size
    lens_offset = captured_at_offset + len(captured_at)

    def ifd_entry(tag: int, type_id: int, count: int, value_field: bytes) -> bytes:
        return (
            tag.to_bytes(2, byte_order)
            + type_id.to_bytes(2, byte_order)
            + count.to_bytes(4, byte_order)
            + value_field
        )

    def short_value(value: int) -> bytes:
        return value.to_bytes(2, byte_order) + b"\x00\x00"

    def long_value(value: int) -> bytes:
        return value.to_bytes(4, byte_order)

    ifd0_entries = [
        ifd_entry(0x0100, 4, 1, long_value(width)),
        ifd_entry(0x0101, 4, 1, long_value(height)),
        ifd_entry(0x010F, 2, len(make), long_value(make_offset)),
        ifd_entry(0x0110, 2, len(model), long_value(model_offset)),
        ifd_entry(0x0112, 3, 1, short_value(6)),
        ifd_entry(0x8769, 4, 1, long_value(exif_ifd_offset)),
    ]
    exif_ifd_entries = [
        ifd_entry(0x9003, 2, len(captured_at), long_value(captured_at_offset)),
        ifd_entry(0xA434, 2, len(lens), long_value(lens_offset)),
    ]

    header = byte_order_marker + (42).to_bytes(2, byte_order) + ifd0_offset.to_bytes(4, byte_order)
    ifd0 = ifd0_entry_count.to_bytes(2, byte_order) + b"".join(ifd0_entries) + b"\x00\x00\x00\x00"
    exif_ifd = exif_ifd_entry_count.to_bytes(2, byte_order) + b"".join(exif_ifd_entries) + b"\x00\x00\x00\x00"
    return header + ifd0 + make + model + exif_ifd + captured_at + lens


def jpeg_with_exif(width: int, height: int, tiff_payload: bytes | None = None) -> bytes:
    exif_payload = b"Exif\x00\x00" + (tiff_payload or synthetic_exif_tiff(width, height))
    app1_segment = b"\xff\xe1" + (len(exif_payload) + 2).to_bytes(2, "big") + exif_payload
    return b"\xff\xd8" + app1_segment + minimal_jpeg(width, height)[2:]


class ExtractTechnicalMetadataTests(unittest.TestCase):
    def test_extracts_png_dimensions_without_changing_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "sample.png"
            path.write_bytes(minimal_png(4032, 3024))
            before = (path.read_bytes(), path.stat().st_mtime_ns)

            metadata = extract_technical_metadata(path)

            after = (path.read_bytes(), path.stat().st_mtime_ns)
            self.assertEqual((metadata.detected_format, metadata.width_pixels, metadata.height_pixels), ("PNG", 4032, 3024))
            self.assertEqual(metadata.status, "extracted")
            self.assertEqual(before, after)

    def test_extracts_jpeg_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "sample.jpg"
            application_segment = b"synthetic app data"
            jpeg = b"\xff\xd8\xff\xe0" + (len(application_segment) + 2).to_bytes(2, "big") + application_segment
            path.write_bytes(jpeg + minimal_jpeg(6000, 4000)[2:])

            metadata = extract_technical_metadata(path)

            self.assertEqual((metadata.detected_format, metadata.width_pixels, metadata.height_pixels), ("JPEG", 6000, 4000))
            self.assertEqual(metadata.status, "extracted")

    def test_extracts_selected_exif_fields_from_jpeg(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "sample.jpg"
            path.write_bytes(jpeg_with_exif(6000, 4000))

            metadata = extract_technical_metadata(path)

            self.assertEqual(metadata.status, "extracted")
            self.assertEqual(metadata.exif.status, "extracted")
            self.assertEqual(metadata.exif.orientation, 6)
            self.assertEqual(metadata.exif.captured_at_original, "2026:08:31 12:34:56")
            self.assertEqual(metadata.exif.camera_make, "OpenAI Camera Co")
            self.assertEqual(metadata.exif.camera_model, "Synthetic 1")
            self.assertEqual(metadata.exif.lens_model, "Test Lens 50mm")
            self.assertFalse(any("gps" in field.casefold() for field in metadata.exif.__dataclass_fields__))

    def test_extracts_dimensions_and_exif_from_big_endian_tiff(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "sample.tiff"
            path.write_bytes(synthetic_exif_tiff(5000, 3333, byte_order="big"))

            metadata = extract_technical_metadata(path)

            self.assertEqual((metadata.detected_format, metadata.width_pixels, metadata.height_pixels), ("TIFF", 5000, 3333))
            self.assertEqual(metadata.status, "extracted")
            self.assertEqual(metadata.exif.status, "extracted")
            self.assertEqual(metadata.exif.orientation, 6)

    def test_preserves_dimensions_when_exif_is_outside_safe_bounds(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "sample.jpg"
            malformed_tiff = b"II\x2a\x00" + (2_000_000).to_bytes(4, "little")
            path.write_bytes(jpeg_with_exif(6000, 4000, malformed_tiff))

            metadata = extract_technical_metadata(path)

            self.assertEqual((metadata.width_pixels, metadata.height_pixels), (6000, 4000))
            self.assertEqual(metadata.status, "extracted")
            self.assertEqual(metadata.exif.status, "invalid")

    def test_reports_unsupported_suffix_without_guessing_format(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "sample.heic"
            path.write_bytes(b"synthetic fixture")

            metadata = extract_technical_metadata(path)

            self.assertEqual(metadata.status, "unsupported")
            self.assertIsNone(metadata.detected_format)
            self.assertIsNone(metadata.width_pixels)

    def test_reports_invalid_content_for_supported_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "sample.jpg"
            path.write_bytes(b"not a jpeg")

            metadata = extract_technical_metadata(path)

            self.assertEqual(metadata.status, "invalid")
            self.assertIsNone(metadata.detected_format)


if __name__ == "__main__":
    unittest.main()
