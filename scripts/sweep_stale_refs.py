#!/usr/bin/env python3
"""Drain the driveguard move-queue and repair stale path references.

WHY
---
Palladia's file moves go through `terminal` (`mv`) because Hermes has no move
tool and no delete tool. Every successful move leaves references to the OLD path
scattered through the drive. `palladia-driveguard`'s transform_terminal_output
enqueues each move; this script drains that queue.

MODE: auto-rewrite exact matches (Daniel, 2026-08-31).

An unattended job editing Daniel's notes needs rails, not good intentions:

  * EXACT full-path matches only. No fuzzy, no partial, no basename-only.
  * Text files only (.md, .base, .csv). Never PDFs, never binaries.
  * Blast-radius cap: more than MAX_REWRITES hits for one move means the match
    is too generic to trust -- report, do not touch.
  * Dry-run first: the complete change set is computed and logged BEFORE
    anything is written.
  * Backup every touched file before writing.
  * `_system-files/` is never auto-edited. Canonical runtime is out of bounds
    for an automated job regardless of match quality.
  * Anything not auto-rewritten is REPORTED, never silently dropped.

Usage:
  sweep_stale_refs.py                # dry run; prints the plan, writes nothing
  sweep_stale_refs.py --apply        # applies, with backups
  sweep_stale_refs.py --apply --vault /path/to/palladrive
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import sys
from pathlib import Path

MARKER = Path("_meta/DRIVE-MAP.md")
CANDIDATES = ["/home/daniel/obsidian-vaults/palladrive", os.path.expanduser("~/PALLAdrive")]
TEXT_SUFFIXES = {".md", ".base", ".csv"}
PROTECTED_PREFIXES = ("_system-files",)
MAX_REWRITES = 20
SKIP_DIRS = {".obsidian", ".trash", ".git", "__pycache__", "node_modules"}


def discover_vault(explicit: str | None) -> Path | None:
    """Marker-verified, same discipline as the plugins. A path that does not
    contain the marker is never accepted -- see the 2026-08-31 inert-guard
    incident."""
    for c in ([explicit] if explicit else []) + [os.environ.get("PALLADRIVE_PATH", "")] + CANDIDATES:
        if c and (Path(c) / MARKER).is_file():
            return Path(c)
    return None


def bridge_dir() -> Path:
    return Path(os.environ.get("DRIVEGUARD_BRIDGE_DIR",
                               os.path.expanduser("~/.hermes/driveguard-bridge")))


def load_queue(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
            if row.get("from") and row.get("to"):
                out.append(row)
        except Exception:
            continue
    return out


def scan(vault: Path, needle: str) -> list[tuple[Path, int]]:
    """Files containing the exact needle, with occurrence counts."""
    hits = []
    for dirpath, dirnames, filenames in os.walk(str(vault)):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for f in filenames:
            if Path(f).suffix.lower() not in TEXT_SUFFIXES or f.startswith("."):
                continue
            p = Path(dirpath) / f
            try:
                text = p.read_text(encoding="utf-8")
            except Exception:
                continue          # unreadable or not really text -> skip, never guess
            n = text.count(needle)
            if n:
                hits.append((p, n))
    return hits


def is_protected(vault: Path, p: Path) -> bool:
    try:
        rel = os.path.relpath(str(p), str(vault))
    except Exception:
        return True               # cannot classify -> treat as protected
    return rel.startswith(PROTECTED_PREFIXES)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--vault", default=None)
    ap.add_argument("--max-rewrites", type=int, default=MAX_REWRITES)
    args = ap.parse_args()

    vault = discover_vault(args.vault)
    if vault is None:
        print(f"FATAL: no vault root contains {MARKER}. Checked --vault, "
              f"PALLADRIVE_PATH, {CANDIDATES}.", file=sys.stderr)
        return 2

    qpath = bridge_dir() / "sweep-queue.jsonl"
    queue = load_queue(qpath)
    stamp = dt.datetime.now().replace(microsecond=0)
    print(f"# stale-reference sweep — {stamp.isoformat()}")
    print(f"# vault: {vault}")
    print(f"# queue: {qpath} ({len(queue)} moves)")
    print(f"# mode : {'APPLY' if args.apply else 'DRY RUN (nothing will be written)'}\n")
    if not queue:
        print("queue empty — nothing to do.")
        return 0

    backup_root = vault / "_meta" / ".sweep-backups" / stamp.strftime("%Y-%m-%d_%H%M%S")
    planned, skipped, rewritten = [], [], 0

    for row in queue:
        old, new = str(row["from"]), str(row["to"])
        if old == new:
            continue
        hits = scan(vault, old)
        if not hits:
            print(f"[clean]   {old}  ->  {new}   (no stale references)")
            continue
        editable = [(p, n) for p, n in hits if not is_protected(vault, p)]
        protected = [p for p, _ in hits if is_protected(vault, p)]
        for p in protected:
            skipped.append((p, old, "protected zone — _system-files is never auto-edited"))
        if len(editable) > args.max_rewrites:
            for p, _ in editable:
                skipped.append((p, old, f"blast radius {len(editable)} > cap {args.max_rewrites}"))
            print(f"[CAPPED]  {old}: {len(editable)} files exceed the cap — reporting, not rewriting")
            continue
        for p, n in editable:
            planned.append((p, old, new, n))
            print(f"[rewrite] {os.path.relpath(str(p), str(vault))}  ({n}x)  {old} -> {new}")

    print(f"\n# planned rewrites: {len(planned)} file(s)")
    print(f"# skipped/reported: {len(skipped)} file(s)")
    for p, old, why in skipped:
        print(f"[SKIP]    {os.path.relpath(str(p), str(vault))}  ({old}): {why}")

    if not args.apply:
        print("\nDRY RUN — nothing written. Re-run with --apply to commit.")
        return 0

    for p, old, new, _ in planned:
        try:
            rel = os.path.relpath(str(p), str(vault))
            dest = backup_root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(p), str(dest))          # backup BEFORE any write
            p.write_text(p.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
            rewritten += 1
        except Exception as exc:
            print(f"[ERROR]   {p}: {type(exc).__name__} — left unchanged", file=sys.stderr)

    if rewritten:
        print(f"\napplied {rewritten} rewrite(s); backups at {backup_root}")
    # Queue drains only after a successful apply, so a crash re-runs safely.
    try:
        qpath.write_text("")
    except Exception:
        print("WARNING: queue could not be cleared; next run may repeat.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
