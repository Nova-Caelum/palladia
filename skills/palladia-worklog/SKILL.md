---
name: palladia-worklog
description: >-
  Use after completing any meaningful unit of case-prep work — a scored case, a
  drill session, a debrief, an intake, a plan change, a decision — and before
  returning to Daniel. Also use when asked what has happened recently, when
  reconstructing history, or when a session is ending.
disable-model-invocation: false
metadata:
  version: "0.1.0"
  author: "Nova Caelum / Chief-PM"
  license: "proprietary"
  platforms: [linux]
  category: palladia
  tags: [worklog, provenance, obsidian, bases, continuity]
  related_skills: [session-intake, warm-up]
  provenance:
    origin: "Nova Caelum-authored"
    platform: "Hermes Agent (Nous Research) — palladia profile, olympus1"
    design_source: "MemoryAndWorklog_Palladia_ChiefPM_2026-08-29.md §2 (locked 2026-08-29)"
category: palladia
---

# Palladia Worklog

## Overview

Your worklog is how a session's work survives the session. Your memory file is a
pointer capped at 2,200 characters and frozen at session start — it cannot hold
history. The worklog can.

**The folder is the database.** One Markdown note per entry. The YAML frontmatter
*is* the columns; the note body *is* the detail. Obsidian Bases reads the
frontmatter across the folder and renders it as a sortable, filterable table, so
there is no separate database file to maintain and nothing to drift out of sync.

Location: `_meta/worklog_entries/` inside PallaDrive.

**Supporting resources, all created 2026-08-29:**

| Path | What it is |
|---|---|
| `_meta/worklog_entries/` | The entries folder. **Exists** — write here. |
| `_meta/Worklog.base` | The Obsidian Base that renders the folder as a table. Four views: All entries · Last 7 days · By type · Scored reps. |
| `_meta/template_library/Worklog_Entry_template.md` | Entry template carrying the frontmatter contract. |
| `_system-files/reference_docs/Bases-Reference_DRAFT.md` | How Bases work, and what is still unconfirmed about them. |

> **The Base is a view, not a store.** `Worklog.base` reads the frontmatter of the notes in `worklog_entries/` and renders them. You never write "into" the Base — you write a note with correct frontmatter into the folder, and it appears as a row. If a column shows empty, your frontmatter key is missing or misspelled; the Base is reporting honestly.

> **The Base has never been rendered.** Its syntax is drafted from Obsidian's published docs — no `.base` file existed in this vault before it. Your entries are unaffected either way (they are plain Markdown), but if Daniel reports the table looking wrong, that is the `.base` file's problem, not yours. Point him at `Bases-Reference_DRAFT.md` §6.

## When to Use

Append an entry after:

- Scoring a case or a behavioral/PEI answer
- Running a drill session
- A debrief
- Ingesting a new artifact (recording, transcript, casebook, notes)
- A change to the weakness ledger, skill matrix, or high-yield note
- A decision Daniel makes about targets, focus areas, or approach
- Any session in which something was learned that a future session would want

Read the worklog when: asked what happened recently, reconstructing why a
weakness was opened or closed, or starting a session after a gap.

Do **not** append for: trivial lookups, a single clarifying question, or work you
abandoned without a conclusion.

## HARD RULE — this worklog is local

You do **not** write to the Nova Caelum Supabase worklog. You have no `nova_ops`
MCP and you should not seek one. Your worklog lives in PallaDrive and nowhere
else. This is deliberate: it is what keeps the whole system portable to another
user later, and it keeps case-prep data out of Nova Caelum's systems of record.

## Frontmatter schema

Mirrors the Nova Caelum Supabase worklog field-for-field where the concepts
match, so the discipline ports unchanged and a future export is a mechanical
transform rather than a redesign.

```yaml
---
created: 2026-08-30T14:22:00        # ISO 8601, local time
author: palladia                     # always
project: case-prep                   # coarse bucket
type: case-scored                    # see vocabulary below
summary: "..."                        # <=280 chars, one line, no newlines
tags: [case-scoring, synthesis, time-pressure]
case_id: case-2026-08-30-01          # omit if not case-linked
dimensions: [synthesis, communication] # readiness dimensions touched; omit if none
independence: light-prompt           # omit if not a scored rep
---
```

**`type` vocabulary:** `case-scored` · `behavioral-scored` · `drill` · `debrief` ·
`intake` · `ledger-update` · `decision` · `plan-change` · `session-note`

**`independence` vocabulary** (how much help the rep needed — required on any
scored rep, because a right answer after three hints is not a right answer):
`no-help` · `neutral-clarification` · `light-prompt` · `directional-hint` ·
`major-scaffold` · `answer-supplied`

**`summary` is capped at 280 characters** and must be one line. If it does not
fit in 280 characters, the detail belongs in the body — that is what the body is
for.

## The body is the detail

Everything below the frontmatter is free-form Markdown. Write what a future
session would need. Link generously — `[[case-2026-08-30-01]]`,
`[[weakness-ledger]]` — because backlinks are the reason this lives in PallaDrive
instead of a spreadsheet.

## Append procedure

1. **Name the file:** `_meta/worklog_entries/YYYY-MM-DD-HHMM-<short-slug>.md`
   (e.g. `2026-08-30-1422-profitability-case-maya.md`). Timestamp-prefixed so the
   folder sorts chronologically without depending on frontmatter.
2. **Write frontmatter first.** Fill every field that applies; omit fields that do
   not rather than writing `null`.
3. **Check the summary length.** 280 characters, one line.
4. **Write the body.** Link to the case note and any ledger entries touched.
5. **Never edit a prior entry.** The worklog is append-only. If you were wrong,
   write a new entry that says so and link back. A silently corrected record
   destroys the history of what you believed and when.

## Pitfalls

- **Writing to one shared file.** Do not. Concurrent writes corrupt, and Daniel
  may have the file open in Obsidian while you write. One note per entry is
  conflict-free by construction.
- **Putting detail in a frontmatter field.** Multi-line text in YAML breaks Bases
  and is miserable to read. Detail goes in the body.
- **Batching.** Append when the work completes, not at session end. Sessions get
  cut off; the entry you did not write is gone.
- **Summarizing instead of recording.** "Worked on cases" is not an entry. What
  case, what happened, what changed.
- **Reaching for the Supabase worklog.** You do not have it. If you find yourself
  looking for `nova_ops`, stop — something is wrong with your configuration and
  you should say so rather than route around it.

## Verification

After appending, confirm:

- [ ] File exists at `_meta/worklog_entries/` with the timestamp-prefixed name.
- [ ] Frontmatter parses — no unquoted colons, no multi-line scalars.
- [ ] `summary` is one line and ≤280 characters.
- [ ] `independence` is present if this was a scored rep.
- [ ] No prior entry was modified.

## Deferred

Flat folder for now. Month-sharding (`_meta/worklog_entries/2026-08/`) is the deferred
alternative and matters past a few thousand notes — it is a `mv` when it matters,
so do not pre-optimize.
