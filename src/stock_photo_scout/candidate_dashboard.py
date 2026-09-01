"""0.05A localhost candidate gallery layered over the existing draft dashboard."""
from __future__ import annotations
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json, mimetypes
from pathlib import Path
from urllib.parse import quote, unquote, urlparse
from .dashboard import DashboardSettings, LocalDashboard
from .workspace import CANDIDATE_STATES, create_preview_copy, load_workspace, save_workspace, set_candidate_state

@dataclass(frozen=True)
class CandidateDashboardSettings:
    drafts: DashboardSettings
    preview_root: Path
    workspace_manifest: Path

    @classmethod
    def create(cls, source_root, drafts_directory, dictionary_path,
               preview_root=Path("local_previews"),
               workspace_manifest=Path("local_workspace")/"candidates.json"):
        drafts=DashboardSettings.create(source_root,drafts_directory,dictionary_path)
        preview=Path(preview_root).expanduser().resolve(strict=False)
        manifest=Path(workspace_manifest).expanduser().resolve(strict=False)
        if preview.is_relative_to(drafts.source_root):
            raise ValueError("Preview workspace must be outside the selected source-photo folder.")
        if manifest.is_relative_to(drafts.source_root) or manifest.suffix.lower()!=".json":
            raise ValueError("Candidate workspace manifest must be external JSON.")
        return cls(drafts,preview,manifest)

class CandidateDashboard:
    def __init__(self,settings):
        self.settings=settings
        self.drafts=LocalDashboard(settings.drafts)

    def _records(self):
        return load_workspace(self.settings.workspace_manifest) if self.settings.workspace_manifest.exists() else {}

    def _save(self,records):
        save_workspace(records,self.settings.workspace_manifest,self.settings.drafts.source_root,
                       overwrite=self.settings.workspace_manifest.exists())

    def list_candidates(self):
        records=self._records()
        for name in self.drafts.list_drafts():
            rel=self.drafts.load_draft(name)["draft"]["relative_path"]
            if rel not in records:
                records=set_candidate_state(records,rel,"maybe")
        out=[]
        for rel in sorted(records):
            rec=records[rel]; available=False
            if rec.preview_relative_path:
                try: available=self.preview_path(rec.preview_relative_path).is_file()
                except (FileNotFoundError,ValueError): pass
            out.append({"relative_path":rel,"state":rec.state,
                        "preview_relative_path":rec.preview_relative_path,
                        "preview_available":available,
                        "preview_url":"/preview/"+quote(rec.preview_relative_path,safe="/") if available else ""})
        return out

    def set_state(self,payload):
        if not isinstance(payload,dict) or not isinstance(payload.get("relative_path"),str):
            raise ValueError("relative_path is required.")
        if payload.get("state") not in CANDIDATE_STATES:
            raise ValueError("Unsupported candidate state.")
        records=set_candidate_state(self._records(),payload["relative_path"],payload["state"])
        self._save(records)
        return {"relative_path":payload["relative_path"],"state":payload["state"]}

    def create_preview(self,payload):
        if not isinstance(payload,dict) or not isinstance(payload.get("relative_path"),str):
            raise ValueError("relative_path is required.")
        if payload.get("consent") is not True:
            raise PermissionError("Explicit preview consent is required.")
        rel=payload["relative_path"]
        dest=create_preview_copy(self.settings.drafts.source_root,rel,self.settings.preview_root,consent=True)
        preview_rel=dest.relative_to(self.settings.preview_root).as_posix()
        records=self._records(); state=records[rel].state if rel in records else "maybe"
        records=set_candidate_state(records,rel,state,preview_relative_path=preview_rel)
        self._save(records)
        return {"relative_path":rel,"preview_relative_path":preview_rel,
                "preview_url":"/preview/"+quote(preview_rel,safe="/")}

    def preview_path(self,relative_path):
        p=Path(relative_path)
        if not relative_path or p.is_absolute() or ".." in p.parts:
            raise ValueError("Invalid preview path.")
        root=self.settings.preview_root.resolve(strict=False)
        target=(root/p).resolve(strict=True)
        if not target.is_relative_to(root) or target.is_symlink() or not target.is_file():
            raise FileNotFoundError("Local preview not found.")
        return target

def serve_candidate_dashboard(settings,port=8765):
    dash=CandidateDashboard(settings)
    server=ThreadingHTTPServer(("127.0.0.1",port),_handler_for(dash))
    print(f"Open http://127.0.0.1:{server.server_port} in your browser. Press Ctrl+C here to stop it.")
    try: server.serve_forever()
    except KeyboardInterrupt: print("Local dashboard stopped.")
    finally: server.server_close()

def _handler_for(dash):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path=urlparse(self.path).path
            try:
                if path=="/": self._send(HTTPStatus.OK,PAGE.encode(),"text/html; charset=utf-8")
                elif path=="/api/candidates": self._json(HTTPStatus.OK,{"candidates":dash.list_candidates()})
                elif path.startswith("/preview/"):
                    p=dash.preview_path(unquote(path.removeprefix("/preview/")))
                    self._send(HTTPStatus.OK,p.read_bytes(),mimetypes.guess_type(p.name)[0] or "application/octet-stream")
                else: self._json(HTTPStatus.NOT_FOUND,{"error":"Not found."})
            except (FileNotFoundError,PermissionError,ValueError,json.JSONDecodeError) as e:
                self._json(HTTPStatus.BAD_REQUEST,{"error":str(e)})
        def do_POST(self):
            try:
                n=int(self.headers.get("Content-Length","0"))
                if not 0<n<=100000: raise ValueError("Request body must be small JSON.")
                payload=json.loads(self.rfile.read(n).decode())
                path=urlparse(self.path).path
                if path=="/api/candidates/state": self._json(HTTPStatus.OK,dash.set_state(payload))
                elif path=="/api/candidates/preview": self._json(HTTPStatus.OK,dash.create_preview(payload))
                else: self._json(HTTPStatus.NOT_FOUND,{"error":"Not found."})
            except (FileNotFoundError,PermissionError,ValueError,json.JSONDecodeError) as e:
                self._json(HTTPStatus.BAD_REQUEST,{"error":str(e)})
        def _json(self,status,value): self._send(status,json.dumps(value).encode(),"application/json")
        def _send(self,status,data,ctype):
            self.send_response(status); self.send_header("Content-Type",ctype)
            self.send_header("Content-Length",str(len(data))); self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff"); self.end_headers(); self.wfile.write(data)
        def log_message(self,*args): return
    return Handler

PAGE="""<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Stock Photo Scout 0.05A</title>
<style>body{font:16px system-ui;margin:20px;background:#f5f6f8}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}.card{background:white;padding:12px;border-radius:9px}.card img{width:100%;height:180px;object-fit:contain;background:#eee}select,button{width:100%;padding:9px;margin-top:8px}</style>
<h1>Stock Photo Scout</h1><p>Only local preview copies are displayed. Originals are never served to the browser.</p><div id=g class=grid></div>
<script>
const S=['skip','maybe','shortlist','edit','metadata-ready','submission-ready'];
async function q(u,o){let r=await fetch(u,o),x=await r.json();if(!r.ok)throw Error(x.error);return x}
async function load(){let d=await q('/api/candidates');g.innerHTML='';for(let c of d.candidates){let e=document.createElement('div');e.className='card';e.innerHTML=(c.preview_available?'<img src="'+c.preview_url+'">':'<div>No preview</div>')+'<div>'+c.relative_path+'</div>';let s=document.createElement('select');for(let x of S){let o=new Option(x,x,x==c.state,x==c.state);s.add(o)}s.onchange=()=>q('/api/candidates/state',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({relative_path:c.relative_path,state:s.value})});e.append(s);if(!c.preview_available){let b=document.createElement('button');b.textContent='Create local preview';b.onclick=async()=>{if(confirm('Read this selected image to create a local preview copy? The original will not be modified.')){await q('/api/candidates/preview',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({relative_path:c.relative_path,consent:true})});load()}};e.append(b)}g.append(e)}}load()
</script>"""
