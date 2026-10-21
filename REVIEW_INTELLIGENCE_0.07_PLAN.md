# 0.07 Review Intelligence — Implementation Contract

Date: 2026-10-21

## Goal
Help a human review a large personal photo collection faster and more consistently without pretending automated measurements can decide stock acceptance.

## Core principle
Separate **observed facts**, **machine-generated review prompts**, and **human decisions**. Never collapse them into a hidden suitability/acceptance score.

## Stage 1 — Fast screening
Purpose: cheaply reduce review volume.

Inputs may include metadata and bounded/derived local observations when explicitly consented.

Outputs:
- duplicate/similar-group context;
- obvious technical-review prompts;
- likely need for editing/inspection;
- human screening decision: skip / hold / inspect;
- human reason codes and notes.

Stage 1 MUST NOT mark a candidate submission-ready.

## Stage 2 — Shortlist inspection
Purpose: deliberate inspection of images a human chose to inspect.

Required dimensions:
- exact-pixel inspection plan;
- subject/focus target selected or confirmed by human;
- focus/motion-blur observations;
- noise/compression/banding/halo/oversharpening/denoising/chromatic-aberration/dust/pixelation observations;
- exposure/color observations;
- composition/usefulness review;
- rights/route handoff;
- exact export provenance and final-QC handoff when preparation begins.

## Review dimensions
Keep independent fields rather than one linear score:
- review decision;
- technical state;
- stock potential;
- rights state;
- final route;
- preparation state;
- edit-needed;
- duplicate/similar group;
- subject/focus review;
- composition/usefulness review.

## Human reason codes
Initial controlled vocabulary:
- duplicate-or-near-duplicate
- weak-subject
- weak-composition
- distracting-background
- insufficient-copy-space
- focus-concern
- motion-blur-concern
- noise-or-artifact-concern
- exposure-or-color-concern
- rights-or-ip-concern
- commercially-limited
- editorial-interest
- stronger-similar-image-exists
- promising-subject
- strong-composition
- useful-copy-space
- technically-clean-looking
- needs-edit
- other

Free-text notes remain available. Reason codes describe a human review; they are not marketplace rejection predictions.

## Similar/burst grouping
0.07 should first support deterministic grouping facts, not opaque visual embeddings. Candidate sources:
- exact duplicate hash where already available;
- capture-time proximity when metadata exists;
- filename sequence proximity as an explicitly weak hint;
- optional future local perceptual comparison only after privacy/resource review.

Groups must never delete or automatically reject photographs. A human chooses the preferred member(s).

## Subject-aware focus
Global sharpness proxies are insufficient because texture, depth of field, motion intent and noise can confound them.

0.07 contract:
- human may identify the intended subject/focus region;
- the system may generate inspection crops/prompts around that region;
- absence of a subject selection is `unknown`, not failure;
- focus observations are advisory;
- final technical pass remains human-controlled at actual pixels.

## Composition / stock usefulness
Use structured prompts rather than scores:
- Is the intended subject clear?
- Is there distracting clutter?
- Is useful negative/copy space available?
- Are there alternate crops/orientations worth preparing?
- Is the image redundant with a stronger similar image?
- Is its likely value commercial, editorial, both-possible during review, or unclear?

These prompts cannot establish marketplace eligibility.

## Calibration
The existing 16-image labelled set is an initial descriptive check only. Before measurements influence prioritisation materially, build a deliberately varied human-labelled set (target roughly 100–200 images over time) spanning:
- low/high detail;
- intentional shallow depth of field;
- low light;
- motion;
- architecture;
- landscapes;
- people/no people;
- clean/noisy backgrounds;
- edited/unedited examples;
- good, needs-editing and unsuitable human labels.

Do not train or deploy a model merely because this set exists.

## Persistence and privacy
- local deterministic JSON outside source folders;
- strict schema/version validation;
- safe relative paths only;
- no absolute source paths in portable review records where avoidable;
- no image bytes in Git;
- source files read-only;
- byte/pixel reads require explicit consent.

## Qualification
0.07 implementation can proceed while 0.06 awaits executable qualification, but it inherits the same qualification boundary. No new test-pass count may be claimed until a full local suite actually runs.
