#!/usr/bin/env python3
"""Behavior tests for home/.local/bin/agent-wait: real processes, exit codes only."""

import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest

AGENT_WAIT = os.path.join(os.path.dirname(__file__), "..", "home", ".local", "bin", "agent-wait")
EXITED, BAD_INPUT, STALLED, JOB_FAILED, STILL_RUNNING = 0, 2, 3, 4, 124

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
        self.detached = []

    def tearDown(self):
        for job in self.jobs:
            job.kill()
            job.wait()
        # The supervisor leads its job's process group; kill both.
        for pid in self.detached:
            try:
                os.killpg(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
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

    def launch(self, *command):
        """Start a job with --start from its own process group, then kill that group.

        Codex kills the calling shell's process group when a tool call returns,
        so the job must survive this.
        """
        launcher = subprocess.Popen([sys.executable, AGENT_WAIT, "--start", "--log", self.log,
                                     "--", *command],
                                    stdout=subprocess.PIPE, start_new_session=True)
        out, _ = launcher.communicate(timeout=30)
        self.assertEqual(launcher.returncode, EXITED)
        pid = int(out)
        self.detached.append(pid)
        try:
            os.killpg(launcher.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        return pid

    def wait_until_gone(self, pid):
        """Wait until pid has exited, counting a zombie a slow subreaper hasn't reaped."""
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            try:
                with open(f"/proc/{pid}/stat") as f:
                    if f.read().rsplit(")", 1)[1].split()[0] in ("Z", "X"):
                        return
            except FileNotFoundError:
                return
            time.sleep(0.1)
        self.fail(f"pid {pid} still running")

    def test_a_killed_supervisor_never_reports_success(self):
        pid = self.launch("sleep", "60")
        os.kill(pid, signal.SIGKILL)
        self.wait_until_gone(pid)
        self.assertEqual(self.wait("--pid", str(pid), "--log", self.log), JOB_FAILED)

    def test_a_malformed_status_never_reports_success(self):
        pid = self.launch("true")
        self.wait_until_gone(pid)
        for content in [b"--1", "²".encode(), b"\xff"]:
            with self.subTest(content=content):
                with open(self.log + ".exit", "wb") as f:
                    f.write(content)
                self.assertEqual(self.wait("--pid", str(pid), "--log", self.log), JOB_FAILED)

    def test_killing_the_process_group_gives_failed(self):
        pid = self.launch("sleep", "60")
        os.killpg(pid, signal.SIGTERM)
        self.assertEqual(self.wait("--pid", str(pid), "--log", self.log,
                                   "--max-seconds", "10"), JOB_FAILED)

    def test_start_rejects_an_unwritable_log_directory(self):
        directory = os.path.join(self.tmp.name, "locked")
        os.mkdir(directory)
        log = os.path.join(directory, "job.log")
        open(log, "w").close()
        os.chmod(directory, 0o500)
        try:
            result = subprocess.run([sys.executable, AGENT_WAIT, "--start", "--log", log,
                                     "--", "true"], capture_output=True, timeout=10)
        finally:
            os.chmod(directory, 0o700)
        self.assertEqual(result.returncode, BAD_INPUT)

    def test_started_job_survives_its_launcher(self):
        pid = self.launch("sleep", "60")
        self.assertEqual(self.wait("--pid", str(pid), "--max-seconds", "2"), STILL_RUNNING)

    def test_started_job_that_succeeds_returns_exited(self):
        pid = self.launch("sh", "-c", "echo started; sleep 2")
        self.assertEqual(self.wait("--pid", str(pid), "--log", self.log), EXITED)

    def test_reports_a_failed_job_once_it_ends(self):
        pid = self.launch("sh", "-c", "sleep 3; exit 42")
        # No result while it runs, then the job's failure once it ends.
        self.assertEqual(self.wait("--pid", str(pid), "--log", self.log, "--max-seconds", "0"),
                         STILL_RUNNING)
        self.assertEqual(self.wait("--pid", str(pid), "--log", self.log), JOB_FAILED)

    def test_reports_the_status_of_a_job_that_ended_before_the_wait(self):
        pid = self.launch("sh", "-c", "exit 42")
        self.wait_until_gone(pid)
        self.assertEqual(self.wait("--pid", str(pid), "--log", self.log), JOB_FAILED)

    def test_start_rejects_a_log_that_is_not_a_regular_file(self):
        fifo = os.path.join(self.tmp.name, "fifo")
        os.mkfifo(fifo)
        result = subprocess.run([sys.executable, AGENT_WAIT, "--start", "--log", fifo,
                                 "--", "true"], capture_output=True, timeout=10)
        self.assertEqual(result.returncode, BAD_INPUT)

    def test_a_missing_command_ends_as_failed(self):
        pid = self.launch("no-such-command-agent-wait")
        self.assertEqual(self.wait("--pid", str(pid), "--log", self.log), JOB_FAILED)

    def test_returns_exited_when_the_job_ends(self):
        # The job stays an unreaped child of this test, so it ends as a zombie.
        job = self.writer(3)
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

    def test_a_log_deleted_mid_wait_counts_as_no_progress(self):
        job = self.start(["sleep", "60"])
        threading.Timer(1, os.remove, [self.log]).start()
        code = self.wait("--pid", str(job.pid), "--log", self.log, "--stall-minutes", "0.05")
        self.assertEqual(code, STALLED)

    def test_rejects_unbounded_or_negative_durations(self):
        job = self.start(["sleep", "60"])
        for flag, value in [("--max-seconds", "inf"), ("--max-seconds", "nan"),
                            ("--max-seconds", "-1"), ("--stall-minutes", "nan")]:
            with self.subTest(flag=flag, value=value):
                self.assertEqual(self.wait("--pid", str(job.pid), flag, value), BAD_INPUT)

    def test_rejects_a_log_that_is_not_a_regular_file(self):
        job = self.start(["sleep", "60"])
        fifo = os.path.join(self.tmp.name, "fifo")
        os.mkfifo(fifo)
        code = self.wait("--pid", str(job.pid), "--log", fifo, "--max-seconds", "0")
        self.assertEqual(code, BAD_INPUT)

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
