# Palladia canonical promotion manifest

**Author:** ChiefPM · 2026-08-29
**Daniel reviewed:** no
**Status:** PROMOTED to PallaDrive canonical on Daniel's Mac. **Not yet confirmed landed on olympus1** — see §3.

Source of truth for what the Palladia rehabilitation installs. Every row was reviewed
in the Nova Caelum workspace, corrected against Vulcan's 2026-08-29 audit, and copied
here. Runtime is materialized FROM this tree, never the other way round.

**Excluded by design:** `__pycache__/`, `*.pyc`, `auth.json`, `.env`, logs, databases,
forensic runtime files, and the 14 Nova Caelum build-record documents (they describe
building the product; they are not part of it). `visual-walkthrough` is cut to v2 and
is deliberately absent.

**Not canonical, but promoted alongside:**
- `_system-files/primer/PRIMER.md` — generated artifact, seeded here so the plugin has something to read on first launch.
- `_system-files/scripts/gen_drive_map.py` — already in its final home; verified byte-identical to the workspace draft, nothing to promote.

## 1. Source → destination, with hashes

| # | Workspace source | PallaDrive destination | sha256 |
|---:|---|---|---|
| 1 | `drafts/SOUL.md` | `_system-files/canonical/identity/SOUL.md` | `f58d74ac9011125440b398cec5226bde7ba0ccb9e4521a9fa6aa8802d0905b88` |
| 2 | `drafts/MEMORY.md` | `_system-files/canonical/identity/MEMORY.md` | `ef19aa6647936ce02b54eeed388bbae4d7013ed91ac941485aa34d94ad65a8c2` |
| 3 | `drafts/USER.md` | `_system-files/canonical/identity/USER.md` | `4a1b125543cea9bce54e29cf8de0a4ed4ab683f5a1ac06a4594282a0ec0bbd24` |
| 4 | `drafts/profile.yaml` | `_system-files/canonical/identity/profile.yaml` | `7d25af0f5f9ddcfa2683cf114a4f30c9589d8b297d366eefc4045bd9228b395f` |
| 5 | `drafts/config-desired-state.yaml` | `_system-files/canonical/config/config-desired-state.yaml` | `40bee8898ca15987555e1d24c12de00d11eeefca38bdbb29f46e778a46abf6f6` |
| 6 | `drafts/reference/SELF-MANAGEMENT.md` | `_system-files/canonical/reference/SELF-MANAGEMENT.md` | `d0110d609d0b28c50b8bcfead7241b5600a24c42ca9c30d2b23c142cb5db5b75` |
| 7 | `drafts/cron/palladia-primer-refresh.md` | `_system-files/canonical/cron/palladia-primer-refresh.md` | `06bb31a36af25f8dae511e527a0c79a336a5d5afd7a6b11ce9b7b940cbdd3ea7` |
| 8 | `drafts/plugins/palladia-primer/plugin.yaml` | `_system-files/canonical/plugins/palladia-primer/plugin.yaml` | `2a1e116d2982b84a4a736499a80a47e491c7245dbde0faf0e7937915e9625cb2` |
| 9 | `drafts/plugins/palladia-primer/__init__.py` | `_system-files/canonical/plugins/palladia-primer/__init__.py` | `5d47089d5a0c9114cc44570ccac4ce83e088bdfb591de7fd56b16284ecf3b402` |
| 10 | `drafts/plugins/palladia-primer/test_primer_hook.py` | `_system-files/canonical/plugins/palladia-primer/test_primer_hook.py` | `b06e9e761fd1331fe9834fae4721ebc6a18cc826c5bdecb3caeb05bb4bdafbbb` |
| 11 | `drafts/plugins/palladia-primer/README.md` | `_system-files/canonical/plugins/palladia-primer/README.md` | `e2d968c190ef0fd9a90905b10066c586cd2392ae11255c20abd0cad6f781245d` |
| 12 | `drafts/skills/assumption-check//SKILL.md` | `_system-files/canonical/skills_library/assumption-check/SKILL.md` | `20d270fd0709a49508d8c09ea75592fe5af9c9174591ce78f6bfe77fb5b8d10e` |
| 13 | `drafts/skills/behavioral-scoring//SKILL.md` | `_system-files/canonical/skills_library/behavioral-scoring/SKILL.md` | `0cc25b6b414a9535dbf281f6281f0a01124643ccd997e5ea1778ba097966cbd4` |
| 14 | `drafts/skills/case-scoring//SKILL.md` | `_system-files/canonical/skills_library/case-scoring/SKILL.md` | `f508e2765c7e19556ef8a267e132d5074ef7ab0227f4c6f65f44e5fd4c10c600` |
| 15 | `drafts/skills/casebook-case-extract//SKILL.md` | `_system-files/canonical/skills_library/casebook-case-extract/SKILL.md` | `875fbe0b56e93712ee4fa48feee2fcd0b0caafb6da63cd14538717201f9f91c5` |
| 16 | `drafts/skills/cron-creator//SKILL.md` | `_system-files/canonical/skills_library/cron-creator/SKILL.md` | `3ba6f56e09dfe04fe6c177ee3cd1c9e38adce79980e0c45ff20b16ff884154d6` |
| 17 | `drafts/skills/generate-image//SKILL.md` | `_system-files/canonical/skills_library/generate-image/SKILL.md` | `f1f3cab462fd8272cf74065561ac1c1d16e0392663fe45aa9be2e0c4b3da2e08` |
| 18 | `drafts/skills/hermes-skill-creator//SKILL.md` | `_system-files/canonical/skills_library/hermes-skill-creator/SKILL.md` | `8a3c80277e86a754cb0382dbf7946c55a426b7be574edccfb68dd07f85f5144f` |
| 19 | `drafts/skills/high-yield-drills//SKILL.md` | `_system-files/canonical/skills_library/high-yield-drills/SKILL.md` | `41b5936dd907284cebc289bde6d2254d5f633dd779bf1033be6500deb4fb8fc8` |
| 20 | `drafts/skills/palladia-worklog//SKILL.md` | `_system-files/canonical/skills_library/palladia-worklog/SKILL.md` | `61ae2d47013efbdd9b2cfc92732bb270eaae1d3cce4f1a23859aff4074aead62` |
| 21 | `drafts/skills/post-case-loop//SKILL.md` | `_system-files/canonical/skills_library/post-case-loop/SKILL.md` | `e778ab4ad168f7e6878dd7296c3a33a9de3517bbac264935114e39985a4a9d4d` |
| 22 | `drafts/skills/sequential-thinking//SKILL.md` | `_system-files/canonical/skills_library/sequential-thinking/SKILL.md` | `9928d8188014e44780db54460c22f86f1448941df955a08a0d208fbc77d8e561` |
| 23 | `drafts/skills/session-intake//SKILL.md` | `_system-files/canonical/skills_library/session-intake/SKILL.md` | `798100ef0d544421407951334abb1cad27acacd8d8ab690f248afdc38a1404d8` |
| 24 | `drafts/skills/update-primer//SKILL.md` | `_system-files/canonical/skills_library/update-primer/SKILL.md` | `f829cb1408833b4670df8f914143ca0cbd004072221fc5e759d0a8c5cb6c45ae` |
| 25 | `drafts/skills/verification-before-completion//SKILL.md` | `_system-files/canonical/skills_library/verification-before-completion/SKILL.md` | `36cad4178ed6dfab1253bd9e5531f5bcb9f047ac2dc866cfef2d54ec2a530f07` |
| 26 | `drafts/skills/warm-up//SKILL.md` | `_system-files/canonical/skills_library/warm-up/SKILL.md` | `e7617514cc95e7935b5c634f9f5cf8ecc2a2cfd343eae693f8bb8f11a3b87b22` |
| 27 | `drafts/skills/weakness-derivation//SKILL.md` | `_system-files/canonical/skills_library/weakness-derivation/SKILL.md` | `0835cc84f6d1a36a758815a846a0f12b2a1db5de14c1b046757c173b5bf2c0d4` |
| 28 | `drafts/primer/PRIMER.md` | `_system-files/primer/PRIMER.md` | `241d7febea59f975f30636a060a0fcbf5dc2a1768cbd59906e952b9c847d4889` |
| 29 | `drafts/scripts/gen_drive_map.py` | `_system-files/scripts/gen_drive_map.py` | `4e14cb6fb814d9d1056859cc11da00986bd18a384479352beb614fca9b8aa032` |

## 2. Counts

| Class | Count |
|---|---:|
| Identity files | 4 |
| Config specs | 1 |
| Reference docs | 1 |
| Cron specs | 1 |
| Plugin files | 4 |
| Custom skills | 16 |
| Generated artifacts promoted (primer seed) | 1 |
| Already in place, verified identical | 1 (`gen_drive_map.py`) |
| **Total files under this manifest** | **29** |

### Skill count — correcting Vulcan's audit

Vulcan's audit §7 states 15 custom skills / 32 total. That count omits **`weakness-derivation`**,
which is present in `drafts/skills/`, present in the `palladia` registry row, and is the skill
that filters `Activity == "Taken"` before deriving anything. His §1C destination list is missing
it too.

**Authoritative count: 17 inherited + 16 custom = 33.** The registry row's own rationale text
said 32 while its `skills` field listed 16 custom; that internal inconsistency is corrected in
the same pass as this promotion.

## 3. Acceptance — promotion is NOT complete until this passes

Canonical promotion is complete only when a fresh olympus1 sync receives these exact
hashes. Obsidian Sync pushes from the Mac while Obsidian is open on that vault, so the
chain is:

1. **Daniel:** open Obsidian on the Mac, on the PallaDrive vault, and let it push.
2. **olympus1:** pull, then verify.

```bash
cd /home/daniel/obsidian-vaults/palladrive
ob sync --path /home/daniel/obsidian-vaults/palladrive
```

Then re-hash and diff against this table:

```bash
cd /home/daniel/obsidian-vaults/palladrive
find _system-files/canonical _system-files/primer _system-files/scripts \
     -type f \( -name '*.md' -o -name '*.yaml' -o -name '*.py' \) \
  | sort | xargs sha256sum
```

Any row whose hash differs, or whose file is absent, means the promotion has not landed.
**Do not start the rehabilitation runbook against a partial canonical tree** — a half-synced
canonical is exactly how the runtime ends up in a state nobody reviewed.

## 4. Credential hygiene

The promoted tree was scanned for credential-shaped values before this manifest was
written: API-key prefixes, bearer tokens, private-key headers, and `*_KEY|TOKEN|SECRET|
PASSWORD = <value>` assignments. **Result: clean.** `auth.json` and `.env` are `no-ship`
and never enter PallaDrive — the drive replicates to two cloud services, so a secret
written here is a secret in both. `granola_api` is pasted by Daniel through the Obsidian
plugin UI and is never written by an agent.

## 5. Addendum — the runbook itself

Added after the 29-row table so the count above stays stable. The rehabilitation
runbook is an **operating** document for olympus1, not a Nova Caelum build record, so
it ships here rather than staying in the workspace — Vulcan executes on the host and
should not need a cross-vault hop to read it. It contains no credential material.

| Workspace source | PallaDrive destination | sha256 |
|---|---|---|
| `Rehabilitation_Palladia_ChiefPM_2026-08-29.md` | `_system-files/canonical/RUNBOOK-rehabilitation.md` | `52b65996baab18d63391017872aed84043f4f17939acf023f066212a33c4173b` |

The other 14 build-record documents (Installer, ComponentManifest, DependencyRegister,
FixRegister, SkillAudit, CronAudit, CasebookReview, PallaDriveFolders, V2_Upgrades,
FirstLaunchChecklist, GapReport, ContentProposal, MemoryAndWorklog, and Vulcan's audit)
stay in the Nova Caelum workspace. They are about building the product, not part of it.
