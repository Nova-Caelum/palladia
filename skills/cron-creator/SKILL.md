---
name: cron-creator
description: >-
  Use before creating a scheduled job with the `cronjob` tool, and before
  editing the instruction of any job that already exists. Also use when a
  running job reports success but delivers the wrong thing, or when asked to
  shorten or clean up a cron prompt.
disable-model-invocation: false
metadata:
  version: "0.1.0"
  author: "Nova Caelum / Chief-PM"
  license: "proprietary"
  platforms: [linux]
  category: automation
  tags: [cron, scheduling, output-contract, regression-guard]
  related_skills: [hermes-skill-creator, palladia-worklog]
  provenance:
    origin: "Nova Caelum-authored"
    platform: "Hermes Agent (Nous Research) — palladia profile, olympus1"
    design_source: "CronAudit_Olympus1_ChiefPM_2026-08-29.md — read-only audit of all 6 jobs across 4 profiles"
    exemplar: "NoVA Local LLM Hardware Scout (c26977bbf2dc) — Daniel's choice, 8/8 contract-clean"
category: automation
---

# Cron Creator

## Overview

Hermes schedules jobs through the native **`cronjob` tool**. This skill does not replace that tool — it governs what goes *into* a job before you call it.

Every requirement below is grounded in an observed failure on this host. None is theoretical.

**The exemplar is NoVA Local LLM Hardware Scout** — 8 of 8 runs contract-clean, 7 exact `[SILENT]`, one clean alert. Where a rule exceeds the exemplar it says so and says why.

## When to Use

Before creating any scheduled job. Before editing the instruction of an existing one. When a job reports `ok` but delivers the wrong artifact. When asked to shorten a cron prompt — **that request is the highest-risk moment this skill exists for.**

---

## Step 0 — classify the job first

Before touching the ingredient list, decide which of two kinds you are building. The ingredients are not identical for both, and applying the wrong set will reject a valid job.

| | **Discovery job** | **Derivation job** |
|---|---|---|
| What it does | Goes looking for candidates in a source that changes on its own — listings, releases, papers, prices | Regenerates an artifact from state that is already known and local |
| The risk | Reporting the same thing twice | Producing a different artifact from unchanged inputs |
| The control | A stable **dedupe key** (ingredient 4a) | **Idempotency** (ingredient 4b) |
| On this host | Independence Watch, Hardware Scout, Models to Watch, Forge Gate | `palladia-primer-refresh` |

**Say which kind in the job's `## Why this job exists` block.** A job that genuinely does both is two jobs; split it.

> *Amended 2026-08-29 after dogfooding this skill on `palladia-primer-refresh`: the original ingredient 4 demanded a dedupe key of every job, which would have blocked a valid derivation job that has no candidate stream to key on.*

---

## The nine required ingredients

A job missing any of 1–8 is invalid. Do not create it. Ingredient 4 has two forms — apply the one matching your Step 0 classification.

**1. A stated reason the job exists.**
Open with `## Why this job exists` — dated context plus the specific gap being closed. Without it a future rewriter cannot tell which sentences are load-bearing, and deletes them. This is the direct antidote to regression.

**2. A no-op contract using the platform's exact token.**
`[SILENT]` — nothing else. Never "produce an empty response": the harness recognises only `[SILENT]`, and a job on this host was written the other way and would have mis-fired every run. **Never combine `[SILENT]` with content** — that combination was delivered live on 2026-08-24 and violates the harness rule.

**3. An explicit ban on meta-commentary, in the delivery section, as its own rule.**
Use this wording:

> **NEVER deliver run summaries, self-checks, or meta-commentary** ("Briefs delivered: 1", "Signals logged: 8", "Here's what I did"). That is noise. The brief IS the delivery.

This is the single highest-value line in the audit. With the rule present: 9 runs, 0 leaks. Deleted: 4 of 29 runs shipped a status line *instead of* the brief. One burned **256,963 tokens and 100 seconds to deliver 63 characters** — while `last_status` read `ok` and `error` was `null`.

**Refuse to emit a job without this line.**

**4a. DISCOVERY JOBS — a named state file with an explicit dedupe KEY.**
Presence of dedupe is not enough — the key decides whether it works. The exemplar keys on *canonical listing URL or stable lot ID* and its contract file is verifiably advancing. A sibling job keys on free-text names and leaks duplicates: one item logged two days running, one model reported under three different names.

Specify four things: file path, the key, the re-alert threshold, and the write mode (`>>` append, never overwrite).

**4b. DERIVATION JOBS — a stated idempotency guarantee instead.**
There is no candidate stream, so there is nothing to key. The equivalent control is:

> **Running twice with no change to the source inputs produces a byte-identical artifact.**

Specify three things: the exact set of source inputs; the output path; and the write mode (whole-file replace is correct here, unlike 4a). Then state the missing-input behavior — a derivation job that loses one input still has the others, so it produces a *degraded* artifact rather than a missed find, and a degraded artifact that looks whole is the failure mode.

Test: run twice against unchanged inputs and diff. A non-empty diff means a nondeterministic instruction — usually a timestamp, a re-ranking, or an unpinned model. Exclude a single generated-at field from the diff, and nothing else.

**5. A verification bar that defaults to reject.**
Exemplar: *"Treat unclear availability or unclear memory architecture as non-qualifying until verified from the source."* Stronger pattern, from an archived job: an explicit **COUNTS / DOES NOT COUNT** list naming the things that *look* like evidence and are not.

**6. Explicit failure behavior when a source is unreachable.**
Two rules, both needed:
- State: *"Do not overwrite the last known good state if a source fetch fails."*
- Delivery: *"If web tools are down, do not send a brief this turn."*

Four of six jobs on this host specify nothing here.

**7. A hard output contract.**
The form depends on where the output goes.

- **Output is a message** (a brief pushed to Telegram or Discord): numeric cap **and** a worked template, inline in the instruction. A cap without a template gets ignored. A template without a cap grows: one job delivered 4,503 characters against its own three-sentence cap.
- **Output is a file** whose template already exists as a separate artifact: do not paste the template into the instruction — it will drift from the real one. **Name the template file by path and require the job to read it at run time.** Then state the cap that applies to the *rendered file*, and one structural assertion the artifact must satisfy (a required section, a required frontmatter field) so a malformed render is detectable without a human reading it.

Either way the cap is numeric. "Concise" is not a contract.

**8. Pin `provider` and `model` explicitly.**
Non-negotiable. Unpinned jobs are killed silently by the drift guard — *"Skipped to prevent unintended spend… this job is unpinned."* One job accumulated **122 consecutive failures**; another has **never had a single successful run in its life**.

⚠️ **This requirement exceeds the exemplar.** Hardware Scout is unpinned right now (snapshot only) and is exposed to exactly this. It has been lucky, not correct. Pin anyway.

**9. Declare `enabled_toolsets` explicitly.**
Never leave it null. A job needing `web` should not hold the full tool surface.

---

## Two architectural traps

**`context_from: ['self']` makes a prompt rewrite inert.**
The injected prior output outranks the current instruction. A job on this host was rewritten with a tight new contract and is still emitting the *old* job's title under a two-day-stale date, 91% similar to the previous day's output, because the model copies the shape of what was injected.

**Before editing any existing job, read its `context_from` first.** If it is `['self']` and the job emits a formatted brief, a prompt edit will not take — change the setting or accept it will not land. It is safe only where the previous output is always `[SILENT]`, because then there is no shape to imitate.

Prefer a state file over self-injection. A state file is explicit, bounded, and keyed; self-injection nests recursively — one 4,160-character instruction assembles into a 17,561-character prompt.

**Never assert an input the job cannot verify it received.**
One job's instruction claims its input is "injected above as context." Across 40 archived prompts that input never appears — and the job spent five weeks reporting a healthy pipeline as down. Make every job *check* for its input and say `[SILENT]`, or state the gap, when it is absent.

---

## Editing an existing job — the deletion diff

Regression on rewrite is the documented failure here, confirmed twice on the two highest-value jobs. One rewrite removed 79% of an instruction in a single edit, taking with it a recency gate anchored to a named incident, a rate limit, the meta-commentary ban, web-outage failure behavior, and worklog integration.

Before any edit lands, answer in writing:

1. What is the current instruction, verbatim?
2. Which rules am I deleting?
3. **For each deletion — what failure was that rule preventing?**
4. What is `context_from` set to? (See the trap above.)

If question 3 cannot be answered for a rule, **do not delete it.** Not understanding why a rule is there is the reason to keep it, not the reason to cut it.

Shortening is legitimate. The 2026-07-21 rewrite produced one genuine improvement — a flat append-only ledger that is a better dedupe primitive than the prose state file it replaced. The failure was not brevity. It was **keeping the mechanics and throwing away the judgment.**

---

## Pitfalls

- Trusting `last_status`, `error: null`, or `executions.db` `status: completed` as health. All three read clean on the run that delivered 63 characters in place of a brief. `executions.db` tracks the *fire process*, not the outcome.
- Writing a dedupe rule with no key.
- Leaving `enabled_toolsets` null "for now."
- Duplicate state files across profiles — one job on this host has two, and writes only one.
- Treating a job as working because it is enabled and recent.

## Verification

A job is not created until all of these hold:

0. The job is classified discovery or derivation, in writing, in its `## Why this job exists` block.
1. All nine ingredients present; ingredient 3 verbatim; ingredient 4 in the form matching the classification.
2. `provider` and `model` are non-null.
3. `context_from` is either unset, or set with an explicit written justification.
4. **Discovery:** the state file path exists or is created, and its key is named. **Derivation:** the source-input set is enumerated, and two runs against unchanged inputs diff clean apart from a single generated-at field.
5. **Health is measured on the delivered artifact.** After the first live run, read the actual output archive — not the status field — and confirm it matches the output contract.
6. For an edit: the deletion diff is written and every removed rule has a stated purpose.
