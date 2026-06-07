# SCHEMA — The Operating Manual

> If you are an LLM agent operating this system, **read this file first** every session. It tells you how the wiki is organized, what each page type is for, and how to keep the system coherent over time.

This file plays the role of `CLAUDE.md` in [Karpathy's LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — it is the operational schema the AI follows.

---

## 1. The three layers

| Layer    | Path           | Who edits it | Mutability |
|----------|----------------|--------------|------------|
| Sources  | `sources/`     | The human    | Immutable once filed |
| Wiki     | `wiki/`        | The AI       | Continuously maintained |
| Schema   | repo root      | The human    | Stable; changes are deliberate |


**You (the AI) own the wiki.** You never modify a source file. You always update the wiki when a new source comes in.

---

## 1b. Taxonomy and file roles

- `prompts/` — reusable instructions for capture, review, and experiment runs.
- `wiki/ops/` — operational contracts, reusable workflow notes, and the change log.
- `wiki/strategies/` — durable playbooks and current-best-practice guidance.
- `wiki/comparisons/` — side-by-side decision guides that choose between approaches.
- `skills/` — if a workflow graduates into a reusable Hermes skill, keep the executable skill in Hermes and mirror the human-readable recipe here.

Rule of thumb: prompts steer one run, wiki pages preserve durable knowledge, and skills are executable recipes you can reuse across sessions.

---

## 2. Page types

Every page in `wiki/` belongs to exactly one of these types. The template lives in `templates/<type>.md`.

| Type       | Path                          | Cardinality | What it is |
|------------|-------------------------------|-------------|------------|
| profile    | `wiki/profile/me.md`          | exactly 1   | The single source of truth about the human |
| positioning| `wiki/profile/positioning.md` | exactly 1   | How to pitch this person to the market |
| company    | `wiki/companies/{slug}.md`    | 1 per target company | Why this company; role families; fit |
| role       | `wiki/roles/{slug}.md`        | 1 per role family | Forward-deployed PM, applied AI PM, etc. |
| job        | `wiki/jobs/{date}-{co}-{slug}.md` | 1 per posting | A specific live job posting |
| outreach   | `wiki/outreach/{slug}.md`     | 1 per contact | A named person + interaction history |
| interview  | `wiki/interviews/{date}-{co}-{round}.md` | 1 per interview | Loop notes + post-mortem |
| evidence   | `wiki/evidence/{slug}.md`     | 1 per story | A reusable story for resumes/interviews |
| resume     | `wiki/resumes/{date}-{co}-{slug}.md` | 1 per generated resume | A tailored output |

**Slugs** are lowercase, hyphen-separated, stable. `cohere-platform-pm`, not `Cohere Platform PM Final v3`.

**Derived navigation:** `wiki/INDEX.md` is a generated catalog, `wiki/aliases.md` is a generated alias map, `scripts/wiki.py index` regenerates both, and `scripts/wiki.py lint` checks broken links and orphaned pages before commit.

---

## 3. Cross-linking rules

Wiki pages reference each other using **Obsidian `[[wikilinks]]`** format — e.g. `[[companies/cohere]]`, `[[evidence/career-accomplishments]]`. This is required for Obsidian Graph View to render connections. Do NOT use relative markdown path links for cross-references.

| When you write... | You must link to... |
|-------------------|---------------------|
| A `job` page      | the `company` page + the `role` page + any `evidence` you'd use. End the page with a `## Related` section listing each as `[[companies/slug]]`, `[[evidence/slug]]` etc. |
| An `interview` page | the `job` page + the `company` page |
| A `resume` page   | the `job` page + every `evidence` page it draws from |
| An `outreach` page | the `company` page + any `job` page in scope |

**Orphans are bugs.** If a page has no inbound links, either link it or delete it during lint.

**Format:** Always end every wiki page with a `## Related` section using `[[wikilinks]]`. Example:
```
## Related
- [[profile/me]]
- [[companies/stripe]]
- [[evidence/career-accomplishments]]
```

---

## 4. Source folders

`sources/` is divided by source type. You decide which folder a new input belongs in. You **never rename or edit** an existing source — only add new ones.

| Folder              | Holds                                          |
|---------------------|------------------------------------------------|
| `job-posts/`        | Pasted or saved job descriptions (markdown)    |
| `company-news/`     | Press releases, blog posts, leadership posts   |
| `user-docs/`        | The human's own artifacts, including onboarding uploads, promo docs, reviews, transcripts |
| `interviews/`       | Recordings, transcripts, recruiter emails      |
| `outreach/`         | Sent and received messages, LinkedIn DMs       |

Filename convention: `YYYY-MM-DD-{short-slug}.md` (or original extension for media).

---

## 5. The ingest contract

When the human files a new source — typically by pasting it in chat, dropping it into `sources/`, or uploading a batch for onboarding — you perform the **ingest** operation. The full spec is in [`ops/ingest.md`](ops/ingest.md) and [`ops/onboarding.md`](ops/onboarding.md). In short:

1. Save the source verbatim into the right `sources/<folder>/` subdir with a dated filename.
2. Identify which wiki pages this source touches (existing pages to update + new pages to create).
3. Update each page in place. Add cross-links. Flag any contradictions inline using `**CONTRADICTION:**` markers.
4. Regenerate `wiki/INDEX.md` and `wiki/aliases.md` if the page set changed, then run `scripts/wiki.py lint`.
5. Summarize the diff to the human in one paragraph: what was added, what changed, what contradicts.

**Never lose a source.** Once it's filed, it stays.

---

## 6. The query contract

When the human asks a question, follow [`ops/query.md`](ops/query.md):

1. Search the wiki for relevant pages.
2. Synthesize an answer with explicit citations: `→ wiki/companies/cohere.md`.
3. If the answer is substantial and reusable, offer to file it as a new wiki page.

---

## 7. The lint contract

Periodic health check, full spec in [`ops/lint.md`](ops/lint.md):

- **Stale**: a page whose claims haven't been verified in N weeks (default: 8).
- **Orphan**: a page with zero inbound wiki links.
- **Broken link**: a link to a wiki page that no longer exists.
- **Contradiction**: a fact that appears with different values on two pages.
- **Catalog drift**: `wiki/INDEX.md` or `wiki/aliases.md` is out of sync with the current wiki pages.

Run lint at the start of any session that begins with "let's review where we are."

---

## 8. The apply contract

When the human says "I want to apply to X," follow [`ops/apply.md`](ops/apply.md). The short version:

1. Ingest the job posting → `wiki/jobs/{date}-{co}-{slug}.md`.
2. Score it against the profile, positioning, and exclusion rules.
3. If it passes, generate a tailored resume in `wiki/resumes/`.
4. Surface outreach options from `wiki/outreach/` and `wiki/companies/{co}.md`.

---

## 9. Resume rules (hard)

These are non-negotiable. See also [`prompts/resume-rules.md`](prompts/resume-rules.md).

- **Verified facts only.** Every metric, claim, and accomplishment must trace to an `evidence/` page or a source. No invented numbers, no extrapolation.
- **One page per resume** unless the human explicitly asks for two.
- **Prose top summary**, not bullets.
- **Anti-slop**: see [`prompts/human-voice-spec.md`](prompts/human-voice-spec.md) and [`prompts/writing-steering-spec.md`](prompts/writing-steering-spec.md).

---

## 10. PII boundary (critical)

This repository **must not contain PII**. The human's real name, contact info, employers, project names, metrics, and salary expectations all live in `wiki/` and `sources/`, which are gitignored.

If you are about to commit something to this repo, scan it for:

- Real names (use placeholders like `[YOUR_NAME]` in templates/examples)
- Email, phone, LinkedIn, location
- Specific employer names, project names, internal codenames
- Specific metrics tied to specific employers
- Compensation figures
- Named outreach contacts

If any of those appear in a file destined for git, **stop and ask the human**.

---

## 11. SQLite tracker + FTS5 search index

**State tracker:** `data/schema.sql` defines tables for applications, outreach contacts, and actions. The wiki holds context; the database holds state transitions. `data/jobsearch.db` is gitignored.

**Full-text search index:** `data/wiki-index.db` is an FTS5 index over all wiki pages, rebuilt every 30 min by a Hermes cron job. Use it to find relevant pages instead of grepping:

```sql
-- Find pages most relevant to a query
SELECT path, title, snippet(wiki_fts, 4, '→', '←', '...', 20) as excerpt
FROM wiki_fts WHERE wiki_fts MATCH 'pricing experimentation healthcare'
ORDER BY rank LIMIT 5;
```

Rebuild manually: `python3 scripts/wiki.py index`

Both database files are gitignored. The utility script (`scripts/wiki.py`) is tracked. Lint reports broken links by default and reports orphans unless you pass `--strict-orphans`.

---

## 12. Index page

`wiki/INDEX.md` is the lightweight navigation hub for the wiki. It should stay curated and generated from the current pages, not become a second database or reporting layer.

---

## 13. Scheduled automation

The Job Search OS can run as a recurring pipeline:

- **Nightly scan:** search Forbes AI50 and adjacent AI/startup/tech/FAANG companies for open U.S. roles that fit the user's lane (forward-deployed PM, presales, solutions, applied AI PM, platform PM, customer-facing technical PM). Verify status and posted date when possible, then add new roles to `wiki/queue/target-queue.md` and create/update matching `wiki/jobs/` pages.
- **Morning report (8:30):** summarize the updated queue, highlight new additions/removals, and surface the best daily application targets.
- **Evening todo (7pm):** produce a concise application/outreach to-do list from the current queue.

Queue state stays split into **favourite**, **application**, and **applied/archive** buckets. New live roles belong in the application queue and are sorted by fit.

---

## 14. Update protocol

If you (the AI) want to change this SCHEMA.md — for example, to add a new page type or automation rule — propose it to the human in chat first. Don't edit silently. The schema is the contract; only the human signs new contracts.

## 15. Agent search workflow

When answering a question or starting an operation, the agent should use this order:

1. **Bootstrap** (every session): read `SCHEMA.md`, `wiki/profile/me.md`, `wiki/profile/positioning.md`
2. **Search** (find relevant pages): query `data/wiki-index.db` with FTS5 — faster and more accurate than grep
3. **Navigate** (follow connections): for each relevant page, read its `## Related` wikilinks to pull connected context
4. **Act** (write/update): every page written/updated must end with a `## Related` section using `[[wikilinks]]`

This ensures the agent always has the right context without reading all 370+ pages on every turn.
