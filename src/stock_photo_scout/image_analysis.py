"""Consent-gated visual-analysis orchestration for Stock Photo Scout.

The core deliberately depends on an injected decoder rather than a specific image
library. This lets the safety and analysis pipeline be tested without installing a
decoder or reading real user photographs.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path, PureWindowsPath
import tempfile
from typing import Protocol, Sequence

from .visual_signals import VisualSignalPolicy, VisualSignalReport, analyze_luminance_grid

ANALYSIS_SCHEMA_VERSION = 1


class LuminanceDecoder(Protocol):
    """Minimal decoder boundary to be implemented by a separately approved local adapter."""

    def decode_luminance(self, source_path: Path) -> Sequence[Sequence[int]]:
        """Return an 8-bit luminance grid for one already-validated local image."""


@dataclass(frozen=True)
class CandidateAnalysis:
    relative_path: str
    decoder_name: str
    report: VisualSignalReport


def analyze_candidate(
    source_root: str | Path,
    relative_path: str,
    decoder: LuminanceDecoder,
    *,
    consent: bool,
    policy: VisualSignalPolicy | None = None,
) -> CandidateAnalysis:
    """Decode and analyze one explicitly selected image after consent."""

    if consent is not True:
        raise PermissionError("Explicit visual-analysis consent is required before decoding image pixels.")

    root = Path(source_root).expanduser().resolve(strict=True)
    relative = _validated_relative_path(relative_path)
    source = (root / relative).resolve(strict=True)
    if not source.is_relative_to(root):
        raise ValueError("Candidate path escapes the selected source-photo folder.")
    if source.is_symlink() or not source.is_file():
        raise ValueError("Candidate must be a regular non-symlink file.")

    decoder_name = type(decoder).__name__
    rows = decoder.decode_luminance(source)
    report = analyze_luminance_grid(rows, policy)
    return CandidateAnalysis(relative.as_posix(), decoder_name, report)


def analysis_observations(analysis: CandidateAnalysis) -> tuple[str, ...]:
    """Convert measured signals and configured prompts into factual packet observations."""

    report = analysis.report
    observations = [
        f"Mean luminance: {report.mean_luminance:.4f}.",
        f"Dark clipping ratio: {report.dark_clip_ratio:.4f}.",
        f"Bright clipping ratio: {report.bright_clip_ratio:.4f}.",
        f"Sharpness proxy: {report.sharpness_proxy:.4f}.",
        f"Noise proxy: {report.noise_proxy:.4f}.",
    ]
    observations.extend(f"{prompt.code}: {prompt.explanation}" for prompt in report.prompts)
    return tuple(observations)


def analysis_to_json(analysis: CandidateAnalysis) -> str:
    return json.dumps(
        {"schema_version": ANALYSIS_SCHEMA_VERSION, "analysis": asdict(analysis)},
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def save_analysis_json(
    analysis: CandidateAnalysis,
    destination: str | Path,
    source_root: str | Path,
    *,
    overwrite: bool = False,
) -> Path:
    """Persist analysis outside the source-photo tree."""

    root = Path(source_root).expanduser().resolve(strict=True)
    target = Path(destination).expanduser().resolve(strict=False)
    if target.suffix.lower() != ".json":
        raise ValueError("Analysis destination must use a .json suffix.")
    if target.is_relative_to(root):
        raise ValueError("Refusing to write analysis inside the selected source-photo folder.")
    target.parent.mkdir(parents=True, exist_ok=True)
    serialized = analysis_to_json(analysis)

    if not overwrite:
        with target.open("x", encoding="utf-8", newline="\n") as output:
            output.write(serialized)
        return target

    if target.is_symlink() or not target.is_file():
        raise FileNotFoundError("Existing regular analysis file not found.")
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=target.parent,
            prefix=f".{target.stem}.", suffix=".tmp", delete=False,
        ) as temporary:
            temporary.write(serialized)
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, target)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    return target


def _validated_relative_path(value: str) -> Path:
    native = Path(value)
    windows = PureWindowsPath(value)
    if (
        not value
        or native.is_absolute()
        or native.drive
        or windows.is_absolute()
        or windows.drive
        or ".." in native.parts
        or ".." in windows.parts
    ):
        raise ValueError("Candidate path must be a safe relative path.")
    return native
