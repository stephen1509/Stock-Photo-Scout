import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from stock_photo_scout.drafts import CandidateDraft, evaluate_readiness
from stock_photo_scout.spelling import SpellingPolicy, find_possible_spelling_issues


class SpellingSuggestionTests(unittest.TestCase):
    def test_suggests_a_close_known_word_without_changing_title(self) -> None:
        title = "People Visiting Todaiji Templi in Nara, Japan"

        suggestions = find_possible_spelling_issues(title)

        templi_suggestion = next(suggestion for suggestion in suggestions if suggestion.token == "Templi")
        self.assertEqual(templi_suggestion.alternatives, ("temple",))
        self.assertIn("Templi", title)

    def test_accepted_term_suppresses_a_suggestion(self) -> None:
        policy = SpellingPolicy(accepted_terms=frozenset({"Templi"}))

        self.assertEqual(find_possible_spelling_issues("Templi", policy), ())

    def test_draft_readiness_explains_possible_spelling(self) -> None:
        draft = CandidateDraft(
            "temple.jpg",
            title="Templi market",
            keywords=("temple", "Templi"),
            notes="Templi at night",
        )

        report = evaluate_readiness(draft)

        spelling_prompts = [prompt for prompt in report.prompts if prompt.code == "possible_spelling"]
        self.assertEqual(len(spelling_prompts), 3)
        self.assertTrue(all("Templi" in prompt.explanation for prompt in spelling_prompts))
        self.assertTrue(any("title" in prompt.explanation for prompt in spelling_prompts))
        self.assertTrue(any("keyword 2" in prompt.explanation for prompt in spelling_prompts))
        self.assertTrue(any("notes" in prompt.explanation for prompt in spelling_prompts))

    def test_unrecognized_word_without_a_close_match_still_requires_confirmation(self) -> None:
        draft = CandidateDraft("temple.jpg", title="Zyzzyva", keywords=("temple",))

        report = evaluate_readiness(draft)

        spelling_prompt = next(prompt for prompt in report.prompts if prompt.code == "possible_spelling")
        self.assertIn("local dictionary", spelling_prompt.explanation)


if __name__ == "__main__":
    unittest.main()
