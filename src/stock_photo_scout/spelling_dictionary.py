"""Explicit local persistence for user-confirmed spelling terms."""

from __future__ import annotations

from dataclasses import dataclass, replace
import json
import os
from pathlib import Path
import tempfile
import time

from .spelling import SpellingPolicy


SPELLING_DICTIONARY_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class AcceptedSpellings:
    """Terms a user has confirmed, retained locally and never auto-populated."""

    terms: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if any(not isinstance(term, str) or not term.strip() for term in self.terms):
            raise ValueError("Accepted spelling terms must be non-empty text.")

    def add(self, *terms: str) -> "AcceptedSpellings":
        """Return a copy with explicitly user-confirmed terms added."""

        return AcceptedSpellings(self.terms | frozenset(terms))

    def apply_to(self, policy: SpellingPolicy | None = None) -> SpellingPolicy:
        """Return a policy that recognizes these confirmed terms."""

        active_policy = policy or SpellingPolicy()
        return replace(active_policy, accepted_terms=active_policy.accepted_terms | self.terms)


def spelling_dictionary_to_json(dictionary: AcceptedSpellings) -> str:
    """Serialize a deterministic local dictionary without any photo information."""

    payload = {
        "schema_version": SPELLING_DICTIONARY_SCHEMA_VERSION,
        "accepted_terms": sorted(dictionary.terms, key=str.casefold),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def spelling_dictionary_from_json(serialized: str) -> AcceptedSpellings:
    """Load a validated local dictionary."""

    payload = json.loads(serialized)
    terms = payload.get("accepted_terms")
    if payload.get("schema_version") != SPELLING_DICTIONARY_SCHEMA_VERSION or not isinstance(terms, list):
        raise ValueError("Spelling dictionary JSON does not match the supported schema.")
    return AcceptedSpellings(frozenset(terms))


def save_spelling_dictionary(dictionary: AcceptedSpellings, destination: str | Path) -> Path:
    """Explicitly save a new local dictionary and refuse to overwrite one."""

    destination_path = _validated_destination(destination)
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    with destination_path.open("x", encoding="utf-8", newline="\n") as output:
        output.write(spelling_dictionary_to_json(dictionary))
    return destination_path


def update_spelling_dictionary(dictionary: AcceptedSpellings, destination: str | Path) -> Path:
    """Explicitly replace an existing regular local dictionary."""

    destination_path = _validated_destination(destination)
    if destination_path.is_symlink() or not destination_path.is_file():
        raise FileNotFoundError(f"Existing regular spelling dictionary not found: {destination_path}")

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
            temporary_file.write(spelling_dictionary_to_json(dictionary))
            temporary_path = Path(temporary_file.name)
        _replace_after_short_file_lock_retry(temporary_path, destination_path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    return destination_path


def _validated_destination(destination: str | Path) -> Path:
    destination_path = Path(destination).expanduser().resolve(strict=False)
    if destination_path.suffix.lower() != ".json":
        raise ValueError(f"Spelling dictionary destination must use a .json suffix: {destination_path}")
    return destination_path


def _replace_after_short_file_lock_retry(temporary_path: Path, destination_path: Path) -> None:
    """Tolerate a brief local-sync lock without broad or indefinite retries."""

    for attempt in range(3):
        try:
            os.replace(temporary_path, destination_path)
            return
        except PermissionError:
            if attempt == 2:
                raise
            time.sleep(0.1)
