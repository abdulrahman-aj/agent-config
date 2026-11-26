#!/usr/bin/env python3
"""Behavior tests for home/.local/bin/agent-wait: real processes, exit codes only."""

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest

AGENT_WAIT = os.path.join(os.path.dirname(__file__), "..", "home", ".local", "bin", "agent-wait")
EXITED, BAD_INPUT, STALLED, JOB_FAILED, STILL_RUNNING = 0, 2, 3, 4, 124

# Appends a line to stdout every 0.2 s for the given number of seconds.
WRITER = """
import sys, time
end = time.monotonic() + float(sys.argv[1])
while time.monotonic() < end:
    print("progress", flush=True)
    time.sleep(0.2)
"""


def has_systemd_user():
    if not shutil.which("systemd-run"):
        return False
    return subprocess.run(["systemd-run", "--user", "--scope", "--quiet", "true"],
                          capture_output=True).returncode == 0


def proc_alive(pid):
    try:
        with open(f"/proc/{pid}/stat") as f:
            return f.read().rsplit(")", 1)[1].split()[0] not in ("Z", "X")
    except OSError:
        return False


class AgentWaitTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.log = os.path.join(self.tmp.name, "job.log")
        self.jobs = []
        self.started_logs = []

    def tearDown(self):
        for log in self.started_logs:
            subprocess.run([sys.executable, AGENT_WAIT, "stop", log],
                           capture_output=True, timeout=30)
        for job in self.jobs:
            job.kill()
            job.wait()
        self.tmp.cleanup()

    def run_aw(self, *args, cwd=None, env=None):
        return subprocess.run([sys.executable, AGENT_WAIT, *args],
                              cwd=cwd, env=env, capture_output=True, text=True, timeout=60)

    def start_job(self, *command, log=None, cwd=None, env=None):
        """Start a job from its own process group, then kill that group.

        Simulates harnesses that kill the calling shell's process group when a
        tool call returns.
        """
        target = self.log if log is None else log
        launcher = subprocess.Popen(
            [sys.executable, AGENT_WAIT, "start", target, "--", *command],
            cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, start_new_session=True)
        out, err = launcher.communicate(timeout=30)
        self.assertEqual(launcher.returncode, EXITED, err)
        resolved = out.strip()
        self.started_logs.append(resolved)
        try:
            os.killpg(launcher.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        return resolved

    def read_job(self, log=None):
        with open((self.log if log is None else log) + ".job") as f:
            return json.load(f)

    def wait_until_gone(self, pid):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if not proc_alive(pid):
                return
            time.sleep(0.1)
        self.fail(f"pid {pid} still running")

    def test_succeeding_job_returns_exited(self):
        log = self.start_job("sh", "-c", "echo started; sleep 1")
        self.assertEqual(self.run_aw("wait", log).returncode, EXITED)

    def test_failing_job_returns_failed(self):
        log = self.start_job("sh", "-c", "sleep 2; exit 42")
        self.assertEqual(self.run_aw("wait", log, "--max-seconds", "0").returncode, STILL_RUNNING)
        self.assertEqual(self.run_aw("wait", log).returncode, JOB_FAILED)

    def test_status_of_job_that_ended_before_wait(self):
        log = self.start_job("sh", "-c", "exit 42")
        self.wait_until_gone(self.read_job(log)["pid"])
        self.assertEqual(self.run_aw("wait", log).returncode, JOB_FAILED)

    def test_missing_command_ends_as_failed(self):
        log = self.start_job("no-such-command-agent-wait")
        self.assertEqual(self.run_aw("wait", log).returncode, JOB_FAILED)

    def test_stall_returns_stalled(self):
        log = self.start_job("sleep", "60")
        result = self.run_aw("wait", log, "--stall-minutes", "0.03")
        self.assertEqual(result.returncode, STALLED)

    def test_growing_log_returns_still_running(self):
        log = self.start_job(sys.executable, "-c", WRITER, "60")
        result = self.run_aw("wait", log, "--stall-minutes", "0.05", "--max-seconds", "3")
        self.assertEqual(result.returncode, STILL_RUNNING)

    def test_started_job_survives_its_launcher(self):
        log = self.start_job("sleep", "60")
        self.assertEqual(self.run_aw("wait", log, "--max-seconds", "2").returncode, STILL_RUNNING)

    def test_wait_on_path_with_no_record_returns_bad_input(self):
        plain = os.path.join(self.tmp.name, "plain.log")
        open(plain, "w").close()
        self.assertEqual(self.run_aw("wait", plain).returncode, BAD_INPUT)
        self.assertEqual(self.run_aw("wait", os.path.join(self.tmp.name, "missing.log")).returncode,
                         BAD_INPUT)

    def test_stop_on_path_with_no_record_returns_bad_input(self):
        plain = os.path.join(self.tmp.name, "plain.log")
        open(plain, "w").close()
        self.assertEqual(self.run_aw("stop", plain).returncode, BAD_INPUT)
        self.assertEqual(self.run_aw("stop", os.path.join(self.tmp.name, "missing.log")).returncode,
                         BAD_INPUT)

    def test_second_start_on_running_log_returns_bad_input_and_preserves_first(self):
        log = self.start_job("sh", "-c", "echo first; sleep 60")
        first_job = self.read_job(log)
        second = self.run_aw("start", log, "--", "sh", "-c", "echo second")
        self.assertEqual(second.returncode, BAD_INPUT)
        self.assertEqual(self.read_job(log)["pid"], first_job["pid"])
        self.assertEqual(self.run_aw("wait", log, "--max-seconds", "1").returncode, STILL_RUNNING)
        with open(log) as f:
            content = f.read()
        self.assertIn("first", content)
        self.assertNotIn("second", content)

    def test_reused_log_after_job_ends_is_emptied(self):
        log = self.start_job("sh", "-c", "echo first-run")
        self.assertEqual(self.run_aw("wait", log).returncode, EXITED)
        log2 = self.start_job("sh", "-c", "echo second-run", log=log)
        self.assertEqual(self.run_aw("wait", log2).returncode, EXITED)
        with open(log2) as f:
            content = f.read()
        self.assertNotIn("first-run", content)
        self.assertIn("second-run", content)

    @unittest.skipUnless(has_systemd_user(), "needs a systemd user manager")
    def test_stop_kills_setsid_descendant(self):
        pid_file = os.path.join(self.tmp.name, "child.pid")
        spawner = (
            "import os, signal, subprocess, sys, time\n"
            "p = subprocess.Popen([sys.executable, '-c', "
            "'import signal, time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(60)'], "
            "start_new_session=True)\n"
            f"open({pid_file!r}, 'w').write(str(p.pid))\n"
            "time.sleep(60)\n"
        )
        log = self.start_job(sys.executable, "-c", spawner)
        deadline = time.monotonic() + 10
        while not os.path.exists(pid_file) and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertTrue(os.path.exists(pid_file), "descendant never wrote its pid")
        with open(pid_file) as f:
            child_pid = int(f.read())
        self.assertTrue(proc_alive(child_pid))
        self.assertEqual(self.run_aw("stop", log).returncode, EXITED)
        self.wait_until_gone(child_pid)
        self.assertEqual(self.run_aw("wait", log).returncode, JOB_FAILED)

    def test_stop_fallback_without_systemd_kills_process_group(self):
        env = dict(os.environ, DBUS_SESSION_BUS_ADDRESS="unix:path=/nonexistent",
                   XDG_RUNTIME_DIR=self.tmp.name)
        log = self.start_job("sleep", "60", env=env)
        job = self.read_job(log)
        self.assertEqual(job["unit"], "")
        self.assertEqual(self.run_aw("stop", log, env=env).returncode, EXITED)
        self.wait_until_gone(job["pid"])
        self.assertEqual(self.run_aw("wait", log, env=env).returncode, JOB_FAILED)

    def test_stop_fallback_after_killed_supervisor_does_not_claim_exited_while_worker_lives(self):
        env = dict(os.environ, DBUS_SESSION_BUS_ADDRESS="unix:path=/nonexistent",
                   XDG_RUNTIME_DIR=self.tmp.name)
        log = self.start_job("sh", "-c", "sleep 60", env=env)
        pid = self.read_job(log)["pid"]
        try:
            os.kill(pid, signal.SIGKILL)
            deadline = time.monotonic() + 10
            while os.path.exists(f"/proc/{pid}") and time.monotonic() < deadline:
                time.sleep(0.05)
            res = self.run_aw("stop", log, env=env)
            if res.returncode == EXITED:
                # If the supervisor stayed a zombie, stop verified its identity and killed the group.
                with self.assertRaises(ProcessLookupError):
                    os.killpg(pid, 0)
            else:
                self.assertEqual(res.returncode, JOB_FAILED)
        finally:
            try:
                os.killpg(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    def test_old_supervisor_on_deleted_files_does_not_clobber_new_job_record(self):
        log = self.start_job("sh", "-c", "sleep 2")
        os.unlink(log)
        os.unlink(log + ".job")
        log2 = self.start_job("sleep", "60", log=log)
        pid2 = self.read_job(log2)["pid"]
        time.sleep(3)
        self.assertEqual(self.read_job(log2)["pid"], pid2)
        self.assertEqual(self.run_aw("wait", log2, "--max-seconds", "1").returncode, STILL_RUNNING)

    def test_wait_does_not_report_replacement_jobs_status(self):
        log = self.start_job("sh", "-c", "sleep 1.3; exit 42")
        pid1 = self.read_job(log)["pid"]
        waiter = subprocess.Popen([sys.executable, AGENT_WAIT, "wait", log],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.jobs.append(waiter)
        # Wait until job 1 finishes (while waiter is between 1s polls), then
        # immediately reuse the log for `true` before waiter polls again.
        self.wait_until_gone(pid1)
        log2 = self.start_job("true", log=log)
        self.assertEqual(self.run_aw("wait", log2).returncode, EXITED)
        waiter.communicate(timeout=10)
        self.assertEqual(waiter.returncode, JOB_FAILED)

    def test_timed_out_start_never_runs_command(self):
        # Fake systemd-run: passes the scopes_work probe, then delays past the
        # 10s start deadline (even in a detached helper holding fd 3) before
        # attempting to run --supervise.
        fake_bin = os.path.join(self.tmp.name, "fake-bin")
        os.mkdir(fake_bin)
        marker = os.path.join(self.tmp.name, "ran")
        shim = os.path.join(fake_bin, "systemd-run")
        with open(shim, "w") as f:
            f.write(
                "#!/bin/sh\n"
                "for a in \"$@\"; do last=\"$a\"; done\n"
                "if [ \"$last\" = \"true\" ]; then exit 0; fi\n"
                "while [ \"$#\" -gt 0 ]; do\n"
                "  if [ \"$1\" = \"--\" ]; then shift; break; fi\n"
                "  shift\n"
                "done\n"
                "(sleep 11; exec \"$@\") &\n"
                "sleep 12\n"
            )
        os.chmod(shim, 0o755)
        env = dict(os.environ, PATH=f"{fake_bin}:{os.environ.get('PATH', '')}")
        res = self.run_aw("start", self.log, "--", "sh", "-c", f"touch {marker}", env=env)
        self.assertEqual(res.returncode, JOB_FAILED)
        # Wait past the delayed child's 11s wake-up to prove it aborted on fd 3 EOF.
        time.sleep(2.5)
        self.assertFalse(os.path.exists(marker))
        self.assertEqual(self.run_aw("wait", self.log).returncode, BAD_INPUT)

    def test_rejects_log_path_ending_in_job_suffix(self):
        bad = os.path.join(self.tmp.name, "build.job")
        self.assertEqual(self.run_aw("start", bad, "--", "true").returncode, BAD_INPUT)
        self.assertEqual(self.run_aw("wait", bad).returncode, BAD_INPUT)
        self.assertEqual(self.run_aw("stop", bad).returncode, BAD_INPUT)

    def test_fifo_sidecar_does_not_block_any_subcommand(self):
        open(self.log, "w").close()
        os.mkfifo(self.log + ".job")
        self.assertEqual(self.run_aw("wait", self.log).returncode, JOB_FAILED)
        self.assertEqual(self.run_aw("stop", self.log).returncode, JOB_FAILED)
        # start replaces the corrupt FIFO sidecar atomically without blocking.
        res = self.run_aw("start", self.log, "--", "true")
        self.assertEqual(res.returncode, EXITED, res.stderr)
        self.assertEqual(self.run_aw("wait", self.log).returncode, EXITED)

    def test_start_succeeds_with_closed_stdio_and_manual_supervise_fails(self):
        # Reproduces closed 0/1/2 where log_fd and socketpair land on low fds.
        res = subprocess.run(
            [sys.executable, AGENT_WAIT, "start", self.log, "--", "true"],
            preexec_fn=lambda: [os.close(fd) for fd in (0, 1, 2)],
            timeout=30)
        self.assertEqual(res.returncode, EXITED)
        self.assertEqual(self.run_aw("wait", self.log).returncode, EXITED)
        # Direct --supervise without fd 3 handshake must fail, not exit 0.
        manual = self.run_aw("--supervise", self.log, "", "--", "true")
        self.assertEqual(manual.returncode, JOB_FAILED)

    def test_stop_on_already_ended_job_returns_exited(self):
        log = self.start_job("true")
        self.assertEqual(self.run_aw("wait", log).returncode, EXITED)
        self.assertEqual(self.run_aw("stop", log).returncode, EXITED)

    def test_faked_mismatched_identity_is_never_waited_on_or_killed(self):
        target = subprocess.Popen(["sleep", "60"], start_new_session=True)
        self.jobs.append(target)
        with open("/proc/sys/kernel/random/boot_id") as f:
            real_boot = f.read().strip()
        with open(f"/proc/{target.pid}/stat") as f:
            real_st = f.read().rsplit(")", 1)[1].split()[19]

        cases = [
            ("wrong_start_time", {"pid": target.pid, "start_time": "1",
                                  "boot_id": real_boot, "unit": "", "exit": None}),
            ("wrong_boot_id", {"pid": target.pid, "start_time": real_st,
                               "boot_id": "00000000-0000-0000-0000-000000000000",
                               "unit": "", "exit": None}),
        ]
        for name, record in cases:
            with self.subTest(case=name):
                fake_log = os.path.join(self.tmp.name, f"{name}.log")
                open(fake_log, "w").close()
                with open(fake_log + ".job", "w") as f:
                    json.dump(record, f)
                # wait must not block on target, and must report unknown (4)
                t0 = time.monotonic()
                res = self.run_aw("wait", fake_log, "--max-seconds", "10")
                self.assertLess(time.monotonic() - t0, 5)
                self.assertEqual(res.returncode, JOB_FAILED)
                # stop must return 0 (already ended) without killing target
                self.assertEqual(self.run_aw("stop", fake_log).returncode, EXITED)
                self.assertIsNone(target.poll())
                self.assertTrue(proc_alive(target.pid))

    @unittest.skipUnless(has_systemd_user(), "needs a systemd user manager")
    def test_tampered_start_time_does_not_kill_live_scope(self):
        log = self.start_job("sleep", "60")
        job = self.read_job(log)
        tampered = dict(job, start_time="1")
        with open(log + ".job", "w") as f:
            json.dump(tampered, f)
        self.assertEqual(self.run_aw("stop", log).returncode, EXITED)
        self.assertTrue(proc_alive(job["pid"]))
        # Restore real record so tearDown stops it cleanly.
        with open(log + ".job", "w") as f:
            json.dump(job, f)

    @unittest.skipUnless(has_systemd_user(), "needs a systemd user manager")
    def test_started_job_survives_stopping_the_callers_scope(self):
        unit = f"agent-wait-test-{os.getpid()}-{time.monotonic_ns()}.scope"
        agent = subprocess.Popen(
            ["systemd-run", "--user", "--scope", "--quiet", "--collect", f"--unit={unit}", "--",
             "sh", "-c", '"$0" "$1" start "$2" -- sleep 60 && exec sleep 60',
             sys.executable, AGENT_WAIT, self.log],
            stdout=subprocess.PIPE, text=True)
        self.jobs.append(agent)
        started_log = agent.stdout.readline().strip()
        agent.stdout.close()
        self.started_logs.append(started_log)
        subprocess.run(["systemctl", "--user", "stop", unit], capture_output=True, timeout=30)
        agent.wait(timeout=10)
        self.assertEqual(self.run_aw("wait", started_log, "--max-seconds", "2").returncode,
                         STILL_RUNNING)

    @unittest.skipUnless(has_systemd_user(), "needs a systemd user manager")
    def test_scoped_job_runs_with_a_log_name_that_starts_with_a_dash(self):
        result = self.run_aw("start", "--", "-job.log", "--", "true", cwd=self.tmp.name)
        self.assertEqual(result.returncode, EXITED, result.stderr)
        log = result.stdout.strip()
        self.started_logs.append(log)
        self.assertEqual(log, os.path.join(self.tmp.name, "-job.log"))
        self.assertEqual(self.run_aw("wait", log).returncode, EXITED)

    def test_relative_log_prints_absolute_path_usable_from_elsewhere(self):
        sub = os.path.join(self.tmp.name, "sub")
        os.mkdir(sub)
        log = self.start_job("sh", "-c", "echo hi; sleep 60", log="rel.log", cwd=sub)
        self.assertTrue(os.path.isabs(log))
        self.assertEqual(log, os.path.join(sub, "rel.log"))
        self.assertEqual(self.run_aw("wait", log, "--max-seconds", "1", cwd="/").returncode,
                         STILL_RUNNING)
        self.assertEqual(self.run_aw("stop", log, cwd="/").returncode, EXITED)

    def test_killed_supervisor_never_reports_success(self):
        log = self.start_job("sleep", "60")
        pid = self.read_job(log)["pid"]
        os.kill(pid, signal.SIGKILL)
        self.wait_until_gone(pid)
        self.assertEqual(self.run_aw("wait", log).returncode, JOB_FAILED)

    def test_malformed_job_record_never_reports_success(self):
        log = self.start_job("true")
        self.assertEqual(self.run_aw("wait", log).returncode, EXITED)
        for content in [b"--1", "²".encode(), b"\xff", b'{"exit": false}']:
            with self.subTest(content=content):
                with open(log + ".job", "wb") as f:
                    f.write(content)
                self.assertEqual(self.run_aw("wait", log).returncode, JOB_FAILED)

    def test_start_rejects_unwritable_log_directory_without_truncating(self):
        directory = os.path.join(self.tmp.name, "locked")
        os.mkdir(directory)
        log = os.path.join(directory, "job.log")
        with open(log, "w") as f:
            f.write("keep-me\n")
        os.chmod(directory, 0o500)
        try:
            result = self.run_aw("start", log, "--", "true")
        finally:
            os.chmod(directory, 0o700)
        self.assertEqual(result.returncode, BAD_INPUT)
        with open(log) as f:
            self.assertEqual(f.read(), "keep-me\n")

    def test_rejects_non_regular_log(self):
        fifo = os.path.join(self.tmp.name, "fifo")
        os.mkfifo(fifo)
        self.assertEqual(self.run_aw("start", fifo, "--", "true").returncode, BAD_INPUT)

    def test_log_deleted_mid_wait_counts_as_no_progress(self):
        log = self.start_job("sleep", "60")
        threading.Timer(0.5, os.remove, [log]).start()
        result = self.run_aw("wait", log, "--stall-minutes", "0.04")
        self.assertEqual(result.returncode, STALLED)

    def test_rejects_bad_arguments_and_misplaced_flags(self):
        log = self.start_job("sleep", "60")
        bad_calls = [
            ("start", log, "--max-seconds", "10", "--", "true"),
            ("start", "--max-seconds", "10", log, "--", "true"),
            ("start", log, "--"),
            ("start", log, "true"),
            ("wait", log, "--max-seconds", "inf"),
            ("wait", log, "--max-seconds", "nan"),
            ("wait", log, "--max-seconds", "-1"),
            ("wait", log, "--stall-minutes", "nan"),
            ("stop", "--max-seconds", "5", log),
            ("--supervise",),
        ]
        for call in bad_calls:
            with self.subTest(call=call):
                self.assertEqual(self.run_aw(*call).returncode, BAD_INPUT)


if __name__ == "__main__":
    unittest.main()
