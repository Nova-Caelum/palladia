"""Tests for driveguard-epoch. Run: python3 -m unittest discover -s . -p 'test_*.py'"""
import importlib.util
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path


def _load(bridge_dir):
    os.environ["DRIVEGUARD_BRIDGE_DIR"] = str(bridge_dir)
    spec = importlib.util.spec_from_file_location(
        "epoch_handler", Path(__file__).parent / "handler.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class EpochTests(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.h = _load(self.dir)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def _epoch(self, sid="s1"):
        p = self.dir / f"epoch-{sid}.json"
        return json.loads(p.read_text())["bridge_epoch"] if p.is_file() else None

    def test_session_start_seeds_one_not_zero(self):
        self.h.handle("session:start", {"session_id": "s1", "platform": "discord"})
        self.assertEqual(self._epoch(), 1,
                         "must seed at 1 so a stale read_generation of 0 cannot match")

    def test_compress_increments_monotonically(self):
        self.h.handle("session:start", {"session_id": "s1"})
        for expected in (2, 3, 4):
            self.h.handle("session:compress", {"session_id": "s1", "compression_count": 99})
            self.assertEqual(self._epoch(), expected)

    def test_ignores_hermes_compression_count_going_backwards(self):
        """Probe D2: Hermes' counter went 1 -> 2 -> 0. Ours must not follow."""
        self.h.handle("session:start", {"session_id": "s1"})
        for cc in (1, 2, 0):
            self.h.handle("session:compress", {"session_id": "s1", "compression_count": cc})
        self.assertEqual(self._epoch(), 4, "our epoch must be monotonic regardless")

    def test_survives_process_restart_by_reading_disk(self):
        """The load-bearing property: a fresh module must not reset the counter."""
        self.h.handle("session:start", {"session_id": "s1"})
        self.h.handle("session:compress", {"session_id": "s1"})
        self.assertEqual(self._epoch(), 2)
        fresh = _load(self.dir)          # simulate gateway restart
        fresh.handle("session:compress", {"session_id": "s1"})
        self.assertEqual(self._epoch(), 3, "in-memory counter would have reset to 1 here")

    def test_corrupt_file_does_not_authorise(self):
        (self.dir / "epoch-s1.json").write_text("{ this is not json")
        self.h.handle("session:compress", {"session_id": "s1"})
        self.assertEqual(self._epoch(), 1,
                         "corrupt reads as 0 -> writes 1 -> cannot match a held generation")

    def test_sessions_are_isolated(self):
        self.h.handle("session:start", {"session_id": "s1"})
        self.h.handle("session:start", {"session_id": "s2"})
        self.h.handle("session:compress", {"session_id": "s1"})
        self.assertEqual(self._epoch("s1"), 2)
        self.assertEqual(self._epoch("s2"), 1)

    def test_session_id_cannot_traverse(self):
        self.h.handle("session:start", {"session_id": "../../etc/passwd"})
        self.assertEqual(list(self.dir.glob("*.json")), [self.dir / "epoch-etcpasswd.json"])

    def test_never_raises_on_garbage(self):
        for bad in ({}, {"session_id": None}, {"session_id": ""}, {"session_id": 12345}):
            self.h.handle("session:compress", bad)   # must not raise

    def test_start_does_not_clobber_existing_epoch(self):
        self.h.handle("session:start", {"session_id": "s1"})
        self.h.handle("session:compress", {"session_id": "s1"})
        self.h.handle("session:start", {"session_id": "s1"})   # duplicate start
        self.assertEqual(self._epoch(), 2, "must not reset a live session to 1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
