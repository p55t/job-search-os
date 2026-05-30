# Writing Steering Spec — ATS + Anti-Slop

The full spec for resume writing in 2026. Used by the `apply` op.

## 1. ATS strategy

- **Formatting:** clean, single-column. Arial or Calibri only. No icons, no graphics, no "skill bars."
- **Section naming:** standard only — Experience, Education. (Skills only if needed.) ATS parsers fail on creative headers like "My Journey" or "Achievements Unlocked."
- **Keyword integration:** never build "skill soup" lists. Embed skills in bullets: "Reduced API latency 35% using [tool/tech] optimization."
- **File type:** export as `.pdf` (or `.docx` if required by the application portal).

## 2. Human voice & anti-slop

- **Messy-problem rule.** Generic bullet: "Led cross-functional initiatives." Human bullet: "Led 7-person team. Blocked by [specific constraint]; redesigned [thing] to meet [requirement], launched in 4 months."
- **Banned words.** Never use: leverage, synergistic, pivotal, groundbreaking, delve, cutting-edge.
- **Sentence shape.** Mix short (3–6 words) with medium compound sentences.
- **Evidence-first.** Metrics at the start or core, not the end.
- **No editorializing.** Never say something was "impressive," "vital," "significant." Show the data.

## 3. Hiring-manager simulation

Before declaring the draft done, simulate a hiring manager for the target role reading the resume in 30 seconds:

- Do they get the seniority signal in the first sentence?
- Do they see the 2–3 strongest stories without scrolling?
- Do they understand what *kind* of PM/engineer/architect this person is?
- Do they want to talk to this person, or do they bounce?

If any of those is "no," rework the top half.

## 4. Pre-submit checklist

- [ ] Every metric traces to an evidence page or source.
- [ ] No banned words in any bullet.
- [ ] Read aloud — no stumbles.
- [ ] One page (unless explicit two-page approval).
- [ ] Standard headers only.
- [ ] PDF exported with single-column layout, 10–11pt font, 0.6–0.8" margins.
- [ ] File named clearly: `{firstname-lastname}-{company-slug}.pdf`.
