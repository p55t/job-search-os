# Resume — Hard Rules

These rules are non-negotiable. The `apply` op enforces them. Violations are bugs.

## 1. Verified facts only

Every metric, claim, and accomplishment in a generated resume must trace back to:

- a `wiki/evidence/{slug}.md` page that itself cites a source, OR
- a source file in `sources/`

If a candidate metric has no traceable source, **leave it out**. Never extrapolate, infer, or "round up" a number.

## 2. No invention

- No invented dates.
- No invented project names.
- No invented people.
- No invented outcomes.
- No "we" when "I" is the truth (or vice versa).

If you don't know whether the person was sole owner or co-owner of an initiative, ask before drafting.

## 3. One page

One page unless the human explicitly approves two. A resume that wraps to a second page because of a single line of overflow is a formatting bug; fix the formatting.

## 4. Prose summary

The top summary is **prose**, 3–4 sentences. Never bullets. Never an "Objective." Never a "Core Competencies" block.

## 5. Section order

Always: Summary → Experience → Education. No exceptions unless the human has > 10 years and explicitly wants Skills or Selected Accomplishments.

## 6. Bullet construction

- Start with an action verb (past tense for prior roles, past or present for current).
- One concrete thing per bullet — no chained accomplishments.
- Metric at the start or core, not at the end.
- No banned words (see § 8).

## 7. ATS-clean

- Standard headers: Experience, Education. (Optional: Skills, only if needed.)
- Single column, no tables, no icons, no graphics, no skill bars.
- Arial or Calibri, 10–11pt.
- Skills embedded in bullets, never a "keyword soup" list.
- Export as `.pdf` (or `.docx` if the application requires it).

## 8. Banned words and phrases

Never use:

- leverage
- synergistic / synergy
- pivotal
- groundbreaking
- delve
- cutting-edge
- world-class
- innovative (as an adjective)
- Responsible for / Tasked with / In charge of
- Successfully (just say it happened)
- Helped to (you either did or you didn't)

## 9. Read aloud

Before considering the draft done, read every bullet aloud at speaking pace. Anything you stumble over gets rewritten.

## 10. Honest "I"

If the human led a team, say so plainly (e.g. "Led 7-person cross-functional team..."). If they contributed, say "Contributed to..." or "Worked with [team] to...". Don't blur ownership.

## See also

- [`human-voice-spec.md`](human-voice-spec.md) — voice rules
- [`writing-steering-spec.md`](writing-steering-spec.md) — ATS + anti-slop spec
- [`style-guide.md`](style-guide.md) — short style reference
