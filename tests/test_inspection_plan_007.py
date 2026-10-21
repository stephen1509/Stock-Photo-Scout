import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.inspection_plan import SubjectRegion,subject_inspection_region,validate_subject_region
class InspectionPlan007Tests(unittest.TestCase):
 def test_subject_crop_contains_subject_center(self):
  r=subject_inspection_region(6000,4000,SubjectRegion(.4,.3,.2,.2,"bird"));self.assertLessEqual(r.left,3000);self.assertGreaterEqual(r.right,3000);self.assertLessEqual(r.top,1600);self.assertGreaterEqual(r.bottom,1600)
 def test_edge_subject_clamps_inside_image(self):
  r=subject_inspection_region(1000,800,SubjectRegion(.9,.8,.1,.2));self.assertEqual(r.right,1000);self.assertEqual(r.bottom,800);self.assertGreaterEqual(r.left,0);self.assertGreaterEqual(r.top,0)
 def test_small_image_never_creates_out_of_bounds_crop(self):
  r=subject_inspection_region(300,200,SubjectRegion(.2,.2,.5,.5));self.assertEqual((r.left,r.top,r.right,r.bottom),(0,0,300,200))
 def test_invalid_regions_fail_closed(self):
  for r in (SubjectRegion(-.1,0,.2,.2),SubjectRegion(.9,.9,.2,.2),SubjectRegion(0,0,0,.2)):
   with self.subTest(r=r),self.assertRaises(ValueError):validate_subject_region(r)
 def test_boolean_dimensions_rejected(self):
  with self.assertRaises(ValueError):subject_inspection_region(True,100,SubjectRegion(0,0,.5,.5))
if __name__=="__main__":unittest.main()
