"""A local-only browser dashboard for reviewing local draft JSON files."""

from __future__ import annotations

from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from .drafts import CandidateDraft, RightsObservations, draft_from_json, edit_draft, evaluate_readiness, update_draft_json
from .spelling_dictionary import (
    AcceptedSpellings,
    save_spelling_dictionary,
    spelling_dictionary_from_json,
    update_spelling_dictionary,
)


@dataclass(frozen=True)
class DashboardSettings:
    """Validated local-only paths used by the dashboard."""

    source_root: Path
    drafts_directory: Path
    dictionary_path: Path

    @classmethod
    def create(cls, source_root: str | Path, drafts_directory: str | Path, dictionary_path: str | Path) -> "DashboardSettings":
        resolved_source = Path(source_root).expanduser().resolve(strict=True)
        resolved_drafts = Path(drafts_directory).expanduser().resolve(strict=False)
        resolved_dictionary = Path(dictionary_path).expanduser().resolve(strict=False)
        if resolved_drafts.is_relative_to(resolved_source):
            raise ValueError("Refusing a local-drafts directory inside the selected source-photo folder.")
        if resolved_dictionary.parent != resolved_drafts:
            raise ValueError("The spelling dictionary must be stored in the selected local-drafts directory.")
        return cls(resolved_source, resolved_drafts, resolved_dictionary)


class LocalDashboard:
    """Strict local data access for the browser interface; it never reads a photo."""

    def __init__(self, settings: DashboardSettings) -> None:
        self.settings = settings

    def list_drafts(self) -> list[str]:
        if not self.settings.drafts_directory.exists():
            return []
        return sorted(
            path.name
            for path in self.settings.drafts_directory.iterdir()
            if path.is_file() and not path.is_symlink() and path.suffix.lower() == ".json" and path != self.settings.dictionary_path
        )

    def load_draft(self, filename: str) -> dict[str, Any]:
        path = self._draft_path(filename)
        draft = draft_from_json(path.read_text(encoding="utf-8"))
        dictionary = self._load_dictionary()
        report = evaluate_readiness(draft, dictionary.apply_to())
        return {
            "filename": path.name,
            "draft": _draft_payload(draft),
            "prompts": [{"code": prompt.code, "severity": prompt.severity, "explanation": prompt.explanation} for prompt in report.prompts],
        }

    def update_draft(self, filename: str, payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ValueError("Draft update must be a JSON object.")
        path = self._draft_path(filename)
        existing = draft_from_json(path.read_text(encoding="utf-8"))
        updated = edit_draft(
            existing,
            title=_text_value(payload, "title"),
            keywords=_keyword_values(payload),
            notes=_text_value(payload, "notes"),
            rights=_rights_value(payload, existing.rights),
        )
        update_draft_json(updated, path, self.settings.source_root)
        return self.load_draft(filename)

    def accept_spelling(self, payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict) or not isinstance(payload.get("term"), str) or not payload["term"].strip():
            raise ValueError("A non-empty spelling term is required.")
        dictionary = self._load_dictionary().add(payload["term"].strip())
        if self.settings.dictionary_path.exists():
            update_spelling_dictionary(dictionary, self.settings.dictionary_path)
        else:
            save_spelling_dictionary(dictionary, self.settings.dictionary_path)
        return {"term": payload["term"].strip()}

    def _load_dictionary(self) -> AcceptedSpellings:
        if not self.settings.dictionary_path.exists():
            return AcceptedSpellings()
        return spelling_dictionary_from_json(self.settings.dictionary_path.read_text(encoding="utf-8"))

    def _draft_path(self, filename: str) -> Path:
        candidate = Path(filename)
        if candidate.name != filename or candidate.suffix.lower() != ".json":
            raise ValueError("Draft filename must name one local JSON draft.")
        path = (self.settings.drafts_directory / candidate).resolve(strict=True)
        if path.parent != self.settings.drafts_directory or path.is_symlink() or not path.is_file():
            raise FileNotFoundError("Local draft not found.")
        return path


def serve_dashboard(settings: DashboardSettings, port: int = 8765) -> None:
    """Serve the dashboard on localhost only until interrupted by the user."""

    dashboard = LocalDashboard(settings)
    handler = _handler_for(dashboard)
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    print(f"Open http://127.0.0.1:{server.server_port} in your browser. Press Ctrl+C here to stop it.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Local dashboard stopped.")
    finally:
        server.server_close()


def _handler_for(dashboard: LocalDashboard) -> type[BaseHTTPRequestHandler]:
    class DashboardHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            try:
                if path == "/":
                    self._send(HTTPStatus.OK, _PAGE, "text/html; charset=utf-8")
                elif path == "/api/drafts":
                    self._send_json(HTTPStatus.OK, {"drafts": dashboard.list_drafts()})
                elif path.startswith("/api/drafts/"):
                    self._send_json(HTTPStatus.OK, dashboard.load_draft(unquote(path.removeprefix("/api/drafts/"))))
                else:
                    self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})
            except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})

        def do_POST(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            try:
                payload = self._read_json()
                if path == "/api/accepted-spellings":
                    self._send_json(HTTPStatus.OK, dashboard.accept_spelling(payload))
                elif path.startswith("/api/drafts/"):
                    self._send_json(
                        HTTPStatus.OK,
                        dashboard.update_draft(unquote(path.removeprefix("/api/drafts/")), payload),
                    )
                else:
                    self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})
            except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
                self._send_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})

        def _read_json(self) -> Any:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 100_000:
                raise ValueError("Request body must be a small JSON object.")
            return json.loads(self.rfile.read(size).decode("utf-8"))

        def _send_json(self, status: HTTPStatus, value: Any) -> None:
            self._send(status, json.dumps(value, ensure_ascii=False), "application/json; charset=utf-8")

        def _send(self, status: HTTPStatus, content: str, content_type: str) -> None:
            encoded = content.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, _format: str, *_args: object) -> None:
            return

    return DashboardHandler


def _draft_payload(draft: CandidateDraft) -> dict[str, Any]:
    return {
        "relative_path": draft.relative_path,
        "title": draft.title,
        "keywords": list(draft.keywords),
        "notes": draft.notes,
        "rights": {
            "recognizable_people": draft.rights.recognizable_people,
            "private_property_or_restricted_location": draft.rights.private_property_or_restricted_location,
            "visible_logos_or_trademarks": draft.rights.visible_logos_or_trademarks,
            "third_party_copyrighted_content": draft.rights.third_party_copyrighted_content,
            "release_evidence": draft.rights.release_evidence,
        },
    }


def _text_value(payload: dict[str, Any], field: str) -> str | None:
    value = payload.get(field)
    if value is not None and not isinstance(value, str):
        raise ValueError(f"{field} must be text.")
    return value


def _keyword_values(payload: dict[str, Any]) -> tuple[str, ...] | None:
    values = payload.get("keywords")
    if values is None:
        return None
    if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
        raise ValueError("keywords must be a list of text values.")
    return tuple(values)


def _rights_value(payload: dict[str, Any], previous: RightsObservations) -> RightsObservations:
    values = payload.get("rights")
    if values is None:
        return previous
    if not isinstance(values, dict):
        raise ValueError("rights must be an object.")
    return RightsObservations(
        recognizable_people=values.get("recognizable_people", previous.recognizable_people),
        private_property_or_restricted_location=values.get(
            "private_property_or_restricted_location", previous.private_property_or_restricted_location
        ),
        visible_logos_or_trademarks=values.get("visible_logos_or_trademarks", previous.visible_logos_or_trademarks),
        third_party_copyrighted_content=values.get(
            "third_party_copyrighted_content", previous.third_party_copyrighted_content
        ),
        release_evidence=values.get("release_evidence", previous.release_evidence),
    )


_PAGE = r'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Stock Photo Scout</title><style>
:root{color-scheme:light;font-family:system-ui,sans-serif;color:#172023;background:#f4f5f7}body{margin:0}.top{padding:22px 30px;background:#172b4d;color:#fff}.top h1{margin:0;font-size:25px}.top p{margin:5px 0 0;color:#dce6f2}.app{display:grid;grid-template-columns:250px 1fr;min-height:calc(100vh - 93px)}aside{padding:20px;background:#fff;border-right:1px solid #d9dee7}aside h2{font-size:13px;text-transform:uppercase;letter-spacing:.08em;color:#5d6b82}.draft{width:100%;text-align:left;border:0;background:none;padding:10px;border-radius:6px;cursor:pointer}.draft:hover,.draft.active{background:#e6f0ff;color:#0756a8}main{max-width:1000px;width:calc(100% - 48px);padding:28px 24px}.card{background:#fff;border:1px solid #d9dee7;border-radius:10px;padding:20px;margin-bottom:18px;box-shadow:0 1px 2px #00000008}.row{display:grid;grid-template-columns:repeat(auto-fit,minmax(205px,1fr));gap:15px}label{display:block;font-weight:650;font-size:14px;margin:0 0 12px}input,textarea,select{box-sizing:border-box;width:100%;margin-top:6px;padding:9px;border:1px solid #aeb8c8;border-radius:6px;font:inherit}textarea{min-height:90px}button{background:#0756a8;color:#fff;border:0;border-radius:6px;padding:10px 14px;font-weight:650;cursor:pointer}button.secondary{background:#e6edf7;color:#172b4d}.prompt{padding:11px;border-left:4px solid #4b83c3;background:#f5f9ff;margin:8px 0}.prompt.attention{border-color:#b85c00;background:#fff6e9}.muted{color:#5d6b82}.empty{padding:45px;text-align:center;color:#5d6b82}@media(max-width:700px){.app{grid-template-columns:1fr}aside{border-right:0;border-bottom:1px solid #d9dee7}main{width:auto}}
</style><body><header class="top"><h1>Stock Photo Scout</h1><p>Local draft review — your original photos are not opened or changed.</p></header><div class="app"><aside><h2>Local drafts</h2><div id="drafts"></div></aside><main id="content"><div class="empty">Loading local drafts…</div></main></div><script>
const $=s=>document.querySelector(s),content=$('#content'),drafts=$('#drafts');let current='';
function esc(v){const e=document.createElement('div');e.textContent=v??'';return e.innerHTML}function select(v,opts){return opts.map(x=>`<option ${x===v?'selected':''}>${x}</option>`).join('')}
async function request(url,options){const r=await fetch(url,options);const x=await r.json();if(!r.ok)throw Error(x.error||'Request failed');return x}
async function list(){const data=await request('/api/drafts');if(!data.drafts.length){content.innerHTML='<div class="empty">No local drafts yet. Create one with the project command, then refresh this page.</div>';return}drafts.innerHTML=data.drafts.map(n=>`<button class="draft ${n===current?'active':''}" data-name="${esc(n)}">${esc(n)}</button>`).join('');[...document.querySelectorAll('.draft')].forEach(b=>b.onclick=()=>load(b.dataset.name));if(!current)load(data.drafts[0])}
async function load(name){current=name;const data=await request('/api/drafts/'+encodeURIComponent(name));render(data);listButtons()}
function listButtons(){[...document.querySelectorAll('.draft')].forEach(b=>b.classList.toggle('active',b.dataset.name===current))}
function render(data){const d=data.draft,r=d.rights,manual=['unknown','yes','no','not_applicable'],evidence=['not_reviewed','available','not_available','not_applicable'];content.innerHTML=`<div class="card"><p class="muted">Candidate</p><h2>${esc(d.relative_path)}</h2><p class="muted">Saved locally as ${esc(data.filename)}. This page does not display or open the image.</p></div><form id="form"><div class="card"><div class="row"><label>Title<input name="title" value="${esc(d.title)}"></label><label>Keywords <span class="muted">(one per line)</span><textarea name="keywords">${esc(d.keywords.join('\n'))}</textarea></label></div><label>Notes<textarea name="notes">${esc(d.notes)}</textarea></label></div><div class="card"><h2>Manual observations</h2><div class="row"><label>Recognizable people<select name="recognizable_people">${select(r.recognizable_people,manual)}</select></label><label>Private property / restricted location<select name="private_property_or_restricted_location">${select(r.private_property_or_restricted_location,manual)}</select></label><label>Logos / trademarks<select name="visible_logos_or_trademarks">${select(r.visible_logos_or_trademarks,manual)}</select></label><label>Third-party content<select name="third_party_copyrighted_content">${select(r.third_party_copyrighted_content,manual)}</select></label><label>Release evidence<select name="release_evidence">${select(r.release_evidence,evidence)}</select></label></div><button>Save local draft</button> <span id="status" class="muted"></span></div></form><div class="card"><h2>Review prompts</h2><div id="prompts">${data.prompts.length?data.prompts.map(p=>`<div class="prompt ${p.severity}"><strong>${esc(p.code)}</strong><br>${esc(p.explanation)}${p.code==='possible_spelling'?`<br><button class="secondary accept" data-term="${esc((p.explanation.match(/'([^']+)'/)||[])[1]||'')}">Confirm this spelling</button>`:''}</div>`).join(''):'<p class="muted">No prompts.</p>'}</div></div>`;$('#form').onsubmit=save;[...document.querySelectorAll('.accept')].forEach(b=>b.onclick=accept)}
async function save(e){e.preventDefault();const f=new FormData(e.target),rights={};for(const key of ['recognizable_people','private_property_or_restricted_location','visible_logos_or_trademarks','third_party_copyrighted_content','release_evidence'])rights[key]=f.get(key);const body={title:f.get('title'),keywords:f.get('keywords').split('\n').map(x=>x.trim()).filter(Boolean),notes:f.get('notes'),rights};$('#status').textContent='Saving…';try{await request('/api/drafts/'+encodeURIComponent(current),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});$('#status').textContent='Saved locally.';await load(current)}catch(err){$('#status').textContent=err.message}}
async function accept(e){const term=e.currentTarget.dataset.term;if(!term)return;await request('/api/accepted-spellings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({term})});await load(current)}list().catch(e=>content.innerHTML='<div class="empty">'+esc(e.message)+'</div>');
</script></body></html>'''
