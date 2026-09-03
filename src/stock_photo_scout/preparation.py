"""Human-approved metadata and editor-handoff records for Stock Photo Scout 0.05C."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import json
import os
from pathlib import Path, PureWindowsPath
import tempfile
from typing import Final, Literal

PREPARATION_SCHEMA_VERSION: Final[int] = 1
SubmissionRoute = Literal["undecided", "commercial", "editorial"]
EditorTarget = Literal["none", "darktable", "rawtherapee", "gimp", "other"]

_ROUTES = frozenset({"undecided", "commercial", "editorial"})
_EDITORS = frozenset({"none", "darktable", "rawtherapee", "gimp", "other"})


@dataclass(frozen=True)
class CategoryPair:
    """One human-selected marketplace category and optional subcategory."""

    category: str
    subcategory: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.category, str) or not self.category.strip():
            raise ValueError("Category pair requires a category.")
        if not isinstance(self.subcategory, str):
            raise TypeError("Category-pair subcategory must be text.")


@dataclass(frozen=True)
class PreparationRecord:
    """Local human-authored preparation state for one candidate."""

    relative_path: str
    title: str = ""
    description: str = ""
    keywords: tuple[str, ...] = ()
    categories: tuple[str, ...] = ()
    category_pairs: tuple[CategoryPair, ...] = ()
    route: SubmissionRoute = "undecided"
    editor_target: EditorTarget = "none"
    working_export_relative_path: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        _validate_relative_path(self.relative_path, "relative_path")
        if self.working_export_relative_path:
            _validate_relative_path(self.working_export_relative_path, "working_export_relative_path")
        if self.route not in _ROUTES:
            raise ValueError("route must use a supported human choice.")
        if self.editor_target not in _EDITORS:
            raise ValueError("editor_target must use a supported value.")
        for value, label in ((self.title, "title"), (self.description, "description"), (self.notes, "notes")):
            if not isinstance(value, str):
                raise TypeError(f"{label} must be text.")
        for values, label in ((self.keywords, "keywords"), (self.categories, "categories")):
            if any(not isinstance(value, str) for value in values):
                raise TypeError(f"{label} must contain text values.")
        if len(self.category_pairs) > 3:
            raise ValueError("Dreamstime preparation supports at most three category pairs.")
        if any(not isinstance(value, CategoryPair) for value in self.category_pairs):
            raise TypeError("category_pairs must contain CategoryPair values.")


@dataclass(frozen=True)
class PreparationPrompt:
    code: str
    explanation: str


@dataclass(frozen=True)
class PreparationReport:
    relative_path: str
    prompts: tuple[PreparationPrompt, ...]


def edit_preparation(record: PreparationRecord, **changes) -> PreparationRecord:
    """Return an explicitly edited immutable record."""

    return replace(record, **changes)


def evaluate_preparation(record: PreparationRecord) -> PreparationReport:
    """Report missing human-preparation fields without making acceptance/legal claims."""

    prompts: list[PreparationPrompt] = []
    if not record.title.strip():
        prompts.append(PreparationPrompt("title_missing", "Add a factual human-approved title."))
    if not record.description.strip():
        prompts.append(PreparationPrompt("description_missing", "Add a factual human-approved description."))
    if not tuple(value.strip() for value in record.keywords if value.strip()):
        prompts.append(PreparationPrompt("keywords_missing", "Add human-reviewed descriptive keywords."))
    if record.route == "undecided":
        prompts.append(PreparationPrompt(
            "route_undecided",
            "Choose commercial or editorial manually using current marketplace requirements and the image context.",
        ))
    if record.editor_target != "none" and not record.working_export_relative_path:
        prompts.append(PreparationPrompt(
            "working_export_missing",
            "An editor is selected but no derived working-export path has been recorded.",
        ))
    if len({value.strip().casefold() for value in record.keywords if value.strip()}) != len(
        [value for value in record.keywords if value.strip()]
    ):
        prompts.append(PreparationPrompt("duplicate_keywords", "Remove duplicate keywords after human review."))
    return PreparationReport(record.relative_path, tuple(prompts))


def preparation_to_json(record: PreparationRecord) -> str:
    return json.dumps(
        {"schema_version": PREPARATION_SCHEMA_VERSION, "preparation": asdict(record)},
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def preparation_from_json(serialized: str) -> PreparationRecord:
    payload = json.loads(serialized)
    if payload.get("schema_version") != PREPARATION_SCHEMA_VERSION or not isinstance(payload.get("preparation"), dict):
        raise ValueError("Preparation JSON does not match the supported schema.")
    item = payload["preparation"]
    keywords = item.get("keywords", [])
    categories = item.get("categories", [])
    category_pairs = item.get("category_pairs", [])
    if not isinstance(keywords, list) or not isinstance(categories, list) or not isinstance(category_pairs, list):
        raise ValueError("Preparation keywords and categories must be lists.")
    try:
        parsed_pairs = tuple(
            CategoryPair(category=pair["category"], subcategory=pair.get("subcategory", ""))
            for pair in category_pairs
            if isinstance(pair, dict)
        )
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("Preparation category pairs must contain category and optional subcategory text.") from error
    if len(parsed_pairs) != len(category_pairs):
        raise ValueError("Preparation category pairs must be objects.")
    return PreparationRecord(
        relative_path=item.get("relative_path", ""),
        title=item.get("title", ""),
        description=item.get("description", ""),
        keywords=tuple(keywords),
        categories=tuple(categories),
        category_pairs=parsed_pairs,
        route=item.get("route", "undecided"),
        editor_target=item.get("editor_target", "none"),
        working_export_relative_path=item.get("working_export_relative_path", ""),
        notes=item.get("notes", ""),
    )


def category_pair_from_text(value: str) -> CategoryPair:
    """Parse one CLI pair as `Category :: Subcategory` without marketplace lookup."""

    category, separator, subcategory = value.partition("::")
    if not category.strip():
        raise ValueError("Category pair must start with a category before '::'.")
    return CategoryPair(category.strip(), subcategory.strip() if separator else "")


def save_preparation_json(
    record: PreparationRecord,
    destination: str | Path,
    source_root: str | Path,
    *,
    overwrite: bool = False,
) -> Path:
    """Persist local preparation state outside the selected photo source."""

    root = Path(source_root).expanduser().resolve(strict=True)
    target = Path(destination).expanduser().resolve(strict=False)
    if target.suffix.lower() != ".json":
        raise ValueError("Preparation destination must use a .json suffix.")
    if target.is_relative_to(root):
        raise ValueError("Refusing to write preparation state inside the selected source-photo folder.")
    target.parent.mkdir(parents=True, exist_ok=True)
    serialized = preparation_to_json(record)

    if not overwrite:
        with target.open("x", encoding="utf-8", newline="\n") as output:
            output.write(serialized)
        return target

    if target.is_symlink() or not target.is_file():
        raise FileNotFoundError("Existing regular preparation file not found.")
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=target.parent,
            prefix=f".{target.stem}.", suffix=".tmp", delete=False,
        ) as temporary:
            temporary.write(serialized)
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, target)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    return target


def _validate_relative_path(value: str, label: str) -> None:
    native = Path(value)
    windows = PureWindowsPath(value)
    if (
        not value
        or native.is_absolute()
        or native.drive
        or windows.is_absolute()
        or windows.drive
        or ".." in native.parts
        or ".." in windows.parts
    ):
        raise ValueError(f"{label} must be a safe relative path.")
