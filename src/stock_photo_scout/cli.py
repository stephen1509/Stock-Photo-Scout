"""Small local command-line workflow for reviewing draft text."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .drafts import draft_from_json, evaluate_readiness
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
    return parser


def main(arguments: Sequence[str] | None = None) -> int:
    """Run an explicit local review or spelling-confirmation action."""

    parsed = build_parser().parse_args(arguments)
    if parsed.command == "review-draft":
        return _review_draft(parsed.draft, parsed.dictionary)
    if parsed.command == "accept-spelling":
        return _accept_spelling(parsed.dictionary, parsed.term)
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


def _load_dictionary(dictionary_path: Path) -> AcceptedSpellings:
    return spelling_dictionary_from_json(dictionary_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
