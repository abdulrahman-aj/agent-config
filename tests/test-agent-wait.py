#!/usr/bin/env python3
"""Behavior tests for home/.local/bin/agent-wait: real processes, exit codes only."""

import os
import subprocess
import sys
import tempfile
import unittest

AGENT_WAIT = os.path.join(os.path.dirname(__file__), "..", "home", ".local", "bin", "agent-wait")
EXITED, BAD_INPUT, STALLED, STILL_RUNNING = 0, 2, 3, 124

# Appends a line to the log every 0.2 s for the given number of seconds.
WRITER = """
import sys, time
end = time.monotonic() + float(sys.argv[2])
while time.monotonic() < end:
    with open(sys.argv[1], "a") as f:
        f.write("progress\\n")
    time.sleep(0.2)
"""


class AgentWaitTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.log = os.path.join(self.tmp.name, "job.log")
        open(self.log, "w").close()
        self.jobs = []

    def tearDown(self):
        for job in self.jobs:
            job.kill()
            job.wait()
        self.tmp.cleanup()

    def start(self, argv):
        job = subprocess.Popen(argv)
        self.jobs.append(job)
        return job

    def writer(self, seconds):
        return self.start([sys.executable, "-c", WRITER, self.log, str(seconds)])

    def wait(self, *args):
        result = subprocess.run([sys.executable, AGENT_WAIT, *args],
                                capture_output=True, timeout=60)
        return result.returncode

    def test_returns_exited_when_the_job_ends(self):
        # The job stays an unreaped child of this test, so it ends as a zombie.
        job = self.writer(2)
        self.assertEqual(self.wait("--pid", str(job.pid), "--log", self.log), EXITED)

    def test_returns_stalled_when_the_log_stops_changing(self):
        job = self.start(["sleep", "60"])
        code = self.wait("--pid", str(job.pid), "--log", self.log, "--stall-minutes", "0.03")
        self.assertEqual(code, STALLED)

    def test_returns_still_running_while_the_log_grows(self):
        job = self.writer(60)
        code = self.wait("--pid", str(job.pid), "--log", self.log,
                         "--stall-minutes", "0.05", "--max-seconds", "4")
        self.assertEqual(code, STILL_RUNNING)

    def test_returns_still_running_without_a_log(self):
        job = self.start(["sleep", "60"])
        self.assertEqual(self.wait("--pid", str(job.pid), "--max-seconds", "2"), STILL_RUNNING)

    def test_rejects_a_missing_process(self):
        job = subprocess.Popen(["true"])
        job.wait()
        self.assertEqual(self.wait("--pid", str(job.pid)), BAD_INPUT)

    def test_rejects_a_missing_log(self):
        job = self.start(["sleep", "60"])
        missing = os.path.join(self.tmp.name, "missing.log")
        self.assertEqual(self.wait("--pid", str(job.pid), "--log", missing), BAD_INPUT)


if __name__ == "__main__":
    unittest.main()
