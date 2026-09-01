"""Project-local command line for the 0.05A candidate workspace."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .workspace import (
    CANDIDATE_STATES,
    create_preview_copy,
    load_workspace,
    save_workspace,
    set_candidate_state,
)


def build_workspace_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stock-photo-workspace",
        description="Create consented local preview copies and manage human candidate states.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    preview = commands.add_parser("preview", help="Create one non-overwriting local preview copy.")
    preview.add_argument("source_root", type=Path)
    preview.add_argument("relative_path")
    preview.add_argument("preview_root", type=Path)
    preview.add_argument(
        "--consent",
        action="store_true",
        help="Required acknowledgement that this selected image may be read to create a local preview copy.",
    )

    state = commands.add_parser("set-state", help="Set one human-controlled candidate state.")
    state.add_argument("source_root", type=Path)
    state.add_argument("manifest", type=Path)
    state.add_argument("relative_path")
    state.add_argument("state", choices=CANDIDATE_STATES)
    state.add_argument("--preview-relative-path")

    show = commands.add_parser("show", help="Show the local candidate workspace manifest.")
    show.add_argument("manifest", type=Path)
    return parser


def workspace_main(arguments: Sequence[str] | None = None) -> int:
    parsed = build_workspace_parser().parse_args(arguments)

    if parsed.command == "preview":
        destination = create_preview_copy(
            parsed.source_root,
            parsed.relative_path,
            parsed.preview_root,
            consent=parsed.consent,
        )
        print(f"Local preview created: {destination}")
        return 0

    if parsed.command == "set-state":
        records = load_workspace(parsed.manifest) if parsed.manifest.exists() else {}
        updated = set_candidate_state(
            records,
            parsed.relative_path,
            parsed.state,
            preview_relative_path=parsed.preview_relative_path,
        )
        save_workspace(updated, parsed.manifest, parsed.source_root, overwrite=parsed.manifest.exists())
        print(f"Candidate state saved locally: {parsed.relative_path} -> {parsed.state}")
        return 0

    if parsed.command == "show":
        records = load_workspace(parsed.manifest)
        for relative_path in sorted(records):
            record = records[relative_path]
            preview = f" preview={record.preview_relative_path}" if record.preview_relative_path else ""
            print(f"{relative_path}: {record.state}{preview}")
        return 0

    raise AssertionError(f"Unsupported command: {parsed.command}")
