# Palladia rehabilitation runbook — canonical → runtime, in place

**Author:** ChiefPM · 2026-08-29
**Daniel reviewed:** no
**Status:** SPECIFIED — NOT RUN. Nothing here has been executed on olympus1.
**Supersedes:** `Installer_Palladia_ChiefPM_2026-08-29.md` §3 (the 15-step blank-profile installer). That document's mapping table (§2) and three-location model (§1) remain valid and are referenced, not repeated. Its step list is dead.
**Executor:** Vulcan on olympus1 (shell + sudo-free), with Daniel for the two UI/interactive gates.
**Inputs:** `PROMOTION-MANIFEST.md` in PallaDrive canonical (29 files, sha256-pinned).
**Deadline context:** Daniel's BCG New Jersey interview is **Thursday 2026-09-03**. Keep every archive until after it.

---

## 0. What changed, and the one apparent contradiction

Vulcan's 2026-08-29 audit returned **DO NOT RUN** on the original installer. Daniel's controlling decision, recorded in that audit: do not build a replacement profile from scratch — preserve the working substrate and rehabilitate in place.

That reads as a contradiction against the standing rule *"`~/.hermes/profiles/palladia/` is FROZEN and identity-failed. Evidence, not a base. Never clone it forward."* It is not one, and the reconciliation is the spine of this document:

> **Never clone forward the contaminated surfaces. Do preserve the credential substrate.**

| Preserve — it works, it is expensive to rebuild, and it carries no identity | Replace or archive — it is contaminated, and it is why PALLADIA-001 happened |
|---|---|
| `auth.json` (Codex OAuth) | `SOUL.md` |
| `.env` (web keys, BWS wiring) | `profile.yaml` |
| Discord token materialization + IDs | `memories/MEMORY.md`, `memories/USER.md` (seed) |
| Session/state databases and history | the entire `skills/` tree |
| Voice and model setup | the entire `plugins/` tree |
| The profile wrapper in `~/.local/bin/` | every config delta in §5 |
| Logs, kept for forensics | `terminal.cwd` |

Nothing that made Palladia believe she was Vulcan survives this. Everything that took a human an afternoon to credential does.

**The one thing that is genuinely lost by this choice:** a blank profile proves the loadout is exactly what we declared. An in-place rehabilitation cannot prove that by construction — it proves it by measurement. Step 7's allowlist gate is therefore a **STOP**, not a note-and-continue. That gate is the whole price of this decision. Do not soften it.

### Corrections absorbed from Vulcan's audit

| # | Audit finding | Resolution here |
|---|---|---|
| 1 | `on_session_start` return values are **ignored**; injection is `pre_llm_call` | Plugin rewritten to `pre_llm_call`, first-turn-gated. v0.2.0, 15/15 tests. Independently confirmed against Hermes' shipped-hook catalog. |
| 2 | `hermes hooks fire` does not exist | Removed. Replaced with a real integration gate (Step 12b). |
| 3 | `hermes profile create palladia` cannot run — the path is occupied | Deleted. No profile is created. |
| 4 | `plugins.enabled: []` conflicts with shipping the primer | Corrected to `[palladia-primer]` + an explicit enable step (Step 8). |
| 5 | `dispatch_in_gateway` is nested under `kanban:` | Corrected everywhere; applied via `config set kanban.dispatch_in_gateway false`. |
| 6 | Live gateway (PID 769944) never quiesced before snapshot | Step 1 is now quiesce, before anything is read or written. |
| 7 | Rollback consumed its own snapshot and lived inside `profiles/` | Rewritten (§9): checksummed archive **outside** `profiles/`, copy-not-move restore, external state captured. |
| 8 | Skill-loader restart claimed mandatory | Corrected: `/reload-skills` suffices for skill files; restart is for plugins/platform config. |
| 9 | Runtime PallaDrive path wrong (`…/palladia`) | Corrected to `/home/daniel/obsidian-vaults/palladrive` in SOUL, config, plugin, README. |
| 10 | Skill category map stale in the installer | Resolved at the source: all 16 skills now carry a top-level `category`, and their previously-conflicting `metadata.category` was reconciled to match (11 files). The runbook derives paths from the files. |
| 11 | Node/npm/`ob` reported absent | Stale. Node v22.23.1, npm 10.9.8, `obsidian-headless` 0.0.14 all present, no sudo used. |
| 12 | P22 open | **RESOLVED.** Bidirectional Obsidian Sync at `/home/daniel/obsidian-vaults/palladrive`. |

**Where Vulcan is wrong, and this document overrides him:** his §7 count of *15 custom / 32 total* omits `weakness-derivation`. It is in the drafts, in the registry, promoted in the manifest, and it is the skill that enforces the `Activity == "Taken"` filter. **Authoritative: 17 inherited + 16 custom = 33.**

---

## 1. Quiesce — before anything is read or written

A snapshot taken while the gateway is live captures torn SQLite/WAL and half-written session state. That is not a restore point; it is a plausible-looking one, which is worse.

```bash
# Identify every live Palladia process. The audit observed gateway PID 769944
# and a manual continuous-sync PID 788126 — do NOT kill the sync one.
pgrep -af 'HERMES_PROFILE=palladia|hermes.*-p *palladia' || true
```

Stop the gateway by whatever route started it (it was launched manually, not as a service):

```bash
hermes gateway stop -p palladia 2>/dev/null || kill <gateway-pid>
sleep 3
pgrep -af 'HERMES_PROFILE=palladia' && echo "STILL RUNNING — do not proceed" || echo "quiesced"
```

**Leave `ob sync --continuous` running.** It is how canonical reaches this host.

| Gate | Pass | On fail |
|---|---|---|
| G1.1 | No process holds `HERMES_HOME=…/profiles/palladia` | **STOP.** Every downstream guarantee depends on this. |

---

## 2. Archive — checksummed, outside `profiles/`

```bash
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
ARCH=~/palladia-rehab-archive/$STAMP
mkdir -p "$ARCH"

# Whole profile, permissions preserved.
tar -C ~/.hermes/profiles -cf "$ARCH/palladia-profile.tar" palladia
shasum -a 256 "$ARCH/palladia-profile.tar" > "$ARCH/palladia-profile.tar.sha256"

# External state the profile directory does NOT contain.
systemctl --user list-unit-files 'hermes*'        > "$ARCH/systemd-units.txt"  2>&1 || true
systemctl --user is-enabled hermes-gateway-palladia.service >> "$ARCH/systemd-units.txt" 2>&1 || true
ls -la ~/.local/bin | grep -i palladia            > "$ARCH/wrapper.txt"        2>&1 || true
ob sync-list-local --json                         > "$ARCH/obsidian-sync.json" 2>&1 || true
( cd /home/daniel/obsidian-vaults/palladrive && find . -type f -not -path './.obsidian/*' | sort | xargs shasum -a 256 ) \
                                                  > "$ARCH/palladrive-pre.sha256" 2>&1 || true

shasum -a 256 -c "$ARCH/palladia-profile.tar.sha256" && echo "ARCHIVE VERIFIED"
```

| Gate | Pass | On fail |
|---|---|---|
| G2.1 | `shasum -c` prints `OK` | **STOP.** No archive, no install. |
| G2.2 | `$ARCH` is outside `~/.hermes/profiles/` | **STOP.** A backup inside the tree you are about to mutate is not a backup. |

> The archive is **not** a rollback target on its own — restoring it restores the identity-failed profile. It is a floor: it guarantees you can always get back to *a known state*, including the credentials. §9 explains what restore actually means here.

---

## 3. Confirm canonical landed

Canonical lives in PallaDrive. It reaches olympus1 over Obsidian Sync, which pushes from Daniel's Mac only while Obsidian is open on that vault.

```bash
ob sync --path /home/daniel/obsidian-vaults/palladrive
cd /home/daniel/obsidian-vaults/palladrive
cat _system-files/canonical/PROMOTION-MANIFEST.md | head -60
find _system-files/canonical _system-files/primer _system-files/scripts \
     -type f \( -name '*.md' -o -name '*.yaml' -o -name '*.py' \) | sort | xargs sha256sum
```

| Gate | Pass | On fail |
|---|---|---|
| G3.1 | All 29 manifest rows present | **STOP.** Ask Daniel to open Obsidian on the Mac and let it push. |
| G3.2 | Every hash matches the manifest | **STOP.** A half-synced canonical installs a runtime nobody reviewed. |

Set the working variables once:

```bash
CAN=/home/daniel/obsidian-vaults/palladrive/_system-files/canonical
P=~/.hermes/profiles/palladia
```

---

## 4. Archive the contaminated trees — move, never delete

Standing Rule #1: nothing is deleted without Daniel's explicit instruction. These trees are also PALLADIA-004/-005 evidence.

```bash
mv "$P/skills"  "$ARCH/skills-contaminated"
mv "$P/plugins" "$ARCH/plugins-contaminated" 2>/dev/null || true
mkdir -p "$P/skills"
ls "$ARCH/skills-contaminated" | wc -l     # expect the inherited 128-skill population
find "$P/skills" -name SKILL.md | wc -l    # expect 0
```

| Gate | Pass | On fail |
|---|---|---|
| G4.1 | `$P/skills` contains zero `SKILL.md` | **STOP.** |
| G4.2 | The moved trees are readable inside `$ARCH` | **STOP.** You just moved the only copy. |

---

## 5. Identity — first, because it is the entire point

```bash
cp "$CAN/identity/SOUL.md"     "$P/SOUL.md"
cp "$CAN/identity/profile.yaml" "$P/profile.yaml"

head -1 "$P/SOUL.md"
grep -ic vulcan "$P/SOUL.md"
grep -ic chiron "$P/profile.yaml"
diff "$CAN/identity/SOUL.md" "$P/SOUL.md" && echo "SOUL byte-identical"
```

| Gate | Pass | On fail |
|---|---|---|
| G5.1 | First heading contains `Palladia` | **STOP AND ROLL BACK.** |
| G5.2 | `grep -ic vulcan` → `0` | **STOP AND ROLL BACK.** This is PALLADIA-001. |
| G5.3 | `grep -ic chiron` on `profile.yaml` → `0` | **STOP.** PALLADIA-007. |
| G5.4 | `diff` canonical↔runtime empty for both | **STOP.** |

### 5b. Memory — `copy-once`, and this profile has history

`MEMORY.md` and `USER.md` are **agent-owned after seeding**. The frozen profile's copies are contaminated (they were written by an agent that thought it was Vulcan), so on this one occasion they ARE replaced — but the rule that governs every future install is `copy-once`, and it starts now.

```bash
mkdir -p "$P/memories"
cp "$P/memories/MEMORY.md" "$ARCH/MEMORY.contaminated.md" 2>/dev/null || true
cp "$P/memories/USER.md"   "$ARCH/USER.contaminated.md"   2>/dev/null || true
cp "$CAN/identity/MEMORY.md" "$P/memories/MEMORY.md"
cp "$CAN/identity/USER.md"   "$P/memories/USER.md"
wc -m "$P/memories/MEMORY.md" "$P/memories/USER.md"
grep -c '2026-09-03\|BCG' "$P/memories/MEMORY.md"
```

| Gate | Pass | On fail |
|---|---|---|
| G5.5 | Both files < 2200 characters | **STOP.** Over the cap, Hermes truncates and the tail is silently lost. |
| G5.6 | `MEMORY.md` carries the BCG NJ / 2026-09-03 line | **STOP.** |
| G5.7 | `USER.md`'s locked block is present — **re-measure, do not trust the pinned hash** in the old installer; Daniel edited it 2026-08-29 and may again | Note and continue; report the measured value to Daniel. |

> **Every install after this one skips 5b entirely.** Overwriting these destroys what she has learned about Daniel.

---

## 6. Config — `config set` only, never a YAML overwrite

`config.yaml` is 18,986 bytes of working configuration including credential wiring. Copying a partial desired-state YAML over it destroys the substrate this whole approach exists to preserve. **Apply deltas.**

```bash
hermes -p palladia config set kanban.dispatch_in_gateway false
hermes -p palladia config set terminal.cwd /home/daniel/obsidian-vaults/palladrive
hermes -p palladia config set discord.require_mention false
```

### The six invariants

| # | Invariant | Verify | On fail |
|---|---|---|---|
| C1 | `kanban.dispatch_in_gateway` is `false` | `hermes -p palladia config get kanban.dispatch_in_gateway` → `false`. **Note:** the bare `dispatch_in_gateway` key returns `not set` and that is expected — top-level is the wrong path. | STOP |
| C2 | `model.default: gpt-5.6-terra`, provider `openai-codex` | `config get` both. Codex uses the **bare** model name; the Nous portal uses an `openai/`-prefixed form. Switching provider without stripping the prefix fails resolution silently. | STOP |
| C3 | `auth.json` `providers` includes `openai-codex` | `python3 -c "import json;print(sorted(json.load(open('$P/auth.json'))['providers']))"` — **names only, never values** | STOP |
| C4 | Connected platforms == exactly `{discord}` | **Discover the effective keys first** — `hermes -p palladia config list` — then set what exists. `gateway_platforms` is this package's desired-state vocabulary and is **not verified** as the runtime key path. Acceptance is behavioural (Step 13), not textual. | STOP |
| C5 | No `nova_ops`, no `nova_vault`, no `agent-registry-guard` | `config list \| grep -iE 'nova_ops\|nova_vault\|registry'` → empty | STOP |
| C6 | `discord.require_mention` is `false` | `config get`. **This install is the test** of PALLADIA-010 — ordinary messages ignored while slash commands worked. | Note; Step 13 is the real gate |

### Credentials — verify by NAME, never by value

```bash
grep -oE '^[A-Z0-9_]+' "$P/.env" | sort -u | grep -E 'EXA|BROWSERBASE|DISCORD'
```

| Gate | Pass | On fail |
|---|---|---|
| G6.1 | `EXA_API_KEY`, `BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID` names present | STOP |
| G6.2 | **No command in this runbook prints a credential value** | If one did, treat it as an incident, not a typo. |

---

## 7. Skills — 33, and the count is a STOP gate

Runtime layout is `skills/<category>/<name>/SKILL.md`. Categories come from each file's top-level `category:` frontmatter, now reconciled with its `metadata.category` (11 files corrected).

### 7a. The 16 custom skills

```bash
cd "$CAN/skills_library"
for d in */; do
  n=${d%/}
  c=$(awk '/^---$/{n++;next} n==1 && /^category:/{print $2; exit}' "$n/SKILL.md")
  [ -n "$c" ] || { echo "NO CATEGORY: $n"; continue; }
  mkdir -p "$P/skills/$c/$n"
  cp "$n/SKILL.md" "$P/skills/$c/$n/SKILL.md"
  echo "$c/$n"
done
```

Expected destinations:

| Category | Skills |
|---|---|
| `casing` (8) | `behavioral-scoring`, `case-scoring`, `casebook-case-extract`, `high-yield-drills`, `post-case-loop`, `session-intake`, `warm-up`, `weakness-derivation` |
| `discipline` (3) | `assumption-check`, `sequential-thinking`, `verification-before-completion` |
| `palladia` (2) | `palladia-worklog`, `update-primer` |
| `automation` (1) | `cron-creator` |
| `creative` (1) | `generate-image` |
| `software-development` (1) | `hermes-skill-creator` |

### 7b. The 17 inherited skills — install from source, not from the archive

```text
find-docs                         innovation/obsidian-headless-sync
messaging-voice-conversation      note-taking/obsidian
productivity/document-to-action-items   productivity/docx
productivity/google-workspace     productivity/meeting-action-items
productivity/nano-pdf             productivity/ocr-and-documents
productivity/pdf                  productivity/powerpoint
productivity/session-librarian    productivity/weekly-review-planning
productivity/xlsx                 research/blocked-page-recovery
research/grounded-citations
```

Preferred source is the Hermes skills distribution at its original category paths. If no clean source path exists on this host, the fallback is a **named, one-by-one** copy out of `$ARCH/skills-contaminated/` — never `cp -r` of the tree, which is how 128 skills got there the first time.

> `obsidian-headless-sync` is **setup-wizard only.** It is installed so the wizard exists; Palladia must never invoke it post-setup without Daniel's clearance. That constraint lives in her SOUL, not in a filesystem permission.

### 7c. The gate

```bash
find "$P/skills" -name SKILL.md | wc -l                       # expect 33
find "$P/skills" -name SKILL.md | sed 's|.*/\([^/]*\)/SKILL.md|\1|' | sort > /tmp/installed.txt
# Compare against the 33-name allowlist (16 above + 17 inherited).
```

| Gate | Pass | On fail |
|---|---|---|
| G7.1 | Exactly **33** `SKILL.md` files | **STOP.** |
| G7.2 | **Zero** skills outside the allowlist | **STOP — not note-and-continue.** This gate is the entire price of choosing in-place rehabilitation over a blank profile. PALLADIA-004 was 128 inherited skills nobody declared. If it fires, archive the offender and re-run; do not proceed past it. |
| G7.3 | Under-count | **STOP.** A missing skill is a capability Daniel will reach for on Wednesday night. |

---

## 8. Plugin — copy, then **enable**

```bash
mkdir -p "$P/plugins/palladia-primer"
cp "$CAN/plugins/palladia-primer/"{plugin.yaml,__init__.py,test_primer_hook.py,README.md} \
   "$P/plugins/palladia-primer/"
cd "$P/plugins/palladia-primer" && python3 -m unittest test_primer_hook -v 2>&1 | tail -3
grep -n 'provides_hooks' -A2 plugin.yaml
hermes -p palladia plugins enable palladia-primer
hermes -p palladia plugins list
```

| Gate | Pass | On fail |
|---|---|---|
| G8.1 | `15 tests … OK` | STOP |
| G8.2 | `plugin.yaml` declares `pre_llm_call` — **not** `on_session_start` | **STOP.** `on_session_start` returns are ignored; that wiring injects nothing, silently, forever. |
| G8.3 | `plugins list` shows `palladia-primer` **enabled** | **STOP.** Standalone plugins are opt-in; copied-but-not-enabled looks identical to installed. |
| G8.4 | `plugins list` shows **no** `agent-registry-guard` | STOP. PALLADIA-006. |

### Primer file

`_system-files/primer/PRIMER.md` arrives over Obsidian Sync (manifest row 29). Verify from the runtime's own view of the drive:

```bash
ls -l /home/daniel/obsidian-vaults/palladrive/_system-files/primer/PRIMER.md
head -5 /home/daniel/obsidian-vaults/palladrive/_system-files/primer/PRIMER.md
```

| Gate | Pass | On fail |
|---|---|---|
| G8.5 | File exists and `generated_at` is present | **STOP.** Without it the hook fires its loud missing-primer notice on every session. That is by design and it is not acceptable as a launch state. |

---

## 9. Drive map

```bash
mkdir -p "$P/bin"
cp /home/daniel/obsidian-vaults/palladrive/_system-files/scripts_library/gen_drive_map.py "$P/bin/"
python3 /home/daniel/obsidian-vaults/palladrive/_system-files/scripts_library/gen_drive_map.py \
        /home/daniel/obsidian-vaults/palladrive
grep -m1 generated /home/daniel/obsidian-vaults/palladrive/_meta/DRIVE-MAP.md
```

| Gate | Pass | On fail |
|---|---|---|
| G9.1 | `DRIVE-MAP.md` regenerated with a current stamp and a file count matching the live drive | Note and continue. |

> The map was stale at audit time (75 vs 77 files). SOUL points at it, so a stale map is a map that lies to her about what she can read.

---

## 10. Static gates — everything verifiable before spending a model turn

```bash
grep -ic vulcan "$P/SOUL.md"                          # 0
grep -ic 'obsidian-vaults/palladia$' "$P"/SOUL.md     # 0 live refs (warnings are fine)
hermes -p palladia config get terminal.cwd            # …/palladrive
hermes -p palladia config get kanban.dispatch_in_gateway  # false
find "$P/skills" -name SKILL.md | wc -l               # 33
hermes -p palladia plugins list                       # palladia-primer enabled, nothing else
```

| Gate | Pass | On fail |
|---|---|---|
| G10.1 | All six lines return the expected value | **STOP.** Every one of these is free; a model turn is not. |

---

## 11. Reload — restart is NOT required for skills

```bash
hermes -p palladia   # start a CLI session
/reload-skills
/skills              # or the equivalent listing command
```

`/reload-skills` rescans the profile's skill tree in a running CLI or gateway; Hermes also does mtime/signature invalidation with a short discovery TTL. A gateway restart is required for **plugin enablement and platform config**, which Step 8 changed — so the gateway does get restarted, but in Step 13, and not because of the skill loader.

| Gate | Pass | On fail |
|---|---|---|
| G11.1 | Skill listing shows 33 and includes `weakness-derivation` | STOP |

---

## 12. Identity and primer — the two tests that justify the project

### 12a. Cold identity

In a fresh CLI session, ask: **"Who are you?"**

| Gate | Pass | On fail |
|---|---|---|
| G12.1 | She answers *Palladia*, a case-interview coach. Not Vulcan. Not a chief of staff. Not a generic assistant. | **STOP AND ROLL BACK (§14).** This is PALLADIA-001 recurring, and everything built on a wrong identity is wasted. |

### 12b. Primer injection — the integration gate that replaces `hermes hooks fire`

`hermes hooks fire` does not exist and would have targeted shell hooks anyway. The real test is behavioural. In a **new** session, first turn:

> *"Without reading any files, what is my current target and what are my open weaknesses?"*

| Gate | Pass | On fail |
|---|---|---|
| G12.2 | She answers from primer content — the BCG NJ target and named weaknesses — without a file-read tool call | **STOP.** The injection is not landing. Confirm `plugin.yaml` says `pre_llm_call`, the plugin is *enabled*, and `PALLADRIVE_PATH` resolves. |
| G12.3 | Temporarily rename `PRIMER.md`, open a new session, ask again → she reports the primer is missing and says her state may be stale | Note. Confirms fail-loud rather than fail-silent. **Rename it back.** |
| G12.4 | On the **second** turn of the same session, the primer block is not repeated | Note. Confirms the first-turn gate. Repetition means `is_first_turn` is absent — visible, not dangerous, but report it. |

---

## 13. Gateway — foreground first, service last

Run the FirstLaunchChecklist gates 1–8 before this step.

```bash
# Foreground, profile-scoped, under an external terminal or supervisor.
hermes -p palladia gateway run
```

| Gate | Pass | On fail |
|---|---|---|
| G13.1 | Connected platforms == exactly `{discord}`. No Telegram or Slack connection attempt, no token conflict. | **STOP.** PALLADIA-008. |
| G13.2 | An **ordinary message** (no slash command, no @mention) in `palladia-text` gets a reply | **STOP.** This is the PALLADIA-010 test and C6's real gate. |
| G13.3 | Voice channel reachable | Note and continue. |
| G13.4 | A real Codex turn completes, and the provider used is `openai-codex` — not a paid fallback | **STOP.** C3 exists because that failover is silent and was observed live on Vulcan. |

Stop the foreground gateway before installing the service.

```bash
# Only after every gate above has passed.
# Install the profile-scoped unit with an EXPLICIT HERMES_HOME.
systemctl --user daemon-reload
systemctl --user enable --now hermes-gateway-palladia.service
systemctl --user status hermes-gateway-palladia.service
pgrep -af 'HERMES_PROFILE=palladia'
```

| Gate | Pass | On fail |
|---|---|---|
| G13.5 | Unit active; process env shows `HERMES_HOME=…/profiles/palladia` | **STOP.** PALLADIA-009 — process environment does not travel the way you assume. |
| G13.6 | One more ordinary Discord message answered, now under the service | STOP |

---

## 14. Rollback — what it actually means here

The old rollback restored the frozen profile. That gets you back to an agent that thinks it is Vulcan, which is not a fallback — it is the failure.

**Three tiers, pick by what broke:**

| Tier | When | Action |
|---|---|---|
| **T1 — surface revert** | A single artifact is wrong (a skill, the plugin, one config key) | Re-copy that artifact from `$CAN`, or `config set` the key back. The archive stays sealed. Cheapest and the common case. |
| **T2 — loadout revert** | Skills/plugins are in an unknown state | `rm -rf "$P/skills" "$P/plugins"`, re-run Steps 7–8. Identity and credentials untouched. |
| **T3 — full restore** | Identity or credentials are damaged | See below. |

```bash
# T3. COPY out of the archive; never move — the archive must survive the restore.
hermes gateway stop -p palladia 2>/dev/null || true
systemctl --user stop hermes-gateway-palladia.service 2>/dev/null || true
shasum -a 256 -c "$ARCH/palladia-profile.tar.sha256"     # verify BEFORE trusting it
mv ~/.hermes/profiles/palladia ~/.hermes/profiles/palladia.failed-$(date -u +%H%M%S)
tar -C ~/.hermes/profiles -xf "$ARCH/palladia-profile.tar"
diff -rq ~/.hermes/profiles/palladia <(echo) 2>/dev/null || true
```

T3 restores the **credential substrate and a known-bad identity**. That is the correct trade under time pressure: Daniel gets a working gateway with wrong personality, and Steps 5–8 can be re-run against it. It is a floor, not a destination.

**Not covered by the profile archive — restore separately from `$ARCH`:** the systemd unit and its enabled state (`systemd-units.txt`), the `~/.local/bin` wrapper (`wrapper.txt`), Obsidian Sync configuration (`obsidian-sync.json`), and any PallaDrive file the primer seed or drive-map run touched (`palladrive-pre.sha256`).

**Keep every archive until after Thursday 2026-09-03.** Standing Rule #1 — nothing is deleted without Daniel saying so.

---

## 15. Idempotency — an honest statement

The old installer claimed Steps 1–9 were idempotent. They were not.

| Re-runnable cleanly | Not idempotent |
|---|---|
| Step 5 identity copy | Step 2 (archive stamp changes each run) |
| Step 6 `config set` calls | Step 5b (**skipped on every re-run by design** — `copy-once`) |
| Step 7 skill copy | Step 9 (drive-map timestamp changes) |
| Step 8 plugin copy + enable | Steps 1, 13 (process lifecycle) |
| Steps 10, 11 verification | Step 4 (the contaminated trees are gone after the first run) |

Re-running the whole runbook top-to-bottom is safe **except** that Step 4 finds nothing to move and Step 5b must be skipped. Both are visible, neither is destructive.

---

## 16. What this runbook does NOT do

1. **No `hermes profile create`.** The profile exists and is being kept.
2. **No `--clone-from`.** That one flag caused PALLADIA-001, -002, -003, -004, -005, -006, -008 and -016.
3. **No hand-edit of runtime.** Runtime is materialized from canonical. A runtime-only edit is drift and dies at the next install.
4. **No credential value written anywhere.** `.env` and `auth.json` are `no-ship` and never enter PallaDrive — the drive replicates to two clouds. `granola_api` is pasted by Daniel through the Obsidian plugin UI.
5. **No deletion.** Contaminated trees are moved to `$ARCH`. SR#1.
6. **No edit through the Hermes Desktop UI.** `~/.hermes/` *is* Hermes; an edit without an explicit profile selection silently retargets him.
7. **No `deploy-olympus1.py`.** A general fleet deployer is a much larger commitment than this needs.
8. **No continuous-sync service.** `ob sync --continuous` runs manually (PID 788126 at audit). A managed unit is a reviewed task for after Thursday.
9. **No casebook guard hook.** Brief only, never built — v2. The blocking contract is now known and recorded in §17 so it is not re-derived.
10. **No PallaDrive file schema.** Daniel is designing it. A skill that lacks a home for a field **asks**; it does not invent one.

---

## 17. Carried forward to v2 — recorded so nothing is re-derived

| Item | State |
|---|---|
| **Casebook guard hook** | Not built. Contract now verified: `pre_tool_call` blocks with `{"action": "block", "message": "<non-empty reason>"}`; first valid directive wins; a **timed-out** `pre_tool_call` fails closed. The old "cannot fail closed, Hermes logs and skips a raising hook" note is only half true — *raising* still skips, but *returning* a block directive works and a timeout blocks. Build it with an explicit `try/except` that returns the block dict, never one that raises. |
| **Primer refresh cron** | Specified (`canonical/cron/palladia-primer-refresh.md`), deliberately **not wired**. Until it is, `PRIMER.md` goes stale and the injected `generated_at` line is the only mitigation. |
| **`casebook-case-extract`** | 235 lines, over the 60–160 house range, and **unrunnable** until a bounded extraction tool exists. Ships as specification. |
| **`session-intake`** | 231 lines; depends on the Granola token (Daniel, UI) and the Granola MCP (untested — B11/P23). |
| **`generate-image`** | Depends on the fal.ai MCP (not installed — B14). |
| **`high-yield-drills`** | Template stub by design; written from live drilling. |
| **Bases syntax** | `Worklog.base` and `Case Log.base` are drafted from Obsidian docs and **never watched render**. If columns come up empty, it is the `note.` prefix — see `canonical/Bases-Reference_DRAFT.md`. |
| **`Case Log.base` / `case-session-entry.md`** | Appeared from the SOUL-review fork; not built by this project. `case-session-entry.md` commits case-session schema Daniel said he was still designing. **Confirm intended before relying on either.** GapReport G3. |
| **`visual-walkthrough`** | Cut to v2. Absent from drafts, absent from canonical, and removed from the registry row. |
| **Managed continuous-sync unit** | Deferred. Manual `ob sync --continuous` is the interim. |

---

## 18. Execution status

**SPECIFIED — NOT RUN.** No step in this document has been executed on olympus1.

**Done on the Mac side (this session):** canonical promotion of 29 hash-pinned files into PallaDrive; primer plugin corrected to `pre_llm_call` (15/15); config key paths corrected; SOUL's P22 blank filled with the resolved path; 11 skill files' `metadata.category` reconciled; registry row and worklog synced.

**Blocking the first step:** Daniel opening Obsidian on the Mac so canonical pushes, and Vulcan confirming the 29 hashes on olympus1 (§3). Then §1 onward.
