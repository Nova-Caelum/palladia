---
name: post-case-taken
description: >-
  Use after Daniel has TAKEN a case — when he says he just cased, just got
  cased by someone, wants a session he solved written up, or a Taken session
  file sits unfilled. Not for cases he gave, not for selecting a case.
disable-model-invocation: false
metadata:
  version: "0.1.0-draft"
  status: PARTS 1-3 SPECIFIED — never run live; cold start on Tier 3 until the first sessions are derived
  author: "Nova Caelum / Chief-PM"
  license: "proprietary"
  platforms: [linux]
  category: casing
  tags: [taken, post-case, transcript, granola, self-assessment]
  related_skills: [granola-capture, taken-case-debrief, post-case-given, weakness-derivation, warm-up]
  provenance:
    origin: "Nova Caelum-authored"
    platform: "Hermes Agent (Nous Research) — palladia profile, olympus1"
    design_source: "Daniel, verbally, 2026-08-30 — capture half mirrors post-case-given"
category: casing
---

# Post-Case (Taken)

> ## The rubric is not in this skill
> Five phases, three tiers, and every standard live in `_wiki/`. This skill is
> **procedure**; the wiki is the **standard**; the template is the **container**.
> Read the phase page before assessing that phase. If this skill and the wiki
> ever disagree, the wiki wins.

## Overview

Daniel took a case. Someone else gave it to him, and this time he is the one
being assessed.

Capture is mechanically identical to the given side — same MCP, same failure
modes, same template. **What changes is direction**, and direction determines
who every label refers to. Getting it backwards silently inverts the record:
the giver's coaching gets attributed to Daniel, and his answers get read as
questions.

**Case selection is not part of this workflow.** Daniel rarely picks the cases
he takes — a partner brings one. If a selection step is ever needed it is a
separate, modular concern. Assume the case has already happened.

## When to Use

Daniel finished taking a case, or a taken-side session file sits at
`Pending download`.

**Not for:** cases he gave (`post-case-given`), pre-case prep for giving
(`pre-case-given`), or drilling (`high-yield-drills`).

## Part 1 — Capture

### 1 · Invoke `granola-capture` first

**Do not call a Granola tool before invoking it.** That skill owns the retrieval
contract — union sweep across folders and workspaces, count assertion, direction
detection, and three silent failure modes. A single `list_meetings` call returns
a clean response that is missing sessions.

The one you cannot engineer around: **a Private note is invisible to every
retrieval path.** If the expected session is not in the union, say so and name
Private as the likely cause. Do not report success.

### 2 · Confirm direction before anything else

This is the step that distinguishes this skill from `post-case-given`, and it
is the easiest thing to get wrong.

Daniel's titles carry the signal — `Taking` / `Taken` / `<Person> x Daniel` mean
he received the case. **Confirm it against the note body anyway:** in a taken
session the coaching flows *toward Daniel*, and the case prompt is read *to* him.

**A reciprocal pair can exist on one day.** On 2026-08-30 Ryan gave Daniel a
case at 12:00 PM and Daniel gave Ryan one at 1:11 PM. Same two people, same
date, two separate sessions, two separate files. **Never collapse them, and
never let one direction's transcript land in the other's file.**

### 3 · Locate the session folder — check before creating

`casing/session_notes/YYYY_MM_DD_Daniel X <Partner>/` (underscores in the date).
**List the directory first.** Exactly one folder per partner per date.

When that date already holds a session in the other direction, both live in the
same dated folder — they are one sitting with two halves, not two sittings.

### 3a · Large-transcript gate — split capture from judgment at 35 KB

`[OBSERVED 2026-08-31 — Will / HRCO given-side run; shared failure mode]` A
43,891-character Granola transcript caused an all-in-one capture → evaluation
run to time out before any artifact was written. Daniel set the guardrail at
roughly 80% of that size: **35,000 characters (~35 KB for mostly ASCII
transcript text).** The same context risk applies on the taken side.

After retrieval, measure the transcript payload before doing any evaluation work.

- **Below 35,000 characters:** the normal end-to-end run is allowed.
- **At or above 35,000 characters:** capture is a separate bounded stage. Do not
  load the case PDF, five phase pages, weakness record, eval template, or case-log
  template in the same context as the Granola pull. Write and verify the recording
  first, then start Part 2 in a fresh stage from the saved file.
- In Part 2, read the saved transcript in chunks of at most **12,000 characters**,
  split only at complete speaker-turn boundaries. Never split inside a turn and
  never replace a chunk with a summary.
- Record chunk ranges in working notes and verify there is no gap or overlap
  before filling the attestation or writing `[P]` content.

Granola does not expose ranged transcript retrieval. At ≥35 KB, **do not ask the
reasoning model to transform or write the MCP response** — even a capture-only
model stage can time out before its first write.

`[VERIFIED 2026-08-31 — Will / HRCO; then Will and Chris taken captures]` Hermes
persists the complete MCP tool result before the next model call in the active
Palladia profile's local session store (`state.db`, `messages` table). Use a
deterministic script to:

1. select the latest `mcp__granola__get_meeting_transcript` and
   `mcp__granola__get_meetings` tool rows containing the exact meeting UUID;
2. JSON-decode the stored tool wrapper and transcript payload mechanically;
3. split only on source speaker labels and replace `Me` / `Them` with the named
   speakers;
4. write the recording directly; and
5. reconstruct the source transcript from the written turns and require an
   **exact character-for-character match** with the decoded Granola transcript.

The local store is a recovery surface, not coaching evidence: read it only to
recover the already-returned MCP payload. Do not modify the database. If Granola
returned an undifferentiated stream, preserve it as such and document the
speaker-attribution limit; never invent turns. If the exact-match check fails,
the capture is invalid and Part 2 does not begin.

Only after that mechanical capture verifies should Part 2 start in a fresh stage
from chunked reads of the saved file.

### 4 · Fill the recording file

Write to **`session-recording_<Partner><YYYYMMDD>_Taken.md`**.

`[VERIFIED 2026-08-31]` **The `_Taken` suffix is required and load-bearing.** The
unsuffixed name is the *given*-side file. On a reciprocal day both directions
live in one folder, and without the suffix the taken capture overwrites the given
transcript. Mirrors the `_Taken` / `_Given` suffix on case-log filenames, so one
convention covers both.

From `_meta/template_library/session-notes_template/YYYY_MM_DD_Daniel X Partner/session-recording_TEMPLATE.md`
— **the same template the given side uses.** Structure does not change with
direction; only header fields do.

Set them deliberately:

| Field | Taken value |
|---|---|
| `Activity` | `Taken` |
| `Candidate` | **Daniel** |
| `Case giver` | the partner |
| `Speaker labels` | source `Me` = Daniel · source `Them` = **the case giver** |

`Me` is always Daniel — he is the note-taker either way. **`Them` is what
flips.** On a given case `Them` is the candidate; here `Them` is the person
asking the questions.

Then load per `granola-capture` Step 3: summary into `## Granola Summary:`,
verbatim transcript into `## Full Transcript:`, header status and Granola ID
filled.

**Only the label changes.** Transcript wording is never tidied or summarized —
it is evidence, and Part 2 will be written against it.

### 5 · Keep assessment out of this file

Scores, self-assessment, feedback, and takeaways **do not belong
in the recording document.** They go to the taken-side eval sheet.

This separation is not cosmetic. The recording is *evidence*; the eval is
*judgment*. Keeping them apart is what lets the eval be written against the
transcript instead of from memory.

### 6 · Flip status only for what you actually pulled

A folder can hold one pulled file and one still pending; that is correct and
common on reciprocal days. Never flip a status to assert a pull that did not
happen.

### 7 · Stop and report

Name the meeting ID, the file written, the direction you confirmed and how, and
anything the union sweep could not reach.

Then continue to Part 2.

## Part 2 — Evaluation

Target: `taken-case_eval-<Partner><YYYYMMDD>.md`, from `taken-case_eval_TEMPLATE.md`
in the folder template.

### Surgical generation rule — one section per write

`[OBSERVED 2026-08-31 — Will and Chris taken evaluations]` Chunked evidence
reading succeeded, but whole-evaluation generation timed out before any file was
written. For any transcript ≥35 KB—or whenever a whole-evaluation generation
fails—build the evaluation incrementally:

1. Copy the complete template to the destination **once**.
2. Fill §0 attestation first and §1 self-assessment second; verify both gates
   before any `[P]` section.
3. Generate and patch one bounded section per call: §2 reviewer feedback, each
   of the five phase subsections separately, §4 divergence,
   §5 takeaways/proposals, §6 drills, then §7 routing.
4. Use targeted `patch` replacements anchored on the unique section heading and
   its placeholder. Never rewrite the whole file after the initial copy.
5. Read back each patched section immediately. A later failure leaves prior
   sections intact and unresolved placeholders identify the exact resume point.
6. Only after every section is present run whole-document validation for voice
   tags, tier ratings, categorical-only performance vocabulary, help level,
   attestation, and drills.

Do not assemble section fragments by overwriting the destination. The evaluation
is one stable container; every addition after creation is surgical.

**Daniel is the subject here, not the assessor.**

The three voices are **not weighted equally, and yours is last:**

| Rank | Voice | Why |
|---|---|---|
| 1 | `[R]` the reviewer | They were **in the room.** They saw delivery, pauses, the paper, the recovery — evidence no transcript preserves. |
| 2 | `[D-self]` Daniel | His own read, written first and independently. |
| 3 | `[P]` Palladia | Supplements. Never overrides. |

**When your analysis disagrees with the reviewer, the reviewer wins** — unless the
transcript holds a specific, quotable contradiction, in which case surface both
rather than picking a side.

#### Authority and high-caliber reviewers

Daniel may explicitly set `Reviewer calibration: authority` or `high-caliber peer`.

- **Authority:** eyewitness and technical feedback both receive exceptional weight and may reopen a cooling weakness or establish the priority intervention when behaviorally specific. The case source still controls a direct factual contradiction.
- **High-caliber peer:** above an ordinary peer and heavily weighted; technical claims are still checked against the case source and baseline.
- **Named calibration, Daniel-set 2026-09-01:** Eric Sodero is `authority`—one of the top three casing authorities at Darden. Ning is `high-caliber peer`, the only current-cycle reviewer Daniel identified as close to Eric's caliber, but below Eric.

Authority affects priority and confidence, not sighting arithmetic: one session remains one sighting.

#### The exception — a less-experienced reviewer

Daniel sometimes cases with people newer than he is. **This is the exception, not
the rule.** When he sets `Reviewer calibration: developing` in the header, the
weighting **splits** rather than inverting:

| Kind of `[R]` observation | Weight under `developing` |
|---|---|
| **Eyewitness** — delivery, pace, presence, whether he was followable, where he lost them, how a recovery landed | **Full weight, always.** They were in the room; you were not. A newer reviewer sees these as well as anyone. |
| **Technical** — framework quality, MECE-ness, math correctness, whether a brainstorm was structured | **Below the standard.** The wiki is the authority and `[P]` outranks `[R]`. A newer reviewer can miss a gap, or praise something the standard would not. |

*"You lost me in the second bucket"* holds full weight from anyone.
*"Your framework was MECE"* gets checked against the wiki before it is accepted.

**Default is `peer`. You do not decide this**, and you never infer it from how
well someone gave the case. If a technical claim looks wrong and calibration is
unset, **ask** — do not quietly downgrade a person in a document he will read.

Your value is **coverage and routing, not verdicts:** catching what the reviewer
did not mention, placing every observation in the right tier, and checking it
against the standard. You are the analyst, not the judge.

### 8 · Confirm the case PDF exists, before reading anything else

The transcript records what was *said* about a number. The PDF shows what Daniel
was actually *looking at*. Exhibit analysis without it is guesswork.

- Present in `casing/individual_cases/<Case Name>/` → read it.
- Absent but the casebook is held → extract it via `casebook-case-extract`.
- Absent and the partner brought a case we do not hold → **proceed, and state the
  gap in the attestation.** Say plainly that exhibit analysis is weaker for it.

### 9 · Read before analyzing. This is a gate, not a suggestion.

Fill section 0 of the template **before writing a single `[P]` line.** Naming a
file is not evidence of having read it — the attestation requires **one specific
thing from each source, found this run:**

- `_wiki/Case Performance Baseline.md`
- the five phase pages: `Prompt and Clarifying Questions` · `Framework` ·
  `Exhibits and Math` · `Brainstorming` · `Conclusion and Recommendation`
- the Daniel-specific / weakness record
- the individual case PDF — **name an exhibit and what it showed**
- the full transcript

This gate exists because the reading step is the one that gets skipped, and an
assessment written from a remembered rubric is an assessment of the wrong thing.

### 9b · Source-data defects — disqualify the insight, not the reviewer

**When the case giver states a fact the case materials contradict, every `[R]`
insight that DEPENDS on that fact is disqualified. Nothing else is.**

This is surgical, not blanket. A reviewer wrong about one figure is still a
reliable eyewitness on delivery, structure, and everything that did not rest on
it. Discarding their whole read because one number was wrong throws away the
highest-weighted voice in the document.

Procedure:

1. Name the contradiction: what was said, what the case materials state, cite both.
2. Trace forward — which conclusions rest on it? Usually the recommendation and
   any sizing that used it as a denominator.
3. **Mark exactly those `[R]` lines `[R–disqualified]`** with a one-line reason.
   Leave every other `[R]` line at full weight.
4. Assess the affected phase on **the reasoning Daniel applied to the figure he
   held**, not against the case's intended answer. He cannot be marked down for
   an input he was given.
5. Do not let it bleed into neighbouring tiers. Arithmetic that was correct stays
   correct.

**This is the one place `[P]` outranks `[R]` outright** — the case's own answer
key is a document, not an opinion, and it is the tiebreaker.

Observed 2026-08-30: the giver stated $500 billion where the case states 500
million SAR. That 1000× error turned a 17.1% result into 0.017% and inverted the
recommendation. Daniel's arithmetic was exactly right; only the conclusion drawn
from the bad denominator was affected.

### 10 · HALT if Daniel has not self-assessed

Section 1 must be filled **before** any `[P]` content.

**Check the transcript first.** Daniel usually self-assesses out loud in the
session — the giver asks "how do you think that went" and he answers. That IS
the self-assessment: it is his, it is unprompted by any analysis of yours, and it
is better evidence than a later recollection. Quote it and tag it `[D-self]`.

Only if the transcript has no such moment do you stop and ask him.

This is mechanical, not stylistic. If Palladia's read lands first it anchors his,
and the self-assessment stops being independent evidence — which is the entire
reason the section is ordered first.

### 11 · Assess five phases × three tiers

For each phase the case reached, rate and comment on all three:

| Tier | Rating vocabulary | What it answers |
|---|---|---|
| Baseline | met · partially met · missed · not observable | Did this clear the bar? |
| Good → Great | demonstrated · opportunity · not observable | What separates it from excellent? |
| Daniel-specific | hit · missed · not applicable · cold start | Did it touch what he is working on? |

**No numeric or composite scores.** The baseline doc bans them deliberately — it
is a coaching standard, not an MBB scorecard. Delete a phase the case never
reached rather than inventing content for it.

### 12 · Cold start on Tier 3 — ask, do not assume

The wiki's five Daniel-specific sections are blank as of 2026-08-30 because this
is **the first round of a new cycle**, not because data is missing.

If they are still blank, **ask Daniel whether that is because the round is just
beginning.** If yes:

- mark Tier 3 `cold start` for every phase — never `missed`;
- assess Baseline and Good → Great normally;
- **propose** Daniel-specific entries from this session in section 6, each as an
  observable behavior rather than a trait, with its evidence.

After the first session or two those proposals get written into
`_wiki/Case Performance Baseline.md` and Tier 3 goes live. **Palladia proposes;
Daniel approves.** Never write his standard for him, and never score a phase
against a standard that does not exist yet.

### 13 · Route every piece of feedback into exactly one tier

Routing is real work, not filing. For each observation from any voice:

- breaks the standard → **Baseline**
- only separates good from excellent → **Good → Great**
- touches something he is already working on → **Daniel-specific**

The third is the most important. **A repeat means the correction has not
transferred**, which is stronger evidence than a fresh observation.

Tag every line: `[D-self]` · `[R]` the case giver, quoted · `[P]` Palladia.

Where the reviewer already covered something, **lead with his words and let `[P]`
add only what he did not say.** A `[P]` line that restates an `[R]` line in
different words is noise — and it quietly inflates Palladia's share of a document
where she is the least-weighted voice.

### 14 · Name where the voices diverge

If Daniel rated a phase well and the transcript shows otherwise, **say so
plainly.** The disagreement is the finding — it is why his self-assessment is
written first rather than last. Do not smooth it.

Same for a `[P]`/`[R]` split: **name it, do not resolve it in your own favor.**
The reviewer holds the higher weight, so the honest form is *"the reviewer said
X; the transcript also shows Y"* — never *"the reviewer was wrong."*

### 15 · Drills

Write **one or two drills**, each with a success criterion and a retest
date. If Daniel finishes reading and does not know what to practice next, the
eval failed regardless of how good the analysis was.

### 15b · Remove template-only authoring comments

Before routing the completed evaluation, remove every HTML authoring comment copied from the template (`<!-- ... -->`). These instructions belong in the template, not in Daniel's final reading artifact, and can appear as extensive grey text in Obsidian's editor. Preserve the attestation, self-assessment, all three voice tags, tier ratings, help levels, drills, and routing fields. Verify a search for `<!--|-->` returns zero matches in the final evaluation.

## Part 3 — Route it back

The eval is written. Now make it survive the session that produced it.

### 16 · Add the case-log entry

`casing/casing-session_log/YYYY-MM-DD_<Case Name>_Taken.md`, from
`_meta/template_library/case-session-entry.md`. **The `_Taken` suffix is
required.**

**Copy the whole template, not only its frontmatter.** Preserve the template's
`## Sync` button block verbatim. Custom session prose may replace the instructional
comment or be added above the button, but it must never replace or omit the button.
A frontmatter-valid note without the sync block is incomplete.

Unlike a Given entry, these three are **populated, not blank**:

| Field | Value |
|---|---|
| `Overall Performance` | Bad · Fine · Good · Great · Perfect — Daniel's word, never a number |
| `Counter` | running tally of cases **taken** — derive as max+1 over date-sorted Taken entries |

`(Growth) Feedback` **is the weakness record** — `weakness-derivation` reads this
field. Write it behaviorally. "Be more concise" is unusable; "read Exhibit 1
line-by-line instead of synthesizing to a so-what" is usable.

Populate `Weaknesses hit`, and record `Top of mind` as hit/missed against the
Dashboard's six-item list. Leave anything the evidence does not support blank —
a blank is honest, a guess corrupts every count built on it.

**Exception — the three difficulty fields are a required gate.** `Difficulty`,
`Qual Diff` and `Quant Diff` are the casebook's *published* ratings, not how the
case felt and not how Daniel performed. "Blank is honest" does not apply to them —
go and look. Source order: the extracted case PDF, then the exact casebook edition
(bounded lookup — **never read a casebook whole**), then the reviewer's own words
in the transcript, then an existing entry for the same case in the same edition.

**Search the transcript for it every time — it is frequently spoken aloud.** Daniel
routinely asks the reviewer what difficulty the case was, usually near the end of
the session, and the reviewer is normally reading it straight off the casebook page.
Search the end-of-session exchange for that question and capture the answer verbatim.
When the reviewer states a rating explicitly, that is an authoritative source, not a
fallback — and if the reviewer also interprets it ("quant 8, that's a hard one"),
their interpretation beats the arithmetic in the mapping guide.

Scales vary — 1–3, 1–5, 1–10, words, stars. Convert every one into Daniel's five
bands using `_system-files/reference_docs/DifficultyMapping.md`. Read it; do not
improvise a conversion.

Finish in exactly one of two states:
- **Sourced** — all three filled, plus one line in the note body:
  `Difficulty source: Stern 25-26 case header — Quant 8/10, Structure 9/10 → M/H, Hard`
- **Unavailable** — marked `unresolved` with the reason inline, and flagged to
  Daniel in one line of your closing report.

A silent blank is not a legal outcome. Sourcing the Sauce and Shisha both shipped
blank this way, and both were recoverable from the casebook.

**If the `Counter` sequence has a gap — a Taken entry with no `Counter`, or a
skipped number — STOP AND ASK.** Do not silently renumber, and do not pick the
value that makes the arithmetic close. A wrong `Counter` is invisible and
corrupts every count built on it. *(2026-08-30: a gap at Soup Bars produced an
off-by-one caught only by a second reader.)*

**Set `Behavioral` directly when the evidence is unambiguous** — a labelled
behavioral segment, or a fit question asked and coached. Ask only when it is
genuinely unclear. `[RELAXED 2026-08-30]` The old rule said always ask; asking
about something the recording plainly shows just spends Daniel's attention.

If this session deliberately retested an earlier one, set `Retest of`.

### 16b · Sync the exact case-log note to Google Sheet — REQUIRED

After the `_Taken` case-log note passes validation, run its sync rather than merely preserving the button.

1. Re-read the exact new `_Taken` note and confirm `Synced` is not already `Y`; the downstream sheet append has no deduplication.
2. Require the full log gates first: sourced difficulty, populated Overall Performance and Counter, one Sync block, and complete payload identity.
3. Execute `_meta/template_library/_sync-this-case.md` against that exact note. If Obsidian/Templater is unavailable, perform the same POST using the script's field mapping and webhook reference; never substitute “most recent note.”
4. Treat only HTTP 2xx as success. On success, set `Synced: Y` and `Synced at:` to the real ISO timestamp, then re-read the note. On any other status, leave both fields unchanged and report the failure.
5. Do not describe the case as synced from the existence of the button or from a request being attempted. The HTTP result and updated frontmatter are the evidence.

Daniel's 2026-09-01 instruction makes this a standing step of the post-case workflow; no separate per-case confirmation is required.

### 17 · Queue a drill if it earned one

`_wiki/drill-queue.md` is the single home for open practice items. **Append to
Open** when either trigger fires:

- a **big miss** — something that broke the baseline standard outright;
- a **repeat of a known high-value error** — a weakness at 3+ sightings, or a
  Top-of-mind item appearing again.

A repeat is the stronger case: it means the correction has not transferred, and
that is what earns a **`coached-redo`** — rerunning one specific section live —
over a written note.

Tag the source. **`[palladia-derived]`** when you found it; **`[daniel-directed]`**
when he asked for it. Name the **section**, not the whole case. Every item needs a
success criterion and a retest date.

**If this session was the retest for an open item, propose closing it — do not
close it yourself.** Closing asserts that a correction transferred, and that is
Daniel's call.

If neither trigger fired, **queue nothing** and say so. A queue that collects
every observation stops being read. If Open already holds ~5 items, say that
instead of quietly adding a sixth.

### 18 · Propose wiki updates

Cold-start or genuinely new patterns go to Daniel as **proposals** for
`_wiki/Case Performance Baseline.md`'s Daniel-specific sections, each as an
observable behavior with its evidence.

**He approves; you never write his standard for him.** Once those land, Tier 3
stops reading `cold start` and goes live.

### 19 · Report, then offer the debrief

Name the case-log entry, whether a drill was queued and why, and any wiki
proposals awaiting his approval.

Then **offer `taken-case-debrief` once** — the live walkthrough where the two of
you work out *why* a mistake happened and change the queue together.

**Offer, do not assume, and do not push.** A clean case may not need one. He can
also take it days later, or ask for it on its own. If he declines, stop here —
this skill's work is complete without it.

## Pitfalls

- **Calling a Granola tool before invoking `granola-capture`.** One unfiltered
  list call silently drops sessions. Observed, reproducible.
- **Getting direction backwards.** The whole record inverts: the giver's
  coaching is attributed to Daniel and his answers read as questions.
- **Relabeling `Them` as the candidate.** On a taken case `Them` is the case
  *giver*. This is the single most likely mistake in this skill.
- **Omitting the `_Taken` suffix.** The unsuffixed name belongs to the given side.
  On a reciprocal day this silently destroys the other direction's transcript.
- **Collapsing a reciprocal pair.** Two people can case each other on one day.
  Two sessions, two files, one folder.
- **Putting the self-assessment in the recording file.** Evidence and judgment
  stay separate.
- **Offering a diagnosis before Daniel has self-assessed.** Anchors him and
  destroys the comparison.
- **Asking him to self-assess when he already did it on the recording.** Check
  the transcript first; his in-session read is the better evidence.
- **Discarding a reviewer's whole read over one wrong fact.** Disqualify only the
  insights that depend on it.
- **Marking Daniel down for a conclusion that follows correctly from a figure he
  was given.** Assess the reasoning, record the source defect separately.
- **Editing transcript wording.** Labels only.
- **Reporting success on a short union sweep.** The response looks clean.
- **Analyzing before the attestation is filled.** The reading step is the one
  that gets skipped, and it is the one that makes the analysis correct.
- **Running capture and assessment in one context for a transcript ≥35 KB.**
  The shared failure mode timed out before any artifact was written. Finish and
  verify capture first; assess in a fresh stage from chunked reads.
- **Writing `[P]` content while section 1 is empty.** Hard stop.
- **Scoring Tier 3 as `missed` during cold start.** There is no standard yet to
  miss. That reads as a failure and it is not one.
- **Writing Daniel-specific entries into the wiki.** Propose; he approves.
- **Assessing exhibits without opening the case PDF.** The transcript says what
  was spoken about a number, not what was on the page.
- **Assigning a numeric or composite score.** The baseline doc bans them.
- **Smoothing a divergence between his self-assessment and the transcript.**
- **Leaving a drill inside the eval file.** That is where drills went to die
  before `drill-queue.md` existed. If it earned a slot, queue it.
- **Queuing every observation.** Two triggers only. A full queue is an unread queue.
- **Closing a drill-queue item yourself.** Propose; Daniel confirms a correction
  transferred.
- **Omitting the source tag** on a queued item. Derived and directed are not the
  same thing and the distinction has to stay visible.
- **Writing a numeric `Overall Performance`.** His vocabulary: Bad/Fine/Good/Great/Perfect.
- **Treating `[P]` as the authority.** It is the lowest-weighted voice. The
  reviewer was in the room; Palladia has a transcript.
- **Restating an `[R]` observation as a `[P]` line.** Noise, and it inflates the
  least-weighted voice's share of the document.
- **Overriding the reviewer without a quotable contradiction from the transcript.**
- **Inferring `Reviewer calibration` yourself.** Daniel sets it. Judging a named
  person's competence from their case-giving is not your call, and the document
  is one he may share.
- **Discounting eyewitness observations under `developing`.** Only technical
  judgments drop. Delivery and followability are seen, not assessed — a newer
  reviewer's read on those is as good as anyone's.

## Verification

- [ ] `granola-capture` was invoked before any Granola tool call.
- [ ] Union sweep ran; count matched expectation, or the shortfall was escalated.
- [ ] Direction confirmed from note **content**, not the title alone. State how.
- [ ] `casing/session_notes/` was listed before any folder was created.
- [ ] **Exactly one** folder matches `YYYY_MM_DD_Daniel X <Partner>`. State the count.
- [ ] `Activity: Taken`, `Candidate: Daniel`, `Case giver:` = the partner.
- [ ] `Them` was relabeled to the **case giver**, not to Daniel.
- [ ] Recording file is named `session-recording_<Partner><YYYYMMDD>_Taken.md`
      and did **not** overwrite the unsuffixed given-side file.
- [ ] `grep -cE '^\*\*(Me|Them):' <file>` returns **0**.
- [ ] Header carries a real Granola UUID and a status matching what happened.
- [ ] No assessment content was written into the recording file.
- [ ] For transcripts ≥35 KB, capture completed and was verified before Part 2 began; Part 2 chunk ranges cover the saved transcript without gaps or overlaps.
- [ ] Final evaluation contains zero `<!--` or `-->` template markers.
- [ ] Attestation section 0 is complete, naming **one specific item per source**.
- [ ] Case PDF was opened, or its absence is stated in the attestation.
- [ ] Daniel's self-assessment was present **before** any `[P]` line was written —
      sourced from the transcript if he gave it in-session.
- [ ] For section-wise generation, the destination template was created once;
      every later write was a targeted section patch, each section was read back,
      and no unresolved placeholder remains in a required section.
- [ ] Any reviewer fact contradicted by the case materials is cited, and only the
      dependent `[R]` lines are marked `[R–disqualified]`.
- [ ] Every phase the case reached carries all three tier ratings + commentary.
- [ ] No numeric or composite score anywhere.
- [ ] Tier 3 reads `cold start`, not `missed`, when no standard exists — and
      Daniel was asked to confirm the cold start.
- [ ] Every feedback line is tagged `[D-self]`, `[R]`, or `[P]`.
- [ ] Divergence between voices is named, not smoothed — and `[R]` was not
      overridden without a quotable contradiction.
- [ ] No `[P]` line merely restates an `[R]` line.
- [ ] `Reviewer calibration` came from Daniel, not from your own inference.
- [ ] Under `developing`: eyewitness `[R]` lines kept full weight; only technical
      claims were checked against the wiki.
- [ ] At least one drill with a success criterion and a retest date.
- [ ] Case-log entry exists with the `_Taken` suffix and validates against
      `case-session-entry.md` — no missing fields, no invented ones.
- [ ] Case-log body contains exactly one `## Sync` section and the command
      `Templater: Insert _sync-this-case`; frontmatter-only validation is insufficient.
- [ ] Case-log sync returned HTTP 2xx; the exact `_Taken` note now has `Synced: Y` and a real `Synced at` timestamp. If not, the failure was reported and the fields remain unchanged.
- [ ] `Overall Performance` and `Counter` are populated.
- [ ] `Counter` was derived from the log, not copied — and any gap in the
      sequence was escalated rather than papered over.
- [ ] `(Growth) Feedback` is behavioral enough for `weakness-derivation` to consume.
- [ ] Drill queued **only** on a big miss or a high-value repeat — or you stated
      that neither fired.
- [ ] Any queued item carries a source tag, a success criterion, and a retest date.
- [ ] No drill-queue item was closed without Daniel's confirmation.
- [ ] Wiki Daniel-specific entries were **proposed**, not written.
