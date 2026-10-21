import json, sys, threading, unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from stock_photo_scout.review_dashboard import ReviewDashboardController
from stock_photo_scout.review_server import _handler_for

class ReviewServerTests(unittest.TestCase):
 def setUp(self):
  self.tmp=TemporaryDirectory(); root=Path(self.tmp.name); self.source=root/"source"; self.reviews=root/"reviews"; self.source.mkdir(); self.controller=ReviewDashboardController(self.source,self.reviews); self.server=ThreadingHTTPServer(("127.0.0.1",0),_handler_for(self.controller)); self.thread=threading.Thread(target=self.server.serve_forever,daemon=True); self.thread.start()
 def tearDown(self):self.server.shutdown();self.server.server_close();self.thread.join(timeout=2);self.tmp.cleanup()
 def request(self,method,path,body=None,headers=None):
  conn=HTTPConnection("127.0.0.1",self.server.server_port,timeout=2); data=None if body is None else json.dumps(body); h={"Host":f"127.0.0.1:{self.server.server_port}"};h.update(headers or {});conn.request(method,path,body=data,headers=h);r=conn.getresponse();payload=r.read();conn.close();return r.status,payload
 def test_review_page_is_local_and_does_not_serve_originals(self):
  (self.source/"private.jpg").write_bytes(b"secret-photo-bytes"); status,body=self.request("GET","/review?relative_path=private.jpg");self.assertEqual(status,200);self.assertNotIn(b"secret-photo-bytes",body);status,_=self.request("GET","/private.jpg");self.assertEqual(status,404)
 def test_nonlocal_host_is_rejected(self):
  status,_=self.request("GET","/review",headers={"Host":"example.com"});self.assertEqual(status,403)
 def test_nonlocal_origin_is_rejected(self):
  status,_=self.request("GET","/review",headers={"Origin":"https://example.com"});self.assertEqual(status,403)
 def test_load_and_save_are_json_only(self):
  status,body=self.request("POST","/api/review/load",{"relative_path":"a.jpg"});self.assertEqual(status,200);self.assertIn(b'"assessment"',body)
  status,body=self.request("POST","/api/review/save",{"relative_path":"a.jpg","screen_decision":"hold"});self.assertEqual(status,200);self.assertIn(b'"hold"',body)
 def test_path_traversal_fails_closed(self):
  status,_=self.request("POST","/api/review/load",{"relative_path":"../a.jpg"});self.assertEqual(status,400)
 def test_oversize_body_rejected_before_read(self):
  conn=HTTPConnection("127.0.0.1",self.server.server_port,timeout=2);conn.request("POST","/api/review/load",body=b"{}",headers={"Host":f"127.0.0.1:{self.server.server_port}","Content-Length":"100001"});r=conn.getresponse();self.assertEqual(r.status,400);r.read();conn.close()
if __name__=="__main__":unittest.main()
