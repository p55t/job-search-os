# Op: Query

Answer a question against the wiki. Synthesize, cite, optionally file the answer.

## When this runs

- The human asks a question — about themselves, a company, a role, a contact, the state of the search.
- The human says "what do we know about X" / "where are we on Y" / "remind me about Z."

## Procedure

### 1. Search

Identify which wiki pages are likely relevant:

| Question shape                              | Pages to read                              |
|---------------------------------------------|--------------------------------------------|
| About the human                              | `wiki/profile/me.md`, `wiki/profile/positioning.md`, `wiki/evidence/*` |
| About a company                              | `wiki/companies/{slug}.md`, related `wiki/jobs/`, `wiki/outreach/` |
| About a role family                          | `wiki/roles/{slug}.md`, related `wiki/companies/` |
| State of a specific job                      | `wiki/jobs/{slug}.md` + linked pages       |
| Outreach status                              | `wiki/outreach/*` + `data/jobsearch.db` (if used) |
| "What should I do today"                     | Run [lint](lint.md) first, then summarize  |

Use grep over `wiki/` if you're not sure where something lives. The schema gives you topology — use it.

### 2. Synthesize

Compose the answer in plain prose. Match the human's question shape — short question gets a short answer.

**Always cite.** Every claim points to a wiki page:

> ExampleCo's strongest live fit is [Role Family X] — your [strength A]/[strength B] map cleanly (→ `wiki/companies/exampleco.md`, `wiki/profile/positioning.md`).

If two pages disagree, surface the disagreement and the dates. Don't pick a side silently.

### 3. Decide if it should be filed

After answering, ask yourself: **is this answer reusable?**

- "What time is the [Co X] interview?" → no, ephemeral.
- "What's our story for why [Co X] fits?" → yes, file as `wiki/companies/{slug}.md` if not already there, or as a section in `wiki/profile/positioning.md`.
- "How does the human's pricing work compare to [Co Y]'s needs?" → yes, file as `wiki/companies/{slug}.md` § Why-it-fits.

If yes, offer to file it. Don't file silently — the human approves new pages.

### 4. Stay honest

Three rules:

1. **No confabulation.** If the wiki doesn't know, say so. Don't fill the gap from your training data.
2. **No invention.** Don't manufacture metrics, dates, or relationships that aren't in a wiki page or source.
3. **Cite source, not vibe.** "I think [Company] values X" is unacceptable. "→ `wiki/companies/{slug}.md` says X" is fine.

## Example

User asks: "Who do we know at [Company X] and have we reached out?"

1. Read `wiki/companies/{slug}.md`, `wiki/outreach/{slug}-*.md`.
2. Synthesize:

   > One named contact: **<name>**, <role> — strength 1 (public-post warm), no touch yet. Draft message is in `wiki/outreach/{slug}.md` § Draft. Recommended: send this week — it ties to the live [Role Family] role (`wiki/jobs/YYYY-MM-DD-{slug}.md`).

3. Don't file — this is a status report, not a reusable artifact.
