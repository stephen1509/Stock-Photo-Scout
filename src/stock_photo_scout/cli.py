"""Small local command-line workflow for reviewing draft text."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .drafts import (
    CandidateDraft,
    RightsObservations,
    draft_from_json,
    edit_draft,
    evaluate_readiness,
    save_draft_json,
    update_draft_json,
)
from .candidate_dashboard import CandidateDashboardSettings, serve_candidate_dashboard
from .preparation import (
    PreparationRecord,
    edit_preparation,
    evaluate_preparation,
    preparation_from_json,
    save_preparation_json,
)
from .preflight import build_preflight_packet, preflight_to_text
from .spelling_dictionary import (
    AcceptedSpellings,
    save_spelling_dictionary,
    spelling_dictionary_from_json,
    update_spelling_dictionary,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stock-photo-scout",
        description="Review local Stock Photo Scout drafts without reading source images.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    review = commands.add_parser("review-draft", help="Show readiness and spelling prompts for one draft JSON file.")
    review.add_argument("draft", type=Path, help="Path to a local draft JSON file.")
    review.add_argument(
        "--dictionary",
        type=Path,
        help="Optional local accepted-spellings JSON file to apply during this review.",
    )

    accept = commands.add_parser(
        "accept-spelling", help="Explicitly add one confirmed term to a local accepted-spellings dictionary."
    )
    accept.add_argument("dictionary", type=Path, help="Path to the local accepted-spellings JSON file.")
    accept.add_argument("term", help="The spelling you have confirmed.")

    create = commands.add_parser("create-draft", help="Create a new local draft outside its source-photo folder.")
    create.add_argument("source_root", type=Path, help="Selected photo-source folder; it is never modified.")
    create.add_argument("relative_path", help="Photo path relative to the selected source folder.")
    create.add_argument("draft", type=Path, help="New local draft JSON destination.")
    _add_draft_fields(create)

    edit = commands.add_parser("edit-draft", help="Explicitly update an existing local draft outside its source folder.")
    edit.add_argument("source_root", type=Path, help="Selected photo-source folder; it is never modified.")
    edit.add_argument("draft", type=Path, help="Existing local draft JSON path.")
    _add_draft_fields(edit)

    dashboard = commands.add_parser("dashboard", help="Start the local candidate gallery and draft workspace.")
    dashboard.add_argument("source_root", type=Path, help="Selected photo-source folder; it is never modified.")
    dashboard.add_argument("--drafts-dir", type=Path, default=Path("local_drafts"))
    dashboard.add_argument("--dictionary", type=Path, default=Path("local_drafts") / "accepted_spellings.json")
    dashboard.add_argument("--previews-dir", type=Path, default=Path("local_previews"))
    dashboard.add_argument("--workspace", type=Path, default=Path("local_workspace") / "candidates.json")
    dashboard.add_argument("--port", type=int, default=8765)

    create_prep = commands.add_parser("create-preparation", help="Create local metadata/editor preparation outside the source tree.")
    create_prep.add_argument("source_root", type=Path)
    create_prep.add_argument("relative_path")
    create_prep.add_argument("destination", type=Path)
    _add_preparation_fields(create_prep)

    edit_prep = commands.add_parser("edit-preparation", help="Update an existing local preparation record.")
    edit_prep.add_argument("source_root", type=Path)
    edit_prep.add_argument("preparation", type=Path)
    _add_preparation_fields(edit_prep)

    review_prep = commands.add_parser("review-preparation", help="Show missing human-preparation fields.")
    review_prep.add_argument("preparation", type=Path)

    preflight = commands.add_parser("preflight", help="Print a local manual-upload preflight packet; performs no upload.")
    preflight.add_argument("preparation", type=Path)
    preflight.add_argument("--state", required=True, choices=("skip","maybe","shortlist","edit","metadata-ready","submission-ready"))
    preflight.add_argument("--technical-observation", action="append", default=[])
    preflight.add_argument("--rights-prompt", action="append", default=[])
    preflight.add_argument("--preview-integrity", choices=("unknown","match","mismatch"), default="unknown")
    preflight.add_argument("--current-requirements-reviewed", action="store_true")
    return parser


def main(arguments: Sequence[str] | None = None) -> int:
    """Run an explicit local review or spelling-confirmation action."""

    parsed = build_parser().parse_args(arguments)
    if parsed.command == "review-draft":
        return _review_draft(parsed.draft, parsed.dictionary)
    if parsed.command == "accept-spelling":
        return _accept_spelling(parsed.dictionary, parsed.term)
    if parsed.command == "create-draft":
        return _create_draft(parsed)
    if parsed.command == "edit-draft":
        return _edit_draft(parsed)
    if parsed.command == "create-preparation":
        return _create_preparation(parsed)
    if parsed.command == "edit-preparation":
        return _edit_preparation(parsed)
    if parsed.command == "review-preparation":
        return _review_preparation(parsed.preparation)
    if parsed.command == "preflight":
        return _preflight(parsed)
    if parsed.command == "dashboard":
        serve_candidate_dashboard(
            CandidateDashboardSettings.create(
                parsed.source_root,
                parsed.drafts_dir,
                parsed.dictionary,
                parsed.previews_dir,
                parsed.workspace,
            ),
            parsed.port,
        )
        return 0
    raise AssertionError(f"Unsupported command: {parsed.command}")


def _review_draft(draft_path: Path, dictionary_path: Path | None) -> int:
    draft = draft_from_json(draft_path.read_text(encoding="utf-8"))
    dictionary = _load_dictionary(dictionary_path) if dictionary_path else AcceptedSpellings()
    report = evaluate_readiness(draft, dictionary.apply_to())
    print(f"Draft: {draft_path}")
    print(f"Candidate: {report.relative_path}")
    if not report.prompts:
        print("No prompts.")
        return 0
    for prompt in report.prompts:
        print(f"[{prompt.severity}] {prompt.code}: {prompt.explanation}")
    return 0


def _accept_spelling(dictionary_path: Path, term: str) -> int:
    existing = _load_dictionary(dictionary_path) if dictionary_path.exists() else AcceptedSpellings()
    updated = existing.add(term)
    if dictionary_path.exists():
        update_spelling_dictionary(updated, dictionary_path)
    else:
        save_spelling_dictionary(updated, dictionary_path)
    print(f"Confirmed spelling saved locally: {term}")
    return 0


def _create_draft(parsed: argparse.Namespace) -> int:
    draft = _apply_draft_fields(CandidateDraft(parsed.relative_path), parsed)
    saved_path = save_draft_json(draft, parsed.draft, parsed.source_root)
    print(f"Local draft created: {saved_path}")
    return 0


def _edit_draft(parsed: argparse.Namespace) -> int:
    existing = draft_from_json(parsed.draft.read_text(encoding="utf-8"))
    updated = _apply_draft_fields(existing, parsed)
    saved_path = update_draft_json(updated, parsed.draft, parsed.source_root)
    print(f"Local draft updated: {saved_path}")
    return 0


def _add_draft_fields(command: argparse.ArgumentParser) -> None:
    command.add_argument("--title", help="Replace the draft title; use an empty string to clear it.")
    command.add_argument("--keyword", action="append", help="Replace keywords with one or more repeatable keyword values.")
    command.add_argument("--notes", help="Replace the draft notes; use an empty string to clear them.")
    command.add_argument("--recognizable-people", choices=("unknown", "yes", "no", "not_applicable"))
    command.add_argument("--private-property", choices=("unknown", "yes", "no", "not_applicable"))
    command.add_argument("--logos", choices=("unknown", "yes", "no", "not_applicable"))
    command.add_argument("--third-party-content", choices=("unknown", "yes", "no", "not_applicable"))
    command.add_argument("--release-evidence", choices=("not_reviewed", "available", "not_available", "not_applicable"))


def _apply_draft_fields(draft: CandidateDraft, parsed: argparse.Namespace) -> CandidateDraft:
    rights = RightsObservations(
        recognizable_people=parsed.recognizable_people or draft.rights.recognizable_people,
        private_property_or_restricted_location=parsed.private_property or draft.rights.private_property_or_restricted_location,
        visible_logos_or_trademarks=parsed.logos or draft.rights.visible_logos_or_trademarks,
        third_party_copyrighted_content=parsed.third_party_content or draft.rights.third_party_copyrighted_content,
        release_evidence=parsed.release_evidence or draft.rights.release_evidence,
    )
    return edit_draft(
        draft,
        title=parsed.title,
        keywords=tuple(parsed.keyword) if parsed.keyword is not None else None,
        notes=parsed.notes,
        rights=rights,
    )


def _add_preparation_fields(command: argparse.ArgumentParser) -> None:
    command.add_argument("--title")
    command.add_argument("--description")
    command.add_argument("--keyword", action="append")
    command.add_argument("--category", action="append")
    command.add_argument("--route", choices=("undecided", "commercial", "editorial"))
    command.add_argument("--editor-target", choices=("none", "darktable", "rawtherapee", "gimp", "other"))
    command.add_argument("--working-export-relative-path")
    command.add_argument("--preparation-notes")


def _apply_preparation_fields(record: PreparationRecord, parsed: argparse.Namespace) -> PreparationRecord:
    changes = {}
    for argument, field in (
        ("title", "title"),
        ("description", "description"),
        ("route", "route"),
        ("editor_target", "editor_target"),
        ("working_export_relative_path", "working_export_relative_path"),
        ("preparation_notes", "notes"),
    ):
        value = getattr(parsed, argument, None)
        if value is not None:
            changes[field] = value
    if getattr(parsed, "keyword", None) is not None:
        changes["keywords"] = tuple(parsed.keyword)
    if getattr(parsed, "category", None) is not None:
        changes["categories"] = tuple(parsed.category)
    return edit_preparation(record, **changes)


def _create_preparation(parsed: argparse.Namespace) -> int:
    record = _apply_preparation_fields(PreparationRecord(parsed.relative_path), parsed)
    saved = save_preparation_json(record, parsed.destination, parsed.source_root)
    print(f"Local preparation created: {saved}")
    return 0


def _edit_preparation(parsed: argparse.Namespace) -> int:
    record = preparation_from_json(parsed.preparation.read_text(encoding="utf-8"))
    updated = _apply_preparation_fields(record, parsed)
    saved = save_preparation_json(updated, parsed.preparation, parsed.source_root, overwrite=True)
    print(f"Local preparation updated: {saved}")
    return 0


def _review_preparation(path: Path) -> int:
    record = preparation_from_json(path.read_text(encoding="utf-8"))
    report = evaluate_preparation(record)
    print(f"Candidate: {report.relative_path}")
    if not report.prompts:
        print("No local preparation prompts.")
        return 0
    for prompt in report.prompts:
        print(f"{prompt.code}: {prompt.explanation}")
    return 0


def _preflight(parsed: argparse.Namespace) -> int:
    record = preparation_from_json(parsed.preparation.read_text(encoding="utf-8"))
    integrity = {"unknown": None, "match": True, "mismatch": False}[parsed.preview_integrity]
    packet = build_preflight_packet(
        record,
        candidate_state=parsed.state,
        technical_observations=parsed.technical_observation,
        unresolved_rights_prompts=parsed.rights_prompt,
        preview_integrity_confirmed=integrity,
        current_requirements_reviewed=parsed.current_requirements_reviewed,
    )
    print(preflight_to_text(packet), end="")
    return 0


def _load_dictionary(dictionary_path: Path) -> AcceptedSpellings:
    return spelling_dictionary_from_json(dictionary_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
