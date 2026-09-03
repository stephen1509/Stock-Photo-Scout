"""Dropbox working-copy launcher for the 0.05A candidate dashboard."""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from stock_photo_scout.candidate_dashboard import CandidateDashboardSettings, serve_candidate_dashboard

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("source_root", type=Path)
    parser.add_argument("--drafts-dir", type=Path, default=Path("local_drafts"))
    parser.add_argument("--dictionary", type=Path, default=Path("local_drafts") / "accepted_spellings.json")
    parser.add_argument("--previews-dir", type=Path, default=Path("local_previews"))
    parser.add_argument("--workspace", type=Path, default=Path("local_workspace") / "candidates.json")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    serve_candidate_dashboard(
        CandidateDashboardSettings.create(
            args.source_root, args.drafts_dir, args.dictionary, args.previews_dir, args.workspace
        ),
        args.port,
    )
