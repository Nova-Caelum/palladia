---
name: pre-case-given
description: >-
  Use when Daniel is preparing to GIVE a case — when he says he is casing
  someone, names a person he is interviewing, asks for case options for a
  partner, or asks what he should give. Not for cases he is taking, not for
  post-session debrief.
disable-model-invocation: false
metadata:
  version: "0.1.0-draft"
  status: FIRST DRAFT — derived from one observed session (Ryan 2026-08-30)
  author: "Nova Caelum / Chief-PM"
  license: "proprietary"
  platforms: [linux]
  category: casing
  tags: [pre-case, given, case-selection, session-folder, casebooks]
  related_skills: [casebook-case-extract, session-intake, post-case-given, warm-up]
  provenance:
    origin: "Nova Caelum-authored"
    platform: "Hermes Agent (Nous Research) — palladia profile, olympus1"
    design_source: "Daniel, verbally, 2026-08-30 — workflow dictated step by step"
    reference_session: "casing/session_notes/2026_08_30_Daniel X Ryan/"
category: casing
---

# Pre-Case (Given)

> ## ⚠ PROVISIONAL — one observed instance
> The house threshold is three. This has one: the Ryan session of 2026-08-30,
> which Daniel walked through directly and asked to be written down. Run it,
> note where it is wrong, and correct it against the next two Given sessions
> before treating any part of it as settled.

## Overview

Daniel is about to give a case to someone else. You are done when the session
folder exists, the case is selected with his explicit approval, the individual
case file is on disk, and the three session documents are staged in the folder.

The output is not a recommendation. It is **a prepared folder** — if he has to
find or fix anything at session time, the skill failed.

## When to Use

Daniel names a person and a date and says he is casing them. Also when a Given
session appears on the calendar with no session folder behind it.

**Not for:** cases he is taking (`warm-up`), logging a finished session
(`session-intake`), or debrief (`post-case-given`).

## Procedure

### 1 · Intake — ask, do not assume

Collect, in one message:

- **Date** and **person's name** — required, both. Everything downstream keys off them.
- **Their case tracker** — link or path, if they keep one.
- **Their notes / loose preferences** — what they want to work on.
- **Industry**, **difficulty**, **firm style**.

**Weighting: firm style and difficulty are the two heavily-weighted criteria**
whenever they are supplied. Everything else is a tiebreaker. If he gives you
neither, ask for them specifically before selecting — do not proceed on
industry alone.

### 2 · Session folder — CHECK BEFORE YOU CREATE

Target: `casing/session_notes/YYYY_MM_DD_Daniel X <Person>/`
(underscores in the date — this differs from `casing-session_log/`, which uses
hyphens. Do not carry one convention into the other.)

1. **List `casing/session_notes/` and read it.** Do not create first.
2. If a folder for that person on that date exists — **use it.** Record the path.
3. Only if it does not exist, create it.

This is a hard stop. Duplicate session folders split a session's evidence in
two and neither half is findable later.

### 3 · Case selection — search, then filter to what we own

Search the web for what is recommended against the stated criteria, then
**filter down to cases we actually hold.** A case we cannot open is not a
candidate. **List each source directory this run — never work from a remembered
inventory.** Catalogs and extracted cases get added; the collection grew by two
in a single day on 2026-08-30.

Availability sources: `casing/casebooks_catalogs/` (school casebooks) ·
`casing/individual_cases/` (already extracted) · `casing/casing-session_log/`
(what has been cased, and how it went). Discard everything else.

### 4 · Present three options — then stop

Return exactly three. For each: **case name · casebook + year · firm style
(if any) · why this one**, argued against his stated criteria.

Then **stop and wait.** Do not extract, do not create documents, do not pick
for him. Daniel signs off explicitly on one case before anything else happens.

### 5 · Get the case on disk

If we already hold it as an individual case, link it and move on. Otherwise
extract it from the casebook via `casebook-case-extract`.

`[VERIFIED 2026-08-30]` Destination and shape follow **HR Co**:

```
casing/individual_cases/<Case Name>/
  Case_<Case Name>_<School><Years>.pdf
  index.md
```

e.g. `casing/individual_cases/HR Co/Case_HR Co_Darden2024-2025.pdf`.

**Note:** `casebook-case-extract` previously stated a different destination
(`casing/casebooks_catalogs/individual_cases/`). That was corrected on
2026-08-31 — the extraction plugin's tool description and README now name
`casing/individual_cases/`, matching this section and HR Co on disk. The two
sources now agree; no override is needed.

### 6 · Create the three session documents

Templates live in the folder-shaped session template at
`_meta/template_library/session-notes_template/YYYY_MM_DD_Daniel X Partner/`.
Copy each into the session folder from step 2:

| Write | From |
|---|---|
| `given-case_selection-<Person><YYYYMMDD>.md` | `given_case-selection_template.md` |
| `given-case_eval-<Person><YYYYMMDD>.md` | `given-case_eval_TEMPLATE.md` |
| `session-recording_<Person><YYYYMMDD>.md` | `session-recording_TEMPLATE.md` |

### 7 · Fill the selection record — and link the case

The selection document is **yours to complete now.** It is the only one of the
three that is finished before the session runs, and it exists so the reasoning
behind the pick survives.

Populate: the criteria Daniel gave with their weights · all three options as
presented · the case he approved and why · the printed difficulty profile.

**Then link the case material. This step is mandatory and easy to skip:**

```
- **Individual case:** [[Case_<Case Name>_<School><Years>]]
- **Folder:** `casing/individual_cases/<Case Name>/`
- **Extracted from:** `<catalog>.pdf`, physical pages N-N / printed N-N
```

**The link must resolve.** Open the folder and confirm the PDF and `index.md`
are both there. If the case could not be extracted, write that plainly instead
of leaving a dead link — a broken link reads as "filed" and is worse than an
honest gap.

### 8 · Leave the other two documents empty

The eval and recording documents are **staged, not written.** Pre-fill only the
header identity — case, person, date, source. Everything else happens later:
`post-case-given` fills them from the transcript after the session.

Do not pre-fill the recording's transcript section, and do not score anything.
Anything you invent there will be read later as something that happened.

## Pitfalls

- **Creating a session folder without listing first.** Observed on 2026-08-30:
  three folders exist for the same date across three people, with inconsistent
  internals. Check, then create.
- **Selecting before he signs off.** Step 4 is a gate. Extraction is expensive
  and a rejected case wastes it.
- **Proposing a case we cannot open.** A web recommendation is a candidate only
  after it is matched to a casebook or an extracted case on disk.
- **Inventing a destination for an extracted case.** The path is
  `casing/individual_cases/<Case Name>/`. Match HR Co.
- **Softening firm style and difficulty into "considerations."** When Daniel
  supplies them they are filters, not preferences.
- **Filling the eval or recording with anticipated content.** They are staging
  surfaces. Anything you invent there will be read later as something that
  happened.
- **Leaving the individual-case link unwritten, or writing one that does not
  resolve.** Step 7. A dead link reads as "filed" and is worse than a stated gap.
- **Folding the selection record into the eval sheet.** They are separate
  documents on purpose: selection is before, evaluation is after.

## Verification

- [ ] Date and person captured; firm style and difficulty captured or explicitly asked for.
- [ ] `casing/session_notes/` was listed this turn, before any folder was created.
- [ ] **Exactly one** folder matches `YYYY_MM_DD_Daniel X <Person>` for that date. State the count.
- [ ] Catalog and individual-case directories were **listed this run**, not recalled.
- [ ] Three options returned, each in a casebook we hold or already extracted.
- [ ] Every option matches firm style and difficulty, and ≥50% of the remaining stated criteria.
- [ ] Daniel approved one case explicitly. Quote the approval.
- [ ] Individual-case PDF **and** `index.md` exist at `casing/individual_cases/<Case Name>/`, named as HR Co is named.
- [ ] **All three** documents exist in the session folder, named `<doc>-<Person><YYYYMMDD>.md`.
- [ ] Selection record is COMPLETE: criteria, all three options, approved case, rationale.
- [ ] The individual-case link is present **and resolves**, or the gap is stated in words.
- [ ] Eval and recording carry header identity only — nothing session-time pre-filled.
