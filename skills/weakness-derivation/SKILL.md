---
name: weakness-derivation
description: >-
  Use when asked what the pattern is across cases — "what do I keep getting
  wrong", "what should I work on", "find the trends", "update the ledger", or
  after new case notes land. Also use before building a study plan or a warm-up.
  Not for scoring a single case, not for a debrief of one session.
disable-model-invocation: false
category: casing
metadata:
  version: "0.1.0"
  author: "Nova Caelum / Chief-PM"
  license: "proprietary"
  platforms: [linux]
  tags: [weakness, ledger, trends, evidence, diagnosis]
  related_skills: [post-case-loop, case-scoring, warm-up, high-yield-drills]
  provenance:
    origin: "Nova Caelum-authored"
    platform: "Hermes Agent (Nous Research) — palladia profile, olympus1"
    design_source: "Specified by the first derivation run, 2026-08-29. Every rule below is a mistake that run either made or narrowly avoided. See WeaknessLedger_Palladia_ChiefPM_2026-08-29.md."
---

# Weakness derivation

## Overview

Read the whole case-note corpus, find what recurs, and produce a ranked ledger of
weaknesses with cited evidence and a drill for each.

This is the skill that turns a pile of session notes into a study plan. It is
**not** case scoring — that reads one case. This reads all of them and asks a
different question: *what survives across sessions?*

The output is a **prior**, not a diagnosis. It says what the record showed. Only
the next unprompted case says what is still true.

## When to use

- The user asks what they keep getting wrong, or what to work on next.
- New case notes have landed since the last pass.
- Before building a warm-up, a drill set, or a study plan — all three need to know
  the current bottleneck.
- The ledger is stale or missing.

**Not for:** scoring one case (`case-scoring`), debriefing one session
(`post-case-loop`), or generating drills once the weakness is already known
(`high-yield-drills`).

## Procedure

### 1. HARD GATE — filter to the user's own cases

> **Read only notes where `Activity == "Taken"`. Exclude every `Given` note.**

A `Given` note records the case the user *ran for someone else*. Its
`(Growth) Feedback` describes **the partner's** performance. Example from the
corpus: *"She pigeon-holed herself by focusing too deeply on operations
concerns…"* — that is not the user.

In the first pass, **7 of 36 notes were `Given`.** Including them would have
attributed other candidates' weaknesses to the user and corrupted every count
downstream. This filter is not optional and not a judgment call.

State the filter result explicitly: total notes, excluded count, derivation base.

### 2. Report the corpus date range before anything else

Print the oldest and newest note dates and how many fall in the current cycle.

If the corpus is stale — most notes older than the current recruiting cycle —
say so **before** presenting any finding, and label the output **priors, not a
current diagnosis**. In the first pass, 35 of 36 notes were nine months old and
the single current note had an empty feedback field. Presenting that as "your
current weaknesses" would have been false.

### 3. Extract sightings with citations

For each note in the base, read `(Growth) Feedback` and any takeaways field.
Record every distinct complaint as a sighting carrying:

- the **verbatim quote** — never a paraphrase
- the **case id and date**
- the note's `Overall Performance` and `Case Type`

**Evidence before diagnosis.** A sighting with no quote is not a sighting.

**Counting unit — UNRESOLVED, default conservative.** When one session states the
same complaint twice (growth field *and* takeaways), count it as **one** sighting,
not two. The corpus contains a real instance: `2025-10-30 Fire Proof` flags
forgetting competition in both fields. One partner, one day, one observation.
Flag the case to the user and ask; do not silently pick.

### 4. Group symptoms into causes — and label the inference

Several surface complaints usually share one root. Group them, then state the
inferred cause **explicitly marked as inference**, distinct from what the
feedback literally said. Never present your inference in the user's voice.

### 5. Apply thresholds

- **2 sightings → WATCH**
- **3 sightings → PROMOTED** — drives drills

### 6. Check currency before promoting — the rule that matters most

**Raw count is not recency, and currency wins.**

In the first pass, framework had the most sightings (14) but was visibly
resolving by the end — *"Best you did on a framework"*, *"much better on
framework"*. Brainstorm had fewer (11) but appeared in **all four final cases,
including both rated `Perfect`.**

> A weakness that survives the user's **best** performances is more current than
> one that dominated their worst.

For each promoted item, check the last several sessions:

- Still appearing in recent cases → **CURRENT**
- Sightings thinning, recent notes praising it → **COOLING** (keep, do not lead with)
- **Reversed** — recent `(Good) Feedback` now praises it → report it as
  **resolved**, never as weak

**The reversal rule is a safety rule.** Math accuracy was genuinely bad through
mid-November, then reversed: six consecutive notes praised it, leaving only speed
and narration. Telling the user their math is weak would have damaged confidence
over a solved problem. Check before you promote.

Rank by currency. Report the count ranking too when the two disagree — the
disagreement is itself a finding.

### 7. Mine `(Good) Feedback` as well

A strength that has **stopped appearing** is a signal. So is a strength that
appears constantly — it tells you what not to spend drill time on.

### 8. Name one or two bottlenecks, not twenty

Rank by what explains the most downstream damage, then say plainly which one or
two to work on and explicitly park the rest.

A long unranked list is the **exhaustive-critic failure**: it feels thorough,
lowers confidence, and gives no executable next step.

### 9. Attach a drill

Each promoted weakness gets one drill with a success criterion and a retest.
A weakness with no drill is an observation, not a plan.

## Pitfalls

- **Including `Given` notes.** The single most damaging error available here.
- **Ranking by raw count.** Produces a stale bottleneck and buries the live one.
- **Promoting a reversed weakness.** Actively harmful before an interview.
- **Presenting stale priors as a current diagnosis.**
- **Paraphrasing feedback.** The user's own words carry information yours do not.
- **Inventing vocabulary.** Use the corpus's own fields — `Overall Performance`,
  `(Growth) Feedback`, `Case Type`, `Activity`, `Partner Type`. Never substitute
  a framework's terms for the user's.
- **Inventing frontmatter or drive schema.** If a derived field has no home, say
  so and ask. Do not create structure.
- **Composite scores or invented precision.** No "7/10 ready."
- **Silently resolving the counting-unit ambiguity.**

## Verification

Before returning:

- [ ] `Activity == "Taken"` filter applied; totals and exclusions stated.
- [ ] Corpus date range reported; staleness labelled if present.
- [ ] Every sighting carries a verbatim quote, case id, and date.
- [ ] Root causes marked as inference.
- [ ] Currency checked on every promoted item; COOLING and reversed items labelled.
- [ ] Any reversed weakness reported as resolved, not weak.
- [ ] One or two bottlenecks named; the rest explicitly parked.
- [ ] Each promoted weakness has a drill, success criterion, and retest.
- [ ] No invented schema; no composite score.
