#!/usr/bin/env python3
"""Behavior tests for home/.local/bin/fleet-run against a stub `tailscale`.

The stub plays the remote: like sshd it joins the command words with spaces and
hands them to the login shell's -c (sh, and fish when installed, since the
fleet's login shell is fish). The remote command is a script that prints its
argv as JSON, so the tests compare what arrived with what was sent.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
FLEET_RUN = os.path.join(ROOT, "home", ".local", "bin", "fleet-run")
AGENT_GUARD = os.path.join(ROOT, "home", ".claude", "hooks", "agent-guard")

STUB = """#!/bin/sh
# tailscale ssh USER@HOST WORDS...: record the destination, run WORDS remotely.
shift
printf '%s' "$1" > "$STUB_DIR/destination"
shift
exec "$REMOTE_SHELL" -c "$*"
"""
ARGV = """#!/usr/bin/env python3
import json, sys
print(json.dumps(sys.argv[1:]))
"""
# Stands in for the remote agent-wait: --start prints a PID, --pid exits $WAIT_EXIT.
FAKE_AGENT_WAIT = """#!/bin/sh
case " $* " in
  *" --start "*) echo 4242 ;;
  *) exit "${WAIT_EXIT:-0}" ;;
esac
"""

TRICKY = ["a b", "it's", '"double"', "$HOME `id` $(id)", "x;y|z&", "", "back\\slash",
          "new\nline", "*", "-n", "--", "tab\there", "ünï", "{a,b}", "~", "#hash", "'"]


def write_exe(path, text):
    with open(path, "w") as f:
        f.write(text)
    os.chmod(path, 0o755)


class FleetRunTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        bin_dir = os.path.join(self.tmp, "bin")
        os.mkdir(bin_dir)
        write_exe(os.path.join(bin_dir, "tailscale"), STUB)
        write_exe(os.path.join(bin_dir, "argv"), ARGV)
        write_exe(os.path.join(bin_dir, "agent-wait"), FAKE_AGENT_WAIT)
        home = os.path.join(self.tmp, "home")
        os.mkdir(home)
        # The remote's `bash -l` reads the stub home's (empty) profile, and
        # /etc/profile keeps the inherited PATH, so the stubs stay reachable.
        self.env = dict(os.environ, PATH=bin_dir + ":" + os.environ["PATH"], HOME=home,
                        STUB_DIR=self.tmp, XDG_STATE_HOME=os.path.join(self.tmp, "state"),
                        REMOTE_SHELL="sh", USER="tester")
        self.env.pop("T3CODE_THREAD_ID", None)
        self.env.pop("FLEET_USER", None)

    def run_fleet(self, *argv, **env):
        return subprocess.run([FLEET_RUN, *argv], env=dict(self.env, **env),
                              capture_output=True, text=True, timeout=30)

    def shells(self):
        return ["sh"] + (["fish"] if shutil.which("fish") else [])

    def test_arguments_arrive_exactly(self):
        for shell in self.shells():
            with self.subTest(remote_shell=shell):
                result = self.run_fleet("box", "--", "argv", *TRICKY, REMOTE_SHELL=shell)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout), TRICKY)

    def test_remote_exit_status_is_returned(self):
        self.assertEqual(self.run_fleet("box", "--", "sh", "-c", "exit 7").returncode, 7)

    def test_user_defaults_and_overrides(self):
        def destination(*argv, **env):
            self.assertEqual(self.run_fleet(*argv, "--", "true", **env).returncode, 0)
            with open(os.path.join(self.tmp, "destination")) as f:
                return f.read()
        self.assertEqual(destination("box"), "tester@box")
        self.assertEqual(destination("box", FLEET_USER="ops"), "ops@box")
        self.assertEqual(destination("root@box"), "root@box")

    def test_remote_job_blocks_stop_until_waited(self):
        thread = {"T3CODE_THREAD_ID": "thread:delegated-task:fleet"}

        def stop_blocked():
            result = subprocess.run([AGENT_GUARD, "stop"], input="{}", capture_output=True,
                                    text=True, env=dict(self.env, **thread), timeout=30)
            return bool(result.stdout.strip()) and json.loads(result.stdout)["decision"] == "block"

        started = self.run_fleet("box", "--", "agent-wait", "--start", "--log", "/l og",
                                 "--", "make", "x", **thread)
        self.assertEqual(started.stdout.strip(), "4242")
        self.assertTrue(stop_blocked())
        self.assertEqual(self.run_fleet("box", "--", "agent-wait", "--pid", "4242", WAIT_EXIT="124",
                                        **thread).returncode, 124)
        self.assertTrue(stop_blocked(), "a wait that returned 124 lifted the block")
        self.assertEqual(self.run_fleet("box", "--", "agent-wait", "--pid", "4242", WAIT_EXIT="3",
                                        **thread).returncode, 3)
        self.assertFalse(stop_blocked(), "a finished wait left the block")

    def test_jobs_outside_t3_are_not_recorded(self):
        self.run_fleet("box", "--", "agent-wait", "--start", "--log", "l", "--", "true")
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "state", "agent-jobs")))


if __name__ == "__main__":
    unittest.main(verbosity=1, argv=[sys.argv[0]])
