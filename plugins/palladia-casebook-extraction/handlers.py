"""Bounded, fail-closed casebook extraction primitives."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re
import shutil
import tempfile
import unicodedata
from typing import Any, Iterable

import pymupdf
import yaml


CASING_RELATIVE = Path("casing")
CATALOG_RELATIVE = CASING_RELATIVE / "casebooks_catalogs"
OUTPUT_RELATIVE = CASING_RELATIVE / "individual_cases"


@dataclass(frozen=True)
class PageAnchor:
    printed_page: int
    physical_page: int
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class PaginationSegment:
    physical_start: int
    physical_end: int
    printed_start: int
    printed_end: int
    start_offset: int
    end_offset: int
    discontinuity: str


def _normalize_literal(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).casefold()
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def _normalize(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).casefold()
    text = re.sub(r"\bslide\s+\d+\s*:\s*", "", text)
    text = re.sub(r"\bcase\s*#?\s*\d+\s*:\s*", "", text)
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def _fs_safe(name: str) -> str:
    """Strip filesystem- and link-hostile characters from a name.

    The case TITLE is preserved verbatim everywhere it is matched against the
    PDF or shown to a reader; this is applied ONLY at the write path, to the
    folder name and the artifact stem.

    ``Shisha: Just Blowing Smoke?`` -> ``Shisha Just Blowing Smoke``

    Observed 2026-08-31: the extractor wrote that title straight into a path.
    Legal on Linux, but ``:`` breaks macOS and Windows, ``?`` breaks URLs and
    Obsidian wikilinks, and the drive syncs across all three. A trailing dot or
    space is silently dropped by some filesystems, which is worse than an error.
    """
    cleaned = re.sub(r'[:?*"<>|\\/]+', " ", name)
    cleaned = " ".join(cleaned.split())
    return cleaned.rstrip(". ")


def _safe_case_name(case_name: str) -> str | None:
    clean = " ".join(str(case_name).split()).strip()
    if not clean or len(clean) > 120:
        return None
    if clean in {".", ".."} or any(ch in clean for ch in ("/", "\\", "\x00", "\r", "\n")):
        return None
    return clean


def _resolve_catalog(vault_root: Path, query: str) -> tuple[Path | None, dict[str, Any] | None]:
    catalog_dir = (vault_root / CATALOG_RELATIVE).resolve()
    if not catalog_dir.is_dir():
        return None, {"status": "refused", "reason": "catalog_directory_missing"}
    candidates = sorted(p for p in catalog_dir.glob("Catalog_*.pdf") if p.is_file())
    needle = _normalize(Path(str(query)).name)
    if not needle:
        return None, {"status": "refused", "reason": "catalog_required"}

    exact = [p for p in candidates if _normalize(p.name) == needle or _normalize(p.stem) == needle]
    matches = exact or [p for p in candidates if needle in _normalize(p.name)]
    if len(matches) != 1:
        return None, {
            "status": "ambiguous" if matches else "not_found",
            "reason": "catalog_match_not_unique" if matches else "catalog_not_found",
            "candidates": [p.name for p in matches],
        }
    chosen = matches[0].resolve()
    if chosen.parent != catalog_dir:
        return None, {"status": "refused", "reason": "catalog_path_escape"}
    return chosen, None


def _row_words(page: pymupdf.Page, rect: pymupdf.Rect) -> list[tuple]:
    center = (rect.y0 + rect.y1) / 2
    tolerance = max(7.0, rect.height)
    return [
        word
        for word in page.get_text("words")
        if abs(((word[1] + word[3]) / 2) - center) <= tolerance
    ]


def _rightmost_page_number(words: Iterable[tuple], width: float) -> tuple[int, float] | None:
    candidates: list[tuple[float, int]] = []
    for word in words:
        token = str(word[4]).strip()
        if word[0] >= width * 0.62 and re.fullmatch(r"\d{1,4}", token):
            candidates.append((float(word[0]), int(token)))
    if not candidates:
        return None
    x, value = max(candidates)
    return value, x


def _title_band(page: pymupdf.Page, rect: pymupdf.Rect, row: list[tuple]) -> tuple[float, float]:
    later = sorted(
        (word for word in row if word[0] > rect.x1 + 8 and word[0] < page.rect.width * 0.62),
        key=lambda word: word[0],
    )
    right = ((rect.x1 + later[0][0]) / 2) if later else page.rect.width * 0.42
    return max(0.0, rect.x0 - 12), right


def _next_index_row(page: pymupdf.Page, rect: pymupdf.Rect, title_band: tuple[float, float]) -> tuple[str, int] | None:
    words = page.get_text("words")
    baselines = sorted({round(float(word[1]), 1) for word in words if word[1] > rect.y1 + 2})
    for baseline in baselines:
        row = [word for word in words if abs(float(word[1]) - baseline) <= 1.6]
        page_number = _rightmost_page_number(row, page.rect.width)
        if page_number is None:
            continue
        title_tokens = [
            str(word[4])
            for word in sorted(row, key=lambda word: word[0])
            if title_band[0] <= word[0] < title_band[1]
            and not re.fullmatch(r"\d+", str(word[4]).strip())
        ]
        title = " ".join(title_tokens).strip(" -–—:;")
        if title:
            return title, page_number[0]
    return None


def _find_index_entry(doc: pymupdf.Document, case_name: str, max_index_pages: int, inspected: set[int]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    matches: list[dict[str, Any]] = []
    limit = min(doc.page_count, max(1, max_index_pages))
    for page_index in range(limit):
        page = doc.load_page(page_index)
        inspected.add(page_index)
        for rect in page.search_for(case_name):
            row = _row_words(page, rect)
            printed = _rightmost_page_number(row, page.rect.width)
            if printed is None:
                continue
            next_row = _next_index_row(page, rect, _title_band(page, rect, row))
            if next_row is None:
                continue
            matches.append(
                {
                    "index_page": page_index + 1,
                    "printed_start": printed[0],
                    "next_case": next_row[0],
                    "next_printed_start": next_row[1],
                }
            )
    unique = {
        (m["printed_start"], _normalize(m["next_case"]), m["next_printed_start"]): m
        for m in matches
    }
    if len(unique) != 1:
        return None, {
            "status": "ambiguous" if unique else "not_found",
            "reason": "case_index_match_not_unique" if unique else "case_not_found_in_bounded_index_scan",
            "candidates": list(unique.values()),
            "max_index_pages": limit,
        }
    return next(iter(unique.values())), None


def _running_header(page: pymupdf.Page) -> tuple[int, str] | None:
    """Parse a casebook running header of the form ``NN | CASE TITLE``.

    Darden-style casebooks print an incrementing per-case counter beside the
    case name on every page of that case, resetting to 1 on the case's first
    page.  That reset is the most reliable case boundary in the document, so it
    is read as a first-class anchor rather than filtered out.

    The header is typeset with letter-spacing, so the raw text extracts as
    ``0 1 | K E G G I N G   C O S T S``.  Whitespace is therefore stripped from
    the counter and the title is normalized before comparison -- matching on the
    raw string does not work and was the original cause of this parser failing
    silently on every Darden case.

    Returns ``(counter, normalized_title)`` for the first header-shaped line in
    the page's top band, or ``None`` when the page carries no header.
    """
    for line in page.get_text("text").splitlines()[:14]:
        if "|" not in line:
            continue
        left, _, right = line.partition("|")
        counter = re.sub(r"\s+", "", left)
        if not re.fullmatch(r"\d{1,2}", counter):
            continue
        title = _normalize(right)
        if title:
            return int(counter), title
    return None


def _title_line_index(page: pymupdf.Page, title: str) -> int | None:
    """Index of the first standalone whole-line title match within the page's
    top content band, ignoring pure printed-page-number lines.  Running headers
    are excluded here (their ``NN |`` prefix breaks letters-only equality) and
    mid-page body mentions are excluded because they sit below the band.
    Returns None when the title is not a standalone line near the top."""
    tc = "".join(re.findall(r"[a-z0-9]+", title.casefold()))
    if not tc:
        return None
    content = 0
    for line in page.get_text("text").splitlines()[:12]:
        stripped = line.strip()
        if not stripped:
            continue
        if re.fullmatch(r"\d{1,4}", stripped):
            continue
        content += 1
        if content > 6:
            return None
        if "".join(re.findall(r"[a-z0-9]+", stripped.casefold())) == tc:
            return content - 1
    return None


def _page_starts_case(page: pymupdf.Page, title: str) -> bool:
    """True only when this page is the FIRST page of the named case.

    Two independent signals, in confidence order:

    1. Running-header counter reset -- ``01 | <TITLE>``.  Unambiguous where the
       casebook prints headers, and immune to the repeated-title collision that
       made every later page of a case look like its start.
    2. Standalone title line in the top band, for casebooks with no headers.

    A page carrying a running header with counter > 1 is explicitly NOT a start,
    even if signal 2 would otherwise fire on it.
    """
    header = _running_header(page)
    wanted = _normalize(title)
    if header is not None:
        counter, header_title = header
        if header_title != wanted and wanted not in header_title:
            return False
        return counter == 1
    return _title_line_index(page, title) is not None


def _page_has_title(page: pymupdf.Page, title: str) -> bool:
    if page.search_for(title):
        return True
    wanted = _normalize(title)
    if not wanted:
        return False
    lines = page.get_text("text").splitlines()[:40]
    return any(wanted == _normalize(line) or wanted in _normalize(line) for line in lines)


def _outline_candidates(doc: pymupdf.Document, title: str) -> list[int]:
    literal = _normalize_literal(title)
    rows = doc.get_toc(simple=True)
    primary = {
        int(page_number)
        for _level, outline_title, page_number in rows
        if page_number > 0 and _normalize_literal(outline_title) == literal
    }
    if primary:
        return sorted(primary)
    wanted = _normalize(title)
    pages = {
        int(page_number)
        for _level, outline_title, page_number in rows
        if page_number > 0 and _normalize(outline_title) == wanted
    }
    return sorted(pages)


def _bounded_title_candidates(
    doc: pymupdf.Document,
    title: str,
    printed_page: int,
    search_radius: int,
    inspected: set[int],
) -> list[int]:
    # Printed page labels are offset from physical indices (covers, roman front
    # matter, per-section inserts).  Search the tight window first and only widen
    # to a full radius on each side when it yields nothing -- the unconditional
    # 2x window inspected ~72 pages per anchor and tripped the page budget on
    # every mid-book case, which read as a boundary failure but was not one.
    radius = max(0, search_radius)
    windows = ((radius, radius), (2 * radius, 2 * radius))
    for back, forward in windows:
        start = max(1, printed_page - back)
        end = min(doc.page_count, printed_page + forward)
        found = []
        for physical in range(start, end + 1):
            page = doc.load_page(physical - 1)
            inspected.add(physical - 1)
            if _page_starts_case(page, title):
                found.append(physical)
        found = _collapse_runs(found)
        if found:
            return found
    return []


def _collapse_runs(pages: list[int]) -> list[int]:
    """Reduce each run of consecutive start-candidates to its first page.

    A case commonly opens with a section divider carrying the title, followed
    immediately by the first content page carrying ``01 | TITLE``.  Both are
    genuine start signals for the same case; treating them as two candidates
    made every such case look ambiguous.  Non-adjacent candidates are left
    alone -- those are real ambiguity and must still refuse.
    """
    collapsed: list[int] = []
    for page in sorted(pages):
        if not collapsed or page != collapsed[-1] + 1:
            collapsed.append(page)
        else:
            collapsed[-1] = collapsed[-1]
    return collapsed


def _resolve_title_anchor(
    doc: pymupdf.Document,
    title: str,
    printed_page: int,
    search_radius: int,
    inspected: set[int],
) -> tuple[PageAnchor | None, dict[str, Any] | None]:
    outline = _outline_candidates(doc, title)
    verified_outline: list[int] = []
    for physical in outline:
        page = doc.load_page(physical - 1)
        inspected.add(physical - 1)
        if _page_starts_case(page, title):
            verified_outline.append(physical)
    verified_outline = _collapse_runs(verified_outline)
    if len(verified_outline) == 1:
        return PageAnchor(printed_page, verified_outline[0], ("toc_match", "outline_match", "title_match")), None
    if len(verified_outline) > 1:
        return None, {"status": "ambiguous", "reason": "multiple_verified_outline_matches", "physical_pages": verified_outline}

    bounded = _bounded_title_candidates(doc, title, printed_page, search_radius, inspected)
    if len(bounded) != 1:
        return None, {
            "status": "ambiguous" if bounded else "refused",
            "reason": "bounded_title_match_not_unique" if bounded else "title_boundary_unverified",
            "physical_pages": bounded,
        }
    return PageAnchor(printed_page, bounded[0], ("toc_match", "title_match")), None


def _detect_sections(doc: pymupdf.Document, start: int, end: int, inspected: set[int]) -> dict[str, bool]:
    chunks: list[str] = []
    for physical in range(start, end + 1):
        page = doc.load_page(physical - 1)
        inspected.add(physical - 1)
        chunks.append(page.get_text("text"))
    text = "\n".join(chunks).casefold()
    return {
        "prompt": bool(re.search(r"\b(candidate\s+)?prompt\b|\bcase\s+prompt\b", text)),
        "exhibits": bool(re.search(r"\bexhibit\s*\d*\b", text)),
        "interviewer_guidance": bool(
            re.search(
                r"\binterviewer\s+(guidance|guide|only|information)\b"
                r"|\bguidance\s+for\s+(the\s+)?interviewer\b"
                r"|\b(framework|exhibit\s+or\s+question|brainstorming)\s+guidance\b",
                text,
            )
        ),
        "solution": bool(
            re.search(
                r"\bsolution\b|\bsample\s+answer\b|\banswer\s+key\b"
                r"|\bsuggested\s+approach\b|\brecommendation\b|\bwe\s+recommend\b",
                text,
            )
        ),
    }


def locate_case(
    *,
    vault_root: str | Path,
    catalog_query: str,
    case_name: str,
    max_index_pages: int = 32,
    search_radius: int = 18,
    max_inspected_pages: int = 96,
) -> dict[str, Any]:
    """Resolve and verify one case without scanning the complete catalog."""
    if max_inspected_pages < 1:
        return {"status": "refused", "reason": "invalid_page_budget", "inspected_pages": 0}
    clean_case = _safe_case_name(case_name)
    if clean_case is None:
        return {"status": "refused", "reason": "unsafe_case_name"}
    root = Path(vault_root).expanduser().resolve()
    catalog, error = _resolve_catalog(root, catalog_query)
    if error is not None:
        return error
    assert catalog is not None

    inspected: set[int] = set()
    try:
        doc = pymupdf.open(catalog)
    except Exception as exc:  # fail closed; never surface path-rich exception text
        return {"status": "refused", "reason": "catalog_open_failed", "error_type": type(exc).__name__}

    try:
        entry, error = _find_index_entry(
            doc,
            clean_case,
            min(max_index_pages, max_inspected_pages),
            inspected,
        )
        if error is not None:
            error["catalog"] = catalog.name
            error["inspected_pages"] = len(inspected)
            return error
        assert entry is not None

        start_anchor, error = _resolve_title_anchor(
            doc, clean_case, entry["printed_start"], search_radius, inspected
        )
        if error is not None:
            return {**error, "catalog": catalog.name, "boundary": "start", "inspected_pages": len(inspected)}
        next_anchor, error = _resolve_title_anchor(
            doc,
            entry["next_case"],
            entry["next_printed_start"],
            search_radius,
            inspected,
        )
        if error is not None:
            return {**error, "catalog": catalog.name, "boundary": "end", "inspected_pages": len(inspected)}
        assert start_anchor is not None and next_anchor is not None
        if next_anchor.physical_page <= start_anchor.physical_page:
            return {
                "status": "refused",
                "reason": "non_monotonic_verified_boundaries",
                "catalog": catalog.name,
                "inspected_pages": len(inspected),
            }

        physical_end = next_anchor.physical_page - 1
        printed_end = next_anchor.printed_page - 1
        projected_pages = inspected | set(
            range(start_anchor.physical_page - 1, physical_end)
        )
        if len(projected_pages) > max_inspected_pages:
            return {
                "status": "refused",
                "reason": "bounded_page_budget_exceeded",
                "catalog": catalog.name,
                "inspected_pages": len(inspected),
                "max_inspected_pages": max_inspected_pages,
                "projected_pages": len(projected_pages),
            }
        next_inside = any(
            _page_starts_case(doc.load_page(page - 1), entry["next_case"])
            for page in range(start_anchor.physical_page, physical_end + 1)
        )
        sections = _detect_sections(doc, start_anchor.physical_page, physical_end, inspected)
        segment = PaginationSegment(
            physical_start=start_anchor.physical_page,
            physical_end=physical_end,
            printed_start=start_anchor.printed_page,
            printed_end=printed_end,
            start_offset=start_anchor.physical_page - start_anchor.printed_page,
            end_offset=next_anchor.physical_page - next_anchor.printed_page,
            discontinuity=(
                "offset_changed"
                if start_anchor.physical_page - start_anchor.printed_page
                != next_anchor.physical_page - next_anchor.printed_page
                else "none"
            ),
        )
        return {
            "status": "verified",
            "catalog": catalog.name,
            "case_name": clean_case,
            "next_case": entry["next_case"],
            "physical_pages": {"start": start_anchor.physical_page, "end": physical_end},
            "printed_pages": {"start": start_anchor.printed_page, "end": printed_end},
            "anchors": [
                {**asdict(start_anchor), "evidence": list(start_anchor.evidence)},
                {**asdict(next_anchor), "evidence": list(next_anchor.evidence)},
            ],
            "segments": [asdict(segment)],
            "boundary_verification": {
                "first_page_has_case_title": _page_starts_case(doc.load_page(start_anchor.physical_page - 1), clean_case),
                "next_page_has_next_case_title": _page_starts_case(doc.load_page(next_anchor.physical_page - 1), entry["next_case"]),
                "next_case_title_inside_extraction": next_inside,
            },
            "sections": sections,
            "index_page": entry["index_page"],
            "inspected_pages": len(inspected),
            "catalog_page_count": doc.page_count,
        }
    finally:
        doc.close()


def _book_slug(catalog_filename: str) -> str:
    """``Catalog_Darden-casebook-2024-25.pdf`` -> ``Darden2024-2025``.

    Matches the on-disk convention set by ``HR Co``.  School and years are split
    on the literal ``casebook`` token (either ``-`` or ``_`` separated), and a
    two-digit end year is expanded against its start year so ``2024-25`` and
    ``2024-2025`` both render identically.
    """
    stem = Path(catalog_filename).stem.removeprefix("Catalog_")
    parts = re.split(r"[-_]casebook[-_]?", stem, maxsplit=1)
    school = parts[0].strip("-_ ")
    years = parts[1].strip("-_ ") if len(parts) > 1 else ""
    match = re.fullmatch(r"(\d{4})-(\d{2})", years)
    if match:
        years = f"{match.group(1)}-{match.group(1)[:2]}{match.group(2)}"
    return f"{school}{years}"


def _artifact_stem(case_name: str, catalog_filename: str) -> str:
    return f"Case_{_fs_safe(case_name)}_{_book_slug(catalog_filename)}"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _index_document(mapping: dict[str, Any]) -> str:
    metadata = {
        "title": _artifact_stem(mapping["case_name"], mapping["catalog"]),
        "case_title": mapping["case_name"],
        "source_catalog": mapping["catalog"],
        "source_pages_physical": (
            f'{mapping["physical_pages"]["start"]}-{mapping["physical_pages"]["end"]}'
        ),
        "source_pages_printed": (
            f'{mapping["printed_pages"]["start"]}-{mapping["printed_pages"]["end"]}'
        ),
        "extracted": datetime.now(timezone.utc).date().isoformat(),
        "properties": {
            "Case book": None,
            "Case Type": None,
            "Difficulty": None,
            "Quant Diff": None,
            "Qual Diff": None,
            "Industry": None,
            "Sections": [
                "prompt",
                "exhibits",
                "interviewer guidance",
                "solution",
            ],
        },
    }
    frontmatter = yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True).rstrip()
    body = (
        f'Bounded extraction of {mapping["case_name"]} from '
        f'{mapping["catalog"]}. Case content and solution remain in the PDF.'
    )
    return f"---\n{frontmatter}\n---\n\n{body}\n"


def _existing_output_conflict(output_root: Path, case_name: str) -> list[str]:
    wanted = _normalize(case_name)
    conflicts: list[str] = []
    if not output_root.exists():
        return conflicts
    for child in output_root.iterdir():
        candidate = child.stem if child.is_file() else child.name
        if _normalize(candidate) == wanted:
            conflicts.append(child.name)
    return sorted(conflicts)


def extract_case(
    *,
    vault_root: str | Path,
    catalog_query: str,
    case_name: str,
    max_index_pages: int = 32,
    search_radius: int = 18,
    max_inspected_pages: int = 96,
) -> dict[str, Any]:
    """Verify boundaries, then atomically write one PDF and one metadata index."""
    clean_case = _safe_case_name(case_name)
    if clean_case is None:
        return {"status": "refused", "reason": "unsafe_case_name"}
    root = Path(vault_root).expanduser().resolve()
    casing_root = (root / CASING_RELATIVE).resolve()
    catalog_root = (root / CATALOG_RELATIVE).resolve()
    output_path = root / OUTPUT_RELATIVE
    output_root = output_path.resolve()
    expected_output_root = casing_root / "individual_cases"
    if (
        not catalog_root.is_relative_to(root)
        or output_path.is_symlink()
        or output_root != expected_output_root
        or not output_root.is_relative_to(casing_root)
    ):
        return {"status": "refused", "reason": "output_path_escape"}

    conflicts = _existing_output_conflict(output_root, clean_case)
    if conflicts:
        return {
            "status": "refused",
            "reason": "output_exists",
            "conflicts": conflicts,
        }

    mapping = locate_case(
        vault_root=root,
        catalog_query=catalog_query,
        case_name=clean_case,
        max_index_pages=max_index_pages,
        search_radius=search_radius,
        max_inspected_pages=max_inspected_pages,
    )
    if mapping.get("status") != "verified":
        return mapping
    verification = mapping["boundary_verification"]
    if verification != {
        "first_page_has_case_title": True,
        "next_page_has_next_case_title": True,
        "next_case_title_inside_extraction": False,
    }:
        return {**mapping, "status": "refused", "reason": "boundary_verification_failed"}
    missing_sections = [name for name, present in mapping["sections"].items() if not present]
    if missing_sections:
        return {
            **mapping,
            "status": "refused",
            "reason": "required_sections_unverified",
            "missing_sections": missing_sections,
        }

    source, error = _resolve_catalog(root, catalog_query)
    if error is not None or source is None:
        return error or {"status": "refused", "reason": "catalog_resolution_failed"}
    source_hash = _sha256(source)
    output_root.mkdir(parents=True, exist_ok=True)
    conflicts = _existing_output_conflict(output_root, clean_case)
    if conflicts:
        return {"status": "refused", "reason": "output_exists", "conflicts": conflicts}

    temp_dir = Path(tempfile.mkdtemp(prefix=".casebook-extract-", dir=output_root))
    # clean_case stays the TRUE title -- it is matched against the PDF text.
    # Only the on-disk names are sanitized.
    final_dir = output_root / _fs_safe(clean_case)
    pdf_name = f"{_artifact_stem(clean_case, source.name)}.pdf"
    pdf_path = temp_dir / pdf_name
    index_path = temp_dir / "index.md"
    try:
        source_doc = pymupdf.open(source)
        extracted_doc = pymupdf.open()
        try:
            start = mapping["physical_pages"]["start"] - 1
            end = mapping["physical_pages"]["end"] - 1
            extracted_doc.insert_pdf(source_doc, from_page=start, to_page=end)
            extracted_doc.save(pdf_path)
        finally:
            extracted_doc.close()
            source_doc.close()

        index_path.write_text(_index_document(mapping), encoding="utf-8")
        expected_count = (
            mapping["physical_pages"]["end"]
            - mapping["physical_pages"]["start"]
            + 1
        )
        check = pymupdf.open(pdf_path)
        try:
            if check.page_count != expected_count:
                return {**mapping, "status": "refused", "reason": "output_page_count_mismatch"}
            if not _page_starts_case(check.load_page(0), clean_case):
                return {**mapping, "status": "refused", "reason": "output_first_page_title_missing"}
            if any(_page_starts_case(page, mapping["next_case"]) for page in check):
                return {**mapping, "status": "refused", "reason": "next_case_leaked_into_output"}
        finally:
            check.close()

        if _sha256(source) != source_hash:
            return {**mapping, "status": "refused", "reason": "source_catalog_changed"}
        if sorted(path.name for path in temp_dir.iterdir()) != sorted([pdf_name, "index.md"]):
            return {**mapping, "status": "refused", "reason": "unexpected_output_files"}
        if final_dir.exists() or _existing_output_conflict(output_root, clean_case):
            return {"status": "refused", "reason": "output_exists"}
        temp_dir.rename(final_dir)
        return {
            **mapping,
            "status": "extracted",
            "output_directory": str(final_dir),
            "output_pdf": str(final_dir / pdf_name),
            "output_index": str(final_dir / "index.md"),
            "source_catalog_unchanged": True,
        }
    except Exception as exc:  # fail closed; return class only to avoid path/content leaks
        return {
            **mapping,
            "status": "refused",
            "reason": "extraction_failed",
            "error_type": type(exc).__name__,
        }
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
