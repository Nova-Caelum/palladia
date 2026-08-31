"""driveguard-epoch — the compression-epoch writer.

WHY THIS EXISTS
---------------
palladia-driveguard must know whether Palladia has read the drivemap SINCE the
last context compression. Two earlier mechanisms were built and killed by probe:

  * Marker presence in ``conversation_history`` (Probe A, 2026-08-31) -- the
    compaction summariser QUOTED the sentinel into the summary, so the marker
    survived two committed compressions. No better sentinel fixes this.
  * Hermes' own ``compression_count`` (Probe D2, 2026-08-31) -- observed going
    1 -> 2 -> 0 on a single session id when a config change rebuilt the agent.
    A counter that runs backwards cannot authorise anything.

What survived is the DISK BRIDGE itself (Probe D4 -- PASS): a gateway hook
writes, a plugin reads, with no race. Measured latencies after session:compress
were 19.741 ms to the next pre_llm_call and 2.403 s to the first read_file. No
post-compression tool call ever observed stale or null bridge state.

So this handler keeps its OWN monotonic counter and treats Hermes'
``compression_count`` as diagnostic metadata only.

THE INCREMENT MUST READ FROM DISK FIRST
---------------------------------------
Step order below is load-bearing: read the existing epoch FROM DISK, then
increment, then write atomically. An in-memory counter would reset whenever the
gateway process restarts -- reproducing the exact ``compression_count`` defect
this design pivoted away from. Do not "optimise" the read away.

FAIL SOFT, NEVER RAISE
----------------------
Hermes catches and logs handler exceptions. A raise here is therefore invisible.
Every path below swallows its exception: a missing epoch bump degrades to the
plugin failing CLOSED (requiring a re-read), which is the safe direction.

SECRETS
-------
Writes counts, ids and timestamps only. Never message content, never env vars,
never tracebacks. Never stdout -- gateway handler stdout can reach model
context (.claude/rules/hook-secret-handling.md).
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path

# Bridge directory. Overridable for probes/tests; defaults under the Hermes home
# so it survives reboots and is not swept by /tmp cleaners.
_DIR = Path(
    os.environ.get(
        "DRIVEGUARD_BRIDGE_DIR",
        os.path.expanduser("~/.hermes/driveguard-bridge"),
    )
)

# Audit log. Diagnostic only -- the gate never reads this.
_LOG = _DIR / "epoch-audit.jsonl"

# Only sessions on these platforms are bridged. Empty set = all platforms.
# Probe D3 established gateway hooks are profile-scoped here, so this is a
# belt-and-braces filter rather than the primary isolation mechanism.
_PLATFORMS: set[str] = set()


def _epoch_path(session_id: str) -> Path:
    # session_id is used as a filename component. Constrain it hard rather than
    # trusting the gateway: no traversal, no separators, bounded length.
    safe = "".join(c for c in str(session_id) if c.isalnum() or c in "-_")[:64]
    return _DIR / f"epoch-{safe}.json"


def _read_epoch(path: Path) -> int:
    """Current epoch on disk, or 0 when absent/corrupt.

    Returning 0 on corruption is deliberate. It makes the next write produce 1,
    which will not match any plugin-held read_generation, so the plugin fails
    closed and requires a re-read. Corruption must never silently authorise.
    """
    try:
        if not path.is_file():
            return 0
        data = json.loads(path.read_text(encoding="utf-8"))
        value = data.get("bridge_epoch")
        return int(value) if isinstance(value, (int, float)) else 0
    except Exception:
        return 0


def _write_atomic(path: Path, payload: dict) -> None:
    """Write via temp file + os.replace so a reader never sees a partial file."""
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".epoch-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, default=str)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except Exception:
            pass
        raise


def _audit(entry: dict) -> None:
    try:
        with _LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, default=str) + "\n")
    except Exception:
        pass


def handle(event_type, context):
    try:
        session_id = str(context.get("session_id", "") or "")
        if not session_id:
            return

        platform = str(context.get("platform", "") or "")
        if _PLATFORMS and platform not in _PLATFORMS:
            return

        _DIR.mkdir(parents=True, exist_ok=True)
        path = _epoch_path(session_id)
        now_mono = time.monotonic()
        now_wall = time.time()

        if event_type in ("session:start", "session:reset"):
            # A fresh or reset session starts at epoch 1, not 0, so that a
            # plugin holding a stale read_generation of 0 cannot match it.
            if not path.is_file():
                _write_atomic(path, {
                    "session_id": session_id,
                    "bridge_epoch": 1,
                    "hermes_compression_count": None,
                    "t_mono": now_mono,
                    "t_wall": now_wall,
                    "reason": event_type,
                })
                _audit({"event": event_type, "session_id": session_id[:16],
                        "bridge_epoch": 1, "t_wall": now_wall})
            return

        if event_type == "session:compress":
            # READ FROM DISK, then increment. See module docstring.
            current = _read_epoch(path)
            new_epoch = current + 1
            _write_atomic(path, {
                "session_id": session_id,
                "bridge_epoch": new_epoch,
                # Diagnostic ONLY. Probe D2 proved this can go backwards.
                "hermes_compression_count": context.get("compression_count"),
                "in_place": context.get("in_place"),
                "t_mono": now_mono,
                "t_wall": now_wall,
                "reason": "session:compress",
            })
            _audit({
                "event": "session:compress",
                "session_id": session_id[:16],
                "bridge_epoch": new_epoch,
                "previous": current,
                "hermes_compression_count": context.get("compression_count"),
                "in_place": context.get("in_place"),
                "t_wall": now_wall,
            })
    except Exception:
        # Never break the gateway. A missed bump fails the plugin CLOSED.
        pass
