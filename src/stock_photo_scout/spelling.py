"""Offline spelling review for every word in user-entered draft text."""

from __future__ import annotations

from dataclasses import dataclass
from difflib import get_close_matches
import re


_DEFAULT_KNOWN_WORDS = frozenset(
    {
        "a",
        "ancient",
        "and",
        "architecture",
        "at",
        "autumn",
        "buddhist",
        "building",
        "city",
        "culture",
        "day",
        "dawn",
        "entrance",
        "festival",
        "garden",
        "historic",
        "in",
        "landmark",
        "market",
        "monk",
        "night",
        "of",
        "people",
        "shrine",
        "temple",
        "the",
        "tourist",
        "travel",
        "visiting",
        "with",
    }
)
_WORD_PATTERN = re.compile(r"[A-Za-z]+(?:['-][A-Za-z]+)*")


@dataclass(frozen=True)
class SpellingPolicy:
    """Local vocabulary settings for suggestion-only text checks."""

    known_words: frozenset[str] = _DEFAULT_KNOWN_WORDS
    accepted_terms: frozenset[str] = frozenset()
    suggestion_cutoff: float = 0.8
    max_suggestions: int = 3
    minimum_token_length: int = 1

    def __post_init__(self) -> None:
        if not 0.0 <= self.suggestion_cutoff <= 1.0:
            raise ValueError("suggestion_cutoff must be between 0 and 1.")
        if self.max_suggestions < 1 or self.minimum_token_length < 1:
            raise ValueError("Spelling limits must be positive.")


@dataclass(frozen=True)
class SpellingSuggestion:
    token: str
    alternatives: tuple[str, ...]


def find_possible_spelling_issues(text: str, policy: SpellingPolicy | None = None) -> tuple[SpellingSuggestion, ...]:
    """Review every word and return unrecognized terms without altering text.

    A term with no close alternative is still returned so the user can confirm a
    proper name, a specialized term, or a possible misspelling. Add confirmed
    terms to ``accepted_terms`` to suppress future prompts.
    """

    if not isinstance(text, str):
        raise TypeError("text must be a string.")
    active_policy = policy or SpellingPolicy()
    vocabulary = {word.casefold() for word in active_policy.known_words}
    accepted_terms = {term.casefold() for term in active_policy.accepted_terms}
    suggestions: list[SpellingSuggestion] = []
    for match in _WORD_PATTERN.finditer(text):
        token = match.group(0)
        normalized = token.casefold()
        if (
            len(normalized) < active_policy.minimum_token_length
            or normalized in vocabulary
            or normalized in accepted_terms
        ):
            continue
        alternatives = get_close_matches(
            normalized,
            sorted(vocabulary),
            n=active_policy.max_suggestions,
            cutoff=active_policy.suggestion_cutoff,
        )
        suggestions.append(SpellingSuggestion(token, tuple(alternatives)))
    return tuple(suggestions)
