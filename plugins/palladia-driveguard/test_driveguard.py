"""Tests for palladia-driveguard. Run: python3 test_driveguard.py

Every test in the Bypasses class corresponds to a defect that was CONFIRMED
LIVE on 2026-08-31 by an adversarial audit, after an earlier 31-test suite
passed through all of them. They are regression locks, not scaffolding.
"""
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parent / "__init__.py"


def _load(vault, bridge, enforce="1"):
    os.environ["PALLADRIVE_PATH"] = str(vault)
    os.environ["DRIVEGUARD_BRIDGE_DIR"] = str(bridge)
    os.environ["DRIVEGUARD_ENFORCE"] = enforce
    sys.modules.pop("dg", None)
    spec = importlib.util.spec_from_file_location("dg", SRC)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["dg"] = mod
    spec.loader.exec_module(mod)
    mod._roots_ready()
    return mod


class Base(unittest.TestCase):
    SID = "sess1"

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.vault = self.root / "PALLAdrive"
        self.bridge = self.root / "bridge"
        for d in ("_meta", "_system-files/plugin_library", "_wiki",
                  "casing/session_notes", "casing/individual_cases", "_inbox"):
            (self.vault / d).mkdir(parents=True, exist_ok=True)
        (self.vault / "_meta/DRIVE-MAP.md").write_text("# map\n")
        (self.vault / "_wiki/weakness-ledger.md").write_text("x\n")
        (self.vault / "casing/session_notes/note.md").write_text("x\n")
        self.bridge.mkdir(parents=True, exist_ok=True)
        self.dg = _load(self.vault, self.bridge)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _epoch(self, n):
        (self.bridge / f"epoch-{self.SID}.json").write_text(json.dumps({"bridge_epoch": n}))

    def _arm(self, n=1):
        self._epoch(n)
        self.dg._post_tool_call(tool_name="read_file",
                                args={"path": str(self.vault / "_meta/DRIVE-MAP.md")},
                                session_id=self.SID)

    def _w(self, rel, sid=None):
        return self.dg._pre_tool_call(
            tool_name="write_file",
            args={"path": str(self.vault / rel), "content": "x"},
            session_id=sid or self.SID)

    def _t(self, cmd, sid=None):
        return self.dg._pre_tool_call(tool_name="terminal", args={"command": cmd},
                                      session_id=sid or self.SID)

    def _act(self, d):
        return (d or {}).get("action", "ALLOW")


class RootDiscovery(Base):
    """The vault moved 2026-08-31 and the guard went silently inert."""

    def _unresolvable(self):
        """Simulate a host where nothing resolves: no marker anywhere.

        The shipped candidate list contains the REAL Mac drive, so it must be
        cleared or the fallback correctly finds it -- which is the behaviour we
        want in production and the thing that makes this test need a stub.
        """
        dg = _load(self.root / "nonexistent", self.bridge)
        dg._CFG["vault_candidates"] = [str(self.root / "also-gone")]
        dg._VAULT = None
        dg._resolve_root()
        return dg

    def test_marker_verified_root_is_required(self):
        self.assertIsNone(self._unresolvable()._VAULT,
                          "a root without the marker must not be accepted")

    def test_unresolved_root_blocks_writes_loudly(self):
        d = self._unresolvable()._pre_tool_call(
            tool_name="write_file", args={"path": "/anywhere/x.md", "content": "x"},
            session_id=self.SID)
        self.assertEqual(self._act(d), "block", "must refuse, not skip silently")
        self.assertIn("configuration error", d["message"])

    def test_env_path_without_marker_falls_through_to_real_drive(self):
        """The 2026-08-31 failure, inverted: a wrong root must not win."""
        dg = _load(self.root / "nonexistent", self.bridge)
        dg._CFG["vault_candidates"] = [str(self.vault)]
        dg._VAULT = None
        dg._resolve_root()
        self.assertEqual(dg._VAULT, Path(os.path.realpath(str(self.vault))))

    def test_falls_through_stale_candidate_to_a_real_one(self):
        os.environ.pop("PALLADRIVE_PATH", None)
        sys.modules.pop("dg", None)
        spec = importlib.util.spec_from_file_location("dg", SRC)
        dg = importlib.util.module_from_spec(spec)
        sys.modules["dg"] = dg
        spec.loader.exec_module(dg)
        dg._CFG["vault_candidates"] = [str(self.root / "gone"), str(self.vault)]
        dg._resolve_root()
        self.assertEqual(dg._VAULT, Path(os.path.realpath(str(self.vault))))


class Bypasses(Base):
    """Each confirmed live 2026-08-31."""

    def test_escaped_symlink_blocked_before_zone_classification(self):
        outside = self.root / "outside"
        outside.mkdir()
        os.symlink(str(outside), str(self.vault / "_system-files" / "escape"))
        self._arm()
        d = self._w("_system-files/escape/leak.md")
        self.assertEqual(self._act(d), "block")
        self.assertIn("leaves the vault", d["message"])

    def test_case_variant_ancestor_still_guarded(self):
        self._arm()
        vc = str(self.vault).replace("PALLAdrive", "PALLADRIVE")
        if not os.path.isdir(vc):
            self.skipTest("case-sensitive volume")
        d = self.dg._pre_tool_call(tool_name="write_file",
                                   args={"path": vc + "/_system-files/x.md", "content": "x"},
                                   session_id=self.SID)
        self.assertEqual(self._act(d), "block")

    def test_case_variant_zone_still_denied(self):
        self._arm()
        if not self.dg._CASE_INSENSITIVE:
            self.skipTest("case-sensitive volume")
        self.assertEqual(self._act(self._w("_System-Files/x.md")), "block")

    def test_gate_arms_on_case_variant_drivemap_read(self):
        """FP1: the wedge that would get this plugin switched off."""
        self._epoch(1)
        if not self.dg._CASE_INSENSITIVE:
            self.skipTest("case-sensitive volume")
        self.dg._post_tool_call(tool_name="read_file",
                                args={"path": str(self.vault / "_meta/drive-map.md")},
                                session_id=self.SID)
        self.assertIn(self.SID, self.dg._READ_GEN)

    def test_negation_does_not_unlock_deny_zone(self):
        self.dg._pre_llm_call(session_id="neg",
                              user_message="whatever you do, don't modify _system-files")
        self.assertNotIn("neg", self.dg._EXPLICIT_SYSTEM_WRITE)

    def test_unlock_is_one_shot(self):
        self._arm()
        self.dg._pre_llm_call(session_id=self.SID,
                              user_message="please update _system-files config")
        self.assertIsNone(self._w("_system-files/one.md"))
        self.assertEqual(self._act(self._w("_system-files/two.md")), "block",
                         "unlock must not persist for the whole session")

    def test_echo_redirection_is_guarded(self):
        self._arm()
        self.assertEqual(self._act(self._t(f"echo x > {self.vault}/_system-files/c.yaml")),
                         "block", "redirection mutates with no mutation verb")

    def test_indirection_wrappers_are_seen_through(self):
        self._arm()
        for cmd in (f"sudo mv {self.vault}/_wiki/a.md {self.vault}/_system-files/b.md",
                    f"env mv {self.vault}/_wiki/a.md {self.vault}/_system-files/b.md",
                    f"nohup mv {self.vault}/_wiki/a.md {self.vault}/_system-files/b.md"):
            self.assertEqual(self._act(self._t(cmd)), "block", cmd)

    def test_unbalanced_quotes_fail_closed(self):
        self._arm()
        cmd = 'mv "unclosed ' + str(self.vault) + '/_system-files/x'
        self.assertEqual(self._act(self._t(cmd)), "block",
                         "a failed parse is not an empty path list")


class ReadGate(Base):
    def test_blocks_when_no_bridge(self):
        self.assertIn("no compression epoch", self._w("casing/new.md")["message"])

    def test_blocks_when_never_read(self):
        self._epoch(1)
        self.assertIn("not read the drive map", self._w("casing/new.md")["message"])

    def test_allows_after_read(self):
        self._arm()
        self.assertIsNone(self._w("casing/new.md"))

    def test_blocks_again_after_compression(self):
        self._arm()
        self.assertIsNone(self._w("casing/a.md"))
        self._epoch(2)
        self.assertIn("was compressed", self._w("casing/b.md")["message"])

    def test_primer_can_arm_the_gate(self):
        """Without this she is blocked on her first write of every session."""
        self._epoch(1)
        self.assertTrue(self.dg.arm_gate(self.SID))
        self.assertIsNone(self._w("casing/new.md"))

    def test_arm_gate_refuses_without_bridge(self):
        self.assertFalse(self.dg.arm_gate(self.SID))


class ZonePolicy(Base):
    def test_denies_system_files(self):
        self._arm()
        self.assertIn("canonical runtime", self._w("_system-files/config/x.yaml")["message"])

    def test_wiki_and_casing_allowed(self):
        self._arm()
        self.assertIsNone(self._w("_wiki/newnote.md"))
        self.assertIsNone(self._w("casing/session_notes/another.md"))

    def test_outside_vault_ignored(self):
        self._arm()
        self.assertIsNone(self.dg._pre_tool_call(
            tool_name="write_file", args={"path": "/tmp/elsewhere.md", "content": "x"},
            session_id=self.SID))

    def test_corrupt_zones_still_denies_system_files(self):
        self.assertTrue(any(z.get("policy") == "deny"
                            for z in self.dg._DEFAULT_ZONES["zones"]),
                        "fallback config must keep the deny zone")


class DuplicateFolder(Base):
    def test_blocks_duplicate_folder_elsewhere(self):
        self._arm()
        d = self._w("_wiki/session_notes/new.md")
        self.assertEqual(self._act(d), "block")
        self.assertIn("casing/session_notes", d["message"])

    def test_blocks_novel_folder_with_missing_parent(self):
        self._arm()
        self.assertIn("does not exist", self._w("casing/brand_new/x.md")["message"])

    def test_existing_parent_allows(self):
        self._arm()
        self.assertIsNone(self._w("casing/session_notes/ok.md"))


class Fuzzy(Base):
    def test_modifies_to_single_fuzzy_match(self):
        self._arm()
        d = self.dg._pre_tool_call(
            tool_name="patch",
            args={"path": str(self.vault / "_wiki/Weakness_Ledger.MD"), "patch": "x"},
            session_id=self.SID)
        self.assertEqual(self._act(d), "modify")
        self.assertTrue(d["args"]["path"].endswith("weakness-ledger.md"))

    def test_patch_skips_directory_checks(self):
        self._arm()
        self.assertIsNone(self.dg._pre_tool_call(
            tool_name="patch",
            args={"path": str(self.vault / "_wiki/session_notes/x.md"), "patch": "y"},
            session_id=self.SID), "patch cannot create a folder")


class Sweep(Base):
    def test_successful_mv_enqueues(self):
        self.dg._transform_terminal_output(
            command=f"mv {self.vault}/_wiki/a.md {self.vault}/casing/b.md",
            output="", returncode=0)
        q = (self.bridge / "sweep-queue.jsonl").read_text()
        self.assertIn("_wiki/a.md", q)

    def test_failed_mv_does_not_enqueue(self):
        self.dg._transform_terminal_output(
            command=f"mv {self.vault}/_wiki/a.md {self.vault}/casing/b.md",
            output="err", returncode=1)
        self.assertFalse((self.bridge / "sweep-queue.jsonl").exists())


class Secrets(Base):
    def test_credential_command_not_parsed_and_not_retained(self):
        self._arm()
        self._t("mv --token=sk-abcdef1234567890 /a /b")
        log = (self.bridge / "driveguard-audit.jsonl").read_text()
        self.assertIn('"verb": "redacted"', log)
        self.assertNotIn("sk-abcdef1234567890", log)

    def test_audit_never_holds_raw_command(self):
        self._arm()
        self._t(f"mv {self.vault}/_wiki/a.md {self.vault}/_wiki/b.md")
        self.assertNotIn("mv /", (self.bridge / "driveguard-audit.jsonl").read_text())


class Robustness(Base):
    def test_never_raises_on_garbage(self):
        for a in (None, {}, {"path": None}, {"path": ""}, {"path": 123}, "notadict"):
            self.dg._pre_tool_call(tool_name="write_file", args=a, session_id=self.SID)
            self.dg._post_tool_call(tool_name="write_file", args=a, session_id=self.SID)

    def test_deferred_wrapper_unwrapped(self):
        self._arm()
        d = self.dg._pre_tool_call(
            tool_name="tool_call",
            args={"name": "write_file",
                  "arguments": {"path": str(self.vault / "_system-files/x.md"), "content": "y"}},
            session_id=self.SID)
        self.assertEqual(self._act(d), "block")

    def test_observe_only_mode_applies_nothing(self):
        dg = _load(self.vault, self.bridge, enforce="0")
        self.assertIsNone(dg._pre_tool_call(
            tool_name="write_file",
            args={"path": str(self.vault / "_system-files/x.md"), "content": "y"},
            session_id=self.SID), "DRIVEGUARD_ENFORCE=0 must apply nothing")

    def test_prompt_section_within_budget(self):
        self.assertLessEqual(len(self.dg._PROMPT_SECTION), 1200)


if __name__ == "__main__":
    unittest.main(verbosity=1)
