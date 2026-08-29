---
name: post-case-loop
description: >-
  Use after a case is logged and Daniel wants to work out what it means — "let's
  debrief", "how did that go", "what should I work on", "what do I fix". Also
  use when a session entry exists with no diagnosis or drills attached. Not for
  logging a session, not for pre-case warm-up.
disable-model-invocation: false
metadata:
  version: "0.1.0"
  author: "Nova Caelum / Chief-PM"
  license: "proprietary"
  platforms: [linux]
  category: casing
  tags: [debrief, diagnosis, drills, weakness, transfer]
  related_skills: [session-intake, case-scoring, warm-up, palladia-worklog]
  provenance:
    origin: "Nova Caelum-authored"
    platform: "Hermes Agent (Nous Research) — palladia profile, olympus1"
    design_source: "SOUL.md §core loop, extracted per Daniel review note 2026-08-29"
category: casing
---

# Post-Case Loop

## Overview

This is the loop that turns a case that happened into a case Daniel learned
from. Without it, a logged case is a diary entry.

Its output is not a report. It is **one or two drills with a success criterion
and a retest date.** If you finish and he does not know what to practice next,
the loop failed regardless of how good the analysis was.

## When to Use

After a session is in the log and Daniel wants to make sense of it — or when you
notice a session entry with no diagnosis attached.

**Not for:** logging a session or pulling its recording (`session-intake`, which
runs first), or the minutes before a case (`warm-up`).

Three skills, one chain, no overlap:

| Skill | Owns | Stops at |
|---|---|---|
| `session-intake` | Getting raw material in — details, entry, media. **Never scores.** | Record created, gaps named. |
| **`post-case-loop`** (this) | The conductor: debrief → assessment → ledger → drills. | Drills and a retest date. |
| `case-scoring` | The assessment engine. Invoked from step 4. | Returns the assessment; does not prescribe. |

`case-scoring` is **not yet written** (blocked on Daniel). Until it exists, do
step 4 inline and say plainly that you are doing so without the rubric.

## Procedure

### 1. Never mutate the source

Transcript, recording, original notes — read, never edit. Everything you produce
is a new artifact that links back. If you find an error in a source, note it in
your artifact; do not correct his file.

### 2. Ask the minimum debrief questions

Use `clarify`. Two or three questions, not an interview — only what you cannot
resolve from the record. Every question the transcript already answered spends
his attention on your convenience.

### 3. Self-assessment BEFORE your read — non-negotiable

Ask how he thinks it went before you say anything about how it went.

**The gap between his assessment and yours is itself the diagnostic.** If he
rates a case Good and you read it as Fine, the finding is not the rating — it is
*what he could not see*. A candidate who cannot feel his own weak cases will not
self-correct in the room, and that outranks whatever the case surfaced.

Never skip this to save a turn. Once he has heard your read, his self-assessment
is gone for that case and cannot be recovered.

### 4. Assess

Invoke `case-scoring` when it exists. Cover at minimum: structure, quantitative
execution, interpretation, synthesis, communication, and process discipline.

Record it in **Daniel's vocabulary** — his field names, his values, per the
drive map. `Overall Performance` is Bad/Fine/Good/Great/Perfect; never a number.
Any field of ours goes **alongside his, never in place of one.**

`(Growth) Feedback` is where the real work lands — it **is** the weakness
record, and recurring patterns are derived from it. Write it as evidence, not
encouragement. Many of his existing notes have it empty; filling it well is the
highest-value thing this loop does.

### 5. Record how much help he needed

A correct answer after three hints is not an independent answer, and a log that
records only outcomes inflates until it is useless.

Capture the help level: no help · neutral clarification · light prompt ·
directional hint · major scaffold · answer supplied.

> `[BLANK — needs Daniel: this is our field, not his, and it has no home in the
> note schema yet. Do not invent one. Ask where it goes.]`

### 6. Update the weakness record

Find the recurring thread across recent `(Growth) Feedback` entries — not just
this case.

- **2 sightings → watch list.** Noted, monitored, not yet formal.
- **3 sightings → promoted.** It becomes a named weakness and it drives drills.

Time matters: a pattern that stopped appearing weeks ago is resolved, not open.
Say when a weakness last appeared.

> `[BLANK — the weakness ledger has no home *in the drive* yet. Proposed home
> `_system-files/`. Ask before creating it. Until then, hold the derivation in
> the debrief output and the worklog entry.]`
>
> **Note (2026-08-29):** a first derived ledger now exists as a review artifact
> outside the drive — `WeaknessLedger_Palladia_ChiefPM_2026-08-29.md` in the
> rebuild workspace, produced by `weakness-derivation` from 36 case notes. Read
> it for current standings. It is **not** in PallaDrive and is not yet the
> live ledger, so the blank above still stands: the in-drive home is undecided.

### 7–8. Update the two notes — warm-up aggressively, high-yield conservatively

The **warm-up note** is allowed to churn: overwrite it with what matters for the
*next* case. Nothing in it needs to survive.

The **high-yield note** takes only what is explicitly important or repeatedly
evidenced, always linked back to its source case. One that accretes everything
becomes a second casebook, which is the opposite of its purpose.

> **Known defect (FixRegister B13):** both exist today as PDFs in
> `casing/notesheets/` and you cannot write to them. Produce the intended update
> as text and tell Daniel it needs hand-application. Do not silently skip the
> step, and do not create a competing Markdown file without asking.

### 9. Prescribe one or two drills

Attack the highest-leverage weakness only. Each drill carries a **success
criterion** and a **retest** — when and how you check that it transferred.

One drill he does beats five he reads. If you found ten problems, name the one
or two that explain most of the others and explicitly park the rest.

### 10. Log it

Append a `palladia-worklog` entry.

## Pitfalls

- **Twenty comments and no plan.** The most common coaching failure and the
  easiest one for a fluent model to commit. Comprehensiveness is not diagnosis.
- **Giving your read first.** Kills step 3 permanently for that case.
- **Scoring inside `session-intake`.** Wrong skill; the record must exist first.
- **Marking a dimension improved because a drill went well.** Not learned until
  it shows up in a real case unprompted.
- **Inventing schema.** A field with no home is `[BLANK]` and a question for
  Daniel — not a folder you create.
- **Composite scores or pass probabilities.** Never.

## Verification

Before you call the loop done:

- [ ] Source material unmodified.
- [ ] He self-assessed before hearing your read, and the gap was addressed.
- [ ] Assessment recorded in his field names and his values.
- [ ] Help level captured (or flagged as having no home yet).
- [ ] Weakness derivation states how many sightings and when the last one was.
- [ ] Warm-up update produced; high-yield touched only if genuinely earned.
- [ ] **One or two drills exist, each with a success criterion and a retest.**
- [ ] Worklog entry appended.

If the drills line is unchecked, the loop is not done.
