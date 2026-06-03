# Target Queue

**Last updated:** YYYY-MM-DD

This file is the working queue for job search prioritization. Keep it focused on live, relevant roles only.

---

## Queue rules

- Keep only **open** roles.
- Keep only **US-based** roles unless the human explicitly says otherwise.
- Remove roles that are already applied to.
- Remove roles that are engineering- or manager-heavy if they are outside the target lane.
- Remove duplicates; keep the best canonical version.
- Rank by:
  1. company preference
  2. role fit
  3. freshness / urgency
  4. referral leverage

---

## Active queue

| Rank | Company | Role | Location | Fit | Status | Next action | Resume | Notes |
|------|---------|------|----------|-----|--------|-------------|--------|-------|
| 1 | [Company] | [Role title] | [Location] | High / Med / Low | open / research / tailor / apply | [research / tailor / apply] | `wiki/resumes/{slug}.md` | [short note] |
| 2 | [Company] | [Role title] | [Location] | High / Med / Low | open / research / tailor / apply | [research / tailor / apply] | `wiki/resumes/{slug}.md` | [short note] |
| 3 | [Company] | [Role title] | [Location] | High / Med / Low | open / research / tailor / apply | [research / tailor / apply] | `wiki/resumes/{slug}.md` | [short note] |

### Status meanings

- **open** — verified live and accepting applications
- **research** — worth reviewing before tailoring
- **tailor** — needs resume / outreach customization
- **apply** — ready to submit
- **applied** — move to archive immediately
- **drop** — closed, wrong geo, wrong lane, or duplicate

---

## Applied archive

Move roles here immediately after submission.

| Applied date | Company | Role | Resume | Application link | Follow-up date | Notes |
|-------------|---------|------|--------|------------------|----------------|-------|
| YYYY-MM-DD | [Company] | [Role title] | `wiki/resumes/{slug}.md` | [link] | YYYY-MM-DD | [status / follow-up note] |

---

## Review checklist

Before a role stays in the active queue, verify:

- [ ] role is still open
- [ ] location is US-based
- [ ] role is not already applied
- [ ] role is not a duplicate
- [ ] role matches target lane
- [ ] there is a clear next action

---

## Suggested workflow

1. New role found → add to active queue.
2. Verify fit → set status.
3. Tailor resume / outreach if needed.
4. Apply.
5. Move to archive.
6. Drop anything that is stale or outside scope.

---

## Links

- Company page → `wiki/companies/{slug}.md`
- Role family → `wiki/roles/{slug}.md`
- Job page → `wiki/jobs/{date}-{co}-{slug}.md`
- Resume page → `wiki/resumes/{date}-{co}-{slug}.md`
