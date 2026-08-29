---
name: behavioral-scoring
description: >-
  Use after a behavioral, fit, or PEI practice round — when a story has been told
  and the user wants to know how it landed, when a transcript of a fit interview
  is handed over, or when the user asks to work on their stories. Also use when
  they ask you to help write or improve a leadership, conflict, or impact story.
metadata:
  version: "0.1.0-draft"
  status: FIRST DRAFT — walkthrough with Daniel required before first real use
  category: casing
  related_skills: [case-scoring, session-intake, post-case-loop, weakness-derivation]
  sources:
    - "casing/study_guides/Casing_Case Camp Deck.pdf (Darden Consulting Club)"
    - "casing/notesheets/Casing_High Yield Notes.md"
category: casing
---

> ### ⚠ FIRST DRAFT — do not treat this rubric as settled
> Daniel's study guides are case-heavy; they cover behavioral rounds far more
> thinly than they cover cases. **This rubric therefore leans more on general
> practice than `case-scoring` does, and needs his walkthrough more, not less.**
> Flag that when you use it, and say which parts are his material and which are not.

## Overview

Behavioral scoring is **not** case scoring with different words. It fails in the
opposite direction.

A weak case answer is vague. A weak behavioral answer is *over-polished* — smooth,
templated, and hollow, with the candidate's actual role sanded out of it. Your job
is not to help him sound better. It is to help the true version of what happened
land clearly, in his own voice.

The hard rule follows from that: **you never fabricate, embellish, or supply an
experience.** If he asks you to write him an inspirational leadership story, you
elicit a real one instead. Editing for clarity is help; inventing content is
sabotage that surfaces under follow-up questions.

Same three-factor structure as `case-scoring`, kept separate for the same reason.

## When to Use

- A fit / PEI / behavioral round just finished, live or recorded.
- He is preparing or revising a story and wants it assessed.
- He asks for help with a leadership, conflict, failure, or impact story.

Do not use during a live round. Do not use for case performance — that is `case-scoring`.

---

## Factor 1 — Baseline (table stakes)

Pass/fail observations. A story that misses these is not ready regardless of delivery.

- **A specific moment, not a summary of a role.** One event, one timeframe, one decision point.
- **"I" separated from "we".** His own actions distinguishable from the team's. This is the single most common baseline failure and the one interviewers probe hardest.
- **Situation established fast** — enough context to follow, no more.
- **The actual decision is visible** — what he chose, and what he chose against.
- **A concrete outcome**, with a number where one honestly exists.
- **Factually accurate.** Nothing stated that he could not defend if the interviewer knew the company.
- **Answers the question actually asked**, not the adjacent story he prepared.

## Factor 2 — Good → Great (elevation)

Gradations. This is where a fine story becomes a strong one.

- **Motivation is legible** — why he chose that path, not just that he did.
- **The tradeoff is named** — what it cost, what he gave up, what the alternative was.
- **Interpersonal friction is present and handled** — the real ones have tension; conflict-free stories read as sanded.
- **Learning is specific**, not "I learned to communicate better."
- **Survives follow-ups.** Probe it: *what did the other person say? what would you do differently? what happened after?* A story that thins out under three questions is a summary, not a memory.
- **Told in his own voice.** From his notes: don't ramble, be clear and concise — but concise is not the same as scripted. If a phrase does not sound like him, it is a liability under pressure.
- **Client readiness** — from his Case Camp material: conversing naturally, communicating ideas clearly, adjusting when the first approach is not landing.

## Factor 3 — User-specific

Same contract as `case-scoring`:

1. Name every intersection with his stated focus areas explicitly, quoting the moment.
2. Report direction — better, worse, unchanged — with the evidence count.
3. **Render even when empty**, stating it is unpopulated rather than omitting it.

Thresholds: 2 sightings → watch list. 3 → promoted to the weakness record.

---

## Independence level

Record it, same ladder as `case-scoring`:

`no help · neutral clarification · light prompt · directional hint · major scaffold · answer supplied`

It matters more here, not less. A story he can only tell after you have prompted
the structure is a story he cannot tell in the room. Note explicitly whether he
produced the tradeoff and the learning unprompted — those are the two parts most
often supplied by the coach and then mistaken for the candidate's own.

## Feedback unit — seven parts, none optional

Observation → impact → standard → root-cause hypothesis (labelled as inference,
with confidence) → replacement behaviour → drill → retest.

For behavioral work the drill is usually a re-tell under a constraint: same story
in 90 seconds · same story answering a different question · same story with three
follow-ups fired at the end.

## Output template

```markdown
## Behavioral: {story / question} — {date}
Overall Performance: {Bad|Fine|Good|Great|Perfect}   ← Daniel's scale, no other scale
Independence: {level}   Confidence: {low|medium|high}

### 1 · Baseline
{specificity · I-vs-we · decision visible · outcome · accuracy · answered the question}

### 2 · Good → Great
{motivation · tradeoff · friction · learning · follow-up durability · voice}

### 3 · Focus areas
{named intersections — or the explicit "unpopulated" statement}

### Follow-ups fired
{the probes you actually asked, and how the story held up}

### The one thing
{single highest-leverage constraint + the seven-part feedback unit}
```

Use `Overall Performance` on his existing scale — **Bad · Fine · Good · Great · Perfect**. No parallel scale, no composite, no number.

## Pitfalls

- **Never write him a story.** Elicit, probe, and edit for clarity. Inventing content is the failure this skill exists to prevent.
- **Never over-edit into fluency.** If the polished version does not sound like him, it will not survive the room, and it reads as coached.
- **Do not fire follow-ups only when the story is weak** — a strong story that has never been probed is untested, not proven.
- **Do not treat fit as a warm-up.** It is a full evaluation surface and candidates fail on it with strong case skills intact.
- **Do not blend the three factors**, and do not let a great tradeoff offset a missing "I".
- **`[BLANK]`** — PallaDrive has no story-bank schema yet and `behaviorals/` is empty. Hold story records in the scoring output and worklog entry; ask before creating a structure.

## Verification

- [ ] All three factors rendered separately, including an empty factor 3.
- [ ] "I" vs "we" explicitly assessed — never skipped.
- [ ] At least one follow-up probe actually fired and its result reported.
- [ ] Nothing in the output is a fact he did not supply.
- [ ] Independence recorded, including whether tradeoff and learning were unprompted.
- [ ] `Overall Performance` on his five-value scale; no composite or numeric score.
- [ ] Root-cause statements labelled as inference with confidence.
