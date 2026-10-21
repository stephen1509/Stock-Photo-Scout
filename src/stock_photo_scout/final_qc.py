"""Final-export QC facts and deterministic actual-pixel inspection planning.

This module records human-controlled final-export inspection. It deliberately
contains no marketplace acceptance score: defects are observations and a human
must explicitly confirm that the exact final export was inspected.
"""
from dataclasses import dataclass

QC_DEFECT_CODES = (
    "focus",
    "motion-blur",
    "noise",
    "compression-artifacts",
    "clipping",
    "banding",
    "halos",
    "over-sharpening",
    "over-denoising",
    "chromatic-aberration",
    "dust-spots",
    "pixelation-or-upscaling",
    "exposure",
    "color",
)


@dataclass(frozen=True)
class InspectionCrop:
    label: str
    left: int
    top: int
    width: int
    height: int


@dataclass(frozen=True)
class FinalExportFacts:
    width_pixels: int
    height_pixels: int
    format_name: str
    color_space: str = "unknown"

    @property
    def pixel_count(self):
        return self.width_pixels * self.height_pixels


@dataclass(frozen=True)
class FinalQcRecord:
    """Human inspection result for one exact export fingerprint.

    `inspected_at_100_percent` and `human_confirmed` must both be literal True.
    `export_sha256` binds the decision to exact bytes so a later export can
    invalidate the QC instead of silently inheriting it.
    """
    export_sha256: str = ""
    inspected_at_100_percent: bool | None = None
    human_confirmed: bool | None = None
    defect_codes: tuple[str, ...] = ()
    notes: str = ""


def plan_100_percent_crops(width: int, height: int, *, crop_size: int = 1024) -> tuple[InspectionCrop, ...]:
    for value, name in ((width, "width"), (height, "height"), (crop_size, "crop_size")):
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise ValueError(f"{name} must be a positive integer")
    cw, ch = min(crop_size, width), min(crop_size, height)
    positions = (
        ("top-left", 0, 0),
        ("top-right", width - cw, 0),
        ("centre", max(0, (width - cw) // 2), max(0, (height - ch) // 2)),
        ("bottom-left", 0, height - ch),
        ("bottom-right", width - cw, height - ch),
    )
    seen, out = set(), []
    for label, left, top in positions:
        key = (left, top, cw, ch)
        if key not in seen:
            seen.add(key)
            out.append(InspectionCrop(label, left, top, cw, ch))
    return tuple(out)


def validate_final_export_facts(f: FinalExportFacts) -> None:
    if not isinstance(f.width_pixels, int) or isinstance(f.width_pixels, bool) or f.width_pixels < 1:
        raise ValueError("width_pixels must be positive")
    if not isinstance(f.height_pixels, int) or isinstance(f.height_pixels, bool) or f.height_pixels < 1:
        raise ValueError("height_pixels must be positive")
    if not isinstance(f.format_name, str) or not f.format_name.strip():
        raise ValueError("format_name is required")
    if not isinstance(f.color_space, str) or not f.color_space.strip():
        raise ValueError("color_space must be a non-empty string")


def final_qc_blockers(record: FinalQcRecord, *, current_export_sha256: str) -> tuple[str, ...]:
    """Return deterministic blockers; unknown/mismatched identity fails closed."""
    blockers = []
    if not isinstance(record.export_sha256, str) or len(record.export_sha256) != 64 or any(c not in "0123456789abcdef" for c in record.export_sha256.lower()):
        blockers.append("Final QC is not bound to a valid export SHA-256 fingerprint.")
    if not isinstance(current_export_sha256, str) or len(current_export_sha256) != 64 or any(c not in "0123456789abcdef" for c in current_export_sha256.lower()):
        blockers.append("Current final export does not have a valid SHA-256 fingerprint.")
    elif record.export_sha256.lower() != current_export_sha256.lower():
        blockers.append("Final export bytes changed after the recorded QC inspection.")
    if record.inspected_at_100_percent is not True:
        blockers.append("Final export has not been explicitly inspected at 100% view.")
    if record.human_confirmed is not True:
        blockers.append("Final export QC has not been explicitly human-confirmed.")
    if not isinstance(record.defect_codes, tuple):
        blockers.append("Final QC defect observations are malformed.")
    else:
        unknown = tuple(code for code in record.defect_codes if code not in QC_DEFECT_CODES)
        if unknown:
            blockers.append("Final QC contains unsupported defect observation codes: " + ", ".join(unknown))
        if record.defect_codes:
            blockers.append("Final QC has unresolved defect observations: " + ", ".join(record.defect_codes))
    if not isinstance(record.notes, str):
        blockers.append("Final QC notes are malformed.")
    return tuple(blockers)
