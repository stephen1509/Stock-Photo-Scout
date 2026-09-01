"""Manual, non-submitting Dreamstime preparation packet for Stock Photo Scout 0.05D."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Iterable

from .preparation import PreparationRecord, evaluate_preparation

PREFLIGHT_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class PreflightPacket:
    """A local review packet; packet completeness is not marketplace acceptance."""

    relative_path: str
    candidate_state: str
    preparation: PreparationRecord
    technical_observations: tuple[str, ...]
    unresolved_rights_prompts: tuple[str, ...]
    preview_integrity_confirmed: bool | None
    current_requirements_reviewed: bool
    local_packet_complete: bool
    blockers: tuple[str, ...]
    reminders: tuple[str, ...]


def build_preflight_packet(
    preparation: PreparationRecord,
    *,
    candidate_state: str,
    technical_observations: Iterable[str] = (),
    unresolved_rights_prompts: Iterable[str] = (),
    preview_integrity_confirmed: bool | None = None,
    current_requirements_reviewed: bool = False,
) -> PreflightPacket:
    """Assemble a local manual-upload review packet.

    The result never claims legal clearance, Dreamstime acceptance, or upload eligibility.
    """

    preparation_report = evaluate_preparation(preparation)
    rights_prompts = tuple(str(value).strip() for value in unresolved_rights_prompts if str(value).strip())
    technical = tuple(str(value).strip() for value in technical_observations if str(value).strip())

    blockers: list[str] = [
        f"Preparation: {prompt.explanation}" for prompt in preparation_report.prompts
    ]
    if candidate_state != "submission-ready":
        blockers.append(
            f"Candidate state is '{candidate_state}', not the user's 'submission-ready' review state."
        )
    if rights_prompts:
        blockers.append("Unresolved people/property/logo/release observations remain for manual review.")
    if preview_integrity_confirmed is False:
        blockers.append("The local preview/export integrity check does not match the current source bytes.")
    if not current_requirements_reviewed:
        blockers.append("Current Dreamstime requirements have not been re-confirmed for this manual submission session.")

    reminders = (
        "Human must inspect the final exported image at useful zoom before upload.",
        "Human must confirm title, description, keywords, categories, and commercial/editorial route.",
        "Human must resolve any relevant releases, trademarks, property, people, or copyrighted-content questions.",
        "Human must confirm current Dreamstime UI and requirements at the time of submission.",
        "This packet does not upload, submit, license, or make an acceptance decision.",
    )

    return PreflightPacket(
        relative_path=preparation.relative_path,
        candidate_state=candidate_state,
        preparation=preparation,
        technical_observations=technical,
        unresolved_rights_prompts=rights_prompts,
        preview_integrity_confirmed=preview_integrity_confirmed,
        current_requirements_reviewed=current_requirements_reviewed,
        local_packet_complete=not blockers,
        blockers=tuple(blockers),
        reminders=reminders,
    )


def preflight_to_json(packet: PreflightPacket) -> str:
    payload = asdict(packet)
    return json.dumps(
        {"schema_version": PREFLIGHT_SCHEMA_VERSION, "preflight": payload},
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def preflight_to_text(packet: PreflightPacket) -> str:
    """Return a concise human-readable manual-upload checklist."""

    lines = [
        "Stock Photo Scout — manual preflight packet",
        f"Candidate: {packet.relative_path}",
        f"Review state: {packet.candidate_state}",
        f"Local packet complete: {'YES' if packet.local_packet_complete else 'NO'}",
        "",
        f"Title: {packet.preparation.title}",
        f"Description: {packet.preparation.description}",
        f"Keywords: {', '.join(packet.preparation.keywords)}",
        f"Categories: {', '.join(packet.preparation.categories)}",
        f"Route: {packet.preparation.route}",
        f"Editor: {packet.preparation.editor_target}",
        f"Working export: {packet.preparation.working_export_relative_path}",
        "",
        "Blockers:",
    ]
    lines.extend(f"- {value}" for value in packet.blockers)
    if not packet.blockers:
        lines.append("- None recorded by the local packet checks.")
    lines.extend(["", "Technical observations:"])
    lines.extend(f"- {value}" for value in packet.technical_observations)
    if not packet.technical_observations:
        lines.append("- None recorded.")
    lines.extend(["", "Manual reminders:"])
    lines.extend(f"- {value}" for value in packet.reminders)
    return "\n".join(lines) + "\n"
