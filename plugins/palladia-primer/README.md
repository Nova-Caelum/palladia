# palladia-primer

**Author:** ChiefPM · 2026-08-29
**Daniel reviewed:** no
**Status:** v0.2.0 — tests pass locally (15/15). **Not deployed. Return contract now VERIFIED (see Mechanism).**
**Contract corrected 2026-08-29:** was `on_session_start` → now `pre_llm_call`, first-turn-gated.

Injects Palladia's generated primer into the first turn of each session.

## Why

`memories/MEMORY.md` is capped at 2,200 characters and is injected as a **frozen snapshot** at session start — mid-session writes reach disk but not the prompt until the next session. Memory therefore cannot carry live state.

This plugin reads a generated primer from PallaDrive at `_system-files/core_text/PRIMER.md` and injects it, so Palladia opens each session knowing the current target, open weaknesses, and recent case activity. Memory holds pointers; the primer holds state.

## Mechanism

Native Hermes plugin: `register(ctx)` → `ctx.register_hook("pre_llm_call", ...)`.

### The contract, and why it changed

v0.1.0 registered `on_session_start` and returned `{"context": ...}`. **That would have silently injected nothing, every session, forever.** Two independent sources settled it on 2026-08-29:

1. Vulcan's live Hermes source scan on olympus1.
2. Hermes' own [shipped plugin hook catalog](https://hermes-agent.nousresearch.com/docs/user-guide/features/hooks).

| Hook | Payload | Return handling |
|---|---|---|
| `on_session_start` | `session_id`, `model`, `platform` | **Ignored.** Observer only — and it fires *after* the system prompt is built. |
| `pre_llm_call` | `session_id`, `user_message`, `conversation_history`, `is_first_turn`, `model`, `platform` | Fires once per turn before the tool loop. **All valid returns are aggregated in plugin order and injected into the current turn's user message.** A dict with `"context"` or a plain non-empty string injects; `None` injects nothing. |

`hermes hooks fire on_session_start` — the verification command v0.1.0's README prescribed — **does not exist**. Live `hermes hooks` supports `list`, `test`, `revoke`, `doctor`, and targets shell hooks in config, not Python plugin hooks. The real gate is an integration test: start a session, ask Palladia what her current target is, and confirm `=== PALLADIA PRIMER` content is present in her answer.

### Why gated to the first turn

`pre_llm_call` fires **every** turn. Injecting 6 KB on every turn of a 90-minute case session burns the context budget for nothing — the primer is already in the transcript after turn one.

`_is_first_turn()` reads `is_first_turn` and **defaults to `True` when the field is absent.** That default is directional on purpose: if Hermes renames or drops the field, we degrade to *visible* over-injection (Daniel sees the primer repeating and reports it) rather than *silent* never-injection. Do not "fix" it to default `False`.

## Fail-soft-and-loud — do not "simplify"

**Hermes logs and SKIPS a hook callback that raises.** A crash here is invisible inside the session: Palladia proceeds with no primer and no signal that anything is missing.

So every failure path returns a loud in-context notice instead of raising:

| Condition | Behaviour |
|---|---|
| File missing | `PRIMER COULD NOT BE LOADED` + instruction to read PallaDrive and tell Daniel |
| File unreadable | `PRIMER COULD NOT BE READ` + exception **class name only** |
| No `generated_at` | Loads anyway, stamps `UNKNOWN — treat as stale` |
| Over 6,000 chars | Truncates with an explicit `[PRIMER TRUNCATED …]` marker |

The bare `except Exception` in `_load_primer` is deliberate and load-bearing. Narrowing it reintroduces the silent-skip failure it exists to prevent.

## Secrets

Hook output reaches model context. This plugin reads one known path and emits nothing else — no env vars, no config, no directory listings, and **no tracebacks** (a traceback can carry filesystem structure and occasionally credential material from surrounding frames). Error text is hand-written constants plus an exception class name.

## Config

| Setting | Default | Override |
|---|---|---|
| PallaDrive root | `/home/daniel/obsidian-vaults/palladrive` | `PALLADRIVE_PATH` env var |
| Primer path | `_system-files/core_text/PRIMER.md` | edit `_PRIMER_RELATIVE` |
| Injection cap | 6,000 chars | edit `_MAX_CHARS` |
| Inject on | first turn only | `_is_first_turn` |

> ⚠️ The sibling path `/home/daniel/obsidian-vaults/palladia` (no `r`) is a **different, near-empty historical folder**. Never point at it. The real Obsidian Sync materialization is `…/palladrive`, verified bidirectional on olympus1 2026-08-29 (77 content files, 23 PDFs, 3 `.base`).

## Tests

```bash
python3 -m unittest test_primer_hook -v
```

15 tests: normal load, missing timestamp, no frontmatter, missing file, missing directory, unreadable file, directory-in-place-of-file, oversize truncation, under-cap passthrough, arbitrary kwargs, the never-raises guarantee across five malformed inputs, and four contract tests — registration wires `pre_llm_call` **and explicitly asserts it is not `on_session_start`**, later turns return `None`, first turns inject, and a missing `is_first_turn` field still injects.

## Enablement — not automatic

Standalone plugins are **opt-in**. Copying the files is not enough; the desired-state config carries `plugins.enabled: [palladia-primer]` and the runbook runs:

```bash
hermes -p palladia plugins enable palladia-primer
```

Without that step the plugin sits on disk and never loads.

## Dependency

The primer must exist and be refreshed. **The refresh task is v2 and is not wired** — for v1 the file is hand-seeded, so its `generated_at` will go stale. The staleness rule in the primer and the timestamp line in the injection are the v1 mitigation, not a fix.
