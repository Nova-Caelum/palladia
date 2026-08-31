---
name: high-yield-drills
description: >-
  Use when Daniel wants to drill the high-yield material — when he says he is
  doing high-yield, asks to be quizzed on it, or asks for practice situations off
  the sheet. Not for case scoring, not for post-case debrief, not for drills that
  target a specific logged weakness.
disable-model-invocation: false
metadata:
  version: "0.0.1-template"
  status: "TEMPLATE — intentionally incomplete, to be written from live observation"
  author: "Nova Caelum / Chief-PM"
  license: "proprietary"
  platforms: [linux]
  category: casing
  tags: [drills, high-yield, retrieval-practice, template]
  related_skills: [hermes-skill-creator, warm-up, palladia-worklog]
  provenance:
    origin: "Nova Caelum-authored"
    platform: "Hermes Agent (Nous Research) — palladia profile, olympus1"
    design_source: "Daniel directive 2026-08-29 — hold as template, complete from today's live drilling session"
category: casing
---

# High-Yield Drills — TEMPLATE

> ## ⚠ THIS IS AN INTENTIONAL STUB
>
> This skill is **deliberately unfinished**. It is not an oversight, and it must
> not be treated as one.
>
> Daniel is doing high-yield drills **today (2026-08-29)** and will discover the
> real shape of this workflow by doing it. Specifying the procedure before that
> session would be guessing, and a guessed procedure is worse than an honest
> blank — it would get followed.
>
> **Your job during today's session is to OBSERVE, not to follow a procedure.**
> Capture what is listed under "What to capture while drilling" below. After the
> session, this skill gets written from that evidence using `hermes-skill-creator`.

## Overview

Drills off the **high-yield information sheet** — the material Daniel most needs
to have at instant recall.

## What we already know

Two things are settled and should survive into the finished skill:

1. **Situational, not flashcards.** The format Daniel specified, in his words:
   *"random situations that require us to know the relevant high-yield material —
   here is a situation, what do you need to know and what do you do?"*
   Recognition ("do you remember this term?") is the wrong shape. Retrieval under
   a realistic frame is the right one.

2. **It is drilling, not teaching.** The point is to make him produce the
   material under pressure, not to re-explain it to him.

## What is still open

Everything else. Named explicitly so the gaps are visible rather than filled in
by assumption:

- ~~`[BLANK — needs Daniel: where does the high-yield sheet live, and what shape is it in?]`~~
  **RESOLVED 2026-08-29.** It is `casing/user_notesheets/Casing_High Yield Notes.md`,
  converted from PDF with Daniel's authorization (the `.pdf` beside it is the
  archival original — read the `.md`). Drillable material it contains: the
  five-stage timing guide · framework rules (MECE, signpost, horizontal→vertical→deep) ·
  the percent↔fraction table (1/6, 1/7, 1/8, 1/9 families) · Rule of 72 vs NPV ·
  case-type triggers (Mergers→synergies, Acquisitions→valuations,
  Expansions/Acquisitions→alternatives) · the nine-formula reference recovered
  from an embedded slide · the "Greatest hits" case index · his Master Feedback list.
  His **Repeated, Outstanding Feedback** section is the highest-yield drill seed —
  it is what he has already been told repeatedly and still misses.
- `[BLANK — needs live observation: how many drills per session before fatigue?]`
- `[BLANK — needs live observation: does he want immediate feedback per drill, or a batch review at the end?]`
- `[BLANK — needs live observation: how is a drill scored — binary got-it/missed-it, or graded?]`
- `[BLANK — needs live observation: what does a good situational prompt look like vs a bad one?]`
- **Yes — a missed drill is evidence and feeds the weakness ledger** (Daniel 2026-08-29). It counts on the same standing thresholds as any other observation: **2 sightings → watch list, 3 → promoted** to a hard weakness that drives drills. A drill miss is not a lesser class of evidence than a case miss; it is cheaper and faster to collect, which makes it the more useful signal between sessions.

## What to capture while drilling

This is the operative section today. During the session, record — in PallaDrive,
via `palladia-worklog` — the following. This is the evidence the finished skill
will be written from.

**About the material:**
- Which items came up, and where on the sheet they live.
- Which items he answered instantly, which needed a beat, which he missed outright.
- Any item he got right but clearly reconstructed rather than recalled.

**About the format:**
- The exact wording of prompts that worked — that produced real retrieval effort.
- The exact wording of prompts that fell flat, and your read on why.
- Whether he asked to change the format mid-session, and to what.

**About the session shape:**
- Total drills run, and where his accuracy or energy dropped off.
- Whether he wanted feedback immediately or preferred to keep going.
- How long the session ran before he stopped.

**About what he said:**
- Any direct instruction he gave about how this should work. Quote it verbatim —
  do not paraphrase a design instruction.

## Pitfalls

- **Do not invent the procedure to fill this file.** If Daniel invokes this skill
  before it is written, say plainly that it is a template, run the session
  conversationally, and capture the observations above.
- **Do not turn drills into teaching.** If he misses one, note it and move on;
  the debrief is a separate moment.
- **Do not let capture interrupt the drilling.** Observation is secondary to him
  actually getting reps in. Capture between drills or at the end, never mid-rep.

## Verification

This skill is complete when:

- Every `[BLANK]` above is resolved from observation or from Daniel.
- The procedure section exists and was written from at least one real session.
- `status` in the metadata block is no longer `TEMPLATE`.
- It has been run once end-to-end against the real high-yield sheet.

Until all five hold, this file stays marked TEMPLATE.
