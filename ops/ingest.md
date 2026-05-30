# Op: Ingest

Add a new source to the knowledge base. Update every wiki page the source touches.

## When this runs

- The human pastes a URL, job posting, blog post, or document in chat.
- The human drops a file into `sources/`.
- The human says "log this" / "add this" / "remember this."

## Procedure

### 1. File the source

Save the source verbatim into the matching `sources/<folder>/` subdir.

| Source kind                              | Folder                |
|------------------------------------------|-----------------------|
| Job description                          | `sources/job-posts/`  |
| Company news, blog, leadership post      | `sources/company-news/` |
| Human's own artifact (review, doc, etc.) | `sources/user-docs/`  |
| Interview recording, transcript, email   | `sources/interviews/` |
| Sent or received message                 | `sources/outreach/`   |

Filename: `YYYY-MM-DD-{slug}.{md|txt|pdf}`. Use today's date.

Never edit or rename a source after filing.

### 2. Identify affected wiki pages

Read the source carefully. List every wiki page it touches:

- Mentions a target company? → `wiki/companies/{slug}.md`
- A specific job? → `wiki/jobs/{date}-{co}-{slug}.md`
- A new contact? → `wiki/outreach/{slug}.md`
- An interview round? → `wiki/interviews/{date}-{co}-{round}.md`
- A new accomplishment or story? → `wiki/evidence/{slug}.md`
- Affects positioning? → `wiki/profile/positioning.md`

Some sources touch multiple pages. Plan all updates before writing.

### 3. Update each page

For each affected page:

- If it doesn't exist, create it from `templates/<type>.md`.
- Update the relevant section. Append, don't overwrite, unless the source explicitly supersedes an old fact.
- Add a citation: `→ sources/<folder>/<filename>` at the end of the changed paragraph or in a `## Sources` section.
- Add cross-links per [SCHEMA § 3](../SCHEMA.md#3-cross-linking-rules).

### 4. Flag contradictions

If a new fact conflicts with an existing fact on a page, do **not** silently overwrite. Insert:

```
**CONTRADICTION (YYYY-MM-DD):** Source X says Y; previously had Z (from source W). Human to resolve.
```

Leave both values until the human picks one.

### 5. Report back

In one paragraph, tell the human:

- Source filed: `<path>`
- Pages updated: `<list>`
- Pages created: `<list>`
- Contradictions flagged: `<count>`
- Recommended next action: ingest is rarely the end — what should happen next? (apply, outreach, query, nothing)

## Example

User pastes: "ExampleCo is hiring a Product Manager, Growth, US Remote."

1. Save → `sources/job-posts/2026-05-30-exampleco-pm-growth.md`
2. Affected pages:
   - `wiki/companies/exampleco.md` (update live-roles section)
   - `wiki/jobs/2026-05-30-exampleco-pm-growth.md` (new)
3. Update both, add citations, link the job page → company page.
4. No contradictions.
5. Report: "Filed ExampleCo PM Growth. Job page created, company page updated with new live role. Recommend running `apply` if you want to draft a resume — your positioning aligns with growth/onboarding/experimentation."
