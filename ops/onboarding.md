# Op: Onboarding

Build the user's deep profile from a batch of uploaded markdown/files.

## When this runs

- The user uploads a bundle of `.md`, `.txt`, `.pdf`, or other supporting files.
- The user says they want the files scanned and folded into the Job Search OS KB.
- The user wants the raw artifacts preserved for future reference.

## Procedure

### 1. File the raw inputs

Save every uploaded file verbatim under `sources/user-docs/onboarding/` using dated, descriptive filenames:

- `YYYY-MM-DD-{short-slug}.md`
- `YYYY-MM-DD-{short-slug}.pdf`
- `YYYY-MM-DD-{short-slug}.txt`

If the upload is a batch, also create a small manifest in the same folder that lists:

- original filename
- received date
- source type
- brief purpose
- whether the file was already seen before

Never edit or rewrite the raw files after filing.

### 2. Read the batch as a whole

Scan all uploaded material for stable facts that help build a deep applicant profile:

- career history
- accomplishments and proof points
- role preferences and exclusions
- company preferences
- story bank material
- outreach context
- resume-ready metrics
- interview anecdotes
- constraints or special instructions

Prefer to synthesize across files instead of treating each file in isolation.

### 3. Update the KB

Fold the batch into the relevant wiki pages. Typical targets:

- `wiki/profile/me.md`
- `wiki/profile/positioning.md`
- `wiki/evidence/*`
- `wiki/companies/*`
- `wiki/roles/*`
- `wiki/outreach/*`
- `wiki/jobs/*` if a file contains a specific role or posting

Rules:

- Use only verified facts.
- Preserve contradictions explicitly instead of overwriting them.
- Add cross-links when a new page is created or updated.
- Keep the applicant story useful for resume generation, fit search, and outreach.

### 4. Report back

Return a concise summary with:

- files filed to `sources/user-docs/onboarding/`
- wiki pages created/updated
- contradictions or missing facts
- recommended next action (usually `query`, `lint`, or `apply`)

## Output style

Keep the result compact and actionable. The goal is to turn uploads into a cleaner profile, not to paraphrase everything back to the user.
