# Cron job draft — `palladia-stale-ref-sweep`

**Author:** ChiefPM · 2026-08-31
**Daniel reviewed:** no
**Status:** 🟡 **READY TO INSTALL.** Script built and rail-tested on a throwaway tree; nothing installed on `olympus1` yet.
**Job class:** **DERIVATION** — repairs references from known local state; discovers nothing.
**Depends on:** `palladia-driveguard` (writes the queue this job drains) and `../scripts_library/sweep_stale_refs.py`.

---

## Purpose

Palladia moves files with `terminal` (`mv`) because Hermes has **no move tool and no delete tool** — verified against `model_tools.py` at tag `v2026.8.18`. Every move leaves references to the old path scattered through the drive. Stale links are Daniel's named complaint and they accumulate silently.

`palladia-driveguard`'s `transform_terminal_output` enqueues each **successful** move (`returncode == 0`) to `sweep-queue.jsonl`. This job drains that queue.

**No model call.** Stage 2 is deterministic `grep` + exact-string rewrite. A cheap-model pass over the ambiguous residue is designed but deferred — see *Deferred* below.

---

## Job specification

```yaml
name: Palladia — Stale Reference Sweep
profile: palladia
schedule:
  kind: cron
  expr: "30 10 * * *"         # 10:30 UTC daily — after the primer refresh
enabled: true
provider: null                 # NO MODEL. Pure script execution.
model: null
enabled_toolsets: [terminal]
context_from: []
deliver: local
job_class: derivation
command: >
  python3 ~/obsidian-vaults/palladrive/_system-files/scripts_library/sweep_stale_refs.py --apply
state_file: null               # the queue file IS the state; it drains on success
```

---

## Mode: auto-rewrite exact matches

**Daniel's call, 2026-08-31.** He was offered report-only and chose auto-rewrite.

An unattended job editing his notes needs rails, not good intentions. All seven are implemented in the script and verified on a throwaway tree:

| Rail | Behaviour | Verified |
|---|---|---|
| Exact full-path only | No fuzzy, no partial, no basename-only | ✅ |
| Text files only | `.md`, `.base`, `.csv`. PDFs and binaries skipped | ✅ PDF untouched |
| Blast-radius cap | >20 hits for one move → report, do not touch | ✅ fired at 25 |
| Dry-run first | Full change set computed and printed before any write | ✅ default mode |
| Backup before write | `_meta/.sweep-backups/<timestamp>/<relpath>` | ✅ 2 files backed up |
| Never `_system-files` | Canonical runtime is never auto-edited | ✅ reported, not rewritten |
| Report, never drop | Everything not rewritten is printed with a reason | ✅ |

Backups land under a **dotfolder**, so `gen_drive_map.py` skips them and they do not inflate the map.

The queue drains only **after** a successful apply, so a crash mid-run re-runs safely.

---

## Verification before enabling

Run once by hand in dry-run and read the output:

```bash
python3 _system-files/scripts_library/sweep_stale_refs.py
```

It writes nothing without `--apply`. Confirm the planned rewrites look right on a real queue before scheduling it unattended.

---

## Deferred — stage 3 (cheap-model residue pass)

Exact matching cannot judge prose mentions, partial paths, or renamed concepts. A cheap-model subagent (`openai-codex/5.6-luna`, Daniel 2026-08-31) over the **residue only** is designed but **not built**, and is blocked on one thing:

> The worklog records a deliberate configuration stopping Hermes from silently failing over from the OpenAI Codex subscription to per-token billing (`JARVIS_STT_OPENAI_KEY` naming decision, 2026-08-30). A **cron-driven** subagent is precisely the shape that bills quietly every night. Vulcan must confirm routing and verify the first live run bills against the subscription before this is enabled.

Stage 2 has no model call and therefore no billing exposure. It can ship alone.
