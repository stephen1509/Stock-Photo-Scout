# Dashboard security/concurrency audit — 0.06

Date: 2026-10-21

## Good existing controls
- HTTP server binds to `127.0.0.1`, not all interfaces.
- Mutations use POST endpoints; GET is read-only.
- Request bodies are bounded to 100 KB JSON.
- Responses use `Cache-Control: no-store` and `X-Content-Type-Options: nosniff`.
- Originals are not directly served; preview route resolves inside preview root.
- Preparation and analysis directories are required outside source root.

## High-priority findings

### D1 — Candidate gallery uses `innerHTML` with filename/path data
`c.relative_path` and `c.preview_url` are interpolated into HTML. A hostile/unusual filename containing markup/quotes could become DOM injection in the localhost UI. Replace dynamic `innerHTML` construction with `textContent`, DOM element properties and validated preview URLs.

### D2 — Preview lexical validation is host-dependent
`preview_path()` uses native `Path` only before resolution. On a non-Windows host, Windows drive/UNC lexical forms may not be rejected consistently. Reuse native + `PureWindowsPath` validation.

### D3 — Concurrent state writes can lose updates
`ThreadingHTTPServer` allows concurrent POST requests while workspace/preparation persistence is read-modify-write without an application lock/version check. Two browser actions can race and last writer can silently overwrite the other. Add a process-local lock or optimistic version/lease around mutable JSON operations.

### D4 — New 0.06 readiness contracts are not yet enforced by UI
The dashboard still exposes legacy `submission-ready` state directly. Until consolidated readiness integration is complete, a human can set the legacy state without satisfying new rights/provenance/final-QC gates. UI must either disable that direct transition or clearly treat it as legacy/non-authoritative.

## Medium findings
- `_find_preparation_path` / `_find_analysis` scan every JSON file and silently skip malformed records. This is safe-ish but can hide damaged private state; surface a diagnostic count/log rather than silently losing evidence.
- Preview GET reads entire preview bytes into memory. Acceptable for bounded local previews, but later add a size ceiling/streaming if previews can be large TIFFs.
- No CSRF token. Because server is loopback-only and JSON POSTs are used, risk is reduced but not zero in a hostile-browser scenario. Consider Origin/Host checks before richer mutations.
- No explicit CSP. After removing dynamic HTML injection, a restrictive local CSP would be useful defense in depth.

## Required before 0.06 UI qualification
1. Remove filename/path `innerHTML` interpolation.
2. Harden preview path lexical validation.
3. Serialize/lease mutable dashboard state writes.
4. Prevent legacy `submission-ready` from being interpreted as authoritative readiness.
5. Add focused dashboard tests for hostile filenames, traversal/Windows paths and concurrent-state protection.
