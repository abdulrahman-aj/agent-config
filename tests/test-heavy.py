#!/usr/bin/env python3
"""Behavior tests for home/.local/bin/heavy: real processes and exit codes.

The remote path runs through tests/fake-ssh, which runs commands on this
machine with a separate home, so the copy, the remote script, copy-back and
remote interrupts are exercised without msi-dux.
"""

import os
import signal
import socket
import subprocess
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
HEAVY = os.path.join(HERE, "..", "home", ".local", "bin", "heavy")
FAKE_SSH = os.path.join(HERE, "fake-ssh")
FAILED = 255
SLOTS = 3 if socket.gethostname() == "msi-dux" else 2


def alive(pid):
    """True while pid runs; a zombie counts as gone."""
    try:
        with open(f"/proc/{pid}/stat") as f:
            return f.read().rpartition(")")[2].split()[0] not in ("Z", "X")
    except OSError:
        return False


class HeavyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = os.path.join(self.tmp.name, "local")
        self.remote_home = os.path.join(self.tmp.name, "remote")
        self.repo = os.path.join(self.home, "repo")
        self.remote_repo = os.path.join(self.remote_home, "repo")
        os.makedirs(self.repo)
        os.makedirs(self.remote_home)
        self.git("init", "-q")
        self.write("tracked.txt", "first\n")
        self.git("add", ".")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")
        self.env = {k: v for k, v in os.environ.items() if not k.startswith(("HEAVY_", "AGENT_HEAVY"))}
        self.env.update(HOME=self.home, HEAVY_LOCK_DIR=os.path.join(self.tmp.name, "locks"),
                        HEAVY_SSH=FAKE_SSH, HEAVY_FAKE_HOME=self.remote_home, HEAVY_WHERE="local")
        self.procs = []

    def tearDown(self):
        for proc in self.procs:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
        self.tmp.cleanup()

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True)

    def write(self, name, text, root=None):
        path = os.path.join(root or self.repo, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)

    def start(self, command, *flags, **env):
        proc = subprocess.Popen([HEAVY, *flags, "--", command], cwd=self.repo, env={**self.env, **env},
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.procs.append(proc)
        return proc

    def run_heavy(self, command, *flags, **env):
        return self.start(command, *flags, **env).wait(timeout=60)

    def wait_for(self, path, seconds=20):
        deadline = time.monotonic() + seconds
        while not os.path.exists(path):
            self.assertLess(time.monotonic(), deadline, f"{path} never appeared")
            time.sleep(0.05)

    def lines(self, name, root=None):
        try:
            with open(os.path.join(root or self.repo, name)) as f:
                return len(f.readlines())
        except FileNotFoundError:
            return 0

    # Local path

    def test_exit_status_passes_through_and_the_job_runs_once(self):
        for code in (0, 3, 75, 255):
            with self.subTest(code=code):
                os.makedirs(self.repo, exist_ok=True)
                count = f"runs-{code}"
                self.assertEqual(self.run_heavy(f"echo run >> {count}; exit {code}"), code)
                self.assertEqual(self.lines(count), 1)  # 75 isn't "slot busy": no rerun

    def test_a_job_past_the_cap_waits_for_a_slot(self):
        hold = "touch started-$N; while [ ! -e release ]; do sleep 0.05; done"
        holders = [self.start(hold.replace("$N", str(n))) for n in range(SLOTS)]
        for n in range(SLOTS):
            self.wait_for(os.path.join(self.repo, f"started-{n}"))
        extra = self.start("touch started-extra")
        time.sleep(1.5)
        self.assertFalse(os.path.exists(os.path.join(self.repo, "started-extra")))
        open(os.path.join(self.repo, "release"), "w").close()
        self.assertEqual([p.wait(timeout=30) for p in holders + [extra]], [0] * (SLOTS + 1))
        self.assertTrue(os.path.exists(os.path.join(self.repo, "started-extra")))

    def test_a_signal_kills_the_job_group_and_runs_cleanup(self):
        self.write(".heavy-cleanup", "touch cleaned\n")
        for signum in (signal.SIGTERM, signal.SIGINT):
            with self.subTest(signal=signum.name):
                for name in ("grandchild", "cleaned"):
                    if os.path.exists(os.path.join(self.repo, name)):
                        os.remove(os.path.join(self.repo, name))
                proc = self.start("sleep 300 & echo $! > grandchild; wait")
                self.wait_for(os.path.join(self.repo, "grandchild"))
                with open(os.path.join(self.repo, "grandchild")) as f:
                    pid = int(f.read())
                proc.send_signal(signum)
                self.assertEqual(proc.wait(timeout=30), 128 + signum)
                self.assertFalse(alive(pid))
                self.assertTrue(os.path.exists(os.path.join(self.repo, "cleaned")))

    def test_deny_refuses_a_local_run_unless_opted_in(self):
        self.assertEqual(self.run_heavy("touch ran", AGENT_HEAVY_JOBS="deny"), FAILED)
        self.assertFalse(os.path.exists(os.path.join(self.repo, "ran")))
        self.assertEqual(self.run_heavy("touch ran", "--local-ok", AGENT_HEAVY_JOBS="deny"), 0)
        self.assertTrue(os.path.exists(os.path.join(self.repo, "ran")))

    @unittest.skipIf(socket.gethostname() == "msi-dux", "msi-dux always runs locally")
    def test_a_silent_remote_falls_back_to_a_local_run(self):
        self.assertEqual(self.run_heavy("touch ran", HEAVY_WHERE="", HEAVY_SSH="false"), 0)
        self.assertTrue(os.path.exists(os.path.join(self.repo, "ran")))

    # Remote path, through fake-ssh

    def test_remote_copy_has_uncommitted_edits_minus_heavyignore(self):
        self.write("tracked.txt", "edited\n")
        self.write("untracked.txt", "new\n")
        self.write(".heavyignore", "skip/\n")
        self.write("skip/big", "x\n")
        check = "grep -q edited tracked.txt && test -e untracked.txt && test ! -e skip"
        self.assertEqual(self.run_heavy(check, HEAVY_WHERE="remote"), 0)

    def test_remote_exit_status_passes_through(self):
        for code in (0, 75, 255):
            with self.subTest(code=code):
                self.assertEqual(self.run_heavy(f"exit {code}", HEAVY_WHERE="remote"), code)

    def test_out_copies_back_what_the_job_made_or_updated(self):
        job = "mkdir -p build && touch build/made && echo more >> tracked.txt"
        rc = self.run_heavy(job, "--out", "build", "--out", "tracked.txt", "--out", "missing",
                            HEAVY_WHERE="remote")
        self.assertEqual(rc, 0)
        self.assertTrue(os.path.exists(os.path.join(self.repo, "build", "made")))
        self.assertEqual(self.lines("tracked.txt"), 2)

    def test_a_signal_stops_the_remote_job_group_and_runs_cleanup(self):
        self.write(".heavy-cleanup", "touch cleaned\n")
        proc = self.start("sleep 300 & echo $! > grandchild; wait", HEAVY_WHERE="remote")
        self.wait_for(os.path.join(self.remote_repo, "grandchild"))
        with open(os.path.join(self.remote_repo, "grandchild")) as f:
            pid = int(f.read())
        proc.send_signal(signal.SIGTERM)
        self.assertEqual(proc.wait(timeout=30), 128 + signal.SIGTERM)
        self.assertFalse(alive(pid))
        self.assertTrue(os.path.exists(os.path.join(self.remote_repo, "cleaned")))

    def test_remote_refuses_to_overwrite_a_directory_it_did_not_copy(self):
        self.write("precious", "keep\n", root=self.remote_repo)
        self.assertEqual(self.run_heavy("touch ran", HEAVY_WHERE="remote"), FAILED)
        self.assertTrue(os.path.exists(os.path.join(self.remote_repo, "precious")))
        self.assertFalse(os.path.exists(os.path.join(self.remote_repo, "ran")))


if __name__ == "__main__":
    unittest.main()
