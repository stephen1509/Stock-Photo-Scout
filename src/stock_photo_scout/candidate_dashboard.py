"""0.05A localhost candidate gallery layered over the existing draft dashboard."""
from __future__ import annotations
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib
import json, mimetypes
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse
from .dashboard import DashboardSettings, LocalDashboard, _PAGE as DRAFT_PAGE
from .workspace import CANDIDATE_STATES, create_preview_copy, load_workspace, save_workspace, set_candidate_state
from .preparation import (
    PreparationRecord, edit_preparation, evaluate_preparation,
    preparation_from_json, save_preparation_json,
)
from .preflight import build_preflight_packet, preflight_to_text
from .image_analysis import analysis_from_json, analysis_observations

@dataclass(frozen=True)
class CandidateDashboardSettings:
    drafts: DashboardSettings
    preview_root: Path
    workspace_manifest: Path
    preparation_directory: Path
    analysis_directory: Path

    @classmethod
    def create(cls, source_root, drafts_directory, dictionary_path,
               preview_root=Path("local_previews"),
               workspace_manifest=Path("local_workspace")/"candidates.json",
               preparation_directory=Path("local_preparation"),
               analysis_directory=Path("local_analysis")):
        drafts=DashboardSettings.create(source_root,drafts_directory,dictionary_path)
        preview=Path(preview_root).expanduser().resolve(strict=False)
        manifest=Path(workspace_manifest).expanduser().resolve(strict=False)
        preparation=Path(preparation_directory).expanduser().resolve(strict=False)
        analysis=Path(analysis_directory).expanduser().resolve(strict=False)
        if preview.is_relative_to(drafts.source_root):
            raise ValueError("Preview workspace must be outside the selected source-photo folder.")
        if manifest.is_relative_to(drafts.source_root) or manifest.suffix.lower()!=".json":
            raise ValueError("Candidate workspace manifest must be external JSON.")
        if preparation.is_relative_to(drafts.source_root):
            raise ValueError("Preparation directory must be outside the selected source-photo folder.")
        if analysis.is_relative_to(drafts.source_root):
            raise ValueError("Analysis directory must be outside the selected source-photo folder.")
        return cls(drafts,preview,manifest,preparation,analysis)

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

    def _find_preparation_path(self, relative_path):
        if not self.settings.preparation_directory.exists():
            return None
        for path in sorted(self.settings.preparation_directory.glob("*.json")):
            if path.is_symlink() or not path.is_file():
                continue
            try:
                record=preparation_from_json(path.read_text(encoding="utf-8"))
            except (ValueError, json.JSONDecodeError, TypeError):
                continue
            if record.relative_path == relative_path:
                return path
        return None

    def load_preparation(self, payload):
        if not isinstance(payload,dict) or not isinstance(payload.get("relative_path"),str) or not payload["relative_path"]:
            raise ValueError("relative_path is required.")
        rel=payload["relative_path"]
        path=self._find_preparation_path(rel)
        record=preparation_from_json(path.read_text(encoding="utf-8")) if path else PreparationRecord(rel)
        report=evaluate_preparation(record)
        return {
            "preparation":{
                "relative_path":record.relative_path,
                "title":record.title,
                "description":record.description,
                "keywords":list(record.keywords),
                "categories":list(record.categories),
                "route":record.route,
                "editor_target":record.editor_target,
                "working_export_relative_path":record.working_export_relative_path,
                "notes":record.notes,
            },
            "prompts":[{"code":p.code,"explanation":p.explanation} for p in report.prompts],
        }

    def save_preparation(self, payload):
        loaded=self.load_preparation(payload)
        existing=PreparationRecord(
            relative_path=loaded["preparation"]["relative_path"],
            title=loaded["preparation"]["title"],
            description=loaded["preparation"]["description"],
            keywords=tuple(loaded["preparation"]["keywords"]),
            categories=tuple(loaded["preparation"]["categories"]),
            route=loaded["preparation"]["route"],
            editor_target=loaded["preparation"]["editor_target"],
            working_export_relative_path=loaded["preparation"]["working_export_relative_path"],
            notes=loaded["preparation"]["notes"],
        )
        changes={}
        for field in ("title","description","route","editor_target","working_export_relative_path","notes"):
            if field in payload:
                changes[field]=payload[field]
        if "keywords" in payload:
            if not isinstance(payload["keywords"],list): raise ValueError("keywords must be a list.")
            changes["keywords"]=tuple(payload["keywords"])
        if "categories" in payload:
            if not isinstance(payload["categories"],list): raise ValueError("categories must be a list.")
            changes["categories"]=tuple(payload["categories"])
        updated=edit_preparation(existing,**changes)
        current=self._find_preparation_path(updated.relative_path)
        if current is None:
            digest=hashlib.sha256(updated.relative_path.encode("utf-8")).hexdigest()[:16]
            current=self.settings.preparation_directory/(digest+".json")
            save_preparation_json(updated,current,self.settings.drafts.source_root)
        else:
            save_preparation_json(updated,current,self.settings.drafts.source_root,overwrite=True)
        return self.load_preparation({"relative_path":updated.relative_path})

    def _find_analysis(self, relative_path):
        if not self.settings.analysis_directory.exists():
            return None
        for path in sorted(self.settings.analysis_directory.glob("*.json")):
            if path.is_symlink() or not path.is_file():
                continue
            try:
                analysis=analysis_from_json(path.read_text(encoding="utf-8"))
            except (ValueError, json.JSONDecodeError, TypeError, KeyError):
                continue
            if analysis.relative_path == relative_path:
                return analysis
        return None

    def build_preflight(self, payload):
        prep=self.load_preparation(payload)["preparation"]
        record=PreparationRecord(
            relative_path=prep["relative_path"], title=prep["title"], description=prep["description"],
            keywords=tuple(prep["keywords"]), categories=tuple(prep["categories"]), route=prep["route"],
            editor_target=prep["editor_target"], working_export_relative_path=prep["working_export_relative_path"],
            notes=prep["notes"],
        )
        records=self._records()
        state=records[record.relative_path].state if record.relative_path in records else "maybe"
        integrity={"unknown":None,"match":True,"mismatch":False}.get(payload.get("preview_integrity","unknown"))
        if payload.get("preview_integrity","unknown") not in ("unknown","match","mismatch"):
            raise ValueError("Unsupported preview_integrity value.")
        technical=list(payload.get("technical_observations",()))
        saved_analysis=self._find_analysis(record.relative_path)
        if saved_analysis is not None:
            technical.extend(analysis_observations(saved_analysis))
        packet=build_preflight_packet(
            record,
            candidate_state=state,
            technical_observations=technical,
            unresolved_rights_prompts=payload.get("rights_prompts",()),
            preview_integrity_confirmed=integrity,
            current_requirements_reviewed=payload.get("current_requirements_reviewed") is True,
        )
        return {"local_packet_complete":packet.local_packet_complete,"text":preflight_to_text(packet)}

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
                elif path=="/preparation": self._send(HTTPStatus.OK,PREPARATION_PAGE.encode(),"text/html; charset=utf-8")
                elif path=="/drafts": self._send(HTTPStatus.OK,DRAFT_PAGE.encode(),"text/html; charset=utf-8")
                elif path=="/api/candidates": self._json(HTTPStatus.OK,{"candidates":dash.list_candidates()})
                elif path=="/api/drafts": self._json(HTTPStatus.OK,{"drafts":dash.drafts.list_drafts()})
                elif path.startswith("/api/drafts/"):
                    self._json(HTTPStatus.OK,dash.drafts.load_draft(unquote(path.removeprefix("/api/drafts/"))))
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
                elif path=="/api/preparation/load": self._json(HTTPStatus.OK,dash.load_preparation(payload))
                elif path=="/api/preparation/save": self._json(HTTPStatus.OK,dash.save_preparation(payload))
                elif path=="/api/preflight": self._json(HTTPStatus.OK,dash.build_preflight(payload))
                elif path=="/api/candidates/preview": self._json(HTTPStatus.OK,dash.create_preview(payload))
                elif path=="/api/accepted-spellings": self._json(HTTPStatus.OK,dash.drafts.accept_spelling(payload))
                elif path.startswith("/api/drafts/"):
                    self._json(HTTPStatus.OK,dash.drafts.update_draft(unquote(path.removeprefix("/api/drafts/")),payload))
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
<style>body{font:16px system-ui;margin:20px;background:#f5f6f8}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}.card{background:white;padding:12px;border-radius:9px}.card img{width:100%;height:180px;object-fit:contain;background:#eee}select,button,a{padding:9px;margin-top:8px}.draftlink{display:inline-block;background:#0756a8;color:white;text-decoration:none;border-radius:6px;margin-bottom:14px}</style>
<h1>Stock Photo Scout</h1><p>Only local preview copies are displayed. Originals are never served to the browser.</p>
<a class=draftlink href='/drafts'>Open title / keyword / rights editor</a><div id=g class=grid></div>
<script>
const S=['skip','maybe','shortlist','edit','metadata-ready','submission-ready'];
async function q(u,o){let r=await fetch(u,o),x=await r.json();if(!r.ok)throw Error(x.error);return x}
async function load(){let d=await q('/api/candidates');g.innerHTML='';for(let c of d.candidates){let e=document.createElement('div');e.className='card';e.innerHTML=(c.preview_available?'<img src="'+c.preview_url+'">':'<div>No preview</div>')+'<div>'+c.relative_path+'</div>';let s=document.createElement('select');for(let x of S){let o=new Option(x,x,x==c.state,x==c.state);s.add(o)}s.onchange=()=>q('/api/candidates/state',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({relative_path:c.relative_path,state:s.value})});e.append(s);let p=document.createElement('a');p.href='/preparation?relative_path='+encodeURIComponent(c.relative_path);p.textContent='Preparation / preflight';p.style.display='block';e.append(p);if(!c.preview_available){let b=document.createElement('button');b.textContent='Create local preview';b.onclick=async()=>{if(confirm('Read this selected image to create a local preview copy? The original will not be modified.')){await q('/api/candidates/preview',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({relative_path:c.relative_path,consent:true})});load()}};e.append(b)}g.append(e)}}load()
</script>"""


PREPARATION_PAGE="""<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>Stock Photo Scout Preparation</title>
<style>body{font:16px system-ui;max-width:900px;margin:20px auto;padding:0 14px;background:#f5f6f8}label{display:block;margin:10px 0}input,textarea,select{width:100%;box-sizing:border-box;padding:8px}button,a{padding:9px;margin:8px 8px 8px 0}pre{white-space:pre-wrap;background:white;padding:12px;border-radius:8px}</style>
<a href='/'>Back to candidates</a><h1>Preparation / manual preflight</h1>
<p>This page edits local preparation JSON only. It does not upload or submit anything.</p>
<form id=f><label>Title<input id=title></label><label>Description<textarea id=description></textarea></label>
<label>Keywords (one per line)<textarea id=keywords></textarea></label><label>Categories (one per line)<textarea id=categories></textarea></label>
<label>Route<select id=route><option>undecided</option><option>commercial</option><option>editorial</option></select></label>
<label>Editor<select id=editor><option>none</option><option>darktable</option><option>rawtherapee</option><option>gimp</option><option>other</option></select></label>
<label>Working export relative path<input id=exportp></label><label>Notes<textarea id=notes></textarea></label>
<button>Save local preparation</button></form>
<label><input type=checkbox id=req style='width:auto'> Current Dreamstime requirements reviewed for this submission session</label>
<label>Preview integrity<select id=integrity><option>unknown</option><option>match</option><option>mismatch</option></select></label>
<button id=pf>Build manual preflight</button><pre id=out></pre>
<script>
const rel=new URLSearchParams(location.search).get('relative_path');if(!rel)throw Error('relative_path missing');
async function q(u,b){let r=await fetch(u,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)}),x=await r.json();if(!r.ok)throw Error(x.error);return x}
async function load(){let x=await q('/api/preparation/load',{relative_path:rel}),p=x.preparation;title.value=p.title;description.value=p.description;keywords.value=p.keywords.join('\n');categories.value=p.categories.join('\n');route.value=p.route;editor.value=p.editor_target;exportp.value=p.working_export_relative_path;notes.value=p.notes;out.textContent=x.prompts.map(y=>y.code+': '+y.explanation).join('\n')}
f.onsubmit=async e=>{e.preventDefault();await q('/api/preparation/save',{relative_path:rel,title:title.value,description:description.value,keywords:keywords.value.split('\n').map(x=>x.trim()).filter(Boolean),categories:categories.value.split('\n').map(x=>x.trim()).filter(Boolean),route:route.value,editor_target:editor.value,working_export_relative_path:exportp.value,notes:notes.value});await load()}
pf.onclick=async()=>{let x=await q('/api/preflight',{relative_path:rel,preview_integrity:integrity.value,current_requirements_reviewed:req.checked});out.textContent=x.text}
load()
</script>"""
