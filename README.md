<p align="center">
  <img src="assets/palladia.png" alt="Palladia" width="320">
</p>

<h1 align="center">Palladia</h1>

<p align="center">
  <em>A case-interview coach that remembers.</em><br>
  <sub>Nova Caelum &amp; Co. · agent on the Hermes platform</sub>
</p>

<p align="center">
  <img alt="status" src="https://img.shields.io/badge/status-in%20development-E8A33D?style=flat-square">
  <img alt="not launched" src="https://img.shields.io/badge/runtime-not%20launched-8C8C8C?style=flat-square">
  <img alt="updated" src="https://img.shields.io/badge/last%20updated-2026--08--29-1E3A5F?style=flat-square">
</p>

---

> ### 🚧 In development — 2026-08-29
>
> **Nothing in this repository is running yet.** This is the reviewed canonical package: identity, skills, plugin, config specification, and the runbook that installs them. The runtime it targets has not been rehabilitated. Treat every path, count, and gate here as *specified*, not *observed*, unless the file says otherwise.
>
> Two things are still unverified and are marked in place: Obsidian **Bases** syntax (drafted from docs, never watched render) and the `case-session-entry` schema (still being designed — skills that lack a home for a field **ask**, they do not invent one).

---

## What she is

Palladia is a personal MBB case-interview coach. She sits on a working folder of Markdown, PDFs, and Obsidian Bases — practice notes, casebooks, transcripts, partner feedback — and turns them into an improvement loop: intake a session, score it against anchored behavioural levels, derive weaknesses from evidence across cases, and drill the two that matter this week.

She is named for **Pallas Athena** and the **Palladium** — the statue that kept a city safe as long as it stood inside the walls.

**What she refuses to do is as designed as what she does.**

- **No composite scores.** No "8.2/10", no "73% ready". There is no public, complete, current MBB rubric, and a number implies a calibration against real interview decisions that nobody has. She uses anchored behavioural levels and states her confidence.
- **No invented evidence.** If a PDF is unreadable or a transcript is missing, she says which one and what she could not read.
- **Provenance is tracked, always** — what she observed, what the user reported, what a partner said, and what she inferred are four different things and stay four different things.
- **Weakness promotion is a rule, not a vibe.** Two sightings puts a pattern on the watch list. Three promotes it, and only then does it drive drills.
- **Derivation reads only sessions the user *took*.** Feedback on a case they *gave* describes their partner. Mixing the two silently poisons the diagnosis, so the filter is a hard gate in `weakness-derivation`.

She is deliberately **not** a fleet agent — no shared ops server, no company vault, her own local worklog — so she is exportable as a product rather than welded to Nova Caelum's internals.

---

## Why this repo exists

The first build failed at the only layer that mattered: **identity.** She was cloned from another agent and launched believing she *was* that agent. One `--clone-from` produced eight of the twenty logged defects, including a 128-skill inherited loadout nobody had declared.

The diagnosis was not "the clone was misconfigured." It was that the runtime had been mutated directly — profile creation, config commands, credential setup, gateway debugging — **without ever producing a reviewable desired-state package.** There was nothing to review, so nothing was reviewed.

This repository is that package. Every file was written, audited, adversarially reviewed by a second agent with shell access, corrected, and hash-pinned before anything was allowed near a runtime.

**It caught a real one.** The context-injection plugin was wired to `on_session_start`, returning `{"context": ...}`. Hermes **ignores** that hook's return value — and it fires *after* the system prompt is built. The plugin would have injected nothing, every session, forever, with no error and no signal. It is now on `pre_llm_call`, first-turn-gated, with a test that asserts it is *not* `on_session_start` so the mistake cannot come back quietly.

---

## Layout

| Path | What it holds |
|---|---|
| `identity/` | `SOUL.md` (who she is, how she reasons, what she refuses), `profile.yaml`, and the `MEMORY.md` / `USER.md` **seeds** — agent-owned after first install, never overwritten again |
| `skills/` | 16 purpose-built skills across `casing`, `discipline`, `palladia`, `automation`, `creative`, `software-development` |
| `plugins/palladia-primer/` | The context-injection plugin. `pre_llm_call`, first-turn-gated, 15/15 tests |
| `config/` | Desired-state **delta specification** — only settings that must differ from a default profile, each with its justification. Never copied over a live `config.yaml` |
| `reference/` | `SELF-MANAGEMENT.md` — read from the drive at runtime, not installed |
| `cron/` | Primer-refresh job specification. Deliberately **not** wired |
| `scripts/` | `gen_drive_map.py` — regenerates the drive map so she never reasons from a stale index |
| `primer/` | Generated working-state artifact. Seeded here; regenerated in place |
| `docs/` | The rehabilitation runbook, the hash manifest, and the drive's Bases conventions |

### The three-location model

**Workspace → canonical → runtime.** Files are authored and reviewed in a workspace, promoted to canonical (this repo, mirrored into the working drive), and materialized to a runtime that is never hand-edited.

**Canonical wins.** Runtime disagrees with canonical → the runtime is wrong, re-run the installer. A change made directly at runtime is drift; report it, never back-propagate it.

Two deliberate exceptions: `MEMORY.md` and `USER.md` are **`copy-once`**. Canonical holds the seed. After first install the agent owns them, and overwriting them would destroy everything she has learned.

---

## The primer, and why a plugin was necessary

Hermes memory files are capped at 2,200 characters and frozen into the prompt at session start — a mid-session write reaches disk but not the model until the next session. So memory cannot carry live state.

`palladia-primer` closes that gap. On the first turn of each session it reads a generated primer from the drive — current target, open weaknesses, recent case activity — and injects it into that turn.

It **fails loud, not soft.** Hermes logs and *skips* a hook that raises, which would make a crash invisible from inside the session: she would coach from stale state and nobody would know. So every failure path returns a visible in-context notice instead of raising, and the bare `except Exception` that makes that possible is load-bearing. The first-turn gate defaults to *inject* when the platform's flag is missing — degrading to visible over-injection rather than silent never-injection.

---

## Status

| | |
|---|---|
| **Package** | Reviewed, corrected, hash-pinned — `docs/PROMOTION-MANIFEST.md` |
| **Runtime** | **Not launched.** Rehabilitation runbook specified, not executed |
| **Skills** | 16 custom (here) + 17 inherited platform skills = 33 declared |
| **Plugin** | v0.2.0, 15/15 tests, not yet deployed or enabled |
| **Working drive** | Live, bidirectional sync verified |
| **Open** | Transcript-ingest MCP untested · image MCP not installed · `casebook-case-extract` needs a bounded extraction tool · Bases render unconfirmed · casebook guard hook is v2 |

`docs/RUNBOOK-rehabilitation.md` is the install path: quiesce → checksummed archive → verify canonical hashes → archive the contaminated trees → identity → config → skills → plugin → static gates → identity and primer integration tests → foreground gateway → managed service last. Every step names its gate and what happens when the gate fails. Three-tier rollback.

---

## Conventions worth stealing

A few of these generalize past this agent, and they are the reason the package is public.

- **A reviewable desired-state package before any runtime mutation.** If there is nothing to review, nothing gets reviewed.
- **Vendor docs are a hypothesis until tested.** The hook contract above was inferred from a convention and was wrong. Two independent confirmations — a source scan and the vendor's own catalog — settled it.
- **Fail loud when the platform fails silent.** Match the failure mode to what the surrounding system actually does, not to what the convention says.
- **Directional defaults.** When a flag might vanish, pick the default whose failure a human will *notice*.
- **Move, never delete.** Contaminated trees are archived, not removed. They are evidence.
- **Counts are gates, not notes.** "One extra skill, note and continue" is how 128 undeclared skills arrive.
- **Hash the promotion.** Promotion is complete when the target host reports the same hashes — not when the copy command exits 0.

---

<p align="center">
  <img src="assets/banner.png" alt="" width="100%">
</p>

<p align="center">
  <sub><strong>Nova Caelum &amp; Co.</strong> · in development · last updated 2026-08-29</sub>
</p>
