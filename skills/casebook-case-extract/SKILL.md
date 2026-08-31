---
name: casebook-case-extract
description: >-
  Use when Daniel names a specific case and a casebook and wants that case pulled
  out — "pull the Pedal Pals case from the Darden casebook", "get me that case
  from Wharton", "extract <case> from <catalog>". Also use when the casebook guard
  blocks a catalog read and the request was for one named case.
disable-model-invocation: false
metadata:
  version: "0.1.0"
  author: "Nova Caelum / Chief-PM"
  license: "proprietary"
  platforms: [linux]
  category: casing
  tags: [casebook, pdf, extraction, pagination, individual-cases]
  related_skills: [session-intake, casebook-router]
  provenance:
    origin: "Nova Caelum-authored"
    platform: "Hermes Agent (Nous Research) — palladia profile"
    design_source: "PALLADIA_CASEBOOK_EXTRACTION_SKILL_BRIEF.md (Vulcan, 2026-08-29) — pagination model reused, not re-derived"
category: casing
---

# Casebook Case Extract

## Overview

One job: **given a catalog and a case name, produce that case as its own PDF in
its own folder, with a small index file so it can be found and linked later.**

This is the second of the two casebook workflows and it is deliberately separate
from the first. Fact-checking a claim inside a catalog is a *lookup* — it returns
a page slice and nothing is written. This skill is an *extraction* — it writes a
durable artifact Daniel will practice from. Same underlying pagination problem,
different output contract, so they are different skills.

The extracted case becomes a real, self-contained study artifact. That is the
point: Daniel should be able to open one folder and case from it, without the
300-page catalog anywhere nearby.

## When to Use

- Daniel names a case and a casebook and asks for the case.
- Daniel asks to add a case to `individual_cases`.
- The casebook guard blocked a generic catalog read and the underlying request
  was for a single named case.

**Not for:** answering a question about something inside a catalog without
extracting (that is a lookup), browsing what cases a catalog contains (that is
`casebook_inspect`), or reading an already-extracted case.

## HARD RULES

1. **Never load the whole catalog into context.** This is the entire reason the
   guard exists. The catalogs in this drive are 1.4–7.0 MB and hundreds of pages
   of dense visual material. One generic read spends the session.
2. **Never mutate the source catalog.** Read-only, always. The extraction writes
   a new PDF elsewhere; the catalog is untouched evidence.
3. **Never guess a page range.** If the case boundary is not verified, stop and
   ask. A confidently wrong extraction is worse than no extraction, because it
   looks finished — Daniel will study a truncated case and not know.
4. **Never overwrite an existing extracted case folder.** If it exists, say so
   and ask before doing anything.

## The pagination problem — read this before you touch a page number

This is the failure mode that makes naive extraction wrong, and it is solved
material. From the extraction brief:

> TOC numbers are often *printed page labels*, while PDF APIs use *physical page
> indexes*. A single global offset is insufficient for documents with covers,
> Roman-numeral front matter, section inserts, duplicated page labels, or
> pagination resets.

So: **the TOC says a case starts on page 112. That is a printed label. The PDF's
page 112 is almost certainly not it.** Casebooks routinely carry a cover, a
Roman-numeral introduction, and per-section inserts — and the offset changes at
each of those discontinuities.

The correct model is a **piecewise mapping**, not one offset:

- A `PageAnchor` ties a printed label to a physical index, with evidence for how
  the tie was made (`page_label`, `header_footer`, `title_match`, `toc_match`).
- A `PaginationSegment` covers a physical range where one mapping rule holds,
  and records why the previous segment ended.
- A case's physical range is derived by locating the nearest anchors on both
  sides and verifying the result, not by adding a constant.

**Verification is not optional.** A candidate range is confirmed when the case
title is found on the proposed start page *and* the next case's title is found
at the proposed end boundary. Both, not either.

Do not re-derive this model. It is specified in
`PALLADIA_CASEBOOK_EXTRACTION_SKILL_BRIEF.md`; extend it there if it needs to
change.

## Procedure

### 1. Resolve inputs

You need the catalog path and the case query. If either is missing, ask one
concise question — do not browse the catalog to find out.

`[VERIFIED 2026-08-29]` Catalogs live at
`casing/casebooks_catalogs/`, named `Catalog_<School>-casebook-<years>.pdf`.

**List the directory. Never rely on a remembered count or a remembered set.**
Catalogs get added — the collection grew by two during a single day on
2026-08-30, and any skill that had memorized the old set would have silently
skipped the new ones.

Match case-insensitively; capitalization is inconsistent across filenames. A
school may appear in more than one year (`Darden-casebook-2023-24` and
`Darden-casebook-2024-25` both exist), so resolving "the Darden casebook" to a
single file is **not** safe — confirm which year when more than one matches.

If Daniel names a school rather than a filename ("the Darden casebook"), resolve
it against the filenames and confirm which you picked if more than one matches.

### 2. Locate the case — bounded, never bulk

Use the plugin-owned extraction tool. Do not run `pdftotext`, a PDF reader
script, OCR, or page rendering yourself against the full document — those
outputs land in the conversation, which is the thing being prevented.

If the tool returns **ambiguous**, show the top candidates with their evidence
and ask Daniel to choose. Never pick for him. Casebooks reuse case names across
editions, and two schools may both have a "Great Burger."

### 3. Verify the boundary

Confirm both edges before extracting. State the physical range and the printed
range you resolved, so an error is visible rather than silent.

**Preserve whole cases.** Casebooks interleave the candidate-facing prompt,
exhibits, interviewer guidance, and the solution. Extract all of it — an
extraction that keeps only the prompt destroys the artifact's value for
self-study and for a partner giving the case.

### 4. Write the artifact

`[VERIFIED 2026-08-29]` Destination:
`casing/individual_cases/` — a SIBLING of `casebooks_catalogs/`, not nested
inside it. `[CORRECTED 2026-08-30]` The previous text said the opposite and did
not match disk; the plugin now writes here and refuses anywhere else.

Create one folder per case:

```
individual_cases/
  <Case Name>/
    Case_<Case Name>_<School><Years>.pdf   ← only this case's pages
    index.md                                ← findable metadata
```

`[INFERENCE]` Folder naming follows Daniel's existing convention in
`casing-session_log/`: original capitalization, spaces preserved, no
kebab-casing. His session notes are `2025-10-23_Pedal Pals.md`, so `Pedal Pals/`
is the consistent folder name. Extracted cases carry no session date, so no date
prefix.

The PDF is a **real page extraction**, not a pointer or a summary.

### 5. Write `index.md`

**This shape is PROVISIONAL.** Daniel is still working the PallaDrive schema and
has asked that we not draft one. This file exists only because he explicitly
asked for "a little index that has difficulty and topic and the kind of case,
case details, just so it can be found and linked."

It deliberately **reuses his vocabulary** from `casing-session_log/` rather than
inventing parallel terms — his properties, his value sets:

```yaml
---
title: "Case_<Case Name>_<School><Years>"   # e.g. Case_HR Co_Darden2024-2025
source_catalog: "Catalog_Darden-casebook-2024-25.pdf"
source_pages_physical: "112-119"
source_pages_printed: "104-111"
extracted: "2026-08-29"
properties:
  "Case book": "Darden 24-25"      # matches his `Case book` values
  "Case Type": ["Profitability"]    # list, as in his notes
  "Difficulty": "Medium"            # Easy | Medium | Hard
  "Quant Diff": null                # Easy | E/M | Medium | M/H | Hard
  "Qual Diff": null                 # Easy | E/M | Medium | M/H | Hard
  "Industry": null
  "Sections": ["prompt", "exhibits", "interviewer guidance", "solution"]
---

Short factual description of the case setup. No solution content here.
```

**Fill only what the source states.** Difficulty, industry, and case type are
often printed in the casebook's own TOC or case header — take them from there.
If a field is not stated, leave it `null`. Do not infer difficulty from reading
the case; that is a judgment Daniel has a five-point scale for and it belongs to
him, not to an extraction tool.

**Do not put solution content in `index.md`.** Daniel may want to case from this
himself. The solution lives in the PDF where he controls when he sees it.

### 6. Report

State: the case, the catalog, the physical and printed ranges, the sections
included, and the path written. If anything was uncertain, say so — including
what you could not confirm.

## Pitfalls

- **Trusting the TOC number as a page index.** The single most likely failure.
  See the pagination section.
- **Extracting only the prompt pages.** Silently destroys the artifact.
- **Filling `index.md` fields by inference.** A guessed difficulty looks like
  data and will be wrong in a way nobody catches.
- **Reading the catalog "just to check."** There is no small read of a 300-page
  catalog. Use the bounded tool or ask.
- **Assuming a case name is unique.** Ask when ambiguous.
- **Writing into `user_notesheets/` or `study_guides/`.** Those are Daniel's. This
  skill writes to `individual_cases/` and nowhere else.

## Verification

Before reporting success, confirm every one:

- [ ] The source catalog is unmodified.
- [ ] The output PDF opens and contains the case's first and last page.
- [ ] Page count matches the verified range — no off-by-one at either edge.
- [ ] The case title appears on the first extracted page.
- [ ] The *next* case's title does **not** appear inside the extraction.
- [ ] `index.md` exists, parses as YAML, and every populated field is sourced
      from the catalog rather than inferred.
- [ ] No solution content leaked into `index.md`.
- [ ] Nothing was written outside `individual_cases/<Case Name>/`.

If a check fails, say which one. Do not report a partial extraction as done.

## Open — needs Daniel

`[RESOLVED 2026-08-30]` Placement and naming are settled by Daniel: the folder
is `casing/individual_cases/<Case Name>/`, holding
`Case_<Case Name>_<School><Years>.pdf` and `index.md`. **`HR Co` is the
reference to match.** The plugin derives the school/years slug from the catalog
filename, so it is not a judgment call.

Still open: whether an extracted case should be cross-linked from its
`casing-session_log/` note when Daniel later cases it.
