import sys
import unittest
from pathlib import Path
PROJECT_ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT_ROOT/"src"))
from stock_photo_scout.candidate_review import CandidateReviewRecord, readiness_blockers, validate_candidate_review

class CandidateReview006Tests(unittest.TestCase):
    def ready(self, **changes):
        values=dict(relative_path="photo.jpg",review_decision="candidate",technical_state="pass",stock_potential="promising",rights_state="clear-looking",route="commercial",preparation_state="ready",edit_needed=False)
        values.update(changes); return CandidateReviewRecord(**values)
    def test_commercial_and_editorial_are_concrete_final_routes(self):
        self.assertEqual(readiness_blockers(self.ready(route="commercial")),())
        self.assertEqual(readiness_blockers(self.ready(route="editorial")),())
    def test_both_possible_is_not_a_final_route(self):
        self.assertTrue(any("concrete" in x for x in readiness_blockers(self.ready(route="both-possible"))))
    def test_undecided_is_not_a_final_route(self):
        self.assertTrue(readiness_blockers(self.ready(route="undecided")))
    def test_review_text_fields_must_be_strings(self):
        with self.assertRaises(ValueError): validate_candidate_review(self.ready(reviewer_notes=None))
    def test_windows_drive_path_rejected_cross_platform(self):
        with self.assertRaises(ValueError): validate_candidate_review(self.ready(relative_path="C:photo.jpg"))

if __name__=="__main__": unittest.main()
