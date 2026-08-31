---
name: update-primer
description: >-
  Use when Daniel says "update the primer", when a case has just been scored, when a
  weakness changes status, when an interview date or target changes, when he adds or
  retires a top-of-mind item, or when the primer's generated_at is older than its
  staleness window. Also use before a session where current state must be right.
category: palladia
metadata:
  version: "0.1.0"
  author: "Daniel Eghdami, Chief-PM"
  status: "DRAFT — not installed"
  related_skills: [palladia-worklog, warm-up, weakness-derivation, case-scoring]
---

# Update Primer

## Overview

`PRIMER.md` is the only live-state surface you have. `MEMORY.md` is capped at 2,200
characters and frozen into the prompt at session start, so it cannot carry anything
that changes. The primer is injected fresh by the `palladia-primer` plugin's
`pre_llm_call` hook on the session's first turn, which
means it — and only it — determines whether you begin a session knowing what is
currently true.

This skill regenerates it. The primer is a **derived artifact**: every fact in it
must already exist in PallaDrive. If you find yourself typing something into the
primer that is not written down anywhere else, stop — write it to PallaDrive first,
then regenerate.

## When to Use

- Immediately after scoring a case.
- When a weakness crosses a threshold: 2 sightings → watch list, 3 → promoted.
- When an interview date, target firm, or office changes.
- When Daniel adds, edits, or retires a **Top of mind** item.
- When `generated_at` is older than `staleness_hours` and a session is starting.
- When Daniel says "update the primer" or "refresh what you know."

**Do not** use it to record something new. That is `palladia-worklog` or a PallaDrive
write. This skill only re-reads and re-renders.

## Procedure

1. **Read the current primer** and note its `generated_at`. You are replacing it, not
   appending to it.

2. **Re-derive each section from PallaDrive.** Never carry a value forward because it
   was in the previous primer — that is how a stale number survives ten regenerations.
   - *Active target* — from the office/application records.
   - *Open weaknesses* — from the weakness ledger. Include sightings, status, last-seen
     date, and retest date. Sort by status then recency.
   - *Recent case activity* — from `casing/casing-session_log/`. Most recent first.
   - *High-yield, most relevant now* — only items already promoted into the high-yield
     note. Do not promote here.

3. **Do not touch the Top of mind block.** It is Daniel's own text, and only Daniel
   edits it. Carry it forward byte-for-byte, including its own `Updated on` date.
   If you believe an item should be retired, say so in conversation and leave the
   block alone.

4. **Set `generated_at`** to the current time and keep `schema_version` accurate.

5. **Respect the size budget.** The primer is injected every session. If it is growing,
   cut the oldest low-signal rows rather than letting it sprawl — a primer nobody can
   read past is the same failure as no primer.

6. **Write it, then re-read it from disk** and confirm what you wrote is what is there.

## Pitfalls

- **Writing state into the primer instead of PallaDrive.** The primer is a read, not a
  record. Anything that exists only here is lost at the next regeneration.
- **Carrying a value forward without re-deriving it.** The most common way a primer
  becomes confidently wrong.
- **Editing Daniel's Top of mind list.** His words, his call, his date.
- **Promoting a weakness during a primer refresh.** Promotion happens in the ledger via
  `weakness-derivation`; the primer only reports what the ledger already says.
- **Leaving a `[BLANK]` in place when the data now exists.** A blank that outlived its
  cause reads as "no data" when the truth is "nobody looked."
- **Letting it grow.** Every character competes with the actual conversation.

## Verification

Before you call this done:

- [ ] `generated_at` is now, not the old value.
- [ ] Every non-blank fact traces to a specific PallaDrive file you read this run.
- [ ] The Top of mind block is byte-identical to before, its own date included.
- [ ] Weakness statuses match the ledger — 2 = watch, 3+ = promoted.
- [ ] No `[BLANK]` remains where PallaDrive now has the answer.
- [ ] You re-read the file from disk after writing it.
- [ ] It is no longer than it needs to be.
