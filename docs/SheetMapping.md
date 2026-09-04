# PallaDrive → Google Sheet field mapping

**Author:** Chief-PM · 2026-08-29
**Daniel reviewed:** no
**Status:** Mapping derived from the live sheet, read 2026-08-29. **Nothing syncs yet — this is the spec for the projection, not a record of one.**
**Sheet:** https://docs.google.com/spreadsheets/d/1cmKjG0YnPkM_-DUbS8mjryaRhuuNy2zT_uMrMRaOXJw/edit?gid=918104704

## What this sheet is

The outward-facing view. Other people read it. Daniel: *"the field mapping isn't entirely 1:1, this is meant for others to view so it can be simpler."* The drive has 30 properties; the sheet has 12.

**The omissions are the point.** Growth feedback, weakness counts, and top-of-mind misses are the private diagnostic record. They should never appear here, and a future sync must not "helpfully" add them.

## Direct mappings

| PallaDrive property | Sheet column | Note |
|---|---|---|
| `Counter` | `#` | Taken-case ordinal. |
| `date` | `Date` | Trailing space in the header was fixed by Daniel 2026-08-29. Verified clean. Note other headers still contain **embedded newlines** (`Industry\n(e.g., Chemicals)`) — match on a normalized prefix, not equality. |
| `Case book` | `Case Book` | |
| filename / `title` | `Case Name` | |
| `Industry` | `Industry (e.g., Chemicals)` | Header carries an inline example. |
| `Case Type` | `Case Type (e.g., Profitability)` | Drive value is a **list**; sheet cell is flat — join with `, `. |
| `Partner` | `Interviewer` | |
| `Format` | `Format (In-Person / Virtual)` | |
| `Difficulty` | `Difficulty` | |
| `Overall Performance` | `Overall Performance` | Same Bad/Fine/Good/Great/Perfect scale. |
| `Highest Level Takeaways` | `Highest Takeaways` | Name differs — "Level" dropped. |

## The one mapping that is NOT 1:1

`Partner Type` → `Interviewer's Classification`. **The vocabularies are different and need translation:**

| Drive value | Sheet value |
|---|---|
| `FY` | FY Peer |
| `SY` | SY Peer |
| `Company` | Firm Rep |
| `Advisor` | Darden Expert *(assumed — Daniel to confirm)* |
| `Self` | **`Self`** — maps directly. Daniel 2026-08-29: *"make self map directly from now on, even if it hadn't been used in the past."* Self-practice sessions DO project to the sheet. |

`Advisor` is new (first seen on the 2026-08-26 Soup Bars session) and its sheet target is an inference, not a confirmed mapping. **Do not encode it in a sync until Daniel confirms.**

## Deliberately NOT projected

`(Good) Feedback` · `(Growth) Feedback` · `Qual Diff` · `Quant Diff` · `Weaknesses hit` · `Top of mind` · `Recording` · `Transcript` · `Retest of` · `Behavioral` · `Casing` · `Company Style` · `Time (min)` · `ID` · `notion_id`

## Current state — read 2026-08-29

The sheet holds **28 rows**: one seed row (`#0`, `Test Case` / Wizardry / Transfiguration) and **27 real sessions**, numbered `#1`–`#28`.

**It mirrors the TAKEN set only**, which is consistent with `#` being the Taken ordinal. The 7 `Given` sessions are absent by design — Daniel was running those cases, so there is no performance of his to publish.

So the sheet is **hand-maintained and current through the 2025 cycle**. It is not stale in the sense of abandoned; it simply stops where last cycle stopped.

**What is missing:** the 2026-08-26 `Soup Bars` session, which would be `#29`. That is the whole gap right now — one row.

Nothing automated is syncing. Every row in that sheet was typed by Daniel.

## Open

1. Confirm `Advisor` → `Darden Expert`.
3. Direction: one-way drive→sheet (recommended — one writer, no conflicts), or two-way? Two-way needs a conflict rule and a decision about which side wins.
4. Mechanism: n8n was the original plan. Nothing is built.
