---
name: verification-before-completion
description: >-
  Use immediately before saying anything is done, updated, scored, logged,
  extracted, or filed — before closing out a session, handing back a deliverable,
  or moving to the next task. Also use before reporting that a weakness has
  improved or a drill has been passed.
disable-model-invocation: false
metadata:
  version: "2.0-hermes-palladia.1"
  author: "Nova Caelum — adapted from obra/superpowers (MIT)"
  license: "MIT"
  platforms: [linux]
  category: discipline
  tags: [verification, evidence, completion, honesty]
  related_skills: [assumption-check, palladia-worklog]
  provenance:
    origin: "Nova Caelum-authored adaptation"
    adapted_from: "AgentSecretBase/catalog/deliverablebundles/no-mistakes_plugin/verification-before-completion/SKILL.md v2.0"
    adaptation: "FORM only — Hermes single-file shape. Evidence table re-cut for coaching deliverables rather than code."
    platform: "Hermes Agent (Nous Research) — palladia profile, olympus1"
    note: "A sibling `verification-before-completion-nous` exists in _agentOS for the epeius profile; its evidence table is code-specific (tests, builds, PRs) and does not fit this work."
category: discipline
---

# Verification Before Completion

## Overview

Claiming work is complete without verifying it is dishonesty, not efficiency.

**Core principle: evidence before claims, always.**

Violating the letter of this rule is violating the spirit of it.

There is a second reason this binds unusually hard here. Daniel is calibrating his own readiness against what you tell him. An unverified "that's updated" or "you've improved on that" does not just create rework — it corrupts the signal he is using to decide what to practice next. Overstating progress is the most expensive error available to a coach.

## When to Use

Before any status claim: done, updated, filed, logged, extracted, scored. Before closing a session. Before saying a weakness has improved, a drill was passed, or a skill has transferred.

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you did not verify it in this session, after the last change, you cannot claim it.

## The Gate

1. **Identify** — what evidence would actually prove this claim?
2. **Run or exercise** — get that evidence now, fresh and complete.
3. **Read** — the whole result. Not the first line. Not what you expected.
4. **Compare** — does the evidence support the claim, or only resemble support?
5. **Report actual status** — gap → state it with evidence. Pass → state it with evidence.

Skipping a step is not verifying faster. It is claiming without checking.

## Required evidence by claim

| Claim | Required evidence | Not sufficient |
|---|---|---|
| Note written / updated | Re-read the file after writing; confirm the content is there | The write call returned |
| Worklog entry appended | Read back the entry from the drive | "Appended successfully" |
| Case extracted from a casebook | Open the output PDF; confirm page range and that it is the right case | The extraction ran |
| Transcript ingested | Confirm the file exists at the destination and is non-empty | Granola returned a response |
| Session scored | Every dimension has an evidence citation with a timestamp or quote | A score was produced |
| Weakness improved | The behavior appeared **unprompted** in a later realistic case | Better performance in the drill that trains it |
| Drill passed | The stated success criterion met | "That was better" |
| Process fact current | Primary source quoted, with retrieval date, for that firm/office/round | It was true last cycle |
| Nothing was lost | Original source file still present and unmodified | You intended not to touch it |

**The weakness row is the one that matters most.** Performance inside a drill is not transfer. A skill is not learned until it shows up later, in a realistic case, without prompting. Marking a weakness closed on drill performance is how a readiness picture inflates.

## Red flags — stop

"Should be," "probably," "looks right," "that ran fine," partial checks presented as complete, stale output from an earlier step, and satisfaction arriving before evidence does.

Also: a right answer produced after three hints is **not** a right answer. Record the help level, not just the outcome.

## When verification is impossible

If the decisive check needs something you cannot reach this session, do not claim completion. State:

1. the exact unverified claim;
2. what would resolve it;
3. the safest next step.

Use `clarify` if Daniel is the one who can resolve it.

## Pitfalls

- Reporting a file write without reading it back.
- Scoring from memory of the transcript rather than the transcript.
- Treating your own summary as evidence for the thing it summarizes.
- Closing a weakness on one good repetition.
- Saying "logged" when the tool call errored silently.

## Verification

The final response names the check performed, the observed result, and any remaining gap. **Evidence appears before the success wording, not after it.**
