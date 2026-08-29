---
name: sequential-thinking
description: >-
  Use when a problem's full shape is not clear upfront — diagnosing a weakness
  with several plausible causes, deciding what to work on with limited time,
  or reasoning where the first answer may need revising. Also use when you
  notice you are defending a conclusion you reached early.
disable-model-invocation: false
metadata:
  version: "2.0-hermes-palladia.1"
  author: "Nova Caelum"
  license: "proprietary"
  platforms: [linux]
  category: discipline
  tags: [reasoning, revision, branching, diagnosis]
  related_skills: [assumption-check, verification-before-completion]
  provenance:
    origin: "Nova Caelum-authored"
    adapted_from: "AgentSecretBase/catalog/deliverablebundles/no-mistakes_plugin/sequential-thinking/SKILL.md v2.0"
    adaptation: "FORM only. Source is written entirely against the sequential-thinking MCP tool; this version keeps the same three techniques and makes them work with or without it."
    platform: "Hermes Agent (Nous Research) — palladia profile, olympus1"
    dependency_note: "Full-fidelity use needs the sequential_thinking MCP. Whether Palladia keeps it is an open decision — see config-desired-state.yaml. The discipline below works without it; the tool makes revision and branching explicit and inspectable."
category: discipline
---

# Sequential Thinking

## Overview

Three techniques — **revision**, **branching**, and **extension** — that stop reasoning from running in a straight line to the first plausible answer.

They matter here because diagnosis is the highest-leverage thing you do, and diagnosis is exactly where linear reasoning fails. A symptom has several possible causes. The first one that fits is not necessarily the one that is true, and committing to it early produces a confident, well-argued, wrong prescription.

**Tooling.** Where the `sequential_thinking` MCP is available, use it — it makes each step, revision, and branch explicit and inspectable. Where it is not, run the same discipline in your own reasoning and *state the moves out loud* ("I'm revising thought 3 — the evidence contradicts it"). The techniques are the skill; the tool is a convenience.

## When to Use

Diagnosing a weakness with more than one plausible root cause. Deciding what to prioritise when time is short. Any reasoning where the first answer may need overturning. **And the tell: when you notice you are defending a conclusion rather than testing it.**

Skip it for a direct question with a direct answer. Structured reasoning about a simple thing is theatre.

---

## Revision — when the evidence turns

Revise an earlier step when:

1. **New information contradicts it.** You concluded the problem was structuring; the transcript shows the structure was fine and the synthesis was rushed.
2. **Deeper understanding emerges.** The first read was shallow.
3. **Later findings need to update earlier ones.** Step 8 changes what step 3 meant.

Say it explicitly: *"Revising my earlier read — I said the issue was math accuracy, but the calculations were all correct. The failure was not connecting them to the objective."*

**Do not quietly replace an earlier conclusion.** The revision is itself information — it tells Daniel which of your reads survived contact with evidence.

## Branching — when there is more than one live explanation

Branch when:

1. **Competing explanations exist.** Structure vs. time pressure vs. note-taking. Evaluate each rather than picking the first.
2. **A sub-question must be settled first.** "Before I can diagnose the recommendation, I need to establish whether he had the numbers in front of him."
3. **A tangent would clutter the main line** but has to be resolved.

Name the branches, work them, then **return and synthesise**. A branch you never close is a loose end, not an insight.

This is the direct antidote to the single-cause reflex. A long recommendation could come from no governing question, weak prioritisation, missing intermediate synthesis, fear of committing, poor notes, or thin evidence — six branches, and only one is usually true.

## Extension — when the problem is bigger than you scoped

If you planned three steps and are at step three with the problem still open, **extend**. Do not force a conclusion to fit the budget you guessed at the start.

The failure this prevents is a premature confident answer, which is worse than an honest "this needs more looking at."

---

## Anti-pattern: linear-only

Using the technique as a numbered list is not using it:

> 1. Read the transcript · 2. Note the errors · 3. Give feedback

If your reasoning never revises, never branches, and never extends, it is a to-do list wearing a method's name. The value is entirely in the moves that change direction.

## Worked shape — diagnosing a weak recommendation

```
1  Hypothesis: the recommendation was unstructured.
2  Checking transcript — the structure was stated clearly up front. Revising.
3  (revises 1) Structure was fine. The problem is downstream.
4  Two live explanations. Branching.
5  (branch: no-synthesis) He never summarised before recommending.
6  (branch: time-pressure) He was at 22 minutes with 3 left.
7  (branch: no-synthesis) Same gap in 2 of the last 3 cases — not situational.
8  (branch: time-pressure) Previous cases had time and showed the same gap. Ruled out.
9  Synthesis: missing intermediate synthesis, recurring. 3 sightings — promote it.
10 (extend) Need one more step: is this a habit or a notes problem?
```

Note step 8. The branch that got ruled out is why the diagnosis is trustworthy.

## Pitfalls

- Branching and never synthesising.
- Revising silently, so the record shows only the final answer.
- Using the structure on a question that needed one sentence.
- Extending forever instead of concluding.
- Treating the first well-argued explanation as the true one — argument quality is not evidence.

## Verification

Before acting on the reasoning: at least one alternative was genuinely considered and explicitly ruled out with a reason, every branch opened was closed, and any revision is visible in what you report rather than silently absorbed.
