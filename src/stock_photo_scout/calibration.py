"""Local summaries of human-labelled visual-signal observations.

This module deliberately reports descriptive group averages only. It does not
train a model, decide whether a photo is suitable, or make rights, legal, or
Dreamstime-acceptance decisions.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from statistics import fmean
from typing import Iterable, Mapping


METRICS = (
    "mean_luminance",
    "dark_clip_ratio",
    "bright_clip_ratio",
    "sharpness_proxy",
    "noise_proxy",
)


@dataclass(frozen=True)
class LabelSummary:
    label: str
    count: int
    mean_luminance: float
    dark_clip_ratio: float
    bright_clip_ratio: float
    sharpness_proxy: float
    noise_proxy: float


def calibration_records_from_json(serialized: str) -> tuple[dict[str, object], ...]:
    """Load a local human-label record without reading any source image."""

    payload = json.loads(serialized)
    records = payload.get("records") if isinstance(payload, dict) else None
    if not isinstance(records, list) or not records:
        raise ValueError("Calibration data must contain at least one record.")
    validated: list[dict[str, object]] = []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Each calibration record must be an object.")
        label = record.get("technical_suitability_label")
        filename = record.get("filename")
        if not isinstance(label, str) or not label.strip() or not isinstance(filename, str) or not filename.strip():
            raise ValueError("Each calibration record needs a filename and technical-suitability label.")
        item: dict[str, object] = {
            "filename": filename,
            "technical_suitability_label": label,
        }
        for metric in METRICS:
            value = record.get(metric)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(f"Calibration record metric {metric} must be numeric.")
            item[metric] = float(value)
        validated.append(item)
    return tuple(validated)


def summarize_calibration(records: Iterable[Mapping[str, object]]) -> tuple[LabelSummary, ...]:
    """Return one descriptive average per human label."""

    grouped: dict[str, list[Mapping[str, object]]] = {}
    for record in records:
        label = record.get("technical_suitability_label")
        if not isinstance(label, str) or not label.strip():
            raise ValueError("Calibration records require a technical-suitability label.")
        grouped.setdefault(label, []).append(record)
    if not grouped:
        raise ValueError("At least one calibration record is required.")
    summaries = []
    for label, rows in grouped.items():
        values: dict[str, float] = {}
        for metric in METRICS:
            series = [row.get(metric) for row in rows]
            if any(not isinstance(value, (int, float)) or isinstance(value, bool) for value in series):
                raise ValueError(f"Calibration record metric {metric} must be numeric.")
            values[metric] = fmean(float(value) for value in series)
        summaries.append(LabelSummary(label=label, count=len(rows), **values))
    return tuple(sorted(summaries, key=lambda summary: summary.label))


def calibration_to_text(summaries: Iterable[LabelSummary]) -> str:
    """Format a local descriptive report; it contains no decision thresholds."""

    rows = tuple(summaries)
    lines = ["Local human-labelled calibration summary (advisory only)"]
    for summary in rows:
        lines.extend((
            f"{summary.label} (n={summary.count})",
            f"  Mean luminance: {summary.mean_luminance:.4f}",
            f"  Dark clipping ratio: {summary.dark_clip_ratio:.4f}",
            f"  Bright clipping ratio: {summary.bright_clip_ratio:.4f}",
            f"  Sharpness proxy: {summary.sharpness_proxy:.4f}",
            f"  Noise proxy: {summary.noise_proxy:.4f}",
        ))
    lines.append("This report does not decide suitability, rights, or marketplace acceptance.")
    return "\n".join(lines) + "\n"
