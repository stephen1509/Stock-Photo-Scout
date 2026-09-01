"""Project-local launcher for the 0.05A candidate workspace; no package installation required."""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from stock_photo_scout.workspace_cli import workspace_main

if __name__ == "__main__":
    raise SystemExit(workspace_main())
