"""Localhost-only HTTP surface for the 0.07 human review workflow."""
from __future__ import annotations
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from urllib.parse import parse_qs, urlparse
from .dashboard_safety import local_request_allowed
from .review_dashboard import REVIEW_PAGE, ReviewDashboardController

_MAX_BODY = 100_000

def _handler_for(controller: ReviewDashboardController):
    class Handler(BaseHTTPRequestHandler):
        def _local(self):
            return local_request_allowed(host_header=self.headers.get("Host"), origin_header=self.headers.get("Origin"))
        def do_GET(self):
            if not self._local():
                self._json(HTTPStatus.FORBIDDEN,{"error":"Localhost request required."}); return
            parsed=urlparse(self.path)
            if parsed.path=="/review":
                self._send(HTTPStatus.OK,REVIEW_PAGE.encode("utf-8"),"text/html; charset=utf-8"); return
            if parsed.path=="/api/review/shortlist-status":
                q=parse_qs(parsed.query,keep_blank_values=True); rel=(q.get("relative_path") or [""])[0]; state=(q.get("workspace_state") or ["maybe"])[0]
                try:
                    if not rel: raise ValueError("relative_path is required.")
                    self._json(HTTPStatus.OK,controller.shortlist_status(rel,state))
                except (ValueError,PermissionError,FileNotFoundError,json.JSONDecodeError) as exc:self._json(HTTPStatus.BAD_REQUEST,{"error":str(exc)})
                return
            self._json(HTTPStatus.NOT_FOUND,{"error":"Not found."})
        def do_POST(self):
            if not self._local():
                self._json(HTTPStatus.FORBIDDEN,{"error":"Localhost request required."}); return
            try:
                raw=self.headers.get("Content-Length")
                if raw is None: raise ValueError("Content-Length is required.")
                n=int(raw)
                if not 0<n<=_MAX_BODY: raise ValueError("Request body must be small JSON.")
                payload=json.loads(self.rfile.read(n).decode("utf-8")); path=urlparse(self.path).path
                if path=="/api/review/load": result=controller.load(payload)
                elif path=="/api/review/save": result=controller.save(payload)
                else: self._json(HTTPStatus.NOT_FOUND,{"error":"Not found."}); return
                self._json(HTTPStatus.OK,result)
            except (ValueError,PermissionError,FileNotFoundError,json.JSONDecodeError,UnicodeDecodeError) as exc:self._json(HTTPStatus.BAD_REQUEST,{"error":str(exc)})
        def _json(self,status,value):self._send(status,json.dumps(value,ensure_ascii=False).encode("utf-8"),"application/json; charset=utf-8")
        def _send(self,status,data,ctype):
            self.send_response(status); self.send_header("Content-Type",ctype); self.send_header("Content-Length",str(len(data))); self.send_header("Cache-Control","no-store"); self.send_header("X-Content-Type-Options","nosniff"); self.send_header("Content-Security-Policy","default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'"); self.end_headers(); self.wfile.write(data)
        def log_message(self,*args):return
    return Handler

def serve_review_dashboard(source_root, review_directory, port=8766):
    """Serve only the external 0.07 review state; originals are never served."""
    controller=ReviewDashboardController(source_root,review_directory)
    server=ThreadingHTTPServer(("127.0.0.1",port),_handler_for(controller))
    print(f"Open http://127.0.0.1:{server.server_port}/review?relative_path=<candidate> in your browser. Press Ctrl+C here to stop it.")
    try: server.serve_forever()
    except KeyboardInterrupt: print("Local review dashboard stopped.")
    finally: server.server_close()
