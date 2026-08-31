# Palladia Casebook Extraction

Profile-local Hermes plugin providing two tools:

- `casebook_locate_case` — read-only bounded page-mapping and boundary verification.
- `casebook_extract_case` — performs the same verification, then writes exactly one case PDF and `index.md`.

## Safety contract

- Named case + named catalog only.
- Never scans or returns an entire catalog.
- Uses independent TOC/outline/title anchors and records a piecewise printed→physical mapping.
- Requires the selected title on the first page and the next case title at the end boundary.
- Refuses ambiguity, page-budget overruns, missing prompt/exhibit/guidance/solution evidence, unsafe names, and overwrite attempts.
- Writes only under `casing/individual_cases/<Case Name>/`.
- Does not call `pdftotext`, OCR, or generic file/PDF tools.

## Verification

```bash
hermes plugins doctor . --ci
python -m pytest tests -q
```

This is a local MVP. It requires CTO audit and hardening before external/client use or production deployment.
