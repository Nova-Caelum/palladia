# Obsidian Bases — verified house rules

**Author:** Chief-PM · 2026-08-29
**Daniel reviewed:** no
**Status:** VERIFIED against a live Obsidian round-trip on `Case Log.base`, not inferred from docs.

Template: `_meta/template_library/_Base Template.base`

## How these were learned

We wrote `Case Log.base` by hand from Obsidian's published syntax. It failed to load. After the fix, Obsidian itself rewrote the file — and **what it wrote back is the authoritative pattern**, because it is the parser's own output rather than our reading of the docs. Everything below is from that round-trip.

## Rules

1. **`groupBy` must carry BOTH `property` and `direction`.** A `groupBy` with only `property` is rejected with `"groupBy" must be a object in view "<name>"` — a misleading message, since the value *is* an object. It just isn't a complete one.

   ```yaml
   groupBy:
     property: "Case Type"
     direction: ASC
   ```

2. **Property names containing spaces, parentheses, or other punctuation work** — quoted in `groupBy.property`, bare in `order` lists. Confirmed live on `Overall Performance`, `(Growth) Feedback`, `Qual Diff`.

3. **Obsidian strips comments on rewrite.** Any `#` comment in a `.base` is deleted the moment Obsidian saves the file. **Design rationale must live in a companion document, never in the `.base` itself.** We lost two explanatory blocks this way.

4. **Filter expressions are written bare, not quoted.** We wrote `- 'Activity == "Taken"'`; Obsidian rewrote it to `- Activity == "Taken"`. Both parse, but match its form.

5. **Key order is not preserved.** Obsidian reorders keys within a view (`limit` moved). Do not rely on file layout for meaning.

6. **Emoji in property names work but are not worth it.** `"💼 Company Style"` parsed fine; renamed to `Company Style` on Daniel's call for legibility.

## Still unverified — do not assume

- **Relative-date filters** such as `created > now() - '7d'`. Used in `Worklog.base` "Last 7 days" but never observed working. **Open that view and confirm it returns rows before trusting it.** If it errors, replace with `limit`-based recency, which is verified.
- **Window/ordinal formulas** — deriving a row's position within a filtered, sorted subset. Documented formula syntax is per-row only. Needed for `taken_seq`; tracked as V2 U12. Not invented.

## The rule that follows from all of this

When a construct cannot be verified from the docs, **build the simplest thing that works, then open the Base in Obsidian and let it rewrite the file.** Its output is the specification. Guessing twice costs more than one round-trip.
