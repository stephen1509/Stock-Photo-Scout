import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class RepositorySafetyTests(unittest.TestCase):
    def test_private_generated_directories_are_git_ignored(self) -> None:
        ignored = {
            line.strip()
            for line in (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        required = {
            "photo_sources/",
            "working_copies/",
            "exports/",
            "local_catalogs/",
            "local_drafts/",
            "local_previews/",
            "local_workspace/",
            "local_preparation/",
        }
        self.assertEqual(required - ignored, set())

    def test_repository_contains_no_persistent_github_workflow(self) -> None:
        workflow_dir = PROJECT_ROOT / ".github" / "workflows"
        if workflow_dir.exists():
            workflows = [path for path in workflow_dir.iterdir() if path.is_file()]
            self.assertEqual(workflows, [], f"Unexpected persistent workflow(s): {workflows}")


if __name__ == "__main__":
    unittest.main()
