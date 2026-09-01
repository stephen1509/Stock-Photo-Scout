"""Optional bounded Pillow-compatible decoder adapter for Stock Photo Scout.

Pillow is NOT a required project dependency at this checkpoint. The adapter imports
it lazily only when real pixel decoding is explicitly invoked. Tests use an injected
synthetic backend, so CI does not install or contact Pillow.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class DecoderUnavailableError(RuntimeError):
    """Raised when the optional local decoder backend is not installed."""


class ImageTooLargeError(ValueError):
    """Raised before full luminance extraction when dimensions exceed configured bounds."""


class PillowLuminanceDecoder:
    """Decode a bounded, sampled 8-bit luminance grid through a Pillow-compatible API."""

    def __init__(
        self,
        *,
        max_source_pixels: int = 100_000_000,
        max_analysis_dimension: int = 1600,
        image_module: Any | None = None,
    ) -> None:
        if max_source_pixels <= 0:
            raise ValueError("max_source_pixels must be positive.")
        if max_analysis_dimension <= 0:
            raise ValueError("max_analysis_dimension must be positive.")
        self.max_source_pixels = max_source_pixels
        self.max_analysis_dimension = max_analysis_dimension
        self._image_module = image_module

    def decode_luminance(self, source_path: Path):
        """Open read-only, bound dimensions, convert to luminance, and downsample for analysis."""

        image_module = self._image_module or self._import_pillow_image()
        with image_module.open(source_path) as image:
            width, height = image.size
            if width <= 0 or height <= 0:
                raise ValueError("Decoded image dimensions must be positive.")
            if width * height > self.max_source_pixels:
                raise ImageTooLargeError(
                    f"Image has {width * height} pixels, above configured safety limit {self.max_source_pixels}."
                )

            luminance = image.convert("L")
            target_width, target_height = _bounded_dimensions(
                width, height, self.max_analysis_dimension
            )
            if (target_width, target_height) != (width, height):
                resampling = getattr(getattr(image_module, "Resampling", image_module), "BILINEAR")
                luminance = luminance.resize((target_width, target_height), resample=resampling)

            data = tuple(luminance.getdata())
            if len(data) != target_width * target_height:
                raise ValueError("Decoder returned an unexpected number of luminance samples.")
            return tuple(
                tuple(int(value) for value in data[row * target_width : (row + 1) * target_width])
                for row in range(target_height)
            )

    @staticmethod
    def _import_pillow_image():
        try:
            from PIL import Image
        except ImportError as error:
            raise DecoderUnavailableError(
                "Optional Pillow decoder is not installed. Do not install it without the project dependency approval step."
            ) from error
        return Image


def _bounded_dimensions(width: int, height: int, maximum: int) -> tuple[int, int]:
    if width <= maximum and height <= maximum:
        return width, height
    scale = min(maximum / width, maximum / height)
    return max(1, round(width * scale)), max(1, round(height * scale))
