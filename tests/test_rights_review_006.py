import sys
import unittest
from pathlib import Path
PROJECT_ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT_ROOT/'src'))
from stock_photo_scout.rights_review import RightsReview,rights_blockers

class RightsReview006Tests(unittest.TestCase):
    def test_default_fails_closed(self):
        self.assertTrue(rights_blockers(RightsReview()))
    def test_present_issue_blocks_until_human_reviewed(self):
        r=RightsReview(logos_or_trademarks='present')
        self.assertTrue(any('logos_or_trademarks' in x for x in rights_blockers(r)))
    def test_reviewed_issue_does_not_itself_block(self):
        r=RightsReview(
            recognizable_people='none-seen',minors='none-seen',private_property='none-seen',
            artwork_or_sculpture='none-seen',logos_or_trademarks='reviewed',branded_products='none-seen',
            copyrighted_characters='none-seen',signs_screens_documents='none-seen',identifiable_interiors='none-seen')
        self.assertEqual(rights_blockers(r),())
    def test_reviewed_release_status_is_allowed(self):
        r=RightsReview(
            recognizable_people='none-seen',minors='none-seen',private_property='none-seen',
            artwork_or_sculpture='none-seen',logos_or_trademarks='none-seen',branded_products='none-seen',
            copyrighted_characters='none-seen',signs_screens_documents='none-seen',identifiable_interiors='none-seen',
            model_release='reviewed')
        self.assertEqual(rights_blockers(r),())

if __name__=='__main__': unittest.main()
