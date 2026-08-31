---
name: session-intake
description: >-
  Use when Daniel finishes a practice case or behavioral session and wants it
  logged — "log that session", "I just cased", "add this session". Also use when
  a recording or transcript arrives for a session that is not yet in the session
  log.
disable-model-invocation: false
metadata:
  version: "0.2.0"
  author: "Nova Caelum / Chief-PM"
  license: "proprietary"
  platforms: [linux]
  category: casing
  tags: [ingestion, granola, session-log, transcripts, provenance]
  related_skills: [case-scoring, palladia-worklog]
  provenance:
    origin: "Nova Caelum-authored"
    platform: "Hermes Agent (Nous Research) — palladia profile"
    design_source: "Daniel, verbally, 2026-08-29 — workflow described directly"
category: casing
---

# Session Intake

> ## ⚠️ PROVISIONAL — do not treat as finished
>
> Daniel: *"The skill does not have to be finalized right now. Once we have a few
> sessions, we'll finalize it."*
>
> This is the **workflow** he described, written down so it can be run and then
> corrected against reality. Two things are deliberately unfinished:
>
> - **The session-entry schema is now SETTLED.** `[VERIFIED 2026-08-29]` The
>   template at `_meta/template_library/case-session-entry.md` is the shape.
>   Populate from it; do not invent a shape per run.
> - **The Granola MCP is not installed.** Steps 4–6 below are unrunnable today.
>
> Run it manually, note where it is wrong, fix it after a few real sessions.

## Overview

Turn a finished practice session into a logged, evidenced session record.

Intake **collects, files, and evidences**. It does not score. Scoring is a
separate step against a separate standard, and folding it in here produces a
rushed verdict on a transcript you have not finished reading.

## When to Use

- Daniel says he finished a case or a behavioral session.
- A recording or transcript arrives for a session not yet logged.
- He asks to log, file, or add a session.

**Not for:** casebooks or case PDFs (that is `casebook-case-extract`), scoring an
already-logged session, or re-filing something already in the session log.

## HARD RULES

1. **Never mutate an original recording or transcript.** It is evidence. Derived
   artifacts live beside it, never in place of it.
2. **Never invent content from an unreadable source.** If audio will not
   transcribe or a transcript is partial, say exactly what is missing and mark
   the gap in the record. A plausible reconstruction is a lie with good posture.
3. **Never score inline.** Log it, then hand off.
4. **Never overwrite an existing session entry.** Sessions repeat — the log
   already contains `Dutch Dam Dilemma` twice, on 2025-11-25 and 2025-11-28. Two
   sessions on the same case are two records.

## Where things go

`[VERIFIED 2026-08-29]`

| Artifact | Location |
|---|---|
| Session entry | `casing/casing-session_log/` |
| Entry template | `_meta/template_library/case-session-entry.md` |
| Case Log Base | `Case Log.base` — renders the folder as tabs |
| Recording | `recordings/` — **top level, not under `casing/`** |
| Unrouted arrivals | `_inbox/` |

**Why `recordings/` is top-level.** Daniel: *"Some of these sessions will have
behaviorals and they will have cases in the same recording. So putting recordings
in either casing or behavioral is not the right call."*

A recording is not owned by one domain. It is referenced *from* a session entry,
never filed *under* one. One recording may be cited by both a case record and a
behavioral record.

## Naming

`[VERIFIED]` Daniel's existing convention, from 35 records:
`YYYY-MM-DD_<Case Name>.md` — original capitalization, spaces preserved, no
kebab-casing. Examples on disk: `2025-10-23_Pedal Pals.md`,
`2025-11-13_Catch me or I go; HuDisney.md`.

Follow it exactly. Do not normalize his names.

## Procedure

### 1. Collect the session details

Use the native **`clarify`** tool — a short structured question set, not
free-form conversation. Daniel has just finished a case and is spending
attention; asking six questions in one pass is cheaper than a dialogue.

Ask only for what you cannot derive. At minimum you need the case name, the
date, and who he cased with. `[VERIFIED]` His existing vocabulary already covers
the rest, and reusing it means the new record sorts alongside the old ones:

- `Activity` — `Given` or `Taken`
- `Format` — `In-person` or `Virtual`
- `Partner Type` — e.g. `FY`, `Self`, `Company`
- `Case book` — which casebook the case came from
- `Case Type` — a list, e.g. `["Profitability"]`
- `Difficulty`, `Qual Diff`, `Quant Diff`
- `Overall Performance` — `Bad` · `Fine` · `Good` · `Great` · `Perfect`
- `Casing` — `Y`/`N`. Usually `Y`.
- `Behavioral` — `Y`/`N`. **Always ask.** Not inferable from a recording, and a
  single session is often both casing and behavioral — that is the whole reason
  these are two independent flags rather than one session-type field.
- `Independence` — `no help` · `neutral clarification` · `light prompt` ·
  `directional hint` · `major scaffold` · `answer supplied`. Ask it plainly.
  A correct answer after three hints is not an independent answer, and without
  this every performance rating drifts upward over time.
- `Retest of` — if this session deliberately retested an earlier weakness, link
  that session. Optional, but it is what makes transfer observable.

> **His vocabulary wins.** These are Daniel's property names and his value sets,
> with 35 records behind them. Do not rename them, do not replace his five-point
> performance scale, and do not substitute our terms. Anything we add later
> attaches alongside; it does not displace.

### 2. Create the session entry

**Copy the template**, do not compose frontmatter from memory:
`_meta/template_library/case-session-entry.md`. It carries every field with a
comment stating its allowed values. `[VERIFIED 2026-08-29]`

Write to `casing/casing-session_log/` as `YYYY-MM-DD_Case Name_Activity.md` —
e.g. `2026-09-02_Great Burger_Taken.md`. The `Activity` suffix disambiguates
repeat cases; Daniel has run the same case twice on different dates before.

> Notes created before 2026-08-29 do not carry the `Activity` suffix. **Do not
> rename them** — wikilinks may point at them, and that is Daniel's call.

Leave a field blank rather than guessing it. Every count built on this data
inherits any value you invent, and a fabricated `Independence` or `Behavioral`
corrupts the exact measurements those fields exist to make possible.

### 3. Pull the media from Granola

> **`[BLOCKED]` The Granola MCP is not installed.** Tracked in the FixRegister
> and DependencyRegister. Until it lands, ask Daniel to drop the file in
> `_inbox/` and continue from step 5.

Both a recording and a transcript are preferred.

**Transcript-only is an unsolved case.** Daniel: *"If it's only transcript, that
is something we have to figure out."* Do not silently proceed as though a
transcript is equivalent to a recording — log which you got, and flag the
absence.

### 4. File the recording

Copy to `recordings/`, unchanged. Reference it from the session entry.

### 5. Attach the transcript

Attach to the session entry. Preserve it verbatim — it is the evidence every
later diagnosis cites, and a cleaned-up transcript cannot support a timestamped
observation.

### 6. Analyze and fill what you can

Read the transcript and populate what it actually supports.

**The highest-value field is the partner's feedback.** Daniel: *"In the session,
we usually get feedback from the person we're sessioning against."* That feedback
is spoken aloud in the recording and, historically, was lost unless he
transcribed it by hand — his existing notes carry `(Good) Feedback` and
`(Growth) Feedback` fields that are frequently null. Capturing it automatically
is the single biggest thing this skill does.

Rules while filling:
- Distinguish what the **partner said** from what **you observed** from what
  **Daniel reported**. These are different evidence classes and collapsing them
  corrupts every downstream diagnosis.
- Quote the partner rather than paraphrasing. His words carry the calibration.
- Leave anything the transcript does not support **empty**, and say what you
  could not determine.
- Do not fill `Overall Performance`. That is Daniel's judgment and his scale.

### 7. Hand off

Report what was logged and what is missing. Offer scoring as the next step —
do not run it.

## Pitfalls

- **Scoring inline.** The most likely drift. Intake ends at "logged and evidenced."
- **Normalizing his case names.** `Catch me or I go; HuDisney` stays exactly that.
- **Filing a recording under `casing/`.** It is top-level for a stated reason.
- **Treating transcript-only as complete.** An open problem, not a variant.
- **Inferring `Overall Performance`.** His scale, his call.
- **Designing schema.** Settled — copy the template. Do not improvise fields.
- **Renaming a note from the filesystem.** Obsidian only rewrites `[[wikilinks]]`
  when the rename happens *inside* Obsidian. A `mv` silently breaks every link
  pointing at that note, with no warning. If a note needs renaming, say so and
  let Daniel do it in the app.

## Verification

- [ ] The session entry exists in `casing/casing-session_log/` with his naming.
- [ ] No existing entry was overwritten.
- [ ] The recording is in `recordings/`, unmodified, and referenced.
- [ ] The transcript is attached verbatim.
- [ ] Partner feedback is quoted, attributed, and separated from your own
      observations.
- [ ] Every unfilled field is unfilled because the source did not support it —
      and you said which.
- [ ] Nothing was scored.

## Open — needs Daniel

- ~~Session-entry field schema.~~ RESOLVED 2026-08-29 — template written.
- Granola MCP install and test; then the transcript-only fallback.
- Does a behavioral-containing session also produce a `behaviorals/` record, or
  does one session entry cover both?
- Should intake write a worklog entry? Held until the worklog location is
  settled — the folder it would target does not currently exist.
