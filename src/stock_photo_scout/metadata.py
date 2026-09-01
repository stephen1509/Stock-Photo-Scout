"""Read-only extraction of explicitly supported technical image metadata."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import BinaryIO, Literal

from .exif import ExifMetadata, parse_tiff_metadata


MetadataStatus = Literal["extracted", "unsupported", "invalid", "error"]

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
_JPEG_START_OF_FRAME_MARKERS = frozenset(
    {
        0xC0,
        0xC1,
        0xC2,
        0xC3,
        0xC5,
        0xC6,
        0xC7,
        0xC9,
        0xCA,
        0xCB,
        0xCD,
        0xCE,
        0xCF,
    }
)
_JPEG_STANDALONE_MARKERS = frozenset({0x01, *range(0xD0, 0xDA)})
_MAX_JPEG_HEADER_BYTES = 1024 * 1024


def _default_exif() -> ExifMetadata:
    return ExifMetadata(status="not_found")


@dataclass(frozen=True)
class TechnicalMetadata:
    """Technical facts read from an image header without changing the file."""

    detected_format: str | None
    width_pixels: int | None
    height_pixels: int | None
    status: MetadataStatus
    message: str | None = None
    exif: ExifMetadata = field(default_factory=_default_exif)


def extract_technical_metadata(image_path: str | Path) -> TechnicalMetadata:
    """Read bounded technical metadata from a regular, non-symlink image file."""

    path = Path(image_path).expanduser()
    if path.is_symlink():
        raise ValueError(f"Refusing to inspect a symlink: {path}")
    if not path.is_file():
        raise FileNotFoundError(f"Image file does not exist: {path}")

    suffix = path.suffix.lower()
    if suffix not in {".jpeg", ".jpg", ".png", ".tif", ".tiff"}:
        format_label = suffix or "files without a suffix"
        return TechnicalMetadata(
            detected_format=None,
            width_pixels=None,
            height_pixels=None,
            status="unsupported",
            message=f"Metadata extraction is not implemented for {format_label}.",
            exif=ExifMetadata(status="unsupported", message="EXIF extraction is not implemented for this format."),
        )

    try:
        with path.open("rb") as stream:
            if suffix == ".png":
                return _extract_png_metadata(stream)
            if suffix in {".tif", ".tiff"}:
                return _extract_tiff_metadata(stream)
            return _extract_jpeg_metadata(stream)
    except OSError as error:
        error_name = type(error).__name__
        return TechnicalMetadata(
            detected_format=None,
            width_pixels=None,
            height_pixels=None,
            status="error",
            message=f"Could not read image header ({error_name}).",
            exif=ExifMetadata(status="error", message=f"Could not read EXIF metadata ({error_name})."),
        )


def _extract_png_metadata(stream: BinaryIO) -> TechnicalMetadata:
    png_exif = ExifMetadata(status="unsupported", message="PNG EXIF extraction is not implemented.")
    header = stream.read(24)
    if (
        len(header) < 24
        or header[:8] != _PNG_SIGNATURE
        or int.from_bytes(header[8:12], "big") != 13
        or header[12:16] != b"IHDR"
    ):
        return TechnicalMetadata(None, None, None, "invalid", "Valid PNG IHDR header not found.", png_exif)

    width = int.from_bytes(header[16:20], "big")
    height = int.from_bytes(header[20:24], "big")
    if width == 0 or height == 0:
        return TechnicalMetadata("PNG", None, None, "invalid", "PNG dimensions must be positive.", png_exif)
    return TechnicalMetadata("PNG", width, height, "extracted", exif=png_exif)


def _extract_tiff_metadata(stream: BinaryIO) -> TechnicalMetadata:
    stream.seek(0, 2)
    span_bytes = stream.tell()
    stream.seek(0)
    parsed = parse_tiff_metadata(stream, base_offset=0, span_bytes=span_bytes)
    if not parsed.recognized:
        return TechnicalMetadata(None, None, None, "invalid", "Valid TIFF header not found.", parsed.exif)
    if parsed.width_pixels is None or parsed.height_pixels is None:
        return TechnicalMetadata("TIFF", None, None, "invalid", "TIFF dimensions were not found.", parsed.exif)
    if parsed.width_pixels == 0 or parsed.height_pixels == 0:
        return TechnicalMetadata("TIFF", None, None, "invalid", "TIFF dimensions must be positive.", parsed.exif)
    return TechnicalMetadata(
        "TIFF",
        parsed.width_pixels,
        parsed.height_pixels,
        "extracted",
        exif=parsed.exif,
    )


def _extract_jpeg_metadata(stream: BinaryIO) -> TechnicalMetadata:
    exif = ExifMetadata(status="not_found")
    if stream.read(2) != b"\xff\xd8":
        return _invalid_jpeg("JPEG start-of-image marker not found.")

    bytes_examined = 2
    while bytes_examined < _MAX_JPEG_HEADER_BYTES:
        prefix = stream.read(1)
        bytes_examined += len(prefix)
        if prefix != b"\xff":
            return _invalid_jpeg("Invalid JPEG marker sequence.", exif)

        marker_byte = stream.read(1)
        bytes_examined += len(marker_byte)
        while marker_byte == b"\xff":
            marker_byte = stream.read(1)
            bytes_examined += len(marker_byte)
        if not marker_byte:
            return _invalid_jpeg("JPEG header ended unexpectedly.", exif)

        marker = marker_byte[0]
        if marker == 0x00:
            return _invalid_jpeg("Unexpected stuffed byte in JPEG header.", exif)
        if marker in _JPEG_STANDALONE_MARKERS:
            if marker == 0xD9:
                break
            continue
        if marker == 0xDA:
            break

        length_bytes = stream.read(2)
        bytes_examined += len(length_bytes)
        if len(length_bytes) != 2:
            return _invalid_jpeg("JPEG segment length is truncated.", exif)
        segment_length = int.from_bytes(length_bytes, "big")
        if segment_length < 2:
            return _invalid_jpeg("JPEG segment length is invalid.", exif)

        payload_length = segment_length - 2
        if bytes_examined + payload_length > _MAX_JPEG_HEADER_BYTES:
            break
        segment_start = stream.tell()

        if marker in _JPEG_START_OF_FRAME_MARKERS:
            if payload_length < 6:
                return _invalid_jpeg("JPEG frame header is truncated.", exif)
            frame_header = stream.read(6)
            if len(frame_header) != 6:
                return _invalid_jpeg("JPEG frame header is truncated.", exif)
            component_count = frame_header[5]
            if component_count == 0 or payload_length != 6 + (3 * component_count):
                return _invalid_jpeg("JPEG frame header length is invalid.", exif)
            height = int.from_bytes(frame_header[1:3], "big")
            width = int.from_bytes(frame_header[3:5], "big")
            if width == 0 or height == 0:
                return _invalid_jpeg("JPEG dimensions must be positive.", exif)
            return TechnicalMetadata("JPEG", width, height, "extracted", exif=exif)

        if marker == 0xE1 and payload_length >= 6 and exif.status != "extracted":
            signature = stream.read(6)
            if signature == b"Exif\x00\x00":
                parsed = parse_tiff_metadata(
                    stream,
                    base_offset=segment_start + 6,
                    span_bytes=payload_length - 6,
                )
                exif = parsed.exif

        stream.seek(segment_start + payload_length)
        bytes_examined += payload_length

    return _invalid_jpeg("JPEG dimensions were not found within the bounded header scan.", exif)


def _invalid_jpeg(message: str, exif: ExifMetadata | None = None) -> TechnicalMetadata:
    return TechnicalMetadata(
        "JPEG" if exif is not None else None,
        None,
        None,
        "invalid",
        message,
        exif or ExifMetadata(status="invalid", message="EXIF was not inspected because the JPEG header is invalid."),
    )
