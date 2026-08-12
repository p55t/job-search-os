# Op: Apply

The end-to-end "I want to apply to this role" flow. Composes ingest, query, and resume generation.

## When this runs

- The human says "apply to X" / "draft a resume for Y" / "this role looks good, let's go."

## Procedure

Before starting, read `SCHEMA.md` and `wiki/ops/source-of-truth.md`. Application state lives in `data/jobsearch.db`; update it before changing the queue page.

### 1. Make sure the job is ingested

If the job page doesn't exist yet, run [ingest](ingest.md) first. By the end of step 1 you must have:

- `wiki/jobs/{date}-{co}-{slug}.md` (the job page)
- `wiki/companies/{co}.md` (the company page, possibly newly created or updated)

Check `data/jobsearch.db` for the company and role before continuing. If the company is within the 90-day applied-company cooldown, stop and ask the human to explicitly reopen it before drafting or recommending another application.

### 2. Score the role

Open `wiki/profile/me.md`, `wiki/profile/positioning.md`, and any exclusion rules (e.g. `wiki/profile/me.md` § Exclusions).

Score the job on three axes:

| Axis           | Question                                                          | 1–5 |
|----------------|-------------------------------------------------------------------|-----|
| Profile fit    | Does this match the human's seniority, geography, role family?    |     |
| Story fit      | Are there 3+ strong stories in `wiki/evidence/` that map to it?   |     |
| Strategic fit  | Does it move the search forward? (priority co, dream lane, etc.)  |     |

If any axis ≤ 2, surface the gap before drafting. Ask the human to confirm before continuing.

### 3. Pick evidence

From `wiki/evidence/`, select 4–6 stories that:

- Have direct overlap with the role's responsibilities.
- Together demonstrate the seniority required.
- Include verifiable metrics.

List the chosen evidence pages in the resume page metadata. No story used in the resume that isn't in `wiki/evidence/`.

### 4. Draft the resume

Create `wiki/resumes/{date}-{co}-{slug}.md` from `templates/resume.md`. Follow:

- `prompts/resume-rules.md` — the hard rules (verified facts only, etc.)
- `prompts/human-voice-spec.md` — the voice
- `prompts/writing-steering-spec.md` — the ATS and anti-slop spec

The resume must trace every claim back to an evidence page or source. **No invented numbers.**

### 5. Cross-link

Update the job page (`wiki/jobs/{slug}.md`) to link the resume. Update the resume to link every evidence page it draws from.

### 6. Outreach check

Before reporting back, scan `wiki/outreach/` for any contact at this company. If one exists and last_touch is stale, suggest re-warming as part of the application path.

### 7. Report

Before reporting, upsert the application row using its non-null `wiki_page` as the identity: `INSERT ... ON CONFLICT(wiki_page) WHERE wiki_page IS NOT NULL DO UPDATE ...`. Record the current status (`new`, `scored`, or `applied` as appropriate), URL, and next action date if known. Then reconcile `wiki/queue/target-queue.md` from that state and rebuild the wiki index.

Return:

- Score summary (3 axes)
- Resume path (`wiki/resumes/{date}-{co}-{slug}.md`)
- Evidence pages used
- Outreach suggestion (if applicable)
- A draft cold-app message if the role allows a cover letter / message field

The human reviews. The human submits. The OS never submits an application on its own.
