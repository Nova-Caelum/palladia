# Obsidian Bases — how to use and write them

> # ⚠️ DRAFTED, NOT CONFIRMED
>
> **Every syntax claim in this document comes from Obsidian's published documentation. Not one of them has been verified against a Base we have watched render.**
>
> There were **zero `.base` files** in PallaDrive or the Nova Caelum vault when this was written, so there was no working local example to copy or check against. The first `.base` file in this vault is `_meta/Worklog.base`, created the same day as this document.
>
> Treat everything below as a well-sourced hypothesis. When Daniel opens `Worklog.base` for the first time, work the **CONFIRM AFTER FIRST RENDER** checklist at the bottom, then correct this document and promote the reusable template out of its placeholder.
>
> **Sources:** [obsidian.md/help/bases/syntax](https://obsidian.md/help/bases/syntax) · [obsidian.md/help/formulas](https://obsidian.md/help/formulas), retrieved 2026-08-29 via Context7.

**Author:** ChiefPM · 2026-08-29
**Daniel reviewed:** no
**Status:** DRAFT. Sections marked ✅ have been confirmed by an actual render; nothing is marked ✅ yet.

---

## 1. The one thing to understand first

**A Base is a view, not a store.**

It does not hold data. It runs a query across the notes in your vault, reads their YAML frontmatter, and renders the results as a table. The notes are the database; the Base is a saved lens onto them.

Three consequences that matter more than any syntax detail:

- **Deleting a `.base` file loses the view, never the entries.** The notes are untouched.
- **A Base cannot show a property that no note has.** If a column is empty, the frontmatter is missing or misspelled — the Base is reporting honestly.
- **You cannot "write a row into" a Base.** You create a note with the right frontmatter in the right folder, and it appears. This is the misconception most likely to cause trouble here: it is tempting to think of the Base as the worklog. The worklog is `_meta/worklog_entries/`.

## 2. When a Base is the right tool

**Use one when:**
- You have many notes sharing a frontmatter shape and want to see them as a table.
- You want several different cuts of the same set — all, recent, grouped, filtered — without duplicating anything.
- The detail belongs in prose but the metadata belongs in columns.

**Do not use one when:**
- There is exactly one record. That is a note.
- The data has no natural per-note grain — a Base over a single CSV gains nothing.
- You need the data outside Obsidian. A Base is an Obsidian view; export needs a script over the frontmatter.

## 3. File structure

A `.base` file is YAML with five top-level keys, all optional except `views`:

```yaml
filters:      # applies to every view in the file
formulas:     # computed properties, available as formula.<name>
properties:   # display names and column config
summaries:    # named aggregations, e.g. custom averages
views:        # one or more rendered views
```

### 3.1 Filters

Filters compose with `and`, `or`, and `not`, nested arbitrarily. Top-level `filters` apply to every view; a view's own `filters` narrow further.

```yaml
filters:
  or:
    - file.hasTag("tag")
    - and:
        - file.hasTag("book")
        - file.hasLink("Textbook")
    - not:
        - file.hasTag("book")
        - file.inFolder("Required Reading")
```

**Known filter functions:**

| Function | Meaning |
|---|---|
| `file.hasTag("x")` | Note carries the tag |
| `file.hasLink("x")` | Note links to `x` |
| `file.inFolder("path")` | Note is in that folder |

Plain expressions also work as filter strings — `'status != "done"'`, `'price > 2.1'`.

### 3.2 Property namespaces

| Namespace | Refers to |
|---|---|
| `file.*` | File metadata — `file.name`, `file.ext`, `file.mtime`, `file.ctime` |
| `note.*` | A property from the note's YAML frontmatter |
| `formula.*` | A formula defined in this file |

⚠️ **Least-confident area.** The published examples reference frontmatter properties *bare* inside filter expressions (`status != "done"`) but *namespaced* inside `order` and `groupBy` (`note.age`). `Worklog.base` follows that split exactly — bare in filters, `note.`-prefixed in `order`/`groupBy`/`properties`. If columns render empty, this is the first thing to test.

### 3.3 Formulas

String expressions, referenced elsewhere as `formula.<name>`:

```yaml
formulas:
  formatted_price: 'if(price, price.toFixed(2) + " dollars")'
  ppu: "(price / age).toFixed(2)"
```

Operators: `+ - * /`, comparisons `> < == !=`, boolean `&&`. Dates support arithmetic with quoted duration strings:

```text
file.mtime > now() - '7d'
start_date + "2w"
if(due_date < now() && status != "Done", "Overdue", "")
```

### 3.4 Properties block

Controls how a column is labelled:

```yaml
properties:
  status:
    displayName: Status
  formula.formatted_price:
    displayName: "Price"
  file.ext:
    displayName: Extension
```

### 3.5 Views

```yaml
views:
  - type: table
    name: "My table"
    limit: 10
    groupBy:
      property: note.age
      direction: DESC
    filters:
      and:
        - 'status != "done"'
    order:
      - file.name
      - note.age
      - formula.ppu
    summaries:
      formula.ppu: Average
```

| Key | Purpose |
|---|---|
| `type` | `table` is the documented type |
| `name` | Tab label in Obsidian |
| `limit` | Max rows |
| `groupBy` | `property` + `direction` (`ASC` / `DESC`) |
| `filters` | Narrows beyond the file-level filters |
| `order` | Column order, left to right |
| `summaries` | Per-column aggregation |

⚠️ **Unverified:** whether `order` also controls *sort* order or only *column* order. The docs call it column order. `Worklog.base` puts `note.created` first in every view assuming sorting is a UI control — **if entries render in the wrong order, that assumption is why.**

## 4. Worked example — `_meta/Worklog.base`

The first Base in this vault. It renders `_meta/worklog_entries/` as Palladia's local worklog.

**Design decisions worth reusing:**

- **File-level filter pins the folder.** `file.inFolder("_meta/worklog_entries")` plus `file.ext == "md"` means it can never accidentally pick up case notes from `casing/casing-session_log/`, which also carry frontmatter.
- **A formula enforces a rule that would otherwise rot.** `summary_overflow` shows `OVER by N` when a summary exceeds 280 characters. A cap nobody can see is a cap nobody keeps.
- **Four views, each earning its place:** *All entries* (the default), *Last 7 days* (the "what did we do this week" cut), *By type* (shows where effort is actually going), *Scored reps* (case + behavioral scores only).

**Frontmatter contract it reads:** `created`, `author`, `project`, `type`, `summary` (≤280), `tags`, `case_id`, `dimensions`. Full definitions live in `_meta/template_library/Worklog_Entry_template.md`.

## 5. Placement conventions

- **Put the `.base` beside the folder it renders, not inside it.** `Worklog.base` sits in `_meta/`, one level above `worklog_entries/`. Obsidian surfaces `.base` files as documents in the file explorer, so a Base living inside its own data folder would appear in the middle of the entries it renders.
- **Name it as it should read as a document title.** Obsidian shows the filename. `Worklog.base` displays as "Worklog".
- **One Base per subject.** A second Base for casing is planned and deliberately separate.

## 6. CONFIRM AFTER FIRST RENDER

Work this list the first time `Worklog.base` is opened in Obsidian. Until then, nothing in this document is confirmed.

- [ ] **The file opens as a Base at all** — not as plain text. If it opens as text, the extension or the Bases plugin is the problem, not the syntax.
- [ ] **All four views appear** as tabs: All entries · Last 7 days · By type · Scored reps.
- [ ] **A test entry appears** — create one from the template and confirm it shows up.
- [ ] **Columns are populated, not empty.** Empty columns ⇒ the `note.` prefix convention in §3.2 is wrong. Try bare property names in `order`/`properties`.
- [ ] **`displayName` labels render** ("When", "Help level", "⚠ Summary") rather than raw property keys.
- [ ] **The `summary_overflow` formula computes.** Write a deliberately >280-char summary and confirm it flags. Tests both `.length` on a string property and `if()`.
- [ ] **`Last 7 days` filters correctly** — tests `now() - '7d'` and bare property reference in a filter.
- [ ] **`By type` groups** — tests `groupBy` with a `note.`-prefixed property.
- [ ] **`Scored reps` filters on an `or` of two equality expressions.**
- [ ] **Sort order** — are entries newest-first, or is `order` column-order only? See the §3.5 warning.
- [ ] **Templates plugin points somewhere.** Settings → Templates → template folder. It is **enabled but unconfigured**; set it to `_meta/template_library` or the entry template cannot be inserted.

**After confirming:** correct every ⚠️ in this document, mark verified sections ✅, and fill §7.

## 7. Reusable template — PLACEHOLDER

> **Not written yet, deliberately.** Promoting a template before a single Base has rendered would propagate any syntax error into every future Base.
>
> Once §6 passes, extract the confirmed skeleton here — file-level folder filter, a `properties` block with display names, and a multi-view stanza — as the copy-paste starting point for the casing Base and everything after it.

## 8. Open questions

1. **Is `type: table` the only view type?** Cards and list views may exist; the retrieved docs only show `table`.
2. **Can a Base span multiple folders?** `file.inFolder` composed under `or` presumably works, untested.
3. **`summaries` semantics** — the docs show `customAverage: 'values.mean().round(3)'` at file level and `formula.ppu: Average` at view level. The relationship between the two forms is not clear from the retrieved material. `Worklog.base` uses neither.
4. **Does a Base see properties from nested subfolders?** Matters if `worklog_entries/` is ever month-sharded.
