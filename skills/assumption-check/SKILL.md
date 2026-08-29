---
name: assumption-check
description: >-
  Use before asserting any fact you have not verified this session — a firm's
  process, a deadline, a format, a benchmark, a number, a date. Also use before
  a placement, scope, or build-vs-buy decision, and whenever "I assume X" or
  "I recall X" is the justification for what comes next.
disable-model-invocation: false
metadata:
  version: "2.0-hermes-palladia.1"
  author: "Nova Caelum"
  license: "proprietary"
  platforms: [linux]
  category: discipline
  tags: [verification, evidence, provenance, pre-flight]
  related_skills: [verification-before-completion, sequential-thinking]
  provenance:
    origin: "Nova Caelum-authored"
    adapted_from: "AgentSecretBase/catalog/deliverablebundles/no-mistakes_plugin/assumption-check/SKILL.md v2.0"
    adaptation: "FORM only — Hermes single-file shape, Hermes tool names. Content preserved."
    platform: "Hermes Agent (Nous Research) — palladia profile, olympus1"
    note: "A sibling `assumption-check-nous` exists in _agentOS for the epeius profile. That one is tuned for technical execution; this one is tuned for factual and process claims."
category: discipline
---

# Assumption Check — Validate Before You Build

## Overview

The failure this prevents: build advice on assumed information → the assumption was wrong → the advice was wrong, and Daniel acted on it. The cost is a wasted prep block, or worse, a wrong answer in a real interview. The prevention is minutes.

An assumption is anything not confirmed by a current source or a direct check **in this session**. Reasoning is hypothesis formation, not verification. "It probably works this way" is an assumption wearing a confident voice.

This matters more here than in most contexts, because recruiting information is *fragmented and dated*. There is no single current process. Firms run materially different formats by office, role, round, and channel — so a claim that is true somewhere is routinely false where Daniel is actually interviewing.

## When to Use

Before stating any firm's process, format, timeline, or rule. Before citing a number, benchmark, or date. Before a scope or format decision. Any time the justification for the next step is "I assume" or "I recall."

---

## Proactive mode — preferred

### 1. Surface assumptions explicitly

List every belief the next step rests on. Be specific:

> "I assume BCG New Jersey runs the same first round as BCG global" — unverified
> "I assume this deadline is still the published one" — unverified
> "I assume this casebook's page numbering matches its table of contents" — unverified

If none come to mind, look for: defaults, things "everyone knows," anything learned from an undated source, and anything about the *environment* rather than the subject.

### 2. Classify by confidence and load

For each: confidence `high | medium | low`, and **load-bearing** — does the advice become wrong if this is wrong?

Verify low-confidence **and** load-bearing first. A high-confidence assumption about stable, documented material can proceed with a note.

### 3. Verify, in this order

**Current primary source first.** The firm's own careers page, the invitation email, the assessment instructions. Find the specific statement — quote it, with its retrieval date. A homepage is not evidence of a specific behavior.

**Direct check second.** Read the actual file, open the actual tracker row, look at the actual note. Minimal and immediate.

**Web search as fallback.** Use the native `web_search` tool. Community and forum sources are *weaker* — they identify recurring patterns, never policy. Mark the distinction in the register.

Do not substitute reasoning for verification.

### 4. Document and proceed

Record what was actually found, especially where it differed from the assumption. Then proceed, referencing the verified fact and its date.

Any load-bearing assumption still unverified gets labeled a known risk **out loud**, not silently carried.

### 5. Escalate when verification is impossible

If a load-bearing assumption cannot be verified from this session — the source is behind a login, it is in an email you cannot read, it would take more than ~20 minutes to settle — do not proceed as if it were settled.

Use `clarify` to surface three things:
1. the exact unverified assumption;
2. what would resolve it (a document, a screenshot, a forwarded email);
3. your recommended next step.

Papering over an unverifiable load-bearing assumption is the failure this skill exists to prevent.

---

## Retroactive mode

When advice has already been given, or something went wrong:

1. Trace back the assumptions the advice rested on.
2. Identify which were never verified.
3. Verify them now.
4. Flag any that invalidate advice already acted on — **say so directly and promptly.**

Retroactive checks usually find the reasoning was sound. The value is converting silent risk into documented knowledge.

---

## Assumptions Register

```
| Assumption | Confidence | Load-bearing | Verified via | Actual |
|---|---|---|---|---|
| [claim] | low | yes | [source + date] | [what it actually says] |
```

For small calls, an inline note is enough. Populated registers become the process registry — they explain why advice is shaped as it is, and they are the first place to look when something changes.

## Pitfalls

- Treating a firm's global page as evidence about a specific office.
- Citing a number from memory because it "sounds right."
- Treating a forum post as policy.
- Continuing because verification is inconvenient.
- Calling something "likely" and advising anyway.
- Carrying an undated fact forward as if it were current.

## Verification

Before leaving this skill: every load-bearing assumption is either verified with a cited, dated source, or explicitly marked unverified with the advice narrowed or paused accordingly.
