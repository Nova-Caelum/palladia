---
name: post-case-given
description: >-
  Use after Daniel has GIVEN a case to someone — when he says he just cased
  a person, asks to write up a session he ran, or a Given session folder exists
  with an unfilled recording or eval file. Not for cases he took, not for
  pre-case prep.
disable-model-invocation: false
metadata:
  version: "0.1.0-draft"
  status: COMPLETE — all three parts run end-to-end against the Ryan 2026-08-30 session
  author: "Nova Caelum / Chief-PM"
  license: "proprietary"
  platforms: [linux]
  category: casing
  tags: [given, post-case, transcript, granola, session-notes]
  related_skills: [granola-capture, pre-case-given, session-intake, case-scoring]
  provenance:
    origin: "Nova Caelum-authored"
    platform: "Hermes Agent (Nous Research) — palladia profile, olympus1"
    design_source: "Daniel, verbally, 2026-08-30, part by part; each part run live before being written"
    rubric_source: "Daniel's 2025 peer feedback sheet (Saumya Garg, 2025-10-23)"
    reference_artifact: "casing/session_notes/2026_08_30_Daniel X Ryan/session-recording_Ryan20260830.md"
category: casing
---

# Post-Case (Given)

> ## Reference run
> Every part below was executed against the **Ryan 2026-08-30** session before
> being written down. That session folder is the worked example — when this
> skill is ambiguous, go look at it.

## Overview

Daniel gave a case. This skill turns that into a record: the transcript and
summary pulled out of Granola and filed correctly, so the session can be
evaluated later instead of being remembered vaguely.

Three parts, in order: **capture** the session out of Granola · **evaluate** it
into Daniel's feedback sheet · **publish** it as a PDF for the candidate and a
row in the case log.

The output that matters is the PDF. Everything upstream exists so that document
is accurate, and the whole point of automating it is that Daniel used to write
it by hand and it was slow.

## When to Use

Daniel finished giving a case. Also when a `YYYY_MM_DD_Daniel X <Person>` folder
holds a recording file still at `Pending download`.

**Not for:** cases Daniel took (`session-intake`), pre-case prep
(`pre-case-given`), or scoring his own performance (`case-scoring`).

## Part 1 — Capture

### 1 · Invoke `granola-capture` first

**Do not call a Granola tool before invoking it.** That skill owns the retrieval
contract — union sweep, count assertion, direction detection, and three silent
failure modes, all observed live. A single `list_meetings` call returns a clean
response that is missing sessions.

The one you cannot engineer around: **a Private note is invisible to every
retrieval path.** If the expected session is not in the union, say so and name
Private as the likely cause. Do not report success.

### 2 · Locate the session folder — check before creating

`casing/session_notes/YYYY_MM_DD_Daniel X <Person>/` (underscores in the date).
**List the directory first.** Exactly one folder per person per date — duplicates
split a session's evidence and neither half is findable later.

### 3 · Fill the recording file

Target: `session-recording_<Person><YYYYMMDD>.md`, from
`_meta/template_library/session-notes_template/YYYY_MM_DD_Daniel X Partner/session-recording_TEMPLATE.md`.

`[LOCKED]` **`session-recording_Ryan20260830.md` is the reference shape.** If the
template and that file ever disagree, Ryan's file wins.

Load per `granola-capture` Step 3: summary into `## Granola Summary:`, verbatim
transcript into `## Full Transcript:`, labels normalized, header status and
Granola ID filled.

**Only the label changes.** Transcript wording is never tidied or summarized —
it is evidence, and Part 2 is written against it.

### 4 · Flip status only for what you actually pulled

A folder can hold one pulled file and one still pending; that is correct.
Never flip a status to assert a pull that did not happen.

## Part 2 — Evaluation

Target: `given-case_eval-<Person><YYYYMMDD>.md`, from
`_meta/template_library/session-notes_template/YYYY_MM_DD_Daniel X Partner/given-case_eval_TEMPLATE.md`. The structure is Daniel's
2025 peer feedback sheet.

### 5 · You write the feedback. Daniel writes the scores.

**Never fill a score or a rating.** Every `___ / 5`, every Great/Good/Fine cell,
and the total ship **blank** — Palladia does not grade a peer. You own the
**feedback prose**, which was the labor-intensive part and the reason this is
automated at all.

### 6 · Attribute every line. Not optional.

- **`[D]`** — Daniel said it in-session. Quote him.
- **`[C]`** — the candidate said it, usually self-assessment.
- **`[obs]`** — visible in the transcript, said by neither.

**Prefer `[D]`, heavily.** His coaching is the asset; your job is retrieval and
arrangement, not authorship. Reference-run split was 33 / 5 / 8 — that is the
target shape. Tags are never weighted differently; they exist so no reader has
to guess who said something.

### 7 · Work the transcript, not the summary

The summary is an index. The **coaching lives in the transcript** — Daniel's
end-of-session feedback runs several long unbroken turns. Read them in full.

Preserve his markers: `(+)` strength · `(-)` growth · `(~)` minor · `(---)`
emphatic · `-->` follow-on.

### 8 · Give the candidate's self-assessment its own section

"How do you think it went" is separate content and belongs in **Candidate's own
read**, never blended into Daniel's assessment. Where the two converge
independently, say so — that is a coachability signal.

### 9 · Let contradictions stand, then resolve them from the text

In the reference run Daniel said *"you didn't catch that it was brainstorm now"*
and the candidate answered *"I knew — I just lost it."* Those are different
failures: recognition versus retention-under-load. The transcript settles it.
**Surface the distinction rather than smoothing it** — it changes the drill.

## Part 3 — Publish

### 10 · Export the PDF

```
python3 _system-files/scripts_library/md_to_pdf.py <eval>.md <eval>.pdf
```

Beside the markdown, in the session folder. **The candidate has no markdown
reader** — the PDF is what they actually receive. Verify it is non-empty and its
extracted text still shows the attribution tags.

### 11 · Add the row to the case log

`casing/casing-session_log/YYYY-MM-DD_<Case Name>_Given.md`, from
`_meta/template_library/case-session-entry.md`. **The `_Given` suffix is
required** — it disambiguates from the same case taken later.

Source it from the eval, not the transcript again. Populate what the evidence
supports; **leave the rest blank — a blank is honest, a guess corrupts every
count built on it.**

Blank by definition on a Given session:

| Field | Why |
|---|---|
| `Overall Performance` | scores Daniel as candidate |
| `Independence` | same |
| `Counter` | tallies cases *taken* |
| `Weaknesses hit` / `Top of mind` | Daniel's ledger and Daniel's checklist — this session's weaknesses are the candidate's |

`(Growth) Feedback` is the weakness record and `weakness-derivation` reads it —
write it **behaviorally and specifically**. "Be more concise" is unusable;
"read Exhibit 1 line-by-line instead of synthesizing to a so-what" is usable.

Set `Casing` and `Behavioral` independently. A session that opened with a fit
question is `Y` and `Y`.

### 12 · Report

Name the meeting ID, the three files written, and anything left blank on
purpose.

## Pitfalls

- **Calling a Granola tool before invoking `granola-capture`.** One unfiltered
  list call silently drops sessions. Observed, reproducible.
- **Reporting success when the union came up short.** The response looks clean.
  The count is the only thing that catches it.
- **Creating a second session folder for a date that already has one.** List first.
- **Collapsing a reciprocal pair.** Two people can case each other on the same
  day. That is two sessions and two files.
- **Editing transcript wording.** Labels only. Part 2 scores against this text.
- **Filling Part 2 from `case-scoring`.** Wrong direction — that rubric is for
  Daniel as candidate.
- **Scoring the candidate.** Not yours. Scores ship blank, always.
- **Writing feedback in your own voice when Daniel's words are right there.**
  Paraphrasing his coaching strips the thing that made these sheets useful.
- **Working from the Granola summary alone.** The quotable coaching is in the
  transcript's long end-of-session turns.
- **Blending the candidate's self-assessment into Daniel's.** Separate sections.
- **Smoothing a contradiction between what Daniel said and what the candidate
  said.** The disagreement is usually the finding.
- **Guessing a case-log field to avoid a blank.** A fabricated value silently
  corrupts every count built on it.
- **Omitting the `_Given` suffix** on the log filename.

## Verification

- [ ] `granola-capture` was invoked before any Granola tool call.
- [ ] Union sweep ran; count matched expectation, or the shortfall was escalated.
- [ ] `casing/session_notes/` was listed before any folder was created.
- [ ] **Exactly one** folder matches `YYYY_MM_DD_Daniel X <Person>`. State the count.
- [ ] `grep -cE '^\*\*(Me|Them):' <file>` returns **0**.
- [ ] Header carries a real Granola UUID and a status matching what happened.
- [ ] Both content sections non-empty; transcript wording unedited.
- [ ] No status flipped for a transcript that was not pulled.
- [ ] **Every score and rating in the eval is blank.**
- [ ] **Every feedback line carries `[D]`, `[C]`, or `[obs]`.** No untagged lines.
- [ ] `[D]` lines quote Daniel rather than paraphrase him.
- [ ] Candidate's self-assessment is in its own section.
- [ ] PDF exists beside the markdown, is non-empty, and its extracted text still
      shows the attribution tags.
- [ ] Case-log entry exists with the `_Given` suffix and validates against
      `case-session-entry.md` — no missing fields, no invented ones.
- [ ] `Overall Performance`, `Independence`, and `Counter` are blank.
- [ ] `(Growth) Feedback` is behavioral and specific enough for
      `weakness-derivation` to consume.
