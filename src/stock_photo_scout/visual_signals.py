"""Pure local visual-signal measurements for Stock Photo Scout 0.05B.

This module intentionally does not decode image files. It operates on caller-supplied
8-bit luminance grids so the measurement logic can be tested independently of any
future image-decoding dependency. Results are observations, not marketplace decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import fmean
from typing import Iterable


@dataclass(frozen=True)
class VisualSignalPolicy:
    """Optional caller-configured prompt thresholds; none are Dreamstime rules."""

    dark_clip_level: int = 2
    bright_clip_level: int = 253
    max_dark_clip_ratio: float | None = None
    max_bright_clip_ratio: float | None = None
    min_sharpness_proxy: float | None = None
    max_noise_proxy: float | None = None

    def __post_init__(self) -> None:
        if not 0 <= self.dark_clip_level <= 255:
            raise ValueError("dark_clip_level must be between 0 and 255.")
        if not 0 <= self.bright_clip_level <= 255:
            raise ValueError("bright_clip_level must be between 0 and 255.")
        if self.dark_clip_level >= self.bright_clip_level:
            raise ValueError("dark_clip_level must be below bright_clip_level.")
        for value, label in (
            (self.max_dark_clip_ratio, "max_dark_clip_ratio"),
            (self.max_bright_clip_ratio, "max_bright_clip_ratio"),
        ):
            if value is not None and not 0 <= value <= 1:
                raise ValueError(f"{label} must be between 0 and 1.")


@dataclass(frozen=True)
class VisualPrompt:
    code: str
    explanation: str


@dataclass(frozen=True)
class VisualSignalReport:
    width: int
    height: int
    mean_luminance: float
    dark_clip_ratio: float
    bright_clip_ratio: float
    sharpness_proxy: float
    noise_proxy: float
    prompts: tuple[VisualPrompt, ...]


def analyze_luminance_grid(
    rows: Iterable[Iterable[int]],
    policy: VisualSignalPolicy | None = None,
) -> VisualSignalReport:
    """Measure an 8-bit luminance grid with no image-file I/O.

    sharpness_proxy is the mean absolute discrete Laplacian on interior pixels.
    noise_proxy is the mean absolute residual from a 4-neighbour local mean.
    Both are simple explainable signals, not quality scores.
    """

    grid = tuple(tuple(row) for row in rows)
    if not grid or not grid[0]:
        raise ValueError("Luminance grid must not be empty.")
    width = len(grid[0])
    if any(len(row) != width for row in grid):
        raise ValueError("Luminance grid rows must have equal width.")
    if any(not isinstance(value, int) or not 0 <= value <= 255 for row in grid for value in row):
        raise ValueError("Luminance values must be integers from 0 to 255.")

    height = len(grid)
    values = [value for row in grid for value in row]
    active = policy or VisualSignalPolicy()
    total = len(values)
    dark_ratio = sum(value <= active.dark_clip_level for value in values) / total
    bright_ratio = sum(value >= active.bright_clip_level for value in values) / total

    laplacians: list[float] = []
    residuals: list[float] = []
    if width >= 3 and height >= 3:
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                center = grid[y][x]
                neighbours = (grid[y - 1][x], grid[y + 1][x], grid[y][x - 1], grid[y][x + 1])
                neighbour_sum = sum(neighbours)
                laplacians.append(abs(4 * center - neighbour_sum))
                residuals.append(abs(center - neighbour_sum / 4))

    sharpness = fmean(laplacians) if laplacians else 0.0
    noise = fmean(residuals) if residuals else 0.0

    prompts: list[VisualPrompt] = []
    if active.max_dark_clip_ratio is not None and dark_ratio > active.max_dark_clip_ratio:
        prompts.append(VisualPrompt(
            "dark_clipping_above_configured_limit",
            f"Dark clipping ratio {dark_ratio:.4f} exceeds the caller-configured limit {active.max_dark_clip_ratio:.4f}.",
        ))
    if active.max_bright_clip_ratio is not None and bright_ratio > active.max_bright_clip_ratio:
        prompts.append(VisualPrompt(
            "bright_clipping_above_configured_limit",
            f"Bright clipping ratio {bright_ratio:.4f} exceeds the caller-configured limit {active.max_bright_clip_ratio:.4f}.",
        ))
    if active.min_sharpness_proxy is not None and sharpness < active.min_sharpness_proxy:
        prompts.append(VisualPrompt(
            "sharpness_proxy_below_configured_limit",
            f"Sharpness proxy {sharpness:.4f} is below the caller-configured limit {active.min_sharpness_proxy:.4f}.",
        ))
    if active.max_noise_proxy is not None and noise > active.max_noise_proxy:
        prompts.append(VisualPrompt(
            "noise_proxy_above_configured_limit",
            f"Noise proxy {noise:.4f} exceeds the caller-configured limit {active.max_noise_proxy:.4f}.",
        ))

    return VisualSignalReport(
        width=width,
        height=height,
        mean_luminance=fmean(values),
        dark_clip_ratio=dark_ratio,
        bright_clip_ratio=bright_ratio,
        sharpness_proxy=sharpness,
        noise_proxy=noise,
        prompts=tuple(prompts),
    )
