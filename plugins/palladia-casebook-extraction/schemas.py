"""Model-facing schemas for bounded casebook extraction."""

CASEBOOK_LOCATE_CASE = {
    "name": "casebook_locate_case",
    "description": (
        "Read-only bounded locator for one named case in one named Palladia casebook. "
        "Builds a piecewise printed-page to physical-page mapping from TOC/outline/title "
        "anchors, verifies the selected case title and the next-case boundary, and reports "
        "section evidence. Never scans or returns the full PDF. Use before extraction when "
        "Daniel asks to inspect the mapping or when a prior extraction was refused."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "catalog": {
                "type": "string",
                "description": "Named catalog or unique school/filename fragment, e.g. Darden or Catalog_Darden-casebook-2024-25.pdf.",
            },
            "case_name": {
                "type": "string",
                "description": "Exact case title to locate. Ambiguous or unverified matches are refused.",
            },
        },
        "required": ["catalog", "case_name"],
        "additionalProperties": False,
    },
}

CASEBOOK_EXTRACT_CASE = {
    "name": "casebook_extract_case",
    "description": (
        "Extract exactly one verified case from one named Palladia casebook. The tool itself "
        "performs bounded TOC/outline/title resolution, independently verifies the case start "
        "and next-case boundary, preserves the complete contiguous case (prompt, exhibits, "
        "interviewer guidance, solution), and writes only "
        "casing/individual_cases/<Case Name>/<Case Name>.pdf plus index.md. "
        "It refuses ambiguous catalogs/cases, missing section evidence, unverified ranges, "
        "unsafe names, page-budget overrun, and every overwrite attempt. Never use generic "
        "PDF/OCR/full-catalog tools for this workflow."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "catalog": {
                "type": "string",
                "description": "Named catalog or unique school/filename fragment, e.g. Darden or Catalog_Darden-casebook-2024-25.pdf.",
            },
            "case_name": {
                "type": "string",
                "description": "Exact case title. Original capitalization and spaces become the output folder/file name.",
            },
        },
        "required": ["catalog", "case_name"],
        "additionalProperties": False,
    },
}
