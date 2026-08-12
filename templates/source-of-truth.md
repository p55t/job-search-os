# Source of Truth Contract

**Last updated:** YYYY-MM-DD

This private wiki page defines where operational state lives so scheduled and ad hoc work do not drift.

## Canonical stores

| Question | Canonical source | Notes |
|---|---|---|
| Profile, positioning, target lanes, evidence, company/job context | `wiki/` pages | Cite the underlying private source or wiki page. |
| Application state, applied/archive records, and company cooldowns | `data/jobsearch.db` | Operational source of truth. |
| Human-readable ranked queue | `wiki/queue/target-queue.md` | Rendered display view; reconcile it from the database. |
| Raw job posts, resumes, and uploads | `sources/` | Immutable once filed. |
| Search/navigation index | `data/wiki-index.db` | Generated only; never canonical. |

## Required bootstrap

1. Read `SCHEMA.md`, this page, `wiki/profile/me.md`, and `wiki/profile/positioning.md`.
2. Query `data/jobsearch.db` and `applied_company_cooldowns` before recommending, adding, removing, or ranking a role.
3. Read `wiki/queue/target-queue.md` only as display context.
4. If the database and queue disagree, update the queue to match the database.

## Write protocol

1. Upsert the application row in `data/jobsearch.db` using non-null `wiki_page` as its identity.
2. File any available raw material under `sources/`.
3. Create or update relevant wiki pages.
4. Reconcile the rendered queue.
5. Rebuild the search index and run lint.

## Cooldown rule

A company is suppressed from active recommendations for 90 days after its latest application date, unless explicitly reopened. Resolve known company aliases before relying on the cooldown view.

## Related
- [[profile/me]]
- [[profile/positioning]]
- [[queue/target-queue]]
