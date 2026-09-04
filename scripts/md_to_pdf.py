#!/usr/bin/env python3
"""Render a PallaDrive markdown doc to a shareable PDF.

Exists because peers receiving a case feedback sheet do not have a markdown
reader. Deliberately dependency-free: a small converter for the subset of
markdown these documents use, then headless Chrome for the PDF step. No pip
install, nothing added to the vault.

Usage: md_to_pdf.py <input.md> [output.pdf]
"""
from __future__ import annotations
import html as _html
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def resolve_chrome() -> str | None:
    """Return an available Chrome/Chromium executable on macOS or Linux."""
    mac = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    if mac.exists():
        return str(mac)
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return found
    return None

CSS = """
@page { size: Letter; margin: 0.6in 0.65in; }
body { font: 10.5pt/1.5 -apple-system,"Helvetica Neue",Arial,sans-serif; color:#1a1a1a; }
h1 { font-size:20pt; margin:0 0 .2em; border-bottom:2px solid #222; padding-bottom:.15em; }
h2 { font-size:13pt; margin:1.4em 0 .35em; background:#f0f0f0; padding:.28em .5em;
     border-left:3px solid #444; page-break-after:avoid; }
h3 { font-size:11pt; margin:1em 0 .3em; page-break-after:avoid; }
h4 { font-size:10pt; margin:.8em 0 .25em; }
table { border-collapse:collapse; width:100%; margin:.5em 0 .9em; font-size:9.5pt;
        page-break-inside:avoid; }
th,td { border:1px solid #c8c8c8; padding:.32em .5em; text-align:left; vertical-align:top; }
th { background:#ededed; font-weight:600; }
ul { margin:.3em 0 .8em; padding-left:1.3em; }
li { margin:.22em 0; }
blockquote { margin:.6em 0; padding:.5em .8em; background:#f7f7f7;
             border-left:3px solid #999; font-size:9.5pt; }
hr { border:0; border-top:1px solid #ccc; margin:1.4em 0; }
code { background:#f0f0f0; padding:.1em .3em; border-radius:2px; font-size:9pt; }
em { color:#333; }
p { margin:.4em 0; }
"""


def inline(text: str) -> str:
    text = _html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def convert(md: str) -> str:
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)          # drop authoring notes
    out: list[str] = []
    lines = md.split("\n")
    i, list_open = 0, False

    def close_list():
        nonlocal list_open
        if list_open:
            out.append("</ul>")
            list_open = False

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            close_list(); i += 1; continue

        if re.fullmatch(r"-{3,}", stripped):
            close_list(); out.append("<hr>"); i += 1; continue

        heading = re.match(r"^(#{1,4})\s+(.*)", stripped)
        if heading:
            close_list()
            level = len(heading.group(1))
            out.append(f"<h{level}>{inline(heading.group(2))}</h{level}>")
            i += 1; continue

        # table: a pipe row followed by a separator row
        if stripped.startswith("|") and i + 1 < len(lines) and \
                re.fullmatch(r"\|[\s\-:|]+\|", lines[i + 1].strip()):
            close_list()
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            header_blank = all(not c for c in cells)
            out.append("<table>")
            if not header_blank:
                out.append("<tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells) + "</tr>")
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>")
                i += 1
            out.append("</table>"); continue

        if stripped.startswith(">"):
            close_list()
            out.append(f"<blockquote>{inline(stripped.lstrip('> ').strip())}</blockquote>")
            i += 1; continue

        bullet = re.match(r"^(\s*)[-*]\s+(.*)", line)
        if bullet:
            if not list_open:
                out.append("<ul>"); list_open = True
            indent = "" if len(bullet.group(1)) < 2 else " style='margin-left:1.1em'"
            out.append(f"<li{indent}>{inline(bullet.group(2))}</li>")
            i += 1; continue

        numbered = re.match(r"^\s*(\d+)\.\s+(.*)", line)
        if numbered:
            if not list_open:
                out.append("<ul>"); list_open = True
            out.append(f"<li><strong>{numbered.group(1)}.</strong> {inline(numbered.group(2))}</li>")
            i += 1; continue

        close_list()
        out.append(f"<p>{inline(stripped)}</p>")
        i += 1

    close_list()
    return "\n".join(out)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__.strip()); return 2
    src = Path(sys.argv[1])
    dest = Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_suffix(".pdf")
    chrome = resolve_chrome()
    if chrome is None:
        print("error: no Chrome/Chromium executable found", file=sys.stderr); return 1

    body = convert(src.read_text(encoding="utf-8"))
    page = f"<!doctype html><meta charset='utf-8'><style>{CSS}</style>{body}"
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as fh:
        fh.write(page); tmp = fh.name

    subprocess.run(
        [chrome, "--headless", "--disable-gpu", "--no-sandbox", "--no-pdf-header-footer",
         f"--print-to-pdf={dest}", f"file://{tmp}"],
        check=True, capture_output=True, timeout=120,
    )
    if not dest.exists() or dest.stat().st_size == 0:
        print("error: Chrome produced no PDF", file=sys.stderr); return 1
    print(f"{dest}  ({dest.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
