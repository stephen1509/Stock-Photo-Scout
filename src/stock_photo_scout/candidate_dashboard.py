"""Localhost candidate gallery with fail-closed 0.07 review integration."""
from __future__ import annotations
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hashlib,json,mimetypes
from pathlib import Path
from urllib.parse import quote,unquote,urlparse
from .dashboard import DashboardSettings,LocalDashboard,_PAGE as DRAFT_PAGE
from .dashboard_safety import MutationLock,local_request_allowed,validated_relative_path
from .workspace import CANDIDATE_STATES,create_preview_copy,load_workspace,save_workspace,set_candidate_preview,set_candidate_state
from .preparation import CategoryPair,PreparationRecord,edit_preparation,evaluate_preparation,preparation_from_json,save_preparation_json
from .preflight import build_preflight_packet,preflight_to_text
from .image_analysis import analysis_from_json,analysis_observations
from .review_service import ReviewService
from .review_dashboard_api import load_review_payload,save_review_payload
from .review_dashboard import REVIEW_PAGE
from .shortlist_gate import assess_workspace_transition,authoritative_shortlist_allowed

SELECTABLE_STATES=tuple(x for x in CANDIDATE_STATES if x!="submission-ready")
@dataclass(frozen=True)
class CandidateDashboardSettings:
 drafts:DashboardSettings;preview_root:Path;workspace_manifest:Path;preparation_directory:Path;analysis_directory:Path;review_directory:Path
 @classmethod
 def create(cls,source_root,drafts_directory,dictionary_path,preview_root=Path("local_previews"),workspace_manifest=Path("local_workspace")/"candidates.json",preparation_directory=Path("local_preparation"),analysis_directory=Path("local_analysis"),review_directory=Path("local_reviews")):
  drafts=DashboardSettings.create(source_root,drafts_directory,dictionary_path);values=[Path(x).expanduser().resolve(strict=False) for x in (preview_root,workspace_manifest,preparation_directory,analysis_directory,review_directory)];preview,manifest,preparation,analysis,review=values
  if preview.is_relative_to(drafts.source_root):raise ValueError("Preview workspace must be outside the selected source-photo folder.")
  if manifest.is_relative_to(drafts.source_root) or manifest.suffix.lower()!=".json":raise ValueError("Candidate workspace manifest must be external JSON.")
  for value,label in ((preparation,"Preparation"),(analysis,"Analysis"),(review,"Review")):
   if value.is_relative_to(drafts.source_root):raise ValueError(label+" directory must be outside the selected source-photo folder.")
  return cls(drafts,preview,manifest,preparation,analysis,review)
class CandidateDashboard:
 def __init__(self,settings):self.settings=settings;self.drafts=LocalDashboard(settings.drafts);self.reviews=ReviewService(settings.drafts.source_root,settings.review_directory);self._mutation=MutationLock()
 def _records(self):return load_workspace(self.settings.workspace_manifest) if self.settings.workspace_manifest.exists() else {}
 def _save(self,r):save_workspace(r,self.settings.workspace_manifest,self.settings.drafts.source_root,overwrite=self.settings.workspace_manifest.exists())
 def list_candidates(self):
  with self._mutation:
   records=self._records();changed=False
   for name in self.drafts.list_drafts():
    rel=self.drafts.load_draft(name)["draft"]["relative_path"]
    if rel not in records:records=set_candidate_state(records,rel,"maybe");changed=True
   if changed:self._save(records)
  out=[]
  for rel in sorted(records):
   rec=records[rel];available=False
   if rec.preview_relative_path:
    try:available=self.preview_path(rec.preview_relative_path).is_file()
    except (FileNotFoundError,ValueError):pass
   assessment=self.reviews.load(rel)["assessment"];out.append({"relative_path":rel,"state":rec.state,"authoritative_shortlist":authoritative_shortlist_allowed(rec.state,assessment["can_shortlist"]),"review_can_shortlist":assessment["can_shortlist"],"review_blockers":assessment["blockers"],"legacy_submission_ready":rec.state=="submission-ready","preview_relative_path":rec.preview_relative_path,"preview_available":available,"preview_url":"/preview/"+quote(rec.preview_relative_path,safe="/") if available else ""})
  return out
 def set_state(self,p):
  if not isinstance(p,dict) or not isinstance(p.get("relative_path"),str):raise ValueError("relative_path is required.")
  state=p.get("state")
  if state not in SELECTABLE_STATES:raise ValueError("Unsupported candidate state; submission-ready requires consolidated readiness review.")
  gate=assess_workspace_transition(self.reviews,p["relative_path"],state)
  if not gate.allowed:raise ValueError("Shortlist blocked: "+"; ".join(gate.blockers))
  with self._mutation:r=set_candidate_state(self._records(),p["relative_path"],state);self._save(r)
  return {"relative_path":p["relative_path"],"state":state,"authoritative_review_complete":gate.authoritative_review_complete}
 def load_review(self,p):return load_review_payload(self.reviews,p)
 def save_review(self,p):
  with self._mutation:return save_review_payload(self.reviews,p)
 def create_preview(self,p):
  if not isinstance(p,dict) or not isinstance(p.get("relative_path"),str):raise ValueError("relative_path is required.")
  if p.get("consent") is not True:raise PermissionError("Explicit preview consent is required.")
  rel=p["relative_path"];dest=create_preview_copy(self.settings.drafts.source_root,rel,self.settings.preview_root,consent=True);preview_rel=dest.relative_to(self.settings.preview_root).as_posix()
  with self._mutation:r=set_candidate_preview(self._records(),rel,preview_rel);self._save(r)
  return {"relative_path":rel,"preview_relative_path":preview_rel,"preview_url":"/preview/"+quote(preview_rel,safe="/")}
 def _find_preparation_path(self,rel):
  if not self.settings.preparation_directory.exists():return None
  for path in sorted(self.settings.preparation_directory.glob("*.json")):
   if path.is_symlink() or not path.is_file():continue
   try:record=preparation_from_json(path.read_text(encoding="utf-8"))
   except (ValueError,json.JSONDecodeError,TypeError):continue
   if record.relative_path==rel:return path
  return None
 def load_preparation(self,p):
  if not isinstance(p,dict) or not isinstance(p.get("relative_path"),str) or not p["relative_path"]:raise ValueError("relative_path is required.")
  rel=p["relative_path"];path=self._find_preparation_path(rel);r=preparation_from_json(path.read_text(encoding="utf-8")) if path else PreparationRecord(rel);report=evaluate_preparation(r)
  return {"preparation":{"relative_path":r.relative_path,"title":r.title,"description":r.description,"keywords":list(r.keywords),"categories":list(r.categories),"category_pairs":[{"category":x.category,"subcategory":x.subcategory} for x in r.category_pairs],"route":r.route,"editor_target":r.editor_target,"working_export_relative_path":r.working_export_relative_path,"notes":r.notes},"prompts":[{"code":x.code,"explanation":x.explanation} for x in report.prompts]}
 def _prep_record(self,p):return PreparationRecord(relative_path=p["relative_path"],title=p["title"],description=p["description"],keywords=tuple(p["keywords"]),categories=tuple(p["categories"]),category_pairs=tuple(CategoryPair(x["category"],x.get("subcategory","")) for x in p.get("category_pairs",[])),route=p["route"],editor_target=p["editor_target"],working_export_relative_path=p["working_export_relative_path"],notes=p["notes"])
 def save_preparation(self,payload):
  with self._mutation:
   p=self.load_preparation(payload)["preparation"];existing=self._prep_record(p);changes={}
   for f in ("title","description","route","editor_target","working_export_relative_path","notes"):
    if f in payload:changes[f]=payload[f]
   for f in ("keywords","categories"):
    if f in payload:
     if not isinstance(payload[f],list):raise ValueError(f+" must be a list.")
     changes[f]=tuple(payload[f])
   if "category_pairs" in payload:
    if not isinstance(payload["category_pairs"],list) or any(not isinstance(x,dict) for x in payload["category_pairs"]):raise ValueError("category_pairs must be a list of objects.")
    changes["category_pairs"]=tuple(CategoryPair(x.get("category",""),x.get("subcategory","")) for x in payload["category_pairs"])
   updated=edit_preparation(existing,**changes);current=self._find_preparation_path(updated.relative_path)
   if current is None:current=self.settings.preparation_directory/(hashlib.sha256(updated.relative_path.encode()).hexdigest()[:16]+".json");save_preparation_json(updated,current,self.settings.drafts.source_root)
   else:save_preparation_json(updated,current,self.settings.drafts.source_root,overwrite=True)
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
  p=self.load_preparation(payload)["preparation"];record=self._prep_record(p);records=self._records();state=records[record.relative_path].state if record.relative_path in records else "maybe";raw=payload.get("preview_integrity","unknown")
  if raw not in ("unknown","match","mismatch"):raise ValueError("Unsupported preview_integrity value.")
  technical=list(payload.get("technical_observations",()));saved=self._find_analysis(record.relative_path)
  if saved is not None:technical.extend(analysis_observations(saved))
  packet=build_preflight_packet(record,candidate_state=state,technical_observations=technical,unresolved_rights_prompts=payload.get("rights_prompts",()),preview_integrity_confirmed={"unknown":None,"match":True,"mismatch":False}[raw],current_requirements_reviewed=payload.get("current_requirements_reviewed") is True)
  return {"local_packet_complete":packet.local_packet_complete,"text":preflight_to_text(packet)}
 def preview_path(self,relative_path):
  p=validated_relative_path(relative_path);root=self.settings.preview_root.resolve(strict=False);unresolved=root/p
  if unresolved.is_symlink():raise FileNotFoundError("Local preview not found.")
  target=unresolved.resolve(strict=True)
  if not target.is_relative_to(root) or not target.is_file():raise FileNotFoundError("Local preview not found.")
  return target
def serve_candidate_dashboard(settings,port=8765):
 dash=CandidateDashboard(settings);server=ThreadingHTTPServer(("127.0.0.1",port),_handler_for(dash));print(f"Open http://127.0.0.1:{server.server_port} in your browser. Press Ctrl+C here to stop it.")
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
    elif path=="/review":self._send(HTTPStatus.OK,REVIEW_PAGE.encode(),"text/html; charset=utf-8")
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
    n=int(self.headers.get("Content-Length","0"))
    if not 0<n<=100000:raise ValueError("Request body must be small JSON.")
    payload=json.loads(self.rfile.read(n).decode());path=urlparse(self.path).path;routes={"/api/candidates/state":dash.set_state,"/api/review/load":dash.load_review,"/api/review/save":dash.save_review,"/api/preparation/load":dash.load_preparation,"/api/preparation/save":dash.save_preparation,"/api/preflight":dash.build_preflight,"/api/candidates/preview":dash.create_preview,"/api/accepted-spellings":dash.drafts.accept_spelling}
    if path in routes:self._json(HTTPStatus.OK,routes[path](payload))
    elif path.startswith("/api/drafts/"):self._json(HTTPStatus.OK,dash.drafts.update_draft(unquote(path.removeprefix("/api/drafts/")),payload))
    else:self._json(HTTPStatus.NOT_FOUND,{"error":"Not found."})
   except (FileNotFoundError,PermissionError,ValueError,json.JSONDecodeError,TypeError,KeyError) as e:self._json(HTTPStatus.BAD_REQUEST,{"error":str(e)})
  def _json(self,status,value):self._send(status,json.dumps(value).encode(),"application/json")
  def _send(self,status,data,ctype):self.send_response(status);self.send_header("Content-Type",ctype);self.send_header("Content-Length",str(len(data)));self.send_header("Cache-Control","no-store");self.send_header("X-Content-Type-Options","nosniff");self.send_header("Content-Security-Policy","default-src 'self'; img-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'");self.end_headers();self.wfile.write(data)
  def log_message(self,*args):return
 return Handler
PAGE="""<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Stock Photo Scout 0.07</title><style>body{font:16px system-ui;margin:20px;background:#f5f6f8}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}.card{background:white;padding:12px;border-radius:9px}.card img{width:100%;height:180px;object-fit:contain;background:#eee}select,button,a{padding:9px;margin-top:8px}.warn{font-weight:bold}.ok{font-weight:bold}</style><h1>Stock Photo Scout</h1><p>Only local preview copies are displayed. Originals are never served to the browser. Shortlist is authoritative only after 0.07 human review qualifies it.</p><a href='/drafts'>Open title / keyword / rights editor</a><div id=g class=grid></div><script>const S=['skip','maybe','shortlist','edit','metadata-ready'];async function q(u,o){let r=await fetch(u,o),x=await r.json();if(!r.ok)throw Error(x.error);return x}async function load(){let d=await q('/api/candidates');g.replaceChildren();for(let c of d.candidates){let e=document.createElement('div');e.className='card';if(c.preview_available){let i=document.createElement('img');i.src=c.preview_url;i.alt='Local preview';e.append(i)}let n=document.createElement('div');n.textContent=c.relative_path;e.append(n);let rs=document.createElement('div');rs.className=c.authoritative_shortlist?'ok':'warn';rs.textContent=c.authoritative_shortlist?'Authoritative shortlist: qualified':'0.07 review shortlist qualification: '+(c.review_can_shortlist?'qualified; apply shortlist state':'not yet qualified');e.append(rs);if(c.legacy_submission_ready){let w=document.createElement('div');w.className='warn';w.textContent='Legacy submission-ready — not authoritative.';e.append(w)}let s=document.createElement('select');for(let x of S)s.add(new Option(x,x,x==c.state,x==c.state));if(c.legacy_submission_ready)s.value='metadata-ready';s.onchange=async()=>{try{await q('/api/candidates/state',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({relative_path:c.relative_path,state:s.value})});load()}catch(err){alert(err.message);load()}};e.append(s);for(let pair of [['Human review','/review?relative_path='],['Preparation / preflight','/preparation?relative_path=']]){let a=document.createElement('a');a.href=pair[1]+encodeURIComponent(c.relative_path);a.textContent=pair[0];a.style.display='block';e.append(a)}if(!c.preview_available){let b=document.createElement('button');b.textContent='Create local preview';b.onclick=async()=>{if(confirm('Read this selected image to create a local preview copy? The original will not be modified.')){await q('/api/candidates/preview',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({relative_path:c.relative_path,consent:true})});load()}};e.append(b)}g.append(e)}}load()</script>"""
PREPARATION_PAGE="""<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Stock Photo Scout Preparation</title><style>body{font:16px system-ui;max-width:900px;margin:20px auto;padding:0 14px;background:#f5f6f8}label{display:block;margin:10px 0}input,textarea,select{width:100%;box-sizing:border-box;padding:8px}button,a{padding:9px;margin:8px 8px 8px 0}pre{white-space:pre-wrap;background:white;padding:12px;border-radius:8px}</style><a href='/'>Back to candidates</a><h1>Local preparation / preflight</h1><p>This page prepares a local packet only. It does not upload, submit, publish, or contact a marketplace.</p><label>Candidate<input id=rel readonly></label><label>Title<input id=title></label><label>Description<textarea id=description></textarea></label><label>Keywords (comma-separated)<input id=keywords></label><label>Categories (comma-separated)<input id=categories></label><label>Dreamstime category pairs (Category::Subcategory, comma-separated; max 3)<input id=category_pairs></label><label>Route<select id=route><option>undecided</option><option>commercial</option><option>editorial</option></select></label><label>Editor target<select id=editor_target><option>none</option><option>darktable</option><option>rawtherapee</option><option>gimp</option><option>other</option></select></label><label>Working export relative path<input id=working_export_relative_path></label><label>Notes<textarea id=notes></textarea></label><button id=save>Save local preparation</button><h2>Prompts</h2><pre id=prompts></pre><h2>Manual preflight</h2><label>Preview integrity<select id=integrity><option value=unknown>Not checked</option><option value=match>Confirmed match</option><option value=mismatch>Mismatch</option></select></label><label><input type=checkbox id=req> Current marketplace requirements reviewed</label><button id=preflight>Build local preflight</button><pre id=packet></pre><script>async function q(u,o){let r=await fetch(u,o),x=await r.json();if(!r.ok)throw Error(x.error);return x}let R=new URLSearchParams(location.search).get('relative_path')||'';rel.value=R;async function load(){let x=await q('/api/preparation/load',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({relative_path:R})}),p=x.preparation;for(let k of ['title','description','route','editor_target','working_export_relative_path','notes'])document.getElementById(k).value=p[k];keywords.value=p.keywords.join(', ');categories.value=p.categories.join(', ');category_pairs.value=p.category_pairs.map(x=>x.category+(x.subcategory?'::'+x.subcategory:'')).join(', ');prompts.textContent=x.prompts.map(x=>x.code+': '+x.explanation).join('\n')}save.onclick=async()=>{let pairs=category_pairs.value.split(',').map(x=>x.trim()).filter(Boolean).map(x=>{let p=x.split('::');return {category:p[0].trim(),subcategory:(p[1]||'').trim()}});await q('/api/preparation/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({relative_path:R,title:title.value,description:description.value,keywords:keywords.value.split(',').map(x=>x.trim()).filter(Boolean),categories:categories.value.split(',').map(x=>x.trim()).filter(Boolean),category_pairs:pairs,route:route.value,editor_target:editor_target.value,working_export_relative_path:working_export_relative_path.value,notes:notes.value})});load()};preflight.onclick=async()=>{let x=await q('/api/preflight',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({relative_path:R,preview_integrity:integrity.value,current_requirements_reviewed:req.checked})});packet.textContent=x.text};load()</script>"""