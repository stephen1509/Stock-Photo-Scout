import sys, unittest
from pathlib import Path
PROJECT_ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(PROJECT_ROOT/'src'))
from stock_photo_scout.rights_review import RightsReview,rights_blockers

def reviewed(**changes):
 base=dict(recognizable_people='none-seen',minors='none-seen',private_property='none-seen',artwork_or_sculpture='none-seen',logos_or_trademarks='none-seen',branded_products='none-seen',copyrighted_characters='none-seen',signs_screens_documents='none-seen',identifiable_interiors='none-seen')
 base.update(changes);return RightsReview(**base)
class RightsReview006Tests(unittest.TestCase):
 def test_default_fails_closed(self):self.assertTrue(rights_blockers(RightsReview()))
 def test_present_issue_blocks_until_human_reviewed(self):self.assertTrue(any('logos_or_trademarks' in x for x in rights_blockers(RightsReview(logos_or_trademarks='present'))))
 def test_reviewed_issue_requires_concrete_route_binding(self):
  r=reviewed(logos_or_trademarks='reviewed');self.assertTrue(any('concrete submission route' in x for x in rights_blockers(r)))
 def test_reviewed_issue_passes_only_for_matching_route(self):
  r=reviewed(logos_or_trademarks='reviewed',reviewed_route='editorial');self.assertEqual(rights_blockers(r,required_route='editorial'),());self.assertTrue(any('selected submission route' in x for x in rights_blockers(r,required_route='commercial')))
 def test_reviewed_release_is_also_route_sensitive(self):
  r=reviewed(model_release='reviewed',reviewed_route='commercial');self.assertEqual(rights_blockers(r,required_route='commercial'),());self.assertTrue(rights_blockers(r,required_route='editorial'))
 def test_none_seen_does_not_need_route_binding(self):self.assertEqual(rights_blockers(reviewed()),())
if __name__=='__main__':unittest.main()
