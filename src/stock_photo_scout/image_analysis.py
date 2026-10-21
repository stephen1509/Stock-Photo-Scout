"""Consent-gated visual-analysis orchestration for Stock Photo Scout."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path, PureWindowsPath
import tempfile
from typing import Protocol, Sequence
from .analysis_validation import validate_metrics
from .visual_signals import VisualSignalPolicy, VisualSignalReport, analyze_luminance_grid

ANALYSIS_SCHEMA_VERSION = 1

class LuminanceDecoder(Protocol):
    def decode_luminance(self, source_path: Path) -> Sequence[Sequence[int]]: ...

@dataclass(frozen=True)
class CandidateAnalysis:
    relative_path: str
    decoder_name: str
    report: VisualSignalReport

def analyze_candidate(source_root: str | Path, relative_path: str, decoder: LuminanceDecoder, *, consent: bool, policy: VisualSignalPolicy | None = None) -> CandidateAnalysis:
    if consent is not True:
        raise PermissionError("Explicit visual-analysis consent is required before decoding image pixels.")
    root = Path(source_root).expanduser().resolve(strict=True)
    relative = _validated_relative_path(relative_path)
    unresolved = root / relative
    if unresolved.is_symlink():
        raise ValueError("Candidate must be a regular non-symlink file.")
    source = unresolved.resolve(strict=True)
    if not source.is_relative_to(root) or not source.is_file():
        raise ValueError("Candidate must be a regular non-symlink file inside the selected source-photo folder.")
    decoder_name = type(decoder).__name__
    rows = decoder.decode_luminance(source)
    report = analyze_luminance_grid(rows, policy)
    return CandidateAnalysis(relative.as_posix(), decoder_name, report)

def analysis_observations(analysis: CandidateAnalysis) -> tuple[str, ...]:
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

def analysis_from_json(serialized: str) -> CandidateAnalysis:
    from .visual_signals import VisualPrompt, VisualSignalReport
    payload = json.loads(serialized)
    if not isinstance(payload, dict) or payload.get("schema_version") != ANALYSIS_SCHEMA_VERSION or not isinstance(payload.get("analysis"), dict):
        raise ValueError("Analysis JSON does not match the supported schema.")
    item = payload["analysis"]
    relative_path = item.get("relative_path", "")
    _validated_relative_path(relative_path)
    decoder_name = item.get("decoder_name")
    if not isinstance(decoder_name, str) or not decoder_name.strip():
        raise ValueError("Analysis JSON requires a non-empty decoder_name.")
    report = item.get("report")
    if not isinstance(report, dict) or not isinstance(report.get("prompts", []), list):
        raise ValueError("Analysis JSON does not contain a valid report.")
    raw_prompts = report.get("prompts", [])
    if any(not isinstance(prompt, dict) for prompt in raw_prompts):
        raise ValueError("Analysis prompts must be objects.")
    prompts = []
    for prompt in raw_prompts:
        code, explanation = prompt.get("code"), prompt.get("explanation")
        if not isinstance(code, str) or not code.strip() or not isinstance(explanation, str) or not explanation.strip():
            raise ValueError("Analysis prompts require non-empty code and explanation.")
        prompts.append(VisualPrompt(code=code, explanation=explanation))
    try:
        width, height = report["width"], report["height"]
        mean = report["mean_luminance"]
        dark, bright = report["dark_clip_ratio"], report["bright_clip_ratio"]
        sharp, noise = report["sharpness_proxy"], report["noise_proxy"]
    except KeyError as exc:
        raise ValueError(f"Analysis report is missing {exc.args[0]}.") from exc
    validate_metrics(width=width, height=height, mean_luminance=mean, dark_clip_ratio=dark, bright_clip_ratio=bright, sharpness_proxy=sharp, noise_proxy=noise)
    visual = VisualSignalReport(width=width, height=height, mean_luminance=float(mean), dark_clip_ratio=float(dark), bright_clip_ratio=float(bright), sharpness_proxy=float(sharp), noise_proxy=float(noise), prompts=tuple(prompts))
    return CandidateAnalysis(relative_path, decoder_name, visual)

def analysis_to_json(analysis: CandidateAnalysis) -> str:
    validate_metrics(width=analysis.report.width, height=analysis.report.height, mean_luminance=analysis.report.mean_luminance, dark_clip_ratio=analysis.report.dark_clip_ratio, bright_clip_ratio=analysis.report.bright_clip_ratio, sharpness_proxy=analysis.report.sharpness_proxy, noise_proxy=analysis.report.noise_proxy)
    if not analysis.decoder_name.strip():
        raise ValueError("decoder_name must be non-empty")
    _validated_relative_path(analysis.relative_path)
    return json.dumps({"schema_version": ANALYSIS_SCHEMA_VERSION, "analysis": asdict(analysis)}, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"

def save_analysis_json(analysis: CandidateAnalysis, destination: str | Path, source_root: str | Path, *, overwrite: bool = False) -> Path:
    root = Path(source_root).expanduser().resolve(strict=True)
    target = Path(destination).expanduser().resolve(strict=False)
    if target.suffix.lower() != ".json": raise ValueError("Analysis destination must use a .json suffix.")
    if target.is_relative_to(root): raise ValueError("Refusing to write analysis inside the selected source-photo folder.")
    target.parent.mkdir(parents=True, exist_ok=True)
    serialized = analysis_to_json(analysis)
    if not overwrite:
        with target.open("x", encoding="utf-8", newline="\n") as output: output.write(serialized)
        return target
    if target.is_symlink() or not target.is_file(): raise FileNotFoundError("Existing regular analysis file not found.")
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=target.parent, prefix=f".{target.stem}.", suffix=".tmp", delete=False) as temporary:
            temporary.write(serialized); temporary.flush(); os.fsync(temporary.fileno()); temporary_path = Path(temporary.name)
        os.replace(temporary_path, target)
    finally:
        if temporary_path is not None and temporary_path.exists(): temporary_path.unlink()
    return target

def _validated_relative_path(value: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError("Candidate path must be a safe relative path.")
    native, windows = Path(value), PureWindowsPath(value)
    if native.is_absolute() or native.drive or windows.is_absolute() or windows.drive or ".." in native.parts or ".." in windows.parts:
        raise ValueError("Candidate path must be a safe relative path.")
    return native
