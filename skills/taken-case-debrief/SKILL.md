---
name: taken-case-debrief
description: >-
  Use when Daniel wants to talk through a case he took — "let's debrief", "walk
  me through it", "what should I work on", "let's go over that one". Also when
  he accepts the offer at the end of post-case-taken. Conversational and
  live-with-him; not for writing up a session alone.
disable-model-invocation: false
metadata:
  version: "0.1.0"
  status: REPLACES post-case-loop — never run live
  author: "Nova Caelum / Chief-PM"
  license: "proprietary"
  platforms: [linux]
  category: casing
  tags: [debrief, coaching, interactive, drills, transfer]
  related_skills: [post-case-taken, weakness-derivation, warm-up, high-yield-drills]
  provenance:
    origin: "Nova Caelum-authored"
    platform: "Hermes Agent (Nous Research) — palladia profile, olympus1"
    design_source: "Daniel, verbally, 2026-08-30 — 'the what, the why, the how'"
    supersedes: "post-case-loop (retired 2026-08-30; single-session content moved to post-case-taken, cross-session promotion rule to weakness-derivation)"
category: casing
---

# Taken-Case Debrief

> **This is a conversation, not a document.** Every other casing skill produces
> a file while Daniel is elsewhere. This one runs **with him in the room** — you
> ask, he answers, and the two of you decide together what changes.
>
> If you find yourself writing a long analysis and presenting it, you are
> running the wrong skill. That was `post-case-taken`. This one is dialogue.

## Overview

The eval says what happened. The debrief works out **why**, and what to do about
it.

Its output is not understanding — it is **a changed drill queue.** If he finishes
and the queue looks exactly as it did before, either the case was clean or the
debrief failed, and you should say which.

## When to Use

- Daniel accepts the offer at the end of `post-case-taken`.
- He asks to go over a case — days later is fine, this does not have to follow
  the session.
- He wants to work a specific section rather than review the whole case.

**Not for:** writing up a session on your own (`post-case-taken`), the minutes
before a case (`warm-up`), or drilling the high-yield sheet (`high-yield-drills`).

**Entirely optional.** It is offered, never assumed. A clean case may not need one.

## Before you start

Read, this turn, not from memory:

- the session's `taken-case_eval-<Partner><YYYYMMDD>.md`
- the transcript it was written from
- `_wiki/drill-queue.md` — Open, so you know what is already being worked on
- the relevant `_wiki/` phase pages for whatever he wants to dig into

If the eval does not exist yet, run `post-case-taken` first. **Debriefing without
it means doing the analysis live, badly, from memory.**

## Procedure

### 1 · Ask what he wants out of it

One question. *"Whole case, or one section?"*

He may already know the thing that is bothering him. If so, go there and skip the
tour. A debrief that marches through five phases when he wanted to talk about the
brainstorm has wasted the part of this that matters — his attention.

### 2 · His read first, always

Even if he self-assessed in the eval, ask what he thinks **now.** Time changes
the read, and the delta between what he wrote right after and what he thinks
today is itself information.

**Never lead with your analysis.** Once he has heard it, his own read is gone for
that case and cannot be recovered.

### 3 · Work the mistakes — what, why, how

For each one that comes up, get through these. Ask; do not assert.

| Question | Why it matters |
|---|---|
| **What** actually happened? | Specific behavior, not a label |
| **Big or small?** | Broke the standard, or cost polish |
| **Common or one-off?** | A repeat is a transfer failure; a one-off is noise |
| **What was the deeper source?** | Three symptoms often share one cause |
| **What would better have looked like?** | Concrete and sayable, in his words |
| **Should it be redone?** | **His call, not yours** |

**The source question is the one worth slowing down for.** Signposting, a
line-by-line exhibit readout, and a lost brainstorm thread can look like three
problems and be one: structure decaying under load. Fixing the cause beats
drilling three symptoms — and finding it is the whole reason to have this
conversation instead of reading the eval.

### 4 · Work the wins with equal weight

Ask what went well and **what improved since last time.** Improvement is the
signal that a correction transferred, and it is the only evidence that anything
in this system works.

Do not treat this as the warm-up before the real conversation. A debrief that is
all deficits teaches him to dread it, and a skill he avoids is a skill that does
nothing.

### 5 · Change the queue — together

`_wiki/drill-queue.md` is the point of all this. In this session you may:

- **Add** a drill or a `coached-redo`. Tag `[daniel-directed]` when he asked for
  it, `[palladia-derived]` when you proposed it and he agreed.
- **Remove** an item he no longer wants. **He decides. Never argue an item back
  onto the list** — say your reasoning once, then do what he says.
- **Close** an item he says has transferred. Here, live, with him confirming, is
  the one place closing is legitimate.
- **Run a drill right now.** See below.

Say the queue state out loud at the end: what was added, removed, closed, and
what is still open. If Open now exceeds ~5, say so — a queue that long is a wish
list.

### 6 · Run a drill in-session, if he wants to

He decides. Offer once; do not push.

**`coached-redo`** — rerun one section live. Give the prompt or the exhibit exactly
as the original interviewer did, let him work it, then compare against what he did
the first time. **The comparison is the value.** Have the transcript open so the
first attempt is quotable rather than remembered.

**`drill`** — run the exercise, then check it against its own success criterion.

If it goes well, that is **not** proof the weakness is fixed. It transferred only
when it shows up unprompted in a real case. Update the item's retest date; do not
close it on a good rep in a safe setting.

### 7 · Close out

Say, in three lines or fewer: the one thing to carry into the next case, what
changed in the queue, and the next retest date.

Then append a `palladia-worklog` entry.

## Pitfalls

- **Presenting instead of asking.** The failure mode of this skill. If you are
  three paragraphs into a monologue, stop and ask a question.
- **Leading with your read.** Kills his self-assessment permanently for that case.
- **Marching through all five phases when he named one.** His attention is the
  scarce resource here.
- **Twenty observations and no plan.** Comprehensiveness is not diagnosis. Name
  the one or two causes that explain most of the rest and park the others out loud.
- **Treating symptoms as separate problems** without asking whether they share a
  source.
- **Arguing a removed drill back onto the queue.** Say it once. His call.
- **Closing an item on a good in-session rep.** It transferred when it appeared
  unprompted in a real case, not in a drill you scaffolded.
- **All deficits, no wins.** Teaches him to avoid the debrief.
- **Running this without the eval.** You will do the analysis live, from memory,
  badly.
- **Ending with the queue unchanged and not saying so.** Either the case was
  clean or the debrief failed — name which.

## Verification

- [ ] Eval, transcript, and `drill-queue.md` Open were read **this turn**.
- [ ] You asked what he wanted from the debrief before starting.
- [ ] His current read came before any analysis of yours.
- [ ] Every mistake worked got through: what · size · common-or-one-off · source
      · what better looks like · redo decision.
- [ ] The deeper-source question was asked, not skipped for a symptom list.
- [ ] Wins and improvements were covered with real weight.
- [ ] Queue changes were **his decisions**; additions carry source tags,
      success criteria, and retest dates.
- [ ] Any item closed was closed with him confirming, live.
- [ ] No item closed on the strength of an in-session rep alone.
- [ ] Queue state stated out loud at the end — or you said the queue is unchanged
      and why.
- [ ] Worklog entry appended.
