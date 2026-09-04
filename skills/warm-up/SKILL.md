---
name: warm-up
description: >-
  Use in the minutes before a live case, mock, or interview — when Daniel says he
  is about to case, has one starting soon, asks what to keep in mind, or asks to
  be warmed up. Not for post-case review and not for study sessions.
disable-model-invocation: false
metadata:
  version: "0.1.0"
  author: "Nova Caelum / Chief-PM"
  license: "proprietary"
  platforms: [linux]
  category: casing
  tags: [pre-case, recall, weakness-ledger, focus-areas]
  related_skills: [palladia-worklog, session-intake]
  provenance:
    origin: "Nova Caelum-authored"
    platform: "Hermes Agent (Nous Research) — palladia profile, olympus1"
    design_source: "MemoryAndWorklog_Palladia_ChiefPM_2026-08-29.md §3"
category: casing
---

# Warm-Up

## Overview

Five minutes before a case, give Daniel **three reminders**. Then stop.

This skill's entire value is that it is short enough to actually run when he is
nervous and about to start. A comprehensive pre-case briefing is a worse product
than three sharp lines, because he will skip the comprehensive one.

## When to Use

- Daniel says he has a case starting soon, or asks to be warmed up.
- Immediately before a mock, a peer case, a coaching session, or a real round.

**Not** for: post-case debrief, study sessions, drill work, or planning. Those
have their own paths.

## Procedure

1. **Read the current evidence.** Read it now — do not answer from your prompt
   snapshot, which is frozen at session start and is stale by construction.
   - `casing/casing-session_log/` — the recent case notes, especially each
     note's `(Growth) Feedback`. This is where recurring weaknesses actually
     live today.
   - `_wiki/drill-queue.md` — **read Open first.** `[VERIFIED 2026-08-30]` This
     is the live list of what Daniel is actually working on. An open item with a
     near retest date outranks a weakness you inferred from the notes: he already
     decided that one matters. `[daniel-directed]` items outrank
     `[palladia-derived]` ones of equal age.
     This read is what keeps the queue from being written and forgotten.
   - `casing/user_notesheets/Casing_Warm Up Page.md` — Daniel's real warm-up page,
     converted to Markdown 2026-08-29 with his authorization. Its four-item
     **HIGH YIELD CHECKLIST** (hypothesis at framework · horizontal the framework ·
     sign post the framework · set up the math before jumping in) is the fastest
     pre-case read there is — surface it verbatim when he is about to case.
     The `.pdf` beside it is the archival original; read the `.md`.
     **This is his authored material.** You may now write to it, but do not
     restructure it, and propose additions rather than making them silently.
2. **Read** Daniel's stated focus areas from `USER.md`.
3. **Select exactly three reminders:**
   - The top **two open weaknesses** by leverage — the ones most likely to change
     the outcome of this case, not the most recently recorded.
   - **One Daniel-specific signature-strength guardrail:** let one natural,
     case-linked point of warmth or personality appear when a genuine hook exists.
     This is not a scripted rapport line and not a personality drill; it is a
     state cue against anxiety/cognitive load suppressing one of Daniel's greatest
     strengths. Phrase it behaviorally, e.g. *“React like yourself once; do not
     sterilize the opening.”*
4. **Phrase each as a behavior, not a critique.** "Before speaking, write one
   answer sentence and two evidence bullets" — not "you rambled last time."
   He is about to perform; give him something to do, not something to feel.
5. **Stop.** Do not add context, encouragement, a framework, or a fourth item.

## Output shape

Three lines. No preamble, no sign-off.

```
1. <highest-leverage analytic behavior> — <the six-word reason, if it helps>
2. <second analytic behavior>
3. <signature-strength guardrail: natural connection, not scripted rapport>
```

If he asks for more, give more. Until then, three.

## Pitfalls

- **Scope creep.** The failure mode of this skill is becoming a briefing. Three
  items. If a fourth feels essential, it means the ledger needs pruning, not that
  this output needs to grow.
- **Recency bias.** The most recently recorded weakness is not automatically the
  highest-leverage one. Rank by expected impact on this case.
- **Answering from memory.** Your memory file is a pointer. Read the ledger.
- **Teaching.** This is not the moment. Note anything worth teaching, and raise it
  in the debrief.
- **Encouragement padding.** "You've got this" costs a line and buys nothing. He
  asked for reminders.

## Verification

- [ ] `drill-queue.md` Open, and the warm-up note, were read this turn, not recalled.
- [ ] Any open item with a near retest date was surfaced, or you said why not.
- [ ] The third line is the Daniel-specific signature-strength guardrail: natural warmth/personality when a genuine hook exists, never a scripted connection.
- [ ] Exactly three items returned.
- [ ] Each is a behavior he can execute, not an observation about the past.

