"""Localhost candidate gallery with fail-closed 0.06 safety boundaries."""
from __future__ import annotations
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib, json, mimetypes
from pathlib import Path
from urllib.parse import quote, unquote, urlparse
from .dashboard import DashboardSettings, LocalDashboard, _PAGE as DRAFT_PAGE
from .dashboard_safety import MutationLock, local_request_allowed, validated_relative_path
from .workspace import CANDIDATE_STATES, create_preview_copy, load_workspace, save_workspace, set_candidate_preview, set_candidate_state
from .preparation import PreparationRecord, edit_preparation, evaluate_preparation, preparation_from_json, save_preparation_json
from .preflight import build_preflight_packet, preflight_to_text
from .image_analysis import analysis_from_json, analysis_observations

SELECTABLE_STATES=tuple(x for x in CANDIDATE_STATES if x!="submission-ready")

@dataclass(frozen=True)
class CandidateDashboardSettings:
    drafts: DashboardSettings; preview_root: Path; workspace_manifest: Path; preparation_directory: Path; analysis_directory: Path
    @classmethod
    def create(cls,source_root,drafts_directory,dictionary_path,preview_root=Path("local_previews"),workspace_manifest=Path("local_workspace")/"candidates.json",preparation_directory=Path("local_preparation"),analysis_directory=Path("local_analysis")):
        drafts=DashboardSettings.create(source_root,drafts_directory,dictionary_path)
        preview=Path(preview_root).expanduser().resolve(strict=False); manifest=Path(workspace_manifest).expanduser().resolve(strict=False); preparation=Path(preparation_directory).expanduser().resolve(strict=False); analysis=Path(analysis_directory).expanduser().resolve(strict=False)
        if preview.is_relative_to(drafts.source_root): raise ValueError("Preview workspace must be outside the selected source-photo folder.")
        if manifest.is_relative_to(drafts.source_root) or manifest.suffix.lower()!=".json": raise ValueError("Candidate workspace manifest must be external JSON.")
        if preparation.is_relative_to(drafts.source_root): raise ValueError("Preparation directory must be outside the selected source-photo folder.")
        if analysis.is_relative_to(drafts.source_root): raise ValueError("Analysis directory must be outside the selected source-photo folder.")
        return cls(drafts,preview,manifest,preparation,analysis)

class CandidateDashboard:
    def __init__(self,settings): self.settings=settings; self.drafts=LocalDashboard(settings.drafts); self._mutation=MutationLock()
    def _records(self): return load_workspace(self.settings.workspace_manifest) if self.settings.workspace_manifest.exists() else {}
    def _save(self,records): save_workspace(records,self.settings.workspace_manifest,self.settings.drafts.source_root,overwrite=self.settings.workspace_manifest.exists())
    def list_candidates(self):
        with self._mutation:
            records=self._records(); changed=False
            for name in self.drafts.list_drafts():
                rel=self.drafts.load_draft(name)["draft"]["relative_path"]
                if rel not in records: records=set_candidate_state(records,rel,"maybe"); changed=True
            if changed:self._save(records)
        out=[]
        for rel in sorted(records):
            rec=records[rel]; available=False
            if rec.preview_relative_path:
                try: available=self.preview_path(rec.preview_relative_path).is_file()
                except (FileNotFoundError,ValueError): pass
            out.append({"relative_path":rel,"state":rec.state,"legacy_submission_ready":rec.state=="submission-ready","preview_relative_path":rec.preview_relative_path,"preview_available":available,"preview_url":"/preview/"+quote(rec.preview_relative_path,safe="/") if available else ""})
        return out
    def set_state(self,payload):
        if not isinstance(payload,dict) or not isinstance(payload.get("relative_path"),str): raise ValueError("relative_path is required.")
        state=payload.get("state")
        if state not in SELECTABLE_STATES: raise ValueError("Unsupported candidate state; submission-ready requires consolidated readiness review.")
        with self._mutation: records=set_candidate_state(self._records(),payload["relative_path"],state); self._save(records)
        return {"relative_path":payload["relative_path"],"state":state}
    def create_preview(self,payload):
        if not isinstance(payload,dict) or not isinstance(payload.get("relative_path"),str): raise ValueError("relative_path is required.")
        if payload.get("consent") is not True: raise PermissionError("Explicit preview consent is required.")
        rel=payload["relative_path"]; dest=create_preview_copy(self.settings.drafts.source_root,rel,self.settings.preview_root,consent=True); preview_rel=dest.relative_to(self.settings.preview_root).as_posix()
        with self._mutation:
            records=set_candidate_preview(self._records(),rel,preview_rel); self._save(records)
        return {"relative_path":rel,"preview_relative_path":preview_rel,"preview_url":"/preview/"+quote(preview_rel,safe="/")}
    def _find_preparation_path(self,rel):
        if not self.settings.preparation_directory.exists(): return None
        for path in sorted(self.settings.preparation_directory.glob("*.json")):
            if path.is_symlink() or not path.is_file(): continue
            try: record=preparation_from_json(path.read_text(encoding="utf-8"))
            except (ValueError,json.JSONDecodeError,TypeError): continue
            if record.relative_path==rel:return path
        return None
    def load_preparation(self,payload):
        if not isinstance(payload,dict) or not isinstance(payload.get("relative_path"),str) or not payload["relative_path"]: raise ValueError("relative_path is required.")
        rel=payload["relative_path"]; path=self._find_preparation_path(rel); record=preparation_from_json(path.read_text(encoding="utf-8")) if path else PreparationRecord(rel); report=evaluate_preparation(record)
        return {"preparation":{"relative_path":record.relative_path,"title":record.title,"description":record.description,"keywords":list(record.keywords),"categories":list(record.categories),"route":record.route,"editor_target":record.editor_target,"working_export_relative_path":record.working_export_relative_path,"notes":record.notes},"prompts":[{"code":p.code,"explanation":p.explanation} for p in report.prompts]}
    def save_preparation(self,payload):
        with self._mutation:
            loaded=self.load_preparation(payload); p=loaded["preparation"]; existing=PreparationRecord(p["relative_path"],p["title"],p["description"],tuple(p["keywords"]),tuple(p["categories"]),p["route"],p["editor_target"],p["working_export_relative_path"],p["notes"]); changes={}
            for field in ("title","description","route","editor_target","working_export_relative_path","notes"):
                if field in payload:changes[field]=payload[field]
            for field in ("keywords","categories"):
                if field in payload:
                    if not isinstance(payload[field],list):raise ValueError(field+" must be a list.")
                    changes[field]=tuple(payload[field])
            updated=edit_preparation(existing,**changes); current=self._find_preparation_path(updated.relative_path)
            if current is None: current=self.settings.preparation_directory/(hashlib.sha256(updated.relative_path.encode()).hexdigest()[:16]+".json"); save_preparation_json(updated,current,self.settings.drafts.source_root)
            else: save_preparation_json(updated,current,self.settings.drafts.source_root,overwrite=True)
        return self.load_preparation({"relative_path":updated.relative_path})
    def _find_analysis(self,rel):
        if not self.settings.analysis_directory.exists():return None
        for path in sorted(self.settings.analysis_directory.glob("*.json")):
            if path.is_symlink() or not path.is_file():continue
            try:a=analysis_from_json(path.read_text(encoding="utf-8"))
            except (ValueError,json.JSONDecodeError,TypeError,KeyError):continue
            if a.relative_path==rel:return a
        return None
    def build_preflight(self,payload):
        p=self.load_preparation(payload)["preparation"]; record=PreparationRecord(p["relative_path"],p["title"],p["description"],tuple(p["keywords"]),tuple(p["categories"]),p["route"],p["editor_target"],p["working_export_relative_path"],p["notes"]); records=self._records(); state=records[record.relative_path].state if record.relative_path in records else "maybe"; raw=payload.get("preview_integrity","unknown")
        if raw not in ("unknown","match","mismatch"):raise ValueError("Unsupported preview_integrity value.")
        technical=list(payload.get("technical_observations",())); saved=self._find_analysis(record.relative_path)
        if saved is not None:technical.extend(analysis_observations(saved))
        packet=build_preflight_packet(record,candidate_state=state,technical_observations=technical,unresolved_rights_prompts=payload.get("rights_prompts",()),preview_integrity_confirmed={"unknown":None,"match":True,"mismatch":False}[raw],current_requirements_reviewed=payload.get("current_requirements_reviewed") is True)
        return {"local_packet_complete":packet.local_packet_complete,"text":preflight_to_text(packet)}
    def preview_path(self,relative_path):
        p=validated_relative_path(relative_path); root=self.settings.preview_root.resolve(strict=False); unresolved=root/p
        if unresolved.is_symlink():raise FileNotFoundError("Local preview not found.")
        target=unresolved.resolve(strict=True)
        if not target.is_relative_to(root) or not target.is_file():raise FileNotFoundError("Local preview not found.")
        return target

def serve_candidate_dashboard(settings,port=8765):
    dash=CandidateDashboard(settings); server=ThreadingHTTPServer(("127.0.0.1",port),_handler_for(dash)); print(f"Open http://127.0.0.1:{server.server_port} in your browser. Press Ctrl+C here to stop it.")
    try:server.serve_forever()
    except KeyboardInterrupt:print("Local dashboard stopped.")
    finally:server.server_close()

def _handler_for(dash):
    class Handler(BaseHTTPRequestHandler):
        def _local(self):return local_request_allowed(host_header=self.headers.get("Host"),origin_header=self.headers.get("Origin"))
        def do_GET(self):
            if not self._local():self._json(HTTPStatus.FORBIDDEN,{"error":"Localhost request required."});return
            path=urlparse(self.path).path
            try:
                if path=="/":self._send(HTTPStatus.OK,PAGE.encode(),"text/html; charset=utf-8")
                elif path=="/preparation":self._send(HTTPStatus.OK,PREPARATION_PAGE.encode(),"text/html; charset=utf-8")
                elif path=="/drafts":self._send(HTTPStatus.OK,DRAFT_PAGE.encode(),"text/html; charset=utf-8")
                elif path=="/api/candidates":self._json(HTTPStatus.OK,{"candidates":dash.list_candidates()})
                elif path=="/api/drafts":self._json(HTTPStatus.OK,{"drafts":dash.drafts.list_drafts()})
                elif path.startswith("/api/drafts/"):self._json(HTTPStatus.OK,dash.drafts.load_draft(unquote(path.removeprefix("/api/drafts/"))))
                elif path.startswith("/preview/"):p=dash.preview_path(unquote(path.removeprefix("/preview/")));self._send(HTTPStatus.OK,p.read_bytes(),mimetypes.guess_type(p.name)[0] or "application/octet-stream")
                else:self._json(HTTPStatus.NOT_FOUND,{"error":"Not found."})
            except (FileNotFoundError,PermissionError,ValueError,json.JSONDecodeError) as e:self._json(HTTPStatus.BAD_REQUEST,{"error":str(e)})
        def do_POST(self):
            if not self._local():self._json(HTTPStatus.FORBIDDEN,{"error":"Localhost request required."});return
            try:
                n=int(self.headers.get("Content-Length","0"));
                if not 0<n<=100000:raise ValueError("Request body must be small JSON.")
                payload=json.loads(self.rfile.read(n).decode()); path=urlparse(self.path).path
                routes={"/api/candidates/state":dash.set_state,"/api/preparation/load":dash.load_preparation,"/api/preparation/save":dash.save_preparation,"/api/preflight":dash.build_preflight,"/api/candidates/preview":dash.create_preview,"/api/accepted-spellings":dash.drafts.accept_spelling}
                if path in routes:self._json(HTTPStatus.OK,routes[path](payload))
                elif path.startswith("/api/drafts/"):self._json(HTTPStatus.OK,dash.drafts.update_draft(unquote(path.removeprefix("/api/drafts/")),payload))
                else:self._json(HTTPStatus.NOT_FOUND,{"error":"Not found."})
            except (FileNotFoundError,PermissionError,ValueError,json.JSONDecodeError) as e:self._json(HTTPStatus.BAD_REQUEST,{"error":str(e)})
        def _json(self,status,value):self._send(status,json.dumps(value).encode(),"application/json")
        def _send(self,status,data,ctype):
            self.send_response(status);self.send_header("Content-Type",ctype);self.send_header("Content-Length",str(len(data)));self.send_header("Cache-Control","no-store");self.send_header("X-Content-Type-Options","nosniff");self.send_header("Content-Security-Policy","default-src 'self'; img-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'");self.end_headers();self.wfile.write(data)
        def log_message(self,*args):return
    return Handler

PAGE="""<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Stock Photo Scout 0.06</title><style>body{font:16px system-ui;margin:20px;background:#f5f6f8}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}.card{background:white;padding:12px;border-radius:9px}.card img{width:100%;height:180px;object-fit:contain;background:#eee}select,button,a{padding:9px;margin-top:8px}.legacy{font-weight:bold}</style><h1>Stock Photo Scout</h1><p>Only local preview copies are displayed. Originals are never served to the browser.</p><a href='/drafts'>Open title / keyword / rights editor</a><div id=g class=grid></div><script>
const S=['skip','maybe','shortlist','edit','metadata-ready'];async function q(u,o){let r=await fetch(u,o),x=await r.json();if(!r.ok)throw Error(x.error);return x}async function load(){let d=await q('/api/candidates');g.replaceChildren();for(let c of d.candidates){let e=document.createElement('div');e.className='card';if(c.preview_available){let img=document.createElement('img');img.src=c.preview_url;img.alt='Local preview';e.append(img)}else{let n=document.createElement('div');n.textContent='No preview';e.append(n)}let name=document.createElement('div');name.textContent=c.relative_path;e.append(name);if(c.legacy_submission_ready){let w=document.createElement('div');w.className='legacy';w.textContent='Legacy submission-ready record — not authoritative under 0.06 readiness.';e.append(w)}let s=document.createElement('select');for(let x of S){s.add(new Option(x,x,x==c.state,x==c.state))}if(c.legacy_submission_ready)s.value='metadata-ready';s.onchange=async()=>{await q('/api/candidates/state',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({relative_path:c.relative_path,state:s.value})});load()};e.append(s);let p=document.createElement('a');p.href='/preparation?relative_path='+encodeURIComponent(c.relative_path);p.textContent='Preparation / preflight';p.style.display='block';e.append(p);if(!c.preview_available){let b=document.createElement('button');b.textContent='Create local preview';b.onclick=async()=>{if(confirm('Read this selected image to create a local preview copy? The original will not be modified.')){await q('/api/candidates/preview',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({relative_path:c.relative_path,consent:true})});load()}};e.append(b)}g.append(e)}}load()</script>"""

PREPARATION_PAGE="""<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Stock Photo Scout Preparation</title><style>body{font:16px system-ui;max-width:900px;margin:20px auto;padding:0 14px;background:#f5f6f8}label{display:block;margin:10px 0}input,textarea,select{width:100%;box-sizing:border-box;padding:8px}button,a{padding:9px;margin:8px 8px 8px 0}pre{white-space:pre-wrap;background:white;padding:12px;border-radius:8px}</style><a href='/'>Back to candidates</a><h1>Local preparation / preflight</h1><p>This page prepares a local packet only. It does not upload, submit, publish, or contact a marketplace.</p><label>Candidate<input id=rel readonly></label><label>Title<input id=title></label><label>Description<textarea id=description></textarea></label><label>Keywords (comma-separated)<input id=keywords></label><label>Categories (comma-separated)<input id=categories></label><label>Route<select id=route><option>undecided</option><option>commercial</option><option>editorial</option></select></label><label>Editor target<select id=editor_target><option>none</option><option>darktable</option><option>RawTherapee</option><option>GIMP</option><option>other</option></select></label><label>Working export relative path<input id=working_export_relative_path></label><label>Notes<textarea id=notes></textarea></label><button id=save>Save local preparation</button><h2>Prompts</h2><pre id=prompts></pre><h2>Manual preflight</h2><label>Preview integrity<select id=integrity><option value=unknown>Not checked</option><option value=match>Confirmed match</option><option value=mismatch>Mismatch</option></select></label><label><input type=checkbox id=req> Current marketplace requirements reviewed</label><button id=preflight>Build local preflight</button><pre id=packet></pre><script>
async function q(u,o){let r=await fetch(u,o),x=await r.json();if(!r.ok)throw Error(x.error);return x}let R=new URLSearchParams(location.search).get('relative_path')||'';rel.value=R;async function load(){let x=await q('/api/preparation/load',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({relative_path:R})}),p=x.preparation;for(let k of ['title','description','route','editor_target','working_export_relative_path','notes'])document.getElementById(k).value=p[k];keywords.value=p.keywords.join(', ');categories.value=p.categories.join(', ');prompts.textContent=x.prompts.map(x=>x.code+': '+x.explanation).join('\n')}save.onclick=async()=>{await q('/api/preparation/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({relative_path:R,title:title.value,description:description.value,keywords:keywords.value.split(',').map(x=>x.trim()).filter(Boolean),categories:categories.value.split(',').map(x=>x.trim()).filter(Boolean),route:route.value,editor_target:editor_target.value,working_export_relative_path:working_export_relative_path.value,notes:notes.value})});load()};preflight.onclick=async()=>{let x=await q('/api/preflight',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({relative_path:R,preview_integrity:integrity.value,current_requirements_reviewed:req.checked})});packet.textContent=x.text};load()</script>"""