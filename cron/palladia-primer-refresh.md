# Cron job draft — `palladia-primer-refresh`

**Author:** ChiefPM · 2026-08-29
**Daniel reviewed:** no
**Status:** 🟡 **READY TO INSTALL — one blocker remains (see Open before install #1).** Source paths resolved against the finalized PallaDrive schema 2026-08-31; `enabled` flipped to `true`. Nothing has been created on `olympus1` yet — installation requires an on-host `hermes -p palladia cronjob` call.
**Authored using:** `../skills_library/cron-creator/SKILL.md` (dogfood run — friction notes at the bottom)
**Job class:** **DERIVATION** (Step 0). Regenerates an artifact from known local state; it discovers nothing. Ingredient 4b applies, 4a does not.
**Re-validated 2026-08-29** against the amended `cron-creator` after this dogfood run produced the discovery/derivation split. All nine ingredients now satisfied — see the checklist.
**Depends on:** the `palladia-primer` plugin (`../plugin_library/palladia-primer/`), which reads what this job writes.

---

## Purpose

Regenerate `PRIMER.md` on a schedule so the `palladia-primer` plugin's `pre_llm_call` hook injects current state rather than stale state.

> **Hook contract note (corrected 2026-08-31):** the injection hook is `pre_llm_call`, gated to the session's first turn — NOT `on_session_start`, whose return value Hermes ignores. See the plugin docstring.

This exists because `MEMORY.md` is capped at 2,200 characters and is frozen into the prompt at session start — mid-session writes do not appear until the next session. The primer is the mechanism that carries live state past that constraint. A primer that is not refreshed is worse than no primer, because it looks current.

---

## Job specification

```yaml
name: Palladia — Primer Refresh
profile: palladia
schedule:
  kind: cron
  expr: "0 10 * * *"          # 10:00 UTC daily — before Daniel's working day
enabled: true                  # ready; still requires an on-host install call
provider: openai-codex         # ingredient 8 — explicit pin, non-negotiable
model: gpt-5.6-terra
enabled_toolsets: [file]       # ingredient 9 — writes one file, reads the drive
context_from: []               # ingredient: NOT ['self'] — see trap note
deliver: local                 # silent file write; no Telegram push
job_class: derivation          # Step 0 — ingredient 4b applies, not 4a
output_path: "_system-files/core_text/PRIMER.md"
write_mode: replace            # 4b: whole-file replace is correct for derivation
state_file: null               # 4b jobs hold no dedupe state — see ingredient 4b
```

### Ingredient 4b — idempotency guarantee

**Running twice with no change to the source inputs produces a byte-identical artifact, apart from `generated_at`.**

Source inputs this artifact derives from — the complete set, nothing outside it:

1. The weakness ledger
2. The case session log (most recent entries)
3. The recorded upcoming-events entry, if one exists
4. The high-yield material

Paths resolved 2026-08-31 against the finalized schema — see `## Source paths` in the instruction below. Input 1 (weakness ledger) remains unresolved; see Open before install #1.

**Missing-input behavior differs from a discovery job.** A discovery job that cannot reach a source has missed a find and should stay silent. This job that cannot read one input still has three, so it produces a *degraded* artifact — and a degraded primer that looks whole is the failure mode. Hence the evidence bar below: mark the section stale, never carry the old value forward silently.

**Test:** run twice against unchanged inputs, diff the outputs, exclude `generated_at` and nothing else. A non-empty diff means a nondeterministic instruction.

### Why `deliver: local`

This job produces an artifact for another mechanism to consume, not a message for Daniel. A push notification every morning saying "primer refreshed" would be exactly the meta-commentary the skill bans. **The primer IS the delivery.**

### Why `context_from` is empty

`cron-creator`'s first architectural trap. A job that regenerates a formatted document must not be fed its own prior output — the model copies the shape of what was injected and the instruction stops landing. This job reads PallaDrive fresh every run. Observed live on another job: rewritten prompt, old output shape, two-day-stale date, 91% similar to the previous day.

---

## Instruction (draft)

> ## Why this job exists
>
> Created 2026-08-29. Palladia's `MEMORY.md` is capped at 2,200 characters and is frozen into her prompt at session start, so it cannot hold current state. `PRIMER.md` is injected fresh by the `palladia-primer` plugin's `pre_llm_call` hook on the first turn of each session and is the only mechanism that carries live recruiting state into her context. If this job stops, she silently coaches against a stale picture.
>
> ## Source paths
>
> 1. Weakness ledger — **see Open before install #1; no in-drive path yet.**
> 2. Case session log — `casing/casing-session_log/` (most recent entries by filename date)
> 3. Upcoming events — `Dashboard.md`
> 4. High-yield material — `casing/user_notesheets/Casing_High Yield Notes.md`
>
> ## Your task
>
> Regenerate `_system-files/core_text/PRIMER.md` in PallaDrive from current drive state. Read, do not guess:
>
> 1. The weakness ledger — open weaknesses, evidence counts, watch-list vs promoted status.
> 2. Recent case activity — the most recent entries in the case session log.
> 3. Upcoming events — the next interview or deadline, if one is recorded.
> 4. The high-yield material most relevant to what is currently weak.
>
> Write `generated_at` as the current UTC timestamp. Preserve the existing primer's section order exactly.
>
> ## Evidence bar
>
> Every line in the primer traces to a file you read this run. **If a section's source cannot be read, write the section as `[stale — source unreadable YYYY-MM-DD]` rather than carrying forward the previous value.** A silently-carried-forward value is indistinguishable from a current one, which is the failure this bar prevents.
>
> ## Failure behavior
>
> If PallaDrive is unreachable: **do not overwrite `PRIMER.md`.** Leave the last known good file in place and return `[SILENT]`. A stale primer with an old `generated_at` is recoverable — the hook surfaces the timestamp and Palladia flags it. A truncated or half-written primer is not.
>
> ## Output contract
>
> The template is the existing `_system-files/core_text/PRIMER.md`. **Read it at the start of the run and preserve its section order and frontmatter keys exactly.** Do not reproduce a template from memory — the file on disk is the only authority, so the two cannot drift.
>
> Hard cap: **6,000 characters** for the rendered file. This is not arbitrary —
> it matches `_MAX_CHARS = 6000` in the `palladia-primer` plugin, which truncates
> anything longer. The two MUST move together; a cron cap above the plugin's cap
> means silent truncation, below it means wasted headroom. (Was 2,000 — corrected
> 2026-08-31; the live PRIMER.md is 5,902 bytes, so 2,000 would have cut it in half.) The primer is injected into every session and competes with everything else for context; over-cap, cut the oldest recent-activity entries first, never the weaknesses.
>
> Structural assertion — the render is malformed and must not be written if any of these fail: frontmatter parses; `generated_at` is present and is this run's UTC timestamp; every section present in the template is present in the output.
>
> ## Delivery rule
>
> Your entire final response is exactly `[SILENT]`. The file write is the deliverable.
>
> **NEVER deliver run summaries, self-checks, or meta-commentary** ("Primer refreshed", "3 weaknesses updated", "Here's what I did"). That is noise. The primer IS the delivery.
>
> Never combine `[SILENT]` with content.

---

## Ingredient checklist

| # | Ingredient | Status |
|---|---|---|
| 1 | Stated reason the job exists | ✅ `## Why this job exists`, dated |
| 2 | No-op contract, exact `[SILENT]` token | ✅ |
| 3 | Meta-commentary ban, verbatim, in delivery section | ✅ |
| 0 | Job classified discovery vs derivation | ✅ **derivation**, stated in header and in `## Why this job exists` |
| 4a | Dedupe key (discovery only) | ➖ not applicable to a derivation job |
| 4b | Idempotency guarantee (derivation) | ✅ source-input set enumerated, write mode stated, diff test defined |
| 5 | Verification bar defaulting to reject | ✅ unreadable source → marked stale, not carried forward |
| 6 | Failure behavior for unreachable source | ✅ both state and delivery |
| 7 | Output contract — file form | ✅ template named by path (not inlined), cap + structural assertion below |
| 8 | Explicit `provider` / `model` pin | ✅ |
| 9 | Explicit `enabled_toolsets` | ✅ `[file]` |

---

## Dogfood friction — what `cron-creator` made awkward

Reported as instructed. Three real frictions, one of them a genuine gap in the skill.

> **✅ RESOLVED 2026-08-29 — frictions 1 and 2 are fixed in `cron-creator`.** Daniel approved the amendment. The skill now opens with a Step 0 discovery-vs-derivation classification; ingredient 4 split into 4a (dedupe key, discovery) and 4b (idempotency, derivation); ingredient 7 gained a file-output form that names the template by path instead of inlining it. This job was re-validated against the amended skill and now satisfies all nine ingredients with no N/A and no partial. Friction 3 remains open — it is a PallaDrive schema dependency, not a skill defect.
>
> The notes below are preserved as the record of what the dogfood run actually found. They are history, not outstanding work.

**1. Ingredient 4 assumes every job is a discovery job.** The dedupe-key requirement is written for jobs that *find new things* and must avoid re-reporting them. This job finds nothing — it regenerates a document from state that already exists. There is no stream of candidate items to key. I marked it N/A, but the skill says "a job missing any of 1–8 is invalid," so following it literally would have blocked a valid job.

**Recommended fix:** `cron-creator` should classify jobs as **discovery** (finds new items, needs a dedupe key) or **derivation** (regenerates an artifact from known state, needs idempotency instead), and apply ingredient 4 only to the first. The derivation equivalent is: *"running twice in a row with no source change produces a byte-identical artifact."*

**2. Ingredient 7 assumes the output is a message.** "Numeric cap plus worked template" fits a brief pushed to Telegram. This job's output is a file whose template already exists as a separate artifact (`../core_text/PRIMER.md`) — restating it in the instruction would create two sources of truth that drift. I pointed at the artifact instead. The skill has no language for this.

**3. The state-file field has nowhere to point yet.** Left `[BLANK]` because PallaDrive's schema is Daniel's open design decision, and inventing a path would violate the standing constraint against drafting drive schema.

**What worked well:** ingredients 2, 3, 6, and 8 were immediately actionable and each caught something I would otherwise have left implicit — particularly 6, where "do not overwrite last known good state on fetch failure" is the difference between a recoverable stale primer and a corrupted one. The `context_from` trap check was the most valuable single item; I would have defaulted to `['self']` for a job that regenerates a document, which is precisely the configuration that is currently breaking another job on this host.

---

## Open before install

1. 🔴 **BLOCKER — the weakness ledger has no in-drive home.** Inputs 2-4 now resolve (schema finalized 2026-08-31), but `WeaknessLedger_Palladia_ChiefPM_2026-08-29.md` lives in the Nova Caelum vault, which `olympus1` cannot reach. The only in-drive weakness data is the summary table inside `PRIMER.md` itself — reading that to regenerate `PRIMER.md` is exactly the `context_from: ['self']` trap this job documents. Resolve by either (a) promoting a ledger file into PallaDrive, or (b) re-deriving weaknesses from `casing/casing-session_log/` each run via `weakness-derivation`. Daniel's call.
2. Whether 10:00 UTC is the right hour for Daniel's actual working rhythm.
3. Whether the primer refresh should also fire on demand, not only on schedule.
4. ~~`cron-creator` amendment per friction note 1~~ — **done 2026-08-29.**
