"""Inject Palladia's generated primer into the LLM context at the start of a session.

WHY THIS EXISTS
---------------
``memories/MEMORY.md`` is capped at 2,200 characters and is injected as a FROZEN
SNAPSHOT at session start -- mid-session writes land on disk but do not reach the
prompt until the next session. So memory cannot carry live state.

This plugin closes that gap: on the FIRST TURN of a session it reads a generated
primer out of PallaDrive and injects it into that turn's user message, so Palladia
opens every session knowing the current target, open weaknesses, and recent case
activity.

HOOK CONTRACT -- VERIFIED 2026-08-29, DO NOT REVERT
---------------------------------------------------
This plugin originally registered ``on_session_start`` and returned
``{"context": ...}``. **That was wrong and would have silently never injected
anything.** Two independent sources settled it:

  * Vulcan's live source scan of Hermes on olympus1 (2026-08-29).
  * Hermes' own shipped-plugin-hook catalog
    (https://hermes-agent.nousresearch.com/docs/user-guide/features/hooks).

The catalog is explicit:

  * ``on_session_start`` -- payload ``session_id``, ``model``, ``platform``.
    Return handling: **"Ignored."** Observer hook only. It also fires AFTER the
    system prompt is built, so it could not inject even if the return were read.
  * ``pre_llm_call`` -- payload ``session_id``, ``user_message``,
    ``conversation_history``, ``is_first_turn`` (bool), ``model``, ``platform``.
    Fires once per turn before the tool-calling loop. **"All valid callback
    returns are aggregated in plugin order and injected into the current turn's
    user message."** A dict with a ``"context"`` key or a plain non-empty string
    injects; ``None`` injects nothing.

So: ``pre_llm_call``, gated to the first turn.

WHY GATED TO THE FIRST TURN
---------------------------
``pre_llm_call`` fires EVERY turn. Injecting a 6 KB primer on every turn of a
90-minute case session would burn the context budget for no benefit -- the primer
is already in the transcript after turn one.

The gate reads ``is_first_turn`` and **defaults to True when the field is absent**.
That default is deliberate and directional: if Hermes ever renames or drops the
field, we degrade to visible over-injection (Daniel sees the primer repeating and
tells us) rather than to silent never-injection (Palladia coaches from stale state
and nobody finds out). Do not "fix" this to default False.

FAIL SOFT AND LOUD -- DO NOT "SIMPLIFY" THIS AWAY
-------------------------------------------------
Hermes LOGS AND SKIPS a hook callback that raises. A crash here is therefore
INVISIBLE inside the session: Palladia would proceed with no primer and no
indication that anything was missing, silently reasoning from stale memory.

That inverts the Nova Caelum fail-safe convention, so every failure path below
returns a LOUD notice instead of raising. The bare ``except Exception`` in
``_load_primer`` is deliberate and load-bearing -- it is what converts an
invisible skip into a visible warning. Narrowing it to specific exception types
reintroduces exactly the silent-failure mode it exists to prevent.

SECRETS
-------
Hook output reaches model context. This plugin reads ONE known path under
PallaDrive and emits nothing else -- no env vars, no config, no directory
listings, no exception tracebacks (a traceback can carry filesystem structure and
occasionally credential material from surrounding frames). Error messages are
hand-written constants plus the exception's class name only.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

# --- Configuration ----------------------------------------------------------

# Verified live 2026-08-29 (Vulcan, Part 1): the Obsidian Sync remote "PallaDrive"
# is materialized on olympus1 at this path, bidirectional, 77 content files.
# The sibling `/home/daniel/obsidian-vaults/palladia` is a DIFFERENT near-empty
# historical folder -- never point at it.
_PALLADRIVE = Path(
    os.environ.get("PALLADRIVE_PATH", "/home/daniel/obsidian-vaults/palladrive")
)
_PRIMER_RELATIVE = Path("_system-files/primer/PRIMER.md")

# Injected primer is capped so a runaway generator cannot eat the context budget.
_MAX_CHARS = 6000
_TRUNCATION_MARKER = (
    "\n\n[PRIMER TRUNCATED at {cap} characters. The full file is at "
    "{path} -- read it directly if you need what was cut.]"
)

_HEADER = "=== PALLADIA PRIMER (generated; read-only) ==="

_MISSING_NOTICE = (
    f"{_HEADER}\n"
    "PRIMER COULD NOT BE LOADED -- the file was not found at {path}.\n"
    "Your working state may be stale. Do not assume you know the current target, "
    "open weaknesses, or recent case activity. Read PallaDrive directly, and tell "
    "Daniel the primer is missing before giving coaching that depends on state."
)

_UNREADABLE_NOTICE = (
    f"{_HEADER}\n"
    "PRIMER COULD NOT BE READ -- the file exists at {path} but could not be opened "
    "({reason}).\n"
    "Your working state may be stale. Read PallaDrive directly, and tell Daniel the "
    "primer failed to load before giving coaching that depends on state."
)


# --- Core -------------------------------------------------------------------


def _primer_path() -> Path:
    return _PALLADRIVE / _PRIMER_RELATIVE


def _extract_generated_at(text: str) -> Optional[str]:
    """Pull generated_at out of the YAML frontmatter without a YAML dependency.

    Deliberately dumb: scans only the frontmatter block. Returns None rather than
    raising on any malformed input -- a missing timestamp must not cost us the
    whole primer.
    """
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    for line in text[3:end].splitlines():
        stripped = line.strip()
        if stripped.startswith("generated_at:"):
            value = stripped.split(":", 1)[1].strip().strip("\"'")
            return value or None
    return None


def _load_primer() -> str:
    """Return primer text to inject. NEVER raises -- see module docstring."""
    path = _primer_path()
    try:
        if not path.is_file():
            return _MISSING_NOTICE.format(path=path)
        text = path.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 -- deliberate; see module docstring.
        # Class name only. Never str(exc) -- messages can carry path internals.
        return _UNREADABLE_NOTICE.format(path=path, reason=type(exc).__name__)

    stamp = _extract_generated_at(text)
    stamp_line = (
        f"Generated at: {stamp}"
        if stamp
        else "Generated at: UNKNOWN -- no generated_at in frontmatter. Treat as stale."
    )

    body = text
    if len(body) > _MAX_CHARS:
        marker = _TRUNCATION_MARKER.format(cap=_MAX_CHARS, path=path)
        body = body[: _MAX_CHARS - len(marker)] + marker

    return f"{_HEADER}\n{stamp_line}\nSource: {path}\n\n{body}"


def _is_first_turn(payload: Dict[str, Any]) -> bool:
    """True when this is the session's opening turn.

    Defaults to True on a missing/None field -- see the module docstring. Any
    non-bool truthy/falsey value is coerced, because a hook must never raise.
    """
    value = payload.get("is_first_turn", True)
    if value is None:
        return True
    return bool(value)


def _pre_llm_call(**payload: Any) -> Optional[Dict[str, Any]]:
    """Per-turn callback. Injects the primer on the first turn only.

    Accepts ``**payload`` only -- Hermes passes the catalog's payload fields as
    keyword arguments and may add more. Do not add positional params.

    Returns ``{"context": <str>}`` on the first turn (the catalog's documented
    injection shape) and ``None`` on every later turn, which injects nothing.
    """
    if not _is_first_turn(payload):
        return None
    return {"context": _load_primer()}


def register(ctx) -> None:
    ctx.register_hook("pre_llm_call", _pre_llm_call)
