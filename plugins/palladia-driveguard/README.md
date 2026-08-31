# palladia-driveguard — install runbook

Zone policy, duplicate-folder prevention, fuzzy path correction, and a
compression-aware read-gate for PallaDrive writes.

**Ships as three pieces across two hook systems and one script. All three are required.**

| Piece | Canonical | Runtime destination | Loads by |
|---|---|---|---|
| `palladia-driveguard` (plugin) | `_system-files/plugin_library/` | profile plugins dir | `plugins enable` |
| `driveguard-epoch` (**gateway hook**) | `_system-files/hook_library/` | `~/.hermes/hooks/` | **gateway restart** |
| `sweep_stale_refs.py` | `_system-files/scripts_library/` | in place | cron |

The plugin fails **closed** without the gateway hook: no epoch → no bridge → writes blocked.

---

## Install on olympus1

```bash
# 1. Plugin
cp -r _system-files/plugin_library/palladia-driveguard ~/.hermes/profiles/palladia/plugins/
hermes -p palladia plugins enable palladia-driveguard

# 2. Gateway hook — REQUIRES A GATEWAY RESTART to load, and again to remove
cp -r _system-files/hook_library/driveguard-epoch ~/.hermes/hooks/
# restart the gateway here

# 3. Cron (see ../../cron_library/palladia-stale-ref-sweep.md)
```

### Vault path — nothing to configure, but verify

Resolution order: `ctx.get_config("vault_path")` → `PALLADRIVE_PATH` (tests only) → candidate list in `zones.json`, **olympus1 first**.

**A candidate is accepted only if it contains `_meta/DRIVE-MAP.md`.** A stale or wrong-host path cannot win quietly — it fails the marker test and we fall through, or refuse.

On 2026-08-31 the Mac vault moved and the previous version's hardcoded root stopped existing. Every path compared as outside the vault; `pre_tool_call` returned `None` for every write. No block, no audit line, nothing. The marker rule exists so that cannot recur. If no root resolves, **writes are blocked with a configuration error** rather than waved through.

Confirm after install — the `register` line in the audit log names the resolved root:

```bash
tail -1 ~/.hermes/driveguard-bridge/driveguard-audit.jsonl
```

### First run: observe-only. Not optional.

```bash
DRIVEGUARD_ENFORCE=0    # logs every decision it WOULD make, applies none
```

Run one real case session, then read the audit log. A guard that false-positives
mid-session is a guard that gets uninstalled. Enforce only after the log looks right.

---

## What it stops

| Failure mode | Check |
|---|---|
| Duplicate folder in the same root | tree-wide basename index |
| Duplicate folder one level up, same exact name | tree-wide basename index |
| Writes into the wrong zone | `zones.json` policy |
| `-` vs `_` vs space vs case path misses | fuzzy resolver → `modify` |
| Writing from a stale mental map after compression | epoch read-gate |
| `mv` into a protected zone | terminal verb + zone check |
| Stale references after a move | queue → cron sweep |

Modes 1–2 are **location** errors: the basename matches exactly, only the parent
is wrong. A fuzzy resolver cannot catch them. That is why there are two
independent checks and neither substitutes for the other.

## Configuration

`zones.json` is **data, not code**. A PallaDrive restructure is an edit to that
file, never a code change.

| Policy | Meaning |
|---|---|
| `deny` | never write unless Daniel says so in-session (one-shot unlock) |
| `read-first` | drive map must be read first |
| `guarded` | full ladder applies |
| `free` | ladder applies, zone adds nothing |

A missing or corrupt `zones.json` does **not** disarm the protected zone — the
built-in fallback carries the `_system-files` deny row explicitly.

## Tests

```bash
python3 test_driveguard.py                              # 36
python3 ../palladia-primer/test_primer_hook.py          # 22
python3 ../../hook_library/driveguard-epoch/test_epoch.py   # 9
```

The `Bypasses` class is not scaffolding. Every test in it corresponds to a defect
that was **confirmed live on 2026-08-31 by an adversarial audit, after an earlier
31-test suite passed through all of them**: escaped symlinks reaching zone
classification, case-variant ancestors skipping the guard entirely, `_System-Files`
bypassing the deny zone, the read-gate wedging on a case-variant drivemap read,
`"don't modify _system-files"` *unlocking* the deny zone, and `echo >` mutating
with no verb to match.

## Probe provenance

Three mechanisms were built and killed by empirical probe before this design settled:

- **Marker in `conversation_history`** — the compaction summariser quoted the sentinel *into* the summary; it survived two committed compressions.
- **Hermes `compression_count` as epoch** — observed `1 → 2 → 0` on one session id when a config change rebuilt the agent.
- **Blocking `mv`, redirecting to `write_file`** — there is no move tool *and no delete tool*, so it would have copied and left the original.

What survived: the disk bridge (19.741 ms to the next `pre_llm_call`), `{"action": "modify"}` honored live at 0.20.4, and gateway hooks firing on Discord.

Full trail: `AgentSecretBase/workspace/Casing-Palladia-platform/palladia_fileschema-guard/`.
