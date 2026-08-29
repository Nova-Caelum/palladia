---
name: hermes-skill-creator
description: >-
  Use when a procedure has now been run enough times to be worth writing down —
  when Daniel says to make this a skill, when you notice you have improvised the
  same multi-step workflow three or more times, or when a TEMPLATE-marked skill
  has collected enough live observation to be completed.
disable-model-invocation: false
metadata:
  version: "0.1.0"
  author: "Nova Caelum / Chief-PM"
  license: "proprietary"
  platforms: [linux]
  category: software-development
  tags: [meta, authoring, skills, evidence-threshold]
  related_skills: [high-yield-drills, palladia-worklog]
  provenance:
    origin: "Nova Caelum-authored"
    platform: "Hermes Agent (Nous Research) — palladia profile, olympus1"
    design_source: "Daniel directive 2026-08-29 — Palladia authors her own skills as patterns emerge"
    house_reference: "_agentOS/skills_library/hermes-platform/prod-caliber-prd-forge/SKILL.md"
category: software-development
---

# Skill Creator

## Overview

Write a new skill, or complete a TEMPLATE one, in the house format.

Hermes will write skills on its own after complex tasks. This skill makes that
deliberate instead of automatic, and holds the output to a standard. The reason
that matters: an automatically-generated skill records *what happened once*. A
skill worth keeping records *what happens repeatedly* — and the difference is
only visible if someone checks.

## When to Use

- Daniel says to turn something into a skill.
- You have improvised the same multi-step procedure **three or more times**.
- A skill marked `TEMPLATE` has accumulated enough observation to be written.

**Not** for: one-off tasks, restating something already covered by an existing
skill, or capturing a procedure you have only reasoned about rather than run.

## The evidence threshold — check this first

**Three real, observed instances. No speculative skills.**

Before writing anything, name the three. Cite the dates, the sessions, or the
worklog entries. If you cannot produce three, you do not have a skill yet — you
have a hypothesis. Log it and wait.

This is the single most important gate here. A skill written from one occurrence
encodes an accident as a rule, and every future run inherits it.

## Procedure

1. **Name the three instances.** Dates and worklog entry links. If this fails,
   stop.
2. **State the trigger in one sentence** — the observable condition under which
   this skill should fire. If you cannot say it in one sentence, the scope is
   wrong; split it or narrow it.
3. **Draft the frontmatter.** `name` and `description` are required. See the
   description rule below — it is the part most often gotten wrong.
4. **Write the body** in house structure: Overview → When to Use → Procedure →
   Pitfalls → Verification.
5. **Write Pitfalls from real failures only.** Every entry must trace to
   something that actually went wrong in one of the three instances. Imagined
   pitfalls are padding.
6. **Write Verification as a checkable condition**, not an aspiration. "Runs
   without error" is not verification. "The case note exists and its `case_id`
   matches the transcript filename" is.
7. **Check length.** 60–160 lines. Shorter than 60 usually means it belongs
   inside an existing skill; longer than 160 usually means it is two skills.
8. **Log it** via `palladia-worklog`, citing the three instances.

## The description rule — do not get this wrong

**`description` states TRIGGERING CONDITIONS ONLY. Never a workflow summary.
Maximum 400 characters.**

A description that summarizes the procedure creates a shortcut the agent will
take — it reads the summary, believes it now knows the skill, and never opens
the body. This is an observed failure in the Nova Caelum fleet: a description
reading "code review between tasks" caused an agent to run **one** review where
the body specified two. The body became documentation the agent skipped.

- **Right:** "Use when Daniel wants to drill the high-yield material — when he
  says he is doing high-yield, asks to be quizzed on it, or asks for practice
  situations off the sheet."
- **Wrong:** "Generates situational drills from the high-yield sheet, scores
  responses, and updates the weakness ledger." — that is the body. It will be
  read instead of the body.

Write when it fires. Never what it does.

## Pitfalls

- **Writing from one instance.** The threshold is three, and it is not a
  formality — it is what separates a rule from an accident.
- **Description as summary.** Covered above. It is the most common failure and
  the most costly, because it silently disables the body.
- **Scope creep into a second skill.** If the procedure branches into two
  genuinely different triggers, that is two skills. A skill with two triggers
  fires on the wrong one.
- **Aspirational Verification.** If the check cannot fail, it is not a check.
- **Rewriting a TEMPLATE from reasoning rather than from the captured
  observations.** The template exists precisely because the shape was unknown;
  filling it from inference defeats the point.

## Verification

A skill is done when:

- Three real instances are cited in the body or the worklog entry.
- `description` is ≤400 characters and contains no workflow summary.
- All five house sections are present.
- Body is 60–160 lines.
- Every Pitfall traces to an observed failure.
- Verification lists conditions that could actually fail.
- The frontmatter parses as valid YAML.
- It has been run once end-to-end.
