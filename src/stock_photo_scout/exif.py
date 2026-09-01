"""Bounded, privacy-conscious parsing of selected TIFF/EXIF fields."""

from __future__ import annotations

from dataclasses import dataclass
from typing import BinaryIO, Literal


ExifStatus = Literal["extracted", "not_found", "unsupported", "invalid", "error"]

_MAX_IFD_ENTRIES = 128
_MAX_METADATA_BYTES_READ = 64 * 1024
_MAX_METADATA_OFFSET = 1024 * 1024
_MAX_TEXT_BYTES = 512

_TYPE_ASCII = 2
_TYPE_SHORT = 3
_TYPE_LONG = 4
_TYPE_SIZES = {_TYPE_ASCII: 1, _TYPE_SHORT: 2, _TYPE_LONG: 4}

_TAG_IMAGE_WIDTH = 0x0100
_TAG_IMAGE_HEIGHT = 0x0101
_TAG_CAMERA_MAKE = 0x010F
_TAG_CAMERA_MODEL = 0x0110
_TAG_ORIENTATION = 0x0112
_TAG_EXIF_IFD = 0x8769
_TAG_CAPTURED_AT_ORIGINAL = 0x9003
_TAG_LENS_MODEL = 0xA434


@dataclass(frozen=True)
class ExifMetadata:
    """A deliberately small EXIF subset that excludes location and owner IDs."""

    status: ExifStatus
    orientation: int | None = None
    captured_at_original: str | None = None
    camera_make: str | None = None
    camera_model: str | None = None
    lens_model: str | None = None
    message: str | None = None


@dataclass(frozen=True)
class ParsedTiff:
    """Selected TIFF baseline and EXIF values returned by the bounded parser."""

    recognized: bool
    width_pixels: int | None
    height_pixels: int | None
    exif: ExifMetadata


@dataclass(frozen=True)
class _IfdEntry:
    type_id: int
    count: int
    value_field: bytes


class _TiffParseError(ValueError):
    pass


class _TiffReader:
    def __init__(self, stream: BinaryIO, base_offset: int, span_bytes: int) -> None:
        if base_offset < 0 or span_bytes < 0:
            raise _TiffParseError("TIFF metadata bounds are invalid.")
        self._stream = stream
        self._base_offset = base_offset
        self._span_bytes = min(span_bytes, _MAX_METADATA_OFFSET)
        self._bytes_read = 0
        self.byte_order = "big"

    def read_at(self, relative_offset: int, size: int) -> bytes:
        if relative_offset < 0 or size < 0 or relative_offset + size > self._span_bytes:
            raise _TiffParseError("TIFF metadata points outside the bounded segment.")
        if self._bytes_read + size > _MAX_METADATA_BYTES_READ:
            raise _TiffParseError("TIFF metadata exceeds the read budget.")

        current_position = self._stream.tell()
        try:
            self._stream.seek(self._base_offset + relative_offset)
            data = self._stream.read(size)
        except OSError as error:
            raise _TiffParseError("TIFF metadata could not be read.") from error
        finally:
            self._stream.seek(current_position)

        self._bytes_read += len(data)
        if len(data) != size:
            raise _TiffParseError("TIFF metadata is truncated.")
        return data


def parse_tiff_metadata(stream: BinaryIO, *, base_offset: int, span_bytes: int) -> ParsedTiff:
    """Read selected TIFF/EXIF fields without reading image pixel blocks."""

    recognized = False
    try:
        reader = _TiffReader(stream, base_offset, span_bytes)
        header = reader.read_at(0, 8)
        if header[:2] == b"II":
            reader.byte_order = "little"
        elif header[:2] == b"MM":
            reader.byte_order = "big"
        else:
            raise _TiffParseError("TIFF byte-order marker not found.")
        if int.from_bytes(header[2:4], reader.byte_order) != 42:
            raise _TiffParseError("TIFF header marker is invalid.")
        recognized = True

        first_ifd_offset = int.from_bytes(header[4:8], reader.byte_order)
        ifd0 = _read_ifd(reader, first_ifd_offset)
        width = _read_unsigned(ifd0.get(_TAG_IMAGE_WIDTH), reader)
        height = _read_unsigned(ifd0.get(_TAG_IMAGE_HEIGHT), reader)
        orientation = _read_unsigned(ifd0.get(_TAG_ORIENTATION), reader)
        if orientation is not None and orientation not in range(1, 9):
            raise _TiffParseError("EXIF orientation is outside the defined range.")

        camera_make = _read_ascii(ifd0.get(_TAG_CAMERA_MAKE), reader)
        camera_model = _read_ascii(ifd0.get(_TAG_CAMERA_MODEL), reader)
        captured_at_original = None
        lens_model = None

        exif_ifd_offset = _read_unsigned(ifd0.get(_TAG_EXIF_IFD), reader)
        if exif_ifd_offset is not None:
            exif_ifd = _read_ifd(reader, exif_ifd_offset)
            captured_at_original = _read_ascii(exif_ifd.get(_TAG_CAPTURED_AT_ORIGINAL), reader)
            lens_model = _read_ascii(exif_ifd.get(_TAG_LENS_MODEL), reader)

        selected_values = (orientation, captured_at_original, camera_make, camera_model, lens_model)
        exif_status: ExifStatus = "extracted" if any(value is not None for value in selected_values) else "not_found"
        exif = ExifMetadata(
            status=exif_status,
            orientation=orientation,
            captured_at_original=captured_at_original,
            camera_make=camera_make,
            camera_model=camera_model,
            lens_model=lens_model,
        )
        return ParsedTiff(True, width, height, exif)
    except (_TiffParseError, OSError):
        return ParsedTiff(
            recognized,
            None,
            None,
            ExifMetadata(status="invalid", message="Selected TIFF/EXIF metadata is malformed or outside safe bounds."),
        )


def _read_ifd(reader: _TiffReader, relative_offset: int) -> dict[int, _IfdEntry]:
    if relative_offset == 0:
        raise _TiffParseError("TIFF image file directory is missing.")
    entry_count = int.from_bytes(reader.read_at(relative_offset, 2), reader.byte_order)
    if entry_count > _MAX_IFD_ENTRIES:
        raise _TiffParseError("TIFF image file directory has too many entries.")

    entries: dict[int, _IfdEntry] = {}
    for index in range(entry_count):
        raw_entry = reader.read_at(relative_offset + 2 + (12 * index), 12)
        tag = int.from_bytes(raw_entry[0:2], reader.byte_order)
        entries[tag] = _IfdEntry(
            type_id=int.from_bytes(raw_entry[2:4], reader.byte_order),
            count=int.from_bytes(raw_entry[4:8], reader.byte_order),
            value_field=raw_entry[8:12],
        )
    return entries


def _entry_data(entry: _IfdEntry, reader: _TiffReader) -> bytes:
    type_size = _TYPE_SIZES.get(entry.type_id)
    if type_size is None or entry.count < 1:
        raise _TiffParseError("Selected TIFF field has an unsupported type or count.")
    total_size = type_size * entry.count
    if total_size > _MAX_TEXT_BYTES:
        raise _TiffParseError("Selected TIFF field exceeds the value-size limit.")
    if total_size <= 4:
        return entry.value_field[:total_size]
    value_offset = int.from_bytes(entry.value_field, reader.byte_order)
    return reader.read_at(value_offset, total_size)


def _read_unsigned(entry: _IfdEntry | None, reader: _TiffReader) -> int | None:
    if entry is None:
        return None
    if entry.type_id not in {_TYPE_SHORT, _TYPE_LONG} or entry.count != 1:
        raise _TiffParseError("Selected TIFF numeric field has an unsupported representation.")
    return int.from_bytes(_entry_data(entry, reader), reader.byte_order)


def _read_ascii(entry: _IfdEntry | None, reader: _TiffReader) -> str | None:
    if entry is None:
        return None
    if entry.type_id != _TYPE_ASCII:
        raise _TiffParseError("Selected EXIF text field is not ASCII.")
    try:
        value = _entry_data(entry, reader).split(b"\x00", 1)[0].decode("ascii").strip()
    except UnicodeDecodeError as error:
        raise _TiffParseError("Selected EXIF text field contains invalid ASCII.") from error
    return value or None
