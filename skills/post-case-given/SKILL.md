---
name: post-case-given
description: >-
  Use after Daniel has GIVEN a case to someone — when he says he just cased
  a person, asks to write up a session he ran, or a Given session folder exists
  with an unfilled recording or eval file. Not for cases he took, not for
  pre-case prep.
disable-model-invocation: false
metadata:
  version: "0.1.0-draft"
  status: COMPLETE — all three parts run end-to-end against the Ryan 2026-08-30 session
  author: "Nova Caelum / Chief-PM"
  license: "proprietary"
  platforms: [linux]
  category: casing
  tags: [given, post-case, transcript, granola, session-notes]
  related_skills: [granola-capture, pre-case-given, session-intake, case-scoring]
  provenance:
    origin: "Nova Caelum-authored"
    platform: "Hermes Agent (Nous Research) — palladia profile, olympus1"
    design_source: "Daniel, verbally, 2026-08-30, part by part; each part run live before being written"
    rubric_source: "Daniel's 2025 peer feedback sheet (Saumya Garg, 2025-10-23)"
    reference_artifact: "casing/session_notes/2026_08_30_Daniel X Ryan/session-recording_Ryan20260830.md"
category: casing
---

# Post-Case (Given)

> ## Reference run
> Every part below was executed against the **Ryan 2026-08-30** session before
> being written down. That session folder is the worked example — when this
> skill is ambiguous, go look at it.

## Overview

Daniel gave a case. This skill turns that into a record: the transcript and
summary pulled out of Granola and filed correctly, so the session can be
evaluated later instead of being remembered vaguely.

Three parts, in order: **capture** the session out of Granola · **evaluate** it
into Daniel's feedback sheet · **publish** it as a PDF for the candidate and a
row in the case log.

The output that matters is the PDF. Everything upstream exists so that document
is accurate, and the whole point of automating it is that Daniel used to write
it by hand and it was slow.

## When to Use

Daniel finished giving a case. Also when a `YYYY_MM_DD_Daniel X <Person>` folder
holds a recording file still at `Pending download`.

**Not for:** cases Daniel took (`session-intake`), pre-case prep
(`pre-case-given`), or scoring his own performance (`case-scoring`).

## Part 1 — Capture

### 1 · Invoke `granola-capture` first

**Do not call a Granola tool before invoking it.** That skill owns the retrieval
contract — union sweep, count assertion, direction detection, and three silent
failure modes, all observed live. A single `list_meetings` call returns a clean
response that is missing sessions.

The one you cannot engineer around: **a Private note is invisible to every
retrieval path.** If the expected session is not in the union, say so and name
Private as the likely cause. Do not report success.

### 2 · Locate the session folder — check before creating

`casing/session_notes/YYYY_MM_DD_Daniel X <Person>/` (underscores in the date).
**List the directory first.** Exactly one folder per person per date — duplicates
split a session's evidence and neither half is findable later.

### 3a · Large-transcript gate — split capture from judgment at 35 KB

`[OBSERVED 2026-08-31 — Will / HRCO]` A 43,891-character Granola transcript
caused the all-in-one capture → evaluation run to time out before any artifact
was written. Daniel set the guardrail at roughly 80% of that size: **35,000
characters (~35 KB for mostly ASCII transcript text).**

After retrieval, measure the transcript payload before doing any evaluation work.

- **Below 35,000 characters:** the normal end-to-end run is allowed.
- **At or above 35,000 characters:** capture is a separate bounded stage. Do not
  load the evaluation template, case-log template, rubric, or reference eval in
  the same context as the Granola pull. Write and verify the recording first,
  then start evaluation in a fresh stage from the saved file.
- In the evaluation stage, read the saved transcript in chunks of at most
  **12,000 characters**, split only at complete speaker-turn boundaries. Never
  split inside a turn and never summarize a chunk as a substitute for evidence.
- Record chunk ranges in working notes (for example, turns 1–80, 81–160) and
  verify there is no gap or overlap before writing feedback.

Granola does not expose ranged transcript retrieval. At ≥35 KB, **do not ask the
reasoning model to transform or write the MCP response** — even a capture-only
model stage can time out before its first write.

`[VERIFIED 2026-08-31 — Will / HRCO]` Hermes persists the complete MCP tool
result before the next model call in the active Palladia profile's local session
store (`state.db`, `messages` table). Use a deterministic script to:

1. select the latest `mcp__granola__get_meeting_transcript` and
   `mcp__granola__get_meetings` tool rows containing the exact meeting UUID;
2. JSON-decode the stored tool wrapper and transcript payload mechanically;
3. split only on source speaker labels and replace `Me` / `Them` with the named
   speakers;
4. write the recording directly; and
5. reconstruct the source transcript from the written turns and require an
   **exact character-for-character match** with the decoded Granola transcript.

The local store is a recovery surface, not coaching evidence: read it only to
recover the already-returned MCP payload. Do not modify the database. If the
exact-match check fails, the capture is invalid and evaluation does not begin.

Only after that mechanical capture verifies should evaluation start in a fresh
stage from chunked reads of the saved file.

### 3 · Fill the recording file

Target: `session-recording_<Person><YYYYMMDD>.md`, from
`_meta/template_library/session-notes_template/YYYY_MM_DD_Daniel X Partner/session-recording_TEMPLATE.md`.

`[LOCKED]` **`session-recording_Ryan20260830.md` is the reference shape.** If the
template and that file ever disagree, Ryan's file wins.

Load per `granola-capture` Step 3: summary into `## Granola Summary:`, verbatim
transcript into `## Full Transcript:`, labels normalized, header status and
Granola ID filled.

**Only the label changes.** Transcript wording is never tidied or summarized —
it is evidence, and Part 2 is written against it.

### 4 · Flip status only for what you actually pulled

A folder can hold one pulled file and one still pending; that is correct.
Never flip a status to assert a pull that did not happen.

## Part 2 — Evaluation

Target: `given-case_eval-<Person><YYYYMMDD>.md`, from
`_meta/template_library/session-notes_template/YYYY_MM_DD_Daniel X Partner/given-case_eval_TEMPLATE.md`. The structure is Daniel's
2025 peer feedback sheet.

**Shared identity header — required on both directions.** The Given evaluation must carry the same eight-field header as the Taken evaluation: `Case`, `Date`, `Case giver`, `Reviewer calibration`, `Case book / source`, `Source difficulty` (overall / quant / qual), `Transcript`, and `Individual case`. For Given, `Case giver` is Daniel and the transcript link is the unsuffixed recording. Populate every field from the source record; unresolved difficulty must be explicit, never silently blank.

### Surgical generation rule — one section per write

`[OBSERVED 2026-08-31 — Will / HRCO]` Chunked reading alone did not prevent a
502/524: the provider failed while generating the entire evaluation in one long
response. For any transcript ≥35 KB—or whenever a whole-evaluation generation
fails—build the evaluation incrementally:

1. Copy the complete template to the destination **once**.
2. Preserve every section heading as a unique patch anchor.
3. Generate and patch exactly one rubric section per bounded call: Presence,
   Behavioral, Prompt/CQ, Framework, Quant, Creativity, Coachability,
   Recommendation, Overall, Candidate read, Next steps.
4. Use targeted `patch` replacements anchored on that section's placeholder.
   Never rewrite the whole file after the initial template copy.
5. Read back the patched section immediately. A later failure leaves all prior
   sections intact and the remaining placeholders show exactly where to resume.
6. After all sections land, run whole-document checks for blank scores,
   attribution tags, separate candidate self-read, and complete source coverage.

Do not assemble independent section fragments by overwriting the destination.
The destination is one stable container; every addition after creation is
surgical.

### 5 · You write the feedback. Daniel writes the scores.

**Never fill a score or a rating.** Every `___ / 5`, every Great/Good/Fine cell,
and the total ship **blank** — Palladia does not grade a peer. You own the
**feedback prose**, which was the labor-intensive part and the reason this is
automated at all.

### 6 · Attribute every line. Not optional.

- **`[D]`** — Daniel said it in-session. Quote him.
- **`[C]`** — the candidate said it, usually self-assessment.
- **`[obs]`** — visible in the transcript, said by neither.

**Prefer `[D]`, heavily.** His coaching is the asset; your job is retrieval and
arrangement, not authorship. Reference-run split was 33 / 5 / 8 — that is the
target shape. Tags are never weighted differently; they exist so no reader has
to guess who said something.

### 7 · Work the transcript, not the summary

The summary is an index. The **coaching lives in the transcript** — Daniel's
end-of-session feedback runs several long unbroken turns. Read them in full.

Preserve his markers: `(+)` strength · `(-)` growth · `(~)` minor · `(---)`
emphatic · `-->` follow-on.

### 8 · Give the candidate's self-assessment its own section

"How do you think it went" is separate content and belongs in **Candidate's own
read**, never blended into Daniel's assessment. Where the two converge
independently, say so — that is a coachability signal.

### 9 · Let contradictions stand, then resolve them from the text

In the reference run Daniel said *"you didn't catch that it was brainstorm now"*
and the candidate answered *"I knew — I just lost it."* Those are different
failures: recognition versus retention-under-load. The transcript settles it.
**Surface the distinction rather than smoothing it** — it changes the drill.

### 9b · Remove template-only authoring comments

Before publishing, remove every HTML authoring comment copied from the template (`<!-- ... -->`) from the completed evaluation. These instructions belong in the template, not in the candidate-facing artifact, and can appear as large grey text in Obsidian's editor. Preserve all substantive feedback, attribution tags, blank Daniel-owned scores, and candidate self-assessment. Verify a search for `<!--|-->` returns zero matches in the final evaluation.

## Part 3 — Publish

### 10 · Export the PDF

```
python3 _system-files/scripts_library/md_to_pdf.py <eval>.md <eval>.pdf
```

Beside the markdown, in the session folder. **The candidate has no markdown
reader** — the PDF is what they actually receive. Verify it is non-empty and its
extracted text still shows the attribution tags.

### 11 · Add the row to the case log

`casing/casing-session_log/YYYY-MM-DD_<Case Name>_Given.md`, from
`_meta/template_library/case-session-entry.md`. **The `_Given` suffix is
required** — it disambiguates from the same case taken later.

**Copy the whole template, not only its frontmatter.** Preserve the template's
`## Sync` button block verbatim. Custom session prose may replace the instructional
comment or be added above the button, but it must never replace or omit the button.
A frontmatter-valid note without the sync block is incomplete.

Source it from the eval, not the transcript again. Populate what the evidence
supports; **leave the rest blank — a blank is honest, a guess corrupts every
count built on it.**

**Exception — the three difficulty fields are a required gate.** `Difficulty`,
`Qual Diff` and `Quant Diff` are the casebook's *published* ratings of the case,
which exist regardless of who was in the candidate seat — so they are populated on
a Given entry too, not blank-by-definition. Source order: the extracted case PDF,
then the exact casebook edition (bounded lookup — **never read a casebook whole**),
then the reviewer's own words, then an existing entry for the same case in the same
edition.

**Check the transcript for it every time.** On a Given session Daniel holds the
casebook, so the rating is often stated aloud — to the candidate, or in the
end-of-session exchange. Capture it verbatim. A rating spoken explicitly is
authoritative, not a fallback, and a speaker's own interpretation of a numeric
scale beats the arithmetic in the mapping guide.

Convert whatever scale the source uses into Daniel's five bands with
`_system-files/reference_docs/DifficultyMapping.md`. Read it; do not improvise a
conversion.

Finish either **sourced** — all three filled plus a one-line
`Difficulty source: …` note recording the raw values and the conversion — or
**unavailable**, marked `unresolved` with the reason inline and flagged to Daniel
in one line of your closing report. A silent blank is not a legal outcome.

Blank by definition on a Given session:

| Field | Why |
|---|---|
| `Overall Performance` | scores Daniel as candidate |
| `Counter` | tallies cases *taken* |
| `Weaknesses hit` / `Top of mind` | Daniel's ledger and Daniel's checklist — this session's weaknesses are the candidate's |

`(Growth) Feedback` is the weakness record and `weakness-derivation` reads it —
write it **behaviorally and specifically**. "Be more concise" is unusable;
"read Exhibit 1 line-by-line instead of synthesizing to a so-what" is usable.

Set `Casing` and `Behavioral` independently. A session that opened with a fit
question is `Y` and `Y`.

### 11b · Sync the exact case-log note to Google Sheet — REQUIRED

After the case-log note passes validation, run its sync rather than merely leaving the button behind.

1. Re-read the exact new `_Given` note and confirm `Synced` is not already `Y`; the downstream sheet append has no deduplication.
2. Require the same gates as the log workflow, including sourced or explicitly unavailable difficulty, one Sync block, and a complete payload identity.
3. Execute `_meta/template_library/_sync-this-case.md` against that exact note. If Obsidian/Templater is unavailable, perform the same POST using the script's field mapping and webhook reference; never substitute “most recent note.”
4. Treat only HTTP 2xx as success. On success, set `Synced: Y` and `Synced at:` to the real ISO timestamp, then re-read the note. On any other status, leave both fields unchanged and report the failure.
5. Do not describe the case as synced from the existence of the button or from a request being attempted. The HTTP result and updated frontmatter are the evidence.

Daniel's 2026-09-01 instruction makes this a standing step of the post-case workflow; no separate per-case confirmation is required.

### 12 · Report

Name the meeting ID, the three files written, and anything left blank on
purpose.

## Pitfalls

- **Calling a Granola tool before invoking `granola-capture`.** One unfiltered
  list call silently drops sessions. Observed, reproducible.
- **Reporting success when the union came up short.** The response looks clean.
  The count is the only thing that catches it.
- **Creating a second session folder for a date that already has one.** List first.
- **Collapsing a reciprocal pair.** Two people can case each other on the same
  day. That is two sessions and two files.
- **Editing transcript wording.** Labels only. Part 2 scores against this text.
- **Filling Part 2 from `case-scoring`.** Wrong direction — that rubric is for
  Daniel as candidate.
- **Scoring the candidate.** Not yours. Scores ship blank, always.
- **Writing feedback in your own voice when Daniel's words are right there.**
  Paraphrasing his coaching strips the thing that made these sheets useful.
- **Working from the Granola summary alone.** The quotable coaching is in the
  transcript's long end-of-session turns.
- **Running capture and evaluation in one context for a transcript ≥35 KB.**
  Observed timeout on Will / HRCO before any file was written. Make capture a
  bounded stage, then evaluate from chunked reads of the saved recording.
- **Blending the candidate's self-assessment into Daniel's.** Separate sections.
- **Smoothing a contradiction between what Daniel said and what the candidate
  said.** The disagreement is usually the finding.
- **Guessing a case-log field to avoid a blank.** A fabricated value silently
  corrupts every count built on it.
- **Omitting the `_Given` suffix** on the log filename.

## Verification

- [ ] `granola-capture` was invoked before any Granola tool call.
- [ ] Union sweep ran; count matched expectation, or the shortfall was escalated.
- [ ] `casing/session_notes/` was listed before any folder was created.
- [ ] **Exactly one** folder matches `YYYY_MM_DD_Daniel X <Person>`. State the count.
- [ ] `grep -cE '^\*\*(Me|Them):' <file>` returns **0**.
- [ ] Header carries a real Granola UUID and a status matching what happened.
- [ ] Both content sections non-empty; transcript wording unedited.
- [ ] For transcripts ≥35 KB, capture completed and was verified before evaluation began; evaluation chunk ranges cover the saved transcript without gaps or overlaps.
- [ ] No status flipped for a transcript that was not pulled.
- [ ] Given evaluation header contains all eight shared identity fields and matches the actual case, source, difficulty, transcript, and individual-case link.
- [ ] Final evaluation contains zero `<!--` or `-->` template markers.
- [ ] **Every score and rating in the eval is blank.**
- [ ] **Every feedback line carries `[D]`, `[C]`, or `[obs]`.** No untagged lines.
- [ ] `[D]` lines quote Daniel rather than paraphrase him.
- [ ] Candidate's self-assessment is in its own section.
- [ ] For section-wise generation, the destination template was created once;
      every later write was a targeted section patch, every patched section was
      read back, and no unresolved placeholder remains in a required section.
- [ ] PDF exists beside the markdown, is non-empty, and its extracted text still
      shows the attribution tags.
- [ ] Case-log entry exists with the `_Given` suffix and validates against
      `case-session-entry.md` — no missing fields, no invented ones.
- [ ] Case-log body contains exactly one `## Sync` section and the command
      `Templater: Insert _sync-this-case`; frontmatter-only validation is insufficient.
- [ ] Case-log sync returned HTTP 2xx; the exact `_Given` note now has `Synced: Y` and a real `Synced at` timestamp. If not, the failure was reported and the fields remain unchanged.
- [ ] `Overall Performance` and `Counter` are blank.
- [ ] `(Growth) Feedback` is behavioral and specific enough for
      `weakness-derivation` to consume.
