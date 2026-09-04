# Difficulty Mapping — any source scale → Daniel's five bands

**Daniel reviewed:** no
**Owner:** Palladia · created 2026-08-31
**Applies to:** `Difficulty`, `Qual Diff`, `Quant Diff` on every case-log entry.

---

## The target scale — never change this

```
Easy · E/M · Medium · M/H · Hard
```

Five bands. This is Daniel's vocabulary and the only thing that may be written into
the three difficulty fields. Never write a number. Never invent a sixth band. Never
write "Moderate", "Med", "3/5", or a range.

---

## The one rule

**Normalize the source value to a position between 0 and 1, then bucket it.**

```
position = (value − scale_min) / (scale_max − scale_min)
```

| position | band |
|---|---|
| 0.000 – 0.125 | **Easy** |
| 0.125 – 0.375 | **E/M** |
| 0.375 – 0.625 | **Medium** |
| 0.625 – 0.875 | **M/H** |
| 0.875 – 1.000 | **Hard** |

Boundaries round to the higher band. The five bands are centred on positions
0, 0.25, 0.5, 0.75, 1.0 — so a five-point source maps one-to-one and every other
scale lands where its proportion says it should.

This rule is the fallback for **any** scale, including one never seen before.
If you can identify the minimum and maximum, you can map it. You do not need
this document to contain the scale.

---

## Known scales — worked out in advance

### 1–3 (Darden casebooks)
Daniel's explicit instruction: this is the best inference available, and he adjusts
ad hoc outside the workflow if it's wrong.

| Value | position | Band |
|---|---|---|
| 1 | 0.00 | Easy |
| 2 | 0.50 | Medium |
| 3 | 1.00 | Hard |

E/M and M/H are unreachable from a three-point source. That is correct and expected —
do not stretch a 3-point scale to fill five bands.

### 1–5
Maps one-to-one. The cleanest case.

| Value | position | Band |
|---|---|---|
| 1 | 0.00 | Easy |
| 2 | 0.25 | E/M |
| 3 | 0.50 | Medium |
| 4 | 0.75 | M/H |
| 5 | 1.00 | Hard |

### 1–10 (e.g. Stern "Quant 8 / Structure 9")

| Value | position | Band |
|---|---|---|
| 1 | 0.00 | Easy |
| 2 | 0.11 | Easy |
| 3 | 0.22 | E/M |
| 4 | 0.33 | E/M |
| 5 | 0.44 | Medium |
| 6 | 0.56 | Medium |
| 7 | 0.67 | M/H |
| 8 | 0.78 | M/H |
| 9 | 0.89 | Hard |
| 10 | 1.00 | Hard |

### 0–10
Same table shifted: `position = value / 10`. 0 → Easy, 5 → Medium, 10 → Hard.
**Check whether the scale starts at 0 or 1 before mapping** — it changes the answer
by roughly one band at the low end.

### Words already in the target vocabulary
`Easy` / `Medium` / `Hard` pass straight through. So do `E/M` and `M/H`.

### Other word scales
Map by position in the source's own ordered list, then apply the rule above.
Example — `Low · Moderate · High` is a 3-point scale: Low → Easy, Moderate → Medium,
High → Hard. Example — `Very Easy · Easy · Medium · Hard · Very Hard` is 5-point:
maps one-to-one onto the five bands.

### Letter grades / star ratings
Treat as their obvious numeric range (A–F → 5-point reversed; ★1–5 → 1–5).
**Watch direction:** if the source's high value means *easier*, invert the position
(`position = 1 − position`) before bucketing. State the inversion in the note.

---

## When the source defines its own bands, the source wins

If a casebook says "7–10 = Hard", use that, not this table. A source's own
definition always beats the general rule. Say so in the note.

Likewise, if the reviewer says it out loud in the transcript — "quant 8, that's a
hard one" — that is a valid source and it overrides the arithmetic.

---

## When you cannot map it

Three things must never happen: inventing a number, guessing a band you can't
justify, and leaving the field silently blank.

If the scale is genuinely unmappable — unknown bounds, unclear direction, a
one-off rubric — then:

1. Leave the field **unresolved**, not blank-with-no-explanation.
2. Record the raw value and its source in the note body, verbatim:
   `Difficulty: unresolved — source says "spice level 4/7", scale direction unclear`
3. Flag it to Daniel in your report at the end of the case. One line.

An unmappable scale is a fine outcome. A silent blank is not.

---

## Provenance — one line, in the note body

Do not add fields to the tracker. Record the source inline in the case-log note body
so a later reader can audit the conversion:

```
Difficulty source: Stern 25-26 case header — Quant 8/10, Structure 9/10 → M/H, Hard
```

If the source was the transcript, say whose words: `reviewer, end of session`.

---

## What these fields mean

The three fields describe the **published difficulty of the case**, not how hard it
felt and not how Daniel performed. A case Daniel struggled with is not thereby Hard.
Perceived difficulty is not tracked here; if it ever is, it gets its own field.

- `Difficulty` — the source's overall rating
- `Qual Diff` — the source's qualitative / structure rating
- `Quant Diff` — the source's quantitative / math rating

If the source publishes only one overall number, put it in `Difficulty` and leave the
other two unresolved with a reason. Do not copy one number into all three.

---

## Source priority

Take the first that yields a value:

1. The extracted individual-case PDF — case header or interviewer guidance
2. The exact casebook edition — TOC, case title page, interviewer page.
   Use bounded case lookup. **Never read a casebook whole.**
3. The transcript — **always check it; the rating is frequently spoken aloud.**
   Daniel routinely asks what difficulty the case was, usually near the end of the
   session, and whoever holds the casebook is normally reading it straight off the
   page. Capture the answer verbatim. A rating stated explicitly is an authoritative
   source, not a consolation prize — it ranks below the published page only because
   the page can be re-checked later. If the two disagree, record both and say so.
4. An existing case-log entry for the **same case in the same casebook edition** —
   not a similarly-named case from a different year

Record which one you used.

Ordering is about checkability, not credibility. Do not skip the transcript because
a PDF already gave you a number — if the reviewer also stated it, that corroborates
the reading, and if they interpreted it ("quant 8, that's a hard one") their
interpretation overrides the arithmetic above.
