import sys, threading, time, unittest
from pathlib import Path
PROJECT_ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT_ROOT/"src"))
from stock_photo_scout.dashboard_safety import MutationLock, local_request_allowed, validated_relative_path

class DashboardSafetyTests(unittest.TestCase):
    def test_windows_drive_unc_and_traversal_are_rejected_on_any_host(self):
        for value in ("../secret.jpg", r"C:\\secret.jpg", r"\\\\server\\share\\secret.jpg"):
            with self.subTest(value=value), self.assertRaises(ValueError): validated_relative_path(value)
        self.assertEqual(validated_relative_path("nested/photo.jpg").as_posix(), "nested/photo.jpg")

    def test_nonlocal_host_and_origin_are_rejected(self):
        self.assertTrue(local_request_allowed(host_header="127.0.0.1:8765", origin_header="http://127.0.0.1:8765"))
        self.assertTrue(local_request_allowed(host_header="localhost:8765", origin_header=None))
        self.assertFalse(local_request_allowed(host_header="evil.example:8765", origin_header=None))
        self.assertFalse(local_request_allowed(host_header="127.0.0.1:8765", origin_header="https://evil.example"))

    def test_mutation_lock_serializes_critical_sections(self):
        lock=MutationLock(); active=0; maximum=0; guard=threading.Lock()
        def worker():
            nonlocal active, maximum
            with lock:
                with guard:
                    active+=1; maximum=max(maximum,active)
                time.sleep(.01)
                with guard: active-=1
        threads=[threading.Thread(target=worker) for _ in range(4)]
        for t in threads:t.start()
        for t in threads:t.join()
        self.assertEqual(maximum,1)

if __name__=="__main__": unittest.main()
