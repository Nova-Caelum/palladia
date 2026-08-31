"""palladia-driveguard — zone policy and duplicate-folder prevention for PallaDrive.

WHAT THIS SOLVES
----------------
Three observed failure modes, in Daniel's words (2026-08-30):

  1. Duplicate folder in the same root -- creates `X/` next to an existing `X/`.
  2. Duplicate folder one level up -- creates `casing/session_notes/` while
     `_meta/session_notes/` already exists.
  3. Writes into the wrong place -- right file, wrong zone.

Modes 1 and 2 are LOCATION errors, not SPELLING errors: the basename matches
exactly, only the parent is wrong. A fuzzy resolver waves them through. They
need a tree-wide BASENAME INDEX, which is a different check from the fuzzy
resolver that catches `Case_Notes` vs `case notes`. Both are here; neither
substitutes for the other.

THE READ GATE
-------------
Writes require that Palladia has read the drive map SINCE the last context
compression. Two earlier mechanisms were killed by probe: marker presence in
``conversation_history`` (the compaction summariser QUOTED the sentinel into the
summary) and Hermes' own ``compression_count`` (observed 1 -> 2 -> 0 when a
config change rebuilt the agent). What survived is the disk bridge: the
``driveguard-epoch`` GATEWAY hook is the sole writer of a monotonic
``bridge_epoch``; this plugin only reads it.

FAIL CLOSED -- AND SAY SO
-------------------------
Any state we cannot positively confirm is treated as "re-read required". A false
re-read costs seconds; a false allow costs a misplaced file and a duplicate
folder.

The one thing worse than blocking wrongly is skipping SILENTLY. On 2026-08-31
the vault moved and this plugin's configured root stopped existing, so every
path compared as outside the vault and every write returned None -- no block, no
audit line, nothing. Two rules came out of that:

  * A root must PROVE ITSELF by containing the marker file before it is
    accepted. A stale or wrong-host path cannot win quietly.
  * If no root resolves, writes are BLOCKED with a configuration error, not
    waved through.

SECRETS
-------
Terminal commands may carry credentials. That exposure exists whether or not we
look -- Hermes passes ``args`` to pre_tool_call for every registered plugin. The
risk is RETENTION. We early-exit before parsing on non-mutation commands, keep
the verb (closed allowlist) and resolved paths only, and never retain the raw
command. Nothing is written to stdout: hook stdout becomes model context and is
prompt-injection-reachable (.claude/rules/hook-secret-handling.md).
"""

from __future__ import annotations

import json
import os
import re
import shlex
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional, Set

_HERE = Path(__file__).resolve().parent
_LOCK = threading.RLock()

# --- Configuration ----------------------------------------------------------
# A corrupt zones.json must not disarm the protected zone, so the fallback
# carries the deny row explicitly rather than an empty list.
_DEFAULT_ZONES: Dict[str, Any] = {
    "vault_candidates": ["/home/daniel/obsidian-vaults/palladrive",
                         "/Users/danieleghdami/PALLAdrive"],
    "vault_marker": "_meta/DRIVE-MAP.md",
    "drivemap_relpath": "_meta/DRIVE-MAP.md",
    "zones": [{"prefix": "_system-files", "policy": "deny", "label": "canonical runtime",
               "reason": "_system-files holds canonical runtime components. "
                         "Say explicitly that you intend to write it."},
              {"prefix": "_meta", "policy": "read-first", "label": "machinery you maintain"}],
    "default_policy": "guarded",
    "terminal": {"mutation_verbs": [], "credential_tripwire": []},
    "fuzzy": {"separators": ["-", "_", " ", "."], "strip_extensions": []},
}


def _load_zones() -> Dict[str, Any]:
    try:
        data = json.loads((_HERE / "zones.json").read_text(encoding="utf-8"))
        merged = dict(_DEFAULT_ZONES)
        merged.update(data)
        return merged
    except Exception:
        return dict(_DEFAULT_ZONES)


_CFG = _load_zones()
_DRIVEMAP_REL = _CFG.get("drivemap_relpath", "_meta/DRIVE-MAP.md")
_MARKER = _CFG.get("vault_marker", "_meta/DRIVE-MAP.md")
_BRIDGE_DIR = Path(os.environ.get(
    "DRIVEGUARD_BRIDGE_DIR", os.path.expanduser("~/.hermes/driveguard-bridge")))
_QUEUE = _BRIDGE_DIR / "sweep-queue.jsonl"
_AUDIT = _BRIDGE_DIR / "driveguard-audit.jsonl"
_ENFORCE = os.environ.get("DRIVEGUARD_ENFORCE", "1") != "0"

_WRITE_TOOLS = {"write_file"}
_EDIT_TOOLS = {"patch"}
_READ_TOOLS = {"read_file", "search_files"}

_READ_GEN: Dict[str, int] = {}
_EXPLICIT_SYSTEM_WRITE: Set[str] = set()
_INDEX_CACHE: Dict[str, Any] = {"built_at": 0.0, "dirs": {}, "files": {}}
_INDEX_TTL = 30.0


def _audit(entry: dict) -> None:
    """File-only. Never stdout."""
    try:
        _BRIDGE_DIR.mkdir(parents=True, exist_ok=True)
        with _AUDIT.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, default=str) + "\n")
    except Exception:
        pass


# --- Vault root discovery ---------------------------------------------------
# MACHINE-AGNOSTIC BY CONSTRUCTION. olympus1 is the runtime host and is probed
# first; the Mac is the authoring copy. Within-drive paths are identical on both,
# so only the pre-drive root differs. A candidate is accepted ONLY if it contains
# the marker file -- see the module docstring for why.

_VAULT: Optional[Path] = None
_VAULT_LEXICAL: Optional[Path] = None
_VAULT_SOURCE: str = "unresolved"
_CASE_INSENSITIVE: bool = False


def _has_marker(root: str) -> bool:
    try:
        return (Path(root) / _MARKER).is_file()
    except Exception:
        return False


def _detect_case_insensitive(root: Path) -> bool:
    """Empirical, never guessed from sys.platform.

    On a case-insensitive volume an agent can address `PALLADRIVE/...` or
    `_System-Files/...`, land on the same inode, and have every string
    comparison here report 'different path'. Verified as a total bypass on
    Daniel's Mac, 2026-08-31.
    """
    try:
        swapped = str(root).swapcase()
        if swapped == str(root):
            return False
        a, b = os.stat(str(root)), os.stat(swapped)
        return (a.st_ino, a.st_dev) == (b.st_ino, b.st_dev)
    except Exception:
        return False


def _set_root(raw: Any, source: str) -> bool:
    global _VAULT, _VAULT_LEXICAL, _VAULT_SOURCE, _CASE_INSENSITIVE
    try:
        expanded = os.path.expanduser(str(raw or "").strip())
        if not expanded or not _has_marker(expanded):
            return False
        _VAULT = Path(os.path.realpath(expanded))
        # abspath, NOT normpath: normpath does not absolutise, so a relative
        # configured root would turn _under() into a cwd-relative comparison and
        # produce false 'inside' verdicts on arbitrary paths.
        _VAULT_LEXICAL = Path(os.path.abspath(expanded))
        _VAULT_SOURCE = source
        _CASE_INSENSITIVE = _detect_case_insensitive(_VAULT)
        return True
    except Exception:
        return False


def _resolve_root(ctx: Any = None) -> None:
    """Order: plugin config -> env (tests only) -> marker-verified candidates."""
    if ctx is not None:
        try:
            if _set_root(ctx.get_config("vault_path", default=""), "plugin-config"):
                return
        except Exception:
            pass
    if _set_root(os.environ.get("PALLADRIVE_PATH", ""), "env"):
        return
    for cand in _CFG.get("vault_candidates", []):
        if _set_root(cand, "candidate"):
            return
    _audit({"event": "VAULT-UNRESOLVED", "marker": _MARKER,
            "checked": _CFG.get("vault_candidates", []), "t": time.time()})


def _roots_ready() -> bool:
    with _LOCK:
        if _VAULT is None:
            _resolve_root()
        return _VAULT is not None


def _fold(s: str) -> str:
    return s.lower() if _CASE_INSENSITIVE else s


# --- Path verdict -----------------------------------------------------------
# Computed ONCE at the hook boundary and passed down. Every earlier bug in this
# module came from re-deriving `rel` at three call sites from three different
# information sets; _zone_for in particular used the realpath and silently fell
# to default policy for an escaped symlink.

class Verdict(NamedTuple):
    real: Path
    lexical: Path
    rel: str
    inside: bool
    escaped: bool


def _lexical(path_str: str) -> Optional[Path]:
    """Absolute, `..` collapsed, symlinks NOT followed. Anchored to the LEXICAL root."""
    try:
        raw = str(path_str or "").strip()
        if not raw:
            return None
        p = Path(os.path.expanduser(raw))
        if not p.is_absolute():
            p = (_VAULT_LEXICAL or Path.cwd()) / p
        return Path(os.path.normpath(str(p)))
    except Exception:
        return None


def _real(path_str: str) -> Optional[Path]:
    """Absolute with symlinks followed. Anchored to the REAL root."""
    try:
        raw = str(path_str or "").strip()
        if not raw:
            return None
        p = Path(os.path.expanduser(raw))
        if not p.is_absolute():
            p = (_VAULT or Path.cwd()) / p
        return Path(os.path.realpath(str(p)))
    except Exception:
        return None


def _under(root: Optional[Path], p: Optional[Path]) -> bool:
    if root is None or p is None:
        return False
    try:
        rel = os.path.relpath(_fold(str(p)), _fold(str(root)))
    except Exception:
        return False
    return not rel.startswith("..")


def _verdict(path_str: str) -> Optional[Verdict]:
    if not _roots_ready():
        return None
    lex, real = _lexical(path_str), _real(path_str)
    if lex is None or real is None:
        return None
    in_lex = _under(_VAULT_LEXICAL, lex)
    in_real = _under(_VAULT, real)
    if not (in_lex or in_real):
        return None
    # Strip the root by LENGTH, not via relpath. On a case-insensitive volume
    # `_under` folds but relpath does not, so an ancestor addressed as
    # `PALLADRIVE/...` yielded `../PALLADRIVE/_system-files/x.md` -- no zone
    # matched, the deny zone silently became `guarded`, and the write was
    # allowed. Verified bypass 2026-08-31. Length-stripping keeps the tail's
    # original case (so index lookups still line up) while tolerating any case
    # of the root itself.
    try:
        base = str(_VAULT_LEXICAL) if in_lex else str(_VAULT)
        full = str(lex) if in_lex else str(real)
        rel = (full[len(base):].lstrip(os.sep) if _fold(full).startswith(_fold(base))
               else os.path.relpath(full, base))
        if not rel:
            return None
    except Exception:
        return None
    return Verdict(real=real, lexical=lex, rel=rel, inside=True,
                   escaped=(in_lex and not in_real))


def _zone_for_rel(rel: str) -> Dict[str, Any]:
    """Longest-prefix-first, case-folded when the volume is case-insensitive."""
    parts = [_fold(x) for x in rel.split(os.sep)]
    best: Dict[str, Any] = {"prefix": "", "policy": _CFG.get("default_policy", "guarded"),
                            "label": "drive", "reason": ""}
    best_len = -1
    for z in _CFG.get("zones", []):
        pref = str(z.get("prefix", "")).strip("/")
        if not pref:
            continue
        pparts = [_fold(x) for x in pref.split("/")]
        if parts[:len(pparts)] == pparts and len(pparts) > best_len:
            best, best_len = z, len(pparts)
    return best


# --- Fuzzy normalisation ----------------------------------------------------

_SEPS = _CFG.get("fuzzy", {}).get("separators", ["-", "_", " ", "."])
_STRIP_EXT = tuple(_CFG.get("fuzzy", {}).get("strip_extensions", []))


def _norm(name: str) -> str:
    s = str(name or "").strip().lower()
    for ext in _STRIP_EXT:
        if s.endswith(ext):
            s = s[: -len(ext)]
            break
    for sep in _SEPS:
        s = s.replace(sep, "")
    return re.sub(r"[^a-z0-9]", "", s)


# --- Tree index -------------------------------------------------------------

def _build_index() -> Dict[str, Any]:
    dirs: Dict[str, List[str]] = {}
    files: Dict[str, List[str]] = {}
    skip = {".obsidian", ".trash", ".git", "__pycache__", "node_modules"}
    try:
        for dirpath, dirnames, filenames in os.walk(str(_VAULT)):
            dirnames[:] = [d for d in dirnames if d not in skip and not d.startswith(".")]
            for d in dirnames:
                rel = os.path.relpath(os.path.join(dirpath, d), str(_VAULT))
                dirs.setdefault(_norm(d), []).append(rel)
            for f in filenames:
                if f.startswith("."):
                    continue
                rel = os.path.relpath(os.path.join(dirpath, f), str(_VAULT))
                files.setdefault(_norm(f), []).append(rel)
    except Exception:
        pass
    return {"built_at": time.time(), "dirs": dirs, "files": files}


def _index() -> Dict[str, Any]:
    with _LOCK:
        if time.time() - _INDEX_CACHE.get("built_at", 0) > _INDEX_TTL:
            _INDEX_CACHE.update(_build_index())
        return _INDEX_CACHE


def _invalidate_index() -> None:
    with _LOCK:
        _INDEX_CACHE["built_at"] = 0.0


# --- Epoch bridge -----------------------------------------------------------

def _bridge_epoch(session_id: str) -> Optional[int]:
    try:
        safe = "".join(c for c in str(session_id) if c.isalnum() or c in "-_")[:64]
        p = _BRIDGE_DIR / f"epoch-{safe}.json"
        if not p.is_file():
            return None
        value = json.loads(p.read_text(encoding="utf-8")).get("bridge_epoch")
        return int(value) if isinstance(value, (int, float)) else None
    except Exception:
        return None


def _armed_on_disk(session_id: str) -> Optional[int]:
    """Epoch recorded by palladia-primer's first-turn injection.

    Plugins are separate modules with separate memory and no guaranteed load
    order, so the primer cannot call into this one. It writes here instead --
    the same disk-bridge pattern Probe D proved for the gateway hook.
    """
    try:
        safe = "".join(c for c in str(session_id) if c.isalnum() or c in "-_")[:64]
        f = _BRIDGE_DIR / f"armed-{safe}.json"
        if not f.is_file():
            return None
        value = json.loads(f.read_text(encoding="utf-8")).get("armed_at_epoch")
        return int(value) if isinstance(value, (int, float)) else None
    except Exception:
        return None


def _drivemap_is_current(session_id: str):
    epoch = _bridge_epoch(session_id)
    if epoch is None:
        return False, "no-bridge"
    held = _READ_GEN.get(session_id)
    if held is None:
        held = _armed_on_disk(session_id)
        if held is not None:
            _READ_GEN[session_id] = held
    if held is None:
        return False, "never-read"
    if held < epoch:
        return False, "compressed-since-read"
    if held > epoch:
        return False, "epoch-regressed"
    return True, "current"


# --- Decision helpers -------------------------------------------------------

def _block(msg: str) -> Dict[str, Any]:
    return {"action": "block", "message": f"driveguard: {msg}"}


def _modify(args: Dict[str, Any]) -> Dict[str, Any]:
    return {"action": "modify", "args": args}


def _path_arg_key(args: Dict[str, Any]) -> Optional[str]:
    for k in ("path", "file_path", "filename", "file", "target"):
        if isinstance(args.get(k), str) and args[k].strip():
            return k
    return None


def _evaluate_write(v: Verdict, session_id: str, creating_dirs: bool,
                    args: Dict[str, Any], key: str) -> Optional[Dict[str, Any]]:
    """The ladder. Returns a directive, or None to allow."""
    # Row 0 -- escapes never reach zone classification. Blocking here means there
    # is no ambiguous zone verdict to get wrong, no iterdir() outside the vault
    # leaking into a block message, and no `../..` strings in the audit log.
    if v.escaped:
        return _block(f"`{v.rel}` leaves the vault through a symlink. "
                      f"Name the real destination explicitly.")

    zone = _zone_for_rel(v.rel)

    # Row 1 -- deny zone
    if zone.get("policy") == "deny":
        if session_id in _EXPLICIT_SYSTEM_WRITE:
            _EXPLICIT_SYSTEM_WRITE.discard(session_id)   # one-shot, not a session-long unlock
            _audit({"event": "deny-zone-unlock-consumed", "rel": v.rel,
                    "session_id": str(session_id)[:16], "t": time.time()})
        else:
            return _block(zone.get("reason") or
                          f"`{zone.get('prefix')}` is a protected zone. "
                          f"Say explicitly that you intend to write it.")

    # Row 2 -- read gate
    ok, why = _drivemap_is_current(session_id)
    if not ok:
        hint = {"no-bridge": "no compression epoch is available",
                "never-read": "you have not read the drive map this session",
                "compressed-since-read": "your context was compressed since you last read the drive map",
                "epoch-regressed": "the compression epoch is inconsistent"}.get(why, why)
        return _block(f"{hint}. Read `{_DRIVEMAP_REL}` before writing, then retry.")

    idx = _index()
    parent_rel = os.path.dirname(v.rel)

    if creating_dirs and not v.real.parent.exists():
        base = os.path.basename(parent_rel)
        # Row 3 -- same basename already exists elsewhere in the tree
        hits = [h for h in idx["dirs"].get(_norm(base), []) if h != parent_rel]
        if hits:
            shown = "\n".join(f"  - {h}/" for h in sorted(hits)[:6])
            return _block(f"a folder named \"{base}\" already exists elsewhere:\n{shown}\n"
                          f"Use one of those, or say explicitly that you want a second "
                          f"folder named \"{base}\" at `{parent_rel}/`.")
        # Row 4 -- parent missing entirely
        gp = v.real.parent.parent
        near = []
        if gp.exists() and _under(_VAULT, gp):
            try:
                near = sorted({d.name for d in gp.iterdir() if d.is_dir()})[:8]
            except Exception:
                near = []
        near_txt = ("\n  Existing folders there: " + ", ".join(near)) if near else ""
        return _block(f"parent folder `{parent_rel}/` does not exist, so this write "
                      f"would create it.{near_txt}\n  Confirm the location against "
                      f"`{_DRIVEMAP_REL}` first.")

    # Rows 5/6 -- fuzzy resolution when the file does not exist as written
    if not v.real.exists():
        cands = [c for c in idx["files"].get(_norm(os.path.basename(v.rel)), [])
                 if os.path.dirname(c) == parent_rel]
        if len(cands) == 1 and cands[0] != v.rel:
            _audit({"event": "fuzzy-correct", "from": v.rel, "to": cands[0],
                    "session_id": str(session_id)[:16], "t": time.time()})
            new_args = dict(args)
            new_args[key] = str(_VAULT / cands[0])
            return _modify(new_args)
        if len(cands) > 1:
            shown = "\n".join(f"  - {c}" for c in sorted(cands)[:6])
            return _block(f"\"{os.path.basename(v.rel)}\" is ambiguous — candidates:\n"
                          f"{shown}\nName the exact path.")

    return None  # Row 7 -- allow


# --- Terminal ---------------------------------------------------------------

_TERM_CFG = _CFG.get("terminal", {})
_MUT_VERBS = set(_TERM_CFG.get("mutation_verbs", []))
_TRIPWIRE = [t.lower() for t in _TERM_CFG.get("credential_tripwire", [])]

# Wrappers that hide the real verb one level down. Verified bypasses 2026-08-31.
_INDIRECT = {"sudo", "env", "nohup", "time", "xargs", "sh", "bash", "zsh", "git"}
# Redirection and in-place editors mutate with no mutation verb at the head.
_REDIRECT = re.compile(r"(?<!\d)>{1,2}(?!&)|\btee\b|\bsed\b\s+-i|\bdd\b\s|\btruncate\b")


def _terminal_verb(command: str) -> Optional[str]:
    """Leading mutation verb, seen through wrappers. Never retains the command."""
    try:
        toks = str(command or "").strip().split()
        for tok in toks[:6]:
            head = os.path.basename(tok.strip("\"'"))
            if head in _MUT_VERBS:
                return head
            if head in _INDIRECT or head.startswith("-") or "=" in head:
                continue
            break
        return None
    except Exception:
        return None


def _mutates(command: str) -> bool:
    return bool(_terminal_verb(command)) or bool(_REDIRECT.search(str(command or "")))


def _has_credential_shape(command: str) -> bool:
    low = str(command or "").lower()
    return any(t in low for t in _TRIPWIRE)


def _terminal_paths(command: str):
    """(paths, parse_ok). A failed parse is NOT an empty path list."""
    out: List[Verdict] = []
    try:
        toks = shlex.split(command)[1:]
    except Exception:
        return out, False           # unbalanced quotes -> fail closed, not open
    for tok in toks:
        if tok.startswith("-"):
            continue
        v = _verdict(tok)
        if v is not None:
            out.append(v)
    return out, True


def _evaluate_terminal(command: str, session_id: str) -> Optional[Dict[str, Any]]:
    if not _mutates(command):
        return None                                  # early exit; never parsed further
    if _has_credential_shape(command):
        _audit({"event": "terminal", "verb": "redacted",
                "session_id": str(session_id)[:16], "t": time.time()})
        return None
    verb = _terminal_verb(command) or "redirect"
    paths, parse_ok = _terminal_paths(command)
    _audit({"event": "terminal", "verb": verb, "parse_ok": parse_ok,
            "paths": [v.rel for v in paths][:8],
            "session_id": str(session_id)[:16], "t": time.time()})
    if not parse_ok:
        return _block("this command could not be parsed safely (unbalanced quotes). "
                      "Rewrite it, or use write_file.")
    for v in paths:
        if v.escaped:
            return _block(f"`{verb}` targets `{v.rel}`, which leaves the vault "
                          f"through a symlink. Name the real destination.")
        if _zone_for_rel(v.rel).get("policy") == "deny":
            if session_id in _EXPLICIT_SYSTEM_WRITE:
                _EXPLICIT_SYSTEM_WRITE.discard(session_id)
                return None
            return _block(f"`{verb}` targets a protected zone (`{v.rel}`). "
                          f"Say explicitly that you intend to modify it.")
    return None                                      # ambiguity defers to the sweep


# --- Hooks ------------------------------------------------------------------

# Deliberately NOT negation-blind: "don't modify _system-files" must not unlock
# the protected zone. Verified as a live bypass 2026-08-31. The unlock is also
# one-shot -- consumed on first use in _evaluate_write -- rather than lasting the
# whole session.
_UNLOCK = re.compile(r"(write|edit|update|change|modify|install)\w*\s[^.]{0,40}?_system[- ]?files")
_NEGATED = re.compile(r"\b(don'?t|do not|never|avoid|without|no longer|stop)\b")


def _pre_llm_call(**payload: Any) -> None:
    try:
        sid = str(payload.get("session_id", "") or "")
        msg = str(payload.get("user_message", "") or "").lower()
        if not sid or not _UNLOCK.search(msg):
            return None
        window = msg[max(0, _UNLOCK.search(msg).start() - 60):_UNLOCK.search(msg).end()]
        if _NEGATED.search(window):
            _audit({"event": "unlock-refused-negated", "session_id": sid[:16], "t": time.time()})
            return None
        _EXPLICIT_SYSTEM_WRITE.add(sid)
        _audit({"event": "unlock-armed", "session_id": sid[:16], "t": time.time()})
    except Exception:
        pass
    return None


def _unwrap(tool_name: str, args: Any):
    if tool_name == "tool_call" and isinstance(args, dict):
        n, a = args.get("name"), args.get("arguments")
        if isinstance(n, str) and isinstance(a, dict):
            return n, a
    return tool_name, args


def _pre_tool_call(tool_name: str = "", args: Any = None, session_id: str = "",
                   task_id: str = "", **_: Any) -> Optional[Dict[str, Any]]:
    try:
        sid = str(session_id or task_id or "")
        if not isinstance(args, dict):
            return None
        name, payload = _unwrap(tool_name, args)
        if name not in (_WRITE_TOOLS | _EDIT_TOOLS | _READ_TOOLS | {"terminal"}):
            return None

        # A guard that cannot locate the vault must SAY SO, not skip silently.
        if not _roots_ready():
            if name in (_WRITE_TOOLS | _EDIT_TOOLS | {"terminal"}):
                return _block(
                    "vault root could not be resolved — no candidate contains "
                    f"`{_MARKER}`. This is a configuration error; set the plugin's "
                    "`vault_path`. Refusing to classify writes until it is fixed.")
            return None

        if name == "terminal":
            d = _evaluate_terminal(str(payload.get("command") or payload.get("cmd") or ""), sid)
            return d if (_ENFORCE and d) else None

        key = _path_arg_key(payload)
        if not key:
            return None
        v = _verdict(payload[key])
        if v is None:
            return None                    # genuinely outside the vault
        if name in _READ_TOOLS:
            return None                    # reads are never blocked

        d = _evaluate_write(v, sid, creating_dirs=(name in _WRITE_TOOLS),
                            args=payload, key=key)
        if d:
            _audit({"event": "decision", "tool": name, "action": d.get("action"),
                    "rel": v.rel, "session_id": sid[:16], "t": time.time()})
        return d if (_ENFORCE and d) else None
    except Exception as exc:
        # A systematically-failing guard must be distinguishable from a quiet one.
        _audit({"event": "EXCEPTION", "where": "pre_tool_call",
                "type": type(exc).__name__, "tool": str(tool_name)[:40], "t": time.time()})
        return None


def _post_tool_call(tool_name: str = "", args: Any = None, result: Any = None,
                    session_id: str = "", task_id: str = "", **_: Any) -> None:
    try:
        sid = str(session_id or task_id or "")
        if not isinstance(args, dict) or not _roots_ready():
            return
        name, payload = _unwrap(tool_name, args)
        if name == "read_file":
            key = _path_arg_key(payload)
            v = _verdict(payload.get(key, "")) if key else None
            # Case-folded compare: on a case-insensitive volume, reading
            # `_meta/drive-map.md` succeeds on disk but an exact string compare
            # fails, so the gate never arms and every later write is blocked with
            # "you have not read the drive map" while she demonstrably just did.
            # That wedge is the fastest route to this plugin being switched off.
            if v is not None and _fold(v.rel) == _fold(_DRIVEMAP_REL):
                epoch = _bridge_epoch(sid)
                if epoch is not None and sid:
                    _READ_GEN[sid] = epoch
                    _audit({"event": "gate-armed", "session_id": sid[:16],
                            "epoch": epoch, "t": time.time()})
            return
        if name in (_WRITE_TOOLS | _EDIT_TOOLS):
            _invalidate_index()
    except Exception:
        pass


def arm_gate(session_id: str) -> bool:
    """Arm the read-gate without a read_file call.

    palladia-primer injects drivemap state into the first turn, so the knowledge
    is already in context. Without this she would be blocked on her first write
    of every session and forced to re-read what she was just handed.
    """
    try:
        epoch = _bridge_epoch(str(session_id))
        if epoch is None or not session_id:
            return False
        _READ_GEN[str(session_id)] = epoch
        safe = "".join(c for c in str(session_id) if c.isalnum() or c in "-_")[:64]
        _BRIDGE_DIR.mkdir(parents=True, exist_ok=True)
        (_BRIDGE_DIR / f"armed-{safe}.json").write_text(
            json.dumps({"session_id": str(session_id), "armed_at_epoch": epoch,
                        "t": time.time()}))
        _audit({"event": "gate-armed-by-primer", "session_id": str(session_id)[:16],
                "epoch": epoch, "t": time.time()})
        return True
    except Exception:
        return False


def _transform_tool_result(tool_name: str = "", args: Any = None, result: Any = None,
                           **_: Any) -> Optional[str]:
    try:
        if tool_name not in _WRITE_TOOLS or not isinstance(result, str):
            return None
        return result + (
            "\n\n---\nDRIVEGUARD: write landed. `_system-files/` is canonical runtime "
            "(do not write unless told), `_meta/` is machinery you maintain, `_wiki/` "
            "is the reference bank. Before creating any new folder, check "
            f"`{_DRIVEMAP_REL}` for one that already exists elsewhere.")
    except Exception:
        return None


def _transform_terminal_output(command: str = "", output: str = "", returncode: int = 1,
                               **_: Any) -> None:
    """Enqueue moved paths for the stale-reference sweep. Never rewrites output."""
    try:
        if returncode != 0 or not _roots_ready():
            return
        if _terminal_verb(command) not in ("mv", "rsync"):
            return
        if _has_credential_shape(command):
            return
        paths, parse_ok = _terminal_paths(command)
        if parse_ok and len(paths) >= 2:
            _BRIDGE_DIR.mkdir(parents=True, exist_ok=True)
            with _QUEUE.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps({"verb": "mv", "from": paths[0].rel,
                                     "to": paths[-1].rel, "t": time.time()}) + "\n")
            _invalidate_index()
    except Exception:
        pass
    return None


_PROMPT_SECTION = (
    "PallaDrive zones. `_system-files/` is canonical runtime — never write there "
    "unless Daniel explicitly says so. `_meta/` holds the drive map, templates and "
    "your worklog; read `_meta/DRIVE-MAP.md` before writing. `_wiki/` is the "
    "reference bank. `casing/`, `behaviorals/`, `networking/` hold your work.\n"
    "Before creating ANY new folder, check the drive map for a folder of that name "
    "somewhere else — creating a second one is the single most common mistake you "
    "make. If a write is blocked, the block message names the existing path or the "
    "candidate list: use it and retry rather than inventing a new location.\n"
    "After a context compression you must read the drive map again before writing."
)


def register(ctx) -> None:
    _resolve_root(ctx)
    _audit({"event": "register", "vault": str(_VAULT), "source": _VAULT_SOURCE,
            "case_insensitive": _CASE_INSENSITIVE, "enforce": _ENFORCE, "t": time.time()})
    try:
        ctx.register_system_prompt_section(
            "palladia-driveguard.zones", _PROMPT_SECTION,
            position="after_memory", max_chars=1200)
    except Exception:
        pass
    ctx.register_hook("pre_llm_call", _pre_llm_call)
    ctx.register_hook("pre_tool_call", _pre_tool_call)
    ctx.register_hook("post_tool_call", _post_tool_call)
    ctx.register_hook("transform_tool_result", _transform_tool_result)
    ctx.register_hook("transform_terminal_output", _transform_terminal_output)
