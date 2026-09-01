# Next ChatGPT Action — Research, Plan, Then Build

## User-directed objective

In the next ChatGPT session, thoroughly and carefully research the current Dreamstime contributor system and the practical tool ecosystem for a Windows photographer. Use the findings to make a concrete product plan for Stock Photo Scout, then begin implementation only after the user has reviewed and authorized that plan.

The intended product is a local-first assistant that helps a photographer select images, prepare titles and keywords, identify possible improvements, coordinate with editors, and prepare for Dreamstime submission. It should assist the photographer; it must not silently alter originals, make legal determinations, or submit anything without approval.

## Start here

Read these files first, in order:

1. `PROJECT_AUTHORITY_CURRENT.md`
2. `CURRENT_STATUS.md`
3. This file
4. `DREAMSTIME_RULES.md`, `PRODUCT_REQUIREMENTS.md`, `ARCHITECTURE.md`, and `ROADMAP.md`

Current working state:

- Dropbox is the working source of truth: `/Projects/Stock Photo Scout`.
- GitHub is checkpoint-only: `https://github.com/stephen1509/Stock-Photo-Scout`.
- The current local dashboard runs at `http://127.0.0.1:8765/` when started from the project folder. It manages only local draft JSON and does not open source photos.
- Local catalogs, local drafts, confirmed spellings, images, and previews are Git-ignored. Do not upload or commit them.

## Research required

Use current, authoritative sources wherever possible. Record direct links, the access date, and the practical meaning of each finding. Do not rely on remembered marketplace rules.

### 1. Dreamstime contributor workflow

Research and distinguish confirmed facts from inference:

- Contributor onboarding, current upload routes, and any official APIs, metadata/import tools, or browser tools available to contributors.
- Technical file requirements, image-type distinctions, review/rejection criteria, and any current policies relevant to commercial versus editorial material.
- Title, description, keyword, category, model/property release, trademark, and recognizable-person workflows.
- Whether any automated keywording, enhancement, upload, or batch tools are officially available or permitted.
- Current terms or restrictions relevant to third-party automation and assisted submission.

Prefer Dreamstime’s own contributor documentation, terms, support pages, and contributor portal documentation. If a portal requires login, do not sign in or change any account state unless separately asked.

### 2. Tool ecosystem for the photographer

Research realistic Windows-compatible options, with free/open-source and reasonably priced choices clearly separated:

- Local and cloud-assisted image classification, caption/title generation, keyword generation, and metadata tools.
- Technical/visual review tools for crop suggestions, colour balance, white balance, exposure, horizon, sharpness, noise, dust spots, and composition.
- Non-destructive image editors and their automation/integration options, including GIMP and likely alternatives such as darktable or RawTherapee. Confirm the user’s other editor rather than assuming it.
- Digital asset management, tagging, metadata sidecar, and batch-preparation tools.
- Submission/upload-assistance tools that are compatible with Dreamstime’s current rules.

For each promising option, capture: purpose, Windows support, local/cloud data path, price/licensing, privacy implications, integration method, reliability/maturity, and any relevant Dreamstime-policy risk.

## Required deliverables before implementation

Create a research brief in the Dropbox project that includes:

1. Source-backed Dreamstime workflow summary.
2. Comparison table of candidate tools.
3. A recommended stack with alternatives and costs.
4. A privacy/data-flow diagram or concise equivalent: which steps stay local, which would send a selected image or metadata to a service, and what explicit consent each requires.
5. A phased build plan for Stock Photo Scout:
   - local candidate workspace and read-only preview;
   - local technical/visual recommendations;
   - optional title/keyword suggestion capability;
   - editor handoff and non-destructive improvement workflow;
   - Dreamstime preflight and submission preparation;
   - any later authorized upload integration.
6. A short list of decisions that require the user’s approval before implementation.

Present the recommendation to the user before installing software, creating accounts, using paid APIs, uploading any photo, connecting Dreamstime, using account credentials, editing photos, or automating submissions.

## Safety and consent gates

- Original photographs are immutable: never rename, move, edit, upload, delete, or overwrite them.
- Do not scan personal photo folders beyond a user-named folder or photo without permission.
- Treat automated titles, keywords, classifications, quality scores, edit recommendations, and rights signals as suggestions for human review—not facts or legal advice.
- Image analysis reads pixels; get permission before analyzing images beyond the explicitly selected set.
- Cloud/AI analysis, paid tools, browser account access, installations, marketplace actions, and uploads each need separate, explicit approval at the relevant time.
- If actual edits are eventually supported, use separate working copies or reversible editor sidecars; never apply them to originals.
- Do not make a GitHub checkpoint containing private drafts, catalogs, previews, originals, credentials, or private research exports unless they are explicitly reviewed and safe to commit.

## Definition of success for the research session

The user can see a well-sourced, cost-aware plan that answers: what Dreamstime allows today; which tools are worth using; what stays private/local; what must be approved; and exactly what Stock Photo Scout should build first.
