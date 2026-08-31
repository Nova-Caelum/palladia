"""Tests for the palladia-primer first-turn context-injection hook.

Imports the plugin directly, following the agent-registry-guard precedent.
Covers: normal load, missing file, unreadable file, oversize truncation,
timestamp extraction, the first-turn gate, and the no-raise guarantee.

HOOK CONTRACT: pre_llm_call, NOT on_session_start. on_session_start returns are
ignored by Hermes (shipped-hook catalog, verified 2026-08-29). These tests pin the
corrected contract so a future 'simplification' back to on_session_start fails.
"""

import importlib.util
import os
import stat
import tempfile
import shutil
import sys
import pathlib
import unittest
from pathlib import Path

PLUGIN = Path(__file__).with_name("__init__.py")
spec = importlib.util.spec_from_file_location("palladia_primer", PLUGIN)
primer = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(primer)


class PrimerHookTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self._orig_root = primer._PALLADRIVE
        primer._PALLADRIVE = self.root
        self.path = self.root / primer._PRIMER_RELATIVE
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        primer._PALLADRIVE = self._orig_root
        # Restore perms so cleanup cannot fail on the unreadable-file test.
        if self.path.exists():
            self.path.chmod(stat.S_IRUSR | stat.S_IWUSR)
        self._tmp.cleanup()

    def _write(self, text):
        self.path.write_text(text, encoding="utf-8")

    # --- normal load --------------------------------------------------------

    def test_normal_load_includes_body_and_timestamp(self):
        self._write(
            "---\ngenerated_at: 2026-08-29T19:15:00Z\n---\n\n# Primer\n\nBCG New Jersey.\n"
        )
        out = primer._pre_llm_call()["context"]
        self.assertIn("BCG New Jersey.", out)
        self.assertIn("Generated at: 2026-08-29T19:15:00Z", out)
        self.assertIn(primer._HEADER, out)
        self.assertNotIn("COULD NOT BE", out)

    def test_missing_timestamp_is_flagged_stale_not_fatal(self):
        self._write("---\nschema_version: 1\n---\n\nbody text\n")
        out = primer._pre_llm_call()["context"]
        self.assertIn("UNKNOWN", out)
        self.assertIn("Treat as stale", out)
        self.assertIn("body text", out)

    def test_no_frontmatter_still_loads(self):
        self._write("# Primer\n\nno frontmatter here\n")
        out = primer._pre_llm_call()["context"]
        self.assertIn("no frontmatter here", out)
        self.assertIn("UNKNOWN", out)

    # --- missing file -------------------------------------------------------

    def test_missing_file_returns_loud_notice_and_does_not_raise(self):
        self.assertFalse(self.path.exists())
        out = primer._pre_llm_call()["context"]
        self.assertIn("PRIMER COULD NOT BE LOADED", out)
        self.assertIn("may be stale", out)
        self.assertIn("tell Daniel", out)

    def test_missing_directory_returns_notice_not_exception(self):
        primer._PALLADRIVE = self.root / "does" / "not" / "exist"
        out = primer._pre_llm_call()["context"]
        self.assertIn("PRIMER COULD NOT BE LOADED", out)

    # --- unreadable file ----------------------------------------------------

    @unittest.skipIf(os.geteuid() == 0, "root bypasses permission bits")
    def test_unreadable_file_returns_loud_notice(self):
        self._write("---\ngenerated_at: 2026-08-29T00:00:00Z\n---\nsecret-ish body\n")
        self.path.chmod(0)
        out = primer._pre_llm_call()["context"]
        self.assertIn("PRIMER COULD NOT BE READ", out)
        self.assertIn("PermissionError", out)
        self.assertNotIn("secret-ish body", out)

    def test_directory_in_place_of_file_is_handled(self):
        # is_file() is False for a directory -> missing notice, no traceback.
        if self.path.exists():
            self.path.unlink()
        self.path.mkdir(parents=True, exist_ok=True)
        out = primer._pre_llm_call()["context"]
        self.assertIn("PRIMER COULD NOT BE LOADED", out)

    # --- truncation ---------------------------------------------------------

    def test_oversize_is_truncated_with_explicit_marker(self):
        self._write("---\ngenerated_at: 2026-08-29T00:00:00Z\n---\n" + ("x" * 20000))
        out = primer._pre_llm_call()["context"]
        self.assertIn("PRIMER TRUNCATED", out)
        # Body cap respected; header/stamp lines sit outside the capped body.
        self.assertLess(len(out), primer._MAX_CHARS + 500)

    def test_under_cap_is_not_truncated(self):
        self._write("---\ngenerated_at: 2026-08-29T00:00:00Z\n---\nshort body\n")
        out = primer._pre_llm_call()["context"]
        self.assertNotIn("PRIMER TRUNCATED", out)

    # --- contract -----------------------------------------------------------

    def test_callback_accepts_arbitrary_kwargs(self):
        self._write("---\ngenerated_at: 2026-08-29T00:00:00Z\n---\nbody\n")
        out = primer._pre_llm_call(
            session_id="s1",
            user_message="hi",
            conversation_history=[],
            is_first_turn=True,
            model="gpt-5.6-terra",
            platform="discord",
            unexpected_future_arg=1,
        )
        self.assertIn("context", out)

    def test_register_wires_pre_llm_call_not_on_session_start(self):
        """Pins the corrected contract. on_session_start returns are IGNORED by
        Hermes -- registering there is the silent-never-injects bug."""
        registered = []

        class FakeCtx:
            def register_hook(self, event, cb):
                registered.append((event, cb))

        primer.register(FakeCtx())
        self.assertEqual(len(registered), 1)
        self.assertEqual(registered[0][0], "pre_llm_call")
        self.assertNotEqual(registered[0][0], "on_session_start")

    # --- first-turn gate ----------------------------------------------------

    def test_later_turns_inject_nothing(self):
        self._write("---\ngenerated_at: 2026-08-29T00:00:00Z\n---\nbody\n")
        self.assertIsNone(primer._pre_llm_call(is_first_turn=False))

    def test_first_turn_injects(self):
        self._write("---\ngenerated_at: 2026-08-29T00:00:00Z\n---\nbody\n")
        out = primer._pre_llm_call(is_first_turn=True)
        self.assertIn("context", out)
        self.assertIn("body", out["context"])

    def test_missing_is_first_turn_field_defaults_to_injecting(self):
        """Directional default: a renamed/dropped field must degrade to VISIBLE
        over-injection, never to silent never-injection."""
        self._write("---\ngenerated_at: 2026-08-29T00:00:00Z\n---\nbody\n")
        self.assertIsNotNone(primer._pre_llm_call(session_id="s1"))
        self.assertIsNotNone(primer._pre_llm_call(is_first_turn=None))

    def test_load_primer_never_raises(self):
        """The no-crash guarantee. A raising hook is logged and SKIPPED by Hermes,
        which makes failure invisible -- so this is the load-bearing test."""
        for setup in (
            lambda: None,
            lambda: self._write(""),
            lambda: self._write("---\n"),
            lambda: self._write("---\ngenerated_at:\n---\n"),
            lambda: self._write("\x00\xff binary-ish"),
        ):
            with self.subTest(setup=setup):
                if self.path.exists():
                    self.path.unlink()
                setup()
                try:
                    result = primer._load_primer()
                except Exception as exc:  # noqa: BLE001
                    self.fail(f"_load_primer raised {type(exc).__name__}")
                self.assertIsInstance(result, str)
                self.assertTrue(result)


class FirstTurnExtras(unittest.TestCase):
    """Drivemap digest, worklog tail, and driveguard gate-arming.

    Added 2026-08-31. Without the gate-arming, Palladia is blocked on her FIRST
    write of every session and told to read a map she was just handed.
    """

    def setUp(self):
        import json as _json
        self.root = pathlib.Path(tempfile.mkdtemp())
        self.vault = self.root / "PALLAdrive"
        self.bridge = self.root / "bridge"
        (self.vault / "_meta/worklog_entries").mkdir(parents=True)
        (self.vault / "_system-files/core_text").mkdir(parents=True)
        (self.vault / "_meta/DRIVE-MAP.md").write_text(
            "# map\n> **Generated:** 2026-08-31T00:00:00\n\n### `_meta/`\n\n### `casing/`\n")
        (self.vault / "_system-files/core_text/PRIMER.md").write_text("---\ngenerated_at: x\n---\nbody\n")
        for name, summ in (("2026-08-01-0900-a.md", "older entry"),
                           ("2026-08-02-0900-b.md", "middle entry"),
                           ("2026-08-03-0900-c.md", "newest entry")):
            (self.vault / "_meta/worklog_entries" / name).write_text(
                f'---\ncreated: 2026-08-0X\nsummary: "{summ}"\n---\nbody\n')
        self.bridge.mkdir()
        os.environ["PALLADRIVE_PATH"] = str(self.vault)
        os.environ["DRIVEGUARD_BRIDGE_DIR"] = str(self.bridge)
        sys.modules.pop("pr", None)
        spec = importlib.util.spec_from_file_location(
            "pr", pathlib.Path(__file__).resolve().parent / "__init__.py")
        self.pr = importlib.util.module_from_spec(spec)
        sys.modules["pr"] = self.pr
        spec.loader.exec_module(self.pr)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)
        os.environ.pop("PALLADRIVE_PATH", None)
        os.environ.pop("DRIVEGUARD_BRIDGE_DIR", None)

    def _inject(self, sid="s", first=True):
        out = self.pr._pre_llm_call(session_id=sid, user_message="hi", is_first_turn=first)
        return (out or {}).get("context", "") if out else None

    def test_marker_verified_root(self):
        self.assertEqual(self.pr._PALLADRIVE, self.vault)

    def test_injects_only_last_two_worklog_entries(self):
        ctx = self._inject()
        self.assertIn("newest entry", ctx)
        self.assertIn("middle entry", ctx)
        self.assertNotIn("older entry", ctx)

    def test_injects_drivemap_digest_not_whole_file(self):
        ctx = self._inject()
        self.assertIn("2026-08-31T00:00:00", ctx)
        self.assertIn("_meta/", ctx)
        self.assertIn("casing/", ctx)

    def test_arms_the_driveguard_gate(self):
        import json as _json
        (self.bridge / "epoch-s.json").write_text(_json.dumps({"bridge_epoch": 4}))
        self._inject()
        armed = self.bridge / "armed-s.json"
        self.assertTrue(armed.is_file())
        self.assertEqual(_json.loads(armed.read_text())["armed_at_epoch"], 4)

    def test_does_not_arm_without_an_epoch(self):
        self._inject()
        self.assertFalse((self.bridge / "armed-s.json").exists(),
                         "no epoch means the guard must stay fail-closed")

    def test_second_turn_injects_nothing(self):
        self.assertIsNone(self._inject(first=False))

    def test_missing_drivemap_is_loud_not_silent(self):
        (self.vault / "_meta/DRIVE-MAP.md").unlink()
        self.assertIn("MISSING", self._inject())


if __name__ == "__main__":
    unittest.main()
