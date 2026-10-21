"""Strict validation for persisted visual-analysis facts."""
from __future__ import annotations
import math


def positive_int(value, name: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def finite_number(value, name: str, *, minimum: float | None = None, maximum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    if minimum is not None and number < minimum:
        raise ValueError(f"{name} is below its valid range")
    if maximum is not None and number > maximum:
        raise ValueError(f"{name} is above its valid range")
    return number


def validate_metrics(*, width, height, mean_luminance, dark_clip_ratio, bright_clip_ratio, sharpness_proxy, noise_proxy) -> None:
    positive_int(width, "width")
    positive_int(height, "height")
    finite_number(mean_luminance, "mean_luminance", minimum=0, maximum=255)
    finite_number(dark_clip_ratio, "dark_clip_ratio", minimum=0, maximum=1)
    finite_number(bright_clip_ratio, "bright_clip_ratio", minimum=0, maximum=1)
    finite_number(sharpness_proxy, "sharpness_proxy", minimum=0)
    finite_number(noise_proxy, "noise_proxy", minimum=0)
