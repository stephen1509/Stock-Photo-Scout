"""Local, editable candidate drafts and non-speculative readiness prompts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json
import os
from pathlib import Path, PureWindowsPath
import tempfile
from typing import Iterable, Literal

from .spelling import SpellingPolicy, find_possible_spelling_issues


DRAFT_SCHEMA_VERSION = 1
ManualAnswer = Literal["unknown", "yes", "no", "not_applicable"]
EvidenceStatus = Literal["not_reviewed", "available", "not_available", "not_applicable"]
PromptSeverity = Literal["info", "attention"]

_MANUAL_ANSWERS = frozenset({"unknown", "yes", "no", "not_applicable"})
_EVIDENCE_STATUSES = frozenset({"not_reviewed", "available", "not_available", "not_applicable"})


@dataclass(frozen=True)
class RightsObservations:
    """User-supplied observations; none of these determine a legal outcome."""

    recognizable_people: ManualAnswer = "unknown"
    private_property_or_restricted_location: ManualAnswer = "unknown"
    visible_logos_or_trademarks: ManualAnswer = "unknown"
    third_party_copyrighted_content: ManualAnswer = "unknown"
    release_evidence: EvidenceStatus = "not_reviewed"

    def __post_init__(self) -> None:
        for value in (
            self.recognizable_people,
            self.private_property_or_restricted_location,
            self.visible_logos_or_trademarks,
            self.third_party_copyrighted_content,
        ):
            if value not in _MANUAL_ANSWERS:
                raise ValueError("Manual observations must use a supported answer.")
        if self.release_evidence not in _EVIDENCE_STATUSES:
            raise ValueError("release_evidence must use a supported status.")


@dataclass(frozen=True)
class CandidateDraft:
    """Editable local notes for one relative photo path."""

    relative_path: str
    title: str = ""
    keywords: tuple[str, ...] = ()
    rights: RightsObservations = RightsObservations()
    notes: str = ""

    def __post_init__(self) -> None:
        candidate_path = Path(self.relative_path)
        windows_path = PureWindowsPath(self.relative_path)
        if (
            not self.relative_path
            or candidate_path.is_absolute()
            or candidate_path.drive
            or windows_path.drive
            or windows_path.is_absolute()
            or ".." in candidate_path.parts
            or ".." in windows_path.parts
        ):
            raise ValueError("relative_path must be a non-empty path inside the selected source folder.")
        if not isinstance(self.title, str) or not isinstance(self.notes, str):
            raise TypeError("title and notes must be text.")
        if any(not isinstance(keyword, str) for keyword in self.keywords):
            raise TypeError("keywords must be text values.")


@dataclass(frozen=True)
class ReadinessPrompt:
    """An explainable request for human follow-up, never a submission decision."""

    code: str
    severity: PromptSeverity
    explanation: str


@dataclass(frozen=True)
class ReadinessReport:
    relative_path: str
    prompts: tuple[ReadinessPrompt, ...]


def edit_draft(
    draft: CandidateDraft,
    *,
    title: str | None = None,
    keywords: Iterable[str] | None = None,
    rights: RightsObservations | None = None,
    notes: str | None = None,
) -> CandidateDraft:
    """Return an edited draft without changing any source image or saved file."""

    return replace(
        draft,
        title=draft.title if title is None else title,
        keywords=draft.keywords if keywords is None else tuple(keywords),
        rights=draft.rights if rights is None else rights,
        notes=draft.notes if notes is None else notes,
    )


def evaluate_readiness(draft: CandidateDraft, spelling_policy: SpellingPolicy | None = None) -> ReadinessReport:
    """Return factual prompts for manual preparation of a candidate draft."""

    prompts: list[ReadinessPrompt] = []
    if not draft.title.strip():
        prompts.append(ReadinessPrompt("title_missing", "attention", "No draft title has been entered."))
    else:
        _append_spelling_prompts(prompts, "title", draft.title, spelling_policy)
    normalized_keywords = [keyword.strip() for keyword in draft.keywords if keyword.strip()]
    if not normalized_keywords:
        prompts.append(ReadinessPrompt("keywords_missing", "attention", "No draft keywords have been entered."))
    elif len(normalized_keywords) != len(draft.keywords):
        prompts.append(ReadinessPrompt("blank_keywords", "attention", "Some draft keywords are blank after trimming."))
    elif _has_duplicate_keywords(draft.keywords):
        prompts.append(
            ReadinessPrompt(
                "duplicate_keywords",
                "info",
                "Some draft keywords repeat after case-insensitive whitespace trimming.",
            )
        )

    for position, keyword in enumerate(draft.keywords, start=1):
        if keyword.strip():
            _append_spelling_prompts(prompts, f"keyword {position}", keyword, spelling_policy)
    if draft.notes.strip():
        _append_spelling_prompts(prompts, "notes", draft.notes, spelling_policy)

    _append_observation_prompts(prompts, draft.rights)
    return ReadinessReport(draft.relative_path, tuple(prompts))


def draft_to_json(draft: CandidateDraft) -> str:
    """Return deterministic local JSON that excludes any source-root path."""

    payload = {"schema_version": DRAFT_SCHEMA_VERSION, "draft": asdict(draft)}
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def draft_from_json(serialized: str) -> CandidateDraft:
    """Load a validated local draft without resolving or reading its source image."""

    payload = json.loads(serialized)
    if payload.get("schema_version") != DRAFT_SCHEMA_VERSION or not isinstance(payload.get("draft"), dict):
        raise ValueError("Draft JSON does not match the supported schema.")
    draft_payload = payload["draft"]
    rights_payload = draft_payload.get("rights")
    keywords_payload = draft_payload.get("keywords", ())
    if not isinstance(rights_payload, dict):
        raise ValueError("Draft JSON does not contain rights observations.")
    if not isinstance(keywords_payload, list):
        raise ValueError("Draft JSON keywords must be a list.")
    return CandidateDraft(
        relative_path=draft_payload.get("relative_path", ""),
        title=draft_payload.get("title", ""),
        keywords=tuple(keywords_payload),
        rights=RightsObservations(**rights_payload),
        notes=draft_payload.get("notes", ""),
    )


def save_draft_json(draft: CandidateDraft, destination: str | Path, source_root: str | Path) -> Path:
    """Explicitly save one draft outside the selected source folder without overwrite."""

    destination_path = _validated_draft_destination(destination, source_root)

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    with destination_path.open("x", encoding="utf-8", newline="\n") as output:
        output.write(draft_to_json(draft))
    return destination_path


def update_draft_json(draft: CandidateDraft, destination: str | Path, source_root: str | Path) -> Path:
    """Explicitly replace an existing local draft outside the selected source tree."""

    destination_path = _validated_draft_destination(destination, source_root)
    if destination_path.is_symlink() or not destination_path.is_file():
        raise FileNotFoundError(f"Existing regular draft file not found: {destination_path}")

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=destination_path.parent,
            prefix=f".{destination_path.stem}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_file.write(draft_to_json(draft))
            temporary_path = Path(temporary_file.name)
        os.replace(temporary_path, destination_path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    return destination_path


def _has_duplicate_keywords(keywords: tuple[str, ...]) -> bool:
    normalized = [keyword.strip().casefold() for keyword in keywords if keyword.strip()]
    return len(normalized) != len(set(normalized))


def _append_spelling_prompts(
    prompts: list[ReadinessPrompt], field_name: str, text: str, spelling_policy: SpellingPolicy | None
) -> None:
    """Append user-confirmation prompts for every unrecognized word in one text field."""

    for suggestion in find_possible_spelling_issues(text, spelling_policy):
        if suggestion.alternatives:
            alternatives = ", ".join(suggestion.alternatives)
            explanation = (
                f"In {field_name}, '{suggestion.token}' may be intended as '{alternatives}'; "
                "confirm or keep the original wording."
            )
        else:
            explanation = (
                f"In {field_name}, '{suggestion.token}' is not in the local dictionary; "
                "confirm its spelling or add it as an accepted term."
            )
        prompts.append(ReadinessPrompt("possible_spelling", "info", explanation))


def _validated_draft_destination(destination: str | Path, source_root: str | Path) -> Path:
    root_path = Path(source_root).expanduser().resolve(strict=True)
    destination_path = Path(destination).expanduser().resolve(strict=False)
    if destination_path.suffix.lower() != ".json":
        raise ValueError(f"Draft destination must use a .json suffix: {destination_path}")
    if destination_path.is_relative_to(root_path):
        raise ValueError(f"Refusing to write a draft inside its source folder: {destination_path}")
    return destination_path


def _append_observation_prompts(prompts: list[ReadinessPrompt], rights: RightsObservations) -> None:
    observations = (
        ("recognizable_people", rights.recognizable_people, "recognizable people"),
        (
            "private_property_or_restricted_location",
            rights.private_property_or_restricted_location,
            "private property or a restricted location",
        ),
        ("visible_logos_or_trademarks", rights.visible_logos_or_trademarks, "visible logos or trademarks"),
        (
            "third_party_copyrighted_content",
            rights.third_party_copyrighted_content,
            "third-party copyrighted content",
        ),
    )
    for code, answer, label in observations:
        if answer == "unknown":
            prompts.append(ReadinessPrompt(f"{code}_unknown", "attention", f"Review whether the image includes {label}."))
        elif answer == "yes":
            prompts.append(
                ReadinessPrompt(
                    f"{code}_present",
                    "attention",
                    f"{label.capitalize()} is recorded as present; confirm current rights and marketplace requirements manually.",
                )
            )
    if rights.release_evidence == "not_reviewed":
        prompts.append(ReadinessPrompt("release_evidence_not_reviewed", "attention", "Release evidence has not been reviewed."))
    elif rights.release_evidence == "not_available":
        prompts.append(
            ReadinessPrompt(
                "release_evidence_not_available",
                "attention",
                "No release evidence is recorded; determine its relevance using current requirements.",
            )
        )
