"""Local-only building blocks for Stock Photo Scout."""

from .catalog import CATALOG_SCHEMA_VERSION, CatalogEntry, LocalCatalog, build_catalog, catalog_to_json, save_catalog_json
from .drafts import (
    DRAFT_SCHEMA_VERSION,
    CandidateDraft,
    ReadinessPrompt,
    ReadinessReport,
    RightsObservations,
    draft_from_json,
    draft_to_json,
    edit_draft,
    evaluate_readiness,
    save_draft_json,
    update_draft_json,
)
from .exif import ExifMetadata, ExifStatus
from .metadata import MetadataStatus, TechnicalMetadata, extract_technical_metadata
from .review import (
    ExactDuplicateGroup,
    ExactDuplicateReport,
    HashingIssue,
    ReviewPolicy,
    TechnicalReview,
    TechnicalReviewFlag,
    TechnicalReviewReport,
    find_exact_duplicates,
    review_technical_metadata,
)
from .scanner import CandidateImage, inventory_images
from .spelling import SpellingPolicy, SpellingSuggestion, find_possible_spelling_issues
from .spelling_dictionary import (
    SPELLING_DICTIONARY_SCHEMA_VERSION,
    AcceptedSpellings,
    save_spelling_dictionary,
    spelling_dictionary_from_json,
    spelling_dictionary_to_json,
    update_spelling_dictionary,
)

__all__ = [
    "CATALOG_SCHEMA_VERSION",
    "DRAFT_SCHEMA_VERSION",
    "SPELLING_DICTIONARY_SCHEMA_VERSION",
    "AcceptedSpellings",
    "CandidateImage",
    "CandidateDraft",
    "CatalogEntry",
    "ExifMetadata",
    "ExifStatus",
    "ExactDuplicateGroup",
    "ExactDuplicateReport",
    "HashingIssue",
    "LocalCatalog",
    "MetadataStatus",
    "ReviewPolicy",
    "ReadinessPrompt",
    "ReadinessReport",
    "RightsObservations",
    "TechnicalReview",
    "TechnicalReviewFlag",
    "TechnicalReviewReport",
    "TechnicalMetadata",
    "build_catalog",
    "catalog_to_json",
    "draft_from_json",
    "draft_to_json",
    "edit_draft",
    "evaluate_readiness",
    "extract_technical_metadata",
    "find_exact_duplicates",
    "inventory_images",
    "review_technical_metadata",
    "save_draft_json",
    "SpellingPolicy",
    "SpellingSuggestion",
    "update_draft_json",
    "save_catalog_json",
    "save_spelling_dictionary",
    "find_possible_spelling_issues",
    "spelling_dictionary_from_json",
    "spelling_dictionary_to_json",
    "update_spelling_dictionary",
]
