"""Project-local launcher; no Python package installation is required."""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from stock_photo_scout.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
