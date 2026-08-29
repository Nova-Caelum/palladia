# Self-management reference

> Read the relevant section **before** you change your own configuration, not after.
> Every procedure here ends in a verification step. A change you have not read back is a change you have not made.

You have no engineer. Nobody is monitoring whether you started this morning. Every procedure below is written on that assumption.

---

## 0. Know where you live

Your configuration is a directory of your own. The installation also has a **root** directory with the identical file layout — same `config.yaml`, same `SOUL.md`, same `memories/`, same `.env`. That root is **the default agent's** configuration, not yours.

This is the single most dangerous fact about your environment, because nothing warns you. A write to the wrong one succeeds, reports success, and changes a different agent.

**Before any configuration write:**

```
1. Print the full absolute path you are about to write to.
2. Confirm it contains your profile name.
3. Write.
4. Read back from that same explicit path — not from a relative path, not from
   whatever the tool defaults to.
```

If a management UI offers to edit "the default profile," that is not you. Decline and edit your own path directly.

---

## 1. Before ANY configuration change

```bash
cp <your-config.yaml> <your-config.yaml>.bak-$(date +%Y%m%d-%H%M)
```

Make the change. Then:

```bash
python3 -c "import yaml,sys; yaml.safe_load(open('<your-config.yaml>')); print('parses OK')"
```

If it does not parse, restore the backup immediately. Do not attempt a second edit on top of a broken file.

**Why:** an unparseable configuration means you do not start. You cannot repair yourself from inside a process that will not boot, and there is no one to do it for you.

---

## 2. Adding an MCP connector

A connector adds a capability (a service, a data source). Adding one badly is the most common way agents break themselves.

1. **Check whether you already have it natively.** Many capabilities — web search, browsing, file handling, scheduling, transcription — are built in. Adding a connector for something you already have doubles the surface and gives you two ways to do one thing. Ask before assuming you need it.
2. **Credentials go in the secret store, referenced by name.** Never write a key value into configuration, and never use environment-variable placeholder syntax in a secret field — it is not reliably populated depending on how you were launched, and the failure is silent and intermittent, which is the worst kind.
3. **Pin the command to a full absolute path.** A bare command name resolves against a login shell's search path that your process may not share.
4. **Back up, add, parse, restart, then test.** In that order. Confirm the connector actually answers a call — presence in a list is not proof it works.
5. **If it fails twice, stop and report.** Do not iterate on a live configuration. Repeated fix-on-fix is how a small breakage becomes an unrecoverable one.

---

## 3. Installing a skill

1. Place the skill in your own skills directory. Do not hand-copy it into an unrelated location.
2. **Restart the gateway.** The loader caches per session; the skill is not live until you do.
3. Verify it appears in your skill list *and* that its trigger conditions actually fire.

**Never install a skill by cloning another agent's whole skill tree.** You will inherit everything it has, including capabilities you should not have and an identity that is not yours.

---

## 4. Changing your model

1. Confirm the provider you are switching to has a credential entry available to *your* profile. A configuration that names a provider you cannot authenticate against will silently fall through to a different one — often a more expensive one — and report success either way.
2. Model names differ by provider. The same model may need a prefix under one provider and a bare name under another. Switching provider without adjusting the name breaks resolution quietly.
3. Change, parse, restart, then send one message and confirm the reply came from the model you expect.

---

## 5. Scheduling a task

A scheduled job runs unattended, so every weakness in its instructions compounds silently.

- **Say what silence looks like.** Define the exact output when there is nothing to report, or the job will invent something to say every run.
- **Ban self-commentary explicitly.** Without it, jobs drift toward reporting on themselves — *"checked successfully, nothing new"* — instead of delivering the thing they exist to deliver.
- **Give it a stable dedupe key** if it discovers things: an identifier that does not change. Keying on free text produces duplicates that look like new findings.
- **Pin the model.** Unpinned jobs get dropped when defaults move, and the failure is invisible.
- **Check whether the job feeds its own prior output back to itself.** If it does, rewriting its instructions will not change its behavior — the old output outranks the new instruction. Change the input configuration, not just the prompt.
- **Judge health by what it delivered**, never by whether the process exited cleanly. A job can report success while producing nothing of value.

---

## 6. Editing your own memory

Your memory files are small and hard-capped, and they are frozen into your context when a session starts — a mid-session write is durable on disk but does not change your current context.

- When the file is full, an addition alone is rejected. Issue **one** batched change that removes or shortens stale entries *and* adds the new one together; the limit is checked on the final result.
- Memory holds stable facts and pointers. Progress, task state, and completed work belong in the drive, not here.
- The locked block at the top of the user file is never edited, compressed, or reformatted.

---

## 7. Hooks fail open

If a hook raises an exception, it is logged and skipped. Execution continues as though the hook did not exist.

The consequence: **a hook that protects you cannot rely on running.** If you write one whose job is to prevent something dangerous, wrap its whole body so that any error results in refusing rather than allowing. Otherwise the protection is silent and imaginary, and you will have no way to distinguish "the guard held" from "the guard died."

---

## 8. When to stop and ask

- The same change has failed twice.
- A step wants you to paste a credential somewhere.
- You would be deleting or overwriting something you did not create.
- A path looks right but you have not confirmed it is yours.
- The request would connect you to an external service, spend money, or send something outward.
- You are about to say "this should work."

Stopping to ask costs a minute. A configuration you cannot boot into costs the user their week — and during interview season, that is not a recoverable cost.
